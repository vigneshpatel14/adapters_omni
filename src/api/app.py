"""
FastAPI application for receiving Evolution API webhooks.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import json
import time

# Import and set up logging
from fastapi.openapi.utils import get_openapi

from src.logger import setup_logging

# Set up logging with defaults from config
setup_logging()

# Configure logging
logger = logging.getLogger("src.api.app")

_MIGRATIONS_READY = False


def _ensure_database_ready(*, force: bool = False) -> float:
    """Ensure database schema is up to date, returning runtime in seconds."""

    global _MIGRATIONS_READY

    if _MIGRATIONS_READY and not force:
        return 0.0

    environment = os.environ.get("ENVIRONMENT")

    if environment == "test":
        _MIGRATIONS_READY = True
        return 0.0

    from src.db.migrations import auto_migrate

    logger.info("Running database migrations (first launch may take longer)...")
    start_time = time.perf_counter()

    if not auto_migrate():
        logger.error("❌ Database migrations failed during module initialization")
        _MIGRATIONS_READY = False
        raise RuntimeError("Database migrations must succeed before startup")

    duration = time.perf_counter() - start_time
    logger.info(f"✅ Database migrations ready in {duration:.2f}s")
    _MIGRATIONS_READY = True
    return duration


def prepare_runtime() -> float:
    """Public helper used by the CLI to warm database state before starting the API."""

    return _ensure_database_ready()


from src.core.telemetry import track_api_request, track_webhook_processed
from src.config import config
from src.services.agent_service import agent_service
from src.channels.whatsapp.evolution_api_sender import evolution_api_sender
from src.api.deps import get_database, get_instance_by_name
from src.api.routes.instances import router as instances_router
from src.api.routes.omni import router as omni_router
from src.api.routes.access import router as access_router
from src.db.database import create_tables, SessionLocal


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming API requests with payload."""

    async def dispatch(self, request: Request, call_next):
        # Skip logging for health check and docs
        if request.url.path in [
            "/health",
            "/api/v1/docs",
            "/api/v1/redoc",
            "/api/v1/openapi.json",
        ]:
            return await call_next(request)

        start_time = time.time()

        # Log request details
        logger.info(f"API Request: {request.method} {request.url.path}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request query params: {dict(request.query_params)}")

        # Log request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Read body
                body = await request.body()
                if body:
                    try:
                        # Try to parse as JSON
                        json_body = json.loads(body.decode())
                        # Mask sensitive fields
                        masked_body = self._mask_sensitive_data(json_body)
                        logger.debug(f"Request body: {json.dumps(masked_body, indent=2)}")
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        logger.debug(f"Request body (non-JSON): {len(body)} bytes")

                # Create new request with body for downstream processing
                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive
            except Exception as e:
                logger.warning(f"Failed to log request body: {e}")

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"API Response: {response.status_code} - {process_time:.3f}s")

        # Track API request telemetry
        try:
            track_api_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=process_time * 1000,
            )
        except Exception as e:
            # Never let telemetry break the API
            logger.debug(f"Telemetry tracking failed: {e}")

        return response

    def _mask_sensitive_data(self, data):
        """Mask sensitive fields and large payloads in request data."""
        if not isinstance(data, dict):
            return data

        masked = data.copy()
        sensitive_fields = [
            "password",
            "api_key",
            "agent_api_key",
            "evolution_key",
            "token",
            "secret",
        ]
        large_data_fields = ["base64", "message", "media_contents", "data"]

        for key, value in masked.items():
            if any(field in key.lower() for field in sensitive_fields):
                if isinstance(value, str) and len(value) > 8:
                    masked[key] = f"{value[:4]}***{value[-4:]}"
                elif isinstance(value, str) and value:
                    masked[key] = "***"
            elif any(field in key.lower() for field in large_data_fields):
                if isinstance(value, str) and len(value) > 100:
                    masked[key] = f"<large_string:{len(value)}_chars:{value[:20]}...{value[-20:]}>"
                elif isinstance(value, list) and len(value) > 0:
                    masked[key] = f"<array:{len(value)}_items>"
                elif isinstance(value, dict):
                    masked[key] = self._mask_sensitive_data(value)
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_data(value)

        return masked


# Note: create_tables() has been moved to lifespan function to ensure proper test isolation
# Database tables will be created during app startup in the lifespan function


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    # Startup
    logger.info("Initializing application...")
    # Skip database setup in test environment (handled by test fixtures)
    environment = os.environ.get("ENVIRONMENT")

    if environment != "test":
        _ensure_database_ready(force=True)

        # After migrations succeed, ensure tables exist for runtime checks
        try:
            create_tables()
            logger.info("✅ Database tables created/verified")
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            # Let the app continue - tables might already exist

        # Load access control rules into cache
        try:
            from src.services.access_control import access_control_service

            with SessionLocal() as db:
                access_control_service.load_rules(db)
            logger.info("✅ Access control rules loaded into cache")
        except Exception as e:
            logger.error(f"❌ Failed to load access control rules: {e}")
            # Continue without access control cache - will be loaded on first use
    else:
        logger.info("Skipping database setup in test environment")

    logger.info(f"Log level set to: {config.logging.level}")
    logger.info(f"API Host: {config.api.host}")
    logger.info(f"API Port: {config.api.port}")
    logger.info(f"API URL: http://{config.api.host}:{config.api.port}")

    # Auto-discover existing Evolution instances (non-intrusive)
    # Skip auto-discovery in test environment to prevent database conflicts
    if environment != "test":
        try:
            logger.info("Starting Evolution instance auto-discovery...")
            from src.services.discovery_service import discovery_service

            with SessionLocal() as db:
                discovered_instances = await discovery_service.discover_evolution_instances(db)
                if discovered_instances:
                    logger.info(f"Auto-discovered {len(discovered_instances)} Evolution instances:")
                    for instance in discovered_instances:
                        logger.info(f"  - {instance.name} (active: {instance.is_active})")
                else:
                    logger.info("No new Evolution instances discovered")
        except Exception as e:
            logger.warning(f"Evolution instance auto-discovery failed: {e}")
            logger.debug(f"Auto-discovery error details: {str(e)}")
            logger.info("Continuing without auto-discovery - instances can be created manually")
    else:
        logger.info("Skipping Evolution instance auto-discovery in test environment")

    # Telemetry status logging
    from src.core.telemetry import telemetry_client

    if telemetry_client.is_enabled():
        logger.info("📊 Telemetry enabled - Anonymous usage analytics help improve Automagik Omni")
        logger.info("   • Collected: CLI usage, API performance, system info (no personal data)")
        logger.info("   • Disable: 'automagik-omni telemetry disable' or AUTOMAGIK_OMNI_DISABLE_TELEMETRY=true")
    else:
        logger.info("📊 Telemetry disabled")

    # Application ready - instances will be created via API endpoints
    logger.info("API ready - use /api/v1/instances to create instances")

    yield

    # Shutdown (cleanup if needed)
    logger.info("Shutting down application...")


# Create FastAPI app with authentication configuration
app = FastAPI(
    lifespan=lifespan,
    title=config.api.title,
    description=config.api.description,
    version=config.api.version,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    openapi_tags=[
        {
            "name": "Instance Management",
            "description": "Create, configure, and monitor messaging channel instances.",
        },
        {
            "name": "Omni Channel Abstraction",
            "description": "Unified channel access to contacts and chats across providers.",
        },
        {
            "name": "messages",
            "description": "Message Operations",
        },
        {
            "name": "traces",
            "description": "Message Tracing & Analytics",
        },
        {
            "name": "webhooks",
            "description": "Webhook Receivers",
        },
        {
            "name": "profiles",
            "description": "User Profile Management",
        },
        {
            "name": "health",
            "description": "System Health & Status",
        },
    ],
)

# Include omni communication routes under instances namespace (for unified API)
app.include_router(
    omni_router,
    prefix="/api/v1/instances",
    tags=["Omni Channel Abstraction"],
)

# Include instance management routes
app.include_router(
    instances_router,
    prefix="/api/v1",
    tags=["Instance Management"],
)


# Include trace management routes
from src.api.routes.traces import router as traces_router

app.include_router(traces_router, prefix="/api/v1", tags=["traces"])

# Include message sending routes
from src.api.routes.messages import router as messages_router

app.include_router(messages_router, prefix="/api/v1/instance", tags=["messages"])

# Include access control management routes
app.include_router(access_router, prefix="/api/v1", tags=["access"])

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allowed_origins,
    allow_credentials=config.cors.allow_credentials,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
)


# Custom OpenAPI schema with enhanced formatting and authentication
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    # Enhanced API description
    enhanced_description = f"""
{config.api.description}

## Features

- Multi-tenant architecture with isolated instances
- Universal messaging across WhatsApp, Discord, and Slack
- Message tracing and analytics
- API key authentication via x-api-key header

## Quick Start

1. Include API key in `x-api-key` header
2. Create an instance for your channel
3. Send messages using the omni endpoints
4. Monitor activity via traces and health endpoints
"""

    openapi_schema = get_openapi(
        title=config.api.title,
        version=config.api.version,
        description=enhanced_description,
        routes=app.routes,
    )

    # Add server information dynamically from configuration
    servers = []

    # Add production server if configured
    if config.api.prod_server_url:
        servers.append(
            {
                "url": config.api.prod_server_url,
                "description": "Production Server",
            }
        )

    # Always add local development server with actual configured port
    servers.append(
        {
            "url": f"http://localhost:{config.api.port}",
            "description": "Local Development Server",
        }
    )

    openapi_schema["servers"] = servers

    # Add ApiKeyAuth security scheme
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}

    # Replace any existing security scheme with ApiKeyAuth
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "x-api-key",
            "description": "API key for authentication (e.g., 'namastex888')",
        }
    }

    # Update security requirement for all operations
    for path in openapi_schema.get("paths", {}).values():
        for operation in path.values():
            if isinstance(operation, dict) and "security" in operation:
                # Update existing security to use ApiKeyAuth
                operation["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health", tags=["health"])
async def health_check():
    """
    System health check endpoint.

    Returns status for API, database, Discord services, and runtime information.
    """

    from datetime import datetime, timezone

    # Basic API health
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "api": {
                "status": "up",
                "checks": {"database": "connected", "runtime": "operational"},
            }
        },
    }

    # Check Discord service status if available
    try:
        # Access Discord bot manager via the exported discord_service
        from src.services.discord_service import discord_service

        bot_manager = getattr(discord_service, "bot_manager", None)

        if bot_manager:
            bot_statuses = {}
            for instance_name in bot_manager.bots.keys():
                bot_status = bot_manager.get_bot_status(instance_name)
                if bot_status:
                    bot_statuses[instance_name] = {
                        "status": bot_status.status,
                        "guild_count": bot_status.guild_count,
                        "uptime": (bot_status.uptime.isoformat() if bot_status.uptime else None),
                        "latency": (round(bot_status.latency * 1000, 2) if bot_status.latency else None),  # ms
                    }

            health_status["services"]["discord"] = {
                "status": "up" if bot_statuses else "down",
                "instances": bot_statuses,
                "voice_sessions": len(bot_manager.voice_manager.get_voice_sessions()),
            }
        else:
            health_status["services"]["discord"] = {
                "status": "not_running",
                "message": "Discord service not initialized",
            }

    except Exception as e:
        health_status["services"]["discord"] = {"status": "error", "error": str(e)}

    return health_status


async def _handle_evolution_webhook(instance_config, request: Request, db: Session):
    """
    Core webhook handling logic shared between default and tenant endpoints.

    Args:
        instance_config: InstanceConfig object with per-instance configuration
        request: FastAPI request object
    """
    from src.services.trace_service import get_trace_context

    start_time = time.time()
    payload_size = 0

    try:
        logger.info(f"🔄 WEBHOOK ENTRY: Starting webhook processing for instance '{instance_config.name}'")

        # Get the JSON data from the request
        raw_data = await request.json()
        logger.info(f"✅ WEBHOOK JSON PARSED: Received webhook for instance '{instance_config.name}'")
        logger.debug(f"Raw webhook data: {raw_data}")
        
        # Check if the payload is Base64-encoded (Evolution API with "Webhook Base64: Enabled")
        # If the payload has a "data" field that's a string, it might be Base64-encoded
        data = raw_data
        if isinstance(raw_data.get("data"), str):
            try:
                import base64
                # Try to decode the Base64 data
                decoded_bytes = base64.b64decode(raw_data["data"])
                decoded_str = decoded_bytes.decode('utf-8')
                data = json.loads(decoded_str)
                logger.info(f"✅ WEBHOOK BASE64 DECODED: Successfully decoded Base64 payload")
                logger.debug(f"Decoded webhook data: {data}")
            except Exception as e:
                logger.warning(f"Could not decode Base64 payload: {e}, using raw data instead")
                # Fall back to treating raw_data as-is
                data = raw_data
        
        payload_size = len(json.dumps(data).encode("utf-8"))

        logger.debug(f"Webhook data: {data}")

        # Extract individual messages from the messages array if present
        # Evolution API sends webhooks as: {"event": "messages.upsert", "data": {"messages": [...]}}
        messages_to_process = []
        
        if "data" in data and isinstance(data.get("data"), dict):
            webhook_data = data["data"]
            if "messages" in webhook_data and isinstance(webhook_data.get("messages"), list):
                # Extract individual messages from array
                messages_to_process = webhook_data["messages"]
                logger.info(f"📨 Processing {len(messages_to_process)} messages from webhook")
            elif "message" in webhook_data:
                # Single message in data.message structure
                messages_to_process = [webhook_data]
            else:
                # Fallback: treat entire webhook_data as a message
                messages_to_process = [webhook_data]
        else:
            # Fallback: treat entire data as a message (backward compatibility)
            messages_to_process = [data]

        # Process each message
        trace_id = None
        for message_to_process in messages_to_process:
            # Enhanced logging for audio message debugging
            message_obj = message_to_process.get("message", {})
            if "audioMessage" in message_obj:
                logger.info(f"🎵 AUDIO MESSAGE DETECTED: {json.dumps(message_obj, indent=2)[:1000]}")
            
            # DEBUG: Log the message structure being processed
            logger.debug(f"🔍 MESSAGE STRUCTURE DEBUG:")
            logger.debug(f"   Message keys: {list(message_to_process.keys())}")
            logger.debug(f"   Has 'key': {'key' in message_to_process}")
            logger.debug(f"   Has 'message': {'message' in message_to_process}")
            logger.debug(f"   Full message: {json.dumps(message_to_process, indent=2)[:500]}")

            # Start message tracing
            with get_trace_context(message_to_process, instance_config.name, db) as trace:
                trace_id = trace.trace_id
                # Update the Evolution API sender with the instance configuration
                # Use the instance_config to set proper Evolution API credentials
                evolution_api_sender.server_url = instance_config.evolution_url
                evolution_api_sender.api_key = instance_config.evolution_key
                # Use the Omni instance name (e.g., "whatsapp-test") as the Evolution API instance name
                # This is more reliable than using the UUID, as Evolution API v2.3.7 accepts both but name is preferred
                evolution_api_sender.instance_name = instance_config.name
                evolution_api_sender.config = instance_config  # Store config for accessing enable_auto_split

                # Capture real media messages for testing purposes
                try:
                    from src.utils.test_capture import test_capture

                    test_capture.capture_media_message(message_to_process, instance_config)
                except Exception as e:
                    logger.error(f"Test capture failed: {e}")

                # Process the message through the agent service
                # The agent service will now delegate to the WhatsApp handler
                # which will handle transcription and sending responses directly
                # Pass instance_config and trace context to service for per-instance agent configuration
                agent_service.process_whatsapp_message(message_to_process, instance_config, trace)

        # Track webhook processing telemetry
        try:
            track_webhook_processed(
                channel="whatsapp",
                success=True,
                duration_ms=(time.time() - start_time) * 1000,
                payload_size_kb=payload_size / 1024,
                instance_type="multi_tenant",
            )
        except Exception as e:
            logger.debug(f"Webhook telemetry tracking failed: {e}")

        # Return success response
        return {
            "status": "success",
            "instance": instance_config.name,
            "trace_id": trace_id,
        }

    except Exception as e:
        # Track failed webhook processing
        try:
            track_webhook_processed(
                channel="whatsapp",
                success=False,
                duration_ms=(time.time() - start_time) * 1000,
                payload_size_kb=payload_size / 1024,
                instance_type="multi_tenant",
                error=str(e)[:100],  # Truncate error message
            )
        except Exception as te:
            logger.debug(f"Webhook telemetry tracking failed: {te}")

        logger.error(
            f"Error processing webhook for instance '{instance_config.name}': {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/evolution/{instance_name}", tags=["webhooks"])
async def evolution_webhook_tenant(instance_name: str, request: Request, db: Session = Depends(get_database)):
    """
    Multi-tenant webhook endpoint for Evolution API.

    Receives incoming messages from Evolution API instances and routes them to the appropriate tenant configuration.
    Supports text, media, audio, and other message types with automatic transcription and processing.
    """
    # Get instance configuration
    instance_config = get_instance_by_name(instance_name, db)

    # Handle using shared logic
    return await _handle_evolution_webhook(instance_config, request, db)


def start_api():
    """Start the FastAPI server using uvicorn."""
    import uvicorn

    host = config.api.host if hasattr(config, "api") and hasattr(config.api, "host") else "0.0.0.0"
    port = config.api.port if hasattr(config, "api") and hasattr(config.api, "port") else 8000

    logger.info(f"Starting FastAPI server on {host}:{port}")

    # Create custom logging config for uvicorn that completely suppresses its formatters
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "src.logger.ColoredFormatter",
                "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%H:%M:%S",
                "use_colors": True,
                "use_emojis": True,
                "shorten_paths": True,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["default"],
        },
    }

    uvicorn.run("src.api.app:app", host=host, port=port, reload=False, log_config=log_config)

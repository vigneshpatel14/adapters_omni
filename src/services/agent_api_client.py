"""
Agent API Client
Handles interaction with the Automagik Agents API and direct Leo integration.
"""

import logging
import uuid
import json
from typing import Dict, Any, Optional, List, Union

import requests
from requests.exceptions import RequestException, Timeout

from src.config import config
from src.services.leo_agent_client import LeoAgentClient


# Configure logging
logger = logging.getLogger("src.services.agent_api_client")


# Custom JSON encoder that handles UUID objects
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # Convert UUID to string
            return str(obj)
        return super().default(obj)


class AgentApiClient:
    """Client for interacting with the Automagik Agents API."""

    def __init__(self, config_override=None):
        """
        Initialize the API client.

        Args:
            config_override: Optional InstanceConfig object for per-instance configuration
        """
        # Store config for later access to instance properties
        self.instance_config = config_override
        
        # Leo client (initialized only if needed)
        self._leo_client = None

        if config_override:
            # Use per-instance configuration
            self.api_url = config_override.agent_api_url
            self.api_key = config_override.agent_api_key
            self.default_agent_name = config_override.default_agent
            self.timeout = config_override.agent_timeout
            
            # Check if this is a direct Leo integration
            if self._is_leo_api_url(self.api_url):
                logger.info(f"Detected Leo API endpoint for instance '{config_override.name}' - using direct integration")
                self._initialize_leo_client()
            else:
                logger.info(f"Agent API client initialized for instance '{config_override.name}' with URL: {self.api_url}")
        else:
            # Use default values for backward compatibility
            # Default to local Hive API
            import os

            self.api_url = os.getenv("AGENT_API_URL", "http://localhost:8000")
            self.api_key = os.getenv("AGENT_API_KEY", "")
            self.default_agent_name = ""
            self.timeout = 60
            logger.debug("Agent API client initialized without instance config - using default values")

        # Configuration will be validated when actually needed

        # Flag for health check
        self.is_healthy = False
    
    def _is_leo_api_url(self, url: str) -> bool:
        """Check if URL is a Leo API endpoint."""
        return "api-leodev.gep.com" in url or "leo-portal-agentic-runtime" in url
    
    def _initialize_leo_client(self):
        """Initialize Leo client with configuration."""
        try:
            # If we have instance config, use it; otherwise use environment config
            if self.instance_config:
                # Use instance-specific configuration
                # For instance config, we have the full agent_api_url but need to extract components
                # The api_url is the base, and we use the configured values
                leo_config = config.leo_agent  # Still need some defaults from env
                
                self._leo_client = LeoAgentClient(
                    api_base_url=self.instance_config.agent_api_url or leo_config.api_base_url,
                    workflow_id=leo_config.workflow_id,  # Still use env workflow_id for instance
                    bearer_token=self.instance_config.agent_api_key or leo_config.bearer_token,  # Use instance key if provided
                    subscription_key=leo_config.subscription_key,
                    bpc=leo_config.bpc,
                    environment=leo_config.environment,
                    version=leo_config.version
                )
                logger.info(f"Leo client initialized for instance '{self.instance_config.name}' with URL: {self.instance_config.agent_api_url}")
            else:
                # Use environment configuration
                if not config.leo_agent.is_configured:
                    logger.warning("Leo credentials not configured in environment variables")
                    return
                
                self._leo_client = LeoAgentClient(
                    api_base_url=config.leo_agent.api_base_url,
                    workflow_id=config.leo_agent.workflow_id,
                    bearer_token=config.leo_agent.bearer_token,
                    subscription_key=config.leo_agent.subscription_key,
                    bpc=config.leo_agent.bpc,
                    environment=config.leo_agent.environment,
                    version=config.leo_agent.version
                )
                logger.info("Leo client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Leo client: {e}", exc_info=True)

    def _make_headers(self) -> Dict[str, str]:
        """Make headers for API requests."""
        headers = {"Content-Type": "application/json", "x-api-key": self.api_key}
        return headers

    def health_check(self) -> bool:
        """Check if the API is healthy."""
        try:
            url = f"{self.api_url}/health"
            response = requests.get(url, timeout=5)
            self.is_healthy = response.status_code == 200
            return self.is_healthy
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.is_healthy = False
            return False

    def run_agent(
        self,
        agent_name: str,
        message_content: str,
        message_type: Optional[str] = None,
        media_url: Optional[str] = None,
        mime_type: Optional[str] = None,
        media_contents: Optional[List[Dict[str, Any]]] = None,
        channel_payload: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        session_name: Optional[str] = None,
        user_id: Optional[Union[str, int]] = None,
        user: Optional[Dict[str, Any]] = None,
        message_limit: int = 100,
        session_origin: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        preserve_system_prompt: bool = False,
    ) -> Dict[str, Any]:
        """
        Run an agent with the provided parameters.

        Args:
            agent_name: Name of the agent to run
            message_content: The message content
            message_type: The message type (text, image, etc.)
            media_url: URL to media if present
            mime_type: MIME type of the media
            media_contents: List of media content objects
            channel_payload: Additional channel-specific payload
            session_id: Optional session ID for conversation continuity (legacy)
            session_name: Optional readable session name (preferred over session_id)
            user_id: User ID (optional if user dict is provided)
            user: User data dict with email, phone_number, and user_data for auto-creation
            message_limit: Maximum number of messages to return
            session_origin: Origin of the session
            context: Additional context for the agent
            preserve_system_prompt: Whether to preserve the system prompt

        Returns:
            The agent's response as a dictionary
        """
        # Use the new agent API endpoint
        endpoint = f"{self.api_url}/api/agent/chat"

        # Prepare headers
        headers = self._make_headers()

        # Generate or use provided session_id - required for the new API
        import uuid as uuid_module
        if session_id:
            actual_session_id = session_id
        elif session_name:
            # Generate a deterministic session ID from session name
            actual_session_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_OID, session_name))
        else:
            # Generate a random session ID
            actual_session_id = str(uuid_module.uuid4())
            logger.info(f"Generated new session_id: {actual_session_id}")

        # Prepare payload for the new API
        payload = {
            "message": message_content,
            "session_id": actual_session_id,
            "session_name": session_name or f"session_{actual_session_id[:8]}",
        }

        # First, determine the user_id - this is REQUIRED by the agent API
        effective_user_id = user_id  # Default to passed user_id
        
        # Safe check: ensure user is dict and has phone_number before trying to access it
        if user is not None and isinstance(user, dict) and "phone_number" in user:
            # If user dict has phone_number, try to use it as deterministic user_id
            if not effective_user_id:
                phone_number = user.get("phone_number")
                if phone_number is not None:
                    phone_num = str(phone_number).replace("+", "").replace(" ", "")
                    if phone_num:
                        effective_user_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_OID, phone_num))
                        logger.info(f"Generated UUID from phone_number: {effective_user_id}")
        
        # Handle user_id validation and generation
        if effective_user_id is not None:
            if isinstance(effective_user_id, str):
                # First, check if it's a valid UUID string
                try:
                    uuid_module.UUID(effective_user_id)
                    # If it's a valid UUID string, keep it as is
                    logger.debug(f"Using UUID string for user_id: {effective_user_id}")
                except ValueError:
                    # If not a UUID, generate a deterministic UUID from the identifier
                    if effective_user_id.isdigit():
                        # Generate UUID from phone number for consistent user identification
                        effective_user_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_OID, effective_user_id))
                        logger.info(f"Generated UUID from phone number: {effective_user_id}")
                    elif effective_user_id.lower() == "anonymous":
                        # Generate UUID for anonymous user
                        effective_user_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_OID, "anonymous"))
                        logger.info(f"Generated UUID for anonymous user: {effective_user_id}")
                    else:
                        # Generate UUID from any string identifier
                        effective_user_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_OID, effective_user_id))
                        logger.info(f"Generated UUID from identifier: {effective_user_id}")
            elif isinstance(effective_user_id, int):
                # Convert integer user_id to UUID for compatibility with agent API
                effective_user_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_OID, str(effective_user_id)))
                logger.info(f"Generated UUID from integer user_id: {effective_user_id}")
            else:
                # If it's not a string or int, generate UUID from string representation
                effective_user_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_OID, str(effective_user_id)))
                logger.warning(f"Unexpected user_id type: {type(effective_user_id)}, generated UUID: {effective_user_id}")
        else:
            # Handle case where user_id is None - generate a default UUID
            default_user_id = str(uuid_module.uuid5(uuid_module.NAMESPACE_OID, "default"))
            logger.warning(f"No user_id provided, using default UUID: {default_user_id}")
            effective_user_id = default_user_id

        # Always include user_id at top level - it's REQUIRED by the agent API
        payload["user_id"] = effective_user_id
        logger.debug(f"Payload user_id set to: {effective_user_id}")
        
        # Also include user dict if provided for automatic user creation
        if user is not None and isinstance(user, dict):
            # Use the user dict for automatic user creation
            payload["user"] = user
            phone_info = user.get('phone_number', 'N/A') if isinstance(user.get('phone_number'), str) else 'N/A'
            logger.info(f"Using user dict for automatic user creation: {phone_info}")

        # Add optional parameters if provided
        if message_type:
            payload["message_type"] = message_type

        if media_url:
            payload["mediaUrl"] = media_url

        if mime_type:
            payload["mime_type"] = mime_type

        if media_contents:
            payload["media_contents"] = media_contents

        if channel_payload:
            payload["channel_payload"] = channel_payload

        if context:
            payload["context"] = context

        if session_origin:
            payload["session_origin"] = session_origin

        # Add preserve_system_prompt flag
        payload["preserve_system_prompt"] = preserve_system_prompt

        # Log the request (without sensitive information)
        logger.info(f"Making API request to {endpoint}")
        # Log payload summary without full content to avoid log clutter
        payload_summary = {
            "message_length": len(payload.get("message", "")),
            "user_id": payload.get("user_id"),
            "session_id": payload.get("session_id"),
            "message_type": payload.get("message_type"),
            "media_contents_count": len(payload.get("media_contents", [])),
            "has_context": bool(payload.get("context")),
        }
        logger.debug(f"Request payload summary: {json.dumps(payload_summary)}")

        try:
            # Check if this is a Leo direct integration
            if self._leo_client:
                logger.info("Using direct Leo API integration")
                try:
                    response_text = self._leo_client.call_agent(
                        message=message_content,
                        session_id=actual_session_id,
                        user_id=effective_user_id,
                        context=context
                    )
                    
                    # Return in standard format
                    return {
                        "text": response_text,
                        "message": response_text,
                        "session_id": actual_session_id,
                        "success": True,
                        "agent_name": "leo"
                    }
                except Exception as leo_error:
                    logger.error(f"Leo API error: {leo_error}", exc_info=True)
                    # Provide better error message for 401 auth errors
                    if "401" in str(leo_error) or "Session has expired" in str(leo_error):
                        logger.error("Leo API session expired - the workflow endpoint credentials need to be refreshed")
                        raise RuntimeError("Agent API authentication failed. Your Leo API session has expired. Please update your agent configuration with fresh credentials.")
                    raise RuntimeError(f"Leo API call failed: {leo_error}")
            
            # Send request to the agent API
            logger.info(f"Sending request to agent API with timeout: {self.timeout}s")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=self.timeout)

            # Log the response status
            logger.info(f"API response status: {response.status_code}")

            if response.status_code == 200:
                # Parse the response
                try:
                    response_data = response.json()

                    # Return the full response structure to preserve all fields
                    if isinstance(response_data, dict):
                        # Normalize response: support both "text" and "message" fields
                        message_text = response_data.get("message") or response_data.get("text") or ""
                        session_id = response_data.get("session_id", "unknown")
                        success = response_data.get("success", True)

                        message_length = len(message_text) if isinstance(message_text, str) else "non-string message"
                        logger.info(
                            f"Received response from agent ({message_length} chars), session: {session_id}, success: {success}"
                        )

                        # Normalize the response to our expected format
                        normalized_response = {
                            "message": message_text,  # Ensure "message" field exists
                            "success": success,
                            "session_id": session_id,
                            "tool_calls": response_data.get("tool_calls", []),
                            "tool_outputs": response_data.get("tool_outputs", []),
                            "usage": response_data.get("usage", {}),
                        }
                        
                        # Preserve any additional fields from the agent response
                        for key, value in response_data.items():
                            if key not in normalized_response:
                                normalized_response[key] = value

                        # Return the complete response structure
                        return normalized_response
                    else:
                        # If response is not a dict, wrap it in the expected format
                        logger.warning(f"Agent response is not a dict, wrapping: {type(response_data)}")
                        return {
                            "message": str(response_data),
                            "success": True,
                            "session_id": None,
                            "tool_calls": [],
                            "tool_outputs": [],
                            "usage": {},
                        }
                except json.JSONDecodeError:
                    # Not a JSON response, try to use the raw text
                    text_response = response.text
                    logger.warning(f"Response was not valid JSON, using raw text: {text_response[:100]}...")
                    return {
                        "message": text_response,
                        "success": True,
                        "session_id": None,
                        "tool_calls": [],
                        "tool_outputs": [],
                        "usage": {},
                    }
            else:
                # Log error
                logger.error(f"Error from agent API: {response.status_code}")
                logger.error(f"Response text: {response.text[:500]}")
                try:
                    error_data = response.json()
                    logger.error(f"Error response JSON: {error_data}")
                except:
                    pass
                return {
                    "error": f"Desculpe, encontrei um erro (status {response.status_code}).",
                    "details": f"Response length: {len(response.text)} chars",
                }

        except Timeout:
            logger.error(f"Timeout calling agent API after {self.timeout}s")
            return {
                "error": "Desculpe, está demorando mais do que o esperado para responder. Por favor, tente novamente.",
                "success": False,
                "session_id": None,
                "tool_calls": [],
                "tool_outputs": [],
                "usage": {},
            }

        except RequestException as e:
            logger.error(f"Error calling agent API: {e}")
            return {
                "error": "Desculpe, encontrei um erro ao me comunicar com meu cérebro. Por favor, tente novamente.",
                "success": False,
                "session_id": None,
                "tool_calls": [],
                "tool_outputs": [],
                "usage": {},
            }

        except Exception as e:
            logger.error(f"Unexpected error calling agent API: {e}", exc_info=True)
            return {
                "error": "Desculpe, encontrei um erro inesperado. Por favor, tente novamente.",
                "success": False,
                "session_id": None,
                "tool_calls": [],
                "tool_outputs": [],
                "usage": {},
            }

    def stream_agent(
        self,
        message: str,
        session_name: str,
        user_id: Optional[str] = None,
        user: Optional[Dict[str, Any]] = None,
        session_origin: Optional[str] = None,
        message_type: str = "text",
        context: Optional[Dict[str, Any]] = None,
        media_contents: Optional[List[Dict[str, Any]]] = None,
        preserve_system_prompt: bool = False,
    ):
        """
        Stream agent response as chunks (for Discord streaming messages).
        
        This method streams text chunks from the agent API as they arrive.
        For Leo API, it yields chunks from the streaming response.
        
        Args:
            message: User's message
            session_name: Session identifier
            user_id: User ID (optional)
            user: User dictionary for auto-creation (optional)
            session_origin: Origin of the session (e.g., 'discord')
            message_type: Type of message (default: 'text')
            context: Additional context (optional)
            media_contents: Media attachments (optional)
            preserve_system_prompt: Whether to preserve system prompt
            
        Yields:
            Text chunks as they arrive
            
        Raises:
            RuntimeError: If API call fails
        """
        # For Leo API, use the stream_agent method
        if self._leo_client:
            logger.info("Using direct Leo API streaming")
            try:
                # Effective user_id: use provided user_id, or use email/phone from user dict, or generate
                effective_user_id = user_id
                if not effective_user_id and user:
                    if isinstance(user, dict):
                        effective_user_id = user.get("email") or user.get("phone_number")
                
                # If still no user_id, generate one
                if not effective_user_id:
                    import uuid
                    effective_user_id = str(uuid.uuid4())
                
                # Stream from Leo API
                for chunk in self._leo_client.stream_agent(
                    message=message,
                    session_id=session_name,
                    user_id=effective_user_id,
                    context=context
                ):
                    yield chunk
                    
            except Exception as e:
                logger.error(f"Leo API streaming error: {e}", exc_info=True)
                raise RuntimeError(f"Leo API streaming failed: {e}")
        else:
            # Fallback: call run_agent and yield the full response
            # (non-streaming agents will return complete response at once)
            logger.info("Streaming not supported for this agent type, using non-streaming mode")
            try:
                response = self.run_agent(
                    agent_name="leo",
                    message_content=message,
                    session_name=session_name,
                    session_id=session_name,
                    user_id=user_id,
                    user=user,
                    session_origin=session_origin,
                    message_type=message_type,
                    media_contents=media_contents,
                    context=context,
                    preserve_system_prompt=preserve_system_prompt,
                )
                
                # Yield the complete message as a single chunk
                if response.get("success"):
                    message_text = response.get("message") or response.get("text") or ""
                    if message_text:
                        yield message_text
                else:
                    # Yield error message
                    error_msg = response.get("error", "An error occurred")
                    yield error_msg
                    
            except Exception as e:
                logger.error(f"Error in fallback streaming: {e}", exc_info=True)
                raise RuntimeError(f"Agent streaming failed: {e}")

    def get_session_info(self, session_name: str) -> Optional[Dict[str, Any]]:
        """
        Get session information from the agent API.

        Args:
            session_name: Name of the session to retrieve

        Returns:
            Session information dictionary if successful, None otherwise
        """
        endpoint = f"{self.api_url}/api/v1/sessions/{session_name}"

        try:
            # Make the request using the configured timeout
            response = requests.get(endpoint, headers=self._make_headers(), timeout=self.timeout)

            # Check for successful response
            if response.status_code == 200:
                session_data = response.json()
                logger.debug(f"Retrieved session info for {session_name}: user_id={session_data.get('user_id')}")
                return session_data
            elif response.status_code == 404:
                logger.warning(f"Session {session_name} not found")
                return None
            else:
                logger.warning(f"Unexpected response getting session {session_name}: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting session info for {session_name}: {str(e)}")
            return None

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Get a list of available agents.

        Returns:
            List of agent information dictionaries
        """
        endpoint = f"{self.api_url}/api/v1/agent/list"

        try:
            # Make the request
            response = requests.get(endpoint, headers=self._make_headers(), timeout=self.timeout)

            # Check for successful response
            response.raise_for_status()

            # Parse and return response
            result = response.json()
            return result

        except Exception as e:
            logger.error(f"Error listing agents: {str(e)}", exc_info=True)
            return []

    def process_message(
        self,
        message: str,
        user_id: Optional[Union[str, int]] = None,
        user: Optional[Dict[str, Any]] = None,
        session_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        message_type: str = "text",
        media_url: Optional[str] = None,
        media_contents: Optional[List[Dict[str, Any]]] = None,
        mime_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        channel_payload: Optional[Dict[str, Any]] = None,
        session_origin: Optional[str] = None,
        preserve_system_prompt: bool = False,
        trace_context=None,
    ) -> Dict[str, Any]:
        """
        Process a message using the agent API.
        This is a wrapper around run_agent that returns the full response structure.

        Args:
            message: The message to process
            user_id: User ID (optional if user dict is provided)
            user: User data dict with email, phone_number, and user_data for auto-creation
            session_name: Session name (preferred over session_id)
            agent_name: Optional agent name (defaults to self.default_agent_name)
            message_type: Message type (text, image, etc.)
            media_url: URL to media if present
            media_contents: List of media content objects
            mime_type: MIME type of the media
            context: Additional context
            channel_payload: Additional channel-specific payload
            session_origin: Origin of the session
            preserve_system_prompt: Whether to preserve the system prompt

        Returns:
            The full response structure from the agent including message, session_id, success, tool_calls, usage, etc.
        """
        if not agent_name:
            agent_name = self.default_agent_name

        # Log agent request if tracing enabled
        if trace_context:
            agent_request_payload = {
                "agent_name": agent_name,
                "message_content": message,
                "user_id": user_id,
                "user": user,
                "session_name": session_name,
                "message_type": message_type,
                "media_url": media_url,
                "media_contents": media_contents,
                "mime_type": mime_type,
                "context": context,
                "channel_payload": channel_payload,
                "session_origin": session_origin,
                "preserve_system_prompt": preserve_system_prompt,
            }
            trace_context.log_agent_request(agent_request_payload)

        # Record timing
        import time

        start_time = time.time()

        # Call run_agent
        result = self.run_agent(
            agent_name=agent_name,
            message_content=message,
            user_id=user_id,
            user=user,
            session_name=session_name,
            message_type=message_type,
            media_url=media_url,
            media_contents=media_contents,
            mime_type=mime_type,
            context=context,
            channel_payload=channel_payload,
            session_origin=session_origin,
            preserve_system_prompt=preserve_system_prompt,
        )

        # Debug log the result from run_agent
        logger.debug(f"run_agent returned: {result}")

        # Record processing time and log response
        processing_time = int((time.time() - start_time) * 1000)
        if trace_context:
            trace_context.log_agent_response(result, processing_time)

        # Fetch current session info to get the authoritative user_id
        # Make this optional and non-blocking to prevent response delays
        current_user_id = None
        if session_name:
            try:
                session_info = self.get_session_info(session_name)
                if session_info and "user_id" in session_info:
                    current_user_id = session_info["user_id"]
                    logger.info(f"Session {session_name} current user_id: {current_user_id}")
            except Exception as e:
                logger.warning(f"Failed to fetch session info for {session_name}: {e}")
                # Don't let session info failure affect the main response
                current_user_id = None

        # Return the full response structure
        if isinstance(result, dict):
            if "error" in result and result.get("error") and result.get("success") is False:
                # Convert error to agent response format (only if error is non-empty and success is False)
                response = {
                    "message": result.get("error", "Desculpe, encontrei um erro."),
                    "success": False,
                    "session_id": None,
                    "tool_calls": [],
                    "tool_outputs": [],
                    "usage": {},
                    "error": result.get("details", ""),
                }
            else:
                # Return the full response (already in correct format from run_agent)
                response = result
        else:
            # Convert non-dict result to agent response format
            response = {
                "message": str(result),
                "success": True,
                "session_id": None,
                "tool_calls": [],
                "tool_outputs": [],
                "usage": {},
            }

        # Add the current user_id from session to the response
        if current_user_id:
            response["current_user_id"] = current_user_id

        return response


# Singleton instance
agent_api_client = AgentApiClient()

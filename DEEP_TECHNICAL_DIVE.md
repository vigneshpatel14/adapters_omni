# Automagik Omni - Deep Technical Dive: Message Flow

## Complete Message Lifecycle - Step by Step

This document traces a single message from WhatsApp user → Omni → Agent → WhatsApp user with exact code paths.

---

## Phase 1: User Sends WhatsApp Message

### User Action
```
WhatsApp User → Types message → Sends
```

### Evolution API Receives
Evolution API (running at your configured URL) detects the message from your WhatsApp instance and prepares a webhook.

---

## Phase 2: Webhook Arrives at Omni API

### HTTP Request

```
POST /api/v1/webhook/evolution/echo-test HTTP/1.1
Host: localhost:8882
Content-Type: application/json

{
  "event": "messages.upsert",
  "data": {
    "message": {
      "key": {
        "id": "XXXXXXXXXXXX@c.us",
        "fromMe": false,
        "remoteJid": "+1234567890@s.whatsapp.net",
        "participant": null
      },
      "messageTimestamp": 1702250400,
      "pushName": "John Doe",
      "status": "ERROR",
      "message": {
        "conversation": "Hello Omni!"
      },
      "sidecar": null
    }
  }
}
```

### Omni Webhook Handler

**File**: `src/api/app.py`

```python
@app.post("/api/v1/webhook/evolution/{instance_name}")
async def evolution_webhook(
    instance_name: str,
    request: Request,
    db: Session = Depends(get_database)
):
    """Receive Evolution API webhook."""
    
    # 1. Parse request body
    body = await request.json()
    logger.info(f"Webhook received: {body['event']} for instance {instance_name}")
    
    # 2. Log incoming request
    track_api_request(
        path="/api/v1/webhook/evolution/{instance_name}",
        method="POST",
        timestamp=now(),
        status_code=200
    )
    
    # 3. Validate instance exists
    instance = db.query(InstanceConfig).filter(
        InstanceConfig.name == instance_name
    ).first()
    
    if not instance:
        logger.error(f"Instance not found: {instance_name}")
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # 4. Create trace context
    trace_context = StreamingTraceContext(
        instance_id=instance.id,
        trace_id=generate_uuid(),
        source_channel="whatsapp",
        created_at=now()
    )
    
    # 5. Log in trace
    trace_service.log_incoming_webhook(trace_context, body)
    
    # 6. Route to message handler
    await handle_whatsapp_webhook(body, instance, trace_context)
    
    return {"status": "received"}
```

---

## Phase 3: WhatsApp Handler Processes Message

### Entry Point

**File**: `src/channels/whatsapp/handlers.py`

```python
def handle_message(message: Dict[str, Any], instance_config=None, trace_context=None):
    """Queue a message for processing."""
    
    # Extract message data
    event = message.get("event")  # "messages.upsert"
    data = message.get("data", {})
    msg_obj = data.get("message", {})
    
    logger.info(f"WhatsApp message received: {event}")
    
    # Queue for async processing
    message_data = {
        "message": message,
        "instance_config": instance_config,
        "trace_context": trace_context,
    }
    message_handler.message_queue.put(message_data)
```

### Process Message Thread

**File**: `src/channels/whatsapp/handlers.py` → `_process_message()`

```python
def _process_message(self, message: Dict[str, Any], instance_config, trace_context):
    """Process a single message."""
    
    # 1. Extract message metadata
    data = message.get("data", {})
    msg_obj = data.get("message", {})
    key = msg_obj.get("key", {})
    
    # Message ID
    message_id = key.get("id", "unknown")
    
    # Sender phone (from Evolution format: "+123456789@s.whatsapp.net")
    remote_jid = key.get("remoteJid", "")
    phone = self._extract_phone_from_jid(remote_jid)  # "+1234567890"
    
    # Is from me? (skip if true)
    from_me = key.get("fromMe", False)
    if from_me:
        logger.debug("Ignoring message from bot")
        return
    
    # 2. Extract message content
    message_body = msg_obj.get("message", {})
    message_type = self._determine_message_type(message_body)
    
    # Handle text
    if "conversation" in message_body:
        text = message_body["conversation"]
    # Handle image/video/document
    elif "imageMessage" in message_body:
        # Transcribe image or extract text
        text = self._process_image(message_body["imageMessage"])
    elif "audioMessage" in message_body:
        # Transcribe audio to text
        text = self._transcribe_audio(message_body["audioMessage"])
    else:
        text = "(unsupported message type)"
    
    logger.info(f"Extracted text from {phone}: {text}")
    
    # 3. Create/get user session
    user = {
        "phone_number": phone,
        "email": None,  # Will get from Automagik API later
        "user_data": {}
    }
    
    session_name = phone  # Human-readable session ID
    
    # 4. Route message
    logger.info(f"Routing to agent: {instance_config.default_agent}")
    
    response_text = message_router.route_message(
        message_text=text,
        user=user,
        session_name=session_name,
        message_type="text",
        session_origin="whatsapp",
        agent_config={"instance_config": instance_config},
        trace_context=trace_context
    )
    
    # 5. Send response back
    if response_text:
        evolution_api_sender.send_text_message(
            instance_config=instance_config,
            phone=phone,
            text=response_text,
            trace_context=trace_context
        )
    
    # 6. Update trace
    trace_service.log_message_sent(trace_context, response_text)
    
    logger.info(f"Message processed and response sent to {phone}")
```

---

## Phase 4: Message Router

### Route the Message

**File**: `src/services/message_router.py`

```python
def route_message(
    self,
    message_text: str,
    user: Dict[str, Any],
    session_name: str,
    message_type: str = "text",
    session_origin: str = "whatsapp",
    agent_config: Optional[Dict[str, Any]] = None,
    trace_context = None
) -> str:
    """Route message to appropriate handler."""
    
    logger.info(f"Routing message to agent: {message_text}")
    
    # 1. Extract instance config from agent_config
    instance_config = agent_config.get("instance_config")
    
    logger.info(f"Instance: {instance_config.name}")
    logger.info(f"Agent API: {instance_config.agent_api_url}")
    
    # 2. Access Control Check
    try:
        # Get phone number for ACL
        phone_for_acl = user.get("phone_number")
        
        # Check if allowed/blocked
        is_allowed = access_control_service.check_access(
            instance_id=instance_config.id,
            phone_number=phone_for_acl
        )
        
        if not is_allowed:
            logger.warning(f"Access denied for {phone_for_acl}")
            trace_service.log_access_denied(trace_context, phone_for_acl)
            return "You are not authorized to use this service."
    
    except Exception as e:
        logger.error(f"ACL check failed: {e}")
        # Fail open (allow) if ACL service errors
    
    # 3. Get or create user session
    session_id = user_service.get_or_create_session(
        instance_id=instance_config.id,
        phone_number=user.get("phone_number"),
        session_name=session_name,
        session_origin=session_origin
    )
    
    # 4. Prepare agent request payload
    agent_request = {
        "user_id": user.get("phone_number"),  # User ID
        "session_id": session_id,              # Session ID
        "session_name": session_name,          # Human-readable name
        "message": message_text,                # The actual message
        "message_type": message_type,           # "text", "image", etc.
        "session_origin": session_origin,       # "whatsapp"
        "user": user,                           # User object with phone, email, etc.
        "context": {                            # Additional context
            "channel": instance_config.channel_type,
            "instance": instance_config.name,
            "timestamp": now().isoformat()
        }
    }
    
    logger.debug(f"Agent request: {json.dumps(agent_request, indent=2)}")
    
    # 5. Log agent request in trace
    trace_service.log_agent_request(trace_context, agent_request)
    
    # 6. Call agent API
    logger.info(f"Calling agent at {instance_config.agent_api_url}")
    
    agent_response = agent_api_client.call_agent(
        agent_url=instance_config.agent_api_url,
        agent_key=instance_config.agent_api_key,
        payload=agent_request,
        timeout=instance_config.agent_timeout,
        trace_context=trace_context
    )
    
    # 7. Extract response text
    if isinstance(agent_response, dict):
        response_text = agent_response.get("text", "No response")
    else:
        response_text = str(agent_response)
    
    logger.info(f"Agent response: {response_text}")
    
    # 8. Log agent response in trace
    trace_service.log_agent_response(trace_context, agent_response)
    
    return response_text
```

---

## Phase 5: Call Your Agent

### Agent API Client

**File**: `src/services/agent_api_client.py`

```python
class AgentAPIClient:
    """Client for calling remote agent APIs."""
    
    def call_agent(
        self,
        agent_url: str,
        agent_key: str,
        payload: Dict[str, Any],
        timeout: int = 60,
        trace_context = None
    ) -> Dict[str, Any]:
        """Call agent API endpoint."""
        
        # 1. Prepare request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {agent_key}"
        }
        
        endpoint = f"{agent_url}/api/agent/chat"
        
        logger.info(f"Calling agent: {endpoint}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        # 2. Start timer
        start_time = time.time()
        
        try:
            # 3. Make HTTP request
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            # 4. Check status
            response.raise_for_status()
            
            # 5. Parse response
            agent_response = response.json()
            
            # 6. Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Agent responded in {duration_ms}ms")
            logger.debug(f"Response: {json.dumps(agent_response, indent=2)}")
            
            # 7. Log in trace
            if trace_context:
                trace_context.agent_duration_ms = duration_ms
            
            return agent_response
        
        except requests.Timeout:
            logger.error(f"Agent timeout after {timeout}s")
            if trace_context:
                trace_service.log_error(trace_context, f"Agent timeout after {timeout}s")
            return {"text": "Sorry, agent took too long to respond."}
        
        except requests.RequestException as e:
            logger.error(f"Agent call failed: {e}")
            if trace_context:
                trace_service.log_error(trace_context, str(e))
            return {"text": "Sorry, I couldn't process your request."}
```

### Your Echo Agent Receives

**Your agent (`agent-echo.py`)**

```python
@app.post("/api/agent/chat")
async def chat(request: AgentRequest):
    """Process a message and return echo response."""
    
    logger.info(f"Received: {request.message}")
    
    # Echo the message
    echo_text = f"[Echo from {request.session_origin}] {request.message}"
    
    return AgentResponse(text=echo_text)
```

### Agent Returns Response

```json
{
  "text": "[Echo from whatsapp] Hello Omni!"
}
```

---

## Phase 6: Send Response Back to WhatsApp

### Response Handler

**File**: `src/channels/whatsapp/handlers.py` (back in `_process_message`)

```python
# After agent returns response...

response_text = message_router.route_message(...)

if response_text:
    # Send back to WhatsApp
    evolution_api_sender.send_text_message(
        instance_config=instance_config,
        phone=phone,  # "+1234567890"
        text=response_text,  # "[Echo from whatsapp] Hello Omni!"
        trace_context=trace_context
    )
```

### Evolution API Sender

**File**: `src/channels/whatsapp/evolution_api_sender.py`

```python
class EvolutionAPISender:
    """Send messages via Evolution API to WhatsApp."""
    
    def send_text_message(
        self,
        instance_config,
        phone: str,
        text: str,
        trace_context = None
    ) -> bool:
        """Send text message via Evolution API."""
        
        # 1. Validate phone format
        phone_jid = f"{phone.lstrip('+')}@s.whatsapp.net"  # Convert to JID format
        
        logger.info(f"Sending message to {phone}: {text}")
        
        # 2. Prepare Evolution API request
        headers = {
            "Content-Type": "application/json",
            "apikey": instance_config.evolution_key
        }
        
        payload = {
            "number": phone_jid,
            "text": text,
            "delay": 1000  # 1 second delay between messages
        }
        
        endpoint = f"{instance_config.evolution_url}/message/sendText/{instance_config.whatsapp_instance}"
        
        logger.info(f"Evolution API call: {endpoint}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        # 3. Start timer
        start_time = time.time()
        
        try:
            # 4. Call Evolution API
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # 5. Check status
            response.raise_for_status()
            
            # 6. Parse response
            result = response.json()
            
            # 7. Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Message sent successfully in {duration_ms}ms")
            logger.debug(f"Evolution response: {json.dumps(result, indent=2)}")
            
            # 8. Update trace
            if trace_context:
                trace_service.log_outgoing_message(
                    trace_context,
                    phone=phone,
                    text=text,
                    status="sent",
                    duration_ms=duration_ms
                )
            
            return True
        
        except requests.Timeout:
            logger.error("Evolution API timeout")
            if trace_context:
                trace_service.log_error(trace_context, "Evolution API timeout")
            return False
        
        except requests.RequestException as e:
            logger.error(f"Evolution API error: {e}")
            if trace_context:
                trace_service.log_error(trace_context, str(e))
            return False
```

### Evolution API Makes HTTP Call to WhatsApp

Evolution API has your WhatsApp session and makes native WhatsApp API call:

```
Evolution API → WhatsApp Cloud API
                      ↓
                  WhatsApp Servers
                      ↓
                  User's Phone
```

---

## Phase 7: Complete - User Receives Response

```
[Your WhatsApp Phone]
        ↓
    Message appears:
    "[Echo from whatsapp] Hello Omni!"
```

---

## Phase 8: Trace Recording

### Full Lifecycle Trace

**File**: `src/services/trace_service.py`

Throughout the entire flow, messages are logged to the trace:

```python
class TraceService:
    """Log complete message lifecycle."""
    
    def log_complete_trace(self, trace_context):
        """Create complete trace entry."""
        
        trace = MessageTrace(
            id=generate_uuid(),
            instance_id=trace_context.instance_id,
            trace_id=trace_context.trace_id,
            created_at=trace_context.created_at,
            
            # Message flow
            status=trace_context.status,  # "sent", "error", etc.
            source_channel="whatsapp",
            source_user_id=trace_context.source_user_id,
            session_id=trace_context.session_id,
            
            # Payloads
            incoming_payload=trace_context.incoming_webhook,
            agent_request_payload=trace_context.agent_request,
            agent_response_payload=trace_context.agent_response,
            outgoing_payload=trace_context.outgoing_message,
            
            # Performance
            duration_ms=trace_context.total_duration_ms,
            agent_duration_ms=trace_context.agent_duration_ms,
            
            # Errors (if any)
            error_message=trace_context.error_message,
            error_traceback=trace_context.error_traceback
        )
        
        # Save to database
        db.add(trace)
        db.commit()
        
        logger.info(f"Trace recorded: {trace_id}")
```

### Query Traces

```bash
curl -H "x-api-key: your-api-key" \
  "http://localhost:8882/api/v1/traces?instance_name=echo-test&page=1"
```

Returns:
```json
{
  "traces": [
    {
      "trace_id": "550e8400-...",
      "instance_name": "echo-test",
      "status": "sent",
      "source_user_id": "+1234567890",
      "incoming_payload": { ... },
      "agent_request_payload": { ... },
      "agent_response_payload": { ... },
      "outgoing_payload": { ... },
      "duration_ms": 245,
      "agent_duration_ms": 12,
      "created_at": "2025-12-10T..."
    }
  ],
  "total": 1,
  "page": 1
}
```

---

## Complete Call Stack

```
User sends WhatsApp message
    ↓
Evolution API webhook
    ↓
POST /api/v1/webhook/evolution/echo-test
    ↓ [src/api/app.py]
evolution_webhook()
    ↓
handle_whatsapp_webhook()
    ↓ [src/channels/whatsapp/handlers.py]
WhatsAppMessageHandler.handle_message()
    ↓
Message queued → _process_messages_loop()
    ↓
_process_message()
    ├─ Extract message data & phone
    ├─ Transcribe audio (if needed)
    └─ message_router.route_message()
        ↓ [src/services/message_router.py]
        ├─ Access control check
        ├─ Create/get user session
        ├─ agent_api_client.call_agent()
        │   ↓ [src/services/agent_api_client.py]
        │   └─ POST to your agent endpoint (http://localhost:8886/api/agent/chat)
        │       ↓
        │       Your Echo Agent Receives & Responds
        │       ↓
        │       Return {"text": "[Echo from whatsapp] ..."}
        │   ↓
        │   Return response to message_router
        │
        └─ Return response text
    ↓
evolution_api_sender.send_text_message()
    ↓ [src/channels/whatsapp/evolution_api_sender.py]
    ├─ Format phone number
    └─ POST to Evolution API
        ↓
        Evolution API sends to WhatsApp
            ↓
            WhatsApp sends to user's phone
                ↓
                User receives message
                
[THROUGHOUT] trace_service.log_*() records lifecycle
```

---

## Performance Metrics (Typical)

For a message flow:

| Step | Duration | Notes |
|------|----------|-------|
| Webhook received to handler | 5-10ms | Network + queuing |
| WhatsApp message processing | 20-50ms | Parsing, transcription if audio |
| Message Router setup | 5-10ms | Database queries |
| Agent API call | 50-200ms | Depends on agent |
| Evolution API send | 100-300ms | WhatsApp cloud API latency |
| **Total** | **180-570ms** | End-to-end |

---

## Error Handling

### At Each Stage

1. **Webhook parsing fails** → Return 400 Bad Request
2. **Instance not found** → Return 404 Not Found
3. **Access denied** → Log warning, respond with "unauthorized"
4. **Agent timeout** → Return "took too long"
5. **Agent returns error** → Log error, don't send to WhatsApp
6. **Evolution API fails** → Retry logic (if configured), log error
7. **Database error** → Return 500, log full traceback

### Trace Error Recording

```python
trace_service.log_error(trace_context, error_message)
# Stores error_message and full traceback in MessageTrace
```

---

## Key Insights

1. **Message queuing** ensures WhatsApp webhooks don't block
2. **Async processing** allows handling multiple messages simultaneously
3. **Access control** runs before agent call (security first)
4. **Tracing** runs in parallel with processing (minimal performance impact)
5. **Timeouts** protect against hanging agents
6. **Error messages** returned to user instead of crashing

---

## Next: Replace Echo with Real Agent

Once you understand this flow, replace the echo agent with:
- LLM integration (OpenAI, Claude, etc.)
- Database lookups (customer info)
- External APIs (weather, calendar, etc.)
- Complex business logic

The Omni framework stays the same - just change what happens in your `/api/agent/chat` endpoint!

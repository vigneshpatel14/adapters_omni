# ADVANCED TOPICS & FAQ: Automagic Omni ↔ Leo Streaming Integration

**Last Updated:** December 15, 2025  
**Status:** Production Ready  
**Version:** 1.0  
**Audience:** Technical experts, architects, advanced users

---

## Table of Contents

1. [Multi-Tenancy & Instance Routing](#multi-tenancy--instance-routing)
2. [Security & Access Control](#security--access-control)
3. [Message Streaming & Delta Handling](#message-streaming--delta-handling)
4. [Performance & Optimization](#performance--optimization)
5. [Advanced Configuration](#advanced-configuration)
6. [Troubleshooting Complex Issues](#troubleshooting-complex-issues)
7. [Production Deployment](#production-deployment)

---

## Multi-Tenancy & Instance Routing

### Q1: If a WhatsApp number is registered in multiple Omni instances, which instance handles the message?

**Context:** You have:
- Instance A: `company-a-bot` (webhook: `/webhook/evolution/company-a-bot`)
- Instance B: `company-b-bot` (webhook: `/webhook/evolution/company-b-bot`)
- Same WhatsApp number: +1-555-1234567

**Problem:** When a message arrives at Evolution API from this number, which instance processes it?

**Answer:**

```
Evolution API → WhatsApp sends message → Evolution API webhook triggers

Evolution API sends webhook to: /webhook/evolution/WHICH_INSTANCE?
```

**The routing is determined by Evolution API, NOT Omni:**

1. **Evolution API Instance Name** - Each Evolution instance is separate
   ```
   Instance A → Evolution instance: "company-a-bot"
   Instance B → Evolution instance: "company-b-bot"
   ```

2. **Webhook URL Points to Specific Instance**
   ```
   Instance A webhook: http://localhost:8882/webhook/evolution/company-a-bot
   Instance B webhook: http://localhost:8882/webhook/evolution/company-b-bot
   ```

3. **Message Routes to Webhook Handler**
   ```python
   # In Omni API
   @app.post("/webhook/evolution/{instance_name}")
   async def webhook_evolution(instance_name: str, request: Request):
       # instance_name tells us which instance to use
       instance = get_instance(instance_name)  # Gets Instance A or B
       # Process message with that instance's config
   ```

**Technical Flow:**

```
WhatsApp User (Same number +1-555-1234567)
     │
     ├─ Sends message to Instance A's WhatsApp number
     │  │
     │  └─ Evolution API (for Instance A)
     │     │
     │     └─ Webhook to: /webhook/evolution/company-a-bot
     │        │
     │        └─ Omni routes to Instance A config
     │           └─ Uses Instance A's agent API
     │
     └─ Sends message to Instance B's WhatsApp number
        │
        └─ Evolution API (for Instance B)
           │
           └─ Webhook to: /webhook/evolution/company-b-bot
              │
              └─ Omni routes to Instance B config
                 └─ Uses Instance B's agent API
```

**Key Point:** The user must send to **different WhatsApp numbers** for each instance. You can't have the same number in multiple instances because:
- Each Evolution instance is separate
- Each has its own WhatsApp number
- The webhook URL contains the instance name

**Example Configuration:**

```
Instance A: company-a-bot
├─ WhatsApp Number: +1-555-1111111 (from Evolution instance "company-a-bot")
├─ Webhook: /webhook/evolution/company-a-bot
└─ Messages sent to +1-555-1111111 → Instance A

Instance B: company-b-bot
├─ WhatsApp Number: +1-555-2222222 (from Evolution instance "company-b-bot")
├─ Webhook: /webhook/evolution/company-b-bot
└─ Messages sent to +1-555-2222222 → Instance B
```

---

### Q2: Can I share one WhatsApp number across multiple instances?

**Short Answer:** ❌ **Not recommended** and technically problematic.

**Why it doesn't work:**

```
Same WhatsApp number in multiple Evolution instances = conflict
Evolution API: "Which instance should handle this message?"
Result: Unpredictable routing or one instance overrides the other
```

**What you SHOULD do:**

1. **One WhatsApp number per instance** (recommended)
   ```
   Instance A → WhatsApp number: +1-555-1111
   Instance B → WhatsApp number: +1-555-2222
   ```

2. **Use routing based on message content** (alternative)
   ```
   One WhatsApp number → Multiple agents based on keyword
   
   Instance with multi-agent support:
   ├─ If message starts with "!a" → Route to Agent A
   ├─ If message starts with "!b" → Route to Agent B
   └─ Else → Default agent
   ```

3. **Use phone number suffix routing** (if you own the number)
   ```
   Base: +1-555-1234567
   Instance A: +1-555-1234567 (main number)
   Instance B: +1-555-1234568 (forwarded to same user, different instance)
   ```

---

## Security & Access Control

### Q3: If our WhatsApp number is public, anyone can message us and reach the agent. How do we prevent unauthorized access?

**Critical Security Concern:** ✅ **Yes, this is a real vulnerability if not handled!**

**The Problem:**

```
Public WhatsApp Number (on website, business card, etc.)
     │
     └─ Anyone can message it
        │
        └─ Omni receives message
           │
           └─ Calls agent API
              │
              └─ Anyone can reach your agent
                 └─ SECURITY HOLE! 🚨
```

**Solutions (in order of security level):**

### Solution 1: Access Control Lists (Recommended for Production)

**Allow List (Whitelist):**
```bash
curl -X POST http://localhost:8882/api/v1/instances/company-a-bot/access-control \
  -H "x-api-key: omni-dev-key-test-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "allow",
    "phone_number": "+1-555-9876543",
    "type": "user"
  }'
```

**Block List (Blacklist):**
```bash
curl -X POST http://localhost:8882/api/v1/instances/company-a-bot/access-control \
  -H "x-api-key: omni-dev-key-test-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "block",
    "phone_number": "+1-555-1234567",
    "type": "user"
  }'
```

**How it works:**
```python
# In Omni webhook handler
def process_webhook(instance, message):
    user_phone = extract_phone(message)  # +1-555-9876543
    
    # Check access control
    if is_blocked(user_phone, instance):
        return {"status": "blocked", "message": "Access denied"}
    
    if has_allow_list(instance):
        if not is_allowed(user_phone, instance):
            return {"status": "not_allowed", "message": "Access denied"}
    
    # Proceed to agent
    return process_with_agent(instance, message)
```

**Configuration Examples:**

```
Instance with ALLOW LIST only (most restrictive):
├─ Allow: +1-555-1111111 (CEO)
├─ Allow: +1-555-2222222 (Customer Support)
└─ All others: DENIED
   Result: Only 2 people can access agent

Instance with BLOCK LIST (less restrictive):
├─ Block: +1-555-spam1
├─ Block: +1-555-spam2
└─ All others: ALLOWED
   Result: Anyone except 2 people can access agent
```

### Solution 2: Pattern-Based Filtering

**Block spam patterns:**
```python
# In agent_service.py
def is_spam_message(message_text):
    spam_keywords = [
        "casino", "lottery",
        "click here", "win now"
    ]
    return any(keyword in message_text.lower() for keyword in spam_keywords)

def process_webhook(instance, message):
    if is_spam_message(message.text):
        return {"status": "spam_blocked"}
    
    # Continue processing
```

### Solution 3: Rate Limiting (Prevent abuse)

**Per-user rate limiting:**
```python
# Limit: 10 messages per minute per user
RATE_LIMITS = {}

def check_rate_limit(user_phone, instance_id):
    key = f"{instance_id}:{user_phone}"
    current_time = time.time()
    
    if key not in RATE_LIMITS:
        RATE_LIMITS[key] = {"count": 0, "window_start": current_time}
    
    limit_data = RATE_LIMITS[key]
    
    # Reset window if > 60 seconds
    if current_time - limit_data["window_start"] > 60:
        limit_data = {"count": 0, "window_start": current_time}
        RATE_LIMITS[key] = limit_data
    
    limit_data["count"] += 1
    
    if limit_data["count"] > 10:
        return False  # Rate limit exceeded
    
    return True  # OK to process
```

### Solution 4: Authentication Token (For API Access)

**If users call agent API directly (not via WhatsApp):**
```python
@app.post("/api/agent/chat")
async def chat(request: AgentRequest, token: str = Header(...)):
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Process request
```

### Solution 5: Private WhatsApp Group

**Don't use public number, use:**
- Closed WhatsApp group (invite only)
- Only approved members can message
- Omni receives from group instead of personal chat

---

### Q4: What if someone gets a customer's API key? How do we prevent misuse?

**Threat:** API key leaked → attacker can access instance

**Mitigations:**

1. **Use short-lived API keys**
   ```python
   # API key expires after 30 days
   api_key_expiry = created_at + timedelta(days=30)
   if datetime.now() > api_key_expiry:
       return {"error": "API key expired"}
   ```

2. **Rotate keys regularly**
   ```bash
   # Monthly key rotation
   Old Key: abc123xyz789 (expires end of Dec)
   New Key: def456uvw012 (valid from Dec 15 onwards)
   ```

3. **Use scoped API keys**
   ```
   Scope 1: Read-only (view instances, traces)
   Scope 2: Write access (modify instances)
   Scope 3: Agent call (call agent API)
   
   Give different scopes to different teams
   ```

4. **Log all API key usage**
   ```python
   # Every API call logs: who, what, when, from where
   LOG: {
       "api_key": "abc123***",  # masked
       "endpoint": "/api/v1/instances",
       "timestamp": "2025-12-15T14:30:00Z",
       "ip_address": "192.168.1.1",
       "method": "GET",
       "status": 200
   }
   ```

5. **Alert on suspicious activity**
   ```
   Alerts trigger if:
   ├─ Same key used from 2 different IPs in 1 minute
   ├─ Key used more than 1000x in 1 hour (bot detected)
   ├─ Key used at unusual times
   └─ Key used from different country than normal
   ```

---

## Message Streaming & Delta Handling

### Q5: WhatsApp messages arrive in streaming format. How does one-by-one delivery work? Is it per-character or per-delta?

**Context:** Leo API returns SSE (Server-Sent Events) with `TEXT_MESSAGE_CONTENT` deltas.

**How Streaming Works:**

**Not One-by-One Character:**
```
❌ WRONG: Message comes character by character
   D → e → l → i → v → e → r → e → d

✅ RIGHT: Message comes in semantic deltas
   "Hello " → "from " → "Leo" → " agent"
```

**What are Deltas?**

Leo's streaming response:
```
event: TEXT_MESSAGE_CONTENT
data: {"delta": "I am", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " Leo,", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " your AI", "type": "text"}

event: TEXT_MESSAGE_CONTENT
data: {"delta": " assistant.", "type": "text"}

event: RUN_FINISHED
data: {"final_response": "I am Leo, your AI assistant."}
```

**Adapter Processing:**
```python
def parse_leo_streaming_response(sse_stream):
    collected_text = ""
    
    for event in sse_stream:
        if event.type == "TEXT_MESSAGE_CONTENT":
            delta = json.loads(event.data)["delta"]
            collected_text += delta
            
            # Log each delta as it arrives
            print(f"Received delta: '{delta}'")
            print(f"Accumulated: '{collected_text}'")
        
        elif event.type == "RUN_FINISHED":
            final_response = json.loads(event.data)["final_response"]
            return final_response
    
    return collected_text
```

**Real Example:**

```
Timestamp    Event                           Accumulated Text
─────────────────────────────────────────────────────────────
T+0ms        RUN_STARTED
T+50ms       TEXT_MESSAGE_CONTENT: "Hello"  "Hello"
T+100ms      TEXT_MESSAGE_CONTENT: ","      "Hello,"
T+150ms      TEXT_MESSAGE_CONTENT: " I"     "Hello, I"
T+200ms      TEXT_MESSAGE_CONTENT: "'m"     "Hello, I'm"
T+250ms      TEXT_MESSAGE_CONTENT: " Leo"   "Hello, I'm Leo"
T+300ms      RUN_FINISHED                   (final message ready)
```

### Q6: What triggers a new delta from Leo? Is it based on sentence, paragraph, or streaming snapshot?

**Answer:** Deltas are based on **Leo's internal token streaming**, not your WhatsApp message structure.

**How Leo decides when to send a delta:**

```
Leo's LLM generates response token by token:
┌─────────────────────────────────────────┐
│ Token Stream from Leo's Language Model  │
│ ────────────────────────────────────────│
│ Token 1: "Hello"                        │
│ Token 2: ","                            │
│ Token 3: "I'm"                          │
│ Token 4: "Leo"                          │
│ ...                                     │
└─────────────────────────────────────────┘
         │
         └─ SSE sends as soon as token ready
            (Not waiting for sentence/paragraph)
```

**Not sentence-based:**
```
❌ WRONG: Leo waits for complete sentence
   Waits... waits... then sends: "Hello, I'm Leo"

✅ RIGHT: Leo streams immediately as tokens arrive
   Sends: "Hello" → "," → "I'm" → "Leo"
   (Could be mid-sentence, that's fine)
```

**Why this matters for WhatsApp:**

```
User sees response appearing in real-time:
✓ "Hello" appears immediately
✓ User sees typing happening
✓ Creates sense of live conversation
✓ Feels more responsive

vs.

Waiting for full response:
✗ 5 seconds of silence
✗ Then entire message appears at once
✗ Feels slow and unresponsive
```

### Q7: What happens if the user closes the chat while streaming? Does Omni still wait for completion?

**Scenario:**
```
User sends message to Leo
Leo starts streaming response
User closes WhatsApp chat before response complete
```

**What Happens:**

```
User closes chat
     │
     ├─ WebSocket from Evolution API closes
     │
     ├─ Leo adapter still calling Leo API
     │
     ├─ Leo is still generating response
     │
     └─ Adapter finishes receiving all deltas
        │
        └─ Returns complete response to Omni
           │
           └─ Omni tries to send back via Evolution API
              │
              └─ But user's chat is closed
                 │
                 └─ Message queues (Evolution API handles)
```

**Technical Details:**

```python
# In adapter
@app.post("/api/agent/chat")
async def chat(request: AgentRequest):
    # This is HTTP request, not WebSocket
    # It completes regardless of whether user reads it
    
    response_text = call_leo_streaming_api(request.message)
    
    # Return even if user closed chat
    return {"text": response_text}  # HTTP request completes
```

**Key Point:** The adapter **doesn't know** user closed chat because it's using HTTP, not WebSocket. It completes the call regardless.

**What Evolution API does:**

```
Evolution API receives response from Omni
     │
     ├─ If user chat still open → delivers immediately
     │
     └─ If user chat closed → queues message
        (Delivered when user opens chat next)
```

---

## Performance & Optimization

### Q8: How long does the entire message flow take? Where are bottlenecks?

**Timeline Breakdown:**

```
Step                                    Time        Cumulative
─────────────────────────────────────────────────────────────
1. User sends WhatsApp message          0ms         0ms
2. WhatsApp → Evolution API             200-500ms   200-500ms
3. Evolution → Omni webhook             10-50ms     210-550ms
4. Omni processes webhook               5-10ms      215-560ms
5. Omni → Adapter API call              20-100ms    235-660ms
6. Adapter processes request            5-10ms      240-670ms
7. Adapter → Leo API call               50-200ms    290-870ms
   (network latency)
8. Leo API processes & streams          2000-5000ms 2290-5870ms ⚠️ BIGGEST
   (model inference + token generation)
9. Leo streaming complete               (included)  2290-5870ms
10. Adapter parses response             10-50ms     2300-5920ms
11. Adapter → Omni response             10-50ms     2310-5970ms
12. Omni → Evolution API send           20-100ms    2330-6070ms
13. Evolution → WhatsApp user           500-1000ms  2830-7070ms
────────────────────────────────────────────────────────────
TOTAL END-TO-END                        ~3-7 sec    2830-7070ms
```

**Bottleneck Identification:**

```
Biggest bottleneck: Step 8 (Leo AI inference)
├─ 70-80% of total time
├─ Can't be optimized (inherent to LLM)
└─ Mitigation: Use faster models, or cache responses

Second: WhatsApp delivery (Step 2, 13)
├─ Network dependent
└─ Mitigation: None (out of our control)

Smallest: Omni processing (Step 4, 12)
├─ Only ~100ms total
└─ Already optimized
```

### Q9: Can we cache responses to speed up similar messages?

**Yes! Caching strategies:**

**Strategy 1: Exact Message Matching**
```python
# Cache if exact same message asked before
RESPONSE_CACHE = {}

def get_agent_response(user_id, message, instance_id):
    cache_key = f"{instance_id}:{message}"
    
    if cache_key in RESPONSE_CACHE:
        cached_response = RESPONSE_CACHE[cache_key]
        if time.time() - cached_response["timestamp"] < 3600:  # 1 hour
            return cached_response["response"]
    
    # Not in cache, call Leo
    response = call_leo_api(message)
    
    # Store in cache
    RESPONSE_CACHE[cache_key] = {
        "response": response,
        "timestamp": time.time()
    }
    
    return response
```

**Strategy 2: Semantic Similarity**
```python
# Cache if similar message already answered
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def find_similar_cached_response(message):
    # Get embedding of current message
    message_embedding = model.encode(message)
    
    for cached_msg, response in CACHE.items():
        cached_embedding = model.encode(cached_msg)
        
        # Calculate similarity (cosine)
        similarity = cosine_similarity(message_embedding, cached_embedding)
        
        if similarity > 0.9:  # 90% similar
            return response  # Return cached response
    
    return None  # Not similar enough
```

**Strategy 3: Intent-Based Caching**
```python
# Cache based on intent, not exact message
INTENT_CACHE = {
    "greeting": "Hello! How can I help you today?",
    "pricing": "Our pricing is $50/month for basic...",
    "support": "Support team available Mon-Fri 9-5..."
}

def detect_intent(message):
    if any(word in message.lower() for word in ["hi", "hello", "hey"]):
        return "greeting"
    elif any(word in message.lower() for word in ["price", "cost", "cheap"]):
        return "pricing"
    elif any(word in message.lower() for word in ["support", "help", "issue"]):
        return "support"
    return None

def get_response(message):
    intent = detect_intent(message)
    
    if intent and intent in INTENT_CACHE:
        return INTENT_CACHE[intent]  # Instant response!
    
    # Not in cache, call Leo
    return call_leo_api(message)
```

---

## Advanced Configuration

### Q10: Can one instance route to multiple agents based on message content?

**Yes! Multi-Agent Routing:**

```python
# In message_router.py
def route_to_agent(instance, message):
    # Detect intent/category
    intent = extract_intent(message.text)
    
    # Route to appropriate agent
    if intent == "technical":
        agent_url = instance.technical_agent_url
        agent_key = instance.technical_agent_key
    elif intent == "billing":
        agent_url = instance.billing_agent_url
        agent_key = instance.billing_agent_key
    elif intent == "sales":
        agent_url = instance.sales_agent_url
        agent_key = instance.sales_agent_key
    else:
        agent_url = instance.default_agent_url  # Fallback
        agent_key = instance.default_agent_key
    
    # Call appropriate agent
    return call_agent(agent_url, agent_key, message)
```

**Instance Configuration:**
```json
{
  "name": "multi-agent-bot",
  "default_agent_url": "http://leo-adapter:8887",
  "technical_agent_url": "http://technical-agent:8888",
  "billing_agent_url": "http://billing-agent:8889",
  "sales_agent_url": "http://sales-agent:8890",
  "routing_strategy": "intent-based"
}
```

---

### Q11: How do we handle multi-turn conversations? Does context persist?

**Session Context Handling:**

```python
# Session structure
SESSION = {
    "session_id": "session-abc123",
    "user_id": "whatsapp:+1-555-1234567",
    "instance_id": "company-a-bot",
    "messages": [
        {"role": "user", "content": "What's your pricing?"},
        {"role": "assistant", "content": "We offer 3 plans..."},
        {"role": "user", "content": "Can I upgrade later?"},
        {"role": "assistant", "content": "Yes, anytime..."}
    ],
    "created_at": "2025-12-15T10:00:00Z",
    "last_message_at": "2025-12-15T10:05:00Z",
    "expires_at": "2025-12-15T11:00:00Z"  # 1 hour timeout
}
```

**Passing Context to Agent:**
```python
@app.post("/api/agent/chat")
async def chat(request: AgentRequest):
    # Load session
    session = get_session(request.session_id)
    
    # Prepare context with conversation history
    context = {
        "messages": session.messages,  # Full history
        "user_profile": get_user_profile(request.user_id),
        "instance_config": get_instance(request.instance_id)
    }
    
    # Agent receives full context
    agent_response = call_agent(
        url=instance.agent_api_url,
        message=request.message,
        context=context,
        session_id=request.session_id
    )
    
    # Store in session
    session.messages.append({
        "role": "user",
        "content": request.message
    })
    session.messages.append({
        "role": "assistant",
        "content": agent_response
    })
    
    save_session(session)
    
    return {"text": agent_response}
```

**Session Storage Options:**
```
Option 1: In-Memory (Fast but loss on restart)
├─ Pros: Ultra-fast
└─ Cons: Lost if server restarts

Option 2: Redis (Fast + Persistent)
├─ Pros: Fast, survives restart
└─ Cons: Need Redis server

Option 3: Database (SQLite/PostgreSQL)
├─ Pros: Survives restart, searchable
└─ Cons: Slower than Redis

Option 4: Hybrid (Redis + Database)
├─ Hot data in Redis (last 24 hours)
├─ Cold data in Database (archives)
└─ Best of both worlds
```

---

## Troubleshooting Complex Issues

### Q12: What if Leo API returns an error but Omni still needs to respond to user?

**Scenarios & Handling:**

**Scenario 1: Leo API timeout**
```python
try:
    response = call_leo_api(message, timeout=120)
except TimeoutError:
    # Leo took too long, don't wait
    return {
        "text": "I'm thinking... this is taking longer than usual. Please wait or try again.",
        "status": "timeout",
        "fallback": True
    }
```

**Scenario 2: Leo API returns error (5xx)**
```python
try:
    response = call_leo_api(message)
except ServerError as e:
    # Leo API down
    return {
        "text": "Our AI is temporarily unavailable. Please try again in a moment.",
        "status": "error",
        "error_code": e.status_code,
        "fallback": True
    }
```

**Scenario 3: Invalid response from Leo**
```python
try:
    response = call_leo_api(message)
    
    if not response.get("text") or len(response["text"]) == 0:
        raise ValueError("Empty response from Leo")
    
    return response
except ValueError as e:
    # Leo returned empty or invalid response
    return {
        "text": "I didn't understand that. Could you rephrase?",
        "status": "invalid_response",
        "fallback": True
    }
```

**Scenario 4: Network issue (agent unreachable)**
```python
try:
    response = call_agent(url, message)
except ConnectionError:
    # Agent API unreachable
    return {
        "text": "Our system is temporarily offline. Please try again.",
        "status": "connection_error",
        "fallback": True
    }
```

**Fallback Strategy:**
```python
def get_fallback_response(error_type):
    fallbacks = {
        "timeout": "Taking longer than expected...",
        "leo_down": "AI temporarily unavailable",
        "invalid_response": "Didn't understand that",
        "network_error": "Connection issue",
        "rate_limited": "Too many requests, wait a moment"
    }
    return fallbacks.get(error_type, "Something went wrong, try again")
```

---

### Q13: How do we debug if messages are silently failing?

**Logging Strategy:**

```python
# Level 1: Basic logging
logger.info(f"Message received from {user_id}")
logger.info(f"Agent called: {agent_url}")
logger.info(f"Response: {response_text}")

# Level 2: Detailed tracing
trace = {
    "trace_id": generate_trace_id(),
    "timestamp": datetime.now().isoformat(),
    "user_id": user_id,
    "message": message_text,
    "steps": [
        {"name": "webhook_received", "status": "success", "duration_ms": 10},
        {"name": "instance_lookup", "status": "success", "duration_ms": 5},
        {"name": "access_check", "status": "success", "duration_ms": 20},
        {"name": "agent_call", "status": "success", "duration_ms": 3500},
        {"name": "response_parse", "status": "success", "duration_ms": 10},
        {"name": "evolution_send", "status": "success", "duration_ms": 150}
    ],
    "total_duration_ms": 3695,
    "status": "completed"
}
save_trace(trace)
```

**Query traces to find failures:**
```bash
# Find all failed messages
curl http://localhost:8882/api/v1/traces?status=failed \
  -H "x-api-key: omni-dev-key-test-2025"

# Find slow messages (>5 seconds)
curl http://localhost:8882/api/v1/traces?min_duration=5000 \
  -H "x-api-key: omni-dev-key-test-2025"

# Find messages from specific user
curl http://localhost:8882/api/v1/traces?user_id=whatsapp:+1-555-1234567 \
  -H "x-api-key: omni-dev-key-test-2025"
```

---

## Production Deployment

### Q14: How do we deploy Omni to production safely?

**Deployment Checklist:**

```
Pre-Deployment:
─────────────
☐ All tests passing
☐ No hardcoded credentials
☐ Environment variables configured
☐ Database backups in place
☐ API keys rotated
☐ Rate limiting enabled
☐ Access control lists configured
☐ Load testing done
☐ Monitoring & alerting setup
☐ Disaster recovery plan

Deployment:
──────────
☐ Use blue-green deployment
  └─ Old server still running (blue)
     New server starts (green)
     Switch traffic once new is healthy
     Keep old for rollback

☐ Gradual traffic shift
  └─ 10% traffic to new → monitor
     25% traffic → monitor
     50% traffic → monitor
     100% traffic → fully deployed

☐ Health checks
  └─ GET /health returns 200 OK
  └─ Database connection test
  └─ External API connectivity check

Post-Deployment:
───────────────
☐ Monitor error rates
☐ Monitor response times
☐ Monitor resource usage (CPU, memory)
☐ Monitor API key usage
☐ Watch for unusual patterns
☐ Have rollback procedure ready
```

### Q15: What metrics should we monitor in production?

**Key Metrics:**

```
1. Availability/Uptime
   ├─ Goal: 99.9% uptime
   ├─ Track: Downtime duration
   └─ Alert: If down > 1 minute

2. Response Time
   ├─ Goal: <5 seconds end-to-end
   ├─ Track: P50, P95, P99 latencies
   └─ Alert: If P95 > 8 seconds

3. Error Rate
   ├─ Goal: < 0.1% of requests
   ├─ Track: 4xx, 5xx errors
   └─ Alert: If error rate > 1%

4. Agent Success Rate
   ├─ Goal: >95% of messages processed
   ├─ Track: Successful vs failed agent calls
   └─ Alert: If success < 90%

5. API Usage
   ├─ Goal: Monitor for abuse
   ├─ Track: Requests per API key
   └─ Alert: If unusual spike (10x normal)

6. Database Performance
   ├─ Goal: Query time <100ms
   ├─ Track: Slow queries
   └─ Alert: If query > 500ms

7. Message Queue Depth
   ├─ Goal: Queue empty
   ├─ Track: Messages waiting to process
   └─ Alert: If queue growing (system can't keep up)

8. Cost Metrics
   ├─ Track: API calls to Leo ($ per month)
   ├─ Track: Server costs
   └─ Calculate: Cost per message processed
```

**Prometheus metrics example:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Counters (monotonically increasing)
messages_processed_total = Counter('messages_processed_total', 'Total messages')
errors_total = Counter('errors_total', 'Total errors', ['error_type'])

# Histograms (measure distribution)
request_latency = Histogram('request_latency_seconds', 'Request latency')
leo_api_latency = Histogram('leo_api_latency_seconds', 'Leo API latency')

# Gauges (up/down values)
active_sessions = Gauge('active_sessions', 'Currently active sessions')
queue_depth = Gauge('queue_depth', 'Messages in queue')

# Usage example
with request_latency.time():
    # Code block timed automatically
    process_message(message)

errors_total.labels(error_type='timeout').inc()
active_sessions.set(get_active_session_count())
```

---

## Summary Table

| Topic | Key Takeaway | Action |
|-------|-------------|--------|
| Multi-Tenancy | Different numbers per instance | Use separate Evolution instances |
| Security | Public number = anyone can access | Use allow/block lists + rate limiting |
| Streaming | Deltas sent as tokens ready | Not character-by-character, not waiting for sentences |
| Performance | Leo inference is bottleneck (70-80%) | Cache responses, use faster models if possible |
| Caching | Can cache exact, similar, or intent-based | Choose strategy based on use case |
| Multi-Agent | Route within one instance | Use intent detection + multiple agent URLs |
| Conversations | Context persists via session | Store in Redis or database |
| Error Handling | Always have fallback response | Never leave user waiting without response |
| Debugging | Use detailed tracing | Query traces to find failures |
| Production | Blue-green + gradual rollout | Monitor uptime, latency, errors, costs |

---

## Additional Resources

- [COMPLETE_SETUP_AND_CONFIGURATION_GUIDE.md](COMPLETE_SETUP_AND_CONFIGURATION_GUIDE.md) - Full setup details
- [COMPLETE_TESTING_GUIDE.md](COMPLETE_TESTING_GUIDE.md) - Testing procedures with examples
- [adapter-leo-agent.py](adapter-leo-agent.py) - Adapter source code
- [setup_leo_instance.py](setup_leo_instance.py) - Instance setup script

---

*Last Updated: December 15, 2025*  
*Questions? Check the sections above or review the complete guides.*

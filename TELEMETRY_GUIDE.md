# Telemetry in Automagic Omni - Quick Guide

**Last Updated:** December 19, 2025

---

## What is Telemetry?

**Simple Definition:** Telemetry is the automatic collection and transmission of data about system performance, usage, and events.

Think of it like: **A car's dashboard that constantly records temperature, fuel, speed, distance traveled** — instead of you having to manually check each one.

---

## Telemetry in Your Project

In **Automagic Omni**, telemetry collects:

```
┌─ Message Events ────────────────────┐
│  - When message received            │
│  - Which instance processed it      │
│  - Who sent it (user_id)            │
│  - Processing time taken            │
│  - Success or failure status        │
└─────────────────────────────────────┘

┌─ Performance Metrics ───────────────┐
│  - Time to call agent API           │
│  - Time to call Evolution API       │
│  - Leo streaming response time      │
│  - Total end-to-end duration        │
└─────────────────────────────────────┘

┌─ System Health ─────────────────────┐
│  - API response times               │
│  - Error counts                     │
│  - Connection issues                │
│  - Resource usage                   │
└─────────────────────────────────────┘
```

---

## Real Uses in Your Project

### 1. **Message Tracing** (Already implemented)
```
Every message gets a trace_id and trace record:
├─ trace_id: Unique identifier
├─ user_id: Who sent message
├─ instance_id: Which Omni instance
├─ message: What they sent
├─ response: What agent replied
├─ status: success/failed
├─ duration_ms: How long it took
└─ steps: Each stage (webhook→agent→evolution→whatsapp)
```

**Use:** You can query all traces to see:
- How many messages processed
- Which ones failed
- How long they took
- Performance bottlenecks

### 2. **Performance Monitoring**
```
Measure response times:
├─ Webhook reception: 10-50ms
├─ Agent API call: 3000-5000ms (Leo processing)
├─ Evolution API send: 20-100ms
└─ Total: 3-7 seconds

Find bottlenecks: "Leo is taking 80% of time"
```

**Use:** Identify slow operations and optimize

### 3. **Debug Problem Messages**
```
Message failed? Check trace:
├─ Where exactly did it fail?
├─ What error message?
├─ What was the agent's response?
├─ What was the webhook payload?

Answer: "Failed at agent_call step, agent returned 401"
```

**Use:** Quickly diagnose issues

### 4. **Business Metrics**
```
Count:
├─ Total messages per day/week/month
├─ Success rate (completed vs failed)
├─ Average response time
├─ Most active users
├─ Peak usage times
```

**Use:** Understand usage patterns and costs

### 5. **Security Monitoring**
```
Track:
├─ Who accessed what instance
├─ Failed authentication attempts
├─ Rate limit violations
├─ Unusual access patterns
```

**Use:** Detect abuse or security issues

---

## How Telemetry Works in Your Database

### Trace Table
```sql
CREATE TABLE message_trace (
    trace_id UUID PRIMARY KEY,
    instance_id INTEGER,              -- Which Omni instance
    user_id VARCHAR,                   -- Who sent it
    message_content TEXT,              -- Original message
    response_content TEXT,             -- Agent response
    status VARCHAR,                    -- completed/failed/error
    duration_ms INTEGER,               -- Total time taken
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    steps JSON,                        -- Each processing step
    error_message VARCHAR              -- If failed, why
);
```

**Every message flow saves data here automatically**

---

## How to Enable/Configure Telemetry

### In `.env` file:

```env
# Telemetry Configuration
AUTOMAGIK_OMNI_ENABLE_TRACING=true          # Enable message tracing (default: true)
AUTOMAGIK_OMNI_TRACE_RETENTION_DAYS=30      # Keep traces for 30 days
AUTOMAGIK_OMNI_LOG_LEVEL=INFO               # Log level: DEBUG, INFO, WARNING, ERROR
AUTOMAGIK_OMNI_ENABLE_METRICS=true          # Enable Prometheus metrics
AUTOMAGIK_OMNI_ENABLE_DETAILED_LOGGING=true # Log each step with details
```

### Verify Telemetry is On:

```bash
# Check if tracing is enabled
curl http://localhost:8882/health -H "x-api-key: omni-dev-key-test-2025"

# Response should show:
# {
#   "tracing_enabled": true,
#   "trace_retention_days": 30,
#   ...
# }
```

### Query Traces:

```bash
# Get all traces
curl http://localhost:8882/api/v1/traces \
  -H "x-api-key: omni-dev-key-test-2025"

# Get traces for specific instance
curl "http://localhost:8882/api/v1/traces?instance_name=whatsapp-bot" \
  -H "x-api-key: omni-dev-key-test-2025"

# Get failed traces only
curl "http://localhost:8882/api/v1/traces?status=failed" \
  -H "x-api-key: omni-dev-key-test-2025"

# Get slow messages (>5 seconds)
curl "http://localhost:8882/api/v1/traces?min_duration=5000" \
  -H "x-api-key: omni-dev-key-test-2025"
```

---

## Trace Data Structure

Each trace contains:

```json
{
  "trace_id": "abc123def456",
  "instance_id": "whatsapp-bot",
  "user_id": "whatsapp:+1-555-1234567",
  "message_content": "What can you do?",
  "response_content": "I am Leo, your AI assistant...",
  "status": "completed",
  "duration_ms": 4250,
  "created_at": "2025-12-19T10:30:00Z",
  "updated_at": "2025-12-19T10:30:04Z",
  "steps": [
    {
      "step": "webhook_received",
      "status": "success",
      "duration_ms": 10,
      "timestamp": "2025-12-19T10:30:00Z"
    },
    {
      "step": "instance_validated",
      "status": "success",
      "duration_ms": 5,
      "timestamp": "2025-12-19T10:30:00Z"
    },
    {
      "step": "agent_called",
      "status": "success",
      "duration_ms": 4200,
      "timestamp": "2025-12-19T10:30:04Z"
    },
    {
      "step": "evolution_send",
      "status": "success",
      "duration_ms": 35,
      "timestamp": "2025-12-19T10:30:04Z"
    }
  ]
}
```

---

## Common Telemetry Queries

### Find Performance Issues
```bash
# Messages taking more than 10 seconds
curl "http://localhost:8882/api/v1/traces?min_duration=10000" \
  -H "x-api-key: omni-dev-key-test-2025"
```

### Find Failed Messages
```bash
# All failed messages
curl "http://localhost:8882/api/v1/traces?status=failed" \
  -H "x-api-key: omni-dev-key-test-2025"
```

### Check Specific User Activity
```bash
# Messages from specific user
curl "http://localhost:8882/api/v1/traces?user_id=whatsapp:+1-555-1234567" \
  -H "x-api-key: omni-dev-key-test-2025"
```

### Success Rate
```bash
# Get all traces
traces = GET /api/v1/traces

# Count: total messages
total = count(traces)

# Count: successful messages
successful = count(traces where status = "completed")

# Success rate = successful / total * 100
success_rate = (successful / total) * 100
```

---

## Disabling Telemetry (If Needed)

```env
# In .env, set:
AUTOMAGIK_OMNI_ENABLE_TRACING=false

# Restart Omni
# python -m src
```

**Note:** Disabling telemetry means:
- ❌ No trace records saved
- ❌ Can't debug failed messages
- ❌ Can't see performance metrics
- ✅ Slightly less database load

---

## Best Practices

✅ **DO:**
- Keep telemetry ON in production
- Review traces regularly for failures
- Monitor response times
- Set up alerts for slow messages (>10sec)
- Clean up old traces (retention: 30 days)

❌ **DON'T:**
- Turn off telemetry unless necessary
- Ignore repeated failures
- Leave storage unlimited (clean up old data)
- Share raw traces with sensitive user data

---

## Summary

| Aspect | Answer |
|--------|--------|
| **What is it?** | Automatic collection of message & performance data |
| **Where stored?** | `message_trace` table in database |
| **Uses** | Debug issues, measure performance, track usage |
| **Enabled?** | By default (set `AUTOMAGIK_OMNI_ENABLE_TRACING=true`) |
| **How to use?** | Query `/api/v1/traces` endpoint |
| **Data kept?** | 30 days (configurable) |

---

*For detailed tracing examples, see [COMPLETE_TESTING_GUIDE.md](COMPLETE_TESTING_GUIDE.md) section "Message Traces"*

# POSTMAN WORKFLOW - Visual Guide

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Create Instance (POST /api/v1/instances)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Omni:                                                                        │
│  1. Receives instance config                                                │
│  2. Validates all fields present                                            │
│  3. Creates database record                                                 │
│  4. Auto-registers webhook in Evolution API                                 │
│  5. Returns instance ID + config                                            │
│                                                                              │
│ Response: {"id": 1, "name": "whatsapp-leo-bot", ...}                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Get QR Code (GET /api/v1/instances/{name}/qr)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Omni:                                                                        │
│  1. Looks up instance by name                                               │
│  2. Calls Evolution API for QR code                                         │
│  3. Evolution API generates fresh QR (valid 5 min)                          │
│  4. Returns base64-encoded PNG                                              │
│                                                                              │
│ Response: {"qr_code": "data:image/png;base64,...", ...}                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Scan QR Code with WhatsApp Mobile                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ User:                                                                        │
│  1. Copy QR data from response                                              │
│  2. Decode to see QR code image                                             │
│  3. Open WhatsApp on phone                                                  │
│  4. Scan QR code                                                            │
│  5. Instance connects to Evolution API                                      │
│  6. Ready to receive messages                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Trigger Webhook (POST /webhook/evolution/{instance})               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ API Call 1: Webhook Received                                                │
│  Request:  POST /webhook/evolution/whatsapp-leo-bot                        │
│           {"data": {"message": {...}}}                                      │
│  Omni:    Parses message, creates trace (status: pending)                  │
│  Response: {"status": "received"}                                           │
│           ↓                                                                  │
│ API Call 2: Instance Validation                                             │
│  Omni:    Looks up instance config, validates active                       │
│  Trace:   Step "instance_validated" ✓                                       │
│           ↓                                                                  │
│ API Call 3: Access Control Check                                            │
│  Omni:    Checks allow/block lists                                          │
│  Trace:   Step "access_control_checked" ✓                                   │
│           ↓                                                                  │
│ API Call 4: Call Leo Adapter                                                │
│  Request:  POST http://localhost:8887/api/agent/chat                       │
│           Headers: X-API-Key: leo-adapter-key-2025                          │
│           Body: {"user_id": "...", "message": "What can you do?"}          │
│                                                                              │
│           Leo Adapter:                                                      │
│           1. Validates API key                                              │
│           2. Translates to Leo format                                       │
│           3. Calls Leo API with streaming                                   │
│           4. Parses SSE deltas (TEXT_MESSAGE_CONTENT)                       │
│           5. Concatenates text response                                     │
│                                                                              │
│  Response: {"text": "I am Leo, your AI assistant..."}                       │
│  Trace:   Step "agent_called" with duration ✓                              │
│           ↓                                                                  │
│ API Call 5: Send to Evolution API                                           │
│  Request:  POST https://evolution-api.../message/sendText/whatsapp-leo-bot │
│           {"number": "+15551234567", "text": "I am Leo..."}                │
│  Evolution: Queues message for WhatsApp delivery                            │
│  Response: {"key": {...}, "status": "PENDING"}                              │
│  Trace:   Step "evolution_api_called" ✓                                     │
│           ↓                                                                  │
│ Final:    Update trace status: "completed"                                  │
│           Record total duration: 7.85 seconds                               │
│           All steps logged and timestamped                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: View Message Trace (GET /api/v1/traces)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Omni:                                                                        │
│  1. Queries all traces from database                                        │
│  2. Returns complete message lifecycle                                      │
│  3. Shows all 5 processing steps with timestamps                            │
│                                                                              │
│ Response:                                                                    │
│ {                                                                            │
│   "total": 1,                                                                │
│   "traces": [{                                                               │
│     "trace_id": "abc123...",                                                 │
│     "status": "completed",                                                   │
│     "duration_ms": 7850,                                                     │
│     "steps": [                                                               │
│       {"step": "webhook_received", "status": "success"},                     │
│       {"step": "instance_validated", "status": "success"},                   │
│       {"step": "access_control_checked", "status": "success"},               │
│       {"step": "agent_called", "status": "success", "duration_ms": 7200},    │
│       {"step": "evolution_api_called", "status": "success"}                  │
│     ]                                                                        │
│   }]                                                                         │
│ }                                                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed API Call Sequence

### Flow Timing

```
0ms  ├─ Webhook received
     │  └─ Omni parses, validates
     │
100ms ├─ Instance looked up
     │  └─ Config retrieved
     │
150ms ├─ Access control checked
     │  └─ User validation
     │
200ms ├─ Leo Adapter called
     │  │
     │  ├─ Request sent (1ms)
     │  │
     │  ├─ Leo Adapter receives
     │  │  ├─ Validates API key (10ms)
     │  │  ├─ Translates format (5ms)
     │  │  └─ Calls Leo API (streaming)
     │  │
     │  ├─ Leo API processing
     │  │  ├─ Workflow execution (~3000-5000ms)
     │  │  └─ Streams SSE response
     │  │
     │  ├─ Leo Adapter parsing
     │  │  ├─ Reads SSE events (~2000-3000ms)
     │  │  ├─ Extracts deltas (50ms)
     │  │  └─ Concatenates text (10ms)
     │  │
     │  └─ Response returned (1ms)
     │
7200ms ├─ Evolution API called
     │  │
     │  ├─ Request sent (1ms)
     │  │
     │  ├─ Evolution API processes
     │  │  └─ Queues message (~500ms)
     │  │
     │  └─ Confirmation returned (1ms)
     │
7850ms ├─ Trace updated
        └─ Status: "completed"
```

---

## Postman Setup Instructions

### Collection Organization

```
Leo Integration Collection
├── Instance Management
│   ├── [POST] Create Instance
│   ├── [GET] List Instances
│   ├── [GET] Get Instance Details
│   ├── [GET] Get QR Code
│   └── [PUT] Update Instance
│
├── Webhook Testing
│   ├── [POST] Trigger Webhook (Simulate Message)
│   ├── [POST] Trigger Webhook (Complex Message)
│   └── [POST] Trigger Webhook (Error Case)
│
├── Message & Trace Management
│   ├── [GET] Get All Traces
│   ├── [GET] Get Trace by ID
│   └── [GET] Get Instance Traces
│
├── Access Control
│   ├── [POST] Block User
│   ├── [POST] Allow User
│   └── [GET] List Access Rules
│
└── Utility
    ├── [GET] Omni Health Check
    ├── [GET] Adapter Health Check
    └── [GET] List Instances (Monitoring)
```

### Environment Variables in Postman

Set these in Postman Environment:

```json
{
  "omni_host": "localhost",
  "omni_port": "8882",
  "omni_url": "http://{{omni_host}}:{{omni_port}}",
  "omni_api_key": "omni-dev-key-test-2025",
  
  "adapter_host": "localhost",
  "adapter_port": "8887",
  "adapter_url": "http://{{adapter_host}}:{{adapter_port}}",
  "adapter_api_key": "leo-adapter-key-2025",
  
  "evolution_url": "https://evolution-api-production-7611.up.railway.app",
  "evolution_key": "FA758317-709D-4BB6-BA4F-987B2335036A",
  
  "instance_name": "whatsapp-leo-bot",
  "test_phone": "+15551234567",
  "test_message": "What can you do?"
}
```

Then use variables in requests:
```
GET {{omni_url}}/api/v1/instances
Headers: x-api-key: {{omni_api_key}}
```

---

## Expected Response Timeline

```
Step          Status Code    Response Time    Notes
────────────────────────────────────────────────────────
1. Create     201           100-200ms         Instance created
2. Get QR     200           50-100ms          QR code generated
3. Webhook    200           7800-8200ms       Full processing + Leo API
4. Get Trace  200           10-50ms           Database lookup
```

---

## Common Test Scenarios

### Scenario 1: Happy Path (Success)
```
Create Instance ✓
Get QR Code ✓
Trigger Webhook (Success) ✓
View Trace (status: completed) ✓
```

### Scenario 2: Validation Error
```
Create Instance (missing field) → 422 Validation Error
Check error message
Fix and retry → 201 Created ✓
```

### Scenario 3: User Blocked
```
Block user: +15551234567
Trigger webhook with that number
Check trace → status: "blocked"
```

### Scenario 4: Agent Timeout
```
Update instance: agent_timeout = 5 (very short)
Trigger webhook
Wait...
Check trace → status: "timeout"
```

### Scenario 5: Invalid API Key
```
Create Instance with wrong x-api-key
→ 401 Unauthorized
Check error: "Invalid API key"
```

---

## Debugging in Postman

### Check Response Details

```
1. Click on response area
2. View tabs:
   - Body: Full response JSON
   - Headers: Response headers, status code
   - Tests: Run assertions
   - Console: Request/response details

3. In Console (Ctrl+Alt+C):
   - See full request sent
   - See full response received
   - Check timing details
```

### Save Responses

```
1. Click three dots next to Send button
2. "Save response as"
3. Choose location
4. Replay later for debugging
```

### Use Tests Tab

```javascript
// Example: Verify response is 200
pm.test("Status is 200", function() {
    pm.response.to.have.status(200);
});

// Example: Check trace status is completed
pm.test("Trace completed", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.traces[0].status).to.eql("completed");
});

// Example: Check response time < 10 seconds
pm.test("Response time < 10s", function() {
    pm.expect(pm.response.responseTime).to.be.below(10000);
});
```

---

*Last Updated: December 15, 2025*

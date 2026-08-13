# A2A Streaming and Push Notifications

A2A provides two complementary mechanisms for real-time and asynchronous task updates.

## Server-Sent Events (SSE) Streaming

### Requirements

- Server must declare `capabilities.streaming: true` in Agent Card
- Client uses `SendStreamingMessage` or `SubscribeToTask` operations
- HTTP response: `Content-Type: text/event-stream`

### Initiating a Stream

**SendStreamingMessage** — send a message and subscribe to updates simultaneously:

```http
POST /message:stream HTTP/1.1
Host: agent.example.com
Content-Type: application/a2a+json
Authorization: Bearer token

{
  "message": {
    "role": "ROLE_USER",
    "parts": [{"text": "Write a detailed report"}],
    "messageId": "msg-uuid"
  }
}
```

**SubscribeToTask** — subscribe to an existing task:

```http
GET /tasks/task-uuid:subscribe HTTP/1.1
Host: agent.example.com
Accept: text/event-stream
Authorization: Bearer token
```

### Event Stream Format

```
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"task":{"id":"task-uuid","contextId":"ctx-uuid","status":{"state":"TASK_STATE_SUBMITTED"}}}

data: {"statusUpdate":{"taskId":"task-uuid","contextId":"ctx-uuid","status":{"state":"TASK_STATE_WORKING","message":{"role":"ROLE_AGENT","parts":[{"text":"Processing..."}],"messageId":"msg-status"}}}}

data: {"artifactUpdate":{"taskId":"task-uuid","contextId":"ctx-uuid","artifact":{"artifactId":"art-1","name":"report.md","parts":[{"text":"# Report\n\nIntroduction..."}]},"append":false,"lastChunk":false}}

data: {"artifactUpdate":{"taskId":"task-uuid","contextId":"ctx-uuid","artifact":{"artifactId":"art-1","name":"report.md","parts":[{"text":"\n\nChapter 2..."}]},"append":true,"lastChunk":false}}

data: {"artifactUpdate":{"taskId":"task-uuid","contextId":"ctx-uuid","artifact":{"artifactId":"art-1","name":"report.md","parts":[{"text":"\n\nConclusion."}]},"append":true,"lastChunk":true}}

data: {"statusUpdate":{"taskId":"task-uuid","contextId":"ctx-uuid","status":{"state":"TASK_STATE_COMPLETED"}}}}
```

### Stream Lifecycle

1. **Initial event:** `Task` object with current state (SUBMITTED or WORKING)
2. **Progress events:** Zero or more `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent`
3. **Termination:** Stream closes when task reaches terminal state (`COMPLETED`, `FAILED`, `CANCELED`, `REJECTED`) or interrupted state (`INPUT_REQUIRED`, `AUTH_REQUIRED`)

### Artifact Streaming

For large artifacts, use incremental streaming:

- `append: true` — content should be appended to previously sent artifact with same `artifactId`
- `lastChunk: true` — this is the final chunk of the artifact
- Client reassembles by concatenating parts from chunks with same `artifactId`

### Multiple Streams

- Agent MAY serve multiple concurrent streams for the same task
- Events are broadcast to all active streams
- Closing one stream does not affect others
- Useful for: multiple viewers, reconnection after network interruption

### Resubscription

If a client's SSE connection breaks while a task is still active:
1. Use `SubscribeToTask` with the same `taskId`
2. Server returns current task state as first event
3. Client continues receiving updates from that point

### When to Use Streaming

- Real-time progress monitoring
- Receiving large results incrementally
- Interactive conversational exchanges
- Applications requiring low-latency updates

## Push Notifications

### Requirements

- Server must declare `capabilities.pushNotifications: true` in Agent Card
- Client provides a webhook URL (HTTPS)
- Server sends HTTP POST to the webhook when task state changes
- Webhook always uses plain HTTP with JSON payloads regardless of agent's primary binding

### Configuring Push Notifications

**Option 1: Include in SendMessage request:**

```json
{
  "message": {
    "role": "ROLE_USER",
    "parts": [{"text": "Generate Q1 sales report"}],
    "messageId": "msg-1"
  },
  "configuration": {
    "taskPushNotificationConfig": {
      "url": "https://client.example.com/webhook/a2a",
      "token": "client-validation-token",
      "authentication": {
        "scheme": "Bearer",
        "credentials": "webhook-auth-token"
      }
    }
  }
}
```

**Option 2: Create separately for existing task:**

```http
POST /tasks/task-uuid/pushNotificationConfigs HTTP/1.1
Content-Type: application/a2a+json

{
  "task_id": "task-uuid",
  "url": "https://client.example.com/webhook/a2a",
  "token": "client-validation-token",
  "authentication": {
    "scheme": "Bearer",
    "credentials": "webhook-auth-token"
  }
}
```

### Push Notification Payload

The webhook receives a `StreamResponse` object — same format as streaming:

```http
POST /webhook/a2a HTTP/1.1
Host: client.example.com
Authorization: Bearer webhook-auth-token
Content-Type: application/a2a+json

{
  "statusUpdate": {
    "taskId": "task-uuid",
    "contextId": "ctx-uuid",
    "status": {
      "state": "TASK_STATE_COMPLETED",
      "timestamp": "2025-01-15T10:30:00.000Z"
    }
  }
}
```

Possible payload types:
- `task` — full task object
- `message` — message response
- `statusUpdate` — `TaskStatusUpdateEvent`
- `artifactUpdate` — `TaskArtifactUpdateEvent`

### Client Webhook Responsibilities

1. **Respond with HTTP 2xx** to acknowledge receipt
2. **Process idempotently** — duplicates may occur
3. **Validate task ID** matches an expected task
4. **Verify the source** — authenticate the A2A server
5. **Call GetTask** to retrieve full updated task state

### Server Delivery Guarantees

- Server MUST attempt delivery at least once
- Server MAY retry with exponential backoff for failures
- Recommended timeout: 10-30 seconds per webhook request
- Server MAY stop after configured number of consecutive failures

### Push Notification CRUD Operations

| Operation | Endpoint | Description |
|---|---|---|
| Create | `POST /tasks/{id}/pushNotificationConfigs` | Create webhook config |
| Get | `GET /tasks/{id}/pushNotificationConfigs/{configId}` | Retrieve config |
| List | `GET /tasks/{id}/pushNotificationConfigs` | List all configs |
| Delete | `DELETE /tasks/{id}/pushNotificationConfigs/{configId}` | Remove config (idempotent) |

## Security for Push Notifications

### Server-Side (sending to webhook)

- **Validate webhook URLs** — don't blindly POST to any URL (SSRF risk)
- **Allowlist trusted domains** or use ownership verification
- **Authenticate to the webhook** using the scheme in `PushNotificationConfig.authentication`

### Client-Side (receiving notifications)

- **Verify the A2A server** — check signatures/tokens
- **Prevent replay attacks** — use timestamps, nonces, or JWT `jti`
- **Validate `PushNotificationConfig.token`** if provided
- **Implement key rotation** for cryptographic credentials

### Example JWT + JWKS Flow

1. Client specifies `authentication.scheme: "Bearer"` in push notification config
2. A2A server generates JWT signed with its private key (includes `iss`, `aud`, `iat`, `exp`, `jti`, `taskId`)
3. Client webhook:
   - Extracts JWT from `Authorization` header
   - Fetches public key from server's JWKS endpoint (using `kid`)
   - Verifies signature and claims
   - Checks `PushNotificationConfig.token` if provided

## When to Use Push Notifications

- Very long-running tasks (minutes, hours, days)
- Clients that cannot maintain persistent connections (mobile, serverless)
- Event-driven architectures
- When only significant state changes matter (not continuous updates)

## Comparison

| Feature | Streaming (SSE) | Push Notifications |
|---|---|---|
| Latency | Low (real-time) | Variable |
| Connection | Persistent | None (server-initiated) |
| Client reachability | Must be online | Must have public webhook |
| Reconnection | SubscribeToTask | GetTask after notification |
| Best for | Interactive apps, dashboards | Long tasks, mobile, serverless |
| Capability | `streaming: true` | `pushNotifications: true` |

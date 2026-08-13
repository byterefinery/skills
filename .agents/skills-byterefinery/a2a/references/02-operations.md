# A2A Core Operations

A2A defines binding-independent operations that all implementations must support.

## 3.1 Core Operations

### SendMessage

Primary operation for initiating agent interactions.

**Endpoint:** `POST /message:send` (HTTP/REST) | `SendMessage` (JSON-RPC/gRPC)

**Request:** `SendMessageRequest`
```json
{
  "message": {
    "role": "ROLE_USER",
    "parts": [{"text": "What is the weather today?"}],
    "messageId": "msg-uuid"
  },
  "configuration": {
    "acceptedOutputModes": ["text/plain"],
    "historyLength": 10,
    "returnImmediately": false
  },
  "metadata": {},
  "tenant": "optional-routing-key"
}
```

**Response:** `Task` (for stateful work) or `Message` (for simple interactions)

**Behavior:**
- Agent MAY create a `Task` for async processing or return a direct `Message`
- With `returnImmediately: false` (default), blocks until terminal/interrupted state
- With `returnImmediately: true`, returns immediately with in-progress task

**Errors:**
- `ContentTypeNotSupportedError` — unsupported media type in parts
- `UnsupportedOperationError` — message sent to terminal-state task
- `TaskNotFoundError` — referenced task ID doesn't exist

### SendStreamingMessage

Real-time streaming version of SendMessage using SSE.

**Endpoint:** `POST /message:stream` (HTTP/REST) | `SendStreamingMessage` (JSON-RPC/gRPC)

**Response:** Stream of `StreamResponse` objects:
1. Initial `Task` or `Message`
2. Zero or more `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent`
3. Stream closes at terminal/interrupted state

**Requirements:**
- Server must declare `capabilities.streaming: true`
- Returns `UnsupportedOperationError` if streaming not supported

**Stream patterns:**
- **Message-only stream:** Single `Message`, then close immediately
- **Task lifecycle stream:** `Task` → status/artifact events → close at terminal state

### GetTask

Retrieves current state of a previously initiated task.

**Endpoint:** `GET /tasks/{id}` (HTTP/REST) | `GetTask` (JSON-RPC/gRPC)

**Request:** `GetTaskRequest`
```json
{
  "id": "task-uuid",
  "historyLength": 5,
  "includeArtifacts": true,
  "tenant": "optional-routing-key"
}
```

**Response:** `Task` with current status, artifacts, and history

**Errors:**
- `TaskNotFoundError` — task doesn't exist or isn't accessible

### ListTasks

Discovers tasks with filtering and cursor-based pagination.

**Endpoint:** `GET /tasks` (HTTP/REST) | `ListTasks` (JSON-RPC/gRPC)

**Request:** `ListTasksRequest`
```json
{
  "contextId": "optional-context-filter",
  "status": "TASK_STATE_WORKING",
  "historyLength": 3,
  "includeArtifacts": false,
  "pageSize": 10,
  "pageToken": "base64-cursor",
  "tenant": "optional-routing-key"
}
```

**Response:** `ListTasksResponse`
```json
{
  "tasks": [...],
  "totalSize": 15,
  "pageSize": 10,
  "nextPageToken": "base64-next-cursor"
}
```

**Behavior:**
- Cursor-based pagination (not offset-based) — avoids deep pagination problems
- Tasks sorted by last update time descending
- `nextPageToken` is empty string when no more results
- When `includeArtifacts` is false, artifacts field must be omitted entirely

### CancelTask

Requests cancellation of an ongoing task.

**Endpoint:** `POST /tasks/{id}:cancel` (HTTP/REST) | `CancelTask` (JSON-RPC/gRPC)

**Request:** `CancelTaskRequest`
```json
{
  "id": "task-uuid",
  "tenant": "optional-routing-key"
}
```

**Response:** Updated `Task` with cancellation status

**Errors:**
- `TaskNotCancelableError` — task already in terminal state
- `TaskNotFoundError` — task doesn't exist

### SubscribeToTask

Establishes streaming connection for an existing task.

**Endpoint:** `GET /tasks/{id}:subscribe` (HTTP/REST) | `SubscribeToTask` (JSON-RPC/gRPC)

**Request:** `SubscribeToTaskRequest`
```json
{
  "id": "task-uuid",
  "historyLength": 5,
  "tenant": "optional-routing-key"
}
```

**Response:** Stream of `StreamResponse`:
1. Initial `Task` with current state
2. `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent` as they occur
3. Stream closes at terminal state

**Requirements:**
- Server must declare `capabilities.streaming: true`
- Task must not be in terminal state
- Multiple concurrent streams per task are allowed

### GetExtendedAgentCard

Retrieves authenticated version of the Agent Card with potentially more details.

**Endpoint:** `GET /extendedAgentCard` (HTTP/REST) | `GetExtendedAgentCard` (JSON-RPC/gRPC)

**Request:** `GetExtendedAgentCardRequest`
```json
{
  "tenant": "optional-routing-key"
}
```

**Response:** `AgentCard` — may contain additional skills/capabilities not in public card

**Requirements:**
- Must authenticate using schemes from public Agent Card
- Server must declare `capabilities.extendedAgentCard: true`
- Clients should replace cached public card with extended card for session duration

## 3.2 Push Notification Operations

### CreateTaskPushNotificationConfig

Creates webhook config for async task updates.

**Endpoint:** `POST /tasks/{task_id}/pushNotificationConfigs` (HTTP/REST)

**Request:** `TaskPushNotificationConfig`
```json
{
  "task_id": "task-uuid",
  "url": "https://client.example.com/webhook",
  "token": "client-validation-token",
  "authentication": {
    "scheme": "Bearer",
    "credentials": "server-to-webhook-token"
  }
}
```

**Response:** Created config with assigned `id`

### GetTaskPushNotificationConfig

**Endpoint:** `GET /tasks/{task_id}/pushNotificationConfigs/{id}` (HTTP/REST)

**Response:** `TaskPushNotificationConfig`

### ListTaskPushNotificationConfigs

**Endpoint:** `GET /tasks/{task_id}/pushNotificationConfigs` (HTTP/REST)

**Response:** `ListTaskPushNotificationConfigsResponse` with paginated configs

### DeleteTaskPushNotificationConfig

**Endpoint:** `DELETE /tasks/{task_id}/pushNotificationConfigs/{id}` (HTTP/REST)

**Behavior:** Idempotent — multiple deletions have the same effect

## 3.3 Operation Semantics

### Idempotency

| Operation | Idempotent | Notes |
|---|---|---|
| GetTask | Yes | Naturally idempotent |
| ListTasks | Yes | Naturally idempotent |
| GetExtendedAgentCard | Yes | Naturally idempotent |
| SendMessage | Maybe | Agents may use `messageId` to detect duplicates |
| CancelTask | Yes | Multiple cancellations have same effect |

### History Length Semantics

The `historyLength` parameter controls messages returned:
- **Unset/undefined:** Server default (implementation-defined, may be all)
- **0:** No history returned; `history` field omitted
- **> 0:** At most this many recent messages

### Service Parameters

Key-value pairs transmitted via binding-specific mechanisms (HTTP headers, gRPC metadata):

| Name | Description | Example |
|---|---|---|
| `A2A-Extensions` | Comma-separated extension URIs | `https://example.com/ext/v1` |
| `A2A-Version` | Protocol version | `1.0` |

### Capability Validation

Before using optional features, check the Agent Card:

| Feature | Capability Field | Error if missing |
|---|---|---|
| Streaming | `capabilities.streaming` | `UnsupportedOperationError` |
| Push Notifications | `capabilities.pushNotifications` | `PushNotificationNotSupportedError` |
| Extended Agent Card | `capabilities.extendedAgentCard` | `UnsupportedOperationError` |
| Extensions (required) | `extensions[].required` | `ExtensionSupportRequiredError` |

## 3.4 Multi-Turn Interactions

### Context Identifier Semantics

- Agent generates `contextId` on first interaction (when not provided)
- Client echoes `contextId` in subsequent messages for continuity
- Agent MAY accept client-provided `contextId` or reject with error
- Server-generated `contextId` values are opaque to clients

### Task Identifier Semantics

- `taskId` is server-generated when creating a new task
- Client includes `taskId` in follow-up messages to continue a specific task
- Agent returns `TaskNotFoundError` if `taskId` doesn't exist
- Client cannot specify `taskId` for new tasks

### Multi-Turn Patterns

1. **Context Continuity:** Include `contextId` in subsequent messages
2. **Task Continuation:** Include both `contextId` and `taskId`
3. **New Task in Context:** Include `contextId` without `taskId`
4. **Input Required:** Agent sets task to `TASK_STATE_INPUT_REQUIRED`; client responds with same `taskId`
5. **Follow-up References:** Use `referenceTaskIds` in `Message` to reference related tasks

### Task Immutability

Terminal-state tasks (`COMPLETED`, `FAILED`, `CANCELED`, `REJECTED`) cannot be restarted. Refinements create new tasks within the same `contextId`.

## 3.5 Task Update Delivery

| Mechanism | Latency | Connection | Best For |
|---|---|---|---|
| Polling (GetTask) | Higher | None | Simple integrations, firewalled clients |
| Streaming (SSE) | Low | Persistent | Interactive apps, real-time dashboards |
| Push Notifications | Variable | None | Long-running tasks, mobile, serverless |

## 3.6 Versioning

- Protocol version uses `Major.Minor` (e.g., `1.0`)
- Clients MUST send `A2A-Version` header (e.g., `A2A-Version: 1.0`)
- Empty values interpreted as version 0.3
- Agents return `VersionNotSupportedError` for unsupported versions

## Error Codes

| Error | JSON-RPC | gRPC | HTTP |
|---|---|---|---|
| `TaskNotFoundError` | `-32001` | `NOT_FOUND` | `404` |
| `TaskNotCancelableError` | `-32002` | `FAILED_PRECONDITION` | `400` |
| `PushNotificationNotSupportedError` | `-32003` | `FAILED_PRECONDITION` | `400` |
| `UnsupportedOperationError` | `-32004` | `FAILED_PRECONDITION` | `400` |
| `ContentTypeNotSupportedError` | `-32005` | `INVALID_ARGUMENT` | `400` |
| `InvalidAgentResponseError` | `-32006` | `INTERNAL` | `500` |
| `ExtendedAgentCardNotConfiguredError` | `-32007` | `FAILED_PRECONDITION` | `400` |
| `ExtensionSupportRequiredError` | `-32008` | `FAILED_PRECONDITION` | `400` |
| `VersionNotSupportedError` | `-32009` | `FAILED_PRECONDITION` | `400` |

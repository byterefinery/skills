# A2A Protocol Bindings

A2A supports multiple protocol bindings that provide functionally equivalent access to the same operations.

## Method Mapping Reference

| Functionality | JSON-RPC Method | gRPC Method | REST Endpoint |
|---|---|---|---|
| Send message | `SendMessage` | `SendMessage` | `POST /message:send` |
| Send streaming message | `SendStreamingMessage` | `SendStreamingMessage` | `POST /message:stream` |
| Get task | `GetTask` | `GetTask` | `GET /tasks/{id}` |
| List tasks | `ListTasks` | `ListTasks` | `GET /tasks` |
| Cancel task | `CancelTask` | `CancelTask` | `POST /tasks/{id}:cancel` |
| Subscribe to task | `SubscribeToTask` | `SubscribeToTask` | `POST /tasks/{id}:subscribe` |
| Create push notification config | `CreateTaskPushNotificationConfig` | `CreateTaskPushNotificationConfig` | `POST /tasks/{id}/pushNotificationConfigs` |
| Get push notification config | `GetTaskPushNotificationConfig` | `GetTaskPushNotificationConfig` | `GET /tasks/{id}/pushNotificationConfigs/{configId}` |
| List push notification configs | `ListTaskPushNotificationConfigs` | `ListTaskPushNotificationConfigs` | `GET /tasks/{id}/pushNotificationConfigs` |
| Delete push notification config | `DeleteTaskPushNotificationConfig` | `DeleteTaskPushNotificationConfig` | `DELETE /tasks/{id}/pushNotificationConfigs/{configId}` |
| Get extended Agent Card | `GetExtendedAgentCard` | `GetExtendedAgentCard` | `GET /extendedAgentCard` |

## JSON-RPC Binding

JSON-RPC 2.0 over HTTP(S) is the primary binding. Content-Type is `application/a2a+json`.

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "SendMessage",
  "id": "unique-request-id",
  "params": {
    "message": {
      "role": "ROLE_USER",
      "parts": [{"text": "Hello"}],
      "messageId": "msg-1"
    }
  }
}
```

### Response Format (success)

```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "result": {
    "task": {
      "id": "task-uuid",
      "contextId": "context-uuid",
      "status": {"state": "TASK_STATE_COMPLETED"},
      "artifacts": [...]
    }
  }
}
```

### Response Format (error)

```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "error": {
    "code": -32001,
    "message": "Task not found",
    "data": {
      "taskId": "nonexistent-id"
    }
  }
}
```

### Streaming (SSE)

For `SendStreamingMessage` and `SubscribeToTask`:

```
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"jsonrpc":"2.0","id":"req-1","result":{"task":{"id":"task-uuid","status":{"state":"TASK_STATE_WORKING"}}}}

data: {"jsonrpc":"2.0","id":"req-1","result":{"statusUpdate":{"taskId":"task-uuid","status":{"state":"TASK_STATE_COMPLETED"}}}}
```

## gRPC Binding

gRPC provides native streaming support and strong typing via Protocol Buffers.

### Service Definition

```protobuf
service A2AService {
  rpc SendMessage(SendMessageRequest) returns (SendMessageResponse);
  rpc SendStreamingMessage(SendMessageRequest) returns (stream StreamResponse);
  rpc GetTask(GetTaskRequest) returns (Task);
  rpc ListTasks(ListTasksRequest) returns (ListTasksResponse);
  rpc CancelTask(CancelTaskRequest) returns (Task);
  rpc SubscribeToTask(SubscribeToTaskRequest) returns (stream StreamResponse);
  rpc CreateTaskPushNotificationConfig(TaskPushNotificationConfig) returns (TaskPushNotificationConfig);
  rpc GetTaskPushNotificationConfig(GetTaskPushNotificationConfigRequest) returns (TaskPushNotificationConfig);
  rpc ListTaskPushNotificationConfigs(ListTaskPushNotificationConfigsRequest) returns (ListTaskPushNotificationConfigsResponse);
  rpc DeleteTaskPushNotificationConfig(DeleteTaskPushNotificationConfigRequest) returns (google.protobuf.Empty);
  rpc GetExtendedAgentCard(GetExtendedAgentCardRequest) returns (AgentCard);
}
```

### gRPC Metadata

Service parameters transmitted via gRPC metadata:

```
A2A-Extensions: https://example.com/ext/v1
A2A-Version: 1.0
```

## HTTP+JSON/REST Binding

RESTful HTTP endpoints with JSON payloads. Content-Type is `application/a2a+json`.

### Request Examples

**Send Message:**
```http
POST /message:send HTTP/1.1
Host: agent.example.com
Content-Type: application/a2a+json
Authorization: Bearer token
A2A-Version: 1.0

{
  "message": {
    "role": "ROLE_USER",
    "parts": [{"text": "Analyze this data"}],
    "messageId": "msg-1"
  }
}
```

**Get Task:**
```http
GET /tasks/task-uuid?historyLength=5&includeArtifacts=true HTTP/1.1
Host: agent.example.com
Authorization: Bearer token
A2A-Version: 1.0
```

**List Tasks:**
```http
GET /tasks?contextId=ctx-123&status=TASK_STATE_WORKING&pageSize=10 HTTP/1.1
Host: agent.example.com
Authorization: Bearer token
```

**Cancel Task:**
```http
POST /tasks/task-uuid:cancel HTTP/1.1
Host: agent.example.com
Content-Type: application/a2a+json
Authorization: Bearer token
```

**Subscribe to Task:**
```http
GET /tasks/task-uuid:subscribe HTTP/1.1
Host: agent.example.com
Accept: text/event-stream
Authorization: Bearer token
```

### Response Format

```http
HTTP/1.1 200 OK
Content-Type: application/a2a+json

{
  "task": {
    "id": "task-uuid",
    "contextId": "context-uuid",
    "status": {"state": "TASK_STATE_COMPLETED"},
    "artifacts": [...]
  }
}
```

### Error Response Format

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://a2a-protocol.org/errors/task-not-found",
  "title": "Task Not Found",
  "status": 404,
  "detail": "The specified task ID does not correspond to an existing or accessible task",
  "instance": "/tasks/nonexistent-id"
}
```

## Custom Protocol Bindings

Custom bindings are identified by URI in the Agent Card:

```json
{
  "supportedInterfaces": [
    {
      "url": "wss://agent.example.com/a2a/websocket",
      "protocolBinding": "https://example.com/bindings/websocket/v1",
      "protocolVersion": "1.0"
    }
  ]
}
```

Custom binding requirements:
- Must provide functionally equivalent access to all operations
- Must define equivalent error code mappings
- Must specify how service parameters are transmitted
- Breaking changes require a new URI

## Multi-Tenancy Routing

Three complementary approaches:

### 1. URL-Based (Sub-Path)

Each agent has distinct URL prefix in its Agent Card:
```json
{
  "supportedInterfaces": [{
    "url": "https://agents.example.com/billing",
    "protocolBinding": "HTTP+JSON",
    "protocolVersion": "1.0"
  }]
}
```

### 2. Authentication Header-Based

Gateway routes based on auth credentials (bearer token claims, API key).

### 3. Body-Based (tenant field)

Agent Card declares a `tenant` value:
```json
{
  "supportedInterfaces": [{
    "url": "https://agents.example.com/a2a",
    "protocolBinding": "HTTP+JSON",
    "protocolVersion": "1.0",
    "tenant": "billing"
  }]
}
```

Client MUST echo the `tenant` value in every request. If not declared, omit the field.

## JSON Naming Conventions

- **Field names:** camelCase (not snake_case from protobuf)
  - `protocol_version` → `protocolVersion`
  - `context_id` → `contextId`
- **Enum values:** SCREAMING_SNAKE_CASE as defined in proto
  - `TASK_STATE_COMPLETED`
  - `ROLE_USER`
- **Timestamps:** ISO 8601 UTC (`YYYY-MM-DDTHH:mm:ss.sssZ`)

## Protocol Selection

- Agent declares all supported protocols in Agent Card
- Client may choose any declared protocol
- Client SHOULD implement fallback logic for alternative protocols
- All protocols must provide identical functionality and consistent behavior

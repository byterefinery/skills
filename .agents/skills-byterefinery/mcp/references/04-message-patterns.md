# Message Patterns

MCP supports several message patterns that define how clients and servers interact.

## Request and Response

The basic pattern: a client sends a request, the server responds with a result or error.

```
Client -> Server: Request (with _meta: version, capabilities)
Server -> Client: ResultResponse or ErrorResponse
```

- Every request carries protocol version and client capabilities in `_meta`
- Every result carries `resultType` (`"complete"` or `"input_required"`)
- Servers SHOULD include `io.modelcontextprotocol/serverInfo` in result `_meta`

## Multi Round-Trip Requests (MRTR)

Servers may require additional client input (elicitation, sampling, roots) to complete a request. Instead of initiating separate requests, the server returns an `InputRequiredResult` and the client retries with the needed input.

### Flow

1. Client sends a request (e.g., `tools/call`)
2. Server responds with `resultType: "input_required"` containing `inputRequests`
3. Client fulfills the input requests (e.g., via user elicitation)
4. Client retries the original request with `inputResponses` and `requestState`
5. Server processes the complete request

### Example

```json
// Initial request
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "deploy_app",
    "arguments": { "environment": "production" }
  }
}

// Server needs confirmation
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "resultType": "input_required",
    "inputRequests": {
      "confirm_deploy": {
        "method": "elicitation/create",
        "params": {
          "mode": "form",
          "message": "Confirm deployment to production?",
          "requestedSchema": {
            "type": "object",
            "properties": { "confirmed": { "type": "boolean" } },
            "required": ["confirmed"]
          }
        }
      }
    },
    "requestState": "eyJlbnYiOiJwcm9kIn0..."
  }
}

// Client retries with input
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "deploy_app",
    "arguments": { "environment": "production" },
    "inputResponses": {
      "confirm_deploy": {
        "action": "accept",
        "content": { "confirmed": true }
      }
    },
    "requestState": "eyJlbnYiOiJwcm9kIn0..."
  }
}
```

Note: the JSON-RPC `id` MUST be different between the initial request and the retry.

## Subscribe and Notify

Clients subscribe to change notifications via `subscriptions/listen`. This opens a long-lived stream for server-to-client notifications.

### Subscription Flow

1. Client sends `subscriptions/listen` with desired notification types:
   - `toolsListChanged` — tool list updates
   - `promptsListChanged` — prompt list updates
   - `resourcesListChanged` — resource list updates
   - `resourceSubscriptions` — individual resource change notifications

2. Server acknowledges with `notifications/subscriptions/acknowledged`

3. Server sends notifications on the stream, each tagged with `io.modelcontextprotocol/subscriptionId`

4. Client cancels by ending the `subscriptions/listen` request

### Notification Example

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": {
    "_meta": { "io.modelcontextprotocol/subscriptionId": 4 },
    "uri": "file:///project/src/main.rs"
  }
}
```

Request-scoped notifications (`notifications/progress`, `notifications/message`) flow on the response stream of the related request, not the `subscriptions/listen` stream.

## Cancellation

Clients can abandon in-flight requests:

- **stdio**: send `notifications/cancelled` notification
- **Streamable HTTP**: close the request's response stream

The server may continue processing but should abandon the request when practical. Cancellation is advisory, not mandatory.

## Progress

Long-running operations can emit progress notifications:

1. Client includes `progressToken` in `_meta` of the request
2. Server sends `notifications/progress` with the matching token
3. Progress notifications flow on the request's response stream (not `subscriptions/listen`)

```json
// Request with progress opt-in
{
  "params": {
    "_meta": { "progressToken": "abc123" }
  }
}

// Progress notification
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "progressToken": "abc123",
    "progress": 50,
    "total": 100
  }
}
```

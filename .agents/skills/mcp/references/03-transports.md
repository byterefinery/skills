# Transports

A transport is a **binding**: it defines how messages are framed and delivered, how request metadata is carried, and how cancellation and termination are signaled. Protocol semantics are identical on every transport.

## Standard Transports

1. **stdio** — newline-delimited messages over standard streams of a client-launched subprocess
2. **Streamable HTTP** — each message is an HTTP POST; replies arrive as JSON or request-scoped SSE stream

Custom transports MAY be implemented but MUST preserve JSON-RPC message format, message patterns, and per-request metadata model.

## stdio

The stdio transport uses newline-delimited JSON-RPC messages over the standard streams of a client-launched subprocess.

### Connection

- The client launches the server as a subprocess
- Messages flow via stdin (client → server) and stdout (server → client)
- stderr is reserved for server logging/diagnostics
- The client controls the server's lifecycle (start, stop)

### Message Framing

- Each JSON-RPC message is on a single line
- Messages are separated by newline characters (`\n`)
- Messages MUST be valid UTF-8

### Cancellation

- The client sends a `notifications/cancelled` notification
- The server may continue processing but should abandon the request when practical

### Discovery

- Clients MAY call `server/discover` on the first request for capability discovery
- On STDIO, `server/discover` can serve as a backward-compatibility probe

## Streamable HTTP

Each message is an HTTP POST to a single MCP endpoint. Replies arrive as a JSON object or a request-scoped SSE stream.

### Request Format

```
POST /mcp
Content-Type: application/json
Mcp-Protocol-Version: 2026-07-28
Mcp-Client-Name: MyClient
Mcp-Client-Version: 1.0.0
Mcp-Method: tools/call
Mcp-Name: my-client

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": { "location": "New York" },
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": { "tools": {} }
    }
  }
}
```

### Required Headers

- `Mcp-Protocol-Version` — protocol version
- `Mcp-Client-Name` / `Mcp-Client-Version` — client identity
- `Mcp-Method` — JSON-RPC method
- `Mcp-Name` — client identifier

### Response

- **Immediate response**: JSON body with `200 OK`
- **SSE stream**: `text/event-stream` content type for long-running operations
- Response streams are **not resumable** — a broken stream loses the in-flight request

### Cancellation

- Client closes the request's response stream
- The server should abandon the request when practical

### Custom Headers from Tool Parameters

The `x-mcp-header` extension property in tool `inputSchema` designates parameters to be mirrored into `Mcp-Param-{name}` HTTP headers. This enables network intermediaries to route requests based on parameter values.

Constraints:
- MUST NOT be empty
- MUST match HTTP field-name token syntax (RFC 9110)
- MUST be case-insensitively unique among all `x-mcp-header` values
- MUST only apply to primitive types (integer, string, boolean — not `number`)
- Integer values MUST be within safe IEEE 754 double range

### Backward Compatibility

Earlier protocol revisions used an `initialize` handshake and `Mcp-Session-Id` header. Implementations interoperate with those revisions by detecting the counterpart's era and falling back. The body remains the source of truth; mismatches between headers and body are rejected with `HeaderMismatchError` (`-32020`).

## Custom Transports

Clients and servers MAY implement custom transports. Custom transports running over a reliable bidirectional byte stream (Unix domain sockets, TCP) SHOULD reuse the stdio framing (newline-delimited JSON-RPC).

Custom transports SHOULD document their connection establishment, message framing, and cancellation patterns.

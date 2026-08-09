# Base Protocol

The Model Context Protocol consists of several key components:

- **Base Protocol**: Core JSON-RPC message types
- **Versioning and Compatibility**: Protocol version negotiation and interoperability
- **Message Patterns**: Request/Response, MRTR, Subscribe and Notify
- **Authorization**: Authentication and authorization framework for HTTP-based transports
- **Server Features**: Resources, prompts, and tools
- **Client Features**: Elicitation
- **Utilities**: Cross-cutting concerns like logging and argument completion

All implementations MUST support the base protocol, versioning, and message patterns.

## Messages

All messages between MCP clients and servers MUST follow the [JSON-RPC 2.0](https://www.jsonrpc.org/specification) specification.

### Requests

Sent from client to server to initiate an operation:

```json
{
  "jsonrpc": "2.0",
  "id": "string-or-number",
  "method": "tools/list",
  "params": { /* optional */ }
}
```

- Requests MUST include a string or integer ID
- Unlike base JSON-RPC, the ID MUST NOT be `null`
- The request ID MUST NOT match any other in-flight request from the same sender

### Result Responses

Sent when the operation completes successfully:

```json
{
  "jsonrpc": "2.0",
  "id": "same-as-request",
  "result": {
    "resultType": "complete",
    /* result-specific fields */
  }
}
```

- Result responses MUST include the same ID as the request
- The `resultType` field indicates the type of result:
  - `"complete"` — request completed successfully
  - `"input_required"` — additional input needed (MRTR pattern)
- Results from earlier-protocol servers omitting `resultType` must be treated as `"complete"`

### Error Responses

Sent when the operation fails:

```json
{
  "jsonrpc": "2.0",
  "id": "same-as-request",
  "error": {
    "code": -32602,
    "message": "Error description",
    "data": { /* optional */ }
  }
}
```

### Notifications

One-way messages (no response expected):

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed",
  "params": { /* optional */ }
}
```

- Notifications MUST NOT include an ID

## Error Codes

MCP uses standard JSON-RPC 2.0 error codes (`-32700`, `-32600` to `-32603`) for general protocol failures.

MCP partitions the `-32000` to `-32099` range:

| Range | Purpose |
|---|---|
| `-32000` to `-32019` | Legacy (grandfathered; new codes MUST NOT be allocated here) |
| `-32020` to `-32099` | Reserved for MCP specification |

MCP-defined error codes:

| Code | Name | Description |
|---|---|---|
| `-32020` | `HeaderMismatch` | Header/body metadata mismatch |
| `-32021` | `MissingRequiredClientCapability` | Server requires a capability the client did not declare |
| `-32022` | `UnsupportedProtocolVersion` | Protocol version not supported |

Backward-compatibility codes (MUST NOT be emitted but SHOULD be accepted):

- `-32002` — resource not found (replaced by `-32602`)
- `-32042` — URL elicitation required (2025-11-25 only)

## Statelessness

MCP is a **stateless protocol**: all information needed to process a request is contained in the request itself.

- Servers MUST NOT rely on prior requests to establish context
- Every request supplies metadata in its `_meta` field
- Servers SHOULD be prepared to handle requests for multiple tasks/threads/conversations
- State spanning multiple requests MUST be referenced by explicit identifiers

## `_meta` Fields

The `_meta` property allows clients and servers to attach additional metadata.

### Key Name Format

Keys have two segments: an optional **prefix** and a **name**.

- **Prefix**: labels separated by dots, followed by a slash (e.g., `io.modelcontextprotocol/`)
- Any prefix where the second label is `modelcontextprotocol` or `mcp` is reserved for MCP use
- **Name**: begins/ends with alphanumeric; may contain hyphens, underscores, dots

### Reserved Keys

| Key | Description |
|---|---|
| `progressToken` | Opts into progress notifications |
| `io.modelcontextprotocol/protocolVersion` | Protocol version (required on requests) |
| `io.modelcontextprotocol/clientInfo` | Client name and version |
| `io.modelcontextprotocol/clientCapabilities` | Client capabilities (required on requests) |
| `io.modelcontextprotocol/logLevel` | Minimum log level for a request |
| `io.modelcontextprotocol/subscriptionId` | Correlates notification with subscription |
| `io.modelcontextprotocol/serverInfo` | Server name and version (in results) |
| `traceparent`, `tracestate`, `baggage` | OpenTelemetry trace context |

### Per-Request Protocol Fields (Client → Server)

| Key | Type | Required | Description |
|---|---|---|---|
| `io.modelcontextprotocol/protocolVersion` | `string` | Yes | e.g., `"2026-07-28"` |
| `io.modelcontextprotocol/clientCapabilities` | `ClientCapabilities` | Yes | Capabilities relevant to this request |
| `io.modelcontextprotocol/clientInfo` | `Implementation` | No | Client name and version |
| `io.modelcontextprotocol/logLevel` | `LoggingLevel` | No | Minimum log level |

A request missing any required field is malformed; the server MUST reject with `-32602`.

### Per-Response Protocol Fields (Server → Client)

| Key | Type | Required | Description |
|---|---|---|---|
| `io.modelcontextprotocol/serverInfo` | `Implementation` | No | Server name and version |

## JSON Schema Usage

MCP uses JSON Schema for validation throughout the protocol.

### Schema Dialect

1. **Default dialect**: When no `$schema` field is present, defaults to JSON Schema 2020-12
2. **Explicit dialect**: Schemas MAY include `$schema` to specify a different dialect
3. **Supported dialects**: Implementations MUST support at least 2020-12
4. **Recommendation**: Use JSON Schema 2020-12

### `$ref` Resolution

- Implementations MUST NOT automatically dereference `$ref` values resolving to network URIs
- Opt-in mode MAY be offered but MUST be disabled by default
- Should enforce allowlist of hosts, reject loopback/private addresses, apply timeouts and size limits
- Schemas failing validation due to unresolved external `$ref` SHOULD be rejected

### Composition Keywords

Implementations SHOULD apply reasonable bounds on `anyOf`, `oneOf`, `allOf`, `if/then/else`, and `$defs` to prevent DoS via expensive schema validation.

## Icons

The `icons` property provides visual identifiers for resources, tools, prompts, and implementations.

- `src`: URI (HTTPS or data URI required)
- `mimeType`: Optional MIME type
- `sizes`: Optional size specifications (e.g., `["48x48"]`, `["any"]`)
- `theme`: Optional (`light` or `dark`)

Required MIME support: `image/png`, `image/jpeg`. SHOULD also support `image/svg+xml`, `image/webp`.

Security: treat icon metadata as untrusted; reject unsafe schemes; validate MIME types via magic bytes; fetch without credentials.

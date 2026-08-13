# Client Features

Clients offer capabilities to servers. The core client feature is Elicitation. Roots, Sampling, and Logging are deprecated.

## Elicitation

Elicitation allows servers to request additional information from users. It operates through the MRTR (Multi Round-Trip Requests) pattern — the server returns `InputRequiredResult` and the client fulfills the request before retrying.

### Modes

**Form mode** — structured input with a JSON Schema:

```json
{
  "resultType": "input_required",
  "inputRequests": {
    "user_input": {
      "method": "elicitation/create",
      "params": {
        "mode": "form",
        "message": "Please provide your input",
        "requestedSchema": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "value": { "type": "number" }
          },
          "required": ["name"]
        }
      }
    }
  }
}
```

**URL mode** — out-of-band interaction via a URL:

```json
{
  "mode": "url",
  "message": "Please complete this action",
  "url": "https://example.com/authorize?state=abc123"
}
```

### Client Response

The client retries the original request with `inputResponses`:

```json
{
  "method": "tools/call",
  "params": {
    "name": "original_tool",
    "arguments": { /* original args */ },
    "inputResponses": {
      "user_input": {
        "action": "accept",
        "content": { "name": "Alice", "value": 42 }
      }
    },
    "requestState": "..."
  }
}
```

Actions: `"accept"` or `"decline"`.

---

## Deprecated Features

The following features remain functional but are scheduled for removal. New implementations should not add support for them.

### Roots

**What it did**: Allowed servers to discover the user's working directories.

**Migration**: Pass directories or files via tool parameters, resource URIs, or server configuration.

### Sampling

**What it did**: Allowed servers to request the client to generate text using an LLM.

**Migration**: Integrate directly with LLM provider APIs.

### Logging

**What it did**: Server-initiated log messages to the client via `notifications/message`.

**Migration**: Log to `stderr` (stdio transport) or use OpenTelemetry.

### Other Deprecated Items

- **HTTP+SSE transport** — deprecated since `2025-03-26`. Migrate to Streamable HTTP.
- **`includeContext` values `"thisServer"` and `"allServers"`** — omit the field or use `"none"`.
- **OAuth 2.0 Dynamic Client Registration (RFC 7591)** — use Client ID Metadata Documents instead.

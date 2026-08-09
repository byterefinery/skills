# Server Features

Servers provide three fundamental building blocks for adding context to language models.

## Control Hierarchy

| Primitive | Control | Description | Example |
|---|---|---|---|
| Prompts | User-controlled | Interactive templates invoked by user choice | Slash commands, menu options |
| Resources | Application-controlled | Contextual data attached by the client | File contents, git history |
| Tools | Model-controlled | Functions exposed to the LLM to take actions | API calls, file writing |

---

## Tools

Tools enable models to interact with external systems. They are **model-controlled** — the LLM discovers and invokes them automatically.

### Capability Declaration

```json
{
  "capabilities": {
    "tools": {
      "listChanged": true
    }
  }
}
```

### Protocol Messages

**Listing tools** — `tools/list` (supports pagination and caching):

```json
// Request
{ "method": "tools/list", "params": { "cursor": "optional-cursor" } }

// Response
{
  "result": {
    "resultType": "complete",
    "tools": [
      {
        "name": "get_weather",
        "title": "Weather Information Provider",
        "description": "Get current weather for a location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": { "type": "string", "description": "City or zip" }
          },
          "required": ["location"]
        }
      }
    ],
    "ttlMs": 300000,
    "cacheScope": "public"
  }
}
```

**Calling tools** — `tools/call`:

```json
// Request
{ "method": "tools/call", "params": { "name": "get_weather", "arguments": { "location": "New York" } } }

// Response
{
  "result": {
    "resultType": "complete",
    "content": [
      { "type": "text", "text": "Temperature: 72°F, Partly cloudy" }
    ],
    "isError": false
  }
}
```

### Tool Definition

- `name` — unique identifier (1-128 chars, alphanumeric + `_`, `-`, `.`)
- `title` — optional human-readable display name
- `description` — human-readable description of functionality
- `inputSchema` — JSON Schema defining parameters (must be valid, defaults to 2020-12)
- `outputSchema` — optional JSON Schema for structured results
- `icons` — optional array of icon objects
- `annotations` — optional behavior descriptors (considered untrusted)

For tools with no parameters: `{ "type": "object", "additionalProperties": false }` (recommended).

### Tool Result Content Types

**Unstructured** (in `content` array):

- `text` — plain text
- `image` — base64-encoded image with mimeType
- `audio` — base64-encoded audio with mimeType
- `resource_link` — URI reference to a resource
- `resource` — embedded resource with uri, mimeType, text/blob

**Structured** (in `structuredContent`):

- Any JSON value conforming to `outputSchema` if defined
- Servers SHOULD also return serialized JSON in a TextContent block for backward compatibility

### Tool Names

- SHOULD be 1-128 characters
- Allowed: A-Z, a-z, 0-9, `_`, `-`, `.`
- Scoped per-server; clients aggregating from multiple servers must disambiguate
- Examples: `getUser`, `DATA_EXPORT_v2`, `admin.tools.list`

### Stateful Tools

MCP has no protocol-level session. Servers needing cross-call state should return explicit handles:

```json
// Create state
{ "name": "create_basket", "arguments": {} }
// → { "structuredContent": { "basket_id": "bsk_a1b2c3" } }

// Use handle
{ "name": "add_item", "arguments": { "basket_id": "bsk_a1b2c3", "sku": "..." } }
```

Handle design considerations: authorization validation, opacity, lifetime, expiry errors.

### Error Handling

1. **Protocol Errors** — request structure issues, returned as JSON-RPC errors:
   ```json
   { "error": { "code": -32602, "message": "Unknown tool: invalid_name" } }
   ```

2. **Tool Execution Errors** — actionable feedback for model self-correction, returned with `isError: true`:
   ```json
   {
     "result": {
       "resultType": "complete",
       "content": [{ "type": "text", "text": "Invalid date: must be in the future" }],
       "isError": true
     }
   }
   ```

---

## Resources

Resources allow servers to share data providing context to language models. They are **application-controlled** — the host determines how to incorporate context.

### Capability Declaration

```json
{
  "capabilities": {
    "resources": {
      "listChanged": true,
      "subscribe": true
    }
  }
}
```

### Protocol Messages

**Listing resources** — `resources/list`:

```json
{ "method": "resources/list", "params": { "cursor": "optional" } }
```

**Reading resources** — `resources/read`:

```json
{ "method": "resources/read", "params": { "uri": "file:///project/src/main.rs" } }
```

**Resource templates** — `resources/templates/list` (URI templates per RFC 6570):

```json
{ "method": "resources/templates/list", "params": { "cursor": "optional" } }
```

### Resource Definition

- `uri` — unique identifier
- `name` — resource name
- `title` — optional display name
- `description` — optional description
- `mimeType` — optional MIME type
- `size` — optional size in bytes
- `icons` — optional icons

### Resource Contents

- **Text**: `{ "uri": "...", "mimeType": "...", "text": "content" }`
- **Binary**: `{ "uri": "...", "mimeType": "...", "blob": "base64-data" }`

### Annotations

- `audience` — `["user"]`, `["assistant"]`, or `["user", "assistant"]`
- `priority` — 0.0 (least important) to 1.0 (most important)
- `lastModified` — ISO 8601 timestamp

### Common URI Schemes

- `https://` — web resources the client can fetch directly
- `file://` — filesystem-like resources (may not map to physical filesystem)
- `git://` — Git version control integration
- Custom schemes — must follow RFC 3986

### Error Handling

- Resource not found: `-32602` (Invalid Params). Clients SHOULD also accept `-32002` for backward compatibility.
- Internal errors: `-32603`
- Servers MUST NOT return an empty `contents` array for non-existent resources

---

## Prompts

Prompts are pre-defined templates or instructions that guide language model interactions. They are **user-controlled** — invoked by explicit user choice.

### Capability Declaration

```json
{
  "capabilities": {
    "prompts": {
      "listChanged": true
    }
  }
}
```

### Protocol Messages

**Listing prompts** — `prompts/list`:

```json
{ "method": "prompts/list", "params": { "cursor": "optional" } }
```

**Getting a prompt** — `prompts/get`:

```json
{
  "method": "prompts/get",
  "params": {
    "name": "summarize",
    "arguments": { "topic": "project status" }
  }
}
```

### Prompt Definition

- `name` — unique identifier
- `title` — optional display name
- `description` — optional description
- `arguments` — optional array of argument definitions (each with `name`, `description`, `required`)
- `icons` — optional icons

### Prompt Messages

Prompt responses contain an array of `PromptMessage` objects, each with:

- `role` — `"user"` or `"assistant"`
- `content` — a content block (`text`, `image`, `audio`, `resource_link`, or `resource`)

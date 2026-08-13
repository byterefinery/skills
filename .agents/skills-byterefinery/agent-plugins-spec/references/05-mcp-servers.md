# MCP Servers

## Configuration file

- Location: `mcp.json` at the plugin root
- MUST be a JSON object with required `$schema` and `mcpServers` fields, no other top-level fields
- `mcpServers` is an object keyed by server name, values are server configuration objects
- Empty `mcpServers` is valid

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "server-name": { ... }
  }
}
```

The `$schema` version MUST match the version declared by `plugin.json`.

## Server variants

Each server MUST contain a `type` field and match exactly one closed variant. Unknown fields, unknown `type` values, or fields belonging to another variant make the server entry invalid.

### stdio

Local process execution via standard I/O.

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"stdio"` | Yes | Selects stdio transport |
| `command` | string | Yes | Executable token to launch |
| `args` | string[] | No | Arguments to the executable |
| `env` | object of strings | No | Environment variables |
| `cwd` | string | No | Working directory |

**command rules:**
- Single executable token, not a shell command string
- Either a bare executable name or plugin-relative path starting with `./`
- Bare names resolved via platform executable search; `./` paths resolved against plugin root
- Clients MUST NOT perform placeholder expansion in `command`
- Plugins bundling an executable MUST use plugin-relative `command`

**cwd rules:**
- When omitted, plugin root is used as working directory
- When present, must be one of:
  1. Plugin-relative path starting with `./`
  2. `${PLUGIN_ROOT}` or `${PLUGIN_ROOT}/...`
  3. `${PLUGIN_DATA}` or `${PLUGIN_DATA}/...`
- Plugin-relative and `${PLUGIN_ROOT}` paths must stay within plugin root
- `${PLUGIN_DATA}` paths must stay within plugin data directory

**env rules:**
- Must not contain entries named `PLUGIN_ROOT` or `PLUGIN_DATA`
- Values support `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` expansion
- Keys are not expanded

### streamable-http

Current MCP Streamable HTTP transport.

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"streamable-http"` | Yes | Selects Streamable HTTP transport |
| `url` | string | Yes | MCP endpoint URL |
| `headers` | object of strings | No | Fixed HTTP headers |

**URL rules:**
- MUST be absolute HTTP or HTTPS URL
- MUST NOT contain user information or fragment
- Non-loopback endpoints MUST use HTTPS
- HTTP allowed for `localhost` or loopback IP literals

**Header rules:**
- Names and values must be valid HTTP header fields
- Case-insensitive names; duplicate names under different casing is invalid
- No placeholder or environment-variable expansion in `url`, header names, or header values
- Do not embed credentials in headers — authorization is client-managed

### sse (legacy)

Deprecated HTTP+SSE transport from MCP 2024-11-05. Does not refer to SSE within Streamable HTTP.

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"sse"` | Yes | Selects legacy SSE transport |
| `url` | string | Yes | MCP endpoint URL |
| `headers` | object of strings | No | Fixed HTTP headers |

Same URL and header rules as `streamable-http`.

## Transport support

- Client MUST support at least one of `stdio` or `streamable-http`
- Client SHOULD support both
- `sse` support is OPTIONAL
- Client MUST use the transport declared by `type` for initial connection
- No fallback behavior defined if the declared transport fails

## Example

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "local-validator": {
      "type": "stdio",
      "command": "./bin/validator",
      "args": ["--data", "${PLUGIN_DATA}/validator"],
      "env": {
        "CONFIG": "${PLUGIN_ROOT}/config.json"
      },
      "cwd": "${PLUGIN_ROOT}"
    },
    "deployment-api": {
      "type": "streamable-http",
      "url": "https://deploy.example.com/mcp",
      "headers": {
        "X-Tenant": "public-tenant"
      }
    },
    "legacy-events": {
      "type": "sse",
      "url": "https://legacy.example.com/sse"
    }
  }
}
```

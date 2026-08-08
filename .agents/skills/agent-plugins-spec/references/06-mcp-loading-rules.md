# MCP Loading Rules

## Rule 1 — Fixed source

Clients that support MCP servers MUST load configuration only from `mcp.json` at the plugin root. No inline MCP config in `plugin.json`, no alternative paths.

## Rule 2 — Invalid mcp.json

If `mcp.json` is:
- Not valid JSON
- Targets an unsupported Agent Plugins version
- Targets a different version than `plugin.json`
- Does not satisfy top-level requirements (missing `$schema`/`mcpServers`, extra fields)

Then the client MUST disable MCP for that plugin and continue loading other component types. The client SHOULD report the issue.

## Rule 3 — Invalid server entries

If an individual server entry does not satisfy variant requirements (unknown `type`, missing required fields, extra fields, wrong field types), the client MUST skip that server and continue loading other servers and component types. The client SHOULD report the invalid entry.

## Rule 4 — Unsupported transport

If the client does not support the transport declared by an otherwise valid server entry, it MUST skip that server and continue loading other servers and component types. The client SHOULD report the unsupported transport.

## Rule 5 — Connection failures

If a server fails to start, connect, authenticate, or complete the MCP handshake, the client MUST continue loading other servers and component types. The client SHOULD report the connection failure.

## Failure isolation summary

```
mcp.json invalid  →  disable MCP for this plugin, continue with skills
server entry bad  →  skip that server, continue with other servers/ components
transport unknown →  skip that server, continue with other servers/ components
connection fail   →  skip that server, continue with other servers/ components
```

No single MCP failure should prevent other components from loading.

---
name: mcp
description: Model Context Protocol (MCP) specification reference — protocol architecture, transports, tools, resources, prompts, extensions, and message patterns. Use when building, debugging, or integrating MCP clients, servers, or SDKs.
license: MIT
compatibility: Requires access to the MCP specification repository or documentation
metadata:
  tags:
    - protocol
    - ai
    - json-rpc
    - specification
---

# mcp

## Overview

Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. Built on JSON-RPC 2.0, MCP provides a standardized way to connect language models with the context they need through a client-host-server architecture.

The current stable specification is version `2026-07-28`. The protocol is stateless: every request carries its own protocol version and client capabilities in `_meta` fields. There is no `initialize` handshake — clients call `server/discover` for capability discovery, then issue requests directly.

MCP servers expose three core primitives:

- **Tools** — model-controlled functions the LLM can invoke (e.g., API calls, file operations)
- **Resources** — application-controlled data providing context (e.g., file contents, database schemas)
- **Prompts** — user-controlled templates guiding LLM interactions (e.g., slash commands)

Clients offer **Elicitation** (server-initiated requests for user input) as a core feature. Roots, Sampling, and Logging are deprecated.

## Usage

The MCP specification lives at <https://github.com/modelcontextprotocol/modelcontextprotocol>. The schema is defined in TypeScript with a generated JSON Schema. Documentation is published at <https://modelcontextprotocol.io>.

### Protocol Structure

```
MCP (2026-07-28)
├── Architecture — Host, Client, Server roles
├── Base Protocol — JSON-RPC messages, _meta, statelessness
├── Transports — stdio, Streamable HTTP
├── Message Patterns — Request/Response, MRTR, Subscriptions
├── Server Features — Tools, Resources, Prompts
├── Client Features — Elicitation (Roots/Sampling/Logging deprecated)
├── Utilities — Pagination, Caching, Completion, Logging
├── Extensions — Tasks, MCP Apps, Auth extensions
└── Authorization — OAuth 2.0, OIDC, client registration
```

### Key Design Principles

1. **Servers should be extremely easy to build** — hosts handle orchestration; servers focus on specific capabilities
2. **Servers should be highly composable** — each server provides focused functionality in isolation
3. **Servers cannot read the whole conversation** — full history stays with the host; servers receive only necessary context
4. **Features are progressively negotiable** — core protocol is minimal; capabilities are declared per-request

### Per-Request Metadata

Every request carries protocol metadata in `_meta`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": { "tools": {} },
      "io.modelcontextprotocol/clientInfo": {
        "name": "MyClient",
        "version": "1.0.0"
      }
    }
  }
}
```

Required fields: `protocolVersion`, `clientCapabilities`. Missing required fields result in `-32602` (Invalid params).

### Result Types

All results carry a `resultType` field:

- `"complete"` — request completed successfully
- `"input_required"` — server needs additional input (MRTR pattern)

Results from earlier-protocol servers omitting `resultType` must be treated as `"complete"`.

## Gotchas

- **No `initialize` handshake** — the protocol is stateless. Every request must include `_meta` with `protocolVersion` and `clientCapabilities`. There is no connection-scoped session.
- **`server/discover` is the discovery mechanism** — clients MAY call this before any other request to learn supported versions and capabilities. It is not mandatory but recommended.
- **Tools are model-controlled, resources are application-controlled, prompts are user-controlled** — understanding this hierarchy is critical for security design. Tools execute arbitrary code; resources provide context; prompts guide interactions.
- **Stateless means explicit handles** — servers cannot rely on connection state. Cross-call state (e.g., shopping carts, browser sessions) must use explicit server-minted handles passed as tool arguments.
- **MRTR replaces server-initiated requests** — servers no longer initiate JSON-RPC requests. Instead, they return `InputRequiredResult` (`resultType: "input_required"`) and clients retry with `inputResponses`.
- **`subscriptions/listen` replaces old subscription model** — single long-lived POST-response stream for opted-in notifications. Clients opt in to specific types (`toolsListChanged`, `promptsListChanged`, `resourcesListChanged`, `resourceSubscriptions`).
- **Roots, Sampling, and Logging are deprecated** — pass directories via tool parameters or resource URIs instead of Roots; integrate directly with LLM provider APIs instead of Sampling; log to stderr or use OpenTelemetry instead of Logging.
- **`ping` is removed** — no keepalive mechanism in the protocol. Transports handle connection health independently.
- **`logging/setLevel` is removed** — log level is set per-request via `io.modelcontextprotocol/logLevel` in `_meta`.
- **Error codes are partitioned** — `-32000` to `-32019` is legacy (grandfathered); `-32020` to `-32099` is reserved for MCP spec. MCP defines: `HeaderMismatch` (`-32020`), `MissingRequiredClientCapability` (`-32021`), `UnsupportedProtocolVersion` (`-32022`).
- **Resource not found is now `-32602`** — changed from `-32002`. Clients should still accept `-32002` for backward compatibility with older servers.
- **SSE transport is deprecated** — use Streamable HTTP instead. SSE was soft-deprecated in `2025-03-26`.
- **`$ref` resolution must not fetch network URIs** — implementations must not automatically dereference `$ref` values resolving to network URIs. Opt-in mode may be offered but must be disabled by default.
- **Tool annotations are untrusted** — descriptions, annotations, and other tool metadata should be considered untrusted unless from a trusted server.
- **Tool names are scoped per-server** — clients aggregating tools from multiple servers must implement disambiguation (e.g., prefixing with server identifier).
- **Streamable HTTP response streams are not resumable** — a broken response stream loses the in-flight request. Clients must re-issue as a new request with a new ID.
- **Extensions are always opt-in** — extensions require explicit capability negotiation. They are disabled by default and evolve independently of the core protocol.
- **`x-mcp-header` constraints** — only on primitive types (integer, string, boolean; not `number`), must be case-insensitively unique, must match HTTP token syntax. Clients must reject tools with violating `x-mcp-header` values.

## References

- [01-architecture](references/01-architecture.md) — Host/Client/Server roles, capability negotiation, design principles
- [02-base-protocol](references/02-base-protocol.md) — JSON-RPC messages, _meta fields, statelessness, error codes, JSON Schema
- [03-transports](references/03-transports.md) — stdio and Streamable HTTP transport bindings
- [04-message-patterns](references/04-message-patterns.md) — Request/Response, MRTR, Subscriptions, Cancellation, Progress
- [05-server-features](references/05-server-features.md) — Tools, Resources, Prompts — full protocol messages and data types
- [06-client-features](references/06-client-features.md) — Elicitation, deprecated features (Roots, Sampling, Logging)
- [07-utilities](references/07-utilities.md) — Pagination, Caching, Completion, Logging
- [08-extensions](references/08-extensions.md) — Extension model, Tasks, MCP Apps, Auth extensions
- [09-authorization](references/09-authorization.md) — OAuth 2.0, OIDC, Dynamic Client Registration, client metadata

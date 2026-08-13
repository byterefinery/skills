# Extensions

MCP extensions are optional additions beyond the core protocol. They enable modular, specialized, or experimental functionality. Extensions are always opt-in and require explicit support from both client and server.

## Extension Identifiers

Format: `{vendor-prefix}/{extension-name}`

- Official extensions use `io.modelcontextprotocol` prefix
- Third-party extensions use reversed domain names (e.g., `com.example/my-extension`)
- Any prefix where the second label is `modelcontextprotocol` or `mcp` is reserved

## Negotiation

Extensions are advertised in the `extensions` field of capabilities.

**Client capabilities** (in `_meta` of each request):

```json
{
  "io.modelcontextprotocol/clientCapabilities": {
    "extensions": {
      "io.modelcontextprotocol/tasks": {},
      "io.modelcontextprotocol/ui": {
        "mimeTypes": ["text/html;profile=mcp-app"]
      }
    }
  }
}
```

**Server capabilities** (in `server/discover` response):

```json
{
  "capabilities": {
    "tools": {},
    "extensions": {
      "io.modelcontextprotocol/tasks": {},
      "io.modelcontextprotocol/ui": {}
    }
  }
}
```

Each extension specifies the schema of its settings object; an empty object indicates no settings.

## Graceful Degradation

If one side supports an extension but the other doesn't, the supporting side falls back to core protocol behavior or rejects the request if the extension is mandatory.

## Extension Lifecycle

1. **Propose** — create a SEP (Extensions Track) in the main MCP repository
2. **Implement** — build at least one reference implementation in an official SDK
3. **Review** — core maintainers review and approve
4. **Publish** — add to the extension repository
5. **Adopt** — other clients, servers, and SDKs implement

Extensions evolve independently of the core protocol. Breaking changes should use a new identifier.

---

## MCP Tasks

**Identifier**: `io.modelcontextprotocol/tasks`

Asynchronous task execution for long-running operations, with polling, mid-flight input, and durable handles.

### Why Tasks

- **No long-lived connections** — blocking ties up connections; many intermediaries impose timeouts
- **Crash resilience** — task IDs are durable handles; clients can resume polling after reconnecting
- **Progress visibility** — tasks carry status metadata (`working`, `input_required`, `completed`, `failed`, `cancelled`)
- **Mid-flight interaction** — tasks move to `input_required` and the client responds via `tasks/update`
- **Server-directed** — the server decides per-request whether to create a task

### Flow

1. **Capability negotiation** — client includes `io.modelcontextprotocol/tasks` in capabilities
2. **Task creation** — server returns `CreateTaskResult` (`resultType: "task"`) with `taskId`, status, TTL, polling interval
3. **Polling** — client calls `tasks/get` with `taskId`
4. **Mid-flight input** — if `input_required`, client responds via `tasks/update`
5. **Completion** — `tasks/get` returns final result or error
6. **Cancellation** — client sends `tasks/cancel` (cooperative, not mandatory)

### Task Statuses

- `working` — task is being processed
- `input_required` — task needs client input
- `completed` — task finished successfully
- `failed` — task failed with an error
- `cancelled` — task was cancelled

---

## MCP Apps

**Identifier**: `io.modelcontextprotocol/ui`

Allows MCP servers to display interactive UI elements (charts, forms, video players) inline within conversations.

- Servers return HTML content with `text/html;profile=mcp-app` MIME type
- Clients render the content in a sandboxed iframe
- Extension settings specify supported MIME types

---

## Authorization Extensions

Live in the `modelcontextprotocol/ext-auth` repository.

### OAuth Client Credentials

**Identifier**: `io.modelcontextprotocol/oauth-client-credentials`

OAuth 2.0 client credentials flow for machine-to-machine authentication.

### Enterprise-Managed Authorization

Framework for enterprise environments requiring centralized access control and policy enforcement.

---

## Creating Extensions

- Extension specs must use RFC 2119 language (MUST, SHOULD, MAY)
- Must have an associated working group or interest group
- SDKs can choose which extensions to implement (not required for conformance)
- Extensions are disabled by default and require explicit opt-in
- Prefer capability flags or versioning within the extension settings for non-breaking changes
- Use a new identifier for breaking changes

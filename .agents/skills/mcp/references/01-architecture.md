# Architecture

The Model Context Protocol follows a client-host-server architecture where each host can run multiple client instances. MCP is a stateless protocol: every request is self-contained and carries its own protocol version and capabilities.

## Core Components

### Host

The host process acts as the container and coordinator:

- Creates and manages multiple client instances
- Controls client connection permissions and lifecycle
- Enforces security policies and consent requirements
- Handles user authorization decisions
- Coordinates AI/LLM integration and sampling
- Manages context aggregation across clients

### Clients

Each client is created by the host and communicates with exactly one server:

- Communicates with exactly one server (1:1 relationship)
- Attaches protocol version and capabilities to every request
- Routes protocol messages bidirectionally
- Manages subscriptions and notifications
- Maintains security boundaries between servers

### Servers

Servers provide specialized context and capabilities:

- Expose resources, tools, and prompts via MCP primitives
- Operate independently with focused responsibilities
- Request client input (sampling, elicitation) via `InputRequiredResult` within a reply
- Must respect security constraints
- Can be local processes or remote services

## Capability Negotiation

MCP uses a capability-based negotiation system where clients and servers declare their supported features on each request.

**Client capabilities** are included in `_meta.io.modelcontextprotocol/clientCapabilities` on every request.

**Server capabilities** are advertised in response to `server/discover`, which clients may call before any other request for up-front capability discovery.

```
Sequence:
  Client -> Server: server/discover (optional, for discovery)
  Server -> Client: supported versions + capabilities

  Client -> Server: Request (with _meta: version, clientCapabilities)
  Server -> Client: Response (with _meta: serverInfo)
```

Each capability unlocks specific protocol features on a per-request basis. For example:

- Implemented server features must be advertised in the server's capabilities
- Receiving resource update notifications requires opening a `subscriptions/listen` stream
- Tool invocation requires the server to declare tool capabilities

## Design Principles

1. **Servers should be extremely easy to build** — hosts handle complex orchestration; servers focus on specific, well-defined capabilities with simple interfaces
2. **Servers should be highly composable** — each server provides focused functionality in isolation; multiple servers combine seamlessly
3. **Servers cannot read the whole conversation** — servers receive only necessary contextual information; full conversation history stays with the host; each server maintains isolation
4. **Features can be added progressively** — core protocol provides minimal required functionality; additional capabilities are negotiated as needed; backwards compatibility is maintained

## Security Architecture

- **User Consent and Control** — users must explicitly consent to and understand all data access and operations
- **Data Privacy** — hosts must obtain explicit user consent before exposing user data to servers
- **Tool Safety** — tools represent arbitrary code execution; hosts must obtain explicit user consent before invoking any tool
- **Isolation** — servers cannot "see into" other servers; cross-server interactions are controlled by the host

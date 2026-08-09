---
name: a2a
description: Agent2Agent (A2A) Protocol v1.0 — enables communication and interoperability between opaque agentic applications. Use when building A2A servers (exposing agents), A2A clients (connecting to agents), agent cards, multi-agent orchestration, or understanding how A2A complements MCP. Covers protocol data model, operations, protocol bindings (JSON-RPC, gRPC, HTTP/REST), streaming (SSE), push notifications, security, and Python SDK patterns.
license: Apache-2.0
compatibility: Requires Python 3.12+, uv, a2a-sdk (pip install a2a-sdk)
allowed-tools: Bash(python:*) Bash(curl:*) Read Write
metadata:
  tags:
    - ai
    - agents
    - protocol
    - interoperability
    - linux-foundation
---

# a2a

Agent2Agent (A2A) Protocol v1.0 — an open standard enabling communication and interoperability between independent, opaque AI agent systems. A2A provides a common language for agents built with diverse frameworks by different vendors to discover, collaborate, and exchange structured data without exposing internal state, memory, or tools.

## Overview

A2A sits at the agent-to-agent layer of the agentic stack, complementing MCP (which connects agents to tools/resources). Key characteristics:

- **Transport:** HTTP(S) with JSON-RPC 2.0, gRPC, or HTTP/REST bindings
- **Data model:** Protocol Buffers (canonical), JSON serialization (ProtoJSON convention)
- **Discovery:** Agent Cards at `/.well-known/agent-card.json` (RFC 8615)
- **Interaction modes:** Synchronous request/response, SSE streaming, push notifications (webhooks)
- **Task model:** Stateful tasks with defined lifecycle, multi-turn conversations, context grouping
- **Opacity:** Agents collaborate without exposing internal logic, memory, or proprietary tools

A2A is a Linux Foundation project contributed by Google. SDKs exist for Python, Go, JavaScript/TypeScript, Java, and .NET.

## Usage

### Server (exposing an agent)

```python
from a2a import AgentCard, AgentInterface, AgentCapabilities, AgentSkill
from a2a.server import DefaultRequestHandler, InMemoryTaskStore
from a2a.server.apps.starlette import create_agent_card_routes, create_jsonrpc_routes
from starlette.applications import Starlette
import uvicorn

# 1. Define Agent Card
agent_card = AgentCard(
    name="My Agent",
    description="An agent that does X",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supported_interfaces=[AgentInterface(
        url="http://127.0.0.1:8000",
        protocol_binding="JSONRPC",
        protocol_version="1.0",
    )],
    capabilities=AgentCapabilities(streaming=True),
    skills=[AgentSkill(
        id="analyze",
        name="Data Analysis",
        description="Analyzes data and generates reports",
        tags=["analysis", "reports"],
        examples=["Analyze this dataset", "Generate a summary"],
    )],
)

# 2. Implement AgentExecutor (see references/06-python-sdk.md)
executor = MyAgentExecutor()

# 3. Wire up the server
request_handler = DefaultRequestHandler(
    agent_executor=executor,
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

app = Starlette(routes=[
    *create_agent_card_routes(agent_card),
    *create_jsonrpc_routes(request_handler, '/'),
])

uvicorn.run(app, host='127.0.0.1', port=8000)
```

### Client (connecting to an agent)

```python
from a2a import Client, ClientConfig, Message, Part, Role, SendMessageRequest
from a2a.client import create_client

# 1. Fetch Agent Card
agent_card = await fetch_agent_card("https://agent.example.com")

# 2. Create client
client = create_client(agent_card, ClientConfig())

# 3. Send message
request = SendMessageRequest(
    message=Message(
        role=Role.ROLE_USER,
        parts=[Part(text="Analyze this data")],
        message_id="msg-1",
    ),
)

async for response in client.send_message(request):
    if response.task:
        print(f"Task: {response.task.id}, State: {response.task.status.state}")
    elif response.message:
        print(f"Message: {response.message.parts[0].text}")
```

### Streaming client

```python
from a2a.client import create_client
from a2a import ClientConfig

streaming_client = create_client(agent_card, ClientConfig(streaming=True))

async for event in streaming_client.send_message(request):
    if event.task:
        print(f"Task started: {event.task.id}")
    elif event.status_update:
        print(f"Status: {event.status_update.status.state}")
    elif event.artifact_update:
        print(f"Artifact: {event.artifact_update.artifact.name}")

await streaming_client.close()
```

## Gotchas

- **A2A is not MCP** — A2A handles agent-to-agent collaboration (stateful, multi-turn, opaque). MCP handles agent-to-tool connections (stateless, structured I/O). An agent uses A2A to talk to other agents and MCP internally to use its own tools. Do not confuse the two.
- **Agent Card `name` must match the directory name** — when using `skman.py`, the frontmatter `name` field must match the directory basename exactly.
- **Tasks are immutable in terminal states** — once a task reaches `COMPLETED`, `FAILED`, `CANCELED`, or `REJECTED`, it cannot be restarted. Follow-ups must create a new task within the same `contextId`.
- **`contextId` groups related tasks** — use the same `contextId` to maintain conversational continuity across multiple tasks. The server generates `contextId` on the first interaction; the client echoes it in subsequent messages.
- **`taskId` is server-generated** — clients cannot specify their own `taskId`. The server generates it when creating a new task.
- **Streaming requires server capability** — check `AgentCard.capabilities.streaming` before using `SendStreamingMessage` or `SubscribeToTask`. Without it, the server returns `UnsupportedOperationError`.
- **Push notifications require server capability** — check `AgentCard.capabilities.pushNotifications` before configuring webhooks. Push notification webhooks always use plain HTTP with JSON payloads regardless of the agent's primary protocol binding.
- **Extended Agent Card needs authentication** — `GetExtendedAgentCard` requires authentication via schemes declared in the public Agent Card. Only available if `capabilities.extendedAgentCard` is `true`.
- **JSON field naming is camelCase** — all JSON serializations use camelCase (not snake_case from protobuf). Enum values use SCREAMING_SNAKE_CASE as defined in the proto.
- **Timestamps are ISO 8601 UTC** — all timestamps use `YYYY-MM-DDTHH:mm:ss.sssZ` format.
- **`return_immediately` controls blocking** — when `false` (default), `SendMessage` blocks until the task reaches a terminal or interrupted state. When `true`, it returns immediately with the task in an in-progress state.
- **Multiple streams per task are allowed** — an agent may serve multiple concurrent streams for the same task. Closing one stream does not affect others.
- **Content-Type is `application/a2a+json`** — use this media type for A2A HTTP requests, not `application/json`.
- **`A2A-Version` header** — clients must send the protocol version (e.g., `A2A-Version: 1.0`). Empty values are interpreted as version 0.3.
- **`tenant` field for multi-tenancy** — when an `AgentInterface` declares a `tenant` value, the client must echo it in every request. If not declared, omit the field entirely.
- **Extensions use URIs** — extensions are identified by URIs, activated via `A2A-Extensions` header, and carry data in `metadata` maps keyed by the extension URI.
- **Parts are oneof content** — a `Part` contains exactly one of: `text`, `raw` (base64 bytes), `url` (string URI), or `data` (structured JSON value).
- **Artifacts are task outputs, not messages** — use `Artifacts` for concrete results of a task. Use `Messages` for communication (questions, status updates, clarifications).
- **Security credentials go in HTTP headers** — A2A protocol payloads never carry identity information. Authentication uses standard HTTP headers (`Authorization: Bearer <token>`, etc.).

## References

- [01-data-model](references/01-data-model.md) — Core data types: Task, Message, Part, Artifact, AgentCard, AgentSkill
- [02-operations](references/02-operations.md) — Core operations: SendMessage, SendStreamingMessage, GetTask, ListTasks, CancelTask, SubscribeToTask, push notification CRUD
- [03-protocol-bindings](references/03-protocol-bindings.md) — JSON-RPC, gRPC, HTTP/REST method mappings, error codes, custom bindings
- [04-streaming-push](references/04-streaming-push.md) — SSE streaming, push notifications, webhook security, delivery semantics
- [05-security](references/05-security.md) — Authentication schemes, authorization, TLS, tracing, enterprise patterns
- [06-python-sdk](references/06-python-sdk.md) — Python SDK patterns: AgentExecutor, EventQueue, TaskStore, client usage
- [07-a2a-vs-mcp](references/07-a2a-vs-mcp.md) — A2A vs MCP comparison, complementary roles, integration patterns

# A2A vs MCP: Complementary Protocols

A2A and MCP address distinct but complementary needs in the agentic ecosystem.

## Core Distinction

| Aspect | A2A | MCP |
|---|---|---|
| **Domain** | Agent-to-Agent | Agent-to-Tool/Resource |
| **Interaction** | Collaborative, conversational | Functional, structured I/O |
| **State** | Stateful (tasks, contexts) | Stateless (per-call) |
| **Autonomy** | Peers negotiate and collaborate | Agent controls the tool |
| **Modality** | Rich (text, files, structured data, multi-turn) | Structured inputs/outputs |
| **Discovery** | Agent Cards | Tool descriptions |
| **Transport** | HTTP(S), JSON-RPC, gRPC | Stdio, SSE, HTTP |

## When to Use A2A

Use A2A when agents need to:
- **Collaborate as peers** — negotiate, delegate, and coordinate
- **Maintain state** — track long-running tasks across interactions
- **Exchange rich content** — text, files, structured data, multi-turn conversations
- **Preserve opacity** — collaborate without exposing internal tools or logic
- **Handle async work** — streaming updates, push notifications, human-in-the-loop

Example scenarios:
- Customer service agent delegating to billing agent
- Travel agent coordinating with flight, hotel, and activity agents
- Research agent collaborating with data analysis agent
- Orchestrator agent managing specialized sub-agents

## When to Use MCP

Use MCP when agents need to:
- **Access tools** — calculators, databases, APIs, file systems
- **Query resources** — structured data retrieval
- **Perform discrete functions** — well-defined inputs and outputs
- **Integrate external systems** — connect to existing services

Example scenarios:
- Agent calling a weather API
- Agent querying a database
- Agent using a calculator tool
- Agent reading/writing files

## The Auto Repair Shop Example

```
Customer ──A2A──> Shop Manager Agent
                        │
                        ├──A2A──> Parts Supplier Agent
                        │
                        ├──A2A──> Mechanic Agent
                        │         │
                        │         ├──MCP──> Diagnostic Scanner
                        │         ├──MCP──> Repair Manual DB
                        │         └──MCP──> Platform Lift
```

- **A2A** handles the higher-level, conversational, task-oriented interactions
- **MCP** enables the mechanic agent to use its specific, structured tools

## Integration Patterns

### Pattern 1: A2A Server with MCP Tools

An A2A server internally uses MCP to access its tools:

```python
# A2A Server
class MyAgentExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        # Agent logic
        result = await self.process(context.message)

        # Internally, the agent uses MCP tools
        data = await self.mcp_client.call_tool("query_database", {...})
        result = await self.llm.generate(prompt, context=[data])

        # Return via A2A
        await event_queue.send(TaskArtifactUpdateEvent(..., artifact=Artifact(parts=[Part(text=result)])))
```

### Pattern 2: A2A Client Using MCP for Discovery

A client agent discovers A2A agents and uses MCP for its own tools:

```python
# Client Agent
class OrchestratorAgent:
    async def handle_request(self, user_request):
        # Use MCP tool to search for agents
        agents = await self.mcp_client.call_tool("search_agents", {"skill": "analysis"})

        # Use A2A to collaborate with discovered agent
        client = create_client(agents[0].agent_card, ClientConfig())
        result = await client.send_message(SendMessageRequest(...))

        # Use MCP for local processing
        formatted = await self.mcp_client.call_tool("format_output", {"data": result})

        return formatted
```

### Pattern 3: A2A Skills as MCP Resources

An A2A server can expose skills as MCP-compatible resources for well-defined, tool-like interactions:

```python
# A2A Agent Card skill exposed as MCP tool
{
  "skills": [
    {
      "id": "currency-convert",
      "name": "Currency Converter",
      "description": "Convert between currencies",
      "input_modes": ["application/json"],
      "output_modes": ["application/json"]
    }
  ]
}

# Same capability as MCP tool
{
  "name": "currency_convert",
  "description": "Convert between currencies",
  "inputSchema": {
    "type": "object",
    "properties": {
      "amount": {"type": "number"},
      "from": {"type": "string"},
      "to": {"type": "string"}
    }
  }
}
```

## Key Differences in Practice

### Task Model
- **A2A:** Tasks are stateful, have lifecycle states, support multi-turn, and produce artifacts
- **MCP:** Each tool call is independent and stateless

### Error Handling
- **A2A:** Rich error model with specific error types (TaskNotFoundError, InputRequired, etc.)
- **MCP:** Standard JSON-RPC errors

### Content Exchange
- **A2A:** Parts support text, binary data, URLs, and structured data with media types
- **MCP:** Structured JSON inputs and outputs

### Authentication
- **A2A:** Full security model with OAuth2, OIDC, mTLS, API keys, extended cards
- **MCP:** Transport-level auth (stdio, SSE headers)

### Discovery
- **A2A:** Agent Cards at `/.well-known/agent-card.json`, curated registries
- **MCP:** Tool schemas in server descriptions

## Protocol Stack

```
┌─────────────────────────────────────┐
│         A2A Protocol                │  ← Agent-to-Agent collaboration
│  (Tasks, Messages, Artifacts)       │
├─────────────────────────────────────┤
│         MCP Protocol                │  ← Agent-to-Tool integration
│  (Tools, Resources, Prompts)        │
├─────────────────────────────────────┤
│      Agent Framework               │  ← LangGraph, ADK, CrewAI, etc.
│  (State management, orchestration)  │
├─────────────────────────────────────┤
│         LLM Model                  │  ← Reasoning engine
└─────────────────────────────────────┘
```

## Summary

- **A2A is for agents partnering on tasks** — stateful, multi-turn, opaque collaboration
- **MCP is for agents using capabilities** — stateless, structured tool invocation
- **They complement each other** — A2A handles inter-agent communication, MCP handles intra-agent tool access
- **An agent typically uses both** — A2A to talk to other agents, MCP to use its own tools

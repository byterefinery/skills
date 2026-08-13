# A2A Python SDK Patterns

The A2A Python SDK (`pip install a2a-sdk`) provides building blocks for both servers and clients.

## Server Architecture

### Core Components

```
┌─────────────────────────────────────────────┐
│                 Starlette/FastAPI            │
│  ┌───────────────────────────────────────┐   │
│  │       DefaultRequestHandler           │   │
│  │  ┌─────────────┐  ┌───────────────┐   │   │
│  │  │  TaskStore   │  │  AgentExecutor │   │   │
│  │  │ (persistence)│  │  (business     │   │   │
│  │  │              │  │   logic)       │   │   │
│  │  └─────────────┘  └───────────────┘   │   │
│  └───────────────────────────────────────┘   │
│  ┌───────────────────────────────────────┐   │
│  │         Agent Card (metadata)          │   │
│  └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### AgentExecutor Interface

The `AgentExecutor` is the bridge between A2A protocol handling and your agent's logic:

```python
from a2a.server.agent_execution import AgentExecutor, RequestContext, EventQueue
from a2a.types import (
    Task, TaskStatus, TaskState, Message, Part, Role,
    TaskStatusUpdateEvent, TaskArtifactUpdateEvent, Artifact
)
import uuid

class MyAgentExecutor(AgentExecutor):
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Handle incoming SendMessage or SendStreamingMessage requests."""
        # 1. Create initial task if none exists
        task_id = str(uuid.uuid4())
        context_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            context_id=context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_SUBMITTED),
        )
        await event_queue.send(task)

        # 2. Enqueue working status
        await event_queue.send(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                status=TaskStatus(
                    state=TaskState.TASK_STATE_WORKING,
                    message=Message(
                        role=Role.ROLE_AGENT,
                        parts=[Part(text="Processing your request...")],
                        message_id=str(uuid.uuid4()),
                    ),
                ),
            )
        )

        # 3. Execute business logic
        result = await self.process_request(context.message)

        # 4. Enqueue artifact
        await event_queue.send(
            TaskArtifactUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                artifact=Artifact(
                    artifact_id=str(uuid.uuid4()),
                    name="result",
                    parts=[Part(text=result)],
                ),
                last_chunk=True,
            )
        )

        # 5. Enqueue completion status
        await event_queue.send(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
            )
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Handle CancelTask requests."""
        task = context.current_task
        if task:
            task.status.state = TaskState.TASK_STATE_CANCELED
            await event_queue.send(task)

    async def process_request(self, message: Message) -> str:
        # Your agent's business logic here
        return "Result from agent processing"
```

### RequestContext

Provides information about the incoming request:

```python
# Access the user's message
message = context.message

# Access current task (if continuing a task)
current_task = context.current_task

# Access task store for persistence
task_store = context.task_store
```

### EventQueue

Used to send events back to the client:

```python
# Send a Task object
await event_queue.send(task)

# Send status update
await event_queue.send(TaskStatusUpdateEvent(...))

# Send artifact update
await event_queue.send(TaskArtifactUpdateEvent(...))

# Send a message (for message-only responses)
await event_queue.send(Message(...))
```

### TaskStore

Manages task lifecycle and persistence:

```python
from a2a.server import InMemoryTaskStore

# In-memory (default, for development)
task_store = InMemoryTaskStore()

# Custom persistent store (implement TaskStore interface)
class DatabaseTaskStore(TaskStore):
    async def get_task(self, task_id: str) -> Task | None: ...
    async def add_task(self, task: Task) -> None: ...
    async def update_task(self, task: Task) -> None: ...
    async def list_tasks(self, ...) -> list[Task]: ...
```

### Server Setup

```python
from a2a import AgentCard, AgentInterface, AgentCapabilities, AgentSkill
from a2a.server import DefaultRequestHandler, InMemoryTaskStore
from a2a.server.apps.starlette import (
    create_agent_card_routes,
    create_jsonrpc_routes,
    create_rest_routes,
)
from starlette.applications import Starlette
import uvicorn

agent_card = AgentCard(
    name="My Agent",
    description="An example A2A agent",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supported_interfaces=[AgentInterface(
        url="http://127.0.0.1:8000",
        protocol_binding="JSONRPC",
        protocol_version="1.0",
    )],
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
        extended_agent_card=True,
    ),
    skills=[AgentSkill(
        id="analyze",
        name="Data Analysis",
        description="Analyzes data",
        tags=["analysis"],
        examples=["Analyze this dataset"],
    )],
)

# Optional: extended card for authenticated users
extended_agent_card = AgentCard(
    name="My Agent (Extended)",
    description="Full-featured agent",
    version="1.0.0",
    # ... same as above but with additional skills
    skills=[
        AgentSkill(id="analyze", name="Data Analysis", ...),
        AgentSkill(id="premium", name="Premium Analysis", ...),
    ],
)

request_handler = DefaultRequestHandler(
    agent_executor=MyAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
    extended_agent_card=extended_agent_card,
)

app = Starlette(routes=[
    *create_agent_card_routes(agent_card),        # /.well-known/agent-card.json
    *create_jsonrpc_routes(request_handler, '/'), # JSON-RPC endpoints
    # *create_rest_routes(request_handler, '/'),   # REST endpoints (optional)
])

uvicorn.run(app, host='127.0.0.1', port=8000)
```

### Multi-Turn with Input Required

```python
class MultiTurnExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task

        # First turn: check if we need clarification
        if task is None or len(task.history) == 1:
            # Need more info
            await event_queue.send(
                TaskStatusUpdateEvent(
                    task_id=task.id,
                    context_id=task.context_id,
                    status=TaskStatus(
                        state=TaskState.TASK_STATE_INPUT_REQUIRED,
                        message=Message(
                            role=Role.ROLE_AGENT,
                            parts=[Part(text="What currency would you like to convert to?")],
                            message_id=str(uuid.uuid4()),
                        ),
                    ),
                )
            )
            return

        # Second turn: process with the provided info
        result = await self.process_with_clarification(context.message, task)
        # ... enqueue artifact and completion
```

## Client Patterns

### Basic Client

```python
from a2a import Client, ClientConfig, Message, Part, Role, SendMessageRequest
from a2a.client import create_client

# Fetch agent card
from a2a.client.card_resolver import A2ACardResolver

card_resolver = A2ACardResolver(base_url="http://127.0.0.1:8000")
agent_card = await card_resolver.get_agent_card()

# Create client
client = create_client(agent_card, ClientConfig())

# Send message
request = SendMessageRequest(
    message=Message(
        role=Role.ROLE_USER,
        parts=[Part(text="Hello, agent!")],
        message_id=str(uuid.uuid4()),
    ),
)

async for response in client.send_message(request):
    if response.task:
        print(f"Task: {response.task.id}")
        print(f"State: {response.task.status.state}")
        for artifact in response.task.artifacts:
            for part in artifact.parts:
                if part.text:
                    print(f"Result: {part.text}")
    elif response.message:
        print(f"Message: {response.message.parts[0].text}")
```

### Streaming Client

```python
from a2a.client import create_client
from a2a import ClientConfig

streaming_client = create_client(
    agent_card,
    ClientConfig(streaming=True),
)

async for event in streaming_client.send_message(request):
    if event.task:
        print(f"Task started: {event.task.id}")
    elif event.status_update:
        print(f"Status: {event.status_update.status.state}")
        if event.status_update.status.message:
            print(f"  Message: {event.status_update.status.message.parts[0].text}")
    elif event.artifact_update:
        artifact = event.artifact_update.artifact
        print(f"Artifact: {artifact.name}")
        for part in artifact.parts:
            if part.text:
                print(f"  Content: {part.text[:100]}...")

await streaming_client.close()
```

### Get Task

```python
task = await client.get_task(task_id="task-uuid", history_length=5)
print(f"Task state: {task.status.state}")
```

### List Tasks

```python
from a2a import ListTasksRequest

response = await client.list_tasks(
    ListTasksRequest(
        context_id="ctx-uuid",
        status=TaskState.TASK_STATE_WORKING,
        page_size=10,
    )
)
for task in response.tasks:
    print(f"{task.id}: {task.status.state}")
```

### Cancel Task

```python
updated_task = await client.cancel_task(task_id="task-uuid")
print(f"Canceled: {updated_task.status.state}")
```

### Subscribe to Task

```python
async for event in client.subscribe_to_task(task_id="task-uuid"):
    if event.task:
        print(f"Current state: {event.task.status.state}")
    elif event.status_update:
        print(f"Update: {event.status_update.status.state}")
    elif event.artifact_update:
        print(f"Artifact: {event.artifact_update.artifact.name}")
```

### Push Notifications

```python
from a2a import TaskPushNotificationConfig, AuthenticationInfo

# Create push notification config
config = await client.create_task_push_notification_config(
    task_id="task-uuid",
    config=TaskPushNotificationConfig(
        url="https://client.example.com/webhook",
        token="validation-token",
        authentication=AuthenticationInfo(
            scheme="Bearer",
            credentials="webhook-token",
        ),
    ),
)

# List configs
configs = await client.list_task_push_notification_configs(task_id="task-uuid")

# Delete config
await client.delete_task_push_notification_config(
    task_id="task-uuid",
    config_id=config.id,
)
```

### Extended Agent Card

```python
# With authentication
extended_card = await client.get_extended_agent_card()
print(f"Extended skills: {[s.name for s in extended_card.skills]}")
```

## Integration with LLM Frameworks

### LangGraph Integration

```python
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

class LangGraphAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = create_react_agent(
            model=ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
            tools=[get_exchange_rate_tool],
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or self._create_task(context, event_queue)

        # Working status
        await event_queue.send(TaskStatusUpdateEvent(
            task_id=task.id,
            context_id=task.context_id,
            status=TaskStatus(
                state=TaskState.TASK_STATE_WORKING,
                message=Message(
                    role=Role.ROLE_AGENT,
                    parts=[Part(text="Looking up exchange rates...")],
                    message_id=str(uuid.uuid4()),
                ),
            ),
        ))

        # Run agent
        user_text = context.message.parts[0].text
        result = await self.agent.ainvoke({
            "messages": [HumanMessage(content=user_text)],
        })

        # Artifact
        await event_queue.send(TaskArtifactUpdateEvent(
            task_id=task.id,
            context_id=task.context_id,
            artifact=Artifact(
                artifact_id=str(uuid.uuid4()),
                name="answer",
                parts=[Part(text=result["messages"][-1].content)],
            ),
            last_chunk=True,
        ))

        # Completion
        await event_queue.send(TaskStatusUpdateEvent(
            task_id=task.id,
            context_id=task.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
        ))
```

## Key SDK Types Reference

| Type | Module | Purpose |
|---|---|---|
| `AgentCard` | `a2a` | Agent metadata |
| `AgentSkill` | `a2a` | Agent capability |
| `AgentInterface` | `a2a` | Endpoint declaration |
| `AgentCapabilities` | `a2a` | Feature flags |
| `Task` | `a2a` | Unit of work |
| `TaskStatus` | `a2a` | Task lifecycle state |
| `TaskState` | `a2a` | State enum |
| `Message` | `a2a` | Communication turn |
| `Part` | `a2a` | Content container |
| `Artifact` | `a2a` | Task output |
| `Role` | `a2a` | Message sender (USER/AGENT) |
| `SendMessageRequest` | `a2a` | Send message request |
| `TaskStatusUpdateEvent` | `a2a` | Status change event |
| `TaskArtifactUpdateEvent` | `a2a` | Artifact update event |
| `AgentExecutor` | `a2a.server.agent_execution` | Server logic interface |
| `RequestContext` | `a2a.server.agent_execution` | Request context |
| `EventQueue` | `a2a.server.agent_execution` | Event sender |
| `DefaultRequestHandler` | `a2a.server` | Request routing |
| `InMemoryTaskStore` | `a2a.server` | Task persistence |
| `Client` | `a2a.client` | A2A client |
| `ClientConfig` | `a2a` | Client configuration |
| `create_client` | `a2a.client` | Client factory |

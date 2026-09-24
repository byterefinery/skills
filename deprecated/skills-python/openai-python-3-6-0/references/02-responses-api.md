# openai-python 3.6.0 — Responses API

The Responses API is the primary way to interact with OpenAI models. `client.responses` (async: `AsyncResponses` on `AsyncOpenAI`) covers creation, retrieval, cancellation, compaction, streaming, structured outputs, tools, background execution, and WebSocket connections.

## Creating responses

```python
response = client.responses.create(
    model="gpt-5.5",
    input="How do I check if a Python object is an instance of a class?",
    instructions="You are a coding assistant.",
)
print(response.output_text)  # convenience: concatenated message output text
```

`input` is either a plain string or a list of typed message dicts (role + content, including `input_text` / `input_image` content parts for vision). Key optional params:

- `instructions` — standing system-style instructions for the response
- `previous_response_id` — continue a stored conversation without resending history
- `store` — whether OpenAI stores the response (default true); required for `previous_response_id` chains
- `metadata` — up to 16 user-defined key/value tags
- `reasoning`, `max_output_tokens`, `max_tool_calls`, `parallel_tool_calls`
- `prompt`, `prompt_cache_key`, `prompt_cache_options`, `prompt_cache_retention` — reusable prompts and caching
- `moderation`, `safety_identifier`, `service_tier`, `context_management`
- `tools`, `tool_choice` — see structured outputs and tools below

Vision input (image URL or base64 data URL):

```python
response = client.responses.create(
    model="gpt-5.5",
    input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": "What is in this image?"},
            {"type": "input_image", "image_url": "https://.../image.jpg"},
            # or "image_url": f"data:image/png;base64,{b64_image}"
        ],
    }],
)
```

## Inspecting, cancelling, compacting

```python
response = client.responses.retrieve(response_id="resp_...")
client.responses.cancel(response_id="resp_...")
client.responses.compact(response_id="resp_...")   # compress a long conversation
client.responses.delete(response_id="resp_...")
```

Supporting subresources:

```python
client.responses.input_items.list(response_id)     # paginated input items
client.responses.input_tokens.count(...)           # estimate input tokens without calling the model
```

## Structured outputs

`client.responses.parse(...)` behaves like `.create()` but takes a Pydantic model in `text_format`; the SDK converts it to a JSON schema and returns the parsed content:

```python
from typing import List
from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str

rsp = client.responses.parse(
    model="gpt-5.5",
    input="solve 8x + 31 = 2",
    text_format=MathResponse,
)

message = rsp.output[0]
assert message.type == "message"
text = message.content[0]
assert text.type == "output_text"
if not text.parsed:
    raise Exception("Could not parse response")
print(text.parsed.final_answer)
```

The same pattern works inside `client.responses.stream(..., text_format=MathResponse)` — streamed events carry partial/complete `parsed` payloads.

## Tools

Declare typed tools from Pydantic models:

```python
import openai
from pydantic import BaseModel

class Query(BaseModel):
    table_name: str
    conditions: List[dict]

with client.responses.stream(
    model="gpt-5.5",
    input="look up all my orders in november of last year",
    tools=[openai.pydantic_function_tool(Query)],
) as stream:
    for event in stream:
        ...  # function-call argument events accumulate; see 04-streaming-and-polling.md
```

For Chat Completions, strict function tools are required when using `.parse()`.

## Background responses

`background=True` starts the response and returns immediately; combine with `stream=True` to observe progress, then resume later:

```python
response_id = None

with client.responses.create(
    model="gpt-5.5",
    input="solve 8x + 31 = 2",
    background=True,
    stream=True,
) as stream:
    for event in stream:
        if event.type == "response.created":
            response_id = event.response.id
        if "output_text" in event.type:
            print(event.delta, end="", flush=True)
        if event.sequence_number == 10:
            break  # interrupt; continue later

# resume the stream from after a given sequence number
with client.responses.retrieve(
    response_id=response_id,
    stream=True,
    starting_after=10,
) as stream:
    for event in stream:
        if "output_text" in event.type:
            print(event.delta, end="", flush=True)
```

Async example: `examples/responses/background_async.py` in the SDK repo.

## Streaming

`client.responses.stream(...)` is a context manager yielding typed events (e.g. `response.output_text.delta`, `response.output_text.done`, `response.function_call_arguments.delta`, `response.completed`, `response.failed`). Helpers: `stream.get_final_response()` and `stream.until_done()`. Full event catalog in [04-streaming-and-polling.md](04-streaming-and-polling.md).

```python
with client.responses.stream(model="gpt-5.5", input="...") as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print(stream.get_final_response().output_text)
```

## Multi-agent (beta)

Multi-agent orchestration runs under the beta namespace and requires the `responses_multi_agent=v1` beta flag:

```python
client = OpenAI()

stream = client.beta.responses.create(
    model="gpt-5.6-sol",
    input=PROMPT,
    multi_agent={"enabled": True},
    stream=True,
    betas=["responses_multi_agent=v1"],
)
for event in stream:
    if event.type == "response.output_item.added":
        item_agents[event.output_index] = event.item.agent  # None for the coordinator
    elif event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
```

Items from subagents carry `item.agent.agent_name`; the coordinator's items have `agent=None`.

## WebSocket connection

`client.responses.connect()` opens a persistent WebSocket to the Responses API for multiple sequential responses over one socket — send `response.create` events and iterate incoming stream events:

```python
with client.responses.connect(
    extra_headers={"OpenAI-Beta": "responses_multi_agent=v1"},  # for beta features
) as connection:
    connection.send({
        "type": "response.create",
        "model": "gpt-5.5",
        input="Say hello!",
    })
    for event in connection:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
        if event.type == "response.completed":
            break
```

`connect()` options: `extra_query`, `extra_headers`, `websocket_connection_options`, `on_reconnecting` (callback receiving `ReconnectingEvent`), `max_retries=5`, `initial_delay=0.5`, `max_delay=8.0`, `max_queue_size=1048576`. The async client mirrors this with `await client.responses.connect(...)`.

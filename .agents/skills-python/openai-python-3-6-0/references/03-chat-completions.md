# openai-python 3.6.0 — Chat Completions API

Chat Completions (`client.chat.completions`) is the previous standard for text generation, supported indefinitely. The newer Responses API is preferred for new work; use Chat Completions when migrating existing code or when its shape fits better.

## Basic usage

```python
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-5.5",
    messages=[
        {"role": "developer", "content": "Talk like a pirate."},
        {"role": "user", "content": "How do I check if a Python object is an instance of a class?"},
    ],
)
print(completion.choices[0].message.content)
print(completion.usage)  # token usage, includes compute_units in 3.6.0
```

Message roles: `developer` (preferred standing instructions), `system`, `user`, `assistant`, `tool`. `content` can be a string or a list of typed content parts (text, image, file).

## Structured outputs with Pydantic

`client.chat.completions.parse(...)` wraps `.create()` and returns a `ParsedChatCompletion`. Passing a Pydantic model as `response_format` makes the SDK convert it to a JSON schema, enforce it server-side, and parse the result back into the model:

```python
from typing import List
from pydantic import BaseModel
from openai import OpenAI

class Step(BaseModel):
    explanation: str
    output: str

class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str

client = OpenAI()
completion = client.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,
)

message = completion.choices[0].message
if message.parsed:
    print(message.parsed.final_answer)
else:
    print(message.refusal)
```

Restrictions of `.parse()` versus `.create()`:

- `finish_reason == "length"` raises `LengthFinishReasonError`; `finish_reason == "content_filter"` raises `ContentFilterFinishReasonError`
- Only strict function tools may be passed (tool schema with `"strict": True`)

## Tool calling with Pydantic models

`openai.pydantic_function_tool(Model)` builds a strict function tool from a Pydantic model; `.parse()` then returns typed arguments:

```python
import openai
from enum import Enum
from typing import List, Union
from pydantic import BaseModel

class Table(str, Enum):
    orders = "orders"
    customers = "customers"

class Condition(BaseModel):
    column: str
    operator: str
    value: Union[str, int]

class Query(BaseModel):
    table_name: Table
    conditions: List[Condition]

completion = client.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Query the database using the query tool."},
        {"role": "user", "content": "look up all my orders in may of last year"},
    ],
    tools=[openai.pydantic_function_tool(Query)],
)

tool_call = (completion.choices[0].message.tool_calls or [])[0]
assert isinstance(tool_call.function.parsed_arguments, Query)
print(tool_call.function.parsed_arguments.table_name)
```

Plain dict tools work too, but then arguments come back as raw JSON in `tool_call.function.arguments` and must be parsed yourself.

## Refusals

When the model refuses, `message.content` is `None` and `message.refusal` carries the refusal text. Always check both before assuming content exists:

```python
msg = completion.choices[0].message
if msg.parsed is None and msg.refusal:
    print("Refused:", msg.refusal)
```

## Streaming

`.create(stream=True)` yields raw `ChatCompletionChunk` objects. The higher-level `client.chat.completions.stream(...)` context manager yields accumulated events (`content.delta`, `content.done`, `refusal.delta`, `tool_calls.function.arguments.delta`, `logprobs.*`, `chunk`) and supports the same Pydantic parsing helpers. It requires a `with` / `async with` block:

```python
with client.chat.completions.stream(
    model="gpt-4o",
    messages=[{"role": "user", "content": "count to 1000"}],
) as stream:
    for event in stream:
        if event.type == "content.delta":
            print(event.delta, end="", flush=True)
    completion = stream.get_final_completion()
```

Event types and stream methods are catalogued in [04-streaming-and-polling.md](04-streaming-and-polling.md).

## Vision

```python
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://.../image.jpg"}},
        ],
    }],
)
```

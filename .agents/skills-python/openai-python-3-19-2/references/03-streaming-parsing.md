# Streaming, Parsing, and Polling Helpers

## Raw streams

Pass `stream=True` to `.create()`; the result iterates SSE chunks (`ChatCompletionChunk` for chat, stream events for responses). You can `next()`/`await anext()` manually or `for`/`async for` to the end. In the Responses API, background/resumable streams support `starting_after=<sequence_number>` on `client.responses.retrieve(response_id=..., stream=True)` to resume.

## Structured outputs parsing

`client.chat.completions.parse()` wraps `.create()` and returns a `ParsedChatCompletion` (subclass of `ChatCompletion`):

```python
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[...],
    response_format=MathResponse,   # any Pydantic model; converted to a JSON schema automatically
)
message = completion.choices[0].message
if message.parsed:
    print(message.parsed.final_answer)
else:
    print(message.refusal)
```

Responses API: `client.responses.parse(..., text_format=YourModel)` (same for `.stream(..., text_format=...)` and async equivalents). Parsing rules: messages with `phase="final_answer"` are parsed; no-phase/null-phase messages keep legacy behavior and are also parsed; commentary and other explicit phases keep their original text with `parsed=None`. `response.output_parsed` returns the first parsed result or `None`; a refusal never falls back to commentary. Invalid JSON or schema-invalid text in an eligible message still raises a validation error. `output_text` keeps concatenating all output text including commentary — use `output_parsed` for the structured result and retain `output` when replaying messages so phases are preserved.

Auto-parsing function tool calls: with `.parse()`, tools built via `openai.pydantic_function_tool(Model)` (or manual schemas with `"strict": True`) yield `tool_call.function.parsed_arguments` as an instance of the model:

```python
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[...],
    tools=[openai.pydantic_function_tool(Query)],
)
tool_call = (completion.choices[0].message.tool_calls or [])[0]
print(tool_call.function.parsed_arguments.table_name)
```

Differences of `.parse()` from `.create()`: it raises `LengthFinishReasonError` / `ContentFilterFinishReasonError` for those finish reasons, and only strict function tools may be passed.

## Chat Completions streaming helper

`client.chat.completions.stream(...)` wraps `.create(stream=True)` with a granular event API and automatic accumulation. Unlike `.create(stream=True)`, it **requires a context manager**; the stream instance stays usable after the block.

```python
async with client.chat.completions.stream(model="gpt-4o-2024-08-06", messages=[...]) as stream:
    async for event in stream:
        if event.type == "content.delta":
            print(event.content, flush=True, end="")
```

Event types:

- `chunk` — every raw chunk; `chunk` + accumulated `snapshot`
- `content.delta` / `content.done` — `delta`/`content`, `snapshot`, `parsed` (if applicable); `done` may fire multiple times for multiple choices
- `refusal.delta` / `refusal.done` — refusal text accumulation
- `tool_calls.function.arguments.delta` / `.done` — `name`, `index`, raw `arguments`, `arguments_delta`, `parsed_arguments`
- `logprobs.content.delta` / `.done` and `logprobs.refusal.delta` / `.done`

Convenience methods: `stream.get_final_completion()` (accumulated `ParsedChatCompletion`; `message.parsed` set if you passed a class), `stream.until_done()`.

## Responses streaming helper

`client.responses.stream(...)` works the same way:

```python
with client.responses.stream(input="solve 8x + 31 = 2", model="gpt-4o-2024-08-06", text_format=MathResponse) as stream:
    for event in stream:
        if "output_text" in event.type:
            print(event)
    response = stream.get_final_response()
```

Common event types: `response.created`, `response.in_progress`, `response.output_item.added`/`.done`, `response.content_part.added`/`.done`, `response.output_text.delta`/`.done`, `response.refusal.delta`/`.done`, `response.function_call_arguments.delta`/`.done`, `response.completed`/`failed`/`incomplete`, plus tool-specific events (web search, file search, code interpreter, image gen, MCP). Each event carries `sequence_number`. `stream.get_final_response()` returns the accumulated (optionally parsed) response; `stream.until_done()` drains it.

## Assistant streaming (beta)

Subscribe by subclassing `AssistantEventHandler` and overriding `on_*` methods:

```python
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text: Text) -> None: ...
    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None: ...
    @override
    def on_tool_call_created(self, tool_call: ToolCall) -> None: ...
    @override
    def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall) -> None: ...
    @override
    def on_end(self) -> None: ...
    @override
    def on_exception(self, exception: Exception) -> None: ...
    @override
    def on_timeout(self) -> None: ...

with client.beta.threads.runs.stream(thread_id=..., assistant_id=..., event_handler=EventHandler()) as stream:
    stream.until_done()
```

Other handlers: `on_event` (raw), `on_run_step_created/delta/done`, `on_message_created/delta/done`, `on_text_done`, `on_image_file_done`, `on_tool_call_done`.

Three stream entry points:

- `client.beta.threads.runs.stream(...)` — existing run + populated thread
- `client.beta.threads.create_and_run_stream(...)` — add a message, start a run, stream
- `client.beta.threads.runs.submit_tool_outputs_stream(...)` — submit tool output, stream the continuation

You can also iterate raw events (`for event in stream:`) or just text deltas (`for text in stream.text_deltas:`). Context accessors: `current_event()`, `current_run()`, `current_message_snapshot()`, `current_run_step_snapshot()`. Final accumulators: `get_final_run()`, `get_final_run_steps()`, `get_final_messages()`.

## Polling helpers

For async server-side operations, `*_and_poll` variants block until a terminal state and return the resulting object. Polling cadence is tuned with `poll_interval_ms`.

```python
client.beta.threads.create_and_run_poll(...)
client.beta.threads.runs.create_and_poll(...)
client.beta.threads.runs.submit_tool_outputs_and_poll(...)
client.vector_stores.files.upload_and_poll(...)
client.vector_stores.files.create_and_poll(...)
client.vector_stores.file_batches.create_and_poll(...)
client.vector_stores.file_batches.upload_and_poll(...)
client.videos.create_and_poll(...)
```

Bare `poll(...)` variants also exist on vector-store files/batches and threads runs for polling an existing object.

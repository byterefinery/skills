# Streaming and Parsing Helpers (v3.60.0)

## Raw streams

`stream=True` on `.create()` returns an SSE iterator (sync iterator or async iterator in `AsyncOpenAI`). Chat Completions chunks may have empty `choices` — skip them. The Responses API streams typed events directly.

## `.stream()` helper (Chat Completions)

`client.chat.completions.stream(...)` wraps `.create(stream=True)` with a typed event API and accumulated snapshots. Unlike `.create(stream=True)`, it **requires a context manager**; the stream instance stays usable after the block.

```python
async with client.chat.completions.stream(model="gpt-4o-2024-08-06", messages=[...]) as stream:
    async for event in stream:
        if event.type == "content.delta":
            print(event.delta, flush=True, end="")
```

Event types (each has `snapshot` = accumulated state where noted):

| `event.type` | Fields |
|---|---|
| `"chunk"` | `chunk` (raw `ChatCompletionChunk`), `snapshot` |
| `"content.delta"` / `"content.done"` | `delta` / `content`, `snapshot`, `parsed` |
| `"refusal.delta"` / `"refusal.done"` | `delta` / `refusal`, `snapshot` |
| `"tool_calls.function.arguments.delta"` / `"...done"` | `name`, `index`, `arguments`, `parsed_arguments`, `arguments_delta` |
| `"logprobs.content.delta"` / `"...done"` | `content`, `snapshot` |
| `"logprobs.refusal.delta"` / `"...done"` | `refusal`, `snapshot` |

Methods: `.get_final_completion()` returns the accumulated `ParsedChatCompletion`; `.until_done()` waits for completion. `.stream()` supports the same parsing helpers as `.parse()`.

## Assistant streaming

`client.beta.threads.runs.stream()`, `client.beta.threads.create_and_run_stream()`, and `client.beta.threads.runs.submit_tool_outputs_stream()` — all context-managed.

- Iterate raw events (`event.event == "thread.message.delta"`), or iterate `stream.text_deltas`.
- Subclass `AssistantEventHandler` and override `on_text_created` / `on_text_delta`, `on_tool_call_created` / `on_tool_call_delta`, `on_message_*`, `on_run_step_*`, `on_image_file_done`, `on_end`, `on_timeout`, `on_exception` — pass via `event_handler=EventHandler()`.
- Context accessors inside handlers: `current_event()`, `current_run()`, `current_message_snapshot()`, `current_run_step_snapshot()`.
- Terminal collectors: `get_final_run()`, `get_final_run_steps()`, `get_final_messages()`.

## Structured outputs

### Chat Completions `.parse()`

`client.chat.completions.parse(..., response_format=Model)` converts the Pydantic model to a JSON schema, sends it, and parses the response into `Model` — `completion.choices[0].message.parsed` is the instance (or `None`; check `message.refusal`). Stricter than `.create()`: raises `LengthFinishReasonError` / `ContentFilterFinishReasonError` for those finish reasons and accepts only strict function tools. `openai.pydantic_function_tool(QueryModel)` auto-parses `tool_call.function.parsed_arguments` into the model.

### Responses API `.parse()`

`client.responses.parse(..., text_format=Model)` (same for `.stream()`):

- Messages with `phase="final_answer"` are parsed; messages with no/null phase also parse (legacy behavior). Commentary and other explicit phases keep raw text with `parsed=None`.
- `response.output_parsed` returns the first parsed result (or `None`); a refusal does not fall back to commentary. `output_text` still concatenates all output text including commentary.
- Invalid JSON or schema-invalid text in an eligible message still raises a validation error; phases are not inferred from text or model name.
- `parse_as=Model` selects the local output type when the schema changed mid-conversation (the request inherits its format from the previous turn); `parse_as=None` reads unparsed text.
- Formats can be updated inline in `input` via `{"type": "configuration_update", "text": {"format": ...}}`; `{"type": "text"}` switches back to plain text.

### Deferred typed Responses tools

`openai.pydantic_responses_function_tool(Model, defer_loading=True)` produces a flat Responses tool definition that retains Pydantic argument parsing in `responses.parse()` / `.stream()`; enable deferred loading alongside hosted tool search: `tools=[{"type": "tool_search"}, tool]`. `openai.pydantic_function_tool()` remains for Chat Completions and its Responses compatibility path.

## Polling helpers

`*_and_poll()` variants block until a terminal state; all accept `poll_interval_ms`:

```python
client.beta.threads.create_and_poll(...)
client.beta.threads.runs.create_and_poll(...)
client.beta.threads.runs.submit_tool_outputs_and_poll(...)
client.vector_stores.files.upload_and_poll(...)
client.vector_stores.files.create_and_poll(...)
client.vector_stores.file_batches.create_and_poll(...)
client.vector_stores.file_batches.upload_and_poll(...)
client.videos.create_and_poll(...)
```

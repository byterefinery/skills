# openai-python 3.6.0 — Streaming and Polling

## Server-Sent Events basics

Pass `stream=True` to `.create()` to get a SSE stream of raw event objects. Sync returns an iterator; async returns an async iterator (`await` on the call, then `async for`):

```python
stream = client.responses.create(model="gpt-5.5", input="...", stream=True)
for event in stream:
    print(event)
```

Raw stream events carry a `sequence_number` (used to resume background responses) and a `type` such as `response.output_text.delta`.

## Chat Completions stream helper

`client.chat.completions.stream(...)` wraps `.create(stream=True)` with accumulated snapshots and typed events. It **requires** a context manager (the stream is closed on exit, but the object remains usable afterwards):

```python
with client.chat.completions.stream(model="gpt-4o", messages=[...]) as stream:
    for event in stream:
        if event.type == "content.delta":
            print(event.content, end="", flush=True)
```

Event types:

| Event type | Meaning |
|---|---|
| `chunk` | Every raw chunk; `event.chunk` is the raw `ChatCompletionChunk`, `event.snapshot` the accumulated state |
| `content.delta` | New content; `event.delta`, `event.snapshot`, `event.parsed` (with Pydantic) |
| `content.done` | Content complete (may fire per choice); `event.content`, `event.parsed` |
| `refusal.delta` / `refusal.done` | Refusal content accumulated / complete |
| `tool_calls.function.arguments.delta` / `...done` | Tool-call args accumulating; `event.parsed_arguments` is the typed model when using `openai.pydantic_function_tool` |
| `logprobs.content.delta` / `...done` | Content log probabilities |
| `logprobs.refusal.delta` / `...done` | Refusal log probabilities |

Stream methods:

- `stream.get_final_completion()` — the accumulated `ParsedChatCompletion`
- `stream.until_done()` — consume the stream to completion (useful with `event_handler`-style code or to wait)

## Responses stream helper

`client.responses.stream(...)` is the same idea for the Responses API:

```python
with client.responses.stream(model="gpt-5.5", input="...", text_format=MathResponse) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    response = stream.get_final_response()
```

Stream methods: `stream.get_final_response()` (accumulated `ParsedResponse`, respects `text_format`), `stream.until_done()`, `stream.close()`.

Frequently encountered event types (all `response.*`):

| Event type | Meaning |
|---|---|
| `response.created` / `response.in_progress` / `response.completed` / `response.incomplete` / `response.failed` | Lifecycle; `completed`/`incomplete`/`failed` carry the full response |
| `response.output_text.delta` / `response.output_text.done` | Output text deltas; `event.delta` / `event.text` |
| `response.refusal.delta` / `response.refusal.done` | Refusal text |
| `response.audio.delta` / `response.audio.done` | Raw audio output |
| `response.audio_transcript.delta` / `...done` | Transcript of the audio |
| `response.reasoning_summary_text.delta` / `...done` | Reasoning summary parts |
| `response.function_call_arguments.delta` / `...done` | Tool-call arguments accumulating |
| `response.output_item.added` / `response.output_item.done` | Output items (messages, tool calls, `agent`-tagged items in multi-agent) |
| `response.content_part.added` / `response.content_part.done` | Content parts within an item |
| `response.file_search_call.*`, `response.web_search_call.*`, `response.mcp_call.*`, `response.shell_call.*`, `response.image_gen_call.*`, `response.code_interpreter_call.*` | Built-in and hosted tool call progress (`in_progress`, `searching`/`generating`/`interpreting`, `completed`, `failed`) |
| `response.error` | Error event inside the stream (see realtime gotcha: not raised) |

## Polling helpers

Actions that complete asynchronously (runs, uploads, batch jobs, videos) have `*_and_poll` variants that poll until a terminal state and return the final object:

```python
client.beta.threads.create_and_poll(...)
client.beta.threads.runs.create_and_poll(...)
client.beta.threads.runs.submit_tool_outputs_and_poll(...)
client.beta.vector_stores.files.upload_and_poll(...)
client.beta.vector_stores.files.create_and_poll(...)
client.beta.vector_stores.file_batches.create_and_poll(...)
client.beta.vector_stores.file_batches.upload_and_poll(...)
client.videos.create_and_poll(...)
```

Polling frequency is configurable on every method via `poll_interval_ms` (milliseconds between status checks).

## Raw responses and headers

Prefix any call with `.with_raw_response.` to get the HTTP layer object plus the parsed body:

```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.with_raw_response.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say this is a test"}],
)
print(response.headers.get("X-My-Header"))
completion = response.parse()  # the object .create() would have returned
```

`with_raw_response` returns a `LegacyAPIResponse` (eagerly reads the body; slated to change in the next major version — sync `content`/`text` become methods, async methods become async).

For lazy body access, use `.with_streaming_response.` — a context manager that only reads the body when you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()`, or `.parse()`:

```python
with client.chat.completions.with_streaming_response.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say hi"}],
) as response:
    print(response.headers.get("X-My-Header"))
    for line in response.iter_lines():
        print(line)
```

The context manager is required so the response is reliably closed. With a native HTTPX2 client, `response.http_response` / `response.http_request` are `httpx2.Response` / `httpx2.Request`.

## Undocumented endpoints, params, and fields

The SDK is typed for the documented API, but can reach beyond it:

- **Undocumented endpoints** — use the HTTP verbs directly; client options (retries, headers) still apply:
  ```python
  import httpx2
  response = client.post("/foo", cast_to=httpx2.Response, body={"my_param": True})
  print(response.headers.get("x-foo"))
  ```
- **Undocumented request params** — pass `extra_query`, `extra_body`, or `extra_headers` request options.
- **Undocumented response fields** — attribute access on the model (`response.unknown_prop`) or the full dict via `response.model_extra`.

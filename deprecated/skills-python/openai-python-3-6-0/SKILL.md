---
name: openai-python-3-6-0
description: >
  Official OpenAI Python SDK (openai 3.6.0) for calling the OpenAI REST API
  from Python 3.10+. Use when writing or debugging Python code that calls
  OpenAI models or APIs. Covers the Responses API (primary) and Chat
  Completions API, sync and async clients, SSE streaming, structured
  outputs with Pydantic, tool calling, background responses, pagination,
  retries and timeouts, the error hierarchy, webhook verification, workload
  identity and mTLS auth, the Realtime API, Azure OpenAI, and the Amazon
  Bedrock provider.
license: Apache-2.0
compatibility: Python 3.10+; pip install openai; optional extras openai[aiohttp], openai[realtime], openai[bedrock], openai[datalib], openai[voice_helpers]
metadata:
  tags:
    - python
    - ai
    - llm
    - openai
    - api-client
---

# openai-python 3.6.0

## Overview

`openai` 3.6.0 is the official Python client for the OpenAI REST API, generated from OpenAI's OpenAPI specification. It provides typed request params (TypedDicts), typed responses (Pydantic models), sync (`OpenAI`) and async (`AsyncOpenAI`) clients, and streaming or non-streaming calls. The HTTP layer is HTTPX2 (the `httpx2` package, **not** `httpx`).

- **Responses API is primary** — `client.responses` is the current standard for text generation, tools, and background work. Chat Completions (`client.chat.completions`) is the previous standard, supported indefinitely.
- Sync and async clients are functionally identical; async is `AsyncOpenAI` plus `await`.
- List endpoints auto-paginate; errors form a typed hierarchy rooted at `openai.APIError`.
- Other resources: `audio` (transcription/translation/speech), `images`, `embeddings`, `files`, `batches`, `fine_tuning`, `vector_stores`, `conversations`, `realtime`, `webhooks`, `uploads`, `models`, `moderations`, `videos`, `evals`, `admin`.

## Installation

```sh
pip install openai
# optional extras
pip install 'openai[aiohttp]'    # aiohttp transport for AsyncOpenAI
pip install 'openai[realtime]'   # websockets for the Realtime API
pip install 'openai[bedrock]'    # botocore for the Amazon Bedrock provider
```

## Usage

### Client setup

```python
from openai import OpenAI, AsyncOpenAI

client = OpenAI()  # reads OPENAI_API_KEY from the environment
```

The constructor infers `api_key`, `admin_api_key`, `organization`, `project`, and `webhook_secret` from `OPENAI_API_KEY`, `OPENAI_ADMIN_KEY`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`, and `OPENAI_WEBHOOK_SECRET`. All options, per-request overrides via `with_options()`, and the module-level client are in [01-client-configuration](references/01-client-configuration.md).

### Responses API (primary)

```python
response = client.responses.create(
    model="gpt-5.5",
    input="How do I check if a Python object is an instance of a class?",
)
print(response.output_text)
```

### Chat Completions API (previous standard)

```python
completion = client.chat.completions.create(
    model="gpt-5.5",
    messages=[
        {"role": "developer", "content": "Talk like a pirate."},
        {"role": "user", "content": "How do I check if a Python object is an instance of a class?"},
    ],
)
print(completion.choices[0].message.content)
```

### Async

```python
async with AsyncOpenAI() as client:
    response = await client.responses.create(model="gpt-5.5", input="...")
```

### Streaming

```python
with client.responses.stream(model="gpt-5.5", input="...") as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
```

`.stream()` helpers are context managers that yield accumulated events; raw SSE chunks come from `.create(..., stream=True)`. Event types, `.get_final_response()`, `.until_done()`, and polling helpers are in [04-streaming-and-polling](references/04-streaming-and-polling.md).

### Structured outputs and tools

```python
import openai
from pydantic import BaseModel

class MathResponse(BaseModel):
    final_answer: str

rsp = client.responses.parse(
    model="gpt-5.5",
    input="solve 8x + 31 = 2",
    text_format=MathResponse,
)
```

`client.responses.parse(text_format=Model)` and `client.chat.completions.parse(response_format=Model)` convert a Pydantic model to a JSON schema, send it to the API, and return the parsed object. `openai.pydantic_function_tool(Model)` declares typed tools. Full patterns are in [02-responses-api](references/02-responses-api.md) and [03-chat-completions](references/03-chat-completions.md).

### Error handling

```python
import openai

try:
    client.responses.create(model="gpt-5.5", input="...")
except openai.APIConnectionError:
    ...  # network failure, no response received
except openai.RateLimitError:
    ...  # 429
except openai.APIStatusError as e:
    print(e.status_code, e.response, e.request_id)
```

Connection errors, 408, 409, 429, and >=500 are retried twice by default with exponential backoff. The full error hierarchy, retries, timeouts, and pagination are in [06-errors-retries-pagination](references/06-errors-retries-pagination.md).

## Gotchas

- **HTTP layer is HTTPX2, not httpx** — `pip install openai` no longer installs `httpx`. Custom clients, transports, and mocks use `DefaultHttpx2Client()`, `httpx2.Timeout`, `httpx2.MockTransport`, etc. The default TLS trust store is now the OS store, not certifi; minimal containers may need `SSL_CERT_FILE` or an explicit `ssl.SSLContext`.
- **`None` means "omit" for request params** — `None` (or `omit()` / `NOT_GIVEN`) omits an optional field. In responses, `None` may be JSON `null` or a missing key; distinguish with `response.model_fields_set`.
- **`.stream()` helpers require a context manager** — `client.responses.stream(...)` and `client.chat.completions.stream(...)` must be used inside `with` / `async with` or the response leaks.
- **`chat.completions.parse()` is stricter than `.create()`** — it raises `LengthFinishReasonError` / `ContentFilterFinishReasonError` when the finish reason is `length` / `content_filter`, and accepts only strict function tools.
- **Realtime `error` events are not raised** — the WebSocket stays open and usable after an error event; check `event.type == "error"` yourself.
- **Webhook bodies must be raw JSON strings** — `client.webhooks.unwrap(body, headers)` parses the JSON itself; pass the unparsed body, not a dict.
- **`_request_id` is public; other `_`-prefixed members are private** — for failed requests the ID lives on the exception: catch `openai.APIStatusError` and read `exc.request_id`.
- **Defaults are generous** — timeout is 10 minutes, retries default to 2; set `timeout=` / `max_retries=` on the client or per-request via `client.with_options(...)`.
- **Azure API shape differs from the core API** — with `AzureOpenAI`, static response/param types are not always correct, and `model` is a deployment name.
- **Multi-agent Responses are beta** — call `client.beta.responses` with `betas=["responses_multi_agent=v1"]` (or `extra_headers={"OpenAI-Beta": "responses_multi_agent=v1"}` on the WebSocket).
- **Workload identity is captured at construction** — `api_key` and `workload_identity` are mutually exclusive; build a new client to change the identity.
- **mTLS clients are transport-wide** — a certificate-bearing HTTP client belongs to one origin; do not reuse it via `with_options()` with a different `base_url`.

## References

- [01-client-configuration](references/01-client-configuration.md) — env vars, client options, with_options, module-level client, HTTPX2 and custom clients, resource management
- [02-responses-api](references/02-responses-api.md) — Responses API: create, parse, stream, background + resume, compact, multi-agent, WebSocket
- [03-chat-completions](references/03-chat-completions.md) — Chat Completions: messages, structured outputs, tools, refusals
- [04-streaming-and-polling](references/04-streaming-and-polling.md) — SSE streaming, stream helper event types, polling `_and_poll`, raw and streaming responses, undocumented access
- [05-authentication-cloud](references/05-authentication-cloud.md) — workload identity, X.509/mTLS, webhook verification, Azure OpenAI, Bedrock provider
- [06-errors-retries-pagination](references/06-errors-retries-pagination.md) — error hierarchy, retries, timeouts, request IDs, pagination, file uploads
- [07-realtime](references/07-realtime.md) — Realtime API over WebSocket: events, audio, error handling

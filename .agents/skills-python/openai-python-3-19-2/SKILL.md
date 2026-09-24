---
name: openai-python-3-19-2
description: >
  Official OpenAI Python API library version 3.19.2 — synchronous OpenAI and
  asynchronous AsyncOpenAI clients for the OpenAI REST API, generated from the
  OpenAPI spec and built on HTTPX2 with typed requests and Pydantic responses.
  Use when the user works with OpenAI APIs from Python — Responses API, Chat
  Completions, embeddings, audio, images, files, fine-tuning, vector stores,
  batches, webhooks, Realtime, Live, or WebSocket responses — or needs
  streaming, structured-output parsing, and polling helpers, client
  configuration (keys, timeouts, retries, proxies), or Azure OpenAI / Amazon
  Bedrock provider integration.
license: Apache-2.0
compatibility: >
  Python 3.10–3.14. Optional extras — openai[aiohttp] for the async aiohttp
  transport, openai[realtime] (websockets) for Realtime/Live/WebSocket APIs,
  openai[voice_helpers] (sounddevice, numpy) for Microphone/LocalAudioPlayer,
  openai[bedrock] (botocore) for SigV4 Bedrock auth, openai[datalib]
  (numpy, pandas). Network access to the OpenAI, Azure, or Bedrock endpoint.
metadata:
  tags:
    - python
    - openai
    - llm
    - sdk
---

# openai-python 3.19.2

## Overview

`openai` 3.19.2 is the official OpenAI Python client, generated from the OpenAI OpenAPI specification. The synchronous `OpenAI` and asynchronous `AsyncOpenAI` clients cover the full REST API; `AzureOpenAI` targets Azure OpenAI and a legacy module-level client (`openai.chat...`) also works.

Key facts:

- **Two text APIs** — `client.responses` (Responses API, the primary API) and `client.chat.completions` (Chat Completions, the previous standard, supported indefinitely).
- **Typed end to end** — request params are TypedDicts (pass plain dicts), responses are Pydantic models with `.to_dict()`, `.to_json()`, `.model_fields_set`, `.model_extra`.
- **HTTPX2 transport** — the default HTTP layer is HTTPX2 (installed automatically; the previous `httpx` package is **not** installed by the SDK).
- **Helpers** — `.stream()` for typed streaming events, `.parse()` for structured outputs, `*_and_poll()` for async operations, auto-paginating iterators for list endpoints.

Install: `pip install openai`. Optional extras:

| Extra | Adds |
|---|---|
| `openai[aiohttp]` | `DefaultAioHttpClient()` — aiohttp transport for async concurrency |
| `openai[realtime]` | `websockets` — Realtime API, Live API, WebSocket responses |
| `openai[voice_helpers]` | `sounddevice`, `numpy` — `Microphone` / `LocalAudioPlayer` helpers |
| `openai[bedrock]` | `botocore` — SigV4 authentication for the Bedrock provider |
| `openai[datalib]` | `numpy`, `pandas` |

Requires Python 3.10+. Check the installed version at runtime with `openai.__version__`.

## Usage

### Quickstart — Responses API (primary)

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from the environment

response = client.responses.create(
    model="gpt-5.5",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)
print(response.output_text)
```

### Chat Completions (previous standard)

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

Import `AsyncOpenAI` and `await` each call; everything else is identical. Use `async with` or `await client.close()` before the event loop shuts down (garbage collection cannot reliably await async cleanup).

```python
import asyncio
from openai import AsyncOpenAI

async def main() -> None:
    async with AsyncOpenAI() as client:
        response = await client.responses.create(model="gpt-5.5", input="Say this is a test.")
        print(response.output_text)

asyncio.run(main())
```

### Module-level client (legacy)

`openai.api_key`, `openai.base_url`, and `openai.chat.completions.create(...)` etc. still work; the client is cached from module state and environment variables. Prefer explicit `OpenAI()` instances in new code.

### Streaming

Raw: pass `stream=True` to `.create()` and iterate SSE chunks (skip empty `chunk.choices`). The richer helper `.stream()` wraps the stream in a context manager (required) and yields typed events with `get_final_response()` / `get_final_completion()` / `until_done()` — see [03-streaming-parsing](references/03-streaming-parsing.md).

### Structured outputs

```python
from pydantic import BaseModel
import openai

class MathResponse(BaseModel):
    final_answer: str

# Chat Completions
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[...],
    response_format=MathResponse,
)
print(completion.choices[0].message.parsed)  # MathResponse instance, or None

# Responses API
response = client.responses.parse(model="gpt-4o-2024-08-06", input="solve 8x + 31 = 2", text_format=MathResponse)
print(response.output_parsed)
```

Pair `openai.pydantic_function_tool(QueryModel)` with `.parse()` to get `tool_call.function.parsed_arguments` as a model instance (requires strict tools).

### Tool calling (function tools)

Pass `tools=[{"type": "function", "name": ..., "parameters": {...}}]` to `chat.completions.create()` or `responses.create()`; read `message.tool_calls`, execute locally, then send tool-result messages back. The same TypedDict param shapes are documented per endpoint in [04-api-surface](references/04-api-surface.md).

### File uploads

File params accept `bytes`, a file-like object, a `Path` (read automatically), or a tuple `(filename, contents, media_type)`. For in-memory file-likes (e.g., `io.BytesIO`), include a filename — pass the tuple form or set `.name` — because the API needs the extension to detect the format.

### Pagination

List endpoints return auto-paginating iterators: `for job in client.fine_tuning.jobs.list(limit=20):` fetches pages as needed. For manual control use `.has_next_page()`, `.next_page_info()`, `.get_next_page()`, or just read `.data` and `.after`.

### Webhooks

```python
# body must be the raw JSON string from the request — do not parse it first
event = client.webhooks.unwrap(request.get_data(as_text=True), request.headers)
```

`.unwrap()` verifies the signature (secret from `OPENAI_WEBHOOK_SECRET` by default) and returns the typed event; `.verify_signature(body, headers)` verifies only.

### Errors

All errors inherit `openai.APIError`. Connection failures raise `openai.APIConnectionError`; non-2xx raises `openai.APIStatusError` (with `.status_code` and `.response`), including `BadRequestError` (400), `AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `UnprocessableEntityError` (422), `RateLimitError` (429), `InternalServerError` (>=500), `APITimeoutError`, `InvalidWebhookSignatureError`, `LengthFinishReasonError`, `ContentFilterFinishReasonError`. Catch SDK exceptions, not raw HTTPX ones (original exception is in `e.__cause__`). The original request ID is `exc.request_id` on errors and the public `response._request_id` property on successes.

### Retries and timeouts

Connection errors, 408, 409, 429, and >=500 are retried automatically (default 2 retries, exponential backoff); only replayable bodies are resent. Configure with `max_retries` (non-negative integer; `0` disables) and `timeout` (default 10 minutes; accepts a float or `httpx2.Timeout`) at client level or per request via `client.with_options(max_retries=5, timeout=5.0)`.

## Gotchas

- **The HTTP layer is HTTPX2, not httpx** — the SDK no longer installs `httpx`; if your app imports it directly, declare it yourself. Custom clients, transports, timeouts, mocks, and event hooks must use `httpx2.*` objects (`DefaultHttpx2Client` / `DefaultAsyncHttpx2Client`). TLS now uses the **operating-system trust store**, not `certifi` — minimal containers and TLS-inspecting proxies may break verification; fix with `SSL_CERT_FILE`/`SSL_CERT_DIR` or an `ssl.SSLContext` passed to `verify`. Full details in [02-http-httpx2](references/02-http-httpx2.md).
- **Responses API is primary; Chat Completions is the previous standard** — both work, but new code should prefer `client.responses` (richer output, conversation state, structured `text_format`).
- **`None` means both `null` and missing** — distinguish with `response.model_fields_set` (field absent vs. field present but null).
- **`_request_id` is public** — unlike other underscore-prefixed members, which are private.
- **Webhook bodies must be raw JSON strings** — parsing first invalidates signature verification.
- **In-memory file uploads need a filename** — `io.BytesIO` alone may arrive as generic `upload`; pass the `(filename, contents, media_type)` tuple.
- **`.parse()` is stricter than `.create()`** — it raises `LengthFinishReasonError` / `ContentFilterFinishReasonError` for those finish reasons and only accepts strict function tools.
- **`.stream()` requires a context manager** (`.create(stream=True)` does not); the stream instance remains usable after the block.
- **Stream consumption is not auto-retried** — read timeouts mid-stream raise `APITimeoutError` because replaying could duplicate delivered output.
- **Realtime errors are events, not exceptions** — the SDK does not raise on `event.type == "error"`; the connection stays open, handle it yourself.
- **`provider` is exclusive** — passing `provider=bedrock(...)` alongside `api_key`, `base_url`, `workload_identity`, or `admin_api_key` raises; Bedrock bearer token env `AWS_BEARER_TOKEN_BEDROCK` shadows the AWS credential chain unless `api_key=None` forces SigV4.
- **Azure static types can be wrong** — the Azure API shape differs from core; `AzureOpenAI` works but response/param types are not always accurate.
- **X.509 workload identity re-routes** — with `x509_workload_identity(...)`, the client defaults to `https://mtls.api.openai.com/v1` unless `base_url`/`OPENAI_BASE_URL` is set.
- **`max_retries` must be a non-negative integer** — use a large value (e.g., 1000) for a bigger budget; other values raise before the request is sent.
- **Long-running work uses polling helpers** — `client.videos.create_and_poll()`, `client.vector_stores.files.upload_and_poll()`, `client.beta.threads.runs.create_and_poll()` block until a terminal state; pass `poll_interval_ms` to tune the cadence.

## References

- [01-client-configuration](references/01-client-configuration.md) — client constructor options, environment variables, `with_options`, data residency, timeouts/retries, module-level client, resource lifecycle, logging
- [02-http-httpx2](references/02-http-httpx2.md) — HTTPX2 migration (TLS trust, custom clients, transports, mocks, legacy escape hatch), raw and streaming responses, mTLS and X.509, undocumented requests
- [03-streaming-parsing](references/03-streaming-parsing.md) — raw streams, `.stream()` helpers and event types, structured outputs and `pydantic_function_tool`, Assistant streaming, polling helpers
- [04-api-surface](references/04-api-surface.md) — full resource map (responses, chat, audio, images, files, fine-tuning, vector stores, batches, admin, beta, ...), type imports, pagination, response objects
- [05-authentication-providers](references/05-authentication-providers.md) — API keys, workload identity (K8s/Azure/GCP/X.509), Azure OpenAI client, Amazon Bedrock provider
- [06-realtime-live-websockets](references/06-realtime-live-websockets.md) — Realtime API, Live API, Responses WebSocket, audio helpers (`Microphone`, `LocalAudioPlayer`)

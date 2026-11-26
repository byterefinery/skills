# Client Configuration

## Constructor options

All options for `OpenAI(...)` (keyword-only; `AsyncOpenAI` mirrors them):

| Option | Default | Notes |
|---|---|---|
| `api_key` | `OPENAI_API_KEY` env | `str` or a `Callable[[], str]` refresh callback; mutually exclusive with `workload_identity` |
| `admin_api_key` | `OPENAI_ADMIN_KEY` env | for admin endpoints |
| `workload_identity` | — | dict or `x509_workload_identity(...)`; see 05-authentication-providers |
| `organization` | `OPENAI_ORG_ID` env | |
| `project` | `OPENAI_PROJECT_ID` env | |
| `webhook_secret` | `OPENAI_WEBHOOK_SECRET` env | used by `client.webhooks` |
| `provider` | — | e.g. `bedrock(...)`; exclusive with `api_key`/`base_url`/`workload_identity`/`admin_api_key` |
| `base_url` | `OPENAI_BASE_URL` env, then `https://api.openai.com/v1` | string or `httpx2.URL` |
| `data_residency` | — | `"global"`, `"us"`, `"eu"`, `"ae"`; selects a fixed regional endpoint; cannot combine with `base_url`, `websocket_base_url`, or `provider` |
| `websocket_base_url` | derived from HTTP base | for Realtime/Live/Responses WebSockets |
| `timeout` | 600s read, 5s connect | float or `httpx2.Timeout`; `None` disables |
| `max_retries` | 2 | non-negative integer only |
| `default_headers` / `default_query` | — | merged into every request |
| `http_client` | SDK default | `httpx2.Client`, `DefaultHttpx2Client`, or `DefaultAioHttpClient` (async) |
| `_strict_response_validation` | `False` | raises `APIResponseValidationError` on schema mismatch (unstable API) |
| `_enforce_credentials` | `True` | |

## Environment variables

`OPENAI_API_KEY`, `OPENAI_ADMIN_KEY`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`, `OPENAI_BASE_URL`, `OPENAI_WEBHOOK_SECRET`, `OPENAI_LOG`, and for Bedrock `AWS_BEDROCK_BASE_URL`, `AWS_BEARER_TOKEN_BEDROCK`, `AWS_REGION`/`AWS_DEFAULT_REGION`, plus the normal AWS profile machinery.

## Per-request overrides

`client.with_options(...)` returns a new client with the given options overridden — `max_retries`, `timeout`, `http_client`, `organization`, `project`, headers, etc.:

```python
client.with_options(max_retries=5).chat.completions.create(...)
client.with_options(timeout=5.0).responses.create(...)
```

The original client is unchanged. Do not pass a certificate-bearing (mTLS) client through `with_options()` with a different `base_url`.

## Timeouts and retries

Defaults (from `openai._constants`): timeout 600s (connect 5s), 2 retries, retry delay starting at 0.5s up to 8s (honoring `retry-after` up to 120s), connection limits 1000 / 100 keepalive.

Retried conditions: connection errors, 408 Request Timeout, 409 Conflict, 429 Rate Limit, >=500. A request is retried only when its body can be safely resent. On timeout an `APITimeoutError` is raised; timed-out requests are retried like any other retryable request.

```python
import httpx2
client = OpenAI(timeout=httpx2.Timeout(60.0, read=5.0, write=10.0, connect=2.0))
```

## Module-level (legacy) client

```python
import openai
openai.api_key = "..."                      # or OPENAI_API_KEY env
openai.base_url = "https://..."             # all client options settable the same way
openai.chat.completions.create(model="gpt-5.6", messages=[...])
```

The module selects and caches a client from module globals and environment; `openai.api_type = "azure"` or `"amazon-bedrock"` routes to the respective client (also via `OPENAI_API_TYPE`). It is stateful and global — avoid it in new code where per-request behavior matters.

## Managing HTTP resources

The library closes underlying HTTP connections when the client is garbage collected, but close explicitly for predictable behavior:

```python
with OpenAI() as client:
    ...
# HTTP client is now closed
```

For `AsyncOpenAI`, use `async with` or `await client.close()` before shutting down the event loop.

## Logging

Standard-library `logging` under the `openai` logger. Set `OPENAI_LOG=info` (or `debug`, `warning`, `error`, `critical`) to configure it; HTTP transport loggers are configured separately.

## Undocumented endpoints, params, and properties

- **Endpoints** — `client.get("/foo")`, `client.post("/foo", cast_to=..., body={...})` and other HTTP verbs; client options like retries are respected.
- **Params** — `extra_query=...`, `extra_body=...`, `extra_headers=...` request options.
- **Response properties** — access `response.unknown_prop` directly, or all extras via `response.model_extra` (Pydantic).

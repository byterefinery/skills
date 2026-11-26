# Client Configuration (v3.60.0)

## Constructor options

- `api_key` — defaults to the `OPENAI_API_KEY` environment variable
- `base_url` — defaults to the `OPENAI_BASE_URL` environment variable; `https://mtls.api.openai.com/v1` when X.509 workload identity is used
- `provider` — `bedrock(...)` or `vertex(...)` from `openai.providers`; configures authentication and the base URL itself
- `workload_identity` — dict with `identity_provider_id`, `service_account_id`, `provider` (see [05-authentication-providers](05-authentication-providers.md))
- `http_client` — `DefaultHttpx2Client` / `DefaultAsyncHttpx2Client` / `DefaultAioHttpClient` (see [02-http-httpx2](02-http-httpx2.md))
- `max_retries` — non-negative integer, default 2
- `timeout` — float (default 10 minutes) or `httpx2.Timeout`

`data_residency` selects an OpenAI regional endpoint and **cannot** be combined with `base_url`, `websocket_base_url`, or `provider`.

## Per-request overrides

`client.with_options(...)` returns a scoped client: `client.with_options(max_retries=5, timeout=5.0, http_client=DefaultHttpx2Client(...))`. Request options apply to every subsequent call on that scoped client.

## Environment variables (SDK-level)

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | API key |
| `OPENAI_BASE_URL` | API root override |
| `OPENAI_LOG` | `info`, `debug`, `warning`, `error`, or `critical`; configures the `openai` logger only — configure HTTP transport loggers separately with Python logging |
| `OPENAI_WEBHOOK_SECRET` | default signing secret for `client.webhooks.unwrap()` / `.verify_signature()` |
| `OPENAI_API_TYPE` | legacy module client provider selector (e.g., `amazon-bedrock`) |
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_AD_TOKEN` | `AzureOpenAI` credentials |
| `OPENAI_API_VERSION` | `AzureOpenAI` API version |
| `AWS_REGION`, `AWS_DEFAULT_REGION`, `AWS_PROFILE`, `AWS_BEDROCK_BASE_URL`, `AWS_BEARER_TOKEN_BEDROCK` | Bedrock provider |
| `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` | Vertex provider |

## Timeouts and retries

- Default timeout is 10 minutes; a timeout raises `APITimeoutError` and, like other retryable failures, is retried by default.
- Retryable: connection errors, 408, 409, 429, >=500 — only when the request body can be safely resent.
- `max_retries` must be a non-negative integer; `0` disables retries; use a large value (e.g., 1000) for a bigger budget.
- Application exceptions raised by custom transports or hooks propagate unchanged, including task-executor cancellation signals.
- Stream consumption is never auto-retried (replay could duplicate delivered output).

## Module-level client (legacy)

`openai.api_key`, `openai.base_url`, `openai.chat.completions.create(...)` and friends build a cached module-level client from module state and environment variables. The Bedrock module client also supports `openai.api_type = "amazon-bedrock"` or `OPENAI_API_TYPE=amazon-bedrock`. See `examples/module_client.py`.

## Raw and undocumented responses

- `.with_raw_response.<method>()` returns a `LegacyAPIResponse` — a legacy class that changes slightly in the next major version (sync `content`/`text` become methods; async methods become async). `response.parse()` yields the typed object.
- `.with_streaming_response.<method>()` returns a context-manager response that reads lazily via `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()`, `.parse()` (async in the async client). The context manager is required so the response is reliably closed.
- Undocumented endpoints: `client.get(...)`, `client.post(..., cast_to=httpx2.Response, body={...})` — client options such as retries are respected.
- Undocumented request params: `extra_query`, `extra_body`, `extra_headers` request options.
- Undocumented response properties: `response.unknown_prop` or the whole `response.model_extra` dict.

## Resource lifecycle

- Sync: `with OpenAI() as client:` or `client.close()`. Connections close on garbage collection by default.
- Async: `async with AsyncOpenAI() as client:` or `await client.close()` before shutting down the event loop — GC cannot reliably await async cleanup.

## Versioning notes

The package follows SemVer with exceptions: static-type-only changes, internal changes, and low-impact changes may ship in minor versions. Minimum supported Python is 3.10 (raised via minor releases, documented in `PYTHON_VERSION_POLICY.md`). Runtime version: `openai.__version__`.

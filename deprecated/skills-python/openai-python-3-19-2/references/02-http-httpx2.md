# HTTP Layer — HTTPX2, Raw Responses, mTLS

Since this SDK line the default HTTP layer is **HTTPX2** (https://httpx2.pydantic.dev/), installed automatically with `openai`. The previous `httpx` package is **not** installed. If your application imported `httpx` only because an earlier SDK pulled it in transitively, add your own `httpx` dependency or migrate those imports to `httpx2`.

## Default client

Constructing `OpenAI`/`AsyncOpenAI` without `http_client` uses an SDK-owned HTTPX2 client; API calls, parsed models, streaming, auth, retries, and numeric timeouts are unchanged.

## TLS trust store change

HTTPX2 verifies certificates against the **operating-system trust store**, not the `certifi` bundle (the SDK no longer installs `certifi`). This can break:

- minimal container images without system CA certificates,
- environments using corporate TLS-inspecting proxies,
- deployments that relied on a custom/modified `certifi` bundle.

Fixes: install CA certificates into the OS trust store, or:

```sh
export SSL_CERT_FILE=/path/to/ca-bundle.pem     # or SSL_CERT_DIR=/path/to/ca-directory
```

These are honored when `trust_env=True` (the default). For explicit control, pass an `ssl.SSLContext` through `verify`:

```python
import ssl
from openai import OpenAI, DefaultHttpx2Client

ssl_context = ssl.create_default_context(cafile="/path/to/ca-bundle.pem")
client = OpenAI(http_client=DefaultHttpx2Client(verify=ssl_context))
```

`DefaultAsyncHttpx2Client(verify=ssl_context)` is the async equivalent; the aiohttp transport uses the same HTTPX2 TLS settings.

## Custom clients and configuration objects

The SDK provides helpers that preserve its recommended timeout, connection-pool, and redirect defaults: `DefaultHttpx2Client` (sync) and `DefaultAsyncHttpx2Client` (async). Directly constructed `httpx2.Client` / `httpx2.AsyncClient` instances also work (their own HTTPX2 defaults then apply). The older names `DefaultHttpxClient` / `DefaultAsyncHttpxClient` still work but construct HTTPX2 clients — prefer the `Httpx2` names.

Object mapping for migration:

| Previous (`httpx`) | HTTPX2 |
|---|---|
| `httpx.Client` | `httpx2.Client` |
| `httpx.AsyncClient` | `httpx2.AsyncClient` |
| `httpx.Timeout` | `httpx2.Timeout` |
| `httpx.URL` | `httpx2.URL` |
| `httpx.Limits` | `httpx2.Limits` |
| `httpx.HTTPTransport` | `httpx2.HTTPTransport` |
| `httpx.AsyncHTTPTransport` | `httpx2.AsyncHTTPTransport` |
| `httpx.MockTransport` | `httpx2.MockTransport` |

Numeric timeout values and string URLs are unchanged. Custom transport subclasses, mounted transports, proxy integrations, and connection-pool instrumentation must target HTTPX2's transport interfaces. Auth handlers and event hooks receive `httpx2.Request`/`httpx2.Response` objects; if you subclass an auth or transport interface, subclass the matching `httpx2` class:

```python
client = OpenAI(http_client=DefaultHttpx2Client(event_hooks={"request": [log_request]}))
```

Module-level configuration: `openai.http_client = openai.DefaultHttpx2Client()`.

## aiohttp

`pip install 'openai[aiohttp]'` provides `DefaultAioHttpClient()` — an `httpx2.AsyncClient` over the SDK's HTTPX2-native aiohttp transport (it does not install legacy `httpx` or the external `httpx-aiohttp` adapter):

```python
async with AsyncOpenAI(http_client=DefaultAioHttpClient()) as client:
    ...
```

## Request mocking and tests

Mocks must intercept HTTPX2 requests and return HTTPX2 responses:

```python
import httpx2
from openai import OpenAI

def handler(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(200, request=request, json={"object": "list", "data": []})

client = OpenAI(http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))
assert client.models.list().data == []
```

RESPX must be HTTPX2-compatible; a RESPX version that only patches legacy `httpx` cannot intercept the SDK's default client.

## Legacy HTTPX escape hatch

For dependencies that require a legacy `httpx` client (runtime-only path, may be discontinued):

```python
from typing import Any, cast
import httpx
from openai import OpenAI

client = OpenAI(http_client=cast(Any, httpx.Client()))   # async: cast(Any, httpx.AsyncClient())
```

This preserves the `httpx` request/response/exception families; raw responses come back as `httpx.Response` (cast `cast_to` too). Static type checkers reject the direct assignment without `cast`/ignore. The same pattern works for legacy `httpx_aiohttp.HttpxAiohttpClient`; prefer `openai[aiohttp]` for new code.

## Raw responses

`.with_raw_response.` prefixes any HTTP method to get the "raw" response before parsing (a `LegacyAPIResponse`):

```python
response = client.chat.completions.with_raw_response.create(...)
print(response.headers.get("X-My-Header"))
print(response.request_id)
completion = response.parse()  # the object .create() would have returned
```

In the sync client `content` and `text` are methods, not properties; in the async client all methods are async.

`.with_streaming_response.` requires a context manager and defers reading the body until you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()`, or `.parse()` (async in `AsyncOpenAI`):

```python
with client.chat.completions.with_streaming_response.create(...) as response:
    print(response.headers.get("X-My-Header"))
    for line in response.iter_lines():
        print(line)
```

With a native HTTPX2 client, `response.http_response` / `response.http_request` are `httpx2.Response` / `httpx2.Request`; request unparsed bodies with `cast_to=httpx2.Response`.

## Mutual TLS (API-key auth)

1. Build a native `ssl.SSLContext`: `ssl.create_default_context(cafile=...)` (server trust; without `cafile` the OS trust store is used), then `load_cert_chain(certfile=..., keyfile=..., password=...)`. The PEM must contain the leaf certificate first, followed by all intermediates; OpenAI does not fetch missing intermediates via AIA.
2. Pass it through the custom HTTP client with `follow_redirects=False` so the client certificate cannot follow a response to another origin.
3. Select the mTLS endpoint explicitly — `base_url` defaults to `https://mtls.api.openai.com/v1` (preserve an EU or custom override via `OPENAI_BASE_URL`).

The certificate-bearing client is transport-wide: dedicate it to the OpenAI mTLS origin. For certificate rotation, build a new `SSLContext`, HTTP client, and SDK client (fresh connection pool), then close the old client after in-flight requests finish.

## X.509 workload identity (mTLS token exchange)

```python
client = OpenAI(
    workload_identity=x509_workload_identity(
        identity_provider_id=..., service_account_id=...),
    http_client=DefaultHttpx2Client(verify=tls_context, follow_redirects=False),
)
```

Defaults to `https://mtls.api.openai.com/v1` when neither `base_url` nor `OPENAI_BASE_URL` is set. X.509 requests require HTTPS on the configured API origin; token exchanges are pinned, lazy, cached, and refreshed automatically; API-key/proxy-only headers cannot be sent alongside X.509 auth; identity settings are captured at construction (create a new client to change identity). Azure clients do not support X.509 workload identity, and Realtime/WebSockets are not covered. Async uses `AsyncOpenAI` + `DefaultAsyncHttpx2Client`.

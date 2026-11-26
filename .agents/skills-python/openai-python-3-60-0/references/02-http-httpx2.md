# HTTPX2 Transport (v3.60.0)

The SDK's default HTTP layer is [HTTPX2](https://httpx2.pydantic.dev/). `httpx2` is installed automatically with `openai`; the previous `httpx` package is **not**. Applications using the default client see no change — API calls, parsed models, streaming, auth, retries, and numeric timeouts keep working.

## TLS trust store

HTTPX2 verifies certificates against the **operating-system trust store**, not the `certifi` bundle (the SDK no longer installs `certifi`). This can break verification in minimal containers without system CA certificates, behind TLS-inspecting proxies, and for deployments that relied on a custom `certifi` bundle. Fixes:

```sh
export SSL_CERT_FILE=/path/to/ca-bundle.pem   # or SSL_CERT_DIR=/path/to/ca-directory
```

Both are honored when `trust_env=True` (the default). Explicit control on a custom client:

```python
import ssl
from openai import OpenAI, DefaultHttpx2Client

ssl_context = ssl.create_default_context(cafile="/path/to/ca-bundle.pem")
client = OpenAI(http_client=DefaultHttpx2Client(verify=ssl_context))
```

`DefaultAsyncHttpx2Client(verify=ssl_context)` is the async equivalent; the aiohttp transport uses the same HTTPX2 TLS settings.

## Custom clients and objects

Prefer `DefaultHttpx2Client` / `DefaultAsyncHttpx2Client` — they preserve the SDK's recommended timeout, connection-pool, and redirect defaults. Directly constructed `httpx2.Client` / `httpx2.AsyncClient` instances also work (their own HTTPX2 defaults apply). The legacy names `DefaultHttpxClient` / `DefaultAsyncHttpxClient` still work but construct HTTPX2 clients. Module-level: `openai.http_client = openai.DefaultHttpx2Client()`.

| Previous object | HTTPX2 object |
| --- | --- |
| `httpx.Client` | `httpx2.Client` |
| `httpx.AsyncClient` | `httpx2.AsyncClient` |
| `httpx.Timeout` | `httpx2.Timeout` |
| `httpx.URL` | `httpx2.URL` |
| `httpx.Limits` | `httpx2.Limits` |
| `httpx.HTTPTransport` | `httpx2.HTTPTransport` |
| `httpx.AsyncHTTPTransport` | `httpx2.AsyncHTTPTransport` |
| `httpx.MockTransport` | `httpx2.MockTransport` |

String URLs and numeric timeouts do not change. Auth handlers and event hooks receive HTTPX2 request/response objects:

```python
def log_request(request: httpx2.Request) -> None:
    print(request.method, request.url)

client = OpenAI(http_client=DefaultHttpx2Client(event_hooks={"request": [log_request]}))
```

## Raw responses, mocking

With a native HTTPX2 client, `response.http_response` / `response.http_request` are `httpx2.Response` / `httpx2.Request`; use `cast_to=httpx2.Response` for unparsed HTTP responses. Mocking targets HTTPX2 — `httpx2.MockTransport(handler)` returning `httpx2.Response(...)`; RESPX must be an HTTPX2-compatible version.

## Legacy HTTPX escape hatch (temporary)

```python
from typing import Any, cast
import httpx
from openai import OpenAI

client = OpenAI(http_client=cast(Any, httpx.Client()))          # runtime-only; fails static typing
response = client.get("/models", cast_to=cast(Any, httpx.Response))
```

Legacy clients preserve the HTTPX request/response/exception families; `cast_to=httpx2.Response` does not convert a legacy response. The existing `httpx-aiohttp` adapter can be injected the same way. This path is a migration aid and may be discontinued.

## Mutual TLS (API-key traffic)

Configure a native `ssl.SSLContext` and pass it through the custom HTTP client. The mTLS client certificate belongs to the HTTP client, not the base URL — select the mTLS origin explicitly:

```python
ssl_context = ssl.create_default_context(cafile=os.environ.get("OPENAI_MTLS_CA_BUNDLE"))
ssl_context.load_cert_chain(
    certfile=os.environ["OPENAI_MTLS_CERTIFICATE_CHAIN"],  # leaf first, then intermediates
    keyfile=os.environ["OPENAI_MTLS_PRIVATE_KEY"],
    password=os.environ.get("OPENAI_MTLS_PRIVATE_KEY_PASSWORD"),
)
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL", "https://mtls.api.openai.com/v1"),
    http_client=DefaultHttpx2Client(verify=ssl_context, follow_redirects=False),
)
```

Rules:

- The certificate-bearing HTTP client is transport-wide — dedicate it to the selected API origin; do not reuse it for unrelated services or pass it through `with_options()` with a different `base_url`.
- `load_cert_chain()` raises at setup for unreadable/malformed files or a key that does not match the leaf. OpenAI does not fetch missing intermediates via AIA — provide a complete, leaf-first client-chain PEM (intermediate-chain support is enabled by request).
- Certificate rotation: build a new `SSLContext`, HTTP client, and SDK client (fresh connection pool); close the old SDK client after in-flight requests finish.
- If redirects are required for API-key mTLS, add an HTTPX2 request hook rejecting requests whose scheme/host/port differs from the mTLS origin before enabling `follow_redirects`.
- Realtime WebSocket mTLS is not included. Examples: `examples/mtls_httpx2.py`, `examples/mtls_httpx2_async.py`.

## X.509 workload identity (mTLS token exchange)

```python
from openai import OpenAI, DefaultHttpx2Client
from openai.auth import x509_workload_identity

client = OpenAI(
    workload_identity=x509_workload_identity(
        identity_provider_id=os.environ["OPENAI_IDENTITY_PROVIDER_ID"],
        service_account_id=os.environ["OPENAI_SERVICE_ACCOUNT_ID"],
        # refresh_buffer_seconds=120.0,
    ),
    http_client=DefaultHttpx2Client(verify=tls_context, follow_redirects=False),
)
```

Constraints: HTTPS only and the request must stay on the configured API origin (effective Host must match); provider API-key and proxy-only headers cannot be sent alongside X.509 auth; token exchanges do not inherit API request hooks, authentication, or cookies; tokens are exchanged lazily, cached, and refreshed automatically. X.509 supports HTTP APIs only — Realtime and WebSockets are not included, and Beta WebSockets always reject X.509 clients. Azure clients do not support X.509 workload identity. Identity settings are captured at construction — create a new client to change the identity. Examples: `examples/x509_workload_identity.py`, `examples/x509_workload_identity_async.py` (app-owned `OPENAI_AUTH_MODE` env var selects API-key vs X.509).

# openai-python 3.6.0 — Client Configuration

## Environment variables

The client infers these from the environment when the matching argument is not passed:

| Variable | Client argument | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | `api_key` | API key authentication |
| `OPENAI_ADMIN_KEY` | `admin_api_key` | Admin API access (`client.admin`) |
| `OPENAI_ORG_ID` | `organization` | Organization to use for requests |
| `OPENAI_PROJECT_ID` | `project` | Project to use for requests |
| `OPENAI_WEBHOOK_SECRET` | `webhook_secret` | Signature verification for `client.webhooks` |
| `OPENAI_BASE_URL` | `base_url` | Endpoint override (default `https://api.openai.com/v1`) |
| `OPENAI_CUSTOM_HEADERS` | merged into `default_headers` | Ignored when a `provider` is set |
| `OPENAI_LOG` | — | Set to `info` or `debug` to enable stdlib logging |

There are **no** env vars for timeout or retry counts — those are constructor options only.

## Constructor options

```python
client = OpenAI(
    api_key="sk-...",            # str, or a zero-arg callable that returns/refreshes a key
    admin_api_key=None,
    organization=None,
    project=None,
    webhook_secret=None,
    base_url=None,               # default https://api.openai.com/v1
    websocket_base_url=None,
    timeout=600.0,               # float seconds or httpx2.Timeout; default 10 minutes
    max_retries=2,               # int; default 2
    http_client=None,            # DefaultHttpx2Client by default; see HTTPX2 section
    default_headers=None,        # dict, merged into every request
    default_query=None,          # dict, merged into every query string
    data_residency=None,         # DataResidency; selects a regional endpoint
    provider=None,               # e.g. openai.providers.bedrock(...)
    workload_identity=None,      # dict; see 05-authentication-cloud.md
)
```

Notes:

- `api_key` accepts a callable `() -> str` for refreshable keys; it is invoked per request.
- `provider` cannot be combined with `api_key`, `admin_api_key`, `workload_identity`, or `base_url` — move those options into the provider constructor.
- `data_residency` cannot be combined with `base_url`, `websocket_base_url`, or `provider`.
- `timeout` accepts a plain float or `httpx2.Timeout(60.0, connect=5.0, read=20.0, write=10.0)` for granular control.

## Per-request overrides

`with_options()` returns a copy of the client with changed options; the original is untouched:

```python
client.with_options(max_retries=5, timeout=5.0).chat.completions.create(...)
```

## Module-level client

The `openai` module exposes lazily-loaded shortcuts sharing one global client. Configure options by assigning module attributes, then call resources directly:

```python
import openai

openai.api_key = "..."            # defaults to os.environ['OPENAI_API_KEY']
openai.base_url = "https://..."
openai.default_headers = {"x-foo": "true"}

completion = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
```

All client options can be set this way (`openai.timeout`, `openai.max_retries`, `openai.http_client`, ...). Prefer explicit `OpenAI()` clients in application code; the module client is for scripts and notebooks.

## Async transport with aiohttp

The async client uses HTTPX2 by default. For higher concurrency, use the aiohttp transport:

```sh
pip install 'openai[aiohttp]'
```

```python
from openai import AsyncOpenAI, DefaultAioHttpClient

async with AsyncOpenAI(http_client=DefaultAioHttpClient()) as client:
    ...
```

`DefaultAioHttpClient()` is an `httpx2.AsyncClient` backed by an HTTPX2-native aiohttp transport; no legacy `httpx` or `httpx-aiohttp` packages are involved.

## HTTPX2 and custom HTTP clients

The SDK ships `DefaultHttpx2Client` (sync) and `DefaultAsyncHttpx2Client` (async), which preserve the SDK's recommended timeout, connection-pool, and redirect defaults. Pass a configured one for proxies, transports, and TLS:

```python
import httpx2
from openai import OpenAI, DefaultHttpx2Client

client = OpenAI(http_client=DefaultHttpx2Client(
    proxy="http://my.test.proxy.example.com",
    transport=httpx2.HTTPTransport(local_address="0.0.0.0"),
    timeout=httpx2.Timeout(30.0, connect=5.0),
))
```

Object mapping from legacy `httpx` to `httpx2`: `Client`, `AsyncClient`, `Timeout`, `URL`, `Limits`, `HTTPTransport`, `AsyncHTTPTransport`, `MockTransport`. Numeric timeouts and string URLs are unchanged.

TLS: HTTPX2 verifies against the **operating-system trust store**, not certifi (the SDK no longer installs certifi). In minimal containers or behind TLS-inspecting proxies, install CAs in the OS store, set `SSL_CERT_FILE` / `SSL_CERT_DIR` (honored with `trust_env=True`, the default), or pass an explicit context:

```python
import ssl
from openai import OpenAI, DefaultHttpx2Client

ssl_context = ssl.create_default_context(cafile="/path/to/ca-bundle.pem")
client = OpenAI(http_client=DefaultHttpx2Client(verify=ssl_context))
```

Legacy `httpx` escape hatch: install `httpx` yourself and inject a legacy client — but only at runtime, since public annotations take HTTPX2 objects, so static checkers need `cast(Any, ...)`:

```python
from typing import Any, cast
import httpx
from openai import OpenAI

client = OpenAI(http_client=cast(Any, httpx.Client()))
response = client.get("/models", cast_to=cast(Any, httpx.Response))
```

The old names `DefaultHttpxClient` / `DefaultAsyncHttpxClient` still work but now construct HTTPX2 clients.

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

## Resource management

Connections close when the client is garbage collected; close explicitly for determinism:

```python
with OpenAI() as client:
    ...  # make requests

client.close()  # or AsyncOpenAI: await client.close()
```

## Logging

Standard-library `logging` under the `openai` logger. Enable with `export OPENAI_LOG=info` (or `debug`).

## Installed version

```python
import openai
print(openai.__version__)  # "3.6.0"
```

If an upgraded environment does not show expected features, check this first — the interpreter may still resolve an older `openai`.

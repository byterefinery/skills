# requests 2.34.2 — Sessions and Adapters

## Session

`Session` persists settings across requests and manages connection pooling via `HTTPAdapter`.

### Attributes

| Attribute | Default | Description |
|---|---|---|
| `headers` | Default User-Agent | Headers sent with every request |
| `auth` | `None` | Default authentication |
| `proxies` | `{}` | Proxy dict merged with env vars if `trust_env=True` |
| `hooks` | `{"response": []}` | Event hook callbacks |
| `params` | `{}` | Default query parameters (merged per-request) |
| `stream` | `False` | Default streaming behavior |
| `verify` | `True` | Default TLS verification |
| `cert` | `None` | Default client certificate |
| `max_redirects` | 30 | Maximum redirect hops |
| `trust_env` | `True` | Read proxies/auth from environment (.netrc, HTTP_PROXY) |
| `cookies` | `RequestsCookieJar()` | Cookie jar persisted across requests |
| `adapters` | `OrderedDict` | Mounted transport adapters by URL prefix |

### Context Manager

```python
with requests.Session() as s:
    s.get("https://api.example.com/endpoint")
# Session.close() called automatically — releases all connection pools
```

### Request Flow

1. `Session.request()` creates a `Request` object with merged parameters
2. `Session.prepare_request()` merges session defaults into the request, producing a `PreparedRequest`
3. `Session.send()` selects the appropriate adapter and transmits the request
4. Response hooks are dispatched
5. Cookies from the response are extracted into the session's cookie jar
6. Redirects are resolved if `allow_redirects=True`

### Setting Defaults

```python
s = requests.Session()
s.headers.update({"Accept": "application/json"})
s.auth = HTTPBasicAuth("user", "pass")
s.params = {"version": "2"}
s.trust_env = False  # ignore env proxy vars
```

Per-request parameters override session defaults. If a per-request value is `None`, the session default is used.

### `Session.mount(prefix, adapter)`

Registers an adapter for URLs matching a prefix. Adapters are matched by longest prefix first.

```python
adapter = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=40,
    max_retries=3,
    pool_block=True,
)
s.mount("https://api.example.com", adapter)
s.mount("http://", adapter)  # all HTTP
```

Default session mounts:
- `https://` → `HTTPAdapter()`
- `http://` → `HTTPAdapter()`

### `Session.get_adapter(url)`

Returns the matching `BaseAdapter` for a URL. Raises `InvalidSchema` if no adapter matches.

## HTTPAdapter

Transport layer wrapping `urllib3`. Handles connection pooling, retries, and proxy management.

### Constructor

```python
HTTPAdapter(
    pool_connections=10,   # number of urllib3 PoolManagers to cache
    pool_maxsize=10,       # max connections per pool
    max_retries=0,         # int or urllib3.util.retry.Retry
    pool_block=False,      # block when pool is exhausted
)
```

### Connection Pooling

Each unique hostname+scheme gets its own `urllib3` connection pool. `pool_connections` controls how many pools are cached; `pool_maxsize` controls connections per pool.

- Default pool: 10 pools, 10 connections each
- Connections are reused within a session automatically
- Call `Session.close()` to release all pooled connections

### Retries

By default, `max_retries=0` means no retries. Set to an integer for simple retry count, or pass a `urllib3.util.retry.Retry` object for fine-grained control.

```python
from urllib3.util.retry import Retry

# Simple: retry up to 3 times on connection failures
adapter = HTTPAdapter(max_retries=3)

# Advanced: custom retry policy
retry = Retry(
    total=5,                       # total retry budget
    connect=3,                     # retries for connection errors
    read=2,                        # retries for read timeouts
    status=3,                      # retries for status_forcelist codes
    backoff_factor=0.5,            # wait = factor * (2 ** attempt)
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET", "POST", "PUT", "DELETE"],  # default excludes non-safe methods
    respect_retry_after_header=True,
)
adapter = HTTPAdapter(max_retries=retry)
```

**Important:** Retries only apply to DNS failures, socket connection failures, and connection timeouts. They do not retry requests where data was sent to the server. A `ReadTimeout` (server connected but didn't respond in time) is retried; a 500 response is retried only if included in `status_forcelist`.

### Proxy Handling

The adapter manages proxy connections internally via `urllib3.proxy_from_url()`. SOCKS proxies require the `requests[socks]` extra (installs `pysocks`).

```python
# HTTP/HTTPS proxy
proxies = {"http": "http://proxy:8080", "https": "http://proxy:8080"}

# SOCKS proxy (requires pip install requests[socks])
proxies = {"all": "socks5h://proxy:1080"}
```

The `socks5h://` scheme forces DNS resolution through the proxy (remote DNS). `socks5://` resolves locally.

## Environment Variables

When `Session.trust_env=True` (default):

| Variable | Effect |
|---|---|
| `HTTP_PROXY` / `http_proxy` | HTTP proxy URL |
| `HTTPS_PROXY` / `https_proxy` | HTTPS proxy URL |
| `NO_PROXY` / `no_proxy` | Comma-separated hosts to bypass proxy |
| `REQUESTS_CA_BUNDLE` | Custom CA bundle path (overrides default verify) |
| `CURL_CA_BUNDLE` | Same as above (cURL compatibility) |

`.netrc` file is consulted for basic auth credentials when no explicit auth is set.

---
name: requests-2-34-2
description: >
  Python HTTP library (requests) version 2.34.2 — sends HTTP/1.1 requests via
  the high-level API (requests.get, requests.post, etc.), Session objects for
  cookie/auth persistence and connection pooling, PreparedRequest for low-level
  control, streaming responses, file uploads, authentication (Basic/Digest),
  proxies, TLS verification, retries, and hooks. Use this skill whenever the
  user works with Python HTTP clients, needs to call REST APIs, upload files,
  handle sessions or cookies, configure timeouts or retries, inspect response
  headers/status codes, or debug HTTP requests in Python, even if they don't
  name "requests" explicitly.
metadata:
  tags:
    - python
    - http
    - networking
---

# requests 2.34.2

## Overview

`requests` 2.34.2 is the de facto standard Python HTTP client library ("HTTP for Humans"). It sits on top of `urllib3` and provides a clean API for making HTTP requests, handling sessions, cookies, authentication, file uploads, streaming responses, retries, and TLS verification.

Key objects:

- **Top-level functions** — `requests.get()`, `requests.post()`, etc. (convenience wrappers that create a one-off `Session` internally)
- **`Session`** — persists cookies, auth, headers, and connection pools across requests; supports context management (`with`)
- **`Request` / `PreparedRequest`** — mutable request objects; `PreparedRequest` holds the exact bytes sent to the server
- **`Response`** — server response with `.status_code`, `.text`, `.content`, `.json()`, `.headers` (case-insensitive), `.cookies`, `.elapsed`
- **`HTTPAdapter`** — transport layer wrapping `urllib3`; controls connection pooling and retries per URL prefix via `Session.mount()`

Dependencies: `urllib3`, `charset-normalizer` (or `chardet` fallback), `idna`, `certifi`.

## Usage

### Quick requests (module-level convenience)

```python
import requests

r = requests.get("https://httpbin.org/get", params={"key": "value"})
r = requests.post("https://httpbin.org/post", json={"key": "value"})
r = requests.put("https://httpbin.org/put", data=b"raw bytes")
r = requests.patch("https://httpbin.org/patch", data={"field": "updated"})
r = requests.delete("https://httpbin.org/delete")
r = requests.head("https://httpbin.org/get")   # no redirect by default
r = requests.options("https://httpbin.org/get")
```

All return a `Response` object.

### Sessions (persistent settings)

Use `Session` when making multiple requests to the same host — it reuses TCP connections and persists cookies:

```python
import requests

with requests.Session() as s:
    s.headers.update({"Authorization": "Bearer token"})
    s.params = {"api_version": "2"}
    r1 = s.get("https://api.example.com/users")
    r2 = s.post("https://api.example.com/users", json={"name": "Alice"})
```

Session attributes set once apply to every request: `headers`, `auth`, `proxies`, `hooks`, `params`, `stream`, `verify`, `cert`, `max_redirects`, `trust_env`, `cookies`.

### Response inspection

```python
r = requests.get("https://httpbin.org/json")

r.status_code           # int, e.g. 200
r.ok                    # True if status < 400
r.headers["Content-Type"]  # case-insensitive dict
r.text                  # str (decoded using r.encoding or apparent_encoding)
r.content               # bytes
r.json()                # parsed JSON (dict, list, etc.)
r.cookies               # RequestsCookieJar
r.elapsed               # datetime.timedelta
r.history               # list of Response objects (redirects)
r.request               # the PreparedRequest that produced this response

# Raise HTTPError on 4xx/5xx
r.raise_for_status()
```

### Timeouts

Always set timeouts to avoid hanging:

```python
requests.get(url, timeout=5.0)              # single float for connect + read
requests.get(url, timeout=(3.0, 7.0))       # (connect_timeout, read_timeout)
```

`timeout=None` means wait forever. On `Session`, the default is also `None`.

### File uploads

```python
# Single file
with open("report.pdf", "rb") as f:
    r = requests.post("https://httpbin.org/post", files={"file": f})

# Multiple files with explicit names and content types
files = [
    ("docs", ("report.pdf", open("r.pdf", "rb"), "application/pdf")),
    ("docs", ("notes.txt", open("n.txt", "rb"), "text/plain")),
]
requests.post(url, files=files)

# File with custom headers
files = {"file": ("data.csv", f, "text/csv", {"X-Custom": "value"})}
```

### Authentication

```python
# Basic auth as tuple (shorthand)
requests.get(url, auth=("user", "pass"))

# Basic auth object (reusable across sessions)
from requests.auth import HTTPBasicAuth
s.auth = HTTPBasicAuth("user", "pass")

# Digest auth
from requests.auth import HTTPDigestAuth
requests.get(url, auth=HTTPDigestAuth("user", "pass"))

# Custom auth — subclass AuthBase
from requests.auth import AuthBase

class TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r
```

### Proxies

```python
proxies = {
    "http": "http://10.10.1.10:3128",
    "https": "http://10.10.1.10:1080",
}
requests.get(url, proxies=proxies)

# Per-host proxy
proxies = {"http://host.name": "http://different.proxy:8080"}

# Proxy with auth
proxies = {"https": "http://user:pass@proxy:3128/"}

# SOCKS (requires pip install requests[socks])
proxies = {"all": "socks5://proxy:1080"}
```

When `Session.trust_env=True` (default), environment variables `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` are respected.

### TLS verification and client certificates

```python
# Verify with system CA bundle (default)
requests.get("https://example.com")

# Verify with custom CA bundle
requests.get(url, verify="/path/to/ca-bundle.crt")

# Disable verification (testing only — vulnerable to MitM)
requests.get(url, verify=False)

# Client certificate as single file (cert + key bundled)
requests.get(url, cert="/path/to/client.pem")

# Client certificate as tuple (cert, key)
requests.get(url, cert=("/path/to/cert.pem", "/path/to/key.pem"))
```

### Streaming responses

```python
# Stream large downloads without loading into memory
r = requests.get("https://example.com/large-file", stream=True)
for chunk in r.iter_content(chunk_size=8192):
    process(chunk)

# Iterate lines (e.g., server-sent events, NDJSON)
for line in r.iter_lines():
    print(line)

# Close when done (or use context manager)
r.close()
```

Without `stream=True`, the full response body is downloaded on return.

### Retries and connection pooling

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

s = requests.Session()

# Simple integer retries (applies to connect failures, DNS, timeouts)
adapter = HTTPAdapter(max_retries=3)
s.mount("https://", adapter)

# Fine-grained retry policy
retry = Retry(
    total=5,
    backoff_factor=0.5,       # 0.5s, 1s, 2s, 4s...
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET", "POST", "PUT"],  # default is only safe methods
)
adapter = HTTPAdapter(max_retries=retry)
s.mount("https://api.example.com", adapter)
```

Default `HTTPAdapter` has `max_retries=0` (no retries). Retries apply to failed DNS lookups, socket connections, and connection timeouts — never to requests where data reached the server.

### Hooks

```python
def log_response(response, **kwargs):
    print(f"{response.request.method} {response.url} -> {response.status_code}")

requests.get(url, hooks={"response": log_response})

# Multiple hooks
hooks = {"response": [log_response, another_callback]}
s.hooks["response"].append(log_response)  # on session level
```

Only one hook event exists: `response` (fired after receiving a response).

### PreparedRequest (low-level control)

```python
from requests import Request, Session

req = Request("POST", url, data={"key": "val"}, headers={"X-Custom": "1"})
s = Session()
prepared = s.prepare_request(req)  # merges session settings

# Modify before sending
prepared.headers["Extra"] = "value"
r = s.send(prepared, timeout=5.0)
```

Use `PreparedRequest` when you need to inspect or modify the exact bytes sent, or implement custom logic between preparation and transmission.

### Status codes lookup

```python
import requests

requests.codes.ok              # 200
requests.codes.not_found       # 404
requests.codes['temporary_redirect']  # 307
requests.codes.teapot          # 418
bool(requests.codes[500])      # True — some codes have aliases
```

## Gotchas

- **Always set `timeout`** — the default is `None` (wait forever). A request without a timeout can hang indefinitely on slow or unresponsive servers.
- **Module-level functions create ephemeral sessions** — `requests.get()` creates a new `Session` per call and closes it, so TCP connections are not reused. Use `Session` for repeated requests to the same host.
- **`r.text` encoding can be wrong** — `requests` infers encoding from HTTP headers only (RFC 2616). If the server omits or misreports charset, set `r.encoding = "utf-8"` before accessing `r.text`. Use `r.apparent_encoding` as a fallback guess.
- **`stream=True` requires explicit `.close()`** — when streaming, the connection stays open until you consume all data and call `r.close()`. Use context managers (`with r:`) to avoid leaking connections.
- **Redirects strip auth headers on cross-host redirects** — if redirected to a different hostname, the `Authorization` header is removed to prevent credential leakage. On same-host http→https redirect (standard ports), auth is preserved.
- **POST body not rewindable on file objects** — if you pass an open file as `data` and the request needs to retry or redirect, requests tries to `seek()` back. Non-seekable streams (pipes, sockets) will fail with `UnrewindableBodyError`.
- **`verify=False` silences InsecureRequestWarning** — setting `verify=False` triggers a warning by default. Suppress with `urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)` if intentional.
- **`Session.trust_env=True` reads proxy env vars** — in production, consider setting `s.trust_env = False` to avoid unexpected proxy configuration from environment.
- **`data` vs `json` parameter** — `data=dict` sends `application/x-www-form-urlencoded`; `json=dict` sends `application/json`. They are mutually exclusive for body encoding (passing both uses `json` for the body and `data` is ignored for encoding).
- **Default retries are zero** — `HTTPAdapter` defaults to no retries. Network blips will cause immediate failures unless you configure retries explicitly.
- **Cookies persist across redirects automatically** but only within a `Session`. Module-level calls do not share cookies between requests.
- **`Response.json()` raises on empty body** — calling `.json()` on a response with no content raises `JSONDecodeError`, not returning `None`.

## References

- [01-api-reference](references/01-api-reference.md) — Full API surface: all parameters, types, and return values
- [02-sessions-and-adapters](references/02-sessions-and-adapters.md) — Session lifecycle, mount prefixes, HTTPAdapter pooling, Retry policies
- [03-authentication](references/03-authentication.md) — Basic, Digest, custom AuthBase, proxy auth, .netrc integration
- [04-response-object](references/04-response-object.md) — Response attributes, encoding detection, streaming iterators, hooks
- [05-exceptions](references/05-exceptions.md) — Exception hierarchy, when each is raised, retryability

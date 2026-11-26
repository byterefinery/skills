# HTTP Client

Source: `docs/client_quickstart.rst`, `docs/client_advanced.rst`, `aiohttp/client.py`.

## TOC

- Session lifecycle
- Making requests
- URL parameters
- Response content
- Sending data
- Streaming uploads
- Headers and authentication
- Cookies
- Timeouts
- JSON serialization
- Charset
- Upload tracking

## Session lifecycle

`ClientSession` is the main entry point for the client API. It contains a cookie storage and connection pool, so cookies and connections are shared between requests made through the same session.

```python
async with aiohttp.ClientSession() as session:
    async with session.get("http://httpbin.org/get") as resp:
        print(resp.status)
        print(await resp.text())
```

- A session context manager is not mandatory, but then you must `await session.close()`.
- One session per application (or per site in complex cases), never one per request. Connection reuse and keep-alive are on by default.
- Constructor parameters (verified from source): `base_url`, `connector`, `cookies`, `headers`, `proxy`, `skip_auto_headers`, `json_serialize`, `json_serialize_bytes`, `request_class`/`response_class`/`ws_response_class`, `version`, `cookie_jar`, `connector_owner` (True), `raise_for_status` (False; bool or callable), `timeout` (sentinel → default), `auto_decompress` (True), `trust_env` (False), `requote_redirect_url` (True), `trace_configs`, `read_bufsize`, `max_line_size`/`max_field_size` (8190), `max_headers` (128), `fallback_charset_resolver`, `middlewares` (tuple, default `()`), `ssl_shutdown_timeout`. Deprecated params that still work: `auth`, `proxy_auth`, `read_timeout`, `conn_timeout`, `loop`. Per-request parameters additionally include `proxy_headers` and `upload_tracker`.
- `base_url` must be absolute and end with `/` (else `ValueError`).
- `raise_for_status=True` (or a callable) makes every response raise `ClientResponseError` on 4xx/5xx.
- The passed `headers`/`cookies` dicts are copied — mutate `session.headers`/`session.cookies` after construction.

## Making requests

Methods: `session.get/post/put/delete/head/options/patch`, or generic `session.request(method, url, ...)`. The mandatory parameter is the URL (`str` or `yarl.URL`).

```python
async with session.post("http://httpbin.org/post", data=b"data") as resp:
    ...
```

Per-request options include `params`, `data`, `json`, `headers`, `cookies`, `allow_redirects` (default True), `timeout`, `middlewares`, `upload_tracker`, `ssl`, `proxy`, `proxy_headers`.

## URL parameters

`params` accepts a `dict`, `MultiDict`, a list of 2-tuples (multiple values per key), or a raw query-string `str`.

```python
params = {"key1": "value1", "key2": "value2"}
async with session.get("http://httpbin.org/get", params=params) as resp:
    assert str(resp.url) == "http://httpbin.org/get?key1=value1&key2=value2"
```

- aiohttp canonicalizes URLs before sending (IDNA host encoding, requoting of path/query).
- `URL("http://example.com/%30", encoded=True)` disables canonicalization, but passing `params` overrides it — build the full URL instead to preserve exact query bytes.
- Passing a `str` as `params` does not encode `+`.

## Response content

`ClientResponse` attributes/methods:

- `resp.status` — int status code
- `await resp.text(encoding=None)` — body decoded to `str` (whole body in memory)
- `await resp.read()` — body as `bytes` (gzip/deflate transfer encodings decoded automatically; brotli if `Brotli`/`brotlicffi` installed; zstd if `backports.zstd` installed or Python >= 3.14)
- `await resp.json(content_type="application/json")` — JSON decode; validates Content-Type (see Gotchas). Override with explicit `content_type='custom/type'` or disable with `content_type=None`.
- `resp.headers` — `CIMultiDictProxy`, case-insensitive, multi-value capable
- `resp.raw_headers` — tuple of `(bytes, bytes)` pairs, unconverted
- `resp.cookies` — cookies from `Set-Cookie` of the **last** request in the redirect chain only
- `resp.history` — tuple of intermediate `ClientResponse`s; empty if no redirects
- `resp.url` — final URL (after redirects)
- `resp.content` — `StreamReader` for streaming; `resp.content_length` may be `None`

Streaming large downloads:

```python
async with session.get(url) as resp:
    with open(filename, "wb") as fd:
        async for chunk in resp.content.iter_chunked(chunk_size):
            fd.write(chunk)
```

After explicitly reading from `resp.content`, `read()`/`json()`/`text()` are no longer usable.

## Sending data

- `data={"key1": "value1", ...}` — form-encoded (`application/x-www-form-urlencoded`)
- `data=b"\x00Binary-data\x00"` — raw bytes, `application/octet-stream` by default
- `data="Тест"` — text with appropriate content-type
- `json={"example": "test"}` — JSON body (uses `json_serialize`, default stdlib `json.dumps`)
- `data=file_object` — file uploaded as multipart (`data={'file': open('report.xls', 'rb')}`); streamed automatically
- `data=aiohttp.FormData()` with `add_field('file', f, filename=..., content_type=...)` for explicit metadata

`data` and `json` are mutually exclusive.

## Streaming uploads

- File-like object: `await session.post(url, data=open("massive-body", "rb"))`
- Async generator (generated on the fly):

```python
async def data_generator():
    for i in range(10):
        yield f"line {i}\n".encode()

async with session.post(url, data=data_generator()) as resp:
    ...
```

- `aiohttp.streamer` is deprecated in favor of async generators (since 3.1).
- Non-rewindable sources cannot replay on 307/308 redirects — `ClientPayloadError`.
- You can chain responses: `await session.post(url, data=resp.content)` — the response body is a `StreamReader`.

## Headers and authentication

Per-request: `headers={"content-type": "image/gif"}`. Session-wide defaults: `ClientSession(headers={...})`.

Basic auth (3.14 way — `auth`/`BasicAuth` deprecated, removed in 4.0):

```python
from aiohttp import encode_basic_auth

headers = {"Authorization": encode_basic_auth("user", "pass")}
async with ClientSession(headers=headers) as session:
    ...
```

Digest auth via client middleware:

```python
from aiohttp import DigestAuthMiddleware

digest_auth = DigestAuthMiddleware(login="user", password="password")
async with ClientSession(middlewares=(digest_auth,)) as session:
    async with session.get("https://example.com/protected") as resp:
        ...
```

The middleware implements RFC 7616 (MD5/SHA/SHA-256/SHA-512 + session variants, qop `auth`/`auth-int`), intercepts 401 responses and retries with proper credentials.

Bearer tokens: set `Authorization` header directly, e.g. `session.headers["Authorization"] = "Bearer eyJh..."` (a background task can refresh it).

Notes: `Authorization` is removed when redirected to a different host or protocol. Credentials embedded in a redirect URL supersede previously set credentials.

## Cookies

- Send: `ClientSession(cookies={'cookies_are': 'working'})` or per request.
- Receive/share: the session jar handles it automatically (`session.cookie_jar` for direct access).
- `CookieJar(unsafe=True)` — accept cookies from IP-address URLs (RFC 2109 forbids it by default).
- `CookieJar(quote_cookie=False)` — skip RFC 2109 quoting for backends that choke on it.
- `DummyCookieJar()` — no cookie processing at all.
- `resp.cookies` holds only the last response's `Set-Cookie` values in a redirect chain.

## Timeouts

`ClientTimeout` is an attrs dataclass with fields `total`, `connect`, `sock_connect`, `sock_read`, `ceil_threshold` (default 5). All floats; `None` or `0` disables that check.

- `total` — whole operation (connect + send + read). Default **300 s**.
- `connect` — establishing a new connection or waiting for a pooled one.
- `sock_connect` — TCP connect for a non-pooled connection. Default **30 s** (DNS fallback allowance).
- `sock_read` — gap between data portions from the peer.
- Timeouts >= `ceil_threshold` (5 s) are ceiled to the next integer second to batch event-loop wakeups; smaller values are not rounded (test-friendly).

Apply per session (`ClientSession(timeout=...)`) or per request (`session.get(url, timeout=...)`).

## JSON serialization

`ClientSession(json_serialize=...)` accepts a string-encoding encoder (default `json.dumps`); `ClientSession(json_serialize_bytes=orjson.dumps)` accepts a bytes-returning encoder and avoids encode/decode overhead.

## Charset

`await resp.text("windows-1252")` forces an encoding. `ClientSession(fallback_charset_resolver=fn)` is called when Content-Type has no charset; `fn(resp, body_bytes) -> str`. Examples in the docs use `chardetng_py.detect` or `charset_normalizer.detect`.

## Upload tracking (3.14)

- `ClientResponse.output_size` — bytes written so far; `ClientResponse.upload_complete` — an `asyncio.Future` that resolves when the request body is fully sent (useful with retries, where `upload_complete` reflects the final attempt).
- `aiohttp.UploadTracker` (3.14.4) — observable upload progress; pass via `ClientSession(upload_tracker=...)` or per request (`session.get(url, upload_tracker=...)`).

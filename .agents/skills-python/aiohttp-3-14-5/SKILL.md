---
name: aiohttp-3-14-5
description: >
  asyncio-based HTTP client/server framework for Python (aiohttp 3.14.5,
  Python 3.10+). Use when building or interacting with async HTTP services,
  REST APIs, WebSocket connections, or async web scraping. Covers
  ClientSession, Application/routing, middlewares, FileResponse, multipart
  uploads, streaming, tracing, and testing with TestClient/TestServer.
license: Apache-2.0 AND MIT
metadata:
  tags:
    - python
    - http
    - async
    - web
    - networking
---

# aiohttp 3.14.5

## Overview

aiohttp is a full-featured asyncio HTTP library providing both a client and a server (Python 3.10+; 3.9 support was dropped in 3.14.0). It uses `multidict` for headers/params, `yarl` for URLs, and `attrs` for data classes. The default client timeout is `ClientTimeout(total=300, sock_connect=30)`.

Key 3.14.x additions: `encode_basic_auth()` (replacing deprecated `BasicAuth`/`auth`/`proxy_auth`), client middleware with per-retry application, `RequestKey`/`ResponseKey`/`AppKey` typed storage keys, `decode_text=False` for raw-bytes WebSocket text, `ClientResponse.output_size`/`upload_complete`, `UploadTracker` (3.14.4), `client_max_fields` on `Application` (3.14.4, default 1000).

### Core imports

```python
# Client
from aiohttp import ClientSession, ClientTimeout, ClientError, encode_basic_auth, TCPConnector

# Server
from aiohttp import web
from aiohttp.web import (
    Application, Request, Response, StreamResponse,
    json_response, FileResponse, RouteTableDef, View, AppKey, RequestKey,
)

# WebSockets
from aiohttp import WSMsgType, WSCloseCode

# Multipart / helpers
from aiohttp import FormData, MultipartReader, MultipartWriter
from aiohttp import TraceConfig, hdrs
```

## Usage

### HTTP Client — basic pattern

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get("https://httpbin.org/get") as resp:
        print(resp.status)
        data = await resp.json()
```

### HTTP Client — POST with JSON

```python
async with aiohttp.ClientSession() as session:
    async with session.post(url, json={"test": "object"}) as resp:
        ...
```

Use `session.post(url, data=payload)` for form-encoded dicts, `data=b"..."` for raw bytes, or `data=file_obj`/async-generator for streaming uploads.

### HTTP Server — minimal app

```python
from aiohttp import web

async def hello(request: web.Request) -> web.Response:
    return web.Response(text="Hello, world")

app = web.Application()
app.add_routes([web.get("/", hello)])
web.run_app(app)
```

### HTTP Server — decorator routing

```python
routes = web.RouteTableDef()

@routes.get("/items/{item_id}")
async def get_item(request: web.Request) -> web.Response:
    item_id = request.match_info["item_id"]
    return web.json_response({"id": item_id})

app = web.Application()
app.add_routes(routes)
web.run_app(app)
```

### CLI (development)

```bash
# package.module:init_func must be a callable taking argv and returning an Application
python -m aiohttp.web -H localhost -P 8080 package.module:init_func
```

### WebSocket server

```python
from aiohttp import web, WSMsgType

async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == "close":
                await ws.close()
            else:
                await ws.send_str(msg.data + "/answer")
        elif msg.type == WSMsgType.ERROR:
            print("ws connection closed with exception", ws.exception())
    return ws

app = web.Application()
app.add_routes([web.get("/ws", ws_handler)])
```

### WebSocket client

```python
async with session.ws_connect("ws://example.org/ws") as ws:
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            print(msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break
```

## Gotchas

- **One `ClientSession` per application, not per request** — the session holds a connection pool and cookie jar; creating one per request is a documented anti-pattern.
- **`base_url` must end with `/`** — `ClientSession(base_url="https://api.example.com")` raises `ValueError("base_url must have a trailing '/'")`.
- **`auth`, `proxy_auth`, `BasicAuth` are deprecated in 3.14 (removed in 4.0)** — use `headers={"Authorization": encode_basic_auth(login, password)}` and `proxy_headers={"Proxy-Authorization": ...}` instead. Digest auth uses the `DigestAuthMiddleware` client middleware.
- **`read()`/`text()`/`json()` load the whole body into memory** — for large downloads iterate `resp.content.iter_chunked(n)`; after reading from `resp.content` you cannot call `read()`/`text()`/`json()`.
- **Non-rewindable bodies cannot replay on redirect** — an async generator or `StreamReader` as `data` raises `ClientPayloadError` on a 307/308 redirect. Use a seekable file or bytes, or `allow_redirects=False`.
- **`resp.json()` validates Content-Type** — it raises `ContentTypeError` for wrong types; pass `content_type='custom/type'` (strict) or `content_type=None` (disable check) to override.
- **Timeouts >= 5 s are ceiled to the next whole second** (`ceil_threshold=5` in `ClientTimeout`); `None`/`0` disables a specific timeout. Default is `total=300`, `sock_connect=30`.
- **Client middlewares run on every retry attempt** — order matters: `middlewares=(retry_mw, logging_mw)` logs each retry; reversed logs only once.
- **Session headers are a copy** — mutating the dict you passed to `ClientSession(headers=...)` has no effect; update `session.headers[...]` directly.
- **`Authorization` is stripped on cross-host/protocol redirects.**
- **Cookies are strict by default** — `CookieJar` refuses cookies from IP-address URLs (RFC 2109); use `CookieJar(unsafe=True)` for testing. `DummyCookieJar` disables cookie handling.
- **Proxy env vars are not read by default** — pass `trust_env=True` to `ClientSession` to honor `HTTP_PROXY`/`HTTPS_PROXY` (and `WS_PROXY`/`WSS_PROXY` since 3.8) and `no_proxy`.
- **Server handlers must be async** — a handler is a coroutine taking `request` and returning a `StreamResponse`-derived object.
- **`raise` HTTP exceptions, never return them** — returning an `HTTPException` from a handler is deprecated. `raise web.HTTPFound("/redirect")`, `raise web.HTTPNotFound()`, etc.
- **`request.post()` buffers the whole payload in memory** — use `await request.multipart()` (streaming `read_chunk()`) for large uploads; `post()` also raises `HTTPRequestEntityTooLarge` (413) when body exceeds `client_max_size` (default 1 MiB) or field count exceeds `client_max_fields` (default 1000, `0` disables).
- **WebSocket reads must stay in the handler task** — `await ws.receive()` / `async for msg in ws` from exactly one task; sending (`ws.send_str`) from other tasks is fine. Parallel reads are forbidden.
- **`decode_text=False` (3.14)** on `ws_connect`/`WebSocketResponse` keeps TEXT frames as `bytes` (e.g. for `orjson`); default decodes to `str`.
- **Client WS compression is off by default** (`compress=0`) while server `WebSocketResponse` compresses by default (`compress=True`).
- **Don't fire-and-forget with `asyncio.create_task` in handlers** — untracked tasks hide exceptions and may be cancelled at shutdown; use `aiojobs` (`spawn`/`shield`/`atomic`) or await the task.
- **`handler_cancellation=True` in `run_app`** cancels the handler when the client disconnects (recommended for DoS resilience); wrap must-not-interrupt work with `aiojobs.aiohttp.shield` or `@atomic`.
- **Use `AppKey`/`RequestKey`/`ResponseKey` for typed storage** (3.14) — `app[my_key] = data` with string keys is untyped; `request.config_dict[...]` searches sub-apps then parents.
- **`aiohttp.pytest_plugin` is deprecated (3.14)** — install the separate `pytest-aiohttp` package (or set `pytest_plugins = 'aiohttp.pytest_plugin'` in `conftest.py`).
- **`Application(router=...)` and `Application(loop=...)` kwargs are deprecated** — build the app with defaults and pass only `middlewares`, `handler_args`, `client_max_size`, `client_max_fields`, `debug`.
- **Sub-app URL reversing must use the sub-app's router** — `admin.router['name'].url_for()` produces `/admin/...` with the prefix; the top-level router does not.
- **Graceful client shutdown** — after closing the session, `await asyncio.sleep(0)` (0.25 s for SSL) before stopping the event loop, or unclosed transports emit `ResourceWarning`.
- **`resp.history`** is only populated when redirects occurred; empty tuple means none. Response cookies come only from the last response in the redirect chain — use the session jar for the full set.
- **Expect header** — the server answers `Expect: 100-continue` with `100 Continue` by default; register a per-route `expect_handler` (via `web.get(..., expect_handler=...)`) to customize.

## References

- [01-http-client](references/01-http-client.md) — ClientSession lifecycle, requests, params, response content, streaming uploads, timeouts, charset
- [02-http-server](references/02-http-server.md) — Application, Request/Response/StreamResponse, json_response, FileResponse, forms, file uploads, data storage
- [03-routing](references/03-routing.md) — UrlDispatcher, RouteTableDef, decorators, variable paths, named routes, View, static files, sub-applications
- [04-websockets](references/04-websockets.md) — ws_connect (client), WebSocketResponse (server), heartbeat, decode_text, shutdown
- [05-connectors-timeouts-ssl](references/05-connectors-timeouts-ssl.md) — TCPConnector, UnixConnector, NamedPipeConnector, ClientTimeout, SSL, fingerprints, proxies
- [06-middlewares-signals-tracing](references/06-middlewares-signals-tracing.md) — client middleware (retry pattern), DigestAuthMiddleware, web middlewares, signals, cleanup_ctx, TraceConfig
- [07-multipart](references/07-multipart.md) — MultipartReader/BodyPartReader, MultipartWriter, FormData, server-side multipart
- [08-testing](references/08-testing.md) — pytest-aiohttp fixtures, TestClient/TestServer, AioHTTPTestCase, make_mocked_request
- [09-exceptions](references/09-exceptions.md) — client exception hierarchy, web HTTPException codes, error handling
- [10-deployment-advanced](references/10-deployment-advanced.md) — AppRunner/sites, graceful shutdown, Gunicorn, background tasks, reverse proxies, third-party libraries

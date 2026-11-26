# HTTP Server

Source: `docs/web_quickstart.rst`, `docs/web_advanced.rst`, `aiohttp/web_app.py`, `aiohttp/web_response.py`.

## TOC

- Application and running
- Handlers
- Request object
- Response objects
- Forms and file uploads
- Data storage
- Redirects and exceptions
- Unicode

## Application and running

`web.Application()` constructor (keyword-only): `logger`, `middlewares` (tuple of middlewares, not factories' results — call factories), `handler_args` (e.g. `{"timeout_ceil_threshold": 1}`), `client_max_size` (default `1024**2`), `client_max_fields` (default 1000, `0` disables; 3.14.4), `debug`. `router=` and `loop=` kwargs are deprecated.

Running:

- `web.run_app(app, host, port, ...)` — blocking; accepts an app instance **or** an async factory coroutine (`web.run_app(make_app())`). `handler_cancellation=True` cancels handlers on client disconnect; `shutdown_timeout` bounds the drain wait.
- CLI: `python -m aiohttp.web -H localhost -P 8080 package.module:init_func` where `init_func(argv) -> Application` (dev only; `aiohttp-devtools` recommended for local development).
- `AppRunner`/`TCPSite` for async startup and multiple hosts (see [10-deployment-advanced](10-deployment-advanced.md)).

```python
runner = web.AppRunner(app)
await runner.setup()
site = web.TCPSite(runner, "localhost", 8080)
await site.start()
# ... later
await runner.cleanup()
```

## Handlers

A handler is a **coroutine** taking one `web.Request` and returning a `StreamResponse`-derived object (`Response`, `StreamResponse`, `WebSocketResponse`, ...).

```python
async def hello(request):
    return web.Response(text="Hello, world")
```

Use a `StreamResponse` directly to stream a body (prepare then write):

```python
resp = web.StreamResponse()
resp.content_length = len(binary)
resp.content_type = "text/plain"
await resp.prepare(request)
await resp.write(binary)
return resp
```

## Request object

`web.Request` (and `BaseRequest`) exposes:

- `request.method`, `request.path`, `request.query_string`, `request.match_info` (dict of `{var}` parts), `request.rel_url`
- `request.headers` (`CIMultiDict`), `request.app`, `request.config_dict` (walks sub-apps → parents), `request.is_connected()`
- `request.host`, `request.remote`, `request.scheme` — behind a reverse proxy these are wrong by default; see [10-deployment-advanced](10-deployment-advanced.md)
- `await request.read()` / `await request.text()` / `await request.json()` / `await request.post()` — high-level methods **cache** their result (safe to call twice)
- `request.content` — raw `StreamReader`; reading it directly consumes the stream (no caching)
- `await request.multipart()` — streaming multipart reader (see [07-multipart](07-multipart.md))

### Forms and file uploads

- GET form data: `request.query` (mapping).
- `await request.post()` — parses `application/x-www-form-urlencoded` **and** `multipart/form-data`; returns a `MultiDict` where uploaded files are `FileField` objects (`.filename`, `.file` file-like). Reads the whole payload into memory — avoid for large uploads.
- `await request.multipart()` — streaming `MultipartReader`; iterate fields with `field = await reader.next()`, read in chunks via `await field.read_chunk()` (8192 bytes default) and write to disk.
- Both raise `web.HTTPRequestEntityTooLarge` (413) when the body exceeds `client_max_size` (1 MiB default) or the form exceeds `client_max_fields` (1000 default, `0` disables; 3.14.4).

```python
async def store_mp3(request):
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename
    with open(f"/spool/{filename}", "wb") as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)
    return web.Response(text=f"{filename} stored")
```

## Response objects

- `web.Response(text=...)` / `web.Response(body=...)` — body (bytes) or text (encoded to bytes); set `status`, `headers`, `content_type`, `charset`.
- `web.json_response(data, content_type="application/json")` — returns a `Response` (cookies etc. still settable).
- `web.FileResponse(path)` — serves a file from disk (supports conditional `If-Modified-Since`/range requests); also `web.StaticRoute`/`web.static(...)` for folders (see [03-routing](03-routing.md)).
- `web.StreamResponse` — base class; call `await resp.prepare(request)` before `resp.write(chunk)` / `resp.drain()`; can be returned from the handler after writes.
- `resp.set_cookie(name, value, ...)` / `resp.del_cookie(name)` on any `StreamResponse`.

`Response` objects are also `MutableMapping` — store per-response data via `ResponseKey` (3.14) for signals/middlewares to read after the handler returns.

## Data storage

No globals/singletons by design. `Application`, `Request`, and `StreamResponse` all support `MutableMapping`.

Prefer typed keys (3.14) for mypy safety:

```python
my_key = web.AppKey("my_private_key", str)   # app-wide
req_key = web.RequestKey("raw_body", bytes)  # request-scoped
resp_key = web.ResponseKey("metric", int)    # response-scoped

app[my_key] = data
# in a handler:
data = request.app[my_key]
# sub-app-aware lookup:
data = request.config_dict[my_key]
```

Choose unique key names (project name or `org.company.app`) to avoid collisions with third-party libraries.

## Redirects and exceptions

Redirect: `raise web.HTTPFound(location)` where location is a relative URL, absolute URL, or named-route URL from the router.

All HTTP status codes have an exception class (`HTTPFound`, `HTTPNotFound`, `HTTPMethodNotAllowed(method, allowed_methods)`, ...). **Raise** them; returning is deprecated:

```python
async def handler(request):
    raise web.HTTPFound("/redirect")
```

Constructor signature: `HTTPNotFound(*, headers=None, reason=None, body=None, text=None, content_type=None)` (redirection exceptions take `location` as first arg). Full hierarchy in [09-exceptions](09-exceptions.md).

## Unicode

aiohttp requotes incoming request paths; Unicode works transparently when adding and resolving routes (internally percent-encoded via yarl). Custom `{identifier:regex}` route patterns see the **percent-encoded** path — a Unicode regex pattern will not match; write patterns for the encoded form.

# Middlewares, Signals, Tracing

Source: `docs/client_advanced.rst` (Client Middleware, Client Tracing), `docs/web_advanced.rst` (Middlewares, Signals, Cleanup Context), `docs/tracing_reference.rst`, `examples/retry_middleware.py`.

## TOC

- Client middlewares
- Retry middleware pattern
- DigestAuthMiddleware
- Web middlewares
- Signals
- Cleanup contexts
- Client tracing (TraceConfig)

## Client middlewares

A client middleware is an async function (or callable class) with the `ClientMiddlewareType` signature — takes a `ClientRequest` and a handler, returns a response:

```python
async def auth_middleware(req: ClientRequest, handler: ClientHandlerType) -> ClientResponse:
    req.headers["Authorization"] = get_auth_header()
    return await handler(req)
```

Apply to a whole session or to a single request:

```python
# session-wide
async with ClientSession(middlewares=(my_middleware,)) as session:
    resp = await session.get("http://example.com")

# per-request (overrides session middlewares)
resp = await session.get("http://example.com", middlewares=(my_middleware,))
```

Execution is an onion: with `middlewares=(m1, m2)`, pre-request code runs m1 → m2 → request, post-response code runs m2 → m1.

**Middlewares run on every retry attempt** (the client's retry loop re-enters the chain). So `middlewares=(retry_mw, logging_mw)` logs each retry, while `(logging_mw, retry_mw)` logs once total.

## Retry middleware pattern

`examples/retry_middleware.py` implements a `RetryMiddleware` class with configurable `max_retries=3`, `retry_statuses={429, 500, 502, 503, 504}`, `initial_delay=1.0`, `backoff_factor=2.0` (exponential backoff). It rewrites the handler so failed statuses are retried with delays.

## DigestAuthMiddleware

Built-in client middleware for HTTP Digest authentication (RFC 7616):

```python
from aiohttp import ClientSession, DigestAuthMiddleware

digest_auth = DigestAuthMiddleware(login="user", password="password")
async with ClientSession(middlewares=(digest_auth,)) as session:
    async with session.get("https://example.com/protected") as resp:
        ...
```

Supports MD5/SHA/SHA-256/SHA-512 (+ session variants), qop `auth`/`auth-int`; intercepts 401 and retries with the computed credentials. Digest signatures use the encoded request-target sent on the wire (3.14 fix for percent-encoded paths).

## Web middlewares

A web middleware is a coroutine `(request, handler) -> StreamResponse`; the second argument must be named `handler` exactly.

```python
from aiohttp import web

@web.middleware
async def middleware(request: web.Request, handler) -> web.StreamResponse:
    resp = await handler(request)
    resp.headers["X-Extra"] = "value"
    return resp

app = web.Application(middlewares=[middleware])
```

- Execution order for `middlewares=[m1, m2]`: `m1 called → m2 called → handler → m2 finished → m1 finished`.
- A middleware may short-circuit (e.g. return 403 without calling the handler).
- Non-`HTTPException` exceptions propagate out of the chain and become 500.
- **Request body caching**: high-level `request.read()/text()/json()/post()` cache their result, so a middleware that reads the body does not starve the handler. Direct `request.content` reads do **not** cache — reading there empties the stream for the handler. If you must read raw stream in middleware, stash the bytes in `request[RequestKey(...)]`.
- Middleware factory: a function returning a middleware; pass the **result** (`middlewares=[factory(' wink')]`), not the factory.

## Signals

App-level hooks (`app.on_*` are `Signal` objects; append async handlers; handlers run sequentially in order and must be coroutines):

- `app.on_startup.append(fn)` — after app setup, before serving
- `app.on_shutdown.append(fn)` — during graceful shutdown (close websockets here)
- `app.on_cleanup.append(fn)` — final teardown (dispose DB engines, etc.)
- `app.on_response_prepare.append(fn)` — called after default headers are computed and **before** headers are sent; the only hook that can modify streamed/WebSocket response headers:

```python
async def on_prepare(request, response):
    response.headers["My-Header"] = "value"

app.on_response_prepare.append(on_prepare)
```

## Cleanup contexts

`app.cleanup_ctx` holds async context managers (code before `yield` = startup, after = cleanup). aiohttp guarantees cleanup runs **iff** startup finished successfully — solving the independent-signal pitfall:

```python
@contextlib.asynccontextmanager
async def pg_engine(app: web.Application):
    app[pg_engine_key] = await create_async_engine("postgresql+asyncpg://...")
    yield
    await app[pg_engine_key].dispose()

app.cleanup_ctx.append(pg_engine)
```

Since 3.14, cleanup contexts also accept **asynchronous context managers** directly (not only async generators).

## Client tracing (TraceConfig)

`TraceConfig` attaches signal handlers to client request flow; pass via `ClientSession(trace_configs=[...])` (list; disabled by default).

```python
async def on_request_start(session, trace_config_ctx, params):
    print("Starting request")

trace_config = aiohttp.TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)
async with aiohttp.ClientSession(trace_configs=[trace_config]) as client:
    ...
```

- Signal handlers receive `(session, trace_config_ctx, params)`; `trace_config_ctx` is a per-request `SimpleNamespace` (shared across signals of the same `TraceConfig` instance).
- `trace_config.trace_config_ctx_factory` replaces the ctx factory; per-request `trace_request_ctx={...}` (accepted by all HTTP verbs) is passed to that factory.
- Documented signals include `on_request_start`, `on_request_chunk_sent`, `on_request_exception`, `on_request_end`, `on_response_chunk_received` (see `docs/tracing_reference.rst` for the full list).

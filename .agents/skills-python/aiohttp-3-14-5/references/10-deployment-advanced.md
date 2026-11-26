# Deployment and Advanced Topics

Source: `docs/web_advanced.rst`, `docs/deployment.rst`, `aiohttp/web_app.py`, `examples/background_tasks.py`.

## TOC

- Running the app
- Graceful shutdown
- Background tasks
- Behind a reverse proxy
- Gunicorn
- Third-party ecosystem
- Performance knobs

## Running the app

- `web.run_app(app, host, port, ...)` — simple blocking runner (default host/port `localhost:8080`). Accepts an app instance or an async factory coroutine.
- `AppRunner` + sites for async control and multiple endpoints:

```python
runner = web.AppRunner(app)
await runner.setup()
await web.TCPSite(runner, "localhost", 8080).start()
await web.TCPSite(runner, "0.0.0.0", 9090).start()
# sites: web.TCPSite, web.UnixSite
await runner.cleanup()   # performs the graceful shutdown steps below (minus final task cancel)
```

`TCPSite.port` (3.14) reports the bound port (useful with dynamic port allocation, port 0).

## Graceful shutdown

`run_app` / `AppRunner.cleanup()` sequence:

1. Stop each site listening (new connections rejected).
2. Close idle keep-alive connections; active ones close on completion.
3. Fire `Application.on_shutdown` — close long-lived connections (websockets) here.
4. Wait briefly for running handlers to finish (bounded by `shutdown_timeout`).
5. Close remaining connections and cancel their handlers.
6. Fire `Application.on_cleanup` — dispose DB engines, complete cleanup contexts.
7. Cancel any remaining tasks and wait for them.

Keep a registry of open websockets in `app[...]` and close them from `on_shutdown` (see [04-websockets](04-websockets.md)).

## Background tasks

Long-running work (queue listeners, etc.) belongs in `cleanup_ctx` so it starts and dies with the app:

```python
@contextlib.asynccontextmanager
async def background_tasks(app):
    app[listener_key] = asyncio.create_task(listen_to_redis(app))
    yield
    app[listener_key].cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await app[listener_key]

app.cleanup_ctx.append(background_tasks)
```

(`examples/background_tasks.py` demonstrates a Redis/Valkey listener broadcasting to websockets.) Rules: do not use bare `asyncio.create_task` fire-and-forget — track and await/cancel the task, or use `aiojobs`. To run a handler immune to client-disconnect cancellation (with `handler_cancellation=True`), wrap the critical section in `aiojobs.aiohttp.shield(request, coro)` or mark the handler with `aiojobs.aiohttp.atomic`.

## Behind a reverse proxy

Deploy behind nginx/CDN in production. Behind a proxy, `request.scheme`, `request.host`, `request.remote` are the proxy's values. aiohttp deliberately ignores `Forwarded`/`X-Forwarded-*` headers by default (clients could spoof them) — apply them yourself in middleware in tight conjunction with your proxy config (e.g. only from trusted addresses); `aiohttp-remotes` provides secure helpers. Use `BaseRequest.clone(...)` inside the middleware to change `scheme`/`host`/`remote`/`client_max_size`/`client_max_fields`.

## Gunicorn

For multi-process serving, Gunicorn with the aiohttp worker class. The factory takes zero parameters:

```python
async def my_web_app():
    app = web.Application()
    app.router.add_get("/", index)
    return app
```

```shell
$ gunicorn my_app_module:my_web_app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker
```

## Third-party ecosystem

From `docs/third_party.rst` (aio-libs maintained):

- `aiohttp-session` — user sessions (EncryptedCookieStorage etc.)
- `aiohttp-jinja2` — Jinja2 templates (`setup(app, loader=...)`, `@aiohttp_jinja2.template(...)` — apply **before** route decorators)
- `aiohttp-mako` — Mako templates
- `aiohttp-cors` — CORS support
- `aiohttp-debugtoolbar` — debug toolbar (`aiohttp_debugtoolbar.setup(app)`)
- `aiohttp-devtools` — dev server with auto-reload (`adev runserver`)
- `aiohttp-sse` — server-sent events
- `pytest-aiohttp` — pytest fixtures
- `aiozipkin` — Zipkin tracing
- `aiocache`, `aiopg`, `aiomysql`, `aioredis`, `aiodocker`, `aiobotocore` — storage/drivers
- `uvloop` — faster event loop; `asyncpg` — async PostgreSQL

Also referenced in the docs: `aiojobs` (background jobs, `shield`/`atomic` for handlers), `aiodns` (async DNS for `AsyncResolver`), `sockjs` (SockJS-compatible servers), `orjson` (fast JSON via `json_serialize_bytes`), `certifi` (CA bundle), `aiohttp-remotes` (trusted-proxy headers).

## Performance knobs

- `TCPConnector(limit=..., limit_per_host=..., ttl_dns_cache=...)` — pool and DNS tuning (see [05-connectors-timeouts-ssl](05-connectors-timeouts-ssl.md)).
- `ClientSession(auto_decompress=True)` — automatic gzip/deflate (brotli if `Brotli`/`brotlicffi` installed, zstd if `backports.zstd` or Python ≥ 3.14).
- `StreamResponse(zlib_executor_size=..., zlib_executor=...)` — server-side zlib compression; chunks up to `zlib_executor_size` (default `MAX_SYNC_CHUNK_SIZE`) are compressed synchronously, larger ones in an executor (3.14 changed the default so compressed payloads are async by default). `set_zlib_backend()` swaps the zlib implementation globally.
- `Application(handler_args={"timeout_ceil_threshold": 1})` — per-app timeout ceiling threshold.
- `resp.json()`/`resp.text()` read whole bodies; stream with `resp.content.iter_chunked()` for large payloads.
- `client_max_size` / `client_max_fields` cap request memory (3.14.4).

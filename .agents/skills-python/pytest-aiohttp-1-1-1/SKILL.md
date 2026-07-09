---
name: pytest-aiohttp-1-1-1
description: >
  Integration testing for aiohttp web applications via pytest fixtures.
  Provides aiohttp_client (TestClient factory), aiohttp_server (TestServer factory),
  aiohttp_raw_server (RawTestServer factory), and aiohttp_client_cls for custom client classes.
  Use when testing aiohttp routes, middleware, websockets, streaming responses, or any
  aiohttp-based HTTP server. Requires pytest-asyncio with asyncio_mode = auto (or strict
  with explicit @pytest.mark.asyncio). Covers pytest-aiohttp 1.1.1 (Python 3.10+, aiohttp 3.10+).
---

# pytest-aiohttp 1.1.1

pytest-aiohttp is a pytest plugin that provides fixtures for creating aiohttp test servers and clients. It sits between pytest-asyncio (event loop management) and aiohttp's own `test_utils` module, offering clean resource lifecycle management. This skill covers version **1.1.1** (Python 3.10+, aiohttp 3.10+).

## Overview

The plugin provides four fixtures:

- **`aiohttp_client`** — Async factory that creates a `TestClient` from an `Application` or `BaseTestServer`. Handles server startup and automatic cleanup.
- **`aiohttp_server`** — Async factory that creates a `TestServer` from an `Application`. Exposes the server's host/port for direct HTTP access (e.g., via `aiohttp.ClientSession` or `requests`).
- **`aiohttp_raw_server`** — Async factory that creates a `RawTestServer` from a raw request handler. Useful for low-level protocol testing.
- **`aiohttp_client_cls`** — Override point to supply a custom `TestClient` subclass (e.g., with helper methods like `login()`).

All fixtures manage cleanup automatically — servers and clients are closed after the test completes, even on failure. The `aiohttp_client` fixture supports both `Application` and pre-created `BaseTestServer`/`RawTestServer` instances, enabling composition patterns.

## Usage

### Basic test with aiohttp_client

```python
from aiohttp import web


async def hello(request):
    return web.Response(text="Hello, world")


def create_app():
    app = web.Application()
    app.router.add_get("/", hello)
    return app


async def test_hello(aiohttp_client):
    client = await aiohttp_client(create_app())
    resp = await client.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert "Hello, world" in text
```

### Passing an async factory

```python
async def create_app():
    app = web.Application()
    app.router.add_get("/", hello)
    return app


async def test_hello(aiohttp_client):
    client = await aiohttp_client(await create_app())
    resp = await client.get("/")
    assert resp.status == 200
```

### Using aiohttp_server for direct URL access

```python
async def test_with_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/", hello)
    server = await aiohttp_server(app)
    # server.make_url("/") gives the full URL
    assert server.port > 0
```

### Custom port via server_kwargs

```python
async def test_custom_port(aiohttp_client, unused_tcp_port):
    client = await aiohttp_client(
        create_app(),
        server_kwargs={"port": unused_tcp_port},
    )
    assert client.port == unused_tcp_port
```

### Composing aiohttp_raw_server with aiohttp_client

```python
async def handler(request):
    return web.Response(text="OK")


@pytest.fixture
async def raw_server(aiohttp_raw_server):
    return await aiohttp_raw_server(handler)


@pytest.fixture
async def client(aiohttp_client, raw_server):
    return await aiohttp_client(raw_server)


async def test_raw(cli):
    resp = await cli.get("/")
    assert resp.status == 200
```

### Custom TestClient subclass

```python
class MyClient(TestClient):
    async def login(self, *, user, pw):
        return await self.post("/login", json={"user": user, "pw": pw})


@pytest.fixture
def aiohttp_client_cls():
    return MyClient


async def test_login(aiohttp_client):
    client = await aiohttp_client(create_app())
    await client.login(user="admin", pw="secret")
```

### Marker-based client selection

```python
@pytest.fixture
def aiohttp_client_cls(request):
    if request.node.get_closest_marker("rest"):
        return RESTfulClient
    if request.node.get_closest_marker("graphql"):
        return GraphQLClient
    return TestClient


@pytest.mark.rest
async def test_rest(aiohttp_client):
    client = await aiohttp_client(app)
    assert isinstance(client, RESTfulClient)
```

### pytest configuration

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

The plugin auto-switches from `asyncio_mode = legacy` to `auto` with a deprecation warning. Both `auto` and `strict` modes are supported.

## Gotchas

- **`aiohttp_client` is a factory, not a client.** You must `await` it: `client = await aiohttp_client(app)`, not `client = aiohttp_client(app)`. Forgetting the `await` produces a coroutine object, not a `TestClient`.
- **`server_kwargs` vs session kwargs.** The `aiohttp_client` factory accepts `server_kwargs` (passed to `TestServer`) and `**kwargs` (passed to `TestClient`/`ClientSession`). Port, host, and SSL go in `server_kwargs`; auth, headers, and timeout go in session kwargs.
- **`aiohttp_client` accepts both Application and BaseTestServer.** When passed an `Application`, it creates a `TestServer` internally. When passed a `BaseTestServer` (from `aiohttp_server`) or `RawTestServer`, it wraps that existing server. This enables the composition pattern in the Usage section.
- **Multiple clients from one factory are independent.** Calling `await aiohttp_client(app)` twice creates two separate `TestClient` instances, each with its own session. Both are auto-cleaned.
- **`aiohttp_server` returns `TestServer`, not `TestClient`.** It gives you the server's host/port but no client. Use `aiohttp_client` for making requests, or `aiohttp_server` + `aiohttp_client(server)` for direct URL access.
- **`aiohttp_raw_server` takes a handler, not an app.** The handler is a `_RequestHandler` (the low-level protocol handler), not an `Application`. Use `aiohttp_server` for app-level testing and `aiohttp_raw_server` only for protocol-level testing.
- **Legacy asyncio_mode is auto-switched to auto.** If your config has `asyncio_mode = legacy` (or no mode set), pytest-aiohttp silently switches to `auto` and emits a `DeprecationWarning`. Set `asyncio_mode = auto` or `asyncio_mode = strict` explicitly.
- **`aiohttp_client_cls` must return a class, not an instance.** The fixture expects `Type[TestClient]`, so return the class itself (`return MyClient`), not `return MyClient()`.
- **TestClient responses are `aiohttp.ClientResponse`, not `web.Response`.** Use `.status`, `.text()`, `.json()`, `.read()` — the same API as `aiohttp.ClientSession` responses.
- **`server_kwargs` port conflicts.** If you set a fixed port in `server_kwargs`, parallel test runs may collide. Use `unused_tcp_port` fixture for dynamic port allocation.
- **WebSocket testing uses TestClient.ws_connect().** The `TestClient` provides `ws_connect()` for WebSocket endpoint testing, same as `ClientSession`.

## References

- [01-fixtures-api](references/01-fixtures-api.md) — Full fixture reference: signatures, return types, Protocol classes, cleanup behavior
- [02-client-patterns](references/02-client-patterns.md) — TestClient usage patterns: requests, sessions, cookies, auth, timeouts, streaming
- [03-server-patterns](references/03-server-patterns.md) — TestServer and RawTestServer patterns: host/port, URL construction, direct HTTP access
- [04-custom-clients](references/04-custom-clients.md) — aiohttp_client_cls override: subclassing TestClient, marker-based selection, helper methods
- [05-asyncio-modes](references/05-asyncio-modes.md) — asyncio_mode configuration: auto vs strict vs legacy, auto-switch behavior, migration
- [06-advanced-patterns](references/06-advanced-patterns.md) — Composition patterns, multiple servers, websocket testing, middleware testing, fixture chaining

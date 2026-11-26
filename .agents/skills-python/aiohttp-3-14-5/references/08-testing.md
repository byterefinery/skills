# Testing

Source: `docs/testing.rst`, `aiohttp/test_utils.py`.

## TOC

- Install / pytest setup
- pytest-aiohttp fixtures
- Framework-agnostic utilities
- unittest
- Mocked requests

## Install / pytest setup

Install the separate pytest plugin (the bundled `aiohttp.pytest_plugin` is deprecated in 3.14):

```shell
$ pip install pytest-aiohttp
```

Run with `--asyncio-mode=auto` or set `asyncio_mode = auto` in pytest config. Alternatively (without the package) add `pytest_plugins = 'aiohttp.pytest_plugin'` to `conftest.py`.

## pytest-aiohttp fixtures

`aiohttp_client(app | server | raw_server, **kwargs)` — factory returning a `TestClient` for the target:

```python
from aiohttp import web

async def hello(request):
    return web.Response(text='Hello, world')

async def test_hello(aiohttp_client):
    app = web.Application()
    app.router.add_get('/', hello)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert 'Hello, world' in text
```

Common pattern — a fixture building an app client:

```python
@pytest.fixture
async def cli(aiohttp_client):
    app = web.Application()
    app.router.add_get('/', previous)
    return await aiohttp_client(app)
```

Other fixtures:

- `aiohttp_server(app, *, port=None, **kwargs)` — factory creating a `TestServer` (kwargs go to `Application.make_handler`).
- `aiohttp_raw_server(handler, *, port=None, **kwargs)` — factory creating a `RawTestServer` from a bare handler.
- `aiohttp_unused_port()` — returns a free IPv4 TCP port.

`TestClient` proxies `ClientSession` operations (`client.get/post/ws_connect/...`) and exposes `client.server.app` to inspect app state. Clients and responses are cleaned up after each test.

## Framework-agnostic utilities

For non-pytest frameworks, use the raw utilities:

- `TestServer` — runs an `Application`-based server; `RawTestServer` runs a low-level `web.Server`.
- `TestClient` — wraps a `ClientSession` bound to a `TestServer`; `await client.start_server()` / `await client.close()`.
- `AioHTTPTestCase` (below).

## unittest

`AioHTTPTestCase` (extends `unittest.IsolatedAsyncioTestCase`): override `async def get_application()` to return the app; then use `self.client`, `self.server`, `self.app`.

```python
from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web

class MyAppTestCase(AioHTTPTestCase):
    async def get_application(self):
        async def hello(request):
            return web.Response(text='Hello, world')
        app = web.Application()
        app.router.add_get('/', hello)
        return app

    async def test_example(self):
        async with self.client.request("GET", "/") as resp:
            self.assertEqual(resp.status, 200)
```

`asyncSetUp`/`asyncTearDown` may be overridden (must call `await super().asyncSetUp()` since 3.8).

## Mocked requests

`make_mocked_request(method, path, headers=None, ...)` builds a fake `web.Request` for unit tests where a full server is overkill (e.g. emulating hard-to-reproduce conditions):

```python
from aiohttp.test_utils import make_mocked_request

def handler(request):
    assert request.headers.get('token') == 'x'
    return web.Response(body=b'data')

req = make_mocked_request('GET', '/', headers={'token': 'x'})
resp = handler(req)
```

Prefer real networking via `TestClient` for business-logic tests; use mocks only for exotic conditions.

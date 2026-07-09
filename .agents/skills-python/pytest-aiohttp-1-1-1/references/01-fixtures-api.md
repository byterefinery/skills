# Fixtures API Reference

## aiohttp_client

**Signature:** `async def aiohttp_client() -> AsyncIterator[AiohttpClient]`

An async fixture factory. Returns a callable that creates `TestClient` instances.

### Call forms

```python
# From an Application — creates TestServer + TestClient
client = await aiohttp_client(app, server_kwargs={"host": "0.0.0.0"}, timeout=10)

# From a pre-created TestServer
server = await aiohttp_server(app)
client = await aiohttp_client(server)

# From a pre-created RawTestServer
raw = await aiohttp_raw_server(handler)
client = await aiohttp_client(raw)
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `__param` | `Application \| BaseTestServer` | The app or server to test |
| `server_kwargs` | `Mapping[str, Any] \| None` | Extra kwargs forwarded to `TestServer()` (e.g., `host`, `port`, `ssl_context`) |
| `**kwargs` | `Any` | Extra kwargs forwarded to `TestClient` / `ClientSession` (e.g., `timeout`, `cookies`, `auth`) |

### Return type

- `TestClient[Request, Application]` when passed an `Application`
- `TestClient[_Request, None]` when passed a `BaseTestServer`

### Cleanup

All clients created through the factory are automatically closed when the test completes. The factory pops clients from an internal list in LIFO order.

## aiohttp_server

**Signature:** `async def aiohttp_server() -> AsyncIterator[AiohttpServer]`

An async fixture factory. Returns a callable that creates `TestServer` instances.

### Call form

```python
server = await aiohttp_server(app, host="127.0.0.1", port=8080)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `app` | `Application` | — | The aiohttp application |
| `host` | `str` | `"127.0.0.1"` | Bind address |
| `port` | `int \| None` | `None` | Bind port (0 = auto-assign) |
| `**kwargs` | `Any` | — | Extra kwargs to `start_server()` |

### Return type

`TestServer` — provides `.host`, `.port`, `.make_url(path)`, and `.closed` property.

### Cleanup

All servers created through the factory are automatically closed when the test completes.

## aiohttp_raw_server

**Signature:** `async def aiohttp_raw_server() -> AsyncIterator[AiohttpRawServer]`

An async fixture factory. Returns a callable that creates `RawTestServer` instances.

### Call form

```python
raw_server = await aiohttp_raw_server(handler, port=8080)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `handler` | `_RequestHandler` | — | Low-level request handler |
| `port` | `int \| None` | `None` | Bind port (0 = auto-assign) |
| `**kwargs` | `Any` | — | Extra kwargs to `start_server()` |

### Return type

`RawTestServer` — provides `.host`, `.port`, `.make_url(path)`, and `.closed` property.

### Cleanup

All servers created through the factory are automatically closed when the test completes.

## aiohttp_client_cls

**Signature:** `def aiohttp_client_cls() -> Type[TestClient[Any, Any]]`

A regular (sync) fixture. Returns the `TestClient` class used by the `aiohttp_client` factory.

### Default

Returns `aiohttp.test_utils.TestClient`.

### Override

```python
@pytest.fixture
def aiohttp_client_cls():
    return MyCustomClient  # return the CLASS, not an instance
```

The custom class must be a subclass of `TestClient`. It receives the same initialization kwargs as the base class.

## Protocol types

The plugin exports three `Protocol` classes for type hints:

- `AiohttpClient` — The async callable returned by `aiohttp_client`
- `AiohttpServer` — The sync callable returned by `aiohttp_server`
- `AiohttpRawServer` — The sync callable returned by `aiohttp_raw_server`

Import from `pytest_aiohttp`:

```python
from pytest_aiohttp import AiohttpClient, AiohttpServer, AiohttpRawServer
```

## Fixture scope

All async fixtures (`aiohttp_client`, `aiohttp_server`, `aiohttp_raw_server`) use `pytest_asyncio.fixture` with default scope (function). The sync `aiohttp_client_cls` uses `@pytest.fixture` with default scope.

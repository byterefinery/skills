# Server Patterns

## TestServer basics

`aiohttp_server` creates a `TestServer` that binds to a real TCP socket. The server runs inside the test's event loop and is automatically shut down after the test.

```python
async def test_server(aiohttp_server):
    app = web.Application()
    app.router.add_get("/", handler)
    server = await aiohttp_server(app)

    assert isinstance(server.host, str)
    assert isinstance(server.port, int)
    assert server.port > 0
```

### Host and port

```python
# Default: localhost, auto port
server = await aiohttp_server(app)

# Custom host and port
server = await aiohttp_server(app, host="0.0.0.0", port=8888)

# Specific port via unused_tcp_port fixture
server = await aiohttp_server(app, port=unused_tcp_port)
```

### URL construction

```python
server = await aiohttp_server(app)

# Build full URLs
url = server.make_url("/api/users")
# → http://127.0.0.1:<port>/api/users

# Use with external HTTP clients
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        assert resp.status == 200
```

## Using TestServer with external clients

`aiohttp_server` is useful when you need to test with a real HTTP client (not `TestClient`):

```python
async def test_with_requests(aiohttp_server):
    app = web.Application()
    app.router.add_get("/", hello)
    server = await aiohttp_server(app)

    import requests
    url = server.make_url("/")
    resp = requests.get(url)
    assert resp.status_code == 200
```

This pattern is useful for:
- Testing with `requests` or `httpx` clients
- Testing reverse proxy configurations
- Testing client libraries that consume your API

## RawTestServer for low-level testing

`aiohttp_raw_server` creates a `RawTestServer` from a raw request handler. This bypasses the `Application`/`Router` layer and tests the protocol handler directly.

```python
from aiohttp.web_protocol import RequestHandler

async def handler(request):
    return web.Response(text="OK")

async def test_raw(aiohttp_raw_server):
    server = await aiohttp_raw_server(handler)
    # server.make_url("/") works the same as TestServer
```

Use `RawTestServer` when:
- Testing custom request handlers that don't use `Application`
- Testing protocol-level behavior (raw TCP, custom framing)
- Building middleware that operates at the handler level

## Composition: server + client

Chain `aiohttp_server` with `aiohttp_client` for full control:

```python
@pytest.fixture
async def test_server(aiohttp_server):
    app = create_app()
    return await aiohttp_server(app, host="127.0.0.1")

@pytest.fixture
async def test_client(aiohttp_client, test_server):
    return await aiohttp_client(test_server)

async def test_endpoint(test_client):
    resp = await test_client.get("/")
    assert resp.status == 200
```

This pattern separates server lifecycle from client lifecycle, allowing multiple clients against the same server.

## Multiple servers in one test

```python
async def test_two_services(aiohttp_server):
    server1 = await aiohttp_server(app1, port=8081)
    server2 = await aiohttp_server(app2, port=8082)

    # Both servers run simultaneously
    url1 = server1.make_url("/health")
    url2 = server2.make_url("/health")
    # ... test inter-service communication
```

Both servers are auto-cleaned when the test completes.

## Server state inspection

```python
server = await aiohttp_server(app)

# Check if server is running
assert not server.closed

# Access the underlying TCPServer
# (useful for advanced diagnostics)
```

## SSL/TLS testing

```python
import ssl

async def test_ssl(aiohttp_server):
    app = web.Application()
    app.router.add_get("/", hello)

    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.load_cert_chain("cert.pem", "key.pem")

    server = await aiohttp_server(
        app,
        # server_kwargs passed to start_server
    )
    # Use aiohttp_client with ssl context for the client side
```

## Server-side app state

```python
async def test_app_state(aiohttp_server):
    app = web.Application()
    app["db"] = {}  # app-level state
    app.router.add_get("/", handler)

    server = await aiohttp_server(app)
    # The app instance is accessible via server.app
    assert server.app["db"] == {}
```

## Cleanup guarantees

All servers created through `aiohttp_server` and `aiohttp_raw_server` are closed in LIFO order when the fixture tears down. This happens even if the test raises an exception or is interrupted.

```python
async def test_cleanup(aiohttp_server):
    server = await aiohttp_server(app)
    # Even if this raises, the server is closed
    raise RuntimeError("test failed")
```

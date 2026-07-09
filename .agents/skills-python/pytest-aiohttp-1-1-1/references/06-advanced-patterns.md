# Advanced Patterns

## Composition: chaining fixtures

Build layered fixtures for complex test setups:

```python
@pytest.fixture
async def app():
    app = web.Application()
    setup_routes(app)
    return app


@pytest.fixture
async def server(aiohttp_server, app):
    return await aiohttp_server(app)


@pytest.fixture
async def client(aiohttp_client, server):
    return await aiohttp_client(server)


async def test_endpoint(client):
    resp = await client.get("/")
    assert resp.status == 200
```

This pattern separates concerns: app creation, server lifecycle, and client creation are each independently testable.

## Multiple clients against one server

```python
@pytest.fixture
async def shared_server(aiohttp_server):
    app = create_app()
    return await aiohttp_server(app)


async def test_concurrent_clients(aiohttp_client, shared_server):
    client1 = await aiohttp_client(shared_server)
    client2 = await aiohttp_client(shared_server)

    # Both clients share the same server
    resp1 = await client1.get("/resource")
    resp2 = await client2.get("/resource")

    assert resp1.status == 200
    assert resp2.status == 200
```

Both clients are auto-cleaned when the test completes.

## Middleware testing

```python
async def timing_middleware(app, handler):
    async def middleware_handler(request):
        start = time.time()
        resp = await handler(request)
        elapsed = time.time() - start
        resp.headers["X-Response-Time"] = str(elapsed)
        return resp
    return middleware_handler


async def test_middleware(aiohttp_client):
    app = web.Application(middlewares=[timing_middleware])
    app.router.add_get("/", hello)
    client = await aiohttp_client(app)

    resp = await client.get("/")
    assert "X-Response-Time" in resp.headers
    assert float(resp.headers["X-Response-Time"]) >= 0
```

## WebSocket testing

```python
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        await ws.send_text(f"echo: {msg.data}")
    return ws


async def test_websocket(aiohttp_client):
    app = web.Application()
    app.router.add_get("/ws", websocket_handler)
    client = await aiohttp_client(app)

    async with client.ws_connect("/ws") as ws:
        await ws.send_text("hello")
        resp = await ws.receive_text()
        assert resp == "echo: hello"
```

## Testing streaming responses

```python
async def streaming_handler(request):
    return web.StreamResponse()


async def test_streaming(aiohttp_client):
    app = web.Application()
    app.router.add_get("/stream", streaming_handler)
    client = await aiohttp_client(app)

    async with client.get("/stream") as resp:
        assert resp.status == 200
        chunks = []
        async for chunk in resp.content.iter_chunked(1024):
            chunks.append(chunk)
```

## Fixture chaining with raw servers

```python
@pytest.fixture
async def raw_handler():
    async def handler(request):
        return web.Response(text="Raw OK")
    return handler


@pytest.fixture
async def raw_server(aiohttp_raw_server, raw_handler):
    return await aiohttp_raw_server(raw_handler)


@pytest.fixture
async def raw_client(aiohttp_client, raw_server):
    return await aiohttp_client(raw_server)


async def test_raw_endpoint(raw_client):
    resp = await raw_client.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert "Raw OK" in text
```

## Testing with database fixtures

```python
@pytest.fixture
async def db_pool():
    pool = await create_db_pool(dsn="postgresql://...")
    yield pool
    await pool.close()


@pytest.fixture
async def app_with_db(db_pool):
    app = web.Application()
    app["db"] = db_pool
    setup_routes(app)
    return app


async def test_db_endpoint(aiohttp_client, app_with_db):
    client = await aiohttp_client(app_with_db)
    resp = await client.get("/items")
    assert resp.status == 200
    items = await resp.json()
    assert isinstance(items, list)
```

## Parameterized tests with aiohttp_client

```python
@pytest.mark.parametrize("method, path, expected_status", [
    ("GET", "/users", 200),
    ("POST", "/users", 201),
    ("GET", "/users/999", 404),
    ("DELETE", "/users/1", 204),
])
async def test_routes(aiohttp_client, method, path, expected_status):
    client = await aiohttp_client(create_app())
    resp = await client.request(method, path)
    assert resp.status == expected_status
```

## Testing error handlers

```python
async def not_found_handler(request):
    return web.json_response({"error": "Not found"}, status=404)


async def test_404(aiohttp_client):
    app = web.Application()
    app.router.add_get("/", hello)
    app.router.add_route("*", "/{path:.*}", not_found_handler)
    client = await aiohttp_client(app)

    resp = await client.get("/nonexistent")
    assert resp.status == 404
    data = await resp.json()
    assert data["error"] == "Not found"
```

## Testing CORS

```python
async def test_cors(aiohttp_client):
    app = web.Application()
    app.router.add_get("/data", data_handler)
    client = await aiohttp_client(app)

    resp = await client.get(
        "/data",
        headers={"Origin": "https://example.com"},
    )
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
```

## Session and state testing

```python
async def test_session(aiohttp_client):
    client = await aiohttp_client(app)

    # Set session data
    resp = await client.post("/login", json={"user": "admin"})
    assert resp.status == 200

    # Session cookies persist
    resp = await client.get("/admin")
    assert resp.status == 200

    # Logout
    resp = await client.post("/logout")
    assert resp.status == 200

    # Session cleared
    resp = await client.get("/admin")
    assert resp.status == 401
```

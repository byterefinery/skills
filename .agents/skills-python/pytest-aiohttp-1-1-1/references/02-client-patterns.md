# Client Patterns

## Making HTTP requests

`TestClient` wraps `aiohttp.ClientSession` and provides the same request methods:

```python
client = await aiohttp_client(app)

# GET
resp = await client.get("/users/123")

# POST with JSON
resp = await client.post("/users", json={"name": "Alice"})

# POST with form data
resp = await client.post("/upload", data={"file": open("data.csv")})

# PUT, DELETE, PATCH
resp = await client.put("/users/123", json={"name": "Bob"})
resp = await client.delete("/users/123")
resp = await client.patch("/users/123", json={"name": "Charlie"})

# HEAD
resp = await client.head("/users/123")

# OPTIONS
resp = await client.options("/users")
```

All methods accept `params` (query string), `headers`, `cookies`, `auth`, `timeout`, and other `ClientSession` kwargs.

## Reading responses

`TestClient` responses are `aiohttp.ClientResponse` objects:

```python
resp = await client.get("/users/123")

# Status code
assert resp.status == 200

# Text body
text = await resp.text()

# JSON body
data = await resp.json()

# Raw bytes
body = await resp.read()

# Headers
content_type = resp.headers.get("Content-Type")

# Content-Type convenience
assert resp.content_type == "application/json"
```

## Query parameters

```python
# Via params dict
resp = await client.get("/search", params={"q": "hello", "page": 1})

# Via URL string
resp = await client.get("/search?q=hello&page=1")
```

## Headers

```python
resp = await client.get(
    "/users",
    headers={"Authorization": "Bearer token123", "Accept": "application/json"},
)
```

## Cookies

```python
# Client-side cookies persist across requests
client = await aiohttp_client(app)
resp = await client.get("/set-cookie")
# Cookies from response are stored in client's jar

resp = await client.get("/read-cookie")  # cookies sent automatically

# Explicit cookies
resp = await client.get("/path", cookies={"session": "abc123"})
```

## Authentication

```python
from aiohttp import BasicAuth

# Basic auth via auth parameter
client = await aiohttp_client(app, auth=BasicAuth("user", "pass"))

# Bearer token via headers
client = await aiohttp_client(
    app,
    headers={"Authorization": "Bearer token123"},
)
```

Auth set in the factory applies to all requests through that client.

## Timeouts

```python
# Per-request timeout
resp = await client.get("/slow", timeout=5.0)

# Client-wide timeout (via ClientSession kwargs)
from aiohttp import ClientTimeout
client = await aiohttp_client(app, timeout=ClientTimeout(total=30))
```

## Streaming responses

```python
async with client.get("/large-file") as resp:
    assert resp.status == 200
    async for chunk in resp.content.iter_chunked(1024):
        process(chunk)
```

## JSON responses with content negotiation

```python
# Server returns JSON by default when Accept header is set
resp = await client.get("/data", headers={"Accept": "application/json"})
data = await resp.json()
```

## Redirects

By default, `TestClient` follows redirects automatically. To disable:

```python
resp = await client.get("/redirect", allow_redirects=False)
assert resp.status == 302
assert resp.headers["Location"] == "/final"
```

## Error handling

```python
# Check status directly
resp = await client.get("/missing")
assert resp.status == 404

# Use raises for client errors
resp = await client.get("/error")
assert resp.status >= 400
```

`TestClient` does not raise on HTTP error status codes — the response is always returned. Check `resp.status` or use `resp.raise_for_status()` manually.

## Server URL access

```python
client = await aiohttp_client(app)

# Full URL construction
url = client.make_url("/path")  # e.g., http://127.0.0.1:8080/path

# Server host and port
host = client.host
port = client.port
```

## Multiple requests in one test

```python
async def test_workflow(aiohttp_client):
    client = await aiohttp_client(app)

    # Create resource
    resp = await client.post("/items", json={"name": "Item 1"})
    item_id = (await resp.json())["id"]

    # Read resource
    resp = await client.get(f"/items/{item_id}")
    assert resp.status == 200

    # Update resource
    resp = await client.put(f"/items/{item_id}", json={"name": "Updated"})
    assert resp.status == 200

    # Delete resource
    resp = await client.delete(f"/items/{item_id}")
    assert resp.status == 204

    # Verify deletion
    resp = await client.get(f"/items/{item_id}")
    assert resp.status == 404
```

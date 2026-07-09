# Custom Clients

## Basic subclassing

Override `aiohttp_client_cls` to inject a custom `TestClient` subclass:

```python
from aiohttp.test_utils import TestClient


class MyClient(TestClient):
    async def login(self, username: str, password: str) -> "MyClient":
        resp = await self.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        resp.raise_for_status()
        return self


@pytest.fixture
def aiohttp_client_cls():
    return MyClient


async def test_login(aiohttp_client):
    client = await aiohttp_client(app)
    await client.login("admin", "secret")
    resp = await client.get("/admin")
    assert resp.status == 200
```

The custom class must be a subclass of `TestClient`. It receives the same `server` and `**kwargs` as the base class constructor.

## Marker-based client selection

Select different client classes based on test markers:

```python
class RESTfulClient(TestClient):
    async def get_json(self, path: str):
        resp = await self.get(path, headers={"Accept": "application/json"})
        return await resp.json()


class GraphQLClient(TestClient):
    async def query(self, query: str, variables=None):
        return await self.post(
            "/graphql",
            json={"query": query, "variables": variables or {}},
        )


@pytest.fixture
def aiohttp_client_cls(request):
    if request.node.get_closest_marker("rest"):
        return RESTfulClient
    if request.node.get_closest_marker("graphql"):
        return GraphQLClient
    return TestClient


@pytest.mark.rest
async def test_rest_endpoint(aiohttp_client):
    client = await aiohttp_client(app)
    data = await client.get_json("/users")
    assert data["count"] > 0


@pytest.mark.graphql
async def test_graphql_query(aiohttp_client):
    client = await aiohttp_client(app)
    resp = await client.query("{ users { id name } }")
    assert resp.status == 200
```

Markers are defined in `conftest.py`:

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "rest: RESTful API tests")
    config.addinivalue_line("markers", "graphql: GraphQL API tests")
```

## Client with pre-configured headers

```python
class AuthenticatedClient(TestClient):
    def __init__(self, *args, token: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._token = token

    async def _request(self, method, str_or_url, **kwargs):
        kwargs.setdefault("headers", {})
        kwargs["headers"]["Authorization"] = f"Bearer {self._token}"
        return await super()._request(method, str_or_url, **kwargs)
```

Or simpler — pass headers through the factory:

```python
client = await aiohttp_client(
    app,
    headers={"Authorization": "Bearer token123"},
)
```

## Type-safe client with Protocol

```python
from typing import Protocol


class TypedClient(Protocol):
    async def get_users(self) -> list[dict]: ...
    async def create_user(self, name: str) -> dict: ...


class TypedTestClient(TestClient):
    async def get_users(self) -> list[dict]:
        resp = await self.get("/users")
        return await resp.json()

    async def create_user(self, name: str) -> dict:
        resp = await self.post("/users", json={"name": name})
        return await resp.json()


@pytest.fixture
def aiohttp_client_cls():
    return TypedTestClient
```

## Per-test client override

Override `aiohttp_client_cls` at the test level for one-off custom clients:

```python
async def test_with_custom_client(aiohttp_client, aiohttp_client_cls):
    # aiohttp_client_cls is already injected; override in a sub-fixture
    ...
```

For one-off cases, prefer the factory kwargs approach:

```python
async def test_specific_headers(aiohttp_client):
    client = await aiohttp_client(
        app,
        headers={"X-Custom-Header": "value"},
    )
```

## Multiple client classes in same test file

```python
@pytest.fixture
def admin_client_cls():
    class AdminClient(TestClient):
        async def as_admin(self):
            resp = await self.post("/auth", json={"role": "admin"})
            return await resp.json()
    return AdminClient


@pytest.fixture
def user_client_cls():
    class UserClient(TestClient):
        async def as_user(self, username):
            resp = await self.post("/auth", json={"username": username})
            return await resp.json()
    return UserClient


# Use the default aiohttp_client_cls fixture for standard tests
# Override with specific fixtures when needed
```

## Important notes

- **Return the class, not an instance.** `aiohttp_client_cls` must return `MyClient`, not `MyClient()`.
- **The class is reused.** The same class is used for every `await aiohttp_client(app)` call within the test scope.
- **Inheritance chain matters.** Your custom class must be a subclass of `TestClient`. The factory passes `server` and `**kwargs` to the constructor, so ensure compatibility.
- **Session kwargs flow through.** Kwargs passed to `aiohttp_client()` after `server_kwargs` are forwarded to both `TestClient` and `ClientSession`.

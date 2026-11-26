# Async Fixtures Reference

## `@pytest_asyncio.fixture`

Declares a coroutine or async generator as a pytest fixture that runs inside an asyncio event loop. Accepts all standard `@pytest.fixture` arguments plus `loop_scope`.

### Basic async fixture (coroutine)

```python
import pytest_asyncio

@pytest_asyncio.fixture
async def http_client():
    client = await create_http_client()
    return client
```

The fixture's coroutine is awaited during setup. The returned value is injected into tests. No teardown logic — use an async generator for that.

### Async generator fixture (with teardown)

```python
@pytest_asyncio.fixture
async def database():
    db = await connect_db()
    yield db
    await db.close()
```

Code before `yield` runs during setup; code after `yield` runs during teardown. The teardown executes in the same event loop as setup.

### Decorator forms

```python
# As decorator with arguments
@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def module_db():
    ...

# As decorator without arguments
@pytest_asyncio.fixture
async def per_test_resource():
    ...
```

### Documented loop_scope/scope combinations

From the official docs (`@pytest_asyncio.fixture` reference):

```python
# Function scope, function loop (default) — fresh loop for every test
@pytest_asyncio.fixture
async def fixture_runs_in_fresh_loop_for_every_function(): ...

# Module-scoped fixture running in the session loop
@pytest_asyncio.fixture(loop_scope="session", scope="module")
async def fixture_runs_in_session_loop_once_per_module(): ...

# Module-scoped fixture running in the module loop
@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def fixture_runs_in_module_loop_once_per_module(): ...

# Function-scoped fixture running in the module loop
# (re-evaluated each test, but always inside the same module loop)
@pytest_asyncio.fixture(loop_scope="module")
async def fixture_runs_in_module_loop_once_per_function(): ...
```

## `loop_scope` vs `scope`

These control different aspects:

| Argument | Controls | Default |
|----------|----------|---------|
| `scope` | Caching lifetime (how often the fixture is recreated) | `function` |
| `loop_scope` | Which event loop runs the fixture | From config, then the fixture's own `scope` |

**Rule: the event loop scope must be larger than or the same as the fixture's caching `scope`.** It is possible to re-evaluate an async fixture multiple times within the same event loop, but not to switch out the running event loop under an async fixture.

### Invalid combinations (will fail)

```python
# ERROR: function-scoped loop cannot hold a module-scoped fixture
@pytest_asyncio.fixture(scope="module", loop_scope="function")
async def impossible_fixture():
    ...
```

The fixture would be cached across tests, but its event loop would be destroyed after the first test.

## Default `loop_scope` for Fixtures

The effective loop scope for an async fixture is resolved in this order:

1. The fixture's explicit `loop_scope` argument (if given)
2. The `asyncio_default_fixture_loop_scope` config option — including the special value `"fixture-scope"` (new in 1.5.0), which resolves to the fixture's own `scope`
3. If the option is unset: the fixture's own `scope` (deprecated behavior, triggers a `PytestDeprecationWarning`)

Set the option explicitly to silence the deprecation warning:

```toml
# Function loop for every fixture (future default, recommended)
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
```

```toml
# Or, new in 1.5.0, make each fixture use a loop matching its own scope
# (explicitly preserves the unset-option behavior of pytest-asyncio 1.x)
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "fixture-scope"
```

## Strict vs Auto Mode for Fixtures

### Strict mode

```python
import pytest_asyncio

# REQUIRED: use @pytest_asyncio.fixture for async fixtures
@pytest_asyncio.fixture
async def my_resource():
    ...

# Using @pytest.fixture on an async function triggers a deprecation warning
# when requested by an asyncio test (will become an error in a future version)
@pytest.fixture
async def will_warn():  # DON'T DO THIS in strict mode
    ...
```

### Auto mode

```python
import pytest

# Both work in auto mode
@pytest_asyncio.fixture
async def explicit_asyncio_fixture():
    ...

@pytest.fixture
async def implicit_asyncio_fixture():
    # Automatically handled by pytest-asyncio in auto mode
    ...
```

## Async Fixtures as Class Methods

```python
class TestSuite:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_test(self):
        self.resource = await create_resource()
        yield
        await cleanup_resource(self.resource)

    @pytest.mark.asyncio
    async def test_with_setup(self):
        assert self.resource is not None
```

Class-level fixtures with matching loop scope:

```python
@pytest.mark.asyncio(loop_scope="class")
class TestClassScopedLoop:
    loop: asyncio.AbstractEventLoop

    @pytest_asyncio.fixture(loop_scope="class")
    async def my_fixture(self):
        TestClassScopedLoop.loop = asyncio.get_running_loop()

    async def test_runs_is_same_loop_as_fixture(self, my_fixture):
        assert asyncio.get_running_loop() is TestClassScopedLoop.loop
```

## Nested Async Fixtures

Async fixtures can depend on other async fixtures:

```python
@pytest_asyncio.fixture
async def connection():
    conn = await connect()
    yield conn
    await conn.close()

@pytest_asyncio.fixture
async def repository(connection):
    # 'connection' is already set up when this runs
    repo = Repository(connection)
    return repo

@pytest.mark.asyncio
async def test_with_repo(repository):
    result = await repository.fetch()
    assert result
```

Fixture teardown runs in reverse dependency order: `repository` first, then `connection`.

## Context Variables (`contextvars`)

pytest-asyncio applies context variable changes made by async fixtures to the requesting context, and restores them during fixture teardown:

```python
from contextvars import ContextVar
import pytest_asyncio

_request_id = ContextVar("request_id")

@pytest_asyncio.fixture
async def set_request_context():
    _request_id.set("abc-123")
    yield

@pytest.mark.asyncio
async def test_sees_context(set_request_context):
    assert _request_id.get() == "abc-123"
```

### Contextvar isolation between tests

Changes to contextvars in one async test do not leak into another, even at module/session scope:

```python
@pytest.mark.asyncio(loop_scope="module")
async def test_sets_var():
    _my_var.set("value")  # This is isolated

@pytest.mark.asyncio(loop_scope="module")
async def test_does_not_see_var():
    with pytest.raises(LookupError):
        _my_var.get()  # Not visible — isolated per test
```

### Sync-to-async contextvar propagation

Contextvars set in sync fixtures propagate to async fixtures and tests:

```python
@pytest.fixture
def sync_context():
    token = _ctx_var.set("from_sync")
    yield
    _ctx_var.reset(token)

@pytest_asyncio.fixture
async def async_check(sync_context):
    assert _ctx_var.get() == "from_sync"  # Works
```

## Parametrized Async Fixtures

```python
@pytest_asyncio.fixture(params=["sqlite", "postgres"])
async def db(request):
    if request.param == "sqlite":
        db = await create_sqlite_db()
    else:
        db = await create_postgres_db()
    yield db
    await db.close()

@pytest.mark.asyncio
async def test_with_db(db):
    # Runs once per parameter
    result = await db.query("SELECT 1")
    assert result
```

## Common Patterns

### Autouse session fixture for global setup

```python
@pytest_asyncio.fixture(autouse=True, scope="session", loop_scope="session")
async def global_setup():
    await initialize_system()
    yield
    await shutdown_system()
```

### Per-test cleanup with autouse

```python
@pytest_asyncio.fixture(autouse=True)
async def cleanup_temp_files():
    yield
    await remove_temp_files()
```

### Fixture providing the running loop

```python
import asyncio

@pytest_asyncio.fixture(loop_scope="module")
async def current_loop():
    return asyncio.get_running_loop()

@pytest.mark.asyncio(loop_scope="module")
async def test_runs_in_module_loop(current_loop):
    assert current_loop is asyncio.get_running_loop()
```

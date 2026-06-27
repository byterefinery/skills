# Core Concepts Reference

## Event Loop Architecture

pytest-asyncio maps event loops to pytest's collector hierarchy. Each collector level gets its own loop:

```
Session (root)
  └── Package
        └── Module
              └── Class
                    └── Function (default scope)
```

By default, every test runs in a fresh **function-scoped** event loop — the narrowest scope, giving maximum isolation between tests. Tests sharing a common ancestor can be configured to share that ancestor's loop via `loop_scope`.

### How loops are managed

pytest-asyncio uses `asyncio.Runner` (Python 3.11+) or `backports.asyncio.runner.Runner` (Python 3.10) internally. A scoped runner fixture (`_<scope>_scoped_runner`) is created per scope level and yields a `Runner` instance. Tests and fixtures execute within the runner's event loop via `runner.run()`.

The runner handles:
- Event loop creation and lifecycle
- Debug mode configuration
- Custom loop factories (when `pytest_asyncio_loop_factories` hook is defined)
- Proper teardown including async generator cleanup

### Getting the running loop

Inside an async test or fixture, get the current loop with:

```python
import asyncio

loop = asyncio.get_running_loop()
```

Never use `asyncio.get_event_loop()` inside async code — it returns the thread's default loop, not necessarily the one pytest-asyncio is running. Prefer `get_running_loop()` which raises if no loop is active.

## Test Discovery Modes

pytest-asyncio provides two modes controlling how async tests and fixtures are discovered:

### Strict Mode (default)

```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"
```

- Only tests with `@pytest.mark.asyncio` are run as async tests
- Only fixtures decorated with `@pytest_asyncio.fixture` are treated as async fixtures
- Unmarked async test functions are ignored by pytest-asyncio (pytest will skip or fail them)
- Async fixtures using `@pytest.fixture` instead of `@pytest_asyncio.fixture` trigger a deprecation warning when requested by a marked test

Use strict mode when multiple async frameworks coexist (e.g., pytest-asyncio + pytest-trio). It prevents pytest-asyncio from claiming tests/fixtures that belong to other plugins.

### Auto Mode

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- All `async def test_*` functions are automatically handled, no marker needed
- All async fixtures (whether decorated with `@pytest.fixture` or `@pytest_asyncio.fixture`) are managed by pytest-asyncio
- Synchronous tests and fixtures are unaffected

Use auto mode for projects that use only asyncio. It is the simplest configuration and recommended default.

### Mode precedence

Command-line flag overrides config file:

```bash
pytest --asyncio-mode=strict   # overrides pyproject.toml setting
```

## Test Execution Model

pytest-asyncio runs tests **sequentially**, just like synchronous pytest tests. Each async test executes as a task within its assigned event loop.

```python
@pytest.mark.asyncio
async def test_first():
    await asyncio.sleep(2)  # Takes 2 seconds

@pytest.mark.asyncio
async def test_second():
    await asyncio.sleep(2)  # Takes 2 seconds

# Total: ~4 seconds, NOT ~2 seconds
```

This sequential execution is intentional. Concurrent test execution would introduce race conditions and side effects where one test interferes with another.

### What runs concurrently within a test

While tests run sequentially *between* each other, code within a single test can use normal asyncio concurrency:

```python
@pytest.mark.asyncio
async def test_concurrent_operations():
    # These run concurrently within the same test
    result_a, result_b = await asyncio.gather(
        fetch_data_a(),
        fetch_data_b(),
    )
    assert result_a and result_b
```

`asyncio.gather()`, `asyncio.create_task()`, and other concurrency primitives work normally within a test's event loop.

## Supported Test Function Types

pytest-asyncio recognizes several async test patterns:

| Pattern | Supported | Notes |
|---------|-----------|-------|
| `async def test_*()` | Yes | Standard coroutine test |
| `@staticmethod async def test_*()` | Yes | Static method in test class |
| `@given(...) async def test_*()` | Yes | Hypothesis + asyncio (see advanced topics) |
| `async def test_*(): yield` | No | Async generators as tests are xfailed |
| `def test_*(): await ...` | No | Sync function with await is syntax error |

### Class-based tests

```python
class TestMyClass:
    @pytest.mark.asyncio
    async def test_method(self):
        ...

    @staticmethod
    @pytest.mark.asyncio
    async def test_static():
        ...
```

Both instance methods and static methods work. The `@pytest.mark.asyncio` can be on the class, individual methods, or applied via `pytestmark`.

## The `event_loop_policy` Fixture (Deprecated)

The built-in `event_loop_policy` fixture returns the current event loop policy. Historically, it was overridden to customize event loop creation:

```python
# DEPRECATED — do not use this pattern
@pytest.fixture(scope="session")
def event_loop_policy():
    return uvloop.EventLoopPolicy()
```

This is deprecated in v1.4.0. Use the `pytest_asyncio_loop_factories` hook instead (see [05-loop-factories.md](05-loop-factories.md)).

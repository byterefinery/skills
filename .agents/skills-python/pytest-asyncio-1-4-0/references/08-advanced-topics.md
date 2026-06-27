# Advanced Topics Reference

## Hypothesis Integration

pytest-asyncio supports `@hypothesis.given` decorated async tests. The plugin detects Hypothesis-wrapped coroutines and synchronizes the inner test function.

### Basic usage

```python
import pytest
from hypothesis import given, strategies as st

@given(n=st.integers())
@pytest.mark.asyncio
async def test_async_hypothesis(n):
    assert isinstance(n, int)
    result = await async_compute(n)
    assert result >= 0
```

### Decorator order

Both decorator orders work:

```python
# @given outer (common)
@given(st.integers())
@pytest.mark.asyncio
async def test_a(n):
    ...

# @pytest.mark.asyncio outer
@pytest.mark.asyncio
@given(st.integers())
async def test_b(n):
    ...
```

### Combined with `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize("y", [1, 2])
@given(x=st.none())
@pytest.mark.asyncio
async def test_combined(x, y):
    assert x is None
    assert y in (1, 2)
```

### Auto mode with Hypothesis

In auto mode, Hypothesis async tests are automatically detected:

```python
# pyproject.toml: asyncio_mode = "auto"

@given(n=st.integers())
async def test_auto_hypothesis(n):
    # No @pytest.mark.asyncio needed
    assert isinstance(n, int)
```

Synchronous Hypothesis tests are not auto-marked — they run normally without asyncio.

### Hypothesis version requirement

pytest-asyncio requires Hypothesis 3.64.0+. Older versions produce a test failure with the message: "pytest-asyncio only works with Hypothesis 3.64.0 or later."

## `is_async_test()` Function

Check whether a pytest item is managed by pytest-asyncio. Useful in hooks and plugins.

```python
from pytest_asyncio import is_async_test

def pytest_collection_modifyitems(session, config, items):
    async_items = [item for item in items if is_async_test(item)]
    sync_items = [item for item in items if not is_async_test(item)]

    # Apply different markers based on async/sync
    for item in async_items:
        item.add_marker(pytest.mark.slow)
```

### Behavior by mode

| Item | Strict mode | Auto mode |
|------|-------------|-----------|
| `@pytest.mark.asyncio` + `async def` | `True` | `True` |
| Unmarked `async def` | `False` | `True` |
| Sync `def` | `False` | `False` |
| `@pytest.mark.asyncio` on sync `def` | `False` (warns) | `False` (warns) |

## Migration from v0.21

The `event_loop` fixture was removed. Migration steps:

1. **Remove `event_loop` fixture requests** — Replace `async def test(foo, event_loop)` with `async def test(foo)` and use `asyncio.get_running_loop()` inside the test.

2. **Convert sync functions requesting `event_loop` to async** — If a sync test or fixture requested `event_loop`, convert it to `async def`.

3. **Replace custom `event_loop` fixtures with `loop_scope`** — Instead of overriding `event_loop` at module scope:

   ```python
   # Old (v0.21)
   @pytest.fixture(scope="module")
   def event_loop():
       loop = asyncio.new_event_loop()
       yield loop
       loop.close()
   ```

   Use `loop_scope` on tests and fixtures:

   ```python
   # New
   pytestmark = pytest.mark.asyncio(loop_scope="module")

   @pytest_asyncio.fixture(loop_scope="module", scope="module")
   async def module_fixture():
       ...
   ```

4. **Set `asyncio_default_fixture_loop_scope`** — Prevent deprecation warnings:

   ```toml
   [tool.pytest.ini_options]
   asyncio_default_fixture_loop_scope = "function"
   ```

## Migration from v0.23

1. **Explicit `loop_scope` on async fixtures** — Replace `@pytest.fixture(scope="...")` with `@pytest_asyncio.fixture(loop_scope="...", scope="...")`:

   ```python
   # Old
   @pytest_asyncio.fixture(scope="module")
   async def my_fixture():
       ...

   # New
   @pytest_asyncio.fixture(loop_scope="module", scope="module")
   async def my_fixture():
       ...
   ```

   Or set the default in config:

   ```toml
   [tool.pytest.ini_options]
   asyncio_default_fixture_loop_scope = "module"
   ```

2. **Replace `scope` with `loop_scope` on markers** — The `scope` keyword argument to `@pytest.mark.asyncio` is deprecated:

   ```python
   # Old (deprecated)
   @pytest.mark.asyncio(scope="module")

   # New
   @pytest.mark.asyncio(loop_scope="module")
   ```

## Deprecated Patterns

### Overriding `event_loop_policy` fixture

```python
# DEPRECATED in v1.4.0
@pytest.fixture(scope="session")
def event_loop_policy():
    return uvloop.EventLoopPolicy()
```

Replace with the `pytest_asyncio_loop_factories` hook:

```python
def pytest_asyncio_loop_factories(config, item):
    return {"uvloop": uvloop.new_event_loop}
```

### Using `scope` instead of `loop_scope` on markers

```python
# DEPRECATED
@pytest.mark.asyncio(scope="session")

# Use instead
@pytest.mark.asyncio(loop_scope="session")
```

### Unset `asyncio_default_fixture_loop_scope`

Leaving this config option unset defaults to the fixture's caching scope, which produces unexpected behavior. Always set it explicitly:

```toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
```

## `asyncio.run()` in Tests

Avoid calling `asyncio.run()` inside pytest-asyncio tests. It creates a new event loop, which can:

1. Leave the outer loop in an inconsistent state
2. Trigger `ResourceWarning: unclosed event loop`
3. Cause `RuntimeError: There is no current event loop` in subsequent tests

If you need to test code that calls `asyncio.run()`, isolate it:

```python
@pytest.mark.asyncio
async def test_code_using_asyncio_run():
    # Run the problematic code in a subprocess or use monkeypatch
    ...
```

## Free-Threaded Python (3.14t)

pytest-asyncio 1.3.0+ is tested against free-threaded Python 3.14t. No special configuration is needed — the plugin works the same way as in standard CPython.

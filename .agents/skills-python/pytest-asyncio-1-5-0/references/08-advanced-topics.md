# Advanced Topics Reference

## Changes in 1.5.0

Two changes landed in 1.5.0 (2026-11-12):

### `fixture-scope` value for `asyncio_default_fixture_loop_scope`

A new `"fixture-scope"` value was added. With it, an asynchronous fixture without `loop_scope` uses its `scope` as its loop scope — exactly the behavior of an unset option in pytest-asyncio 1.x. Use it to pin that behavior explicitly while the unset option remains deprecated:

```toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "fixture-scope"
```

The deprecation warning emitted when the option is unset now also recommends this: *"Set it to 'fixture-scope' to keep the current behavior."*

### Clearer invalid-marker errors

Invalid arguments to the `asyncio` marker — including an invalid `loop_scope`, positional arguments, unknown keywords, and bad `loop_factories` — are now reported with a message that names the test (its node ID) instead of a traceback. Example:

```
tests/test_foo.py::test_bar: mark.asyncio got an unexpected loop scope value 'bogus'.
Valid scopes are: function, class, module, package, session.
```

Also relevant since 1.4.x: declared support for Python 3.15 (1.4.1), and `AsyncIterable` is allowed as a return type for async generator fixtures (1.4.1).

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

pytest-asyncio requires Hypothesis 3.64.0+. Older versions cause a test failure with the message: "pytest-asyncio only works with Hypothesis 3.64.0 or later."

## `is_async_test()` Function

Check whether a pytest item is managed by pytest-asyncio. Intended for use in pytest hooks or by plugins that depend on pytest-asyncio:

```python
from pytest_asyncio import is_async_test


def pytest_collection_modifyitems(items):
    for item in items:
        if is_async_test(item):
            pass  # item is an async test managed by pytest-asyncio
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

1. **Remove `event_loop` fixture requests** — Replace `async def test(foo, event_loop)` with `async def test(foo)` and use `event_loop = asyncio.get_running_loop()` inside the test.

2. **Convert sync functions requesting `event_loop` to async** — Sync test cases and fixtures that requested `event_loop` become async.

3. **Replace custom `event_loop` fixtures with `loop_scope`** — For each re-implemented `event_loop` fixture (start with the deepest nesting level), configure `loop_scope` for affected tests and fixtures to match the `event_loop` fixture scope:

   ```python
   # Old (v0.21)
   @pytest.fixture(scope="module")
   def event_loop():
       loop = asyncio.new_event_loop()
       yield loop
       loop.close()
   ```

   ```python
   # New
   pytestmark = pytest.mark.asyncio(loop_scope="module")

   @pytest_asyncio.fixture(loop_scope="module", scope="module")
   async def module_fixture():
       ...
   ```

   Then remove the re-implemented `event_loop` fixture.

4. **Set `asyncio_default_fixture_loop_scope`** — If not set yet, set it to `function` to silence the deprecation warning.

## Migration from v0.23

These steps assume no re-implementations of the `event_loop` fixture. If there are any, follow the v0.21 guide first.

1. **Explicit `loop_scope` on async fixtures** — Replace `@pytest.fixture(scope="...")` / `@pytest_asyncio.fixture(scope="...")` with `@pytest_asyncio.fixture(loop_scope="...", scope="...")` such that `loop_scope` and `scope` are the same. In auto mode, resolve any missing `pytest_asyncio` imports. Alternatively, set `asyncio_default_fixture_loop_scope` to a single loop scope used by all fixtures.

2. **Set `asyncio_default_fixture_loop_scope`** — If not set, set it to `function` to address the deprecation warning.

3. **Replace `scope` with `loop_scope` on markers** — Change all `pytest.mark.asyncio(scope="...")` to `pytest.mark.asyncio(loop_scope="...")`.

## Migration from 1.x to 1.5.0

No code changes are required. If you relied on the unset `asyncio_default_fixture_loop_scope` behavior (fixtures loop in their own scope), that behavior still works but is deprecated. Pin it explicitly with `fixture-scope` (new in 1.5.0), or move to `function`.

## Deprecated Patterns

### Overriding `event_loop_policy` fixture

```python
# DEPRECATED — will be removed in a future version
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

Leaving this config option unset defaults to the fixture's caching scope, which produces a deprecation warning. Always set it explicitly:

```toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
```

or `"fixture-scope"` to preserve the current behavior.

## `asyncio.run()` in Tests

Avoid calling `asyncio.run()` inside pytest-asyncio tests. It creates a new event loop, which can:

1. Leave the outer loop in an inconsistent state
2. Trigger `ResourceWarning: unclosed event loop`
3. Cause `RuntimeError: There is no current event loop` in subsequent tests

If you need to test code that calls `asyncio.run()`, isolate it (e.g., run the problematic code in a subprocess).

## Free-Threaded Python (3.14t)

pytest-asyncio is tested against free-threaded Python 3.14t. No special configuration is needed — the plugin works the same way as in standard CPython. Supported Python versions per the package metadata: 3.10 through 3.15.

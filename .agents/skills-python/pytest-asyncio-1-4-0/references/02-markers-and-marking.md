# Markers and Marking Reference

## `@pytest.mark.asyncio`

The `asyncio` marker tells pytest-asyncio to run a coroutine as an async test. It accepts keyword arguments only.

### Basic usage

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_fetch():
    result = await fetch_data()
    assert result.status == 200
```

In auto mode, the marker is added automatically to all async test functions, so explicit decoration is unnecessary.

### `loop_scope` argument

Controls which event loop the test runs in. Valid values: `function`, `class`, `module`, `package`, `session`.

```python
@pytest.mark.asyncio(loop_scope="module")
async def test_shared_module_loop():
    # All tests with loop_scope="module" in this file share one loop
    ...
```

Default is determined by `asyncio_default_test_loop_scope` config option (defaults to `function`).

### `loop_factories` argument

Selects a subset of configured event loop factories for a specific test:

```python
@pytest.mark.asyncio(loop_factories=["uvloop"])
async def test_with_uvloop():
    # Runs only with the "uvloop" factory
    ...
```

Requires at least one `pytest_asyncio_loop_factories` hook implementation. See [05-loop-factories.md](05-loop-factories.md).

### Combining arguments

```python
@pytest.mark.asyncio(loop_scope="session", loop_factories=["custom"])
async def test_session_custom():
    ...
```

### Deprecated: `scope` argument

The marker historically accepted `scope=...` instead of `loop_scope=...`. This is deprecated. Migrating:

```python
# Old (deprecated)
@pytest.mark.asyncio(scope="module")

# New
@pytest.mark.asyncio(loop_scope="module")
```

Passing both `scope` and `loop_scope` raises a `pytest.UsageError`.

## Marker Validation Rules

The marker only accepts keyword arguments. These patterns raise `ValueError`:

```python
# ERROR: positional argument
@pytest.mark.asyncio("session")

# ERROR: unknown keyword
@pytest.mark.asyncio(loop_scope="session", foo="bar")

# ERROR: loop_factories must be non-empty sequence of strings
@pytest.mark.asyncio(loop_factories="custom")       # string, not list
@pytest.mark.asyncio(loop_factories=[])              # empty
@pytest.mark.asyncio(loop_factories=[""])            # empty string
@pytest.mark.asyncio(loop_factories=[1])             # non-string
```

## `pytestmark` Patterns

Apply the marker to all tests in a module or class using `pytestmark`:

### Module-level marking

```python
import pytest

# All async functions in this module use asyncio with module-scoped loop
pytestmark = pytest.mark.asyncio(loop_scope="module")

async def test_a():
    ...

async def test_b():
    ...
```

In strict mode without `loop_scope`:

```python
pytestmark = pytest.mark.asyncio  # uses default loop_scope (function)
```

### Class-level marking

```python
class TestClass:
    pytestmark = pytest.mark.asyncio(loop_scope="class")

    async def test_a(self):
        ...

    async def test_b(self):
        ...
```

Or as a class decorator:

```python
@pytest.mark.asyncio(loop_scope="class")
class TestClass:
    async def test_a(self):
        ...
```

### Package-level marking

Add to `__init__.py` of the test package:

```python
import pytest

pytestmark = pytest.mark.asyncio(loop_scope="package")
```

This applies to all tests in the package directory but **not** to subpackages. Each subdirectory is its own package scope.

## Marker Inheritance

The `asyncio` marker is inherited by subclasses:

```python
@pytest.mark.asyncio(loop_scope="class")
class TestBase:
    pass

class TestChild(TestBase):
    async def test_inherits_marker(self):
        # Runs with class-scoped loop from parent
        ...
```

## Warnings and Errors

| Situation | Result |
|-----------|--------|
| `@pytest.mark.asyncio` on sync function | `PytestWarning`: "marked but not an async function" |
| `@pytest.mark.asyncio` on async generator test | `xfailed` with warning: "async generators not supported" |
| Positional args to marker | `ValueError` at collection |
| Unknown kwargs to marker | `ValueError` at collection |
| Both `scope` and `loop_scope` | `UsageError` at collection |
| `loop_factories` without hook impl | `UsageError` at collection |
| Unmarked async test in strict mode | Ignored by pytest-asyncio; pytest may skip/fail it |

## Combining with Other Markers

The `asyncio` marker composes with other pytest markers:

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("value", [1, 2, 3])
async def test_parametrized(value):
    result = await compute(value)
    assert result > 0

@pytest.mark.asyncio
@pytest.mark.skip(reason="not ready")
async def test_skipped():
    ...

@pytest.mark.asyncio
@pytest.mark.xfail
async def test_expected_failure():
    ...
```

Order of decorators does not matter for `@pytest.mark.*` markers.

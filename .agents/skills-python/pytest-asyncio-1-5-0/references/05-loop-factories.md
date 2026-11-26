# Loop Factories Reference

## `pytest_asyncio_loop_factories` Hook

The `pytest_asyncio_loop_factories` hook lets you define named event loop factories and parametrize async tests across them. This is the replacement for the deprecated `event_loop_policy` fixture override pattern.

### Basic usage

Define the hook in `conftest.py`:

```python
import asyncio

class CustomEventLoop(asyncio.SelectorEventLoop):
    pass

def pytest_asyncio_loop_factories(config, item):
    return {
        "stdlib": asyncio.new_event_loop,
        "custom": CustomEventLoop,
    }
```

Each async test runs once per factory. Mapping keys are used as test IDs:

```
test_example[stdlib] PASSED
test_example[custom] PASSED
```

### Single factory (no name change)

When only one factory is configured, the parametrize ID is hidden, so test names remain unchanged:

```python
def pytest_asyncio_loop_factories(config, item):
    return {"asyncio": asyncio.new_event_loop}
# test_example  (not test_example[asyncio])
```

### Factory signature

Each factory must be a callable with no required parameters that returns an `asyncio.AbstractEventLoop`:

```python
# Function factory
def my_factory():
    return asyncio.SelectorEventLoop()

# Class as factory (class is callable)
class MyLoop(asyncio.SelectorEventLoop):
    pass

# Lambda
factory = lambda: asyncio.new_event_loop()
```

### Hook contract

- Must return a non-empty `dict` (mapping) of non-empty string names to callables
- Returning `None` means "not applicable for this item" (next hook implementation is tried)
- Multiple implementations: the first non-`None` result in pytest's hook dispatch order wins
- The hook result is snapshotted at parametrization time, so mutating the original mapping later has no effect
- Invalid return values (empty mapping, non-mapping, empty names, non-callable values) raise `pytest.UsageError`: "pytest_asyncio_loop_factories must return a non-empty mapping of factory names to callables."

```python
# Valid: return None to defer to another implementation
def pytest_asyncio_loop_factories(config, item):
    if should_use_custom(item):
        return {"custom": CustomLoop}
    return None  # Let next hook handle it

# Invalid — raises UsageError
def bad_hook(config, item):
    return {}              # empty mapping
    return []              # not a mapping
    return {"": Factory}   # empty name
    return {"x": 123}      # non-callable value
```

## Per-Test Factory Selection

Use `loop_factories` on the marker to select a subset of available factories:

```python
@pytest.mark.asyncio(loop_factories=["custom"])
async def test_runs_with_only_custom_factory():
    ...

# No loop_factories — runs with ALL configured factories
@pytest.mark.asyncio
async def test_runs_with_every_configured_factory():
    ...
```

Factory selection preserves the order given in the marker.

### Missing factory handling

If a requested factory name is not available from the hook, that variant is **skipped** (not errored):

```
SKIPPED: Loop factory 'missing' is not available. Available factories: stdlib, custom.
```

Partial intersection runs available variants and skips missing ones.

### Platform-conditional factories

```python
import sys

def pytest_asyncio_loop_factories(config, item):
    factories = {"default": asyncio.new_event_loop}
    if sys.platform == "win32":
        factories["proactor"] = asyncio.ProactorEventLoop
    return factories
```

Tests requesting unavailable platform-specific factories are automatically skipped.

## Per-Item Factory Configuration

The hook receives the current `pytest.Item`, enabling item-specific factory selection. For example, return different factories for tests that request a particular fixture (from the official how-to guide):

```python
# conftest.py
import asyncio

import pytest


class CustomEventLoop(asyncio.SelectorEventLoop):
    pass


@pytest.fixture
def requires_custom_loop():
    pass


def pytest_asyncio_loop_factories(config, item):
    if "requires_custom_loop" in item.fixturenames:
        return {"custom": CustomEventLoop}
    return {"default": asyncio.new_event_loop}
```

```python
# test_extra_loop_factories.py
import pytest


@pytest.mark.asyncio
async def test_runs_with_default_factory_only():
    pass  # parametrized only over "default"


@pytest.mark.asyncio
async def test_runs_with_custom_factory_only(requires_custom_loop):
    pass  # parametrized only over "custom"
```

The same pattern works with any information available from the item: fixture names, markers, node IDs, or file paths.

### By marker

```python
def pytest_asyncio_loop_factories(config, item):
    if item.get_closest_marker("slow"):
        return {"slow": SlowLoop}
    return {"fast": FastLoop}
```

### By node ID

```python
def pytest_asyncio_loop_factories(config, item):
    if "test_integration" in item.nodeid:
        return {"integration": IntegrationLoop}
    return {"unit": asyncio.new_event_loop}
```

## Nested `conftest.py` Locality

The hook is a standard pytest hook, so its placement matters. An implementation in a nested `conftest.py` applies only to tests collected under that directory — use it when a whole package or directory should share the same factory set.

## uvloop Integration

From the official how-to guide:

```python
import uvloop


def pytest_asyncio_loop_factories(config, item):
    return {
        "uvloop": uvloop.new_event_loop,
    }
```

Tests requesting `loop_factories=["uvloop"]` run with the uvloop loop.

Note: `asyncio.AbstractEventLoopPolicy` is deprecated as of Python 3.14 (removal planned for 3.16), and `uvloop.EventLoopPolicy` will be removed alongside it. The `pytest_asyncio_loop_factories` hook approach above is the recommended way to test with uvloop; overriding the `event_loop_policy` fixture is deprecated in pytest-asyncio as well.

## Synchronous Fixtures with Custom Factories

When custom loop factories are configured, the scoped runner sets the running event loop so that synchronous `@pytest_asyncio.fixture` functions see the correct event loop even if test code disrupts it (e.g., via `asyncio.run()` or `asyncio.set_event_loop(None)`):

```python
def pytest_asyncio_loop_factories(config, item):
    return {"custom": CustomEventLoop}

@pytest_asyncio.fixture(autouse=True)
def enable_debug():
    # This sees the custom loop
    asyncio.get_event_loop().set_debug(True)

@pytest.mark.asyncio
async def test_debug_enabled():
    assert asyncio.get_running_loop().get_debug()
```

## Migration from `event_loop_policy`

**Old pattern (deprecated):**

```python
@pytest.fixture(scope="session")
def event_loop_policy():
    return uvloop.EventLoopPolicy()
```

**New pattern:**

```python
def pytest_asyncio_loop_factories(config, item):
    return {"uvloop": uvloop.new_event_loop}
```

The hook approach is more flexible: it supports per-test factory selection, multiple factories with parametrization, and item-specific configuration. The `event_loop_policy` fixture override will be removed in a future version.

## Interaction with `loop_scope`

Factory parametrization and loop scoping work independently:

- **Factory** determines *which type* of event loop is created
- **loop_scope** determines *how long* the loop lives

```python
def pytest_asyncio_loop_factories(config, item):
    return {"a": LoopA, "b": LoopB}

@pytest.mark.asyncio(loop_scope="session", loop_factories=["a"])
async def test_session_a():
    # One LoopA instance for all session tests
    ...

@pytest.mark.asyncio(loop_scope="function")
async def test_per_function():
    # New LoopA and LoopB per test (2 variants)
    ...
```

The configured loop scope still determines how long each event loop instance is kept alive, even when factories parametrize the test.

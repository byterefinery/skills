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

Each async test runs once per factory. Test output shows factory names as parametrization IDs:

```
test_example[stdlib] PASSED
test_example[custom] PASSED
```

### Single factory (no name change)

When only one factory is configured, test names remain unchanged (no `[factory_name]` suffix):

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

- Must return a non-empty `dict` mapping string names to callables
- Names must be non-empty strings
- Values must be callables
- Returning `None` means "not applicable for this item" (next hook impl is tried)
- Multiple implementations: first non-`None` result wins (pytest hook dispatch order)
- Invalid return values raise `pytest.UsageError`

```python
# Valid: return None to defer to another implementation
@pytest.hookimpl(tryfirst=True)
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
async def test_only_custom():
    # Runs only with "custom" factory
    ...

@pytest.mark.asyncio(loop_factories=["stdlib", "custom"])
async def test_both():
    # Runs with both factories
    ...

# No loop_factories — runs with ALL configured factories
@pytest.mark.asyncio
async def test_all_factories():
    ...
```

### Missing factory handling

If a requested factory name is not available from the hook, that variant is **skipped** (not errored):

```python
@pytest.mark.asyncio(loop_factories=["missing"])
async def test_missing():
    # SKIPPED: "Loop factory 'missing' is not available"
    ...
```

Partial intersection runs available variants and skips missing ones:

```python
@pytest.mark.asyncio(loop_factories=["available", "missing"])
async def test_partial():
    # Runs once with "available", skips "missing"
    ...
```

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

The hook receives the current `pytest.Item`, enabling item-specific factory selection:

### By fixture request

```python
@pytest.fixture
def requires_uvloop():
    pass

def pytest_asyncio_loop_factories(config, item):
    if "requires_uvloop" in item.fixturenames:
        return {"uvloop": uvloop.new_event_loop}
    return {"default": asyncio.new_event_loop}
```

### By node ID

```python
def pytest_asyncio_loop_factories(config, item):
    if "test_integration" in item.nodeid:
        return {"integration": IntegrationLoop}
    return {"unit": asyncio.new_event_loop}
```

### By marker

```python
def pytest_asyncio_loop_factories(config, item):
    if item.get_closest_marker("slow"):
        return {"slow": SlowLoop}
    return {"fast": FastLoop}
```

## Nested `conftest.py` Locality

Hook implementations in nested `conftest.py` files apply only to tests under that directory:

```
project/
├── conftest.py           # root hook → applies to test_root.py
│   └── pytest_asyncio_loop_factories → {"root": RootLoop}
└── subdir/
    ├── conftest.py       # nested hook → applies to test_sub.py
    │   └── pytest_asyncio_loop_factories → {"sub": SubLoop}
    └── test_sub.py
```

The nearest `conftest.py` hook wins (pytest's standard conftest locality).

## uvloop Integration

```python
import uvloop

def pytest_asyncio_loop_factories(config, item):
    return {
        "stdlib": asyncio.new_event_loop,
        "uvloop": uvloop.new_event_loop,
    }
```

Tests run once with the standard library loop and once with uvloop. Select specific implementations:

```python
@pytest.mark.asyncio(loop_factories=["uvloop"])
async def test_uvloop_specific():
    ...
```

## Synchronous Fixtures with Custom Factories

When custom loop factories are configured, synchronous `@pytest_asyncio.fixture` functions see the correct event loop even if test code disrupts it (e.g., via `asyncio.run()` or `asyncio.set_event_loop(None)`):

```python
def pytest_asyncio_loop_factories(config, item):
    return {"custom": CustomEventLoop}

@pytest_asyncio.fixture(autouse=True)
def enable_debug():
    # This sees the custom loop's event loop
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

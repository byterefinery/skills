---
name: pytest-asyncio-1-4-0
description: >
  Test async/await code with pytest using event loops, async fixtures, and loop scopes.
  Use when writing async tests, configuring asyncio mode (auto/strict), managing event loop scopes,
  using @pytest.mark.asyncio, @pytest_asyncio.fixture, custom loop factories via
  pytest_asyncio_loop_factories hook, port fixtures (unused_tcp_port, unused_udp_port),
  testing with uvloop or other custom event loops, integrating Hypothesis with async tests,
  or migrating from older pytest-asyncio versions. Covers pytest-asyncio 1.4.0+ and Python 3.10+.
---

# pytest-asyncio 1.4.0

pytest-asyncio is a pytest plugin that enables testing of `asyncio`-based code. It provides event loop management, async test support, and async fixtures. This skill covers version **1.4.0** (Python 3.10+, pytest 8.4+).

## Overview

pytest-asyncio runs async tests sequentially inside managed asyncio event loops. Key capabilities:

- **Async test functions** — mark `async def test_*` with `@pytest.mark.asyncio` (or use auto mode)
- **Async fixtures** — declare with `@pytest_asyncio.fixture`, supporting both coroutines and async generators
- **Event loop scoping** — control loop lifetime via `loop_scope` on tests (`function`, `class`, `module`, `package`, `session`)
- **Custom event loops** — parametrize tests across loop implementations via `pytest_asyncio_loop_factories` hook
- **Port fixtures** — `unused_tcp_port`, `unused_udp_port`, and their factory variants for network testing

Tests run sequentially, not concurrently. Each test gets its own event loop by default (function scope), ensuring isolation.

## Usage

### Minimal async test

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_fetch_data():
    result = await my_async_function()
    assert result == expected
```

### Auto mode (recommended for pure-asyncio projects)

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

With auto mode, the `@pytest.mark.asyncio` decorator is unnecessary — all async test functions are handled automatically.

### Async fixtures

```python
import pytest_asyncio

@pytest_asyncio.fixture
async def db_connection():
    conn = await create_connection()
    yield conn
    await conn.close()
```

In strict mode, use `@pytest_asyncio.fixture` (not `@pytest.fixture`) for async fixtures. In auto mode, either decorator works.

### Scoped event loops

Share an event loop across tests in a class:

```python
@pytest.mark.asyncio(loop_scope="class")
class TestSharedLoop:
    async def test_a(self): ...
    async def test_b(self): ...  # same loop as test_a
```

Use module-level `pytestmark` for all tests in a file:

```python
pytestmark = pytest.mark.asyncio(loop_scope="module")
```

## Gotchas

- **Always set `asyncio_default_fixture_loop_scope`** — Leaving it unset triggers a deprecation warning and defaults to the fixture's caching scope. Future versions default to `"function"`. Set it explicitly in config.
- **Don't close the event loop in tests** — Calling `loop.close()` or `asyncio.run()` inside a test can break runner teardown. Use `asyncio.get_running_loop()` instead of creating new loops.
- **`@pytest_asyncio.fixture` vs `@pytest.fixture`** — In strict mode, async fixtures must use `@pytest_asyncio.fixture`. Using `@pytest.fixture` on an async function in strict mode produces a deprecation warning (will become an error). In auto mode, both work.
- **`loop_scope` is not the same as `scope`** — On `@pytest_asyncio.fixture`, `loop_scope` controls which event loop runs the fixture, while `scope` controls caching lifetime. The `loop_scope` must be >= the fixture's `scope` (e.g., a `session`-scoped fixture can run in a `session` loop but not a `function` loop).
- **Tests run sequentially** — pytest-asyncio does not run tests concurrently. Two `await asyncio.sleep(2)` tests take ~4 seconds total, not ~2.
- **Async generators as tests are unsupported** — An `async def test_*` that yields is marked xfail with a warning. Use regular async coroutines for tests; reserve async generators for fixtures.
- **`@pytest.mark.asyncio` on sync functions warns** — The marker is validated: applying it to a non-async function emits a PytestWarning. Remove the marker from sync tests or check for global `pytestmark`.
- **`scope` kwarg deprecated in favor of `loop_scope`** — The asyncio marker accepted `scope=...` historically; use `loop_scope=...` instead. Passing both `scope` and `loop_scope` raises a `UsageError`.
- **`event_loop_policy` fixture override is deprecated** — Do not override the `event_loop_policy` fixture to customize event loops. Use the `pytest_asyncio_loop_factories` hook instead.
- **Contextvars are isolated between async tests** — Changes to contextvars in one async test do not leak into another, even at module/session scope. Sync-to-sync contextvar changes are not isolated.
- **Subpackages don't share package-scoped loops** — Each package directory is its own scope boundary. Subdirectories constitute separate packages with their own event loops.

## References

- [01-core-concepts](references/01-core-concepts.md) — Event loop architecture, auto vs strict mode, test execution model
- [02-markers-and-marking](references/02-markers-and-marking.md) — `@pytest.mark.asyncio`, `loop_scope`, `pytestmark` patterns, marker validation
- [03-async-fixtures](references/03-async-fixtures.md) — `@pytest_asyncio.fixture`, loop_scope vs scope, async generators, contextvars
- [04-configuration](references/04-configuration.md) — pyproject.toml options, CLI flags, default values, report header
- [05-loop-factories](references/05-loop-factories.md) — `pytest_asyncio_loop_factories` hook, custom loops, uvloop, per-test selection
- [06-scope-patterns](references/06-scope-patterns.md) — Class/module/package/session scope patterns with complete examples
- [07-port-fixtures](references/07-port-fixtures.md) — `unused_tcp_port`, `unused_udp_port`, factory fixtures, network testing
- [08-advanced-topics](references/08-advanced-topics.md) — Hypothesis integration, `is_async_test()`, migration guides, deprecated patterns

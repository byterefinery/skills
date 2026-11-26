# Scope Patterns Reference

## Function Scope (Default)

Each test gets its own event loop. Maximum isolation.

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_a():
    # Own event loop
    ...

@pytest.mark.asyncio
async def test_b():
    # Different event loop from test_a
    ...
```

Set as default in config:

```toml
[tool.pytest.ini_options]
asyncio_default_test_loop_scope = "function"
```

## Class Scope

All tests in a class share one event loop. Useful when tests need to verify shared state within the same loop.

### As class decorator

```python
import asyncio
import pytest

@pytest.mark.asyncio(loop_scope="class")
class TestSharedClassLoop:
    loop: asyncio.AbstractEventLoop

    async def test_remember_loop(self):
        TestSharedClassLoop.loop = asyncio.get_running_loop()

    async def test_same_loop(self):
        assert asyncio.get_running_loop() is TestSharedClassLoop.loop
```

### Via pytestmark

```python
class TestSharedClassLoop:
    pytestmark = pytest.mark.asyncio(loop_scope="class")

    async def test_a(self):
        ...

    async def test_b(self):
        ...  # Same loop as test_a
```

### Class-scoped fixtures

```python
@pytest.mark.asyncio(loop_scope="class")
class TestWithFixture:
    @pytest_asyncio.fixture(loop_scope="class", scope="class")
    async def session_data(self):
        data = await fetch_expensive_data()
        yield data
        await cleanup(data)

    @pytest.mark.asyncio
    async def test_one(self, session_data):
        assert session_data

    @pytest.mark.asyncio
    async def test_two(self, session_data):
        # Same fixture instance, same loop
        assert session_data
```

## Module Scope

All tests in a file share one event loop. Apply via `pytestmark` at module level.

```python
import asyncio
import pytest

pytestmark = pytest.mark.asyncio(loop_scope="module")

loop: asyncio.AbstractEventLoop

async def test_remember_loop():
    global loop
    loop = asyncio.get_running_loop()

async def test_same_loop():
    global loop
    assert asyncio.get_running_loop() is loop

class TestClassA:
    async def test_also_same_loop(self):
        global loop
        assert asyncio.get_running_loop() is loop
```

### Module-scoped fixtures

```python
import pytest_asyncio

@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def module_db():
    db = await connect()
    yield db
    await db.close()

@pytest.mark.asyncio(loop_scope="module")
async def test_query(module_db):
    result = await module_db.query("SELECT 1")
    assert result
```

## Package Scope

All tests in a package directory share one event loop. Add `pytestmark` to the package's `__init__.py`:

```python
# tests/__init__.py
import pytest

pytestmark = pytest.mark.asyncio(loop_scope="package")
```

```python
# tests/test_a.py
async def test_a():
    # Package-scoped loop
    ...

# tests/test_b.py
async def test_b():
    # Same loop as test_a
    ...
```

### Subpackages are separate

Subdirectories do not inherit the parent package's loop:

```
tests/
├── __init__.py       # pytestmark = loop_scope="package"
├── test_root.py      # Uses package loop
└── subpkg/
    ├── __init__.py   # No pytestmark → separate package
    └── test_sub.py   # Different loop from test_root.py
```

## Session Scope

All tests across all files share one event loop. Useful for expensive integration test setup.

```python
import asyncio
import pytest

@pytest.mark.asyncio(loop_scope="session")
async def test_remember_loop():
    # All session-scoped tests share this loop
    ...
```

### Session fixtures

```python
@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def global_server():
    server = await start_server()
    yield server
    await server.stop()
```

### Cross-package session sharing

Session-scoped loops span packages and subpackages:

```python
# tests/test_a.py
@pytest.mark.asyncio(loop_scope="session")
async def test_in_package_a():
    ...

# tests/subpkg/test_b.py
@pytest.mark.asyncio(loop_scope="session")
async def test_in_subpackage():
    # Same loop as test_in_package_a
    ...
```

## Mixed Scopes

Tests and fixtures can use different scopes within the same file. A test with narrower scope than its fixture runs in a different loop:

```python
@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def session_resource():
    return await create_resource()

@pytest.mark.asyncio(loop_scope="function")
async def test_function_loop(session_resource):
    # Test runs in function loop, fixture ran in session loop
    # They are different loops
    assert asyncio.get_running_loop() is not session_resource.loop
```

### Restoring scope after a narrow test

```python
@pytest.mark.asyncio(loop_scope="module")
async def test_module_1():
    ...

@pytest.mark.asyncio(loop_scope="function")
async def test_function_only():
    # Briefly uses function-scoped loop
    ...

@pytest.mark.asyncio(loop_scope="module")
async def test_module_2():
    # Back to module-scoped loop
    ...
```

The module loop is preserved across the function-scoped test.

## Scope Hierarchy Summary

```
session  (widest — all tests share one loop)
  └── package  (all tests in a directory)
        └── module  (all tests in a file)
              └── class  (all tests in a class)
                    └── function  (narrowest — each test gets its own loop)
```

**Recommendation:** Keep neighboring tests at the same scope level. Mixing scopes within a module or class makes test code harder to follow. Use `asyncio_default_test_loop_scope` for project-wide defaults and override only when needed.

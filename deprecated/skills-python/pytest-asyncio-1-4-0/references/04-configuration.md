# Configuration Reference

## Config Options

pytest-asyncio provides four configuration options, settable via config file or CLI.

### `asyncio_mode`

Controls test discovery behavior.

| Value | Behavior |
|-------|----------|
| `"strict"` (default) | Only marked tests/fixtures handled by pytest-asyncio |
| `"auto"` | All async tests/fixtures automatically handled |

**Config file:**

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

```ini
# setup.cfg
[tool:pytest]
asyncio_mode = auto
```

**CLI:**

```bash
pytest --asyncio-mode=strict
```

CLI overrides config file. Invalid values raise `pytest.UsageError`.

### `asyncio_default_fixture_loop_scope`

Default event loop scope for async fixtures when `loop_scope` is not specified on the fixture decorator.

| Value | Effect |
|-------|--------|
| `"function"` | Fixtures run in a fresh loop per test (recommended) |
| `"class"` | Fixtures share the class-scoped loop |
| `"module"` | Fixtures share the module-scoped loop |
| `"package"` | Fixtures share the package-scoped loop |
| `"session"` | All fixtures share one session-wide loop |
| unset | Defaults to fixture's own `scope` (deprecated, triggers warning) |

**Always set this explicitly.** Leaving it unset produces a `PytestDeprecationWarning`. Future versions default to `"function"`.

```toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
```

### `asyncio_default_test_loop_scope`

Default event loop scope for async tests when `loop_scope` is not specified on the marker.

| Value | Effect |
|-------|--------|
| `"function"` (default) | Each test gets its own loop |
| `"class"` | Tests in a class share one loop |
| `"module"` | All tests in a module share one loop |
| `"package"` | All tests in a package share one loop |
| `"session"` | All tests share one session-wide loop |

```toml
[tool.pytest.ini_options]
asyncio_default_test_loop_scope = "function"
```

Individual markers override this default:

```python
# Config says module, but marker overrides to function
@pytest.mark.asyncio(loop_scope="function")
async def test_isolated():
    ...
```

### `asyncio_debug`

Enables asyncio debug mode for event loops used by tests and fixtures.

**Config file:**

```ini
# pytest.ini
[pytest]
asyncio_debug = true
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_debug = true
```

**CLI:**

```bash
pytest --asyncio-debug
```

Debug mode enables:
- Slow task cancellation warnings
- Loop lifetime tracking
- Daemon task warnings
- Other asyncio debug diagnostics

## Recommended Configurations

### Pure asyncio project (recommended)

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

This is the simplest setup. All async tests and fixtures work without explicit markers or decorators.

### Multi-framework project

```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"
asyncio_default_fixture_loop_scope = "function"
```

Use strict mode when pytest-trio, pytest-anyio, or other async plugins share the codebase. Explicitly mark asyncio tests with `@pytest.mark.asyncio` and fixtures with `@pytest_asyncio.fixture`.

### Session-scoped loops (shared state)

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
```

All tests and fixtures share one event loop. Useful for integration tests with expensive setup. Individual tests can still override with `loop_scope="function"`.

## Report Header

pytest-asyncio adds a line to the pytest header showing active configuration:

```
pytest-asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
```

Use `-v` or `--debug` to see this. It is useful for verifying the correct mode and scopes are active.

## Validation

Invalid scope values raise `pytest.UsageError` at configuration time:

```toml
# ERROR: "request" is not a valid scope
asyncio_default_fixture_loop_scope = "request"
```

Valid scopes are: `function`, `class`, `module`, `package`, `session`.

## Environment Variables

pytest-asyncio does not support environment variables for configuration. Use config files or CLI flags.

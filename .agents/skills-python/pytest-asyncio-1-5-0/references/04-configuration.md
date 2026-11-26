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

CLI overrides config file. Invalid values raise `pytest.UsageError` listing the valid modes.

### `asyncio_default_fixture_loop_scope`

Default event loop scope for async fixtures when `loop_scope` is not specified on the fixture decorator.

| Value | Effect |
|-------|--------|
| `"function"` | Fixtures run in a fresh loop per test (recommended; future default when unset) |
| `"class"` | Fixtures share the class-scoped loop |
| `"module"` | Fixtures share the module-scoped loop |
| `"package"` | Fixtures share the package-scoped loop |
| `"session"` | All fixtures share one session-wide loop |
| `"fixture-scope"` | New in 1.5.0 — each fixture uses a loop matching its own `scope` (the unset-option behavior of pytest-asyncio 1.x) |
| unset | Defaults to the fixture's own `scope` (deprecated, triggers a warning) |

**Always set this explicitly.** Leaving it unset produces a `PytestDeprecationWarning` stating that future versions will default to `"function"`; the warning also tells you to set `"fixture-scope"` to keep the current behavior.

```toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
```

```toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "fixture-scope"
```

Note that `fixture-scope` resolves per fixture — a `scope="session"` fixture gets the session loop, a `scope="module"` fixture gets the module loop, and so on.

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

```ini
# pytest.ini
[pytest]
asyncio_default_test_loop_scope = session
```

```ini
# setup.cfg
[tool:pytest]
asyncio_default_test_loop_scope = session
```

Individual markers override this default:

```python
# Config says module, but marker overrides to function
@pytest.mark.asyncio(loop_scope="function")
async def test_isolated():
    ...
```

### `asyncio_debug`

Enables asyncio debug mode for the default event loop used by asynchronous tests and fixtures. Disabled by default.

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
pytest tests --asyncio-debug
```

## Recommended Configurations

### Pure asyncio project (recommended)

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

This is the simplest setup. All async tests and fixtures work without explicit markers or decorators. (The pytest-asyncio project itself uses exactly this configuration.)

### Legacy fixture behavior (explicit)

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "fixture-scope"
```

Use this to explicitly preserve the pre-1.5.0 unset-option behavior — each async fixture runs in a loop matching its own scope — without relying on the deprecated default.

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

pytest-asyncio adds a line to the pytest session header showing active configuration:

```
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
```

It is useful for verifying the correct mode and scopes are active.

## Validation

Invalid scope values raise `pytest.UsageError` at configuration time:

```toml
# ERROR: "request" is not a valid asyncio_default_fixture_loop_scope
asyncio_default_fixture_loop_scope = "request"
```

Valid scopes are `function`, `class`, `module`, `package`, `session` (plus `fixture-scope` for `asyncio_default_fixture_loop_scope`).

## Environment Variables

pytest-asyncio does not support environment variables for configuration. Use config files or CLI flags.

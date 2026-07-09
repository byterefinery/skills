# asyncio_mode Configuration

## Modes overview

pytest-aiohttp depends on pytest-asyncio for event loop management. The `asyncio_mode` setting controls how async tests and fixtures are discovered:

| Mode | Behavior |
|---|---|
| `auto` | All `async def test_*` functions are treated as asyncio tests automatically. No `@pytest.mark.asyncio` needed. |
| `strict` | Only functions explicitly marked with `@pytest.mark.asyncio` are treated as asyncio tests. |
| `legacy` | Deprecated. pytest-aiohttp auto-switches to `auto` and emits a warning. |

## Recommended: auto mode

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

With auto mode:

```python
async def test_hello(aiohttp_client):
    client = await aiohttp_client(app)
    resp = await client.get("/")
    assert resp.status == 200
```

No decorator needed. All async test functions and async fixtures are handled.

## strict mode

```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"
```

With strict mode, mark async tests explicitly:

```python
import pytest

@pytest.mark.asyncio
async def test_hello(aiohttp_client):
    client = await aiohttp_client(app)
    resp = await client.get("/")
    assert resp.status == 200
```

`aiohttp_client` works in strict mode because the fixture itself uses `@pytest_asyncio.fixture`.

## Legacy mode auto-switch

If `asyncio_mode` is `legacy` (or unset with pytest-asyncio defaults), pytest-aiohttp detects this in `pytest_configure` and switches to `auto`:

```
DeprecationWarning: The 'asyncio_mode' is 'legacy', switching to 'auto' for the
sake of pytest-aiohttp backward compatibility. Please explicitly use
'asyncio_mode=strict' or 'asyncio_mode=auto' in pytest configuration file.
```

This auto-switch is a backward-compatibility measure. Set `asyncio_mode` explicitly to suppress the warning.

## Configuration locations

`asyncio_mode` can be set in any pytest config location:

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

```ini
# setup.cfg
[tool:pytest]
asyncio_mode = auto
```

```bash
# CLI (overrides config)
pytest --asyncio-mode=auto
```

CLI takes precedence over config files.

## Migration from older pytest-aiohttp

Before v1.0.0, pytest-aiohttp had its own async test runner. Since v1.0.0, it delegates to pytest-asyncio. If migrating:

1. Ensure `pytest-asyncio` is installed
2. Set `asyncio_mode = auto` in config
3. Remove any custom `event_loop` fixture overrides
4. Replace `@pytest.fixture(loop_scope=...)` with `@pytest_asyncio.fixture`

## Interaction with fixture scopes

The asyncio mode does not affect fixture scope behavior. Fixtures declared with `@pytest_asyncio.fixture` respect their `scope` parameter regardless of mode. The mode only controls whether `async def test_*` functions are auto-detected.

## Testing sync functions alongside async

```python
# Sync test — runs normally
def test_config():
    assert config.debug is False

# Async test — handled by pytest-asyncio
async def test_endpoint(aiohttp_client):
    client = await aiohttp_client(app)
    resp = await client.get("/")
    assert resp.status == 200
```

Both sync and async tests coexist in the same file. In auto mode, async tests are detected automatically. In strict mode, mark them with `@pytest.mark.asyncio`.

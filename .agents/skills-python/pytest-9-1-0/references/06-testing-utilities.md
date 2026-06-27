# Testing Utilities Reference

## monkeypatch

The `monkeypatch` fixture safely patches objects, environment variables, dictionaries, and sys.path. All modifications are automatically undone after the test.

### Methods

| Method | Description |
|---|---|
| `setattr(obj, name, value, raising=True)` | Set an attribute on an object |
| `delattr(obj, name, raising=True)` | Delete an attribute |
| `setitem(mapping, name, value)` | Set a dict item |
| `delitem(obj, name, raising=True)` | Delete a dict item |
| `setenv(name, value, prepend=None)` | Set environment variable |
| `delenv(name, raising=True)` | Delete environment variable |
| `syspath_prepend(path)` | Prepend to sys.path (invalidates import caches) |
| `chdir(path)` | Change working directory |
| `context()` | Context manager for scoped patches |

### Patching Functions

```python
from pathlib import Path

def test_getssh(monkeypatch):
    def mock_home():
        return Path("/abc")
    monkeypatch.setattr(Path, "home", mock_home)
    assert get_ssh_path() == Path("/abc/.ssh")
```

### Patching with Mock Classes

```python
import requests

class MockResponse:
    @staticmethod
    def json():
        return {"key": "value"}

def test_api(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(requests, "get", mock_get)
    result = my_app.fetch_data("https://api.example.com")
    assert result["key"] == "value"
```

### Environment Variables

```python
def test_with_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    assert get_database_url() == "sqlite:///test.db"

def test_missing_env(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        load_secret()
```

### Scoped Patches with context()

Use `monkeypatch.context()` when patching stdlib or shared objects to limit blast radius:

```python
import functools

def test_partial(monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(functools, "partial", 3)
        assert functools.partial == 3
    # Patch automatically undone
```

### Global Prevention Pattern

```python
# conftest.py — prevent all HTTP requests in tests
@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")
```

**Important**: Patch the reference your code uses, not the original. If code does `from os import getcwd`, patch `mymodule.getcwd`, not `os.getcwd`.

## tmp_path and tmp_path_factory

### tmp_path (function-scoped)

Provides a unique `pathlib.Path` temp directory per test:

```python
def test_file_ops(tmp_path):
    subdir = tmp_path / "data"
    subdir.mkdir()
    file = subdir / "hello.txt"
    file.write_text("content", encoding="utf-8")
    assert file.read_text(encoding="utf-8") == "content"
    assert len(list(tmp_path.iterdir())) == 1
```

### tmp_path_factory (session-scoped)

Create arbitrary temp directories from any fixture or test:

```python
@pytest.fixture(scope="session")
def shared_data_dir(tmp_path_factory):
    """Generate expensive data once per session."""
    dir = tmp_path_factory.mktemp("shared_data")
    img = generate_expensive_image()
    img.save(dir / "reference.png")
    return dir

def test_histogram(shared_data_dir):
    img = load_image(shared_data_dir / "reference.png")
    assert compute_histogram(img) == expected
```

### Retention Policy

By default, pytest keeps temp directories from the last 3 runs. Configure:

```toml
[pytest]
tmp_path_retention_count = 5
tmp_path_retention_policy = "all"  # "all", "failed", or "none"
```

## Output Capture

### capsys — sys.stdout/stderr Capture

```python
def test_output(capsys):
    print("hello")
    import sys
    sys.stderr.write("world\n")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
    assert captured.err == "world\n"
```

`readouterr()` returns a namedtuple with `out` and `err`. Calling it multiple times gives incremental snapshots.

### capfd — File Descriptor Capture

Captures at the OS file descriptor level (FD 1 and 2), catching output from subprocesses and C extensions:

```python
def test_subprocess_output(capfd):
    import subprocess
    subprocess.run(["echo", "hello"])
    captured = capfd.readouterr()
    assert "hello" in captured.out
```

### capteesys — Passthrough Capture

Like `capsys` but passes output through to the real stdout/stderr:

```python
def test_live_and_captured(capteesys):
    print("visible and captured")
    captured = capteesys.readouterr()
    assert captured.out == "visible and captured\n"
```

### Disabling Capture Temporarily

```python
def test_partial_capture(capsys):
    print("captured")
    with capsys.disabled():
        print("goes directly to terminal")
    print("captured again")
```

## caplog — Log Capture

### Basic Usage

```python
import logging

def test_log_output(caplog):
    caplog.set_level(logging.INFO)
    logger = logging.getLogger()
    logger.info("test message")
    assert "test message" in caplog.text
```

### Per-Logger Level Control

```python
def test_specific_logger(caplog):
    with caplog.at_level(logging.DEBUG, logger="myapp.database"):
        do_database_operation()
    assert any("query executed" in r.message for r in caplog.records)
```

### Inspecting Records

```python
def test_log_details(caplog):
    caplog.set_level(logging.WARNING)
    func_that_warns()
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
    # Check specific tuples
    assert ("root", logging.INFO, "boo arg") in caplog.record_tuples
```

### Multi-Stage Access

`caplog.records` only contains records from the current stage (setup/call/teardown). Use `get_records()` for other stages:

```python
@pytest.fixture
def monitored_window(caplog):
    window = create_window()
    yield window
    # Check logs from setup and call phases during teardown
    for when in ("setup", "call"):
        warnings = [r.message for r in caplog.get_records(when)
                     if r.levelno == logging.WARNING]
        assert not warnings, f"Warnings in {when}: {warnings}"
```

### Clearing Records

```python
def test_with_clear(caplog):
    noisy_setup()
    caplog.clear()
    do_the_thing()
    assert len(caplog.records) == 1
```

## cache — Cross-Session Storage

Store and retrieve JSON-serializable values between pytest runs:

```python
@pytest.fixture
def cached_data(pytestconfig):
    cache = pytestconfig.cache
    val = cache.get("expensive/computation", None)
    if val is None:
        val = compute_expensive_value()
        cache.set("expensive/computation", val)
    return val
```

### CLI

```bash
pytest --cache-show          # Show all cached values
pytest --cache-show "ex/*"   # Filter by glob
pytest --cache-clear         # Clear all cache
```

## subtests (9.0+)

Group assertions within a single test so failures don't interrupt execution:

```python
def test_multiple(subtests):
    for i in range(5):
        with subtests.test(msg="iteration", i=i):
            assert i % 2 == 0
    # All iterations run even if some fail
```

Output shows each failed subtest individually as `SUBFAILED`. The parent test fails if any subtest fails.

### Mixing with Normal Assertions

```python
def test_mixed(subtests):
    for i in range(5):
        with subtests.test("stage 1", i=i):
            assert process(i) is not None
    assert final_result() == expected  # Regular assertion outside subtests
```

### Parametrization vs Subtests

| | Parametrization | Subtests |
|---|---|---|
| When | Collection time | Runtime |
| CLI selection | `pytest test.py::test[x]` | Not individually selectable |
| Interrupt on failure | Yes (unless `-x` disabled) | No — all iterations run |
| Use case | Known parameter sets | Dynamic/unknown iterations |

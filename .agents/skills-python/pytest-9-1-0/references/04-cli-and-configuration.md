# CLI and Configuration Reference

## Configuration Files

pytest searches for configuration files from the common ancestor of test paths upward. Priority (highest to lowest):

1. `pytest.toml` or `.pytest.toml` (9.0+)
2. `pytest.ini` or `.pytest.ini`
3. `pyproject.toml` — `[tool.pytest]` section (9.0+, native TOML types) or `[tool.pytest.ini_options]` (legacy INI-style)
4. `tox.ini` — `[pytest]` section
5. `setup.cfg` — `[tool:pytest]` section (not recommended)

### pytest.toml (Preferred, 9.0+)

```toml
[pytest]
minversion = "9.0"
addopts = ["-ra", "-q", "--strict-markers"]
testpaths = ["tests", "integration"]
python_files = ["test_*.py", "*_test.py"]
markers = [
    "slow: marks tests as slow",
    "serial: tests must run serially",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning:old_module",
]
```

### pyproject.toml

```toml
# Native TOML (9.0+)
[tool.pytest]
addopts = ["-ra", "-q"]
testpaths = ["tests"]

# Legacy INI-style (6.0+)
[tool.pytest.ini_options]
addopts = "-ra -q"
testpaths = ["tests"]
```

### pytest.ini

```ini
[pytest]
minversion = 6.0
addopts = -ra -q
testpaths = tests integration
```

## Key Configuration Options

| Option | Type | Description |
|---|---|---|
| `addopts` | list/str | Default CLI options applied to every run |
| `testpaths` | list of paths | Directories to search when no args given |
| `python_files` | list | Patterns for test files (default: `test_*.py`, `*_test.py`) |
| `python_classes` | list | Class name patterns (default: `Test*`) |
| `python_functions` | list | Function name patterns (default: `test_*`) |
| `norecursedirs` | list | Directories to skip during recursion |
| `minversion` | str | Minimum pytest version required |
| `markers` | list | Register custom markers |
| `filterwarnings` | list | Warning filters |
| `tmp_path_retention_count` | int | Number of tmp dirs to keep (default: 3) |
| `tmp_path_retention_policy` | str | `"all"`, `"failed"`, or `"none"` |
| `empty_parameter_set_mark` | str | Behavior when parametrize has empty list |
| `pythonpath` | list | Directories added to sys.path |
| `strict` | bool | Enable all strict options at once (9.0+) |
| `strict_config` | bool | Error on unknown config options |
| `strict_markers` | bool | Error on unregistered markers |
| `strict_parametrization_ids` | bool | Error on duplicate parametrization IDs |
| `strict_xfail` | bool | XPASS is a failure |
| `max_warnings` | int | Max warnings before exit code 6 (9.1+) |

## Strict Mode (9.0+)

Enable all strictness options at once:

```toml
[pytest]
strict = true
```

This enables: `strict_config`, `strict_markers`, `strict_parametrization_ids`, `strict_xfail`. Individual options can still be toggled off:

```toml
[pytest]
strict = true
strict_parametrization_ids = false
```

## Command-Line Options

### Output Control

| Option | Description |
|---|---|
| `-v`, `--verbose` | Verbose output |
| `-q`, `--quiet` | Quiet output |
| `-s` | Disable output capture (show print statements) |
| `--tb=style` | Traceback style: `long`, `short`, `no`, `line`, `native`, `auto`, `compact`, `verbose` |
| `--no-header` | Suppress header |
| `--no-summary` | Suppress summary |
| `-r chars` | Show extra report: `f`ailed, `E`rror, `s`kipped, `x`failed, `X`passed, `p`assed, `P`assed with output, `a`ll except passed, `A`ll |

### Test Selection

| Option | Description |
|---|---|
| `-k EXPR` | Keyword expression |
| `-m MARKEXPR` | Marker expression |
| `--ignore=path` | Ignore a file/dir during collection |
| `--deselect=id` | Deselect a test by node ID |
| `--collect-only` | Only collect, don't run |
| `--co -q` | List collected tests quietly |

### Failure Handling

| Option | Description |
|---|---|
| `-x` | Stop at first failure |
| `--strict-markers` | Unknown markers are errors |
| `--strict-config` | Unknown config options are errors |
| `--maxfail=num` | Stop after N failures |
| `--lf`, `--last-failed` | Only run tests that failed last time |
| `--ff`, `--failed-first` | Run last failures first, then rest |
| `--nf`, `--new-first` | Run new/changed tests first |
| `--sw`, `--stepwise` | Stop at first failure, resume from there next run |

### Output and Logging

| Option | Description |
|---|---|
| `--capture=method` | `fd` (default), `sys`, `no`, `tee-sys` |
| `--show-capture` | When to show captured output on failure |
| `--log-cli-level=LEVEL` | Enable live log output at given level |
| `--log-file=path` | Write logs to file |
| `--log-format=format` | Log message format |

### Warnings

| Option | Description |
|---|---|
| `-W arg` | Warning filter (like Python's `-W`) |
| `--max-warnings=N` | Exit code 6 if warnings exceed N (9.1+) |
| `--disable-warnings` | Suppress warning summary |

### Doctest

| Option | Description |
|---|---|
| `--doctest-modules` | Run doctests in source code docstrings |
| `--doctest-glob=pattern` | Additional glob for text doctest files |
| `--doctest-continue-on-failure` | Report all failures, not just first |

### Profiling

```bash
pytest --durations=10          # Show 10 slowest tests
pytest --durations=10 --durations-min=1.0  # Only show tests > 1s
```

### Cache

```bash
pytest --cache-show             # Inspect cache contents
pytest --cache-show "example/*" # Filter by glob
pytest --cache-clear            # Clear all cache
```

### Plugin Control

```bash
pytest -p no:doctest            # Disable a plugin
pytest -p myplugin              # Early-load a plugin
pytest --disable-plugin-autoload  # Disable auto-loading (8.4+)
pytest --trace-config           # Show loaded plugins
```

## Exit Codes

| Code | Name | Meaning |
|---|---|---|
| 0 | `OK` | All tests passed |
| 1 | `TESTS_FAILED` | Some tests failed |
| 2 | `INTERRUPTED` | User interrupted |
| 3 | `INTERNAL_ERROR` | Internal pytest error |
| 4 | `USAGE_ERROR` | CLI usage error |
| 5 | `NO_TESTS_COLLECTED` | No tests found |
| 6 | `MAX_WARNINGS_ERROR` | Warning threshold exceeded (9.1+) |

```python
from pytest import ExitCode
print(ExitCode.TESTS_FAILED)  # 1
```

## Environment Variables

| Variable | Description |
|---|---|
| `PYTEST_ADDOPTS` | Extra CLI options (like permanent `addopts`) |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD` | Disable plugin auto-discovery |
| `PYTEST_PLUGINS` | Comma-separated list of plugin modules to load |
| `PYTEST_DEBUG_TEMPROOT` | Override temp directory root |
| `PYTHONWARNINGS` | Python warning filters (pytest respects these) |
| `PYTHONTRACEMALLOC` | Enable tracemalloc for ResourceWarning context |

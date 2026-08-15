# Marks and Selection Reference

## Marks Overview

Marks attach metadata to test functions, classes, or modules. They are used for selection, conditional execution, and plugin integration.

### Built-in Marks

| Mark | Purpose |
|---|---|
| `@pytest.mark.skip` | Always skip a test |
| `@pytest.mark.skipif` | Conditionally skip |
| `@pytest.mark.xfail` | Expect test to fail |
| `@pytest.mark.parametrize` | Run test with multiple argument sets |
| `@pytest.mark.usefixtures` | Activate fixtures without declaring them as arguments |
| `@pytest.mark.filterwarnings` | Filter warnings for specific tests |

### Custom Marks

Register in config to avoid warnings:

```toml
# pytest.toml
[pytest]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "serial: tests must run serially",
    "db: tests requiring a database",
]
```

Or programmatically:

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
```

Apply to individual tests:

```python
@pytest.mark.slow
def test_heavy_computation():
    ...
```

Apply to classes or modules:

```python
@pytest.mark.slow
class TestHeavyStuff:
    def test_one(self): ...
    def test_two(self): ...
```

Module-level via `pytestmark`:

```python
pytestmark = pytest.mark.slow  # Applies to all tests in module
```

### Strict Markers

Unregistered marks emit warnings. Enable strict mode to turn them into errors:

```toml
[pytest]
strict_markers = true
```

Or `--strict-markers` on CLI.

## Skipping Tests

### Unconditional Skip

```python
@pytest.mark.skip(reason="not implemented yet")
def test_todo():
    ...
```

### Conditional Skip (skipif)

```python
import sys

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX only")
def test_posix_feature():
    ...
```

Condition is evaluated at collection time. Share markers between modules:

```python
# conftest.py or shared module
minversion = pytest.mark.skipif(
    mymodule.__version__ < (1, 0),
    reason="requires mymodule >= 1.0"
)

# test_file.py
from conftest import minversion

@minversion
def test_feature():
    ...
```

### Imperative Skip

```python
def test_function():
    if not valid_config():
        pytest.skip("unsupported configuration")
    # rest of test...
```

### Module-Level Skip

```python
import sys
import pytest

if not sys.platform.startswith("win"):
    pytest.skip("windows-only tests", allow_module_level=True)
```

### Skip on Missing Import

```python
docutils = pytest.importorskip("docutils")
numpy = pytest.importorskip("numpy", minversion="1.20")
```

Skips the test if the import fails. Optionally checks version via `__version__`.

## XFail (Expected Failure)

### Basic Usage

```python
@pytest.mark.xfail(reason="known parser bug #1234")
def test_parser_bug():
    assert parse("input") == expected
```

- **XFAIL**: Test fails as expected — reported as expected failure
- **XPASS**: Test passes despite xfail — reported as unexpected pass

### With Condition

```python
@pytest.mark.xfail(sys.platform == "win32", reason="bug on Windows")
def test_feature():
    ...
```

### With Expected Exception

```python
@pytest.mark.xfail(raises=RuntimeError)
def test_crashes():
    buggy_function()
```

If a different exception is raised, it's reported as a regular failure.

### Strict XFail

```python
@pytest.mark.xfail(strict=True)  # XPASS becomes a failure
def test_should_fail():
    ...
```

Enable globally: `strict_xfail = true` in config.

### Imperative xfail

```python
def test_function():
    if slow_module.slow_check():
        pytest.xfail("too slow")
    # No code after this runs — raises internally
```

### Ignore xfail Markers

```bash
pytest --runxfail  # Treat all xfail tests as normal
```

## Parametrization

### Basic Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    ("3+5", 8),
    ("2+4", 6),
    ("6*9", 54),
])
def test_eval(input, expected):
    assert eval(input) == expected
```

Each parameter set runs as a separate test instance.

### Multiple Parametrization (Cartesian Product)

```python
@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_foo(x, y):
    pass
# Runs: (0,2), (1,2), (0,3), (1,3) — inner decorator varies fastest
```

### Marking Individual Parameters

```python
@pytest.mark.parametrize("n,expected", [
    (1, 2),
    pytest.param(1, 0, marks=pytest.mark.xfail),
    pytest.param(1, 3, marks=pytest.mark.skip(reason="known issue")),
    (2, 3),
])
def test_increment(n, expected):
    assert n + 1 == expected
```

### Custom IDs

```python
@pytest.mark.parametrize("input,expected", [
    ("3+5", 8),
    ("2+4", 6),
], ids=["sum-3-5", "sum-2-4"])
def test_eval(input, expected):
    ...
```

Or via callable:

```python
@pytest.mark.parametrize("data", complex_data, ids=lambda d: d.name)
def test_complex(data):
    ...
```

### Parametrized Fixtures

```python
@pytest.fixture(params=["sqlite", "postgres"])
def db(request):
    return create_db(request.param)

def test_query(db):
    # Runs twice — once per param
    assert db.query("SELECT 1")
```

### pytest_generate_tests Hook

For dynamic parametrization:

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption("--stringinput", action="append", default=[])

def pytest_generate_tests(metafunc):
    if "stringinput" in metafunc.fixturenames:
        values = metafunc.config.getoption("stringinput")
        metafunc.parametrize("stringinput", values)
```

This hook can also be defined in test modules or classes (unlike other hooks).

## Test Selection

### By File/Directory

```bash
pytest test_mod.py
pytest tests/unit/
```

### By Node ID

```bash
pytest test_mod.py::test_func
pytest test_mod.py::TestClass::test_method
pytest test_mod.py::test_func[param1-param2]
```

### By Keyword Expression (-k)

```bash
pytest -k "MyClass and not method"    # Python-like expression
pytest -k "test_login or test_logout" # OR logic
pytest -k "slow"                       # Matches any part of test name
```

### By Marker Expression (-m)

```bash
pytest -m slow
pytest -m "not slow"
pytest -m "db and not integration"
pytest -m "slow(phase=1)"             # With arguments
```

### From File (@)

```bash
pytest @tests_to_run.txt
```

File contains one argument per line (node IDs, markers, paths).

### By Package (--pyargs)

```bash
pytest --pyargs pkg.testing  # Import pkg.testing, run tests from its location
```

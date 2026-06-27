# Doctest and unittest Reference

## Test Discovery Conventions

pytest discovers tests automatically using these rules:

### File Discovery

- Recurse into directories (unless matching `norecursedirs`)
- Collect files matching `python_files` patterns (default: `test_*.py`, `*_test.py`)
- Text files matching `test*.txt` for doctests (extendable via `--doctest-glob`)

### Item Discovery (within Python files)

- Functions/methods prefixed with `test` (matching `python_functions`, default: `test_*`)
- Methods inside classes prefixed with `Test` (matching `python_classes`, default: `Test*`)
  - Class must **not** have `__init__` (prevents instantiation)
  - `@staticmethod` and `@classmethod` methods are also collected
- `unittest.TestCase` subclasses are collected as items

### Import Modes

| Mode | Behavior |
|---|---|
| `prepend` (default) | Adds test directory to sys.path; imports as top-level modules |
| `importlib` (recommended) | Uses importlib without modifying sys.path; no name conflicts |
| `append` | Appends test directory to sys.path |

For new projects, use `--import-mode=importlib`:

```toml
[pytest]
addopts = ["--import-mode=importlib"]
```

## Project Layout Patterns

### src Layout (Recommended)

```
pyproject.toml
src/
    mypkg/
        __init__.py
        app.py
tests/
    conftest.py
    test_app.py
```

- Tests run against installed package (`pip install -e .`)
- Use `--import-mode=importlib` to avoid import issues

### Inlined Tests

```
pyproject.toml
mypkg/
    __init__.py
    app.py
    tests/
        test_app.py
```

Run with: `pytest --pyargs mypkg`

## Doctest Integration

### Running Doctests from Text Files

By default, pytest collects `test*.txt` files containing doctest directives:

```
# content of test_example.txt
>>> x = 3
>>> x
3
```

Run with: `pytest` (auto-collected) or specify additional globs:

```bash
pytest --doctest-glob="*.rst" --doctest-glob="*.md"
```

### Running Doctests from Docstrings

```python
# mymodule.py
def factorial(n):
    """
    >>> factorial(5)
    120
    >>> factorial(0)
    1
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

Run with: `pytest --doctest-modules mymodule.py`

### Doctest Options

Configure in pytest config:

```toml
[pytest]
doctest_optionflags = ["NORMALIZE_WHITESPACE", "IGNORE_EXCEPTION_DETAIL"]
```

Or inline in docstrings:

```python
def example():
    """
    >>> something()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: ...
    """
```

### pytest-Specific Doctest Options

| Option | Description |
|---|---|
| `ALLOW_UNICODE` | Strip `u` prefix from unicode strings in expected output |
| `ALLOW_BYTES` | Strip `b` prefix from byte strings in expected output |
| `NUMBER` | Compare floats by precision written (uses `pytest.approx`) |

### Using Fixtures in Doctests

```rst
# example.rst
>>> tmp = getfixture('tmp_path')
>>> file = tmp / "test.txt"
>>> file.write_text("hello")
5
```

The fixture must be defined in a visible `conftest.py` or plugin.

### doctest_namespace Fixture

Inject objects into doctest namespace:

```python
# conftest.py
@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    import numpy
    doctest_namespace["np"] = numpy
```

Then in docstrings: `>>> np.array([1, 2, 3])`

### Skipping Doctest Checks

```python
def example():
    """
    >>> random.random()  # doctest: +SKIP
    0.5

    >>> 1 + 1
    2
    """
```

Or use `pytest.skip()` / `pytest.xfail()` in doctests (discouraged — reduces readability).

## unittest Compatibility

pytest runs standard `unittest.TestCase` tests natively:

```python
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)

    def setUp(self):
        self.data = [1, 2, 3]

    def tearDown(self):
        self.data = None
```

Run with: `pytest test_math.py` (no special flags needed).

### pytest Fixtures in unittest Tests

```python
import unittest

class TestWithFixtures(unittest.TestCase):
    # Request pytest fixtures as class attributes
    db = None  # Will be injected if 'db' fixture exists

    def test_query(self, db):
        # Use fixture as method argument
        assert db.query("SELECT 1")
```

### xunit-style setUp/tearDown

pytest supports the classic `xunit_setup` pattern:

```python
# Module-level
def setup_function(function):
    print(f"Setting up {function.__name__}")

def teardown_function(function):
    print(f"Tearing down {function.__name__}")

# Class-level
class TestExample:
    @classmethod
    def setup_class(cls):
        cls.shared = create_expensive_resource()

    @classmethod
    def teardown_class(cls):
        cls.shared.close()

    def setup_method(self, method):
        self.local = prepare_for(method)

    def teardown_method(self, method):
        cleanup(self.local)

    def test_one(self):
        ...
```

Order: `setup_class` → `setup_method` → test → `teardown_method` → (next method) → ... → `teardown_class`.

## Customizing Test Collection

### Ignoring Paths

```toml
[pytest]
norecursedirs = ["venv", ".git", "build", "node_modules"]
```

Or programmatically:

```python
def pytest_ignore_collect(collection_path, config):
    if collection_path.name.startswith("legacy_"):
        return True
```

### Custom Collection via Hooks

```python
def pytest_collect_file(file_path, parent):
    if file_path.suffix == ".yaml":
        return YamlFile.from_parent(parent, path=file_path)
```

## xunit_setup vs Fixtures

| | xunit_setup | Fixtures |
|---|---|---|
| Composition | Limited (inheriting classes) | Full dependency injection |
| Scope control | Implicit (method/class/module) | Explicit (`scope=` parameter) |
| Parametrization | Not supported | Native support |
| Reusability | Inheritance only | Request by name from anywhere |
| Teardown | Separate method | `yield` pattern or `addfinalizer` |

Fixtures are the preferred approach. Use `xunit_setup` when migrating from unittest or when simple per-test setup suffices.

# Fixtures Reference

Fixtures are pytest's dependency injection system. They replace unittest-style `setUp`/`tearDown` with composable, scoped functions that provide test dependencies.

## Defining Fixtures

```python
import pytest

@pytest.fixture
def simple_fixture():
    return 42

@pytest.fixture
def yield_fixture():
    # setup
    resource = create_resource()
    yield resource
    # teardown (always runs, even on failure)
    resource.close()
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `scope` | str or callable | `"function"` | One of: `"function"`, `"class"`, `"module"`, `"package"`, `"session"` |
| `params` | iterable | `None` | Values that cause multiple fixture invocations; access via `request.param` |
| `autouse` | bool | `False` | If True, fixture activates for all tests in scope without explicit request |
| `ids` | seq or callable | `None` | Custom IDs for parametrized fixture instances in test names |
| `name` | str | `None` | Override the fixture name (useful when function name is shadowed by argument) |

## Fixture Scopes

Scopes determine how long a fixture instance lives and how many tests share it:

- **`function`** (default): One instance per test function. Created before, destroyed after.
- **`class`**: One instance per test class. Shared by all methods in the class.
- **`module`**: One instance per test module (`.py` file). Shared across the file.
- **`package`**: One instance per package (directory with `__init__.py`). Shared across the package.
- **`session`**: One instance per pytest run. Global singleton for the session.

Higher-scoped fixtures execute before lower-scoped ones within a test's fixture chain.

### Dynamic Scope

```python
@pytest.fixture(scope=lambda name, config: "session" if config.getoption("--fast") else "function")
def dynamic_scope_fixture():
    ...
```

## Fixture Availability and conftest.py

Fixtures are discovered from the test's perspective, searching upward through scopes:

1. Test function's own module (local fixtures)
2. `conftest.py` in the same directory
3. `conftest.py` in parent directories (up to rootdir)
4. Third-party plugins (loaded last)

The first fixture found wins, enabling **override by proximity**.

### conftest.py Structure

```
project/
├── conftest.py          # Global fixtures for entire project
├── tests/
│   ├── conftest.py      # Fixtures for all tests/ subdirectories
│   ├── test_api.py
│   └── integration/
│       ├── conftest.py  # Fixtures only for integration tests
│       └── test_db.py
```

- `conftest.py` is **never imported** — pytest auto-discovers it
- Each directory can have its own `conftest.py` with scoped fixtures
- Parent `conftest.py` fixtures are available to child directories
- Child directories cannot access sibling `conftest.py` fixtures

## Fixture Execution Order

Three factors determine order (in priority):

1. **Scope**: Higher scope first (session → package → module → class → function)
2. **Dependencies**: If fixture A requests fixture B, B executes first
3. **Autouse**: Autouse fixtures execute before explicitly requested ones within their scope

Names, definition order, and request order have no bearing on execution order.

### Example

```python
@pytest.fixture(scope="session")
def database():
    # Executes first (session scope)
    db = connect()
    yield db
    db.close()

@pytest.fixture
def user(database):
    # Depends on database, so executes after it
    return database.create_user("alice")

@pytest.fixture(autouse=True)
def log_test(request):
    # Autouse: runs before other function-scoped fixtures
    print(f"Running {request.node.name}")

def test_something(user):
    # Fixture chain: log_test → database → user → test_something
    assert user.name == "alice"
```

## Parametrized Fixtures

```python
@pytest.fixture(params=["sqlite", "postgres"])
def db_driver(request):
    return create_driver(request.param)

def test_connect(db_driver):
    # Runs twice: once with sqlite, once with postgres
    assert db_driver.connect()
```

Access the current parameter value via `request.param` inside the fixture.

## The `request` Fixture

Every fixture can request the special `request` fixture to access test context:

| Attribute | Description |
|---|---|
| `request.node` | The test item/collector node |
| `request.config` | The pytest Config object |
| `request.function` | The test function (function-scoped only) |
| `request.cls` | The test class (class-scoped only) |
| `request.instance` | The test class instance |
| `request.module` | The module containing the test |
| `request.path` | Path to the test file |
| `request.fixturenames` | Names of fixtures available to this test |
| `request.param` | Current parameter value (for parametrized fixtures) |
| `request.addfinalizer(func)` | Register a cleanup callback |

```python
@pytest.fixture
def temp_file(request):
    f = tempfile.NamedTemporaryFile(delete=False)
    request.addfinalizer(lambda: os.unlink(f.name))
    return f.name
```

## Built-in Fixtures

| Fixture | Scope | Description |
|---|---|---|
| `tmp_path` | function | Unique `pathlib.Path` temp directory per test |
| `tmp_path_factory` | session | Factory for creating temp directories at any scope |
| `capsys` | function | Capture `sys.stdout`/`sys.stderr` as text |
| `capfd` | function | Capture file descriptors 1 and 2 as text |
| `caplog` | function | Control logging level and access log records |
| `cache` | session | Store/retrieve values across pytest runs |
| `monkeypatch` | function | Safely patch attributes, env vars, dicts, sys.path |
| `pytestconfig` | function | Access configuration values and plugin hooks |
| `recwarn` | function | Record warnings emitted during the test |
| `subtests` | function | Group assertions as subtests (9.0+) |

## Autouse Fixtures

```python
@pytest.fixture(autouse=True, scope="module")
def setup_module():
    print("Module setup")
    yield
    print("Module teardown")
```

Autouse fixtures activate for all tests in their scope without being explicitly requested. Use sparingly — they make test dependencies implicit and harder to reason about.

## Fixture Composition

Fixtures can request other fixtures, building a dependency tree:

```python
@pytest.fixture
def browser():
    br = Browser()
    yield br
    br.quit()

@pytest.fixture
def logged_in_user(browser):
    user = User("alice")
    browser.login(user)
    return user

@pytest.fixture
def admin_session(logged_in_user, database):
    logged_in_user.grant_admin()
    return logged_in_user
```

The chain resolves automatically: `database` → `browser` → `logged_in_user` → `admin_session`.

## Common Patterns

### Factory Pattern (avoiding shared state in session-scoped fixtures)

```python
@pytest.fixture(scope="session")
def user_factory(tmp_path_factory):
    """Returns a callable that creates isolated users."""
    db = Database.connect()
    yield lambda name: db.create_user(name, tmp_path_factory.mktemp(f"user-{name}"))
    db.close()

def test_one(user_factory):
    user = user_factory("alice")  # Each call gets fresh state

def test_two(user_factory):
    user = user_factory("bob")  # Independent from test_one
```

### Named Fixture with Shadowed Function Name

```python
@pytest.fixture(name="config")
def fixture_config():
    """The function name avoids shadowing the 'config' argument."""
    return load_config()

def test_something(config):
    assert config.debug is False
```

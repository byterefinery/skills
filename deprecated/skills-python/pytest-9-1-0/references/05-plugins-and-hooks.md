# Plugins and Hooks Reference

## Plugin Architecture

pytest is built on [pluggy](https://pluggy.readthedocs.io/), a library for managing plugin hooks. Every aspect of pytest — configuration, collection, running, reporting — is implemented through hook calls.

### Plugin Discovery Order

1. `-p no:name` blocks plugins (before normal parsing)
2. Built-in plugins (`_pytest/`)
3. `-p name` early-loads specific plugins
4. Third-party plugins via `pytest11` entry points
5. Plugins from `PYTEST_PLUGINS` environment variable
6. Initial `conftest.py` files (loaded per test path, parent-first)

### conftest.py: Local Per-Directory Plugins

`conftest.py` files are auto-discovered in test directories. They provide directory-scoped fixtures and hook implementations.

```
tests/
├── conftest.py          # Available to all tests/ subdirectories
├── test_api.py
└── integration/
    ├── conftest.py      # Only for integration/ tests
    └── test_db.py
```

Key rules:
- Never `import conftest` — pytest loads it automatically
- Hooks in `conftest.py` apply only to tests in that directory tree
- Parent `conftest.py` fixtures are available to child directories
- Child cannot access sibling `conftest.py` fixtures

### Loading Plugins Programmatically

```python
# In a test module or conftest.py
pytest_plugins = ["myapp.testsupport.myplugin"]
```

Plugins loaded this way are processed recursively (if the loaded plugin also declares `pytest_plugins`). Note: using `pytest_plugins` in non-root `conftest.py` is deprecated.

## Hook Functions

Hooks are functions that plugins implement to interact with pytest's lifecycle. All hooks start with `pytest_`.

### Hook Validation

pytest validates argument names against the hook specification. Extra parameters in the spec that you don't need can be omitted — pytest prunes dynamically, ensuring forward compatibility.

```python
def pytest_collection_modifyitems(config, items):
    # 'session' parameter from spec is omitted — fine
    items.sort(key=lambda x: x.name)
```

### Hook Ordering

```python
import pytest

@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    # Executes as early as possible
    ...

@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items):
    # Executes as late as possible
    ...

@pytest.hookimpl(wrapper=True)
def pytest_collection_modifyitems(items):
    # Wraps all other implementations
    result = yield
    return result
```

Execution order: wrappers → tryfirst → normal → trylast → wrapper post-yield.

### Hook Wrappers

```python
import pytest

@pytest.hookimpl(wrapper=True)
def pytest_pyfunc_call(pyfuncitem):
    start_time = time.time()
    outcome = yield
    elapsed = time.time() - start_time
    pyfuncitem.stash[elapsed_key] = elapsed
    return outcome
```

The wrapper yields once. Code before `yield` runs before other hooks; code after runs after. If underlying hooks raise, the exception propagates to `yield`.

### firstresult Hooks

Some hooks use `firstresult=True`, meaning only the first non-None return value is used:

```python
# Only one plugin's implementation will take effect
def pytest_pyfunc_call(pyfuncitem):
    # If this returns True, other implementations are skipped
    if should_handle(pyfuncitem):
        handle_test(pyfuncitem)
        return True
```

## Key Hook Specifications

### Session Lifecycle

| Hook | When Called |
|---|---|
| `pytest_sessionstart(session)` | Before any test activity |
| `pytest_configure(config)` | After config parsing, before collection |
| `pytest_collection(session)` | Before collecting tests |
| `pytest_collection_modifyitems(session, config, items)` | After collection, can modify item list |
| `pytest_collection_finish(session)` | After collection completes |
| `pytest_runtestloop(session)` | Override the entire test loop |
| `pytest_sessionfinish(session, exitstatus)` | After all tests complete |
| `pytest_unconfigure(config)` | Final cleanup |

### Test Execution

| Hook | When Called |
|---|---|
| `pytest_runtest_setup(item)` | Before test (fixture setup phase) |
| `pytest_runtest_call(item)` | During test execution |
| `pytest_runtest_teardown(item, nextitem)` | After test (teardown phase) |
| `pytest_runtest_makereport(item, call)` | Create report for a test phase |
| `pytest_runtest_logreport(report)` | Log a test report |

### Collection

| Hook | When Called |
|---|---|
| `pytest_ignore_collect(path, config)` | Return True to skip a path |
| `pytest_collect_directory(path, parent)` | Custom directory collection |
| `pytest_collect_file(file_path, parent)` | Custom file collection |
| `pytest_pycollect_makeitem(name, obj, owner)` | Custom item creation from Python objects |
| `pytest_generate_tests(metafunc)` | Dynamic parametrization |

### Configuration

| Hook | When Called |
|---|---|
| `pytest_addoption(parser, pluginmanager)` | Add CLI options and ini settings |
| `pytest_addhooks(pluginmanager)` | Declare new hook specs |
| `pytest_cmdline_parse(pluginmanager, args)` | Early command-line parsing |

## Writing a Plugin

### Basic Plugin with Fixture

```python
# myplugin.py
import pytest

@pytest.fixture
def api_client():
    client = APIClient(base_url="http://localhost:8000")
    yield client
    client.close()
```

### Plugin with CLI Option

```python
def pytest_addoption(parser):
    parser.addoption(
        "--api-url",
        action="store",
        default="http://localhost:8000",
        help="Base URL for API tests",
    )

@pytest.fixture
def api_base_url(request):
    return request.config.getoption("--api-url")
```

### Plugin Entry Point (Installable)

```toml
# pyproject.toml
[project.entry-points.pytest11]
myplugin = "myplugin.plugin"
```

### Testing Plugins with pytester

```python
# conftest.py
pytest_plugins = ["pytester"]

# test_plugin.py
def test_hello(pytester):
    pytester.makeconftest("""
        import pytest
        @pytest.fixture
        def my_fixture():
            return 42
    """)
    pytester.makepyfile("""
        def test_it(my_fixture):
            assert my_fixture == 42
    """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
```

## Storing Data on Items (Stash)

Use `item.stash` instead of private attributes for type-safe cross-hook data sharing:

```python
import pytest

been_there_key = pytest.StashKey[bool]()
elapsed_key = pytest.StashKey[float]()

def pytest_runtest_setup(item: pytest.Item) -> None:
    item.stash[been_there_key] = True

def pytest_runtest_teardown(item: pytest.Item, nextitem) -> None:
    if not item.stash[been_there_key]:
        print("Setup was skipped!")
```

Stashes are available on all node types (`Item`, `Class`, `Session`, `Config`).

## Declaring Custom Hooks

```python
# hooks.py
def pytest_my_custom_hook(config):
    """Called with the config object. Return value is collected."""

# plugin.py
def pytest_addhooks(pluginmanager):
    from my_app.tests import hooks
    pluginmanager.add_hookspecs(hooks)
```

Other plugins implement the hook:

```python
# In conftest.py
def pytest_my_custom_hook(config):
    print("Custom hook called!")
```

Call your hook from a fixture or another hook:

```python
@pytest.fixture
def my_fixture(pytestconfig):
    results = pytestconfig.hook.pytest_my_custom_hook(config=pytestconfig)
    return results
```

## Common Plugin Patterns

### Conditional Plugin Loading

```python
class XDistPlugin:
    def pytest_testnodedown(self, node, error):
        ...

def pytest_configure(config):
    if config.pluginmanager.hasplugin("xdist"):
        config.pluginmanager.register(XDistPlugin())
```

### Accessing Another Plugin

```python
plugin = config.pluginmanager.get_plugin("name_of_plugin")
```

Get plugin names with `pytest --trace-config`.

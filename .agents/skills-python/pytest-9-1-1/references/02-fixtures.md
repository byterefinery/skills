# Fixtures

## Contents

- [The `@pytest.fixture` decorator](#the-pytestfixture-decorator)
- [Scopes](#scopes)
- [Fixture availability](#fixture-availability)
- [Overriding fixtures](#overriding-fixtures)
- [Instantiation order](#instantiation-order)
- [Parametrized fixtures](#parametrized-fixtures)
- [The `request` fixture](#the-request-fixture)
- [Class-scoped fixtures (9.1 deprecation)](#class-scoped-fixtures-91-deprecation)
- [Programmatic registration (9.1)](#programmatic-registration-91)

## The `@pytest.fixture` decorator

Fixtures are the core setup/teardown mechanism. A test (or another fixture) requests a fixture by naming it as an argument; pytest runs the fixture, captures its return value, and passes it in.

```python
import pytest

@pytest.fixture
def db_session(tmp_path):
    db = connect(tmp_path / "db.sqlite")   # may request other fixtures
    yield db                                # value visible to the test
    db.close()                              # teardown, even on failure

@pytest.fixture(scope="session")
def config_file():
    return load_config()
```

Decorator parameters:

- `scope` — `function` (default), `class`, `module`, `package`, `session`
- `params` / `ids` — make the fixture parametrized (see below)
- `autouse=True` — run for every test that can see it, even without being requested
- `name` — override the fixture name (defaults to the function name)

Teardown works two ways: code after a `yield` (fixture function becomes a generator), or `request.addfinalizer(fn)` for non-generator fixtures. Finalizers run when the fixture's scope unwinds, in reverse order of setup.

Fixtures can request other fixtures — this is how complex setup is composed. The requested fixture runs first, and its value is cached per scope: multiple requests of the same fixture within one test return the same object (side effects included), which is how tests stay isolated.

## Scopes

- Higher-scoped fixtures are instantiated **first** (session → package → module → class → function), and a fixture's value is shared across everything in its scope.
- **Scope mismatch error**: a fixture with a *larger* scope cannot request a fixture with a *smaller* scope (e.g., a `session` fixture cannot request a `function` fixture) — pytest raises `ScopeMismatch` at setup time. The reverse direction is always fine.
- `package` scope (since 4.0) covers a whole package (directory with `__init__.py`, or the test directory tree).
- Use wider scopes for expensive resources (DB connections, servers); narrow scopes for state that must not leak between tests.

## Fixture availability

Availability is determined **from the perspective of the test**:

- A fixture defined inside a class is available only to tests of that class; a module-level fixture is available to every test in the module (including tests inside classes).
- **`conftest.py` files** make fixtures available to every test in their directory and subdirectories, without imports. Nested conftest files stack — each adds to the ones from parent directories.
- The lookup searches **upward only** (test file → its conftest → parent conftests → ...): a test can never see fixtures defined "down" in a sibling directory or a deeper conftest.
- **Third-party plugin fixtures are searched last**, after all local scopes have been exhausted.
- A fixture may request other fixtures regardless of where they are defined, as long as the requesting *test* can see all of them.
- Availability is not instantiation order — see below.

Inspect what a test sees with:

```bash
pytest --fixtures [test-id]        # list fixtures (add -v to include _prefixed ones)
pytest --setup-plan [test-id]      # show the exact setup order without running
```

## Overriding fixtures

The first fixture a test finds wins — so defining a same-named fixture in a closer scope (test module, or a nearer conftest) overrides a more general one. This is the standard way to replace a plugin's fixture or specialize a shared setup.

Since 9.1, when fixtures with the same name are registered programmatically (plugins), override order is determined first by **visibility in the collection tree**: a fixture visible only at a more specific node (module, item) always beats one visible at a more general node (session), even if the general one was registered later. Fixtures with incomparable or equal visibility keep the previous "last registered wins" behavior.

## Instantiation order

pytest orders fixture setup by three factors only — scope, dependencies, autouse. Names, definition order, and request order in the signature have no bearing (don't rely on coincidences):

1. **Scope** — higher-scoped fixtures run first.
2. **Dependencies** — a fixture runs after all fixtures it requests. If order matters, express it as a dependency (request the fixture you need to run first, even if you don't use its value).
3. **Autouse** — autouse fixtures run before non-autouse ones within their scope. A fixture requested by an autouse fixture is *effectively* autouse for the tests the autouse fixture applies to (but not elsewhere).

If the graph is ambiguous (two independent chains), pytest may pick any linearization that satisfies the constraints — make ordering explicit through dependencies when behavior depends on it. Teardown is the exact reverse of setup.

## Parametrized fixtures

```python
@pytest.fixture(params=["sqlite", "postgres"], ids=lambda x: x)
def db(request):
    if request.param == "sqlite":
        db = SqliteDB()
    else:
        db = PostgresDB()
    request.addfinalizer(db.close)
    return db
```

- Every test (or fixture) requesting `db` runs once per parameter value, with `request.param` holding the current value.
- `params` may be any `Collection`; `ids` accepts a list of strings or a callable mapping each param to an id (duplicates are auto-suffixed `0`, `1`, ... unless `strict_parametrization_ids` is set — see [03-parametrize](03-parametrize.md)).
- Fixture parametrization crosses with test-level `@pytest.mark.parametrize` into the full cartesian product.
- A parametrized fixture cannot be requested by a non-parametrized context with a specific value — the parameter is fixed by the fixture's own `params` (or by indirect test parametrization, which passes values through `request.param`).

## The `request` fixture

`request` exposes information about the current test/fixture invocation:

- `request.param` — the current parameter value (in parametrized fixtures/tests)
- `request.node` — the `Item` (collected test); `request.node.nodeid`, `request.node.name`
- `request.cls` — the test class (for `unittest.TestCase` and class-based tests); `request.instance` — the instance it runs on
- `request.function` — the test function
- `request.config` — the `Config` object (same as the `pytestconfig` fixture)
- `request.fixturenames` — all fixture names the test requests (transitive closure)
- `request.getfixturevalue(name)` — request a fixture dynamically at runtime (e.g., conditionally). **Deprecated in 9.1** when used during teardown for a fixture not yet requested; that becomes an error in pytest 10. Request such fixtures before the `yield`.
- On a `Node`: `node.get_closest_marker(name)`, `node.iter_markers()` (closest-to-function first), `node.get_closest_marker` returns `None` if absent.

## Class-scoped fixtures (9.1 deprecation)

Defining a class-scoped fixture as a plain instance method is deprecated (removal in pytest 10) because it silently breaks: the fixture runs once per class on its own instance, while each test method runs on a fresh instance — so attributes set on `self` inside the fixture are invisible to the tests.

```python
class TestExample:
    @pytest.fixture(scope="class")
    @classmethod
    def setup_data(cls):
        cls.data = [1, 2, 3]      # set on the class, visible to all tests

    def test_something(self, setup_data):
        assert self.data == [1, 2, 3]
```

## Programmatic registration (9.1)

`pytest.register_fixture(name, func, node=...)` registers a fixture imperatively — intended for plugins where the decorator is impractical. Scope is controlled by the `node` (collection-tree node) parameter; `node=session` gives global visibility. The string-based `nodeid`/`baseid` parameters are deprecated and removed in pytest 10. Normally, declare fixtures with `@pytest.fixture` — pytest discovers and registers them automatically during collection.

# Fixtures

Grounded in `doc/en/how-to/fixtures.rst` and `doc/en/reference/fixtures.rst` of the 9.2.0 tag.

## Requesting fixtures

Tests request fixtures by declaring them as arguments. pytest looks up fixtures matching parameter names, runs them, and passes the returned objects into the test.

- Fixtures can **request other fixtures** the same way tests do.
- Fixtures are **reusable** — two tests requesting the same fixture each get their own execution (function scope), keeping tests isolated.
- A test/fixture can request **many fixtures** at once.
- A fixture requested multiple times per test is **executed once**; its return value (and side effects) is cached for that test. So if fixture `a` mutates an object and test `t` requests both `a` and the mutated object, both see the same instance.

## Teardown

Two mechanisms:

1. **Yield fixtures (recommended)** — `yield` instead of `return`; code after the `yield` is teardown. pytest runs fixtures up to their yield in order, then runs teardown code in **reverse order** (last set up is first torn down).
   - If a yield fixture raises *before* yielding, its post-`yield` code does not run; all fixtures that already ran successfully are still torn down.
2. **`request.addfinalizer(fn)`** — finalizers run first-in-last-out. The finalizer runs even if the fixture raises after adding it, so add the finalizer only after the state-changing action succeeds.

Safe structure: each fixture does one state-changing action with its own teardown, so a failure at any step leaves no residue.

## Scope

`@pytest.fixture(scope=...)` — possible values `function` (default), `class`, `module`, `package`, `session`:

- `function` — destroyed at the end of the test
- `class` — destroyed during teardown of the last test in the class
- `module` — destroyed during teardown of the last test in the module
- `package` — destroyed during teardown of the last test in the package where the fixture is defined (including sub-packages/dirs)
- `session` — destroyed at the end of the test session

A higher-scoped fixture is shared across all tests in that scope (same instance visible in tracebacks). Pytest caches **one instance per scope at a time**; a parametrized fixture may therefore be invoked more than once within a scope.

**Dynamic scope** (since 5.2): `scope` may be a callable returning a scope string; called once during fixture definition with keyword args `fixture_name` and `config` — useful for CLI-controlled scopes (e.g., keep docker containers across a session when a flag is set).

**Direction rule**: a fixture may use a broader-scoped fixture, but not the other way round (a session-scoped fixture cannot meaningfully use a module-scoped one).

## Autouse

`@pytest.fixture(autouse=True)` — the fixture is requested automatically by every test that can see it (no explicit argument needed). Autouse fixtures run before other fixtures in their scope, and fixtures they request become effectively autouse for those tests. Use sparingly: an autouse fixture runs for every test that can reach it.

## `request` object

Fixture functions may accept the `request` fixture to introspect the requesting context:

- `request.module` — the test module (read module-level config values)
- `request.param` — the current parameter value of a parametrized fixture
- `request.node.get_closest_marker("name")` — markers applied to the test (9.2: may pass a `MarkDecorator` as `default`)
- `request.cls` — the test class (used e.g. to set class attributes from a class-scoped fixture)

Markers can pass data into fixtures this way: `@pytest.mark.fixt_data(42)` on a test, `request.node.get_closest_marker("fixt_data").args[0]` in the fixture.

## Factories as fixtures

Return a callable instead of data when a test needs multiple independent instances:

```python
@pytest.fixture
def make_customer_record():
    created = []
    def _make(name):
        r = models.Customer(name=name); created.append(r); return r
    yield _make
    for r in created:
        r.destroy()
```

## Parametrized fixtures

`@pytest.fixture(params=[...])` runs the fixture (and all dependent tests) once per value; access via `request.param`. Test IDs include the parameter (e.g., `test_ehlo[smtp.gmail.com]`), selectable with `-k`; `ids` accepts a list of strings or a function (returning `None` falls back to auto ID). `pytest.param(value, marks=...)` marks individual fixture parameter values (e.g., skip one).

Automatic grouping: pytest minimizes active fixtures — with a parametrized module-scoped fixture, all tests run against one parameter, finalizers run, then the next parameter starts.

## `conftest.py` and fixture availability

- Fixtures in a `conftest.py` are available to every test in that directory tree without import; nested directories add their own `conftest.py` fixtures on top of parents'.
- Search is **upward only** from the test's perspective — a test can find fixtures in ancestor directories but never downward into sibling subtrees. First fixture found wins, so nearer definitions **override** farther ones (directory conftest, then test module, then plugin fixtures last).
- A fixture defined inside a class is only requestable by tests in that class.
- `pytest --fixtures [path]` lists available fixtures (leading-`_` fixtures need `-v`); `pytest --setup-plan [path]` shows fixture execution order for a test.

## Overriding fixtures

Override at:
- **Directory level** — same-named fixture in a deeper `conftest.py` (the overriding fixture can request the base to wrap it);
- **Module level** — same-named fixture in the test module;
- **Direct parametrization** — `@pytest.mark.parametrize('username', [...])` overrides the fixture value even if the test doesn't name it;
- **Parametrized ↔ non-parametrized** — either can be overridden by the other in a narrower scope.

## Using fixtures from other projects

Install plugins that provide fixtures (entry points). Without entry points, register the module in the **top-level** `conftest.py` via `pytest_plugins = "mylibrary.fixtures"`. Importing fixtures into a test module is not recommended (they become registered as defined in that module).

## `usefixtures`

`@pytest.mark.usefixtures("cleandir", "other")` (test or class), or module-level `pytestmark = pytest.mark.usefixtures(...)`, requests fixtures without naming them in test signatures. Also settable in config: `usefixtures = ["cleandir"]`. Cannot be applied to fixture functions (error).

## Instantiation order

pytest orders fixtures by three factors — names, definition order, and request order have **no** bearing:

1. **Scope** — higher-scoped fixtures run first (session before function).
2. **Dependencies** — a fixture's dependencies run before it; if the dependency graph is ambiguous, pytest may pick any linearization, so make order-bearing dependencies explicit.
3. **Autouse first within scope** — autouse fixtures (and their transitive dependencies, effectively) execute before non-autouse fixtures in the same scope.

Verify the actual order with `pytest --setup-plan`.

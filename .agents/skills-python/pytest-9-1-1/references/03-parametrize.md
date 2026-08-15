# Parametrization

## Contents

- [`@pytest.mark.parametrize`](#pytestmarkparametrize)
- [Parameter set IDs](#parameter-set-ids)
- [Per-value control with `pytest.param`](#per-value-control-with-pytestparam)
- [Stacking decorators](#stacking-decorators)
- [Class- and module-level parametrization](#class--module-level-parametrization)
- [Indirect parametrization](#indirect-parametrization)
- [Custom parametrization with `pytest_generate_tests`](#custom-parametrization-with-pytest_generate_tests)
- [9.x gotchas](#9x-gotchas)

## `@pytest.mark.parametrize`

Runs one test function multiple times with different argument sets:

```python
import pytest

@pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

- **`argnames`** — a comma-separated string (`"a,b"`), a list of names (`["a", "b"]`), or a single name. For a single argument the values may be scalars (no tuple wrapping). Since 9.1, the trailing-comma string form `"arg,"` behaves like the tuple form — argvalues are treated as a list of 1-tuples to unpack (previously a subtle bug).
- **`argvalues`** — a list of value tuples (or scalars for one argname). Values are passed **as-is, no copy**: if a test mutates a list/dict parameter, the mutation is visible to subsequent parameter sets. Pass copies if the test may mutate.
- **Empty `argvalues`** — the test is skipped by default (configurable with `empty_parameter_set_mark`, e.g., `empty_parameter_set_mark = fail_at_setup`).
- Applies to functions and classes (see below); on a class, every test method is parametrized.

Non-`Collection` iterables (generators, iterators) as `argvalues` are **deprecated in 9.1** — they are exhausted after the first iteration, so shared marks (class-level) or repeated collection skip silently. Materialize with `list(...)`; `range` objects are `Collection`s and fine.

## Parameter set IDs

Each parameter set gets an ID used in node ids and reports (`test_eval[3+5-8]`):

- Auto-generated from the `repr` of the values; non-ASCII characters are escaped by default (use `disable_test_id_escaping_and_forfeit_all_rights_to_community_support = true` to see raw unicode in ids — accepted side effects included).
- `ids=` — explicit list of ids (strings or `None`) or a callable `values -> id`.
- Per-value ids via `pytest.param(..., id="...")`.
- `pytest.HIDDEN_PARAM` — hide a value from the auto-generated id.
- Duplicate auto-generated ids are silently suffixed (`a`, `a` → `a0`, `a1`) unless `strict_parametrization_ids = true` (or `strict = true`) is set, in which case duplicates are an error.
- Select one parameter set on the command line with its node id: `pytest test_eval.py::test_eval[3+5-8]` (quote the brackets in a shell).

## Per-value control with `pytest.param`

```python
@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("3+5", 8),
        ("2+4", 6),
        pytest.param("6*9", 42, marks=pytest.mark.xfail(reason="broken until fix")),
        pytest.param(1, 1, id="one"),
    ],
)
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

`pytest.param(*values, id=None, marks=None)` attaches a marker (skip, xfail, filterwarnings, ...) to a single parameter set — the standard way to xfail one case while running the rest.

## Stacking decorators

Multiple `parametrize` decorators produce the cartesian product; the **topmost decorator's values vary fastest**:

```python
@pytest.mark.parametrize("x", [0, 1])   # topmost — varies fastest
@pytest.mark.parametrize("y", [2, 3])
def test_foo(x, y): ...
# (0,2), (1,2), (0,3), (1,3)
```

## Class- and module-level parametrization

```python
@pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])
class TestClass:
    def test_simple(self, n, expected): ...

# module-level: applies to all tests in the file
pytestmark = pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])
```

`pytestmark` accepts a single mark or a list of marks.

## Indirect parametrization

`indirect=True` (or `indirect=["arg_name"]` for a subset) makes the given argvalues act as **parameters of fixtures with the same name** instead of test arguments:

```python
@pytest.mark.parametrize("host", ["localhost", "127.0.0.1"], indirect=True)
def test_ping(host):        # `host` is provided by a fixture named `host`
    ...

@pytest.fixture
def host(request):
    return connect(request.param)
```

- The fixture must be parametrized-capable: it reads `request.param`. An unparametrized fixture receives the value through `request.param` when parametrized indirectly.
- A list in `indirect=[...]` parametrizes only the named arguments indirectly, the rest directly.
- 9.1.1 fixed a regression where overriding a parametrized fixture with an indirect `parametrize` raised "duplicate parametrization of '<fixture name>'".

## Custom parametrization with `pytest_generate_tests`

Implement `pytest_generate_tests(metafunc)` in a `conftest.py` (or — unlike other hooks — also directly in a test module/class) for dynamic parametrization:

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption("--stringinput", action="append", default=[],
                     help="list of strings to test")

def pytest_generate_tests(metafunc):
    if "stringinput" in metafunc.fixturenames:
        metafunc.parametrize("stringinput", metafunc.config.getoption("stringinput"))
```

- `metafunc.parametrize(argnames, argvalues, indirect=..., ids=..., ...)` — same semantics as the marker; called per test function during collection.
- Calling it multiple times for the same test: parameter names must not repeat across calls (error).
- An empty parameter list skips the test (respecting `empty_parameter_set_mark`).

## 9.x gotchas

- **Generators as `argvalues`** (deprecated in 9.1) — see above; wrap in `list()`.
- **Mutation leaks between parameter sets** — values are shared references.
- **Duplicate ids** are auto-suffixed by default; enable `strict_parametrization_ids` to catch accidental duplicates early.
- **Parametrizing fixtures and tests crosses multiplicatively** — a 3-value test param on a 2-value fixture param yields 6 tests.
- **unittest.TestCase classes cannot use `@pytest.mark.parametrize`** — use subtests (9.0+) or convert to plain functions.
- For values only known at runtime (not collection), prefer [subtests](01-new-in-9.md#subtests) over building parameter lists dynamically.

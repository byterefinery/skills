# Parametrization and subtests

Grounded in `doc/en/how-to/parametrize.rst` and `doc/en/how-to/subtests.rst` of the 9.2.0 tag.

## `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

- Runs the test once per tuple; each instance gets an ID like `test_eval[6*9-42]` (selectable via `-k` or node ID).
- Applies to test **functions**, **classes** (methods receive the parameters), and **modules** via `pytestmark = pytest.mark.parametrize(...)`.
- **Values are passed as-is — no copy.** Mutating a list/dict parameter in one case affects subsequent cases; pass copies when mutation is expected.
- Non-ASCII in IDs is escaped by default; set `disable_test_id_escaping_and_forfeit_all_rights_to_community_support = true` to see unicode IDs as-is.
- **Long str/bytes values (new in 9.2):** `parametrize_long_str_id_strategy` configures auto IDs — `short` (default; >100 chars → `argname+index`), `sha256`, `legacy`, `disallow`. Explicit `ids=[...]`/`id=` are unaffected.
- **Keyword-only since 9.2:** `indirect=`, `ids=`, `scope=` must be keyword arguments.
- **Empty parameter list** → the test is skipped per `empty_parameter_set_mark` (default: skip).
- **Stacking** decorators produces the cartesian product, exhausting parameters in decorator order:

```python
@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_foo(x, y): ...
```

## Per-instance marks

`pytest.param(*values, marks=..., id=...)` marks individual parameter sets (e.g., `marks=pytest.mark.xfail` or `skipif`); the return type is `pytest.ParameterSet` (9.2).

```python
@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (1, 2),
        pytest.param(1, 0, marks=pytest.mark.xfail(reason="some bug")),
        pytest.param(10, 11, marks=pytest.mark.skipif(sys.version_info >= (3, 0), reason="py2k")),
    ],
)
def test_increment(n, expected):
    assert n + 1 == expected
```

## Indirect parametrization

`indirect=True` (or `indirect=["argname"]`) routes parameter values through fixtures of the same name instead of the test arguments — the fixture receives `request.param`. Useful for combining parametrization with expensive setup.

## `pytest_generate_tests`

Hook for dynamic/custom parametrization. Called during collection with a `metafunc`; use `metafunc.parametrize(name, values, ...)` to add parameters. Unlike other hooks, it may live in a test module or class, not only `conftest.py`:

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption("--stringinput", action="append", default=[],
                     help="list of stringinputs to pass to test functions")

def pytest_generate_tests(metafunc):
    if "stringinput" in metafunc.fixturenames:
        metafunc.parametrize("stringinput", metafunc.config.getoption("stringinput"))
```

- `metafunc.parametrize` with an empty list skips the test.
- Calling it multiple times requires non-duplicated parameter names across calls.
- Combine with `pytest_addoption` to drive parameters from the CLI.

## Subtests (since 9.0, experimental)

Group assertions inside one test; each failure is reported individually as `SUBFAILED` without stopping the test:

```python
def test(subtests):
    for i in range(5):
        with subtests.test(msg="custom message", i=i):
            assert i % 2 == 0
```

- Compact progress shows `u` for both passed and failed subtests; `-v` also shows passed-subtest progress; `verbosity_subtests` config controls default verbosity.
- Subtests can be used multiple times per test and mixed with plain assertions.
- `pytest.Subtests` is exported for type annotations.
- Not selectable individually from the CLI; execution-handling plugins (e.g., `--last-failed`) cannot target individual subtests.
- Core implementation is compatible with the former `pytest-subtests` plugin, except it lacks the plugin's custom CLI output options.

## Parametrization vs subtests

| | Parametrization | Subtests |
|---|---|---|
| When | collection time | test execution |
| Known at collection | yes | no (dynamically generated) |
| CLI-selectable | yes | no |
| Failure stops | that instance | no — all failures reported |
| Good for | decision tables | loops, unknown-at-collection values |

Fixture parametrization (`@pytest.fixture(params=[...])`) re-runs all dependent tests per value — see [02-fixtures](02-fixtures.md).

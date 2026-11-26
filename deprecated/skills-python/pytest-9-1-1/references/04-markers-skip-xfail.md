# Markers, skip, and xfail

## Contents

- [Markers](#markers)
- [Registering marks and strict mode](#registering-marks-and-strict-mode)
- [Built-in markers](#builtin-markers)
- [Skipping](#skipping)
- [`pytest.importorskip`](#pytestimportorskip)
- [XFail](#xfail)
- [Selecting with `-m`](#selecting-with--m)
- [unittest.TestCase and marks](#unittesttestcase-and-marks)

## Markers

`pytest.mark` attaches metadata to tests. Marks are applied with decorators to functions or classes, or via the module-level `pytestmark` global. They are read by plugins and by the `-m` command-line selection.

```python
pytestmark = pytest.mark.slow          # all tests in this module

@pytest.mark.slow
class TestNetwork: ...                 # all tests in the class

@pytest.mark.slow
def test_fetch(): ...
```

- Marks on **fixture functions have no effect** — applying one is an error since 9.0.
- A `Mark` object carries `.args` and `.kwargs` (e.g., `@pytest.mark.timeout(10, "slow", method="thread")` → `args=(10, "slow")`, `kwargs={"method": "thread"}`).
- Read marks in fixtures/hooks: `request.node.get_closest_marker("slow")`, `request.node.iter_markers()` (closest-to-function first).

## Registering marks and strict mode

Custom marks must be registered to avoid `PytestUnknownMarkWarning`:

```toml
# pytest.toml
[pytest]
markers = [
    "slow: marks tests as slow (deselect with -m 'not slow')",
    "serial",
]
```

or programmatically in a `pytest_configure` hook:

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "env(name): mark test to run only on named environment")
```

- Everything after the `:` in a `markers` entry is an optional description.
- With `strict_markers = true` (or `strict = true`), any unregistered mark is an **error** instead of a warning — third-party plugins should always register their marks.
- `pytest --markers` lists all built-in and registered marks.

## Built-in markers

- `pytest.mark.skip(reason=None)` — skip unconditionally
- `pytest.mark.skipif(condition, *, reason=None)` — skip when `condition` is true at collection time
- `pytest.mark.xfail(condition=False, *, reason=None, raises=None, run=True, strict=strict_xfail)` — expected failure
- `pytest.mark.parametrize(argnames, argvalues, ...)` — see [03-parametrize](03-parametrize.md)
- `pytest.mark.usefixtures(*names)` — use the named fixtures without requesting them in the signature
- `pytest.mark.filterwarnings(filter)` — per-test warning filter (same syntax as `-W`/`filterwarnings`)

## Skipping

**Marker form** (evaluated at collection):

```python
@pytest.mark.skip(reason="no way of currently testing this")
def test_the_unknown(): ...

@pytest.mark.skipif(sys.version_info < (3, 13), reason="requires python3.13 or higher")
def test_function(): ...
```

**Imperative form** (condition known only at runtime):

```python
def test_function():
    if not valid_config():
        pytest.skip("unsupported configuration")   # stops the test
```

- Module-level skip: `pytest.skip("...", allow_module_level=True)` in module code, or `pytestmark = pytest.mark.skip("all WIP")`.
- `skipif` on a class skips every method; multiple `skipif` marks skip if **any** condition is true.
- Skip conditions are evaluated at import/collection time — `skipif` conditions that need runtime state belong in the imperative form.
- Markers are importable, so shared conditions can live in one module: `minversion = pytest.mark.skipif(...)` then `@minversion` elsewhere.
- Skipping whole files/directories is done by excluding them from collection (`conftest.py` with `pytest_ignore_collect` / `pytest_collect_file`), not with marks.
- Show skip reasons with `pytest -rs` (or `-rxXs` for xfail/xpass/skip details).

## `pytest.importorskip`

Skip a test (or module) when an import fails:

```python
pexpect = pytest.importorskip("pexpect")
docutils = pytest.importorskip("docutils", minversion="0.3")   # version from __version__
```

- Use at module level (skips the whole module), in a test, or in fixture setup.
- **Since 9.1 only `ModuleNotFoundError` is caught by default** — a broken/installed package surfaces its real error instead of skipping. Pass `exc_type=ImportError` (added in 8.2) to restore the old behavior.

## XFail

`@pytest.mark.xfail` marks a test as expected to fail: it still runs, a failure is reported as `XFAIL` (no traceback), an unexpected pass is reported as `XPASS`.

```python
@pytest.mark.xfail(reason="known parser issue")
def test_function(): ...

# conditional — a reason is required when condition is used
@pytest.mark.xfail(sys.platform == "win32", reason="bug in a 3rd party library")
def test_platform(): ...
```

Parameters:

- `raises=` — a single exception or tuple; the test is xfailed **only** if it fails with that type (or a subclass). Any other exception is a regular failure. Accepts `RaisesGroup` for exception groups.
- `run=False` — mark without executing (tests that crash the interpreter).
- `strict=` — when `True`, an `XPASS` **fails the suite**. Defaults to the `strict_xfail` ini option (alias of legacy `xfail_strict`), which defaults to `False`; also enabled by `strict = true`.
- `reason=` — free text shown in reports.

Imperative form — `pytest.xfail("msg")` inside a test (or fixture) xfails the rest of the test; nothing after the call runs (it raises internally). Useful for runtime conditions.

- `pytest --runxfail` ignores all xfail marks (runs/reports as unmarked) — handy to see the real state of xfails.
- Per-parameter-set xfail: `pytest.param(..., marks=pytest.mark.xfail(...))` in `parametrize`.
- `xfail` + `raises` documents "should fail this way"; `pytest.raises` is the better tool for exceptions your own code deliberately raises.

## Selecting with `-m`

`-m` runs tests matching a marker expression:

```bash
pytest -m slow                     # marked slow
pytest -m "not slow"               # everything else
pytest -m "slow and not integration"
pytest -m "slow(phase=1)"          # annotated marks: match by kwargs
```

The expression supports `and`, `or`, `not` over mark names (and `name(args/kwargs=...)` for annotated marks). Unmarked tests are deselected when `-m` is given.

## unittest.TestCase and marks

pytest runs `unittest` suites natively. In `TestCase` subclasses, the `skip`, `skipif`, and `xfail` marks **do work**, and autouse fixtures apply. Regular (non-autouse) fixtures and parametrization do **not** work on `TestCase` classes — use `unittest`'s own mechanisms or convert the class to plain test functions. `unittest.TestCase.subTest` is supported since 9.0 (it integrates with subtests reporting). The `load_tests` protocol is not supported.

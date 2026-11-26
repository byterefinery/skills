---
name: pytest-9-2-0
description: >
  Python testing framework pytest, version 9.2.0 (Python 3.10+, officially
  supports 3.10-3.15). Use when writing, running, or debugging Python tests
  with pytest — test discovery and selection, fixtures and scoping,
  parametrization, subtests, markers, skip and xfail, assertion rewriting and
  pytest.approx, exception groups, monkeypatching, capturing stdout/stderr
  and logs, temp directories, cross-run cache, TOML and INI config files,
  command-line selection, exit codes, custom collectors, or the plugin hook
  system. Emphasizes what's new and breaking in 9.2 — keyword-only
  parametrize arguments, -c validation, plugin import failure exit codes,
  -m marker validation under strict mode.
license: MIT
compatibility: Requires Python 3.10+; pulls in pluggy>=1.6,<2, iniconfig>=2, packaging>=24, pygments>=2.15
metadata:
  tags:
    - python
    - testing
    - pytest
    - test-framework
---

# pytest 9.2.0

pytest 9.2.0 (released 2026-10-27) is Python's test framework. It discovers and runs tests, provides a flexible fixture system for setup/teardown, rewrites assertions for rich failure introspection, and supports parametrization, subtests, markers, and an extensible plugin hook system. Requires Python 3.10+; supports 3.10 through 3.15.

## Overview

Key capabilities:

- **Test discovery** — `test_*.py` / `*_test.py` files, `test`-prefixed functions, `Test`-prefixed classes, `unittest.TestCase` subclasses; naming configurable via `python_files`/`python_classes`/`python_functions`
- **Fixtures** — `@pytest.fixture` with `function`/`class`/`module`/`package`/`session` scopes (or a callable for dynamic scope), `autouse`, parametrized fixtures, yield teardown and `request.addfinalizer`, `conftest.py`-based availability
- **Parametrization** — `@pytest.mark.parametrize` (tests, classes, modules), per-value marks via `pytest.param`, stacked decorators for cartesian products, `pytest_generate_tests`; `indirect`/`ids`/`scope` are keyword-only since 9.2
- **Subtests** (since 9.0, experimental) — `subtests.test()` context manager groups assertions; failures reported as `SUBFAILED`
- **Markers** — skip, skipif, xfail, usefixtures, filterwarnings, parametrize, custom marks; `-m` selection
- **Assertions** — plain `assert` with rewritten introspection, `pytest.approx`, `pytest.raises` / `RaisesGroup` / `RaisesExc`, `pytest.warns`, `pytest.fail`, `pytest.skip`, `pytest.xfail`, `pytest.importorskip`
- **Isolation** — `monkeypatch`, `capsys`/`capfd` capture, `caplog` logging, `tmp_path`, cross-run `cache`
- **Config** — native TOML (`pytest.toml`), `[tool.pytest]` in `pyproject.toml`, plus `pytest.ini`, `tox.ini`, `setup.cfg`
- **CLI** — node IDs, `-k`/`-m` selection, `@file` argument lists, `--lf`/`--ff`, durations, custom collectors, exit codes 0–6 (`pytest.ExitCode` enum)

New in 9.2.0 (details in [01-new-in-9-2](references/01-new-in-9-2.md)): `parametrize` arguments keyword-only, `-c` path validation, plugin import failures classified with exit codes 3/4, `-m` marker validation under `strict_markers`, `parametrize_long_str_id_strategy` option, entry-point names accepted in `pytest_plugins`/`PYTEST_PLUGINS`.

## Usage

Write tests in `test_*.py` files, then run `pytest` (or `python -m pytest`, which additionally puts the current directory on `sys.path`):

```python
# test_calc.py
import pytest

@pytest.fixture
def connection(tmp_path):
    conn = open_db(tmp_path / "db.sqlite")
    yield conn            # teardown runs after the test
    conn.close()

@pytest.mark.parametrize("x,expected", [(2, 4), (3, 9)])
def test_square(x, expected, connection):
    assert connection.square(x) == expected

def test_docstrings(subtests):   # subtests — since 9.0
    for path in sorted(Path("docs").glob("*.md")):
        with subtests.test(path=path.name):
            assert path.read_text().startswith("#")
```

```bash
pytest test_calc.py::test_square          # node ID selection
pytest -k "square and not 3"             # keyword expression
pytest -m slow                           # marker expression
pytest --lf --maxfail=2 -q               # rerun last failures, stop at 2
pytest --durations=10                    # slowest tests
pytest --collect-only -q > ids.txt && pytest @ids.txt   # args from file
```

Minimal config — TOML:

```toml
# pytest.toml (or pyproject.toml under [tool.pytest])
[pytest]
minversion = "9.2"
addopts = ["-ra", "-q"]
testpaths = ["tests"]
markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')"]
filterwarnings = ["error", "ignore::DeprecationWarning"]
```

## Gotchas

- **`indirect`, `ids`, `scope` of `parametrize` are keyword-only since 9.2** — positional passing (e.g., `parametrize("a", "b", [(1, 2)])`) now fails with a `TypeError`; previously the argvalues silently landed in `indirect`.
- **`-c <path>` is validated since 9.2** — a missing path, a directory, or an unsupported format raises a usage error instead of being ignored or crashing with `FileNotFoundError`.
- **Plugin import failures get distinct exit codes since 9.2** — plugin not found (via `-p`, `pytest_plugins`, `PYTEST_PLUGINS`) exits 4; found-but-raises (broken `pytest11` entry point, missing dependency) exits 3 with the traceback preserved.
- **Higher-scoped fixtures as instance methods are deprecated since 9.2** — `module`, `package`, and `session` fixtures defined as plain instance methods on test classes are deprecated (attributes set on `self` are invisible to the tests because each test gets a fresh instance). Use `@classmethod`; the 9.1 rule covers `class` scope.
- **Marks cannot be applied to fixture functions** — applying one is an error; use a regular function or `request` introspection.
- **`usefixtures` cannot decorate fixture functions** — it is an error on fixtures; put it on tests, classes, or modules (`pytestmark`).
- **Assertion rewriting applies only to collected test modules** — asserts in helper modules are not rewritten. Call `pytest.register_assert_rewrite("mymod")` before importing it (root `conftest.py`), or add `PYTEST_DONT_REWRITE` to a module docstring to opt out; `--assert=plain` disables globally.
- **Each test method gets a unique class instance** — instance state does not leak between tests; class-level attributes are shared, so use fixtures (with `scope="class"`) instead of `self` state.
- **`pytest.skip` at module level needs `allow_module_level=True`** — plain `pytest.skip()` inside a test or setup only; `pytest.importorskip("mod", minversion="0.3")` reads the module's `__version__`.
- **`xfail` tests do not fail the suite by default** — set `strict=True` on the marker or `xfail_strict = true` in config to make `XPASS` fail; `run=False` skips execution entirely; `pytest.xfail()` raises, so no code after it runs.
- **`parametrize` values are passed as-is** — mutating a list/dict parameter in one test case affects later cases; wrap in a copy if mutation is expected.
- **Empty parameter sets skip the test** — `metafunc.parametrize` with `[]` skips per `empty_parameter_set_mark` (default `skip`); use `pytest.param(..., marks=...)` to mark individual instances.
- **`caplog.records` holds only the current phase** — inside `setup` it contains setup logs only; use `caplog.get_records("setup"|"call"|"teardown")` for other phases. Reconfiguring the root logger (e.g., `dictConfig`) can remove pytest's handler and silently stop capture.
- **`--basetemp` is wiped blindly every run** — without it, pytest keeps the last 3 runs under `pytest-of-{user}/pytest-{num}/` (configurable via `tmp_path_retention_count`/`tmp_path_retention_policy`).
- **`pytest` vs `python -m pytest`** — the latter adds the current directory to `sys.path`; the bare script does not. `pytest.main()` returns the exit code instead of raising `SystemExit`, and calling it repeatedly in one process is not recommended (import caching).
- **`unittest.TestCase` limits** — no non-autouse fixtures and no parametrization inside `TestCase` subclasses (use `@pytest.mark.usefixtures` and autouse class fixtures); `load_tests` protocol unsupported; setup/teardown run in the `call` phase, not `setup`.
- **Subtests are experimental** — since 9.0 they are built in, but reporting details may evolve; subtest failures do not stop the test (all failures are collected), and subtests cannot be selected from the command line.
- **Duplicate CLI paths are collapsed** — `pytest a/ a/b` is `pytest a/`; `pytest --keep-duplicates` runs a file twice.
- **`--no-summary` only suppresses pytest's own summary since 9.2** — the `pytest_terminal_summary` hook still runs, so plugins (e.g., coverage) can write their own.
- **`pytest.approx` with `Decimal`** — passing a float tolerance that cannot be represented exactly for a `Decimal` comparison emits `PytestApproxDecimalToleranceWarning` (tolerance is widened to the float's binary value) since 9.2.

## References

- [01-new-in-9-2](references/01-new-in-9-2.md) — What's new and breaking in pytest 9.2.0, deprecations scheduled for 10/11
- [02-fixtures](references/02-fixtures.md) — Fixture API, scopes, teardown, availability, override order, instantiation order, `request`
- [03-parametrize](references/03-parametrize.md) — `parametrize` marker, `pytest.param`, IDs, `pytest_generate_tests`, subtests alternative
- [04-markers-skip-xfail](references/04-markers-skip-xfail.md) — Markers, registration, skip/skipif/importorskip, xfail semantics
- [05-assertions](references/05-assertions.md) — Assertion rewriting, `approx`, `raises`/`RaisesGroup`/`RaisesExc`, `warns`, custom comparisons
- [06-env-fixtures](references/06-env-fixtures.md) — `capsys`/`capfd`/`caplog`, `monkeypatch`, `tmp_path`, `cache`, `request`, `subtests`
- [07-config-running](references/07-config-running.md) — Config files, rootdir, discovery, CLI flags, plugins, exit codes, programmatic use
- [08-examples-demos](references/08-examples-demos.md) — Walkthroughs of the repo's own demos: xfail_demo, customdirectory, nonpython, reportingdemo, cmdopt pattern

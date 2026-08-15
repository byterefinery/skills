---
name: pytest-9-1-1
description: >
  Python testing framework pytest, version 9.1.1 (Python 3.10+, official
  3.15 support). Use when writing, running, or debugging Python tests with
  pytest — test discovery, fixtures and scoping, parametrization, subtests,
  markers, skip and xfail, assertion rewriting and pytest.approx,
  monkeypatching, capturing stdout/stderr/logs, temp directories, warnings,
  config files (TOML and INI), command-line selection and reporting, exit
  codes, or the plugin hook system. Emphasizes what's new and breaking in
  pytest 9.x — native TOML config, strict mode, built-in subtests,
  max-warnings, and the 9.1 deprecations.
metadata:
  tags:
    - python
    - testing
    - pytest
    - test-framework
---

# pytest 9.1.1

pytest 9.1.1 (released 2026-06-19) is Python's test framework. It discovers and runs tests, provides a flexible fixture system for setup/teardown, rewrites assertions for rich failure introspection, and supports parametrization, markers, and an extensible plugin hook system. Requires Python 3.10+; 3.15 is officially supported.

## Overview

Key capabilities:

- **Test discovery** — `test_*.py` / `*_test.py` files, `test`-prefixed functions, `Test`-prefixed classes, `unittest.TestCase` subclasses; import modes `prepend`, `append`, `importlib`
- **Fixtures** — `@pytest.fixture` with `function`/`class`/`module`/`package`/`session` scopes, `autouse`, parametrized fixtures, finalizers, `conftest.py`-based availability
- **Parametrization** — `@pytest.mark.parametrize` (tests, classes, modules), per-value marks, indirect parametrization, `pytest_generate_tests`
- **Subtests** (new in 9.0, experimental) — loop assertions in one test with individually reported `SUBFAILED` results
- **Markers** — skip, skipif, xfail, usefixtures, filterwarnings, custom marks; `-m` selection
- **Assertions** — rewritten `assert`, `pytest.approx` (floats, sequences, dicts, numpy, datetime/timedelta), `pytest.raises` / `RaisesGroup`, `pytest.warns`
- **Isolation** — `monkeypatch`, `capsys`/`capfd`/`caplog` capture, `tmp_path`, cross-run `cache`
- **Config** — native TOML (`pytest.toml`, `[tool.pytest]`) since 9.0, plus `pytest.ini`, `tox.ini`, `setup.cfg`, `[tool.pytest.ini_options]`
- **CLI** — node IDs, `-k`/`-m` selection, `--lf`/`--ff`, durations, JUnit XML, exit codes 0–6

New in the 9.x line (details in [01-new-in-9](references/01-new-in-9.md)): built-in subtests, native TOML config, strict mode, `--max-warnings` (exit code 6), `approx` datetime support, `pytest.register_fixture()`, and several removals/deprecations that affect porting from 8.x.

## Usage

Write tests in `test_*.py` files, then run `pytest` (or `python -m pytest`, which additionally puts the current directory on `sys.path`):

```python
# test_calc.py
import pytest

@pytest.fixture
def connection(tmp_path):
    conn = open_db(tmp_path / "db.sqlite")
    yield conn            # teardown after the test
    conn.close()

@pytest.mark.parametrize("x,expected", [(2, 4), (3, 9)])
def test_square(x, expected, connection):
    assert connection.square(x) == expected

def test_docstrings(subtests):   # subtests — new in 9.0
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
pytest --collect-only -q > ids.txt && pytest @ids.txt   # args from file (8.2+)
```

Minimal config — native TOML format since 9.0:

```toml
# pytest.toml (or pyproject.toml under [tool.pytest])
[pytest]
minversion = "9.0"
addopts = ["-ra", "-q"]
testpaths = ["tests"]
markers = ["slow: marks tests as slow (deselect with -m 'not slow')"]
filterwarnings = ["error", "ignore::DeprecationWarning"]
strict = true
```

## Gotchas

- **Python 3.9 support was dropped in 9.0** — pytest 9.x requires Python 3.10+.
- **`PytestRemovedIn9Warning` is an error by default** in 9.x — 8.x-era deprecated uses (yield-style tests, `py.path.local` hook args) now fail hard.
- **`pytest.importorskip` (9.1) only catches `ModuleNotFoundError` by default** — broken installs no longer skip silently. Pass `exc_type=ImportError` to restore the old skip-on-any-`ImportError` behavior.
- **Overlapping/duplicate path arguments are collapsed (9.0)** — `pytest a/ a/b` is equivalent to `pytest a/`, and `pytest x.py x.py` runs the file once. Use `--keep-duplicates` to run a file twice.
- **Class-scoped fixtures as plain instance methods are deprecated (9.1)** — attributes set on `self` are invisible to the tests, because each test method gets a fresh class instance while the fixture ran once on a different one. Use `@classmethod` and set class attributes.
- **Passing generators to `parametrize` is deprecated (9.1)** — non-`Collection` argvalues are exhausted on re-collection (e.g., class-level marks shared by several methods). Wrap in `list()`; `range` is a `Collection` and is fine.
- **Marks on fixture functions have no effect** — applying one is an error since 9.0.
- **`[tool.pytest]` and `[tool.pytest.ini_options]` are mutually exclusive** in `pyproject.toml`, and options are never merged across multiple config files — the first match wins.
- **`--rootdir` cannot go in `addopts`** — the rootdir is used to find the config file in the first place.
- **`pytest` vs `python -m pytest`** — the latter adds the current directory to `sys.path`; the bare script does not. Use the `pythonpath` ini option or `--import-mode=importlib` for layout control.
- **Assertion rewriting applies only to collected test modules** — asserts in helper modules are not rewritten. Call `pytest.register_assert_rewrite("mymod")` before importing it (root `conftest.py`), or add `PYTEST_DONT_REWRITE` to a module docstring to opt out.
- **`pytest.approx` tolerance semantics** — specifying `abs` disables the relative tolerance unless `rel` is also given. For datetime/timedelta (9.1), `abs` must be a `timedelta`, and `rel` is not supported for datetimes.
- **`pytest.raises` matches subclasses** — for the exact type, check `excinfo.type is X`. `match=` uses `re.search` on the message (and PEP-678 `__notes__`), so regex metacharacters in messages need escaping.
- **`caplog` quirks** — `caplog.records` holds only the current phase (setup/call/teardown); use `caplog.get_records(when)` for other phases. Reconfiguring the root logger (e.g., `dictConfig`) can remove pytest's handler and silently stop capture. Since 9.1, logs from non-propagating loggers are captured too.
- **`tmp_path` retention** — pytest keeps the last 3 runs by default (`tmp_path_retention_count`); `tmp_path_retention_policy = "failed"` keeps only failed tests' dirs. `--basetemp` wipes its directory blindly on every run.
- **`request.getfixturevalue()` during teardown for a first-time request is deprecated (9.1)** — it becomes an error in pytest 10. Request the fixture before the `yield`.
- **`pytest.console_main()` is deprecated (9.1)** — use `pytest.main()` for programmatic invocation; it returns the exit code instead of raising `SystemExit`.
- **Strict mode (`strict = true`) opts into future strictness options** — enable it only with a pinned pytest version, or set the individual `strict_*` options.
- **`--doctest-modules` + module-scoped autouse fixtures defined inline in test modules may run twice (9.1)** — the module is collected both as a module and as a doctest module. Move such fixtures to `conftest.py`.
- **CI detection (9.0) requires `$CI` or `$BUILD_NUMBER` to be non-empty** — an empty `CI=` no longer triggers CI behavior (untruncated summaries, disabled assertion truncation).

## References

- [01-new-in-9](references/01-new-in-9.md) — What's new and breaking in 9.0/9.1, deprecations targeted for pytest 10
- [02-fixtures](references/02-fixtures.md) — Fixture API, scopes, availability, override order, instantiation order, `request`
- [03-parametrize](references/03-parametrize.md) — `parametrize` marker, IDs, `pytest.param`, indirect, `pytest_generate_tests`
- [04-markers-skip-xfail](references/04-markers-skip-xfail.md) — Markers, registration, skip/skipif/importorskip, xfail semantics
- [05-assertions](references/05-assertions.md) — Assertion rewriting, `approx`, `raises`/`RaisesGroup`, `warns`, custom explanations
- [06-capture-mock-env](references/06-capture-mock-env.md) — `capsys`/`capfd`/`caplog`, `monkeypatch`, `tmp_path`, `cache`, warnings
- [07-config-running](references/07-config-running.md) — Config files, rootdir, discovery, CLI flags, exit codes, CI, programmatic use

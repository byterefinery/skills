---
name: pytest-9-1-0
description: Write, run, and debug Python tests with pytest 9.1.0. Use when the user mentions pytest, writing tests, test fixtures, parametrization, test discovery, conftest.py, pytest plugins, test marks, skip/xfail, monkeypatch, tmp_path, capsys, caplog, assertion rewriting, or any Python testing task.
metadata:
  tags:
    - python
    - testing
---

# pytest 9.1.0

## Overview

pytest is a mature full-featured Python testing framework. It makes building simple and scalable tests straightforward. Key strengths include zero-boilerplate test discovery, rich assertion introspection via AST rewriting, a powerful fixture system with dependency injection, and an extensible plugin architecture.

This skill covers pytest 9.1.0, including features added in recent releases: subtests (9.0), `pytest.toml` config (9.0), strict mode (9.0), `--max-warnings` (9.1), and the `RaisesGroup`/`RaisesExc` API for exception groups.

## Usage

### Running tests

```bash
pytest                          # run all tests from current directory
pytest tests/                   # run tests in a directory
pytest test_mod.py              # run a specific file
pytest test_mod.py::test_func   # run a single test
pytest -k "word"                # keyword expression (case-insensitive)
pytest -m "slow"                # marker expression
pytest --lf                     # re-run last failures only
pytest --ff                     # run last failures first
pytest -x                       # stop at first failure
pytest --tb=short               # shorten tracebacks
pytest -v                       # verbose output
pytest --collect-only -q        # list tests without running
```

### Invoking from Python

```python
import pytest
retcode = pytest.main(["-x", "tests/"])  # returns ExitCode int
```

### Quick test patterns

```python
def test_simple():
    assert 1 + 1 == 2

def test_with_fixture(db_connection):
    result = db_connection.query("SELECT 1")
    assert result == [(1,)]

@pytest.mark.parametrize("input,expected", [(2, 4), (3, 9)])
def test_parametrized(input, expected):
    assert input ** 2 == expected
```

## Gotchas

- **Assertion rewriting only applies to collected test modules.** Asserts in helper/imported modules won't get introspection. Call `pytest.register_assert_rewrite("mypackage.helper")` before importing, or use `--assert=plain` to disable rewriting entirely.
- **Fixture scope determines sharing, not execution order.** Fixtures execute by scope (session > package > module > class > function), then by dependency graph. Request order and definition order don't matter.
- **`conftest.py` is never imported directly.** It's auto-discovered per-directory. Never `import conftest`. Place shared fixtures in the root `conftest.py` or use `pytest_plugins` to load plugin modules.
- **`monkeypatch.setattr()` patches the object you pass, not the reference your code holds.** If code does `from os import getcwd`, patch `mymodule.getcwd` not `os.getcwd`.
- **`tmp_path` is a `pathlib.Path`, not `py.path.local`.** Use `tmp_path / "subdir"` and `.write_text()`, not legacy `py.path` methods.
- **Parametrized mutable values are shared across test instances.** If you pass a list/dict as a param value and the test mutates it, subsequent parametrized runs see the mutation. Use `pytest.param()` with copies or factory functions.
- **`@pytest.mark.xfail(strict=True)` makes XPASS a failure.** Without strict, unexpectedly passing tests are silently XPASS. Enable `strict_xfail = true` in config for CI safety.
- **`return value` from test functions is ignored.** Returning `True`/`False` does not determine pass/fail. Always use `assert`.
- **Subtests (9.0+) are not individually addressable on CLI.** Unlike parametrized tests, subtests happen at runtime and can't be selected with `pytest test.py::test_func[subtest]`.
- **`--doctest-modules` runs doctests from source code docstrings.** This means your production code's examples become tests. Be careful with non-deterministic output.

## References

- [01-fixtures.md](references/01-fixtures.md) — Fixture system: scopes, conftest.py, autouse, parametrization, dynamic scope
- [02-assertions-and-exceptions.md](references/02-assertions-and-exceptions.md) — Assertion rewriting, `pytest.raises`, `pytest.warns`, `pytest.approx`, exception groups
- [03-marks-and-selection.md](references/03-marks-and-selection.md) — Marks, skip/xfail, parametrize, test selection strategies
- [04-cli-and-configuration.md](references/04-cli-and-configuration.md) — CLI flags, config files (pytest.toml, pyproject.toml), addopts, strict mode
- [05-plugins-and-hooks.md](references/05-plugins-and-hooks.md) — Plugin architecture, hook functions, conftest.py plugins, writing plugins
- [06-testing-utilities.md](references/06-testing-utilities.md) — monkeypatch, tmp_path, capsys/capfd, caplog, cache, subtests
- [07-doctest-and-unittest.md](references/07-doctest-and-unittest.md) — Doctest integration, unittest compatibility, test discovery conventions

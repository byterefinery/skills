# Config, CLI, discovery, exit codes

Grounded in `doc/en/how-to/usage.rst`, `doc/en/example/simple.rst`, `doc/en/example/pythoncollection.rst`, and `doc/en/reference/exit-codes.rst` of the 9.2.0 tag.

## Invoking pytest

- `pytest [...]` — standard script.
- `python -m pytest [...]` — same, **plus** adds the current directory to `sys.path`.
- `pytest.main([...])` from Python — returns the exit code (does **not** raise `SystemExit`); reads `sys.argv` if no args; extra plugins via `plugins=[MyPlugin()]`. Not recommended to call repeatedly in one process (import caching hides file changes).

```bash
pytest --version   # shows where pytest was imported from
pytest --fixtures  # list builtin and custom fixtures
pytest -h          # CLI + config file options
```

## Selecting tests

- **Node IDs** — `pytest tests/test_mod.py::test_func`, `::TestClass`, `::TestClass::test_method`, parametrized instance `::test_func[x1,y2]`.
- **Keywords** — `pytest -k 'MyClass and not method'` (case-insensitive; matches names, file/class, markers; use `""` on Windows).
- **Markers** — `pytest -m slow`, `pytest -m "slow(phase=1)"` (since 9.2, names validated against registered marks when `strict_markers` is on).
- **Packages** — `pytest --pyargs pkg.testing` (imports the package, uses its filesystem location).
- **Args from file** (8.2+) — `pytest @tests_to_run.txt`, one entry per line (paths, node IDs, options like `-m slow`); generate with `pytest --collect-only -q`.
- **Deselect** — `--deselect=item` removes specific collected items.
- **Ignore** — `--ignore=path` (repeatable) and `--ignore-glob='*_01.py'` (shell-style wildcards).
- **Duplicates** — duplicate CLI paths are collapsed (`pytest a a` collects once); `--keep-duplicates` runs them twice.

## Config files

Formats include TOML (`pytest.toml` with a `[pytest]` table; `[tool.pytest]` in `pyproject.toml`) and INI (`pytest.ini`, `tox.ini` `[pytest]` section, `setup.cfg` `[tool:pytest]`).

```toml
# pytest.toml
[pytest]
minversion = "9.2"
addopts = ["-ra", "-q"]
testpaths = ["tests"]
markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')"]
filterwarnings = ["error", "ignore::DeprecationWarning"]
```

- **`addopts`** — default CLI options; the final command line is `<config addopts> $PYTEST_ADDOPTS <extra CLI args>` — on conflicts the **last wins** (`pytest -ra -q -v -m slow` → verbose, since `-v` overwrites `-q`).
- **`PYTEST_ADDOPTS`** environment variable adds options while set (`export PYTEST_ADDOPTS="-v"`).
- **`-c <path>`** selects the config file explicitly — since 9.2, a missing path, directory, or unsupported format is a usage error.
- Common ini options seen in the docs: `minversion`, `addopts`, `testpaths`, `markers`, `filterwarnings`, `usefixtures`, `strict_markers`, `xfail_strict` (TOML) / `strict_xfail` (INI), `python_files`, `python_classes`, `python_functions`, `norecursedirs`, `log_format`, `log_date_format`, `log_cli`, `log_cli_level`, `log_file*`, `junit_family`, `junit_logging`, `junit_duration_report`, `console_output_style`, `empty_parameter_set_mark`, `assertion_text_diff_style`, `tmp_path_retention_count`, `tmp_path_retention_policy`, `disable_test_id_escaping_and_forfeit_all_rights_to_community_support`, `parametrize_long_str_id_strategy`, `verbosity_subtests`, `max-warnings` (`--max-warnings`, exit code 6 when exceeded). Since 9.2, several of these are value-registered: bad values are clean usage errors and `--help` lists accepted values; `config.getini` raises `pytest.UsageError` on type mismatch.

## Discovery conventions

- Files: `test_*.py` or `*_test.py`; functions/methods `test*`; classes `Test*` (no `__init__`).
- `unittest.TestCase` subclasses and their `test` methods are collected automatically (see *unittest integration* below).
- **Customize** via `python_files = ["check_*.py", ...]`, `python_classes = ["Check"]`, `python_functions = ["*_check"]` (space-separated or list patterns). `python_functions`/`python_classes` do **not** affect `unittest.TestCase` method discovery.
- **`norecursedirs`** — globs pytest won't recurse into (default includes build dirs).
- **`collect_ignore`** / **`collect_ignore_glob`** in `conftest.py` — per-directory ignore lists (e.g., `collect_ignore = ["setup.py"]`).
- **`__test__ = False`** on a class (or mixin setting it via `__init_subclass__`) prevents collection.
- **Peek** at the collection tree without running: `pytest --collect-only [path]`.

## Durations and profiling

- `pytest --durations=10 --durations-min=1.0` — slowest 10 tests over 1.0s.
- Durations below 0.005s are hidden unless `-vv`.

## Plugins

- **Early-load** — `-p myproject.plugins` (importable dotted name) or `-p pytest_cov` (entry-point name).
- **Disable** — `-p no:doctest`, `-p no:legacypath`, `-p no:logging` (prefix `no:`).
- **`pytest_plugins`** in the **top** `conftest.py` and the **`PYTEST_PLUGINS`** env var accept module names **and, since 9.2, entry-point names** (e.g., `xdist`); such plugins appear in the header's `plugins:` line.
- Warnings from plugin imports (via `-p`, `PYTEST_PLUGINS`, entry-point autoloading) are captured and reported (9.2). Plugin import failures exit 4 (not found) or 3 (raises; 9.2).

## unittest integration

pytest runs `unittest` suites out of the box (`pytest tests`); supported: `skip`/`skipIf` decorators, `setUp`/`tearDown`, `setUpClass`/`tearDownClass`, `setUpModule`/`tearDownModule`, `TestCase.subTest` (since 9.0). Not supported: the `load_tests` protocol. Benefits kept: better tracebacks, capturing, `-k`/`-m` selection, `--maxfail`, `--pdb`, xdist, plain `assert` statements. Inside `TestCase` subclasses, marks (`skip`/`skipif`/`xfail`) and **autouse** fixtures work; regular fixtures, parametrization, and custom hooks do **not**. Mix fixtures in via `@pytest.mark.usefixtures("db_class")` on the class (fixture sets `request.cls.db`) or class-level `@pytest.fixture(autouse=True)` methods (e.g., `monkeypatch.chdir(tmp_path)`). Note: unittest setup/teardown runs in pytest's **call** phase, not setup — setup errors surface as call errors.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | all tests collected and passed |
| 1 | tests ran, some failed |
| 2 | execution interrupted by user |
| 3 | internal error (or, since 9.2, plugin found but raised while importing) — `pytest.ExitCode.INTERNAL_ERROR` |
| 4 | usage error (bad `-c`, plugin not found, `conftest.py` import failure) — `pytest.ExitCode.USAGE_ERROR` |
| 5 | no tests collected |
| 6 | max warnings exceeded (`--max-warnings`) |

Represented by the public `pytest.ExitCode` enum (`from pytest import ExitCode`).

## Useful CLI flags

- `-q`/`-v` verbosity; `-s` no capture; `--capture=fd|sys|tee-sys|no`
- `-x`/`--maxfail=N` stop after N failures; `--lf`, `--ff`, `--nf`, `--sw`, `--stepwise-skip`
- `-r` report extras (e.g., `-rxXs` for xfailed/xpassed/skipped details)
- `--tb=...` traceback styles; `--full-trace` (9.2: all RecursionError frames)
- `--collect-only`, `--setup-plan`, `--fixtures`, `--markers`, `--version`
- `--deselect=item`, `--ignore=path`, `--ignore-glob=...`, `--keep-duplicates`
- `--durations=N --durations-min=S`
- `--cache-show [glob]`, `--cache-clear`
- `--max-warnings=N` (exit code 6)
- `--runxfail`, `--strict-markers`
- `--basetemp=dir`, `--import-mode=...`, `--pyargs`, `--no-summary` (9.2: plugin summaries still run)
- `--assert=plain|rewrite` (default rewrite)

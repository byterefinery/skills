# Configuration, invocation, and running tests

## Contents

- [Config file formats](#config-file-formats)
- [rootdir and configfile](#rootdir-and-configfile)
- [Test discovery and import modes](#test-discovery-and-import-modes)
- [Key configuration options](#key-configuration-options)
- [Command-line invocation](#command-line-invocation)
- [Selecting tests](#selecting-tests)
- [Exit codes](#exit-codes)
- [CI behavior](#ci-behavior)
- [Programmatic use](#programmatic-use)
- [Plugins](#plugins)
- [Reporting extras](#reporting-extras)

## Config file formats

pytest looks for configuration in these files, **in this precedence order** (first match wins; options are never merged across files, and 9.x prints a warning when more than one file contains pytest config):

1. `pytest.toml` / `.pytest.toml` — `[pytest]` table, **native TOML types** (9.0+). Matches even when empty; highest precedence.
2. `pytest.ini` / `.pytest.ini` — `[pytest]` section, INI syntax. Matches even when empty (hidden `.pytest.ini` since 9.0).
3. `pyproject.toml` — `[tool.pytest]` (native TOML, 9.0+) **or** `[tool.pytest.ini_options]` (INI-compat, 6.0+). The two tables cannot be combined. Since 9.0, a `pyproject.toml` matches even without either table when nothing else did.
4. `tox.ini` — `[pytest]` section.
5. `setup.cfg` — `[tool:pytest]` section. Discouraged: `.cfg` uses a different parser that causes hard-to-track problems; use the others.

```toml
# pytest.toml — native TOML (9.0+)
[pytest]
minversion = "9.0"
addopts = ["-ra", "-q"]
testpaths = ["tests", "integration"]
```

```ini
; pytest.ini — INI
[pytest]
minversion = 9.0
addopts = -ra -q
testpaths =
    tests
    integration
```

Overrides: `-o name=value` on the command line (repeatable) wins over the file. `minversion` is enforced — a too-new/too-old config aborts with a clear error.

## rootdir and configfile

For each run pytest determines a **rootdir** (reference directory for node ids, `.pytest_cache` location, etc. — it does *not* affect `sys.path` or imports) and a **configfile** (may be `None`). Both are printed in the session header.

Algorithm:

1. `-c FILE` forces the config file; its directory becomes the rootdir.
2. Otherwise, find the common ancestor directory of the existing paths given on the command line (or the CWD if none).
3. From that ancestor **upwards**, look for `pytest.toml`, `.pytest.toml`, `pytest.ini`, `.pytest.ini`, `pyproject.toml` (must contain a `[tool.pytest*]` table), `tox.ini` (must contain `[pytest]`), `setup.cfg` (must contain `[tool:pytest]`) — in that order. First match = configfile + rootdir.
4. Else look for `setup.py` upwards (its directory = rootdir).
5. Else look for config files upwards from each given argument.
6. Else the common ancestor itself is the rootdir (no configfile).

- `--rootdir=path` forces the rootdir. It **cannot** be set via `addopts` — the rootdir is needed to find the config file in the first place.
- `config.rootpath` / `config.inipath` are the `pathlib.Path` versions (legacy `config.rootdir` / `config.inifile` are `py.path.local`).

## Test discovery and import modes

Default discovery:

- Collection starts at `testpaths` (when configured) or the CWD, and recurses into directories **except** those matching `norecursedirs` (default: `*.egg`, `.*`, `_darcs`, `build`, `CVS`, `dist`, `node_modules`, `venv`, `{arch}`).
- Test files: `python_files` patterns (default `test_*.py` and `*_test.py`).
- Test items: `test`-prefixed functions/methods; inside `Test`-prefixed classes (`python_classes`, default `Test*`) that have **no `__init__` method** — plain `@staticmethod`/`@classmethod` methods count. `unittest.TestCase` subclasses are collected via their `test*` methods.
- `collect_imported_tests = false` (8.4+) restricts collection to classes/functions **defined in** the test file (not imported into its namespace) — prevents collecting production classes whose names start with `Test`.

Import modes (`--import-mode=`):

- `prepend` (default) — pytest inserts the module's "basedir" (first upward directory without `__init__.py`) into `sys.path` and imports with the full package name. Consequences: test files without `__init__.py` must have **unique basenames** per run (they are imported as top-level modules); with `__init__.py` packages the repo root lands on `sys.path` (local code shadows installed code — e.g., under tox).
- `append` — same, but appends instead of prepends.
- `importlib` — no `sys.path` manipulation at all; same-named test modules in different packages work, and the installed version of your package is used. **Recommended for new projects** (`addopts = ["--import-mode=importlib"]`).

`pythonpath = ["src"]` (ini) prepends paths to `sys.path` before test collection (the alternative to setting `PYTHONPATH`).

Namespace packages: `consider_namespace_packages = true` (8.1+) makes pytest treat PEP 420 native namespace packages during collection; since 9.0 it also allows them as `--pyargs` targets (`pytest --pyargs my.namespace.pkg`).

## Key configuration options

Common `pytest.toml` entries (INI equivalents exist for all of them):

- `addopts` — default CLI arguments (e.g., `["-ra", "-q", "--import-mode=importlib"]`)
- `testpaths` — where to collect when no args are given (supports globs incl. `**`)
- `norecursedirs` — glob patterns of directories to skip
- `markers` — registered custom marks (`"name: description"`)
- `filterwarnings` — warning filters (list, last match wins)
- `usefixtures` — fixtures applied to all tests (same as `@pytest.mark.usefixtures` everywhere)
- `minversion` — abort if pytest is older
- `cache_dir` — cache location (default `.pytest_cache`)
- `strict` — enable all strictness options (9.0); plus individual `strict_config`, `strict_markers`, `strict_parametrization_ids`, `strict_xfail` (alias `xfail_strict`)
- `empty_parameter_set_mark` — what empty `parametrize` argvalues do (default: skip)
- `log_level`, `log_cli`, `log_cli_level`, `log_file*` — logging capture/live/file
- `junit_family`, `junit_duration_report`, `junit_log_passing_tests`, `junit_suite_name` — JUnit XML report options
- `tmp_path_retention_count` (default `"3"`), `tmp_path_retention_policy` (`all`/`failed`/`none`)
- `truncation_limit_chars` (640), `truncation_limit_lines` (8) — assertion output truncation
- `faulthandler_timeout` (seconds, 0=off), `faulthandler_exit_on_timeout` (9.0, default `false`)
- `python_files`, `python_classes`, `python_functions` — discovery patterns
- `pythonpath` — paths prepended to `sys.path`
- `collect_imported_tests` (8.4, default `true`), `consider_namespace_packages` (8.1, default `false`)
- `console_output_style` — `progress` (default) | `classic` | `count` | `times` | `progress-even-when-capture-no`
- `required_plugins` — abort if the named plugins are missing
- `assertion_text_diff_style` (9.1: `ndiff` | `block`), `verbosity_assertions`, `verbosity_test_cases`, `verbosity_subtests` — fine-grained output control (default `"auto"`)

## Command-line invocation

```bash
pytest                       # collect from testpaths or CWD
python -m pytest             # same, but CWD is also added to sys.path
pytest -h                    # help: CLI flags and config options
pytest --version             # 9.0+: fast, CLI-only (no plugins loaded); double --version lists plugins
```

Reporting and behavior flags (most have ini/config counterparts where noted):

- `-q`/`--quiet`, `-v` (repeatable) — verbosity
- `-r CHARS` / `--report-chars` (9.1 long form) — short summary entries: `x` xfailed, `X` xpassed, `f` failed, `F` failed+errors, `E` errors, `s` skipped, `S` skipped+errors, `w` warnings, `W` warnings+errors, `p` passed, `P` passed+warnings, `a` all
- `-x` stop at first failure, `--maxfail=N` stop after N
- `--tb=auto|long|short|line|native` traceback style (`native` for pdb-style, useful when patching builtins)
- `--durations=N --durations-min=X` — slowest tests
- `--show-capture=no|stdout|stderr|log|all`, `--no-header`
- `--setup-show`, `--setup-plan` — fixture setup order
- `--collect-only` (or `-co`) — list what would run; `--collect-only -q` gives bare node ids (feed back via `@file`)
- `--fixtures [test-id]`, `--markers` — list fixtures/marks
- `--lf/--ff/--nf/--sw` — cache-based rerun (see [06](06-capture-mock-env.md#cache-and-rerunning-failures))
- `-W` warning filters, `--max-warnings` (9.1), `--maxfail`
- `-o name=value` — override ini options
- `--capture=fd|sys|tee-sys|no` (-s = no), `--basetemp=dir`
- `--junitxml=file` — JUnit XML report
- `--import-mode=importlib` (recommended), `--rootdir=path`, `-c FILE`
- `--keep-duplicates` (9.0) — run explicitly repeated paths multiple times
- `--doctest-modules`, `--doctest-glob=GLOB`, `doctest_optionflags`, `doctest_encoding`, `doctest_namespace` fixture (doctests do **not** support parametrized fixtures — including parametrized autouse — since before 9.1)
- `-p NAME` / `-p no:NAME` — early-load / disable a plugin (e.g., `-p no:doctest`, `-p no:cacheprovider`, `-p no:legacypath`, `-p no:logging`, `-p no:terminalprogress`, `-p no:assertion`)
- Environment: `PYTEST_ADDOPTS` (extra args), `PYTEST_PLUGINS` (comma-separated plugins to load), `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `PYTEST_DEBUG_TEMPROOT`, `PYTEST_THEME`/`PYTEST_THEME_MODE` (syntax highlighting)

## Selecting tests

```bash
pytest tests/                          # directory
pytest test_mod.py                     # file
pytest tests/test_mod.py::test_func    # node id
pytest tests/test_mod.py::TestClass    # whole class
pytest "tests/test_mod.py::test_func[x1,y2]"   # one parametrization (quote it)
pytest -k "MyClass and not method"     # case-insensitive keyword expression (and/or/not)
pytest -m "slow and not integration"   # marker expression
pytest --pyargs mypkg.testing          # tests of an installed package
pytest --deselect tests/test_x.py::test_y
pytest @tests_to_run.txt               # args from file, one per line (8.2+); generate with --collect-only -q
```

In `-k` expressions, `""` instead of `''` is safer on Windows.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | all tests passed (and collected) |
| 1 | some tests failed |
| 2 | execution interrupted (e.g., `KeyboardInterrupt`) |
| 3 | internal error |
| 4 | usage error (bad CLI/config) |
| 5 | no tests were collected |
| 6 | max number of warnings exceeded (`--max-warnings`, 9.1) |

`pytest.main()` returns these as `pytest.ExitCode` values.

## CI behavior

Since 9.0, CI mode activates when `$CI` or `$BUILD_NUMBER` is set to a **non-empty** value (before 9.0, merely being defined sufficed). Effects: short-summary messages are not truncated to terminal width, and assertion output truncation limits are disabled.

## Programmatic use

```python
import pytest

retcode = pytest.main(["-x", "mytestdir"])      # returns ExitCode, does not raise SystemExit
retcode = pytest.main(["-qq"], plugins=[MyPlugin()])
```

- No arguments → reads `sys.argv` (often undesirable); pass explicit args.
- `pytest.main()` imports your test modules; calling it **multiple times in one process** does not pick up file changes (import caching) — not recommended for rerun loops.
- `pytest.console_main()` is deprecated (9.1) — it is the CLI entry point, not the programmatic API.

## Plugins

- External plugins are discovered via entry points (group `pytest11`) and loaded automatically; `required_plugins` ini aborts the run if a needed plugin is missing.
- Early-load or disable on the command line: `-p myproject.plugins` (dotted importable name or entry-point name, e.g., `-p pytest_cov`), `-p no:cacheprovider`. **conftest files cannot be disabled via `-p no:`** (since 9.0.3 a clear `UsageError`).
- `PYTEST_PLUGINS` env var loads plugins without installing them; `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` skips auto-loading entirely.
- `conftest.py` files double as local plugins: fixtures, hooks, and `pytest_addoption` (initial conftests only) all work there.
- Writing plugins: implement `pytest_*` hooks in a module/class; `@pytest.hookimpl(tryfirst=True)` / `trylast=True` / `hookwrapper=True` control call order (`specname=` only works for names starting with `pytest_`). Use `parser.addini()` / `parser.addoption()` in `pytest_addoption` to register config options (the `aliases=` parameter, 9.0+, registers alternative option names). See `pytest.freeze_includes()` for freezing test-included files.

## Reporting extras

- **JUnit XML**: `--junitxml=path`; `record_property` fixture adds properties to the JUnit test element, `record_xml_attribute` adds attributes. Since 9.0.3 the `<testsuite tests="...">` attribute always matches the `<testcase>` count.
- **`record_property`/`record_xml_attribute`** — request in the test to annotate reports.
- **Pastebin**: the old `--pastebin` option is deprecated (9.1); install the `pytest-pastebin` plugin to keep it.
- **Terminal progress**: OSC 9;4 tab progress via the `terminalprogress` plugin — disabled by default except on Windows since 9.0.2 (`-p terminalprogress` to enable, `-p no:terminalprogress` to force off; no escape codes with `TERM=dumb`).

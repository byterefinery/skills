# What's new in pytest 9 (9.0.0 → 9.1.1)

## Contents

- [9.1.1 (2026-06-19)](#911-2026-06-19)
- [9.1.0 (2026-06-13)](#910-2026-06-13)
  - [Features](#features)
  - [Behavior changes](#behavior-changes)
  - [Deprecations (removal in pytest 10)](#deprecations-removal-in-pytest-10)
- [9.0.0 (2025-11-05)](#900-2025-11-05)
  - [Subtests](#subtests)
  - [Native TOML configuration](#native-toml-configuration)
  - [Strict mode](#strict-mode)
  - [Other features](#other-features)
  - [Breaking changes](#breaking-changes)
  - [Removed features](#removed-features)
- [Patch releases 9.0.1–9.0.3](#patch-releases-901903)
- [Removed in 9.1](#removed-in-91)
- [Porting from 8.x — checklist](#porting-from-8x--checklist)

## 9.1.1 (2026-06-19)

Bug-fix release:

- Fixed a logic bug in `pytest.RaisesGroup` that produced incorrect "It matches `FooError()` which was paired with `BarError`" messages.
- Fixed a 9.1.0 regression where overriding a parametrized fixture with an indirect `@pytest.mark.parametrize` failed with "duplicate parametrization of '<fixture name>'".
- Fixed `conftest.py` files in `<invocation dir>/test*` not being loaded as initial conftests when invoked without arguments (hooks like `pytest_addoption` in them no longer miss).
- Fixed mypy typing of `parametrize` `argvalues`.

## 9.1.0 (2026-06-13)

### Features

- **`pytest.register_fixture()`** — imperative fixture registration, intended for plugins when the declarative `@pytest.fixture` decorator is impractical. Fixture scoping uses the `node` parameter (not the deprecated `nodeid` string); `node=session` gives global visibility.
- **`--max-warnings` CLI option and `max_warnings` ini option** — fail the run (exit code `6`, `ExitCode.MAX_WARNINGS_ERROR`) when all tests pass but the total warning count exceeds the threshold. Filtered-out warnings do not count.
- **`--report-chars`** — long form of the existing `-r CHARS` report option.
- **`assertion_text_diff_style`** ini option (`ndiff` default; `block` renders string-equality failures as separate `Left:` / `Right:` blocks instead of `ndiff` output).
- **`pytest.approx` supports `datetime` and `timedelta`** — `abs` must be a `timedelta`; `rel` is not supported for datetime comparisons, while for timedelta `rel` is a plain number (fraction of the expected value). See [05-assertions](05-assertions.md).
- **Official Python 3.15 support.**
- **Fixture override resolution is visibility-based** — a fixture defined for a more specific node (module/item) now always beats one defined for a more general node (session), even if the general one was registered later; same-visibility fixtures keep "last registered wins". Mostly affects plugins registering same-named fixtures programmatically.
- **`caplog` captures logs from non-propagating loggers** — previously only log records that reached the root logger were captured.
- **Improved diagnostics** — clearer "DID NOT RAISE" messages (exception type name instead of `repr`); `pytest.warns` reports "Regex pattern did not match" instead of "DID NOT WARN" when warnings were emitted but `match` failed; `PytestCollectionWarning` (not a cryptic `TypeError`) when a module-level `__getattr__` returns `None` for `pytestmark`; dict-diff output preserves key insertion order.
- **`pytest.ScopeName` is public** for use in type annotations.

### Behavior changes

- **`--doctest-modules`** — autouse fixtures with `module`, `package`, or `session` scope defined inline in Python test modules (not in plugins/conftests) may now execute twice, because the module can be collected both as a `Module` and as a `DoctestModule`. If that is undesirable, move the fixture definition to a `conftest.py`.

### Deprecations (removal in pytest 10)

- **Class-scoped fixtures defined as instance methods** (without `@classmethod`) — such fixtures set attributes on a different instance than the tests use. Use `@classmethod` and set class attributes.
- **`request.getfixturevalue()` during teardown** to request a fixture that was not already requested — brittle because teardown runs while scopes are unwinding. Request the fixture before the `yield` (declare it in the fixture signature, or call `getfixturevalue` before yielding).
- **Non-`Collection` iterables as `argvalues`** in `@pytest.mark.parametrize` / `metafunc.parametrize` — generators and iterators are exhausted after the first iteration, causing unexpected skips when collecting multiple times (e.g., class-level `parametrize`, repeated `pytest.main()`). Wrap in `list()`/`tuple()`; `range` is a `Collection` and unaffected.
- **`config.inicfg`** (private attribute) — use `config.getini()` instead. It was restored with a compatibility shim in 9.0.2 and is now deprecated.
- **Passing `baseid`/`nodeid` strings to fixture registration APIs** (`FixtureDef`, `FixtureManager.parsefactories`/`_register_fixture`) — use the `node` parameter instead.
- **Configuring hooks using markers** (deprecated since 7.2).
- **`--pastebin` option** — extracted to the external `pytest-pastebin` plugin.
- **`pytest.console_main()`** — never intended for programmatic use; use `pytest.main()`.
- **Private `FixtureDef.has_location` attribute** — obsolete after the visibility-based override resolution above.

## 9.0.0 (2025-11-05)

### Subtests

Subtests are now built into core pytest (previously the `pytest-subtests` plugin). They group assertions inside a normal test, useful when parametrization values are not known at collection time. The feature is **experimental** — functionality and usage are stable, but failure reporting may evolve.

```python
def test_files_contain_docstring(subtests):
    for path in Path.cwd().glob("*.py"):
        with subtests.test(path=str(path)):
            assert has_docstring(path)
```

- Each assertion failure or error inside the `with subtests.test(...)` block is caught and reported individually as `SUBFAILED`; the top-level test fails with "contains N failed subtests".
- `subtests.test(msg=..., **kwargs)` — extra kwargs appear in the report (e.g., `test [custom message] (i=1)`).
- You can mix multiple subtests blocks with normal assertions in the same test.
- Compact progress shows `u` for passed and failed subtests; by default only subtest failures are shown. `-v` (or `verbosity_subtests = "1"`) also shows passed subtests; `verbosity_subtests = "0"` suppresses them.
- `pytest.Subtests` is exported for type annotations: `def test(subtests: pytest.Subtests) -> None`.
- `unittest.TestCase.subTest` is also supported since 9.0.
- Differences vs `@pytest.mark.parametrize` — parametrization happens at collection time, generates individually selectable tests, and plays with execution plugins (`--last-failed`); subtests happen at execution time, can be generated dynamically, cannot be referenced individually from the command line, and a failure inside a subtest does not interrupt the test (all failures appear in one report).

### Native TOML configuration

pytest 9.0 uses the native TOML data model (before, values in `pyproject.toml` were treated as strings/strings-lists in an "INI compatibility mode"):

- `pyproject.toml` under **`[tool.pytest]`** — native TOML types (real arrays, booleans, ints).
- New dedicated files **`pytest.toml` / `.pytest.toml`** with a `[pytest]` table.
- `[tool.pytest.ini_options]` remains supported, but **both tables cannot be used at the same time** in one `pyproject.toml`.

```toml
# pytest.toml
[pytest]
minversion = "9.0"
addopts = ["-ra", "-q"]
testpaths = ["tests", "integration"]
```

### Strict mode

The new **`strict = true`** config option enables a bundle of strictness options at once:

- `strict_config` — config-file parsing warnings become errors
- `strict_markers` — unregistered marks become errors
- `strict_parametrization_ids` (new in 9.0) — duplicate auto-generated parameter-set IDs become errors instead of being silently suffixed with `0`, `1`, ...
- `strict_xfail` — `XPASS` results fail the suite by default (alias of the old `xfail_strict`)

Individually set `strict_*` options override the global `strict` setting (e.g., `strict = true` with `strict_parametrization_ids = false`). Note that any **new** strictness option added by pytest in the future will also be enabled by `strict` — only enable strict mode with a pinned/locked pytest version if that is not what you want.

Related renames: `strict_xfail` (alias `xfail_strict`), `strict_config` (alias for `--strict-config`), `strict_markers` (alias for `--strict-markers`) give all strictness options a consistent `strict_` prefix. In 9.x, prefer the `strict_markers`/`strict_config` ini options over `--strict-markers`/`--strict-config` in `addopts` (a 9.0 regression that ignored them in `addopts` was fixed in 9.1).

### Other features

- **Terminal tab progress** (OSC 9;4) — progress indicator in the terminal tab on supporting emulators (Windows Terminal, ConEmu, GNOME, Kitty, Ghostty...). Automatically enabled in a TTY; internal plugin `terminalprogress` (`-p no:terminalprogress` disables). **Disabled by default since 9.0.2 except on Windows** due to compatibility issues; re-enable with `-p terminalprogress`. No escape codes when `TERM=dumb`.
- **PEP 420 namespace packages as `--pyargs` targets** when `consider_namespace_packages = true` (option itself since 8.1; now also affects test discovery via `--pyargs`).
- **`faulthandler_exit_on_timeout`** (default `false`) — with `faulthandler_timeout`, exit the pytest process after the timeout instead of only dumping thread tracebacks (useful for CI deadlock protection).
- **Config option aliases** — `Parser.addini(aliases=[...])` lets plugins register alternative names for options; the canonical name always wins if both are set.
- **`--version` is faster** (skips loading the plugin infrastructure) and now only takes effect when passed directly on the command line — it no longer works via `addopts` or `PYTEST_ADDOPTS`. `pytest --version --version` keeps the old behavior (version + plugin list).
- **`config.args`** is now only strings (no `pathlib.Path` instances).

### Breaking changes

- **Python 3.9 support dropped** (EOL) — 9.0+ requires Python 3.10+.
- **`PytestRemovedIn9Warning` deprecation warnings are errors by default** — every use of a feature slated for removal in 9 now fails instead of warning. (The 9.0.x stopgap `filterwarnings = ignore::pytest.PytestRemovedIn9Warning` no longer works in 9.1+; the features are gone.)
- **Overlapping/duplicate path arguments** — `pytest a/b a/` or `pytest a/ a/b` now equal `pytest a` (the prefix remains); `pytest x.py x.py` equals `pytest x.py` (previously: run twice). `--keep-duplicates` retains the old behavior. Nonsensical invocations like `pytest x.py[a]` are now a usage error.
- **CI detection** — CI mode activates only if `$CI` or `$BUILD_NUMBER` is defined **and non-empty** (previously, being defined at all was enough).
- **Multiple config files** — having pytest configuration in more than one file (e.g., `pytest.ini` and `pyproject.toml` with `[tool.pytest.ini_options]`) now prints a warning; only one file is ever used (first match wins).
- **Hidden `.pytest.ini` files are picked up even when empty** (consistency with `pytest.ini`).
- **`pyproject.toml` is always considered a candidate config file** (even without a `[tool.pytest]` table) when nothing else matches.

### Removed features

- **Sync tests depending on async fixtures** — now an error. Wrap the async fixture in a sync wrapper that returns the coroutine, e.g.:

  ```python
  @pytest.fixture
  def unawaited_fixture():
      async def inner_fixture():
          return 1
      return inner_fixture()
  ```

- **Applying marks to fixture functions** — was a silent no-op, now an error (common user mistake, e.g., `@pytest.mark.usefixtures` above `@pytest.fixture`).
- **`py.path.local` arguments for hooks** — replaced by `pathlib.Path` kwargs: `pytest_ignore_collect(collection_path)`, `pytest_collect_file(file_path)`, `pytest_pycollect_makemodule(module_path)`, `pytest_report_header(start_path)`, `pytest_report_collectionfinish(start_path)`. (Note the confusing historical naming: for *hooks* the new arg is `*_path`, for *Node constructors* the new arg is `path`.)
- **`yield`-style tests** (tests that `yield` callables) — collection error since 8.4; `pytest.yield_fixture` remains a deprecated alias for `@pytest.fixture`.

## Patch releases 9.0.1–9.0.3

- **9.0.1** — restored `raise unittest.SkipTest` skipping; `terminalprogress` auto-disabled when iTerm2 is detected.
- **9.0.2** — `terminalprogress` disabled by default except on Windows; `config.inicfg` restored via compatibility shim (deprecated in 9.1); TOML type docs fixed.
- **9.0.3** — `-p no:` can no longer be used to block a `conftest.py` (now a clear `UsageError`, not an internal assertion failure); fixed an insecure temporary directory (CVE-2025-71176); `pytest.approx` now considers `Mapping` key order; blocking a `conftest` via `-p` raises a clear error.

## Removed in 9.1

- **`pytest.importorskip` default behavior** — since 9.1 it captures only `ModuleNotFoundError` by default (the 8.2+ `exc_type` parameter controls this). A broken-but-installed package now surfaces the real import error instead of silently skipping. Pass `exc_type=ImportError` to keep the traditional behavior.
- **`fspath` argument to Node constructors** (`pytest.Function.from_parent()` etc.) — pass `path` (`pathlib.Path`) instead. Nodes keep both `fspath` (`py.path.local`) and `path` attributes for now.

## Porting from 8.x — checklist

1. Drop Python 3.9 from CI matrix; add 3.14/3.15 if needed.
2. Fix anything that raised `PytestRemovedIn9Warning` under 8.x (yield tests, marks on fixtures, `py.path.local` hook args, sync tests requesting async fixtures) — they are errors now.
3. Audit `pytest.importorskip` call sites for the new `ModuleNotFoundError`-only default.
4. If you relied on running a file twice (`pytest x.py x.py`) or overlapping paths, add `--keep-duplicates`.
5. Move module-level autouse fixtures used with `--doctest-modules` into `conftest.py`.
6. Consider migrating config to native TOML (`pytest.toml` or `[tool.pytest]`) and enabling `strict = true` (or the individual `strict_*` options) on a pinned version.
7. Plugin authors: move off `config.inicfg`, `baseid`/`nodeid` registration args, and `pytest.console_main()` before pytest 10.

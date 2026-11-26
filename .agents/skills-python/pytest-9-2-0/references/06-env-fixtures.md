# Environment fixtures: capture, logging, monkeypatch, tmp, cache

Grounded in `doc/en/how-to/capture-stdout-stderr.rst`, `doc/en/how-to/logging.rst`, `doc/en/how-to/monkeypatch.rst`, `doc/en/how-to/tmp_path.rst`, `doc/en/how-to/cache.rst`, and `doc/en/reference/fixtures.rst` of the 9.2.0 tag.

## stdout/stderr capture

- **Default** is fd-level capture (OS file descriptors 1 and 2), so prints, C-level output, and subprocesses are captured; captured output of failed tests is shown with the traceback. `stdin` becomes a null object that fails on read.
- **Modes** — `--capture=fd` (default), `--capture=sys` (only `sys.stdout`/`sys.stderr`), `--capture=tee-sys` (capture + pass through, live printing), `-s` (disable all).
- **Since 9.2** fd-level capture skips reading the buffer for tests that produced no output (per-test overhead reduced).

### Fixtures

| Fixture | Purpose |
|---|---|
| `capsys` | text `stdout`/`stderr` at `sys` level |
| `capfd` | text at OS file-descriptor level (also captures subprocess/C output) |
| `capsysbinary` / `capfdbinary` | bytes variants |
| `capteesys` | like `capsys` but passes text through according to `--capture` |

`readouterr()` returns a `namedtuple` (`out`, `err`) and **snapshots** — capturing continues afterward; call again for later output. `capsys.disabled()` context manager temporarily disables capture. Using a capture fixture takes precedence over global `-s`/`--capture=no`.

```python
def test_myoutput(capsys):
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
```

## Logging

- **Auto-captured** — messages at `WARNING`+ are captured and shown in their own section for failed tests. Format via `--log-format` / `--log-date-format` (or ini `log_format`, `log_date_format`); disable specific loggers with `--log-disable=name`; `--show-capture=no` hides all captured content on failures.
- **`caplog` fixture**:
  - `caplog.set_level(logging.INFO)` — default targets the root logger; `logger="name"` targets a specific one; levels restored after the test.
  - `caplog.at_level(level, logger=...)` — context manager form.
  - `caplog.records` — `LogRecord` list; **current phase only** (setup/call/teardown). Use `caplog.get_records("setup"|"call"|"teardown")` for other phases.
  - `caplog.text`, `caplog.record_tuples` (list of `(logger_name, level, message)`), `caplog.clear()`.
  - **Warning:** reconfiguring the root logger (e.g., `dictConfig`) can remove pytest's handler and silently stop capture — only add handlers.
- **Live logs** — ini `log_cli = true` prints records to the console as emitted; `--log-cli-level`, `--log-cli-format`, `--log-cli-date-format`. Live logs go to `sys.stdout` (no `-s` needed).
- **Log file** — `--log-file=path` (write mode; `--log-file-mode=a` appends), `--log-file-level`, `--log-file-format`, `--log-file-date-format`. Relative paths resolve against the CWD.
- The logging plugin replaces `pytest-catchlog`; disable it with `-p no:logging` if you must use the old plugin.

## `monkeypatch`

Temporarily modifies objects; everything is reverted after the test. Methods:

- `monkeypatch.setattr(target, name, value, raising=True)` — patch attributes/functions (`Path.home`, `requests.get`, …); `raising=False` allows patching a missing attribute; `setattr("module.attr", ...)` string form works for modules.
- `monkeypatch.delattr(obj, name, raising=True)`
- `monkeypatch.setenv(name, value, prepend=None)` / `delenv(name, raising=True)` — environment variables; `setenv("PATH", v, prepend=os.pathsep)` prepends to PATH.
- `monkeypatch.setitem(mapping, key, value)` / `delitem(mapping, key)`
- `monkeypatch.chdir(path)`
- `monkeypatch.syspath_prepend(path)`
- `monkeypatch.context()` — use a `MonkeyPatch` instance manually as a context manager.

Typical pattern: `setattr` a stub function or object (e.g., a `MockResponse` class) to fake network calls.

## Temp directories

- **`tmp_path`** — `pathlib.Path`, unique per test function.
- **`tmp_path_factory`** — session-scoped factory; `tmp_path_factory.mktemp("data")` creates arbitrary dirs (e.g., share an expensive artifact across tests).
- **`tmpdir` / `tmpdir_factory`** — legacy `py.path.local` variants; prefer the pathlib versions. Run `pytest -p no:legacypath` to error on legacy usage and modernize a codebase.
- **Location/retention** — default template `{temproot}/pytest-of-{user}/pytest-{num}/{testname}/` (`{temproot}` = `tempfile.gettempdir()`, overridable via `PYTEST_DEBUG_TEMPROOT`). Last 3 runs kept by default; configure with `tmp_path_retention_count` and `tmp_path_retention_policy` (value-registered since 9.2 — invalid values are usage errors). `--basetemp=mydir` uses that dir directly with **no retention and blind clearing each run** — dedicate the directory.

## Cross-run cache

- **`--lf/--last-failed`** — rerun only failures from the last run (others deselected).
- **`--ff/--failed-first`** — run failures first, then the rest.
- **`--nf/--new-first`** — run new tests first; files sorted by modification time (most recent first).
- **`--lfnf/--last-failed-no-failures`** — `all` (default) runs everything when no failures are known; `none` exits successfully without running.
- **`--sw/--stepwise`** — stop at the first failure; next run continues from it. `--sw-skip` skips the currently stuck failing test and stops at the next one (implies `--stepwise`).
- **`cache` fixture** — `cache.get("key", default)` / `cache.set("key", value)` for JSON-encodable values across runs; inspect with `--cache-show [glob]`, wipe with `--cache-clear` (recommended in CI).
- Plugin/conftest access: `pytestconfig.cache` (may be absent if the plugin is disabled — internal name `cacheprovider`).

## Other builtin fixtures

- **`request`** — the requesting test context: `request.node`, `request.module`, `request.cls`, `request.param`, `request.fspath`/`request.path`; `getfixturevalue("name")` for dynamic requests.
- **`pytestconfig`** — configuration object, plugin manager, ini access.
- **`recwarn`** — records warnings emitted by the test (with `__str__` including location info); assert with `any("..." == str(w.message) for w in recwarn)`.
- **`doctest_namespace`** — dict injected into doctests' namespace.
- **`record_property`** / **`record_testsuite_property`** — add properties to test/suite (JUnit XML).
- **`testdir`** — temporary test directory for testing plugins (run pytest in-process).
- **`subtests`** — see [03-parametrize](03-parametrize.md).
- **`capsys`/`capfd`/`capteesys`/binary, `caplog`, `monkeypatch`, `tmp_path`(+factory), `tmpdir`(+factory), `cache`, `request`, `pytestconfig`** are the full builtin set per the fixtures reference.

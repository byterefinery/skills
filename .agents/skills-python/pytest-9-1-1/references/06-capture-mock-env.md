# Capture, monkeypatching, temp dirs, cache, warnings

## Contents

- [Capturing stdout/stderr](#capturing-stdoutstderr)
- [`caplog`](#caplog)
- [`monkeypatch`](#monkeypatch)
- [`tmp_path` and `tmp_path_factory`](#tmp_path-and-tmp_path_factory)
- [`cache` and rerunning failures](#cache-and-rerunning-failures)
- [Warnings capture and control](#warnings-capture-and-control)

## Capturing stdout/stderr

During each test, pytest captures writes to stdout/stderr and (unless disabled) points stdin at a null object so tests never block on input. Captured output of a **failing** test is shown in its report (`--show-capture` controls which phases: `no`, `stdout`, `stderr`, `log`, `all` (default)).

Capture modes (`--capture=`):

- `fd` (default) — replaces OS file descriptors 1 and 2; catches output from C libraries and subprocesses
- `sys` — replaces only `sys.stdout`/`sys.stderr`
- `tee-sys` — like `sys`, but also passes output through to the real streams (live printing + capture)
- `no` — no capturing (equivalent to `-s`)

Access captured output from inside a test:

```python
def test_output(capsys):                 # or capfd / capsysbinary / capfdbinary / capteesys
    print("hello")
    captured = capsys.readouterr()       # namedtuple(out=..., err=...)
    assert captured.out == "hello\n"

    with capsys.disabled():              # temporarily stop capturing
        print("goes straight to the terminal")
```

- `capsys`/`capsysbinary` — `sys` level (text/bytes); `capfd`/`capfdbinary` — file-descriptor level (text/bytes), needed when the code writes via C or forks subprocesses; `capteesys` — captured **and** passed through.
- `readouterr()` is a **snapshot**: it returns output so far and capturing continues, so you can call it multiple times.
- Requesting a capture fixture takes precedence over `-s`/`--capture=no` — the fixture still captures (clarified in 9.0.3).

## `caplog`

pytest captures log records at **WARNING level and above** by default and shows them in failed tests' reports ("Captured log call"). Inside tests:

```python
import logging

def test_logging(caplog):
    caplog.set_level(logging.INFO)               # for the whole test (root logger)
    caplog.set_level(logging.DEBUG, logger="mymodule.db")
    do_work()
    assert "done" in caplog.text
    for record in caplog.records:                # logging.LogRecord instances
        assert record.levelname != "CRITICAL"
    assert caplog.record_tuples == [("root", logging.INFO, "boo arg")]

    with caplog.at_level(logging.WARNING, logger="root.baz"):
        do_work_loudly()

    caplog.clear()                               # drop captured records
```

- `set_level`/`at_level` are restored automatically after the test.
- **`caplog.records` contains only the current phase** (setup, call, or teardown). For other phases use `caplog.get_records("setup" | "call" | "teardown")` — e.g., a teardown fixture checking that its fixture never logged warnings:

  ```python
  @pytest.fixture
  def window(caplog):
      w = create_window()
      yield w
      msgs = [r.message for r in caplog.get_records("call") if r.levelno >= logging.WARNING]
      if msgs:
          pytest.fail(f"warnings during test: {msgs}")
  ```

- **Since 9.1, log records from non-propagating loggers are captured too** — previously only records that reached the root logger were seen.
- **Warning**: reconfiguring the root logger during a test (e.g., `logging.config.dictConfig` with a handler list that doesn't include pytest's handler) removes the capture handler and silently drops logs. Root-logger configuration must *add* to existing handlers.
- Change the global capture level with `log_level` (ini) / `--log-level`; disable specific loggers with `--log-disable=NAME` (repeatable).

Live logs and files:

```toml
[pytest]
log_cli = true                 # print records to the console as they are emitted
log_cli_level = "INFO"
log_cli_format = "%(asctime)s %(levelname)s %(message)s"
log_file = "tests.log"         # append: log_file_mode = "a"
log_file_level = "INFO"
```

## `monkeypatch`

The `monkeypatch` fixture temporarily modifies objects, dictionaries, environment variables, and `sys.path`; **all modifications are undone automatically** after the requesting test/fixture finishes:

```python
def test_home(monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: Path("/abc"))
    monkeypatch.setenv("USER", "tester")
    monkeypatch.setenv("PATH", "/opt/bin", prepend=os.pathsep)   # prepend to PATH
    monkeypatch.delenv("OLD_VAR", raising=False)
    monkeypatch.setitem(app.DEFAULT_CONFIG, "user", "test_user")
    monkeypatch.delitem(app.DEFAULT_CONFIG, "token")
    monkeypatch.syspath_prepend(str(src_dir))
    monkeypatch.chdir(tmp_path)
```

- `setattr(obj, name, value, raising=True)` / `delattr` / `setitem` / `delitem` / `setenv` / `delenv` — `raising` controls whether a missing target raises (`KeyError`/`AttributeError`) or is ignored.
- `setattr` accepts a `"module.attr"` string target; patch the reference **your code uses** (if the module does `from os import getcwd`, patch `mymodule.getcwd`, not `os.getcwd`), or the patch is bypassed.
- **Avoid patching builtins** (`open`, `compile`, ...) — it can break pytest internals (assertion rewriting, tracebacks). If unavoidable, `--tb=native --assert=plain --capture=no` may help, with no guarantee.
- **`monkeypatch.context()`** (scoped patching) — apply patches only inside a `with` block; the safe way to patch stdlib or third-party objects pytest itself relies on:

  ```python
  def test_partial(monkeypatch):
      with monkeypatch.context() as m:
          m.setattr(functools, "partial", 3)
          assert functools.partial == 3
      # patch gone here
  ```

- `syspath_prepend` also invalidates the import caches; since 9.0 it warns when the prepended path contains **legacy** (`pkg_resources.declare_namespace`) namespace packages — migrate to native PEP 420 namespace packages.

## `tmp_path` and `tmp_path_factory`

- `tmp_path` — a unique `pathlib.Path` directory per test, created automatically.
- `tmp_path_factory` — session-scoped factory for arbitrary temp dirs, used to build shared expensive artifacts once:

  ```python
  @pytest.fixture(scope="session")
  def big_image(tmp_path_factory):
      path = tmp_path_factory.mktemp("data") / "img.png"   # numbered unique dir
      compute_expensive_image().save(path)
      return path
  ```

- Default location: `{temproot}/pytest-of-{user}/pytest-{num}/{testname}/`, where `{temproot}` is the system temp dir (override with `PYTEST_DEBUG_TEMPROOT`) and `{num}` increments per run.
- **Retention**: by default the last **3** runs' directories are kept — `tmp_path_retention_count = "N"`; `tmp_path_retention_policy` = `all` (default) | `failed` | `none`.
- **`--basetemp=dir`** — uses `dir` directly as the base and **wipes it blindly before every run**; use a dedicated directory and expect no retention.
- `tmpdir`/`tmpdir_factory` are the legacy `py.path.local` equivalents — prefer the `pathlib` versions. Run `pytest -p no:legacypath` (or add to `addopts`) to hard-error on legacy path usage while migrating.

## `cache` and rerunning failures

The built-in cache plugin (internal name `cacheprovider`) stores state in `.pytest_cache` under rootdir (override with `cache_dir`).

Rerun controls:

```bash
pytest --lf              # only rerun last failures
pytest --ff              # last failures first, then the rest
pytest --nf              # new tests first, then the rest (sorted by file mtime)
pytest --sw              # stepwise: stop at first failure; next run continues after it
pytest --stepwise-skip   # ignore one failure, stop at the second (enables --sw)
pytest --last-failed --last-failed-no-failures none   # if nothing failed: run nothing
```

`--last-failed-no-failures=all` (default) runs the full suite when there are no known failures. `--cache-clear` wipes all cache values (use in CI); `--cache-show [glob]` prints them; disable the plugin with `-p no:cacheprovider`.

Programmatic access (conftest/plugins) via the `pytestconfig` fixture:

```python
@pytest.fixture
def mydata(pytestconfig):
    cache = getattr(pytestconfig, "cache", None)   # None when cacheprovider is disabled
    if cache is not None:
        val = cache.get("example/value", None)
        if val is None:
            val = expensive_computation()
            cache.set("example/value", val)
    return val
```

Values must be JSON-encodable.

## Warnings capture and control

- Warnings emitted during tests are collected and printed in a session summary by default; `PytestRemovedIn9Warning` (and other pytest deprecation warnings) are **errors by default** in 9.x.
- Per-run: `-W error::UserWarning` (same filter syntax as Python's `-W`).
- Per-project:

  ```toml
  [pytest]
  filterwarnings = [
      "error",
      "ignore::UserWarning",
      "ignore:function ham\\(\\) is deprecated:DeprecationWarning",   # single-quoted TOML strings for raw regex
  ]
  ```

  When a warning matches several entries, the **last matching** action wins. A warning filter referencing an unimportable class no longer fails the run (9.0) — it prints a message instead.
- Per-test: `@pytest.mark.filterwarnings("ignore::DeprecationWarning")`.
- **`max_warnings` (9.1)** / `--max-warnings` — when all tests pass but the total warning count exceeds the limit, the run fails with exit code **6** (`MAX_WARNINGS_ERROR`). Filtered-out warnings don't count.

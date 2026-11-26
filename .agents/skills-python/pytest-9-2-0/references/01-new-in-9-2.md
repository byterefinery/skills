# New in pytest 9.2.0 (2026-10-27)

Grounded in `doc/en/changelog.rst` of the 9.2.0 tag.

## Removals and backward-incompatible changes

- **`-c` path validation** (`#14716`) — `-c` now raises a usage error for a path that does not exist, is a directory, or is in a format pytest has no loader for. Such paths were previously ignored or produced an unhandled `FileNotFoundError`.
- **`parametrize` args keyword-only** (`#8593`) — `indirect`, `ids`, `scope` of `Metafunc.parametrize()` (and therefore `@pytest.mark.parametrize`) are keyword-only. Passing them positionally (e.g., `parametrize("arg1", "arg2", [(1, 2)])`) now fails with a clear `TypeError` instead of landing argvalues in `indirect` and failing with `indirect fixture '(1, 2)' doesn't exist`.
- **Plugin import failure classification** (`#993`) — startup plugin import failures no longer escape as raw tracebacks with accidental exit code 1:
  - plugin not found (via `-p`, `pytest_plugins`, or `PYTEST_PLUGINS`) → exit code `USAGE_ERROR` (4), like a failing `conftest.py`;
  - plugin found but raises while importing (broken `pytest11` entry point, missing dependency) → exit code `INTERNAL_ERROR` (3), traceback preserved.
  - `pytest.main` now returns these codes instead of raising `ImportError`.

## Deprecations (removal scheduled for pytest 10 or 11)

- **`CallSpec2` renamed** (`#14742`) — private `_pytest.python.CallSpec2` renamed to `CallSpec`; the alias remains for now.
- **`yield_fixture` scheduled for removal** (`#14755`).
- **Higher-scoped instance-method fixtures** (`#14774`) — following the 9.1 deprecation of class-scoped instance-method fixtures, *all* higher-scoped fixtures (`module`, `package`, `session`) defined as instance methods are now deprecated. Same underlying problem: each test method gets a fresh class instance, so state set on `self` is invisible to tests. Use `@classmethod` and class attributes.
- **Non-string values for `string`-typed ini options** (`#14808`) — passing a non-string value to a `string`-typed ini option (affects `[tool.pytest.ini_options]` in `pyproject.toml`) now emits `PytestRemovedIn10Warning`; pytest 10 will raise `TypeError`.
- **`TerminalReporter.write_line()` bytes** (`#7323`) — passing `bytes` is deprecated; pass `str`.

## New features

- **Diff legend** (`#14743`) — the `Full diff:` output now includes a legend explaining the `+`/`-` symbols.
- **`-m` marker validation** (`#2781`) — with `strict_markers` enabled, marker names used in `-m` expressions are validated against registered markers (previously only decorated usage was checked).
- **`parametrize_long_str_id_strategy`** (`#6881`) — new config option controlling how long `str`/`bytes` parameter values appear in auto-generated test IDs (explicit `ids=[...]` or `pytest.param(..., id=...)` are unaffected). Strategies: `short` (default; values over 100 chars fall back to `argname+index`), `sha256`, `legacy` (keep full value), `disallow` (error asking for explicit IDs).

## Improvements

- **RecursionError rendering** (`#10745`) — a `RecursionError` whose recursion origin cannot be located shows only the first and last 10 stack frames (previously ~1000 near-identical frames); `--full-trace` shows all. Module statement line numbers are computed once per traceback, speeding up failures from large modules.
- **Hash-based rewrite cache** (`#11418`) — cached rewritten modules in `__pycache__` are invalidated by source hash (checked-hash pyc, PEP 552) instead of mtime, so restored caches survive CI checkouts that refresh mtimes. Existing timestamp-based caches are ignored and rewritten once.
- **Entry-point names in `pytest_plugins`/`PYTEST_PLUGINS`** (`#12624`) — both now accept installed-plugin entry-point names (e.g., `xdist`) in addition to importable module names, matching `-p`. Such plugins are also listed in the terminal header's `plugins:` line.
- **Plugin import warnings captured** (`#12697`) — warnings emitted while importing plugins via `-p`, `PYTEST_PLUGINS`, or entry-point autoloading are now captured, filtered, and reported like other warnings.
- **`dict.items()`/`dict.keys()` diffs** (`#12860`) — comparison diffs show missing items, like set comparisons.
- **`get_closest_marker` accepts `MarkDecorator` defaults** (`#13354`) — e.g., `item.get_closest_marker("foo", pytest.mark.foo(1))`; returns the wrapped `Mark`. Previously the only way to build a `default` was instantiating the private `pytest.Mark`.
- **`RunResult.assert_outcomes` error** (`#13369`) — clearer error when a plugin changes or removes pytest's standard terminal summary; docs describe isolating output-changing plugins.
- **`pytest.ParameterSet`** (`#13431`) — exposed as the return type of `pytest.param()` for annotations and `isinstance` checks.
- **Fixture decorator order warning** (`#13564`) — warns when a fixture is wrapped by a decorator that prevents correct discovery (`@classmethod` or `@staticmethod` *above* `@pytest.fixture`). Put `@pytest.fixture` above those decorators on test classes.
- **`pytest.Approx`** (`#14164`) — exposed as the return type of `pytest.approx()`.
- **Mapping key diffs** (`#14463`) — assertion diffs for mappings match keys the way the mappings compare their own keys (via key views), so e.g. case-insensitive header mappings no longer report common keys as missing.
- **Lazy capped diffs** (`#14523`) — large comparison diffs are built lazily and capped to the truncation budget; the truncation footer no longer reports the exact number of hidden lines.
- **fd-capture fast path** (`#14687`) — default fd-level capturing skips reading the capture buffer for tests that produce no output, reducing per-test overhead.
- **`--no-summary` scope** (`#14724`) — applies only to pytest's own summary; `pytest_terminal_summary` hook still runs (plugins can write their own).
- **`parser.addini` type expressions** (`#14751`) — the `type` argument now accepts Python type expressions (`str`, `bool`, `int`, `float`, string `Literal`, unions like `int | str`) in addition to string tags.
- **`approx` timedelta infinities** (`#14754`) — infinite relative tolerances for `timedelta` raise a clear `ValueError` instead of `OverflowError`.
- **Registered ini values** (`#14791`) — `junit_family`, `junit_logging`, `junit_duration_report`, `console_output_style`, `empty_parameter_set_mark`, `assertion_text_diff_style`, `tmp_path_retention_policy` are registered with their accepted values: invalid values fail with a clean usage error and `pytest --help` lists them. `config.getini` raises `pytest.UsageError` (not `TypeError`/`ValueError`) on a type mismatch; an unknown option name still raises `ValueError`.
- **`PytestApproxDecimalToleranceWarning`** (`#15006`) — `pytest.approx` warns when a `rel`/`abs` float tolerance cannot be represented exactly for a `Decimal` comparison (tolerance is widened to the float's binary value).
- **`pluggy>=1.6` required** (`#9236`) — older pluggy stopped running remaining hook-wrapper teardowns once an old-style `hookwrapper` raised in its own teardown, which left the logging plugin's wrapper suspended and broke later `caplog` capture.
- **Build** — building pytest from a git checkout now requires `setuptools-scm >= 10.1`.

## Internal / typing

- **`FixtureRequest.node`** (`#13888`) — explicitly annotated `Any` for strict pyright.
- **Structured internal node ids** (`#14758`) — internal node ids are now a structured `NodeId` dataclass instead of re-parsed strings; the public `nodeid: str` on nodes/reports is unchanged.

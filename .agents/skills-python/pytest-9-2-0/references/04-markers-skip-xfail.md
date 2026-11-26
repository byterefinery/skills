# Markers, skip, xfail

Grounded in `doc/en/how-to/mark.rst`, `doc/en/how-to/skipping.rst`, and `doc/en/example/markers.rst` of the 9.2.0 tag.

## Marks in general

`pytest.mark` sets metadata on test functions (and classes/modules). Builtin markers: `usefixtures`, `filterwarnings`, `skip`, `skipif`, `xfail`, `parametrize`. Custom markers are used by plugins and for CLI selection with `-m`.

**Marks can only be applied to tests — applying one to a fixture function is an error.**

List all markers (builtin + custom): `pytest --markers`.

## Registering marks

Config (TOML or INI), where text after `:` is an optional description:

```toml
[pytest]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "serial",
]
```

Or programmatically:

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "env(name): mark test to run only on named environment")
```

Unregistered marks used via `@pytest.mark.name` emit a warning (guards against typos). With `strict_markers` enabled (config or `addopts = ["--strict-markers"]`), unknown marks are **errors** — and since 9.2, marker names in `-m` expressions are validated against registered marks too.

## Skipping

- **`@pytest.mark.skip(reason=...)`** — always skip; `reason` is optional.
- **Imperative `pytest.skip(reason)`** — inside a test or setup when the condition can't be evaluated at import/collection time.
- **Module-level skip** — `pytest.skip("reason", allow_module_level=True)` at module level skips the whole module (e.g., `if not sys.platform.startswith("win"):`).
- **`@pytest.mark.skipif(condition, reason=...)`** — boolean condition evaluated at collection; skippable on functions and classes. Condition **strings** are supported for backward compatibility but can't be shared across modules; prefer booleans. Multiple `skipif` decorators skip if any condition is true.
- **Share markers between modules** — define once (`minversion = pytest.mark.skipif(...)`) and import into other test modules; for big suites keep one file defining shared markers.
- **Skip whole module** — `pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="linux only")`.
- **Skip on missing dependency** — `mod = pytest.importorskip("mod")` (module level, in a test, or in setup); `pytest.importorskip("docutils", minversion="0.3")` version-checks via the module's `__version__`. Skips rather than errors when the import fails.
- **Skip files/directories** — exclude from collection with `--ignore`/`--ignore-glob`/`collect_ignore` rather than skipping inside them (see [07-config-running](07-config-running.md)).
- **Reporting** — `-r xXs` (e.g., `pytest -rxXs`) shows details for xfailed/xpassed/skipped tests; without it, details are suppressed to keep output clean.

Quick decision guide:
1. Skip all in module unconditionally → `pytestmark = pytest.mark.skip("...")`
2. Skip all conditionally → `pytestmark = pytest.mark.skipif(cond, reason=...)`
3. Skip on missing import → `pytest.importorskip("dep")`

## xfail — expected failures

- **`@pytest.mark.xfail`** — test runs; failures report `XFAIL` (no traceback by default), passes report `XPASS`.
- **`condition` parameter** — `@pytest.mark.xfail(sys.platform == "win32", reason=...)`: first positional arg is the condition; a `reason` must also be given.
- **`raises=`** — only counts as xfail if the test fails with that exception (or subclass); any other failure is a regular failure.
- **`run=False`** — report as XFAIL without executing (for tests that crash the interpreter).
- **`strict=True`** — `XPASS` fails the suite. Default is controlled by the `xfail_strict` ini option (`xfail_strict = true` in TOML config; `strict_xfail` key in INI files).
- **Imperative `pytest.xfail("reason")`** — inside test/setup; raises internally, so **no code after it executes**.
- **`pytest --runxfail`** — run and report xfail tests as if unmarked; also disables `pytest.xfail()`.
- **xfail + parametrize** — apply via `pytest.param(..., marks=pytest.mark.xfail)` to individual instances (see [03-parametrize](03-parametrize.md)).

`xfail` with `raises=` is best for documenting unfixed bugs; `pytest.raises` is better for deliberately raised exceptions (see [05-assertions](05-assertions.md)).

## Demo output shape

From `doc/en/example/xfail_demo.py` run with `pytest -rx xfail_demo.py`: the short summary lists each `XFAIL` with its reason/condition, and the session line reports `7 xfailed`. `test_hello2` (run=False) shows `reason: [NOTRUN]`.

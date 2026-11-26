# Assertions

## Contents

- [The `assert` statement](#the-assert-statement)
- [Assertion rewriting: scope and control](#assertion-rewriting-scope-and-control)
- [Truncation and verbosity](#truncation-and-verbosity)
- [`pytest.approx`](#pytestapprox)
- [`pytest.raises` and `ExceptionInfo`](#pytestraises-and-exceptioninfo)
- [Exception groups: `RaisesGroup`, `RaisesExc`, `group_contains`](#exception-groups-raisesgroup-raisesexc-group_contains)
- [`pytest.warns` and `pytest.deprecated_call`](#pytestwarns-and-pytestdeprecated_call)
- [Imperative helpers](#imperative-helpers)
- [Custom comparison explanations](#custom-comparison-explanations)

## The `assert` statement

Use plain `assert` — pytest rewrites it to include intermediate values in the failure report:

```python
def test_function():
    assert f() == 4, "value was odd, should be even"
    # failure shows: assert 3 == 4  +  where 3 = f()
```

- A message as the second argument is printed alongside the introspection.
- Context-sensitive comparisons give better output: sequences show "At index N diff" (more with `-v`), dicts show which keys differ (9.1: non-`dict` mappings improved; dict diffs keep insertion order), sets show extra items, long strings get a line diff.
- String equality diffs: `ndiff`-style by default; `assertion_text_diff_style = "block"` (9.1) renders `Left:` / `Right:` blocks instead.

## Assertion rewriting: scope and control

pytest rewrites `assert` statements **at import time, only for modules it collects as test modules**. Consequences:

- Asserts in *supporting* modules imported by tests are **not** rewritten (no introspection there). Fix: call `pytest.register_assert_rewrite("module.name")` before the first import — the root `conftest.py` is the standard place.
- Disable rewriting for one module by including the string `PYTEST_DONT_REWRITE` in its docstring.
- Disable globally with `--assert=plain` (or `-p no:assertion`); `--assert=rewrite` is the default.
- Rewritten modules are cached to `.pyc`; set `sys.dont_write_bytecode = True` at the top of a root `conftest.py` to avoid leaving pyc files around (introspection still works; caching is skipped silently on read-only filesystems).

## Truncation and verbosity

- Large assertion outputs are truncated: `truncation_limit_chars` (default 640) and `truncation_limit_lines` (default 8); `0` disables each limit. On CI (detected, see [07-config-running](07-config-running.md#ci-behavior)) truncation is disabled automatically.
- `verbosity_assertions` sets a verbosity level dedicated to assertion output (default `"auto"` follows global `-v`); likewise `verbosity_test_cases` for test-execution output.

## `pytest.approx`

Approximate equality for floats and sequences of floats:

```python
assert (0.1 + 0.2) == pytest.approx(0.3)
assert [1.0, 2.0] == pytest.approx([1.0000001, 2.0])
assert {"a": 0.1 + 0.2} == pytest.approx({"a": 0.3})       # dict values, same keys
assert np.array([1.0, 2.0]) == pytest.approx(np.array([0.999, 2.0]))
```

Semantics:

- Defaults: relative tolerance `rel=1e-6`, absolute `abs=1e-12`; equal if **either** is met. If you specify `abs` without `rel`, the relative tolerance is not considered at all; specifying both means either suffices.
- Infinity equals only itself; NaN equals nothing unless `nan_ok=True`.
- `Decimal` is supported; non-numeric values in dicts/sequences fall back to strict equality (so `None` stays `None` — handy for mixed optional/float data).
- Only ordered sequences (lists/tuples/arrays); sets are not supported.
- **datetime/timedelta (9.1)** — `abs` must be a `timedelta`; `rel` is **not supported for datetimes**, while for timedeltas `rel` is a plain number (fraction of the expected duration):

  ```python
  from datetime import datetime, timedelta
  assert dt_actual == pytest.approx(datetime(2024, 1, 1, 12), abs=timedelta(seconds=1))
  assert delta_actual == pytest.approx(timedelta(minutes=5), rel=0.01)
  ```

- `pytest.approx` in a boolean context raises an `AssertionError` with a hint — it is for `assert x == approx(y)`, not `if approx(y)`.

## `pytest.raises` and `ExceptionInfo`

```python
def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_recursion():
    with pytest.raises(RuntimeError) as excinfo:
        recurse()
    assert "maximum recursion" in str(excinfo.value)
```

- Matches the given type **or any subclass** (like `except`). For the exact type, assert `excinfo.type is RuntimeError`.
- `excinfo` is an `ExceptionInfo`: `.type`, `.value` (the exception), `.traceback`; `.match(pattern)` re-checks the message.
- `match=` — a regex matched with `re.search` against `str(exception)` **and PEP-678 `__notes__`**; escape regex metacharacters in the expected message (`|`, `.`, etc.). 9.0 improved the "match failed" message; 9.1 fixed `|` escaping and suppresses the mismatched exception from the resulting `AssertionError`'s cause chain.
- No exception (or a non-matching one) → "DID NOT RAISE" / "Expected X, but got Y" (9.1: clearer wording).
- The legacy callable form `pytest.raises(Exc, func, *args, **kwargs)` still works but is discouraged.

## Exception groups: `RaisesGroup`, `RaisesExc`, `group_contains`

For `ExceptionGroup` / `BaseExceptionGroup` (PEP 654):

```python
with pytest.RaisesGroup(ValueError):
    raise ExceptionGroup("group msg", [ValueError("value msg")])

with pytest.RaisesGroup(ValueError, TypeError):
    raise ExceptionGroup("msg", [ValueError("foo"), TypeError("bar")])
```

- `pytest.RaisesGroup(Exc1, Exc2, ...)` — the group must contain (at least) those exception types. Structure-strict unlike `except*`:
  - `match=` — regex against the **group** message
  - `check=` — callable receiving the group; must return `True`
  - `flatten_subgroups=True` — accept subgroups at any depth
  - `allow_unwrapped=True` — also accept the bare exception (no group)
- `pytest.RaisesExc(ValueError, match="foo")` — describes one expected member exception with its own `match`; nest inside `RaisesGroup` for detailed expectations.
- Both provide `.matches(exc_or_group)` and `.fail_reason` for matching outside a `with` block (e.g., inspecting `__cause__`/`__context__`).
- `excinfo.group_contains(Exc, match=..., depth=...)` — recursive presence check (default: any nesting level; `depth=1` = direct children only). Caveat: it cannot verify the group contains *no other* exceptions — for full structural expectations use `RaisesGroup`.
- `@pytest.mark.xfail(raises=RaisesGroup(IndexError))` works with xfail too.

## `pytest.warns` and `pytest.deprecated_call`

```python
def test_deprecated():
    with pytest.warns(DeprecationWarning, match="use new API"):
        old_function()
```

- `match=` uses the same `re.search` semantics as `pytest.raises`.
- 9.1: when warnings were emitted but the `match` pattern didn't match, the report says "Regex pattern did not match" (previously the misleading "DID NOT WARN").
- `pytest.deprecated_call([match])` — asserts a `DeprecationWarning` (or `PendingDeprecationWarning`) was emitted; context-manager form preferred.
- The `recwarn` fixture records all warnings of a test for later inspection (`recwarn.list`).

## Imperative helpers

- `pytest.fail(msg)` — fail the current test immediately.
- `pytest.skip(reason)` / `pytest.xfail(reason)` — skip / xfail at runtime (see [04-markers-skip-xfail](04-markers-skip-xfail.md)).
- `pytest.exit(reason, returncode=None)` — exit the whole run with a specific code.
- A test function **returning a value** (instead of asserting) only produces a `PytestReturnNotNoneWarning` — the return value is ignored, so `return f(x) == expected` never fails. Replace `return` with `assert`.

## Custom comparison explanations

Implement `pytest_assertrepr_compare` in a `conftest.py` to render failed `==`/`!=` for your own types:

```python
def pytest_assertrepr_compare(op, left, right):
    if op == "==" and isinstance(left, Foo) and isinstance(right, Foo):
        return [
            "Comparing Foo instances:",
            f"   vals: {left.val} != {right.val}",
        ]
```

Return a list of strings (or `None` to fall back to default rendering).

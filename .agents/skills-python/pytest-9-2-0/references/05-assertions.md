# Assertions

Grounded in `doc/en/how-to/assert.rst`, `doc/en/example/reportingdemo.rst`, and the 9.2.0 changelog.

## `assert` with introspection

Plain `assert` works; pytest rewrites assert statements in **collected test modules** to embed subexpression values in the failure message:

```
>   assert func(3) == 5
E   assert 4 == 5
E    +  where 4 = func(3)
```

- A message (`assert cond, "msg"`) prints alongside the introspection.
- **Rewriting scope** — only test modules discovered by collection are rewritten. For helper modules, call `pytest.register_assert_rewrite("mymod")` *before* importing (root `conftest.py` is a good place).
- **Opt out per module** — put the string `PYTEST_DONT_REWRITE` in the module docstring; globally with `--assert=plain`.
- **Bytecode caching** — rewritten modules are cached to disk (`.pyc`); set `sys.dont_write_bytecode = True` at the top of `conftest.py` to avoid stale `.pyc` files. Since 9.2 the cache is invalidated by source hash (PEP 552), so CI checkouts no longer discard it.

## `pytest.approx` — approximate equality

Works with scalars, lists, dicts, and NumPy arrays; supports NaN comparisons:

```python
assert (0.1 + 0.2) == pytest.approx(0.3)
a = np.array([1.0, 2.0, 3.0])
b = np.array([0.9999, 2.0001, 3.0])
assert a == pytest.approx(b)
```

- `pytest.Approx` is the exposed return type (9.2) for annotations/`isinstance`.
- **9.2:** float tolerances on `Decimal` comparisons emit `PytestApproxDecimalToleranceWarning` when the float can't be represented exactly (tolerance widens to the float's binary value).
- **9.2:** infinite relative tolerance for `timedelta` raises a clear `ValueError` (was `OverflowError`).

## `pytest.raises`

Context-manager form (preferred):

```python
with pytest.raises(ZeroDivisionError):
    1 / 0

with pytest.raises(RuntimeError) as excinfo:
    ...
assert "maximum recursion" in str(excinfo.value)
```

- Matches the exception **type or subclasses**; for the exact type check `excinfo.type is X`.
- `excinfo` is `pytest.ExceptionInfo` with `.type`, `.value`, `.traceback`.
- **`match=`** — `re.search` against `str(exception)`, including PEP 678 `__notes__`; escape regex metacharacters.
- **Legacy form** `pytest.raises(ValueError, func, x=-1)` still works but is rarely used.
- **`xfail` + `raises=`** — `@pytest.mark.xfail(raises=IndexError)` xfails only on that exception (or subclass).

## Exception groups — `RaisesGroup` / `RaisesExc`

For `ExceptionGroup`/`BaseExceptionGroup`:

```python
with pytest.RaisesGroup(ValueError):
    raise ExceptionGroup("group msg", [ValueError("value msg")])
```

- `match=` checks the group message; `check=` takes a callable receiving the group (must return `True`).
- **Strict about structure and unwrapped exceptions** (unlike `except*`): `flatten_subgroups=True` and `allow_unwrapped=True` relax this.
- Nest `pytest.RaisesGroup(pytest.RaisesGroup(ValueError))` for nested groups; `pytest.RaisesExc(ValueError, match="foo")` for contained exceptions.
- `.matches(group)` methods exist for matching outside a context manager (e.g., checking `__context__`/`__cause__`); `RaisesExc.matches` has a `.fail_reason` on failure.
- **`excinfo.group_contains(Exc, match=..., depth=...)`** — checks membership (recursive by default; `depth=1` = top group only). Warning from the docs: it cannot prove the absence of *other* exceptions — prefer `RaisesGroup` for full-structure assertions.

## `pytest.warns`

Assert a warning is emitted (context manager around the code that triggers it). See also `recwarn` fixture for recording warnings and `filterwarnings` marker/config for filtering.

## Context-sensitive comparisons

Rich diff output for failures (demo: `doc/en/example/reportingdemo.rst`, `failure_demo.py`):

- long strings → context diff with `-`/`+` lines (9.2: `Full diff:` includes a legend for the symbols)
- long sequences → first failing index (`At index 100 diff: 1 != 2`)
- dicts → differing items, items on left/right only (9.2: key matching follows the mapping's own key semantics; `dict.items()`/`dict.keys()` comparisons show missing items)
- sets → extra items on each side
- dataclasses/attrs → differing attributes with drill-down
- `in`/`not in` on text → shows the containing context with `+++` markers
- long diffs are capped lazily to the truncation budget (9.2); use `-v`/`-vv` for more detail ("Use -v to get more diff")

## Custom explanation

`pytest_assertrepr_compare(op, left, right)` hook (e.g., in `conftest.py`) returns a list of lines explaining a custom object comparison:

```python
def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, Foo) and isinstance(right, Foo) and op == "==":
        return ["Comparing Foo instances:", f"   vals: {left.val} != {right.val}"]
```

## Returning non-None from tests

`PytestReturnNotNoneWarning` is emitted when a test function returns a value other than `None` — pytest ignores return values; `assert` instead of `return foo() == expected`.

## `pytest.fail`

Raise `Failed` immediately from a test/setup (used in the cache demo as `pytest.fail("bad luck")`).

# Assertions and Exceptions Reference

## Assertion Rewriting

pytest rewrites `assert` statements at import time using an AST transform. This provides rich introspection on failure without boilerplate.

```python
def test_assertion():
    assert 1 + 1 == 2, "Addition should work"  # Custom message shown on failure
```

On failure, pytest shows:
- The failing assertion
- Values of sub-expressions
- Context diffs for strings
- Set/dict differences with extra/missing items
- First failing index for sequences

### Rewriting Scope

Assertion rewriting **only applies to collected test modules** (files matching `test_*.py` or `*_test.py`). Asserts in imported helper modules won't get introspection.

To enable rewriting for a specific module, call before import:

```python
# In conftest.py
import pytest
pytest.register_assert_rewrite("mypackage.test_helpers")
```

### Disabling Rewriting

```bash
pytest --assert=plain    # Disable all assertion rewriting
```

Or add `PYTEST_DONT_REWRITE` to a module's docstring.

## pytest.approx — Approximate Equality

Compare floating-point values with tolerance:

```python
import pytest

def test_floats():
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert [1.0, 2.0] == pytest.approx([0.9999, 2.0001])
```

Works with scalars, lists, dicts, and NumPy arrays. Supports NaN comparison.

### Tolerance Options

```python
pytest.approx(0.3, abs=1e-6)      # Absolute tolerance
pytest.approx(0.3, rel=1e-4)      # Relative tolerance
pytest.approx(expected, nan=True) # Allow NaN == NaN
```

## pytest.raises — Exception Assertions

### Context Manager Form (preferred)

```python
import pytest

def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_with_info():
    with pytest.raises(ValueError) as exc_info:
        int("not_a_number")
    assert "invalid literal" in str(exc_info.value)
```

### Matching Exception Messages

```python
with pytest.raises(ValueError, match=r".*123.*"):
    raise ValueError("Error code 123")
```

The `match` parameter uses `re.search()` against the exception string. It also matches PEP-678 `__notes__`.

### ExceptionInfo Attributes

| Attribute | Description |
|---|---|
| `exc_info.type` | The exception class |
| `exc_info.value` | The exception instance |
| `exc_info.traceback` | The traceback object |
| `str(exc_info.value)` | String representation of the exception |

### Exact Type Check

`pytest.raises` matches subclasses by default (like `except`). For exact type:

```python
with pytest.raises(RuntimeError) as exc_info:
    foo()  # Raises NotImplementedError
assert exc_info.type is RuntimeError  # Fails — it's a subclass
```

## Exception Groups (9.0+)

### pytest.RaisesGroup

```python
import pytest

def test_exception_group():
    with pytest.RaisesGroup(ValueError):
        raise ExceptionGroup("group", [ValueError("v"), TypeError("t")])

# Multiple exception types
with pytest.RaisesGroup(ValueError, TypeError):
    raise ExceptionGroup("", [ValueError(), TypeError()])
```

### RaisesGroup Parameters

```python
# Match group message
with pytest.RaisesGroup(ValueError, match="my group msg"):
    raise ExceptionGroup("my group msg", [ValueError()])

# Custom check callable
with pytest.RaisesGroup(Exception, check=lambda eg: len(eg) == 2):
    raise ExceptionGroup("", [TypeError(), ValueError()])

# Flatten nested groups
with pytest.RaisesGroup(ValueError, flatten_subgroups=True):
    raise ExceptionGroup("outer", [ExceptionGroup("inner", [ValueError()])])

# Allow unwrapped exceptions
with pytest.RaisesGroup(ValueError, allow_unwrapped=True):
    raise ValueError("direct")
```

### pytest.RaisesExc — Detail Matching in Groups

```python
with pytest.RaisesGroup(pytest.RaisesExc(ValueError, match="foo")):
    raise ExceptionGroup("", [ValueError("foo")])
```

### RaisesGroup.matches() — Non-context Usage

```python
from pytest import RaisesGroup, RaisesExc

exc_group = ExceptionGroup("", [ValueError("error")])
if RaisesGroup(ValueError).matches(exc_group):
    ...

# Check fail reason
r = RaisesExc(ValueError)
assert r.matches(e), r.fail_reason
```

### ExceptionInfo.group_contains()

```python
with pytest.raises(ExceptionGroup) as exc_info:
    raise ExceptionGroup("msg", [RuntimeError("123")])

assert exc_info.group_contains(RuntimeError, match=r".*123.*")
assert not exc_info.group_contains(TypeError)
# Depth-specific matching
assert exc_info.group_contains(RuntimeError, depth=1)
```

## pytest.warns — Warning Assertions

```python
import warnings
import pytest

def test_warning():
    with pytest.warns(UserWarning):
        warnings.warn("my warning", UserWarning)

# Match warning message
with pytest.warns(UserWarning, match="must be 0"):
    warnings.warn("value must be 0 or None", UserWarning)

# Record all warnings
with pytest.warns() as record:
    warnings.warn("user", UserWarning)
    warnings.warn("runtime", RuntimeWarning)
assert len(record) == 2
assert str(record[0].message) == "user"
```

### Deprecation Warnings

```python
def test_deprecated():
    with pytest.deprecated_call():
        my_old_function()
```

### recwarn Fixture

```python
def test_warnings(recwarn):
    do_something_that_warns()
    assert len(recwarn) == 1
    warning = recwarn.pop(UserWarning)
    assert str(warning.message) == "expected text"
```

## Custom Assertion Explanations

Implement `pytest_assertrepr_compare` in `conftest.py`:

```python
def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, MyType) and isinstance(right, MyType) and op == "==":
        return [
            "Comparing MyType instances:",
            f"  left.val: {left.val!r}",
            f"  right.val: {right.val!r}",
        ]
```

## Context-Sensitive Comparisons

pytest provides special diff output for:

- **Sets**: Shows extra items in left/right
- **Dicts**: Shows differing entries
- **Long strings**: Context diff format
- **Sequences**: First failing index
- **Dataclasses/NamedTuples**: Field-by-field comparison

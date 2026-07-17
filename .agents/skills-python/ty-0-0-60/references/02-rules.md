# Rules Reference

## Rule levels

- `error` — violation exits with code 1
- `warn` — violation is a warning; exit code depends on `terminal.error-on-warning`
- `ignore` — rule disabled

Set via CLI (`--error`, `--warn`, `--ignore`) or config (`[rules]` section).

## Complete rules list

### Error by default

| Rule | Description |
|------|-------------|
| `abstract-method-in-final-class` | `@final` class with unimplemented abstract methods |
| `assert-type-unspellable-subtype` | `assert_type()` with unspellable subtype |
| `call-abstract-method` | Calling an abstract method |
| `call-non-callable` | Calling a non-callable value |
| `conflicting-declarations` | Conflicting type declarations for the same symbol |
| `conflicting-metaclass` | Incompatible metaclass during inheritance |
| `cyclic-class-definition` | Class definition with a cycle |
| `deprecated` | Use of a deprecated symbol |
| `division-by-zero` | Division by zero detected at type-checking time |
| `duplicate-base` | Duplicate base class in inheritance list |
| `empty-body` | Function/class body is empty (no `pass`, `...`, or statements) |
| `inconsistent-mro` | Method resolution order is inconsistent |
| `index-out-of-bounds` | Index access out of known bounds |
| `invalid-argument-type` | Argument type does not match parameter type |
| `invalid-assignment` | Assignment type is incompatible |
| `invalid-attribute-access` | Attribute access on incompatible type |
| `invalid-await` | Awaiting a non-awaitable |
| `invalid-base` | Invalid base class |
| `invalid-context-manager` | Object used as context manager but doesn't support it |
| `invalid-exception-caught` | Catching a non-exception type |
| `invalid-key` | Invalid key for TypedDict or mapping |
| `invalid-metaclass` | Invalid metaclass |
| `invalid-method-override` | Method override is incompatible with base |
| `invalid-overload` | Overload signature issues |
| `invalid-parameter-default` | Parameter default type is incompatible |
| `invalid-raise` | Raising a non-exception |
| `invalid-return-type` | Return type is incompatible with annotation |
| `invalid-type-arguments` | Invalid type arguments to a generic |
| `invalid-type-form` | Invalid type annotation syntax |
| `missing-argument` | Required argument is missing |
| `missing-override-decorator` | Override method missing `@override` decorator |
| `missing-typed-dict-key` | Missing required TypedDict key |
| `no-matching-overload` | No overload matches the call |
| `not-iterable` | Iterating over a non-iterable |
| `not-subscriptable` | Subscripting a non-subscriptable type |
| `parameter-already-assigned` | Parameter assigned multiple times |
| `redundant-cast` | Unnecessary type cast |
| `too-many-positional-arguments` | Too many positional arguments |
| `type-assertion-failure` | `assert_type()` fails |
| `undefined-reveal` | `reveal_type()` on undefined variable |
| `unknown-argument` | Unknown keyword argument |
| `unresolved-attribute` | Attribute doesn't exist on the type |
| `unresolved-import` | Import cannot be resolved |
| `unresolved-reference` | Reference to an undefined name |
| `unsupported-operator` | Operator not supported for the types |
| `unused-awaitable` | Awaitable result not awaited |

### Warn by default

| Rule | Description |
|------|-------------|
| `ambiguous-protocol-member` | Protocol member with ambiguous declaration |

### Ignore by default

| Rule | Description |
|------|-------------|
| `blanket-ignore-comment` | `ty: ignore` without specific rule codes (added in 0.0.57) |
| `missing-type-argument` | Generic type missing type arguments |
| `possibly-missing-attribute` | Attribute may not exist (on gradual types) |
| `possibly-unresolved-reference` | Reference may be unresolved (on gradual types) |
| `unused-ignore-comment` | Suppression comment with no matching diagnostics |

## Suppression

### Inline suppression

```python
value = unknown  # ty: ignore[unresolved-reference]
value = unknown  # ty: ignore[unresolved-reference, invalid-assignment]
```

### Own-line suppression (0.0.60+)

```python
# ty: ignore[missing-argument]
sum_three_numbers(3, 2)
```

### File-level suppression

Place before any Python code:

```python
# ty: ignore[unresolved-reference]

import some_untyped_module
```

### Standard `type: ignore` format

```python
value = unknown  # type: ignore
value = unknown  # type: ignore[ty:unresolved-reference]
# Mixed checker suppressions:
value = unknown  # type: ignore[arg-type, ty:invalid-argument-type]
```

### `@no_type_check` decorator

```python
from typing import no_type_check

@no_type_check
def main():
    sum_three_numbers(1, 2)  # no error for missing argument
```

Only supported on functions, not classes.

## Rule explanation

```bash
ty explain rule unresolved-import    # Explain a specific rule
ty explain rule                      # List all rules
ty explain rule --output-format json # JSON output
```

## Rules not yet implemented

ty does not yet have equivalents for:
- Exhaustive `match` checking (tracked in [#1060](https://github.com/astral-sh/ty/issues/1060))
- Unreachable code detection (tracked in [#1948](https://github.com/astral-sh/ty/issues/1948))
- Missing type stubs warnings (tracked in [#3638](https://github.com/astral-sh/ty/issues/3638))
- Overlapping overloads (tracked in [#103](https://github.com/astral-sh/ty/issues/103))
- Property type mismatch (tracked in [#3633](https://github.com/astral-sh/ty/issues/3633))

Use Ruff for supplementary checks (ANN rules for missing annotations, PYI rules for stub files).

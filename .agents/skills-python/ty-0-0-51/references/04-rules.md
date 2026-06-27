# Rules and Suppression

## Rule Severities

Each rule has a configurable level:
- **`error`** — Violations cause exit code 1
- **`warn`** — Violations reported but exit code stays 0 (unless `--error-on-warning`)
- **`ignore`** — Rule is disabled

Configure via CLI flags (`--error`, `--warn`, `--ignore`) or config file `[rules]` section.

## Key Rules

### Enabled by default

| Rule | Description |
|------|-------------|
| `call-abstract-method` | Calling an abstract method |
| `call-non-callable` | Calling something not callable |
| `conflicting-declarations` | Redefining a symbol with incompatible types |
| `deprecated` | Using deprecated symbols |
| `division-by-zero` | Literal division by zero |
| `index-out-of-bounds` | Indexing beyond known bounds |
| `invalid-argument-type` | Wrong argument type for a call |
| `invalid-assignment` | Type mismatch in assignment |
| `invalid-attribute-access` | Accessing non-existent attribute |
| `invalid-await` | Awaiting non-awaitable |
| `invalid-base` | Invalid base class |
| `invalid-context-manager` | Using non-context-manager in `with` |
| `invalid-exception-caught` | Catching non-exception type |
| `invalid-key` | Invalid TypedDict key |
| `invalid-method-override` | Method override type mismatch |
| `invalid-overload` | Overload implementation mismatch |
| `invalid-parameter-default` | Default value type mismatch |
| `invalid-raise` | Raising non-exception |
| `invalid-return-type` | Return type mismatch |
| `invalid-type-arguments` | Invalid generic type arguments |
| `invalid-type-form` | Malformed type annotation |
| `missing-argument` | Required argument missing |
| `missing-override-decorator` | Missing `@override` decorator |
| `no-matching-overload` | Call doesn't match any overload |
| `not-iterable` | Iterating over non-iterable |
| `not-subscriptable` | Subscripting non-subscriptable type |
| `parameter-already-assigned` | Duplicate parameter binding |
| `redundant-cast` | Unnecessary `cast()` call |
| `too-many-positional-arguments` | Extra positional arguments |
| `type-assertion-failure` | `assert_type()` mismatch |
| `unresolved-attribute` | Accessing definitely missing attribute |
| `unresolved-import` | Cannot resolve import |
| `unresolved-reference` | Undefined name |
| `unsupported-operator` | Operator not supported for types |
| `unused-awaitable` | Coroutine/awaitable not awaited |
| `unused-ignore-comment` | Suppression comment with no matching diagnostic |

### Disabled by default

| Rule | Description |
|------|-------------|
| `missing-type-argument` | Generic type missing type parameter (e.g., `list` vs `list[int]`) |
| `possibly-missing-attribute` | Attribute might not exist on some union members |
| `possibly-unresolved-reference` | Name might be undefined in some branches |

Enable these for stricter checking:
```toml
[rules]
missing-type-argument = "error"
possibly-unresolved-reference = "warn"
```

## Suppression Comments

### ty-specific suppression

```python
# Single rule
a + "b"  # ty: ignore[unsupported-operator]

# Multiple rules
func("x", 5)  # ty: ignore[invalid-argument-type, missing-argument]

# All rules on a line
result = risky_call()  # ty: ignore

# File-level (before any code)
# ty: ignore[unresolved-import]
```

For multi-line violations, place the comment on the first or last line.

### Standard `type: ignore` support

ty supports PEP 484 `type: ignore` comments by default:

```python
func("x")  # type: ignore           # suppresses all ty errors
func("x")  # type: ignore[ty:invalid-argument-type]  # suppresses specific rule
# Combined with mypy
func("x")  # type: ignore[arg-type, ty:invalid-argument-type]
```

Disable with `respect-type-ignore-comments = false` in config.

### `@no_type_check` decorator

Suppress all violations inside a function:

```python
from typing import no_type_check

@no_type_check
def legacy_code():
    func("x", )  # no errors reported inside this function
```

Note: decorating classes with `@no_type_check` is not supported.

### Multiple suppression comments on one line

```python
result = calculate()  # ty: ignore[invalid-argument-type]  # fmt: skip
```

## Explaining Rules

```bash
ty explain rule unresolved-import   # details for one rule
ty explain rule                     # list all rules
```

# Rules Reference

## Rule levels

- `error` — violation reported as error, ty exits with code 1
- `warn` — violation reported as warning
- `ignore` — rule disabled

Set via CLI: `--error <rule>`, `--warn <rule>`, `--ignore <rule>`.
Set all at once: `--error all`, `--warn all`, `--ignore all`.

## Core type-checking rules

### `call-abstract-method`
Calling an abstract method directly.

### `call-non-callable`
Calling something that is not callable.

### `conflicting-declarations`
Same symbol declared with incompatible types (redeclaration with conflicting type).

### `conflicting-metaclass`
Class inherits from bases with different metaclasses that are not compatible.

### `cyclic-class-definition`
A class definition references itself cyclically in a way that cannot be resolved.

### `deprecated`
Using a deprecated function, class, or attribute.

### `division-by-zero`
Division by a literal zero or statically determined zero value.

### `duplicate-base`
A class lists the same base class multiple times.

### `empty-body`
Function, class, or module with an empty body (no `...` or `pass`).

### `inconsistent-mro`
Method Resolution Order cannot be computed due to conflicting inheritance.

### `index-out-of-bounds`
Indexing a sequence with an out-of-bounds index.

### `invalid-argument-type`
Argument type does not match the expected parameter type.

### `invalid-assignment`
Assigned value type is incompatible with the target type.

### `invalid-attribute-access`
Accessing an attribute that does not exist on the type.

### `invalid-await`
Awaiting something that is not awaitable.

### `invalid-base`
Invalid base class in inheritance (not a class or incompatible).

### `invalid-context-manager`
Using something in a `with` statement that doesn't support context management.

### `invalid-exception-caught`
Catching an exception that is not an Exception subclass.

### `invalid-key`
Using an invalid key type for a TypedDict or mapping.

### `invalid-metaclass`
Invalid metaclass specification.

### `invalid-method-override`
Method override has incompatible signature with parent.

### `invalid-overload`
Overload signatures are inconsistent or the implementation doesn't match.

### `invalid-parameter-default`
Default value type is incompatible with parameter type.

### `invalid-raise`
Raising something that is not an exception.

### `invalid-return-type`
Return value type is incompatible with declared return type.

### `invalid-type-arguments`
Invalid type arguments to a generic type.

### `invalid-type-form`
Malformed type annotation (e.g., `list` without brackets used incorrectly).

### `missing-argument`
Required argument not provided in a call.

### `missing-override-decorator`
Method overrides a parent but lacks `@override` decorator (Python 3.12+).

### `missing-type-argument`
Generic type used without type arguments (e.g., `list` instead of `list[int]`).
Disabled by default.

### `missing-typed-dict-key`
Missing required key in TypedDict construction.

### `no-matching-overload`
No overload variant matches the call arguments.

### `not-iterable`
Iterating over something that is not iterable.

### `not-subscriptable`
Subscripting something that doesn't support `__getitem__`.

### `parameter-already-assigned`
Parameter assigned a value more than once.

### `possibly-missing-attribute`
Attribute may not exist (on Optional or union types).
Disabled by default.

### `possibly-missing-import`
Import may not be available in all environments.

### `possibly-unresolved-reference`
Reference may not be resolved in all code paths.
Disabled by default.

### `redundant-cast`
Unnecessary type cast.

### `too-many-positional-arguments`
Too many positional arguments provided.

### `type-assertion-failure`
`assert_type()` check will fail at runtime.

### `undefined-reveal`
`reveal_type()` used without importing it.

### `unknown-argument`
Unknown keyword argument provided.

### `unresolved-attribute`
Attribute access on a type that does not have it.

### `unresolved-import`
Import cannot be resolved (module not found).

### `unresolved-reference`
Reference to an undefined name.

### `unsupported-operator`
Operator not supported for the operand types.

### `unused-awaitable`
Awaitable result not awaited (coroutine/async generator).

### `unused-ignore-comment`
`ty: ignore` or `type: ignore` comment with no matching violation.

### `blanket-ignore-comment`
`type: ignore` without specific error codes.
Disabled by default.

## Configuration

```toml
[rules]
all = "warn"                          # Set default for all rules
missing-type-argument = "error"       # Override specific rule
redundant-cast = "ignore"             # Disable specific rule
possibly-unresolved-reference = "warn"
```

## CLI

```bash
ty check --error all                              # All rules as errors
ty check --error invalid-assignment --warn missing-type-argument
ty check --ignore redundant-cast,unused-ignore-comment
ty check --add-ignore                             # Auto-add suppression comments
```

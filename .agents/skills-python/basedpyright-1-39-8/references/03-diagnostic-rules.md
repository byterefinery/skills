# Diagnostic Rules Reference

Diagnostic rules control which type issues are reported. Each rule can be set to `"error"`, `"warning"`, `"information"`, `"hint"`, or `"none"`. Boolean values (`true`/`false`) are aliases for `"error"`/`"none"`.

## Type Checking Modes

| Mode | Description |
|------|-------------|
| `"off"` | All diagnostic rules disabled. Syntax/semantic errors still reported. (basedpyright treats this as truly off) |
| `"basic"` | Minimal type checking |
| `"standard"` | Moderate type checking |
| `"strict"` | Most rules enabled as errors |
| `"recommended"` | **Default in basedpyright**. All rules enabled as warnings or errors. `failOnWarnings: true` |
| `"all"` | All rules enabled as errors |

## Core Type Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportGeneralTypeIssues` | error | General type inconsistencies, unsupported operations, argument/parameter mismatches |
| `reportPropertyTypeMismatch` | error | Setter type not assignable to getter return type |
| `reportFunctionMemberAccess` | error | Non-standard member access on functions |
| `reportInvalidTypeForm` | error | Invalid type annotation expressions |
| `reportInvalidTypeArguments` | error | Invalid type argument usage |

## Import Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportMissingImports` | warning | Import has no corresponding file or stub |
| `reportMissingModuleSource` | warning | Stub found but no source file (may fail at runtime) |
| `reportMissingTypeStubs` | warning | Import has no type stub |
| `reportImportCycles` | warning | Cyclical import chains |
| `reportUnusedImport` | warning | Imported symbol not referenced in the file |
| `reportDuplicateImport` | warning | Symbol imported more than once |
| `reportWildcardImportFromLibrary` | error | Wildcard import from external library (`from x import *`) |
| `reportPrivateImportUsage` | warning | Use of private symbol from third-party `py.typed` module |

### basedpyright-exclusive import rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportPrivateLocalImportUsage` | warning | Like `reportPrivateImportUsage` but for your own code. Re-export with `from .mod import x as x` |
| `reportImplicitRelativeImport` | warning | Non-relative import that doesn't specify full module path (works as script, breaks as module) |

## Assignment and Return Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportArgumentType` | error | Argument type incompatibility in call expressions |
| `reportAssertTypeFailure` | error | Type mismatch in `typing.assert_type` |
| `reportAssignmentType` | error | Assignment type incompatibility |
| `reportCallIssue` | error | Issues with call expressions and arguments |
| `reportIndexIssue` | error | Issues with index/subscript operations |
| `reportOperatorIssue` | error | Issues with unary/binary operators |
| `reportReturnType` | error | Function return type incompatibility |

## Optional Type Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportOptionalSubscript` | error | Subscript on `Optional` type |
| `reportOptionalMemberAccess` | error | Member access on `Optional` type |
| `reportOptionalCall` | error | Call on `Optional` type |
| `reportOptionalIterable` | error | Use `Optional` as iterable (e.g., in `for`) |
| `reportOptionalContextManager` | error | Use `Optional` as context manager |
| `reportOptionalOperand` | error | Use `Optional` as operator operand |

## Overload Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportInconsistentOverload` | error | Overload signatures inconsistent with each other or implementation |
| `reportNoOverloadImplementation` | error | Overloaded function without implementation |
| `reportOverlappingOverload` | error | Overloads that overlap and obscure each other |

## Class and Inheritance Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportAbstractUsage` | error | Instantiating abstract class or using unimplemented abstract method |
| `reportIncompatibleMethodOverride` | error | Method override with incompatible signature |
| `reportIncompatibleVariableOverride` | error | Class variable override with incompatible type |
| `reportInconsistentConstructor` | warning | `__init__` signature inconsistent with `__new__` |
| `reportMissingSuperCall` | warning | `__init__`, `__enter__`, etc. missing `super()` call |
| `reportUninitializedInstanceVariable` | warning | Instance variable not initialized in class body or `__init__` |

### basedpyright-exclusive class rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUnsafeMultipleInheritance` | warning | Multiple base classes with `__init__`/`__new__` — constructors may not be called correctly |
| `reportImplicitAbstractClass` | warning | Class extends ABC without explicitly declaring itself abstract or implementing all methods |
| `reportEmptyAbstractUsage` | warning | Instantiating a class that extends `ABC` but has no abstract methods |
| `reportIncompatibleUnannotatedOverride` | warning | Override with incompatible type when base class attribute lacks annotation |
| `reportUnannotatedClassAttribute` | warning | Class attribute without type annotation (can be overridden unsafely) |
| `reportInvalidAbstractMethod` | warning | `@abstractmethod` on a non-abstract class (doesn't raise at runtime) |

## Unknown/Any Type Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUnknownParameterType` | warning | Function parameter with unknown type |
| `reportUnknownArgumentType` | warning | Call argument with unknown type |
| `reportUnknownLambdaType` | warning | Lambda parameter/return with unknown type |
| `reportUnknownVariableType` | warning | Variable with unknown type |
| `reportUnknownMemberType` | warning | Class/instance variable with unknown type |
| `reportMissingParameterType` | warning | Function parameter missing type annotation (`self`/`cls` exempt) |
| `reportMissingTypeArgument` | warning | Generic class used without type arguments |

### basedpyright-exclusive Any rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportAny` | warning | **Catches all `Any` usage** — expressions typed as `Any`, including explicit `Any` that older rules miss |
| `reportExplicitAny` | warning | Ban direct use of the `Any` type in annotations |

## Untyped Decorator/Base Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUntypedFunctionDecorator` | warning | Function decorator without type annotations (obscures function type) |
| `reportUntypedClassDecorator` | warning | Class decorator without type annotations |
| `reportUntypedBaseClass` | warning | Base class whose type cannot be determined statically |
| `reportUntypedNamedTuple` | warning | Uses `namedtuple()` instead of `NamedTuple` (no type info) |

## Code Quality Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUnusedClass` | warning | Private class (`_name`) not accessed |
| `reportUnusedFunction` | warning | Private function/method not accessed |
| `reportUnusedVariable` | warning | Variable not accessed |
| `reportUnusedCallResult` | hint | Call result not used and not `None` |
| `reportUnusedCoroutine` | error | Coroutine result not used (missing `await`) |
| `reportUnusedExcept` | error | Unreachable `except` clause |
| `reportUnusedExpression` | warning | Expression result not used |
| `reportConstantRedefinition` | warning | Redefining ALL_CAPS variable |
| `reportDeprecated` | hint | Use of deprecated class/function |
| `reportRedeclaration` | warning | Symbol redeclared with same or different type |

### basedpyright-exclusive code quality rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUnusedParameter` | hint | Unused function parameter (pyright only greys it out; this makes it configurable) |

## Pattern Matching Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportMatchNotExhaustive` | warning | `match` statement doesn't cover all types |

## Reachability Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUnreachable` | hint | Structurally unreachable code or unreachable by type analysis |

## Type Guard Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportInvalidTypeVarUse` | error | TypeVar used inappropriately (e.g., appears only once) |
| `reportPossiblyUnboundVariable` | error | Variable possibly unbound on some code paths |

## Naming and Style Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportSelfClsParameterName` | warning | Missing or misnamed `self`/`cls` parameter |
| `reportPrivateUsage` | warning | Accessing private/protected variables or functions |
| `reportImplicitStringConcatenation` | warning | Implicit string concatenation (adjacent string literals) |
| `reportInvalidStringEscapeSequence` | warning | Invalid escape sequences in strings |

### basedpyright-exclusive naming rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportSelfClsDefault` | warning | Default value on `self` or `cls` parameter (almost certainly a mistake) |

## Ignore Comment Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUnnecessaryTypeIgnoreComment` | warning | `# type: ignore` or `# pyright: ignore` that has no effect |

### basedpyright-exclusive ignore rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportIgnoreCommentWithoutRule` | warning | `# pyright: ignore` or `# type: ignore` without specifying a rule in brackets |

## Cast Rules

### basedpyright-exclusive cast rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportInvalidCast` | warning | `cast()` to non-overlapping type (e.g., `cast(str, int_value)`) |

## TypedDict Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportTypedDictNotRequiredAccess` | error | Accessing non-required TypedDict field without checking presence |

## Stub File Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportInvalidStubStatement` | error | Syntactically correct but meaningless statement in `.pyi` file |
| `reportIncompleteStub` | warning | Module-level `__getattr__` in stub (indicates incomplete stub) |
| `reportUnsupportedDunderAll` | warning | `__all__` manipulation not supported by static type checkers |

## Default Initializer Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportCallInDefaultInitializer` | warning | Function call, list/set/dict expression in default parameter (expensive at module init time) |

## Unnecessary Check Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUnnecessaryIsInstance` | warning | `isinstance`/`issubclass` always true or false |
| `reportUnnecessaryCast` | warning | `cast()` statically determined unnecessary |
| `reportUnnecessaryComparison` | warning | Comparison always true/false (including unreachable `match` cases) |
| `reportUnnecessaryContains` | warning | `in` operation always true/false |
| `reportAssertAlwaysTrue` | error | `assert (v > 0, "msg")` — parenthesized tuple instead of condition |

## Type Comment Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportTypeCommentUsage` | warning | Use of deprecated type comments (Python 3.5+ supports inline annotations) |

## Hashability Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportUnhashable` | error | Using unhashable object in hash-requiring container |

## Override Rules

| Rule | Default (recommended) | Description |
|------|----------------------|-------------|
| `reportImplicitOverride` | warning | Overridden method missing `@override` decorator |

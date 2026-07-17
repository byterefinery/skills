# Diagnostic Rules Reference

## Type Check Modes

| Mode | Description |
|------|-------------|
| `"off"` | All diagnostic rules disabled. Python syntax/semantic errors still reported. |
| `"basic"` | Minimal type checking. Close to pyright's original defaults. |
| `"standard"` | Moderate type checking. |
| `"strict"` | Most rules enabled as errors. |
| `"recommended"` | All rules enabled. Likely runtime issues as errors, others as warnings. `failOnWarnings` true. |
| `"all"` | All rules as errors. |

basedpyright defaults to `"recommended"`.

## Severity Levels

| Level | CLI behavior | Language server |
|-------|-------------|-----------------|
| `"error"` | Exit code 1 | Red squiggly |
| `"warning"` | Exit code 1 if `failOnWarnings` | Yellow squiggly |
| `"information"` | No effect | Blue info |
| `"hint"` | No effect | Greyed out / strikethrough |
| `"none"` | Disabled | Hidden |

Deprecated aliases: `"unreachable"`, `"unused"`, `"deprecated"` → all map to `"hint"`.

## Standard Rules (from pyright)

### General type issues

- **`reportGeneralTypeIssues`** — General type inconsistencies, unsupported operations, argument/parameter mismatches
- **`reportPropertyTypeMismatch`** — Setter type not assignable to getter return type
- **`reportFunctionMemberAccess`** — Non-standard member access on functions
- **`reportMissingImports`** — Imports with no corresponding file or stub
- **`reportMissingModuleSource`** — Stub found but no source (may fail at runtime)
- **`reportInvalidTypeForm`** — Invalid type annotation expressions
- **`reportMissingTypeStubs`** — Imports without type stubs (no typeshed, no `py.typed`)
- **`reportImportCycles`** — Cyclical import chains

### Unused / duplicate

- **`reportUnusedImport`** — Imported symbol not referenced
- **`reportUnusedClass`** — Private class not accessed
- **`reportUnusedFunction`** — Private function/method not accessed
- **`reportUnusedVariable`** — Variable not accessed
- **`reportDuplicateImport`** — Symbol imported more than once
- **`reportWildcardImportFromLibrary`** — Wildcard import from external library

### Abstract usage

- **`reportAbstractUsage`** — Instantiating abstract class or calling abstract method

### Argument / assignment / call

- **`reportArgumentType`** — Argument type incompatibility in calls
- **`reportAssertTypeFailure`** — `typing.assert_type` mismatch
- **`reportAssignmentType`** — Assignment type incompatibility
- **`reportAttributeAccessIssue`** — Attribute access issues
- **`reportCallIssue`** — Call expression issues
- **`reportInconsistentOverload`** — Overload signatures inconsistent with each other or implementation
- **`reportIndexIssue`** — Index operation issues
- **`reportInvalidTypeArguments`** — Invalid type argument usage
- **`reportNoOverloadImplementation`** — Overloaded function without implementation
- **`reportOperatorIssue`** — Unary/binary operator issues

### Optional handling

- **`reportOptionalSubscript`** — Subscripting an Optional type
- **`reportOptionalMemberAccess`** — Member access on Optional type
- **`reportOptionalCall`** — Calling an Optional type
- **`reportOptionalIterable`** — Using Optional as iterable (e.g., `for` loop)
- **`reportOptionalContextManager`** — Using Optional as context manager (`with`)
- **`reportOptionalOperand`** — Using Optional as operand in expression

### Redefinition / return type

- **`reportRedeclaration`** — Symbol with multiple type declarations
- **`reportReturnType`** — Return type compatibility issues

### TypedDict / decorators / base classes

- **`reportTypedDictNotRequiredAccess`** — Accessing non-required TypedDict field without check
- **`reportUntypedFunctionDecorator`** — Function decorator without type annotations
- **`reportUntypedClassDecorator`** — Class decorator without type annotations
- **`reportUntypedBaseClass`** — Base class type cannot be determined statically
- **`reportUntypedNamedTuple`** — Using `namedtuple` instead of `NamedTuple`

### Private / type comments

- **`reportPrivateUsage`** — Incorrect usage of private/protected members
- **`reportTypeCommentUsage`** — Using deprecated type comments
- **`reportPrivateImportUsage`** — Using non-exported symbol from third-party `py.typed` module
- **`reportConstantRedefinition`** — Redefining ALL_CAPS variables

### Deprecated / override / inheritance

- **`reportDeprecated`** — Using deprecated class or function
- **`reportIncompatibleMethodOverride`** — Method override with incompatible signature
- **`reportIncompatibleVariableOverride`** — Variable override with incompatible type
- **`reportInconsistentConstructor`** — `__init__` inconsistent with `__new__`
- **`reportOverlappingOverload`** — Overloads that obscure each other
- **`reportPossiblyUnboundVariable`** — Variable possibly unbound on some paths
- **`reportMissingSuperCall`** — Missing `super()` call in `__init__`, `__init_subclass__`, etc.
- **`reportUninitializedInstanceVariable`** — Instance variable not initialized in class body or `__init__`

### Code quality

- **`reportInvalidStringEscapeSequence`** — Invalid escape sequences in strings
- **`reportUnknownParameterType`** — Parameter with unknown type
- **`reportUnknownArgumentType`** — Call argument with unknown type
- **`reportUnknownLambdaType`** — Lambda parameter/return with unknown type
- **`reportUnknownVariableType`** — Variable with unknown type
- **`reportUnknownMemberType`** — Class/instance variable with unknown type
- **`reportMissingParameterType`** — Parameter missing type annotation
- **`reportMissingTypeArgument`** — Generic class without type arguments
- **`reportInvalidTypeVarUse`** — TypeVar used inappropriately (e.g., appears only once)
- **`reportCallInDefaultInitializer`** — Function call in default value expression

### Unnecessary checks

- **`reportUnnecessaryIsInstance`** — `isinstance`/`issubclass` always true/false
- **`reportUnnecessaryCast`** — `cast` call statically unnecessary
- **`reportUnnecessaryComparison`** — Comparison always true/false
- **`reportUnnecessaryContains`** — `in` operation always true/false
- **`reportAssertAlwaysTrue`** — `assert` with parenthesized tuple (common mistake)

### Naming / style

- **`reportSelfClsParameterName`** — Missing or misnamed `self`/`cls`
- **`reportImplicitStringConcatenation`** — Implicit string concatenation

### Undefined / unbound / hashable

- **`reportUndefinedVariable`** — Undefined variable
- **`reportUnboundVariable`** — Unbound variable
- **`reportUnhashable`** — Unhashable object in hash-requiring container

### Stub files

- **`reportInvalidStubStatement`** — Statement with no purpose in `.pyi` file
- **`reportIncompleteStub`** — Module-level `__getattr__` in stub (incomplete)
- **`reportUnsupportedDunderAll`** — `__all__` manipulated in unsupported way

### Unused results

- **`reportUnusedCallResult`** — Call result not used (and not None)
- **`reportUnusedCoroutine`** — Coroutine result not used (missing `await`)
- **`reportUnusedExcept`** — `except` clause never reached
- **`reportUnusedExpression`** — Expression result not used

### Type ignore / match

- **`reportUnnecessaryTypeIgnoreComment`** — Unnecessary `# type: ignore` / `# pyright: ignore`
- **`reportMatchNotExhaustive`** — `match` not covering all types
- **`reportUnreachable`** — Structurally unreachable or type-unreachable code
- **`reportImplicitOverride`** — Override missing `@override` decorator

## basedpyright-exclusive Rules

### Any type enforcement

- **`reportAny`** — Reports all expressions typed as `Any`, including implicit ones.
  Catches what `reportUnknown*` rules miss (explicit `Any`, `Any` from typed code).

- **`reportExplicitAny`** — Bans direct use of `Any` type in annotations.
  Use with `reportAny` for a complete `Any` ban.

### Ignore comment safety

- **`reportIgnoreCommentWithoutRule`** — Enforces `# pyright: ignore[rule]` with specific
  rule codes. Prevents blanket suppression that hides new errors.

### Import enforcement

- **`reportPrivateLocalImportUsage`** — Like `reportPrivateImportUsage` but for your own
  code. Enforces explicit re-exports via `from .x import y as y`.

- **`reportImplicitRelativeImport`** — Bans `import sibling` within packages.
  Requires `from . import sibling` or full absolute path.

### Cast safety

- **`reportInvalidCast`** — Flags `cast()` to non-overlapping types.
  Note: casting `dict` to `TypedDict` triggers this (they don't overlap in type system).

### Inheritance safety

- **`reportUnsafeMultipleInheritance`** — Bans multiple inheritance when base classes
  have `__init__`/`__new__` methods. Prevents unsafe MRO constructor chains.

### Parameter / abstract class checks

- **`reportUnusedParameter`** — Unused function parameters (supports all severity levels,
  unlike pyright which only greys them out).

- **`reportImplicitAbstractClass`** — Subclasses of `ABC` must also extend `ABC` to remain
  abstract. Prevents accidental concrete classes.

- **`reportEmptyAbstractUsage`** — Instantiating a class that extends `ABC` but has no
  abstract methods. Likely unintentional.

- **`reportInvalidAbstractMethod`** — `@abstractmethod` on a non-abstract class (not
  extending `ABC`). The method would not raise at runtime.

### Override / attribute checks

- **`reportIncompatibleUnannotatedOverride`** — Variable override with incompatible type
  when base class has no annotation. Disabled in `"recommended"` due to performance concerns.

- **`reportUnannotatedClassAttribute`** — Class attributes without type annotations.
  Use as alternative to `reportIncompatibleUnannotatedOverride` if performance is a concern.

### Self/cls defaults

- **`reportSelfClsDefault`** — Default value on `self` or `cls` parameter. Almost always
  a mistake.

## Type Evaluation Settings

- **`strictListInference`** — Infer `list[int | str | float]` instead of `list[Any]`
- **`strictDictionaryInference`** — Infer `dict[str, int | str]` instead of `dict[str, Any]`
- **`strictSetInference`** — Infer `set[int | str | float]` instead of `set[Any]`
- **`analyzeUnannotatedFunctions`** — Analyze functions without type annotations
- **`strictParameterNoneValue`** — Require explicit `Optional` when parameter defaults to `None`
- **`deprecateTypingAliases`** — Deprecate `typing.List` in favor of `list` (Python 3.9+)
- **`enableExperimentalFeatures`** — Enable experimental typing features
- **`disableBytesTypePromotions`** — Don't treat `bytearray`/`memoryview` as `bytes` subtypes

### basedpyright-exclusive evaluation settings

- **`strictGenericNarrowing`** — Narrow generics to bound/constraint instead of `Any`
  on `isinstance` checks
- **`enableBasedFeatures`** — Enable extra `dataclass_transform` features

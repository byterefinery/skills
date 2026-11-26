# Diagnostic rules

## Contents

- [Type checking modes](#type-checking-modes)
- [Default severities](#default-severities)
- [BasedPyright-exclusive rules](#basedpyright-exclusive-rules)
- [Diagnostic categories](#diagnostic-categories)
- [Overriding rules](#overriding-rules)

## Type checking modes

`typeCheckingMode` selects the default rule set. The default is `"recommended"`.

| Mode | Meaning |
|---|---|
| `off` | All type-checking rules disabled — literally off in basedpyright, unlike pyright which still reports some rules as warnings. Python syntax and semantic errors are still reported |
| `basic` | Pyright's basic subset |
| `standard` | Pyright's default subset |
| `strict` | Pyright's strict subset |
| `recommended` | BasedPyright default — every rule enabled as `"error"` or `"warning"`, plus `failOnWarnings`, `strictGenericNarrowing`, and `deprecateTypingAliases` |
| `all` | Same as `recommended` but every rule is `"error"` (and `reportIncompatibleUnannotatedOverride` is enabled) |

`"recommended"` is essentially as strict as `"all"`; it only distinguishes errors that
are likely to cause a runtime crash (e.g. an undefined variable) from less serious
warnings (e.g. a missing type annotation), while `failOnWarnings` keeps the exit code
non-zero for both. The four pyright modes are the only ones where the basedpyright
rules are off and `enableTypeIgnoreComments` is back on.

## Default severities

Default severity of every setting in each mode, per the official docs:

| Setting | off | basic | standard | strict | recommended | all |
|---|---|---|---|---|---|---|
| strictListInference | false | false | false | true | true | true |
| strictSetInference | false | false | false | true | true | true |
| strictDictionaryInference | false | false | false | true | true | true |
| analyzeUnannotatedFunctions | true | true | true | true | true | true |
| strictParameterNoneValue | false | true | true | true | true | true |
| enableBasedFeatures | false | false | false | false | false | false |
| enableExperimentalFeatures | false | false | false | false | false | false |
| deprecateTypingAliases | false | false | false | false | true | true |
| disableBytesTypePromotions | true | true | true | true | true | true |
| strictGenericNarrowing | false | false | false | false | true | true |
| enableTypeIgnoreComments | true | true | true | true | false | false |
| enableReachabilityAnalysis | false | true | true | true | true | true |
| failOnWarnings | false | false | false | false | true | true |
| reportGeneralTypeIssues | none | error | error | error | error | error |
| reportPropertyTypeMismatch | none | none | none | none | warning | error |
| reportFunctionMemberAccess | none | none | error | error | error | error |
| reportMissingImports | none | error | error | error | error | error |
| reportMissingModuleSource | none | warning | warning | warning | error | error |
| reportInvalidTypeForm | none | error | error | error | error | error |
| reportMissingTypeStubs | none | none | none | error | warning | error |
| reportImportCycles | none | none | none | none | error | error |
| reportUnusedImport | hint | hint | hint | error | warning | error |
| reportUnusedClass | hint | hint | hint | error | warning | error |
| reportUnusedFunction | hint | hint | hint | error | warning | error |
| reportUnusedVariable | hint | hint | hint | error | warning | error |
| reportDuplicateImport | none | none | none | error | warning | error |
| reportWildcardImportFromLibrary | none | warning | warning | error | warning | error |
| reportAbstractUsage | none | error | error | error | error | error |
| reportEmptyAbstractUsage | none | none | none | none | warning | error |
| reportArgumentType | none | error | error | error | error | error |
| reportAssertTypeFailure | none | error | error | error | error | error |
| reportAssignmentType | none | error | error | error | error | error |
| reportAttributeAccessIssue | none | error | error | error | error | error |
| reportCallIssue | none | error | error | error | error | error |
| reportInconsistentOverload | none | error | error | error | error | error |
| reportIndexIssue | none | error | error | error | error | error |
| reportInvalidTypeArguments | none | error | error | error | error | error |
| reportNoOverloadImplementation | none | error | error | error | error | error |
| reportOperatorIssue | none | error | error | error | error | error |
| reportOptionalSubscript | none | error | error | error | error | error |
| reportOptionalMemberAccess | none | error | error | error | error | error |
| reportOptionalCall | none | error | error | error | error | error |
| reportOptionalIterable | none | error | error | error | error | error |
| reportOptionalContextManager | none | error | error | error | error | error |
| reportOptionalOperand | none | error | error | error | error | error |
| reportRedeclaration | none | error | error | error | warning | error |
| reportReturnType | none | error | error | error | error | error |
| reportTypedDictNotRequiredAccess | none | error | error | error | error | error |
| reportUntypedFunctionDecorator | none | none | none | error | warning | error |
| reportUntypedClassDecorator | none | none | none | error | warning | error |
| reportUntypedBaseClass | none | none | none | error | warning | error |
| reportUntypedNamedTuple | none | none | none | error | warning | error |
| reportPrivateUsage | none | none | none | error | warning | error |
| reportTypeCommentUsage | hint | hint | hint | error | warning | error |
| reportPrivateImportUsage | none | error | error | error | warning | error |
| reportConstantRedefinition | none | none | none | error | error | error |
| reportDeprecated | hint | hint | hint | error | warning | error |
| reportIncompatibleMethodOverride | none | none | error | error | error | error |
| reportIncompatibleVariableOverride | none | none | error | error | error | error |
| reportInconsistentConstructor | none | none | none | error | error | error |
| reportOverlappingOverload | none | none | error | error | error | error |
| reportPossiblyUnboundVariable | none | none | error | error | error | error |
| reportMissingSuperCall | none | none | none | none | error | error |
| reportUninitializedInstanceVariable | none | none | none | none | error | error |
| reportInvalidStringEscapeSequence | none | warning | warning | error | error | error |
| reportUnknownParameterType | none | none | none | error | warning | error |
| reportUnknownArgumentType | none | none | none | error | warning | error |
| reportUnknownLambdaType | none | none | none | error | warning | error |
| reportUnknownVariableType | none | none | none | error | warning | error |
| reportUnknownMemberType | none | none | none | error | warning | error |
| reportMissingParameterType | none | none | none | error | warning | error |
| reportMissingTypeArgument | none | none | none | error | error | error |
| reportInvalidTypeVarUse | none | warning | warning | error | warning | error |
| reportCallInDefaultInitializer | none | none | none | none | warning | error |
| reportUnnecessaryIsInstance | none | none | none | error | warning | error |
| reportUnnecessaryCast | none | none | none | error | warning | error |
| reportUnnecessaryComparison | none | none | none | error | warning | error |
| reportUnnecessaryContains | none | none | none | error | warning | error |
| reportAssertAlwaysTrue | none | warning | warning | error | error | error |
| reportSelfClsParameterName | none | warning | warning | error | error | error |
| reportImplicitStringConcatenation | none | none | none | none | warning | error |
| reportUndefinedVariable | none | error | error | error | error | error |
| reportUnhashable | none | error | error | error | error | error |
| reportUnboundVariable | none | error | error | error | error | error |
| reportInvalidStubStatement | none | none | none | error | warning | error |
| reportIncompleteStub | none | none | none | error | warning | error |
| reportUnsupportedDunderAll | none | warning | warning | error | warning | error |
| reportUnusedCallResult | none | none | none | none | warning | error |
| reportUnusedCoroutine | none | error | error | error | warning | error |
| reportUnusedExcept | hint | error | error | error | error | error |
| reportUnusedExpression | none | warning | warning | error | warning | error |
| reportUnnecessaryTypeIgnoreComment | none | none | none | none | warning | error |
| reportMatchNotExhaustive | none | none | none | error | warning | error |
| reportUnreachable | hint | hint | hint | hint | warning | error |
| reportImplicitOverride | none | none | none | none | warning | error |
| reportAny | none | none | none | none | warning | error |
| reportExplicitAny | none | none | none | none | warning | error |
| reportIgnoreCommentWithoutRule | none | none | none | none | warning | error |
| reportInvalidCast | none | none | none | none | error | error |
| reportImplicitRelativeImport | none | none | none | none | error | error |
| reportPrivateLocalImportUsage | none | none | none | none | warning | error |
| reportUnsafeMultipleInheritance | none | none | none | none | error | error |
| reportUnusedParameter | hint | hint | hint | hint | warning | error |
| reportImplicitAbstractClass | none | none | none | none | error | error |
| reportUnannotatedClassAttribute | none | none | none | none | warning | error |
| reportIncompatibleUnannotatedOverride | none | none | none | none | none | error |
| reportInvalidAbstractMethod | none | none | none | none | warning | error |
| reportSelfClsDefault | none | none | none | none | warning | error |

Rows `reportAny` through `reportSelfClsDefault` are the basedpyright-exclusive rules.

## BasedPyright-exclusive rules

### `reportAny`

Pyright's `reportUnknown*` rules only catch "Unknown" (a distinction for `Any` that
comes from untyped code), not `Any` in general. `reportAny` reports usages of anything
typed as `Any`:

```python
def foo(bar, baz: Any) -> Any:
    print(bar)  # pyright: unknown type
    print(baz)  # basedpyright: reportAny
```

### `reportExplicitAny`

Bans usages of the `Any` type itself (e.g. in annotations), complementing `reportAny`
which bans expressions typed as `Any`:

```python
def foo(baz: Any) -> Any:  # reportExplicitAny
    print(baz)             # reportAny
```

### `reportIgnoreCommentWithoutRule`

Enforces that every `# type: ignore` / `# pyright: ignore` comment specifies a rule in
brackets (e.g. `# pyright: ignore[reportUnreachable]`). With a bracketed rule, if the
error changes or a new error appears on the same line, the comment no longer covers it
and the new error is reported.

### `reportPrivateLocalImportUsage`

Like pyright's `reportPrivateImportUsage`, but also for imports from your own code.
To re-export a name, give it a redundant alias (as in PEP 484 stub files):

```python
# foo.py
from .some_module import a        # private
from .some_module import b as b   # explicit re-export

# bar.py
from foo import a  # reportPrivateLocalImportUsage error
from foo import b  # fine
```

### `reportImplicitRelativeImport`

Bans non-relative imports that do not specify the full module path. Inside a package,
`import foo` (instead of `import pkg.foo` or `from pkg import foo`) works when the file
is run as a script but crashes with `ModuleNotFoundError` when it is imported as a
module. For a sibling module inside a package use `from . import foo`.

### `reportInvalidCast`

Reports `cast()` to a type that does not overlap with the original type:

```python
foo: int
cast(str, foo)  # reportInvalidCast — int and str do not overlap
```

Caveat — casting a plain `dict` to a `TypedDict` is a common use case but errors under
this rule, because checkers treat `TypedDict` as a subtype of `Mapping` that does not
overlap with `dict`. Build the `TypedDict` explicitly or disable the rule.

### `reportUnsafeMultipleInheritance`

Bans multiple inheritance when multiple base classes have an `__init__` or `__new__`
method, since MRO super-calls can then reach a constructor with the wrong (or no)
arguments. This allows `reportMissingSuperCall` to be less noisy — with it enabled,
missing `super()` calls are only reported on classes that actually have a base class.

### `reportUnusedParameter`

Pyright only greys out unused function parameters (hint). This rule reports them with a
real severity:

```python
def print_value(value: str):  # reportUnusedParameter
    print("something else")
```

### `reportImplicitAbstractClass`

A class that extends an abstract class is implicitly abstract even if it does not
implement all abstract methods — pyright assumes you intend that. This rule bans
implicit abstraction: to keep a subclass abstract you must explicitly extend `ABC` as
well, signaling intent:

```python
class FooImpl(AbstractFoo):       # error — implicitly abstract
class FooImpl(AbstractFoo, ABC):  # OK, explicitly abstract
```

### `reportEmptyAbstractUsage`

Flags instantiation of a class that directly extends `ABC` (or uses `ABCMeta`) but has
no abstract methods — likely an accident. Subclasses are not affected, since they may
be intentionally concrete.

### `reportIncompatibleUnannotatedOverride`

Catches class attribute overrides with an incompatible type when the base class'
attribute has **no** type annotation (pyright's `reportIncompatibleVariableOverride`
misses this case):

```python
class A:
    value = 1      # inferred as int

class B(A):
    value = None   # error with this rule
```

Disabled by default even in `recommended` (enabled in `all`) pending performance
confidence; the project intends to enable it by default. If it is slow, disable it and
use `reportUnannotatedClassAttribute` instead.

### `reportUnannotatedClassAttribute`

Reports all unannotated class attributes that could be overridden (i.e. not `Final`
and not private), even without an incompatible override. A practical alternative to
`reportIncompatibleUnannotatedOverride`, and required if you want your library to be
safe under plain pyright.

### `reportInvalidAbstractMethod`

Reports `@abstractmethod` on a class that does not extend `ABC` — the decorator has no
effect there and the class can be instantiated, which is usually a mistake. Reported at
the method definition, not at every instantiation site.

### `reportSelfClsDefault`

Reports a default value for the first parameter of a class or instance method
(`def foo(self=1)`), which is almost certainly a mistake.

## Diagnostic categories

A rule can be set to any of:

- `error` — CLI exits with code 1
- `warning` — CLI exits with code 1 only when `failOnWarnings` is on (default in `recommended`/`all`)
- `information` — never fails the CLI
- `hint` — language-server only (grey-out / strikethrough via diagnostic tags); never reported by the CLI and never fails it. Baselined diagnostics are reported as hints. In the CLI context this is effectively the same as `none`
- `none` — disabled entirely

`"unreachable"`, `"unused"`, and `"deprecated"` are deprecated category names that act
as aliases for `"hint"` and may be removed.

## Overriding rules

Three levels, in decreasing scope:

1. **Config file** — set the rule key to a boolean or a category string in
   `pyrightconfig.json` / `[tool.basedpyright]` (or per execution environment).
2. **File comment** — `# pyright: strict`, `# pyright: basic`, or individual
   overrides like `# pyright: reportPrivateUsage=false` and
   `# pyright: reportPrivateUsage=warning, reportOptionalCall=error`, placed at or
   near the top of the file.
3. **Language server** — `basedpyright.analysis.diagnosticSeverityOverrides` map
   (discouraged in favor of a committed config file).

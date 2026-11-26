# Coming from mypy or Pyright (ty 0.0.111)

Source: `docs/coming-from-mypy-or-pyright.md` in the ty repository at tag 0.0.111 (https://github.com/astral-sh/ty/tree/0.0.111).

- [Migration tips](#migration-tips)
- [Stricter checking with ty](#stricter-checking-with-ty)
- [Mapping mypy/Pyright rules to ty/Ruff rules](#mapping-mypy-pyright-rules-to-ty-ruff-rules)

## Migration tips

- mypy disables an error code with `# type: ignore[code]`; pyright suppresses a single line with `# pyright: ignore[reportXyz]`; ty's equivalent is `# ty: ignore[rule]`.
- mypy's `disable_error_code` and pyright's `reportXyz = "none"` both correspond to setting `<rule> = "ignore"` under `[tool.ty.rules]`.
- Severities in ty are `ignore`, `warn`, `error`. Pyright's `"information"` level and basedpyright's `"hint"` level have no direct ty equivalent — use `warn` for both.
- For the equivalent of `disallow_untyped_defs` / `no-untyped-def` (mypy) or `reportMissingParameterType` / `reportUnknownParameterType` (pyright): ty does not warn about missing type annotations by default; use Ruff's `ANN` rules instead (see the recommended configuration below).
- Unlike mypy, ty checks the bodies of unannotated functions unconditionally, so there is no ty rule corresponding to mypy's `check_untyped_defs`. The equivalent pyright setting is `analyzeUnannotatedFunctions = true`.
- ty does not have an equivalent to mypy plugins, but it has built-in support for select popular libraries.

## Stricter checking with ty

Both mypy and pyright "strict" modes enable otherwise-disabled error codes and change fundamental inference behavior. Mypy's strict mode includes `--check-untyped-defs`; pyright's includes `strictListInference` (without it, `[1, "foo"]` infers as `list[Unknown]`).

ty's default mode is stricter than either in many ways: it has no `--check-untyped-defs` or `strictListInference` flags because those are ty's default behavior and not currently configurable. Nearly all ty rules are enabled by default; the ones disabled by default are usually very opinionated or have many false positives.

Recommended approximation of `--strict` (from the ty docs):

```toml
[tool.ty.rules]
dynamic-function-decorator-return = "error"
missing-type-argument = "error"
possibly-unresolved-reference = "warn"
unsound-return = "error"

[tool.ruff.lint]
extend-select = ["ANN", "PYI"]
preview = true
```

An even stricter configuration (beyond mypy/pyright `--strict` in several respects):

```toml
[tool.ty.rules]
blanket-ignore-comment = "error"
dynamic-function-decorator-return = "error"
missing-type-argument = "error"
possibly-unresolved-reference = "warn"
unsound-assignment = "error"
unsound-return = "error"
unsound-yield = "error"
unsupported-dynamic-base = "warn"

# NOTE: the following rules are known to have a significant number of false positives,
# which is mostly unavoidable. Enable them at your own risk!
division-by-zero = "warn"
possibly-missing-attribute = "warn"
possibly-missing-import = "warn"

[tool.ty.analysis]
strict-equality-semantics = true
strict-generic-narrowing = true

[tool.ruff.lint]
extend-select = ["ANN", "PYI", "PGH003"]
preview = true
```

## Mapping mypy/Pyright rules to ty/Ruff rules

How to read: the first column is the ty rule (configure under `[tool.ty.rules]`) or, where no ty rule exists, the Ruff rule or group providing equivalent coverage. The mypy column is the value passed to `# type: ignore[<code>]` or `disable_error_code`; some ty rules surface as one of mypy's catch-all codes (`misc`, `assignment`, `valid-type`) — those mappings are deliberately broad. The pyright column is the `report*` setting. A mypy code or pyright diagnostic may appear in several rows; when migrating a suppression, look for the row that matches the error in your code. Some listed rules are disabled by default in ty.

| ty or Ruff rule | Mypy error code | Pyright or basedpyright diagnostic |
|---|---|---|
| `abstract-and-final-method` | `misc` |  |
| `abstract-class-instantiation` | `abstract` (abstract classes); `misc` (protocols) | `reportAbstractUsage` |
| `abstract-method-call` (direct calls on the class) |  | `reportAbstractUsage` |
| `abstract-method-in-final-class` | `misc` | `reportGeneralTypeIssues` |
| `blanket-ignore-comment` (`# ty: ignore`) | `ignore-without-code` | `reportIgnoreCommentWithoutRule` (basedpyright only) |
| `call-to-function-with-unknown-signature` |  |  |
| `conflicting-declarations` | `no-redef` | `reportRedeclaration` |
| `conflicting-metaclass` | `metaclass` | `reportGeneralTypeIssues` |
| `cyclic-class-definition` | `misc` | `reportGeneralTypeIssues` |
| `cyclic-type-alias-definition` | `misc` | `reportGeneralTypeIssues` |
| `deprecated` | `deprecated` | `reportDeprecated` |
| `disjoint-cast` |  | `reportInvalidCast` (basedpyright only) |
| `disjoint-type-is-narrowing` (`TypeIs` target and input cannot overlap) | `narrowed-type-not-subtype` | `reportGeneralTypeIssues` |
| `division-by-zero` |  |  |
| `duplicate-base` | `misc` | `reportGeneralTypeIssues` |
| `duplicate-kw-only` | `misc` | `reportGeneralTypeIssues` |
| `dynamic-function-decorator-return` | `untyped-decorator` | `reportUntypedFunctionDecorator` (`Unknown` returns only) |
| `final-on-non-method` | `misc` | `reportGeneralTypeIssues` |
| `final-without-value` | `misc` | `reportGeneralTypeIssues` |
| `implicit-string-concatenation-in-annotation` |  | `reportGeneralTypeIssues`; `reportImplicitStringConcatenation` (same line only) |
| `import-not-found` | `import-not-found` | `reportMissingImports` |
| `incompatible-attribute-override` | `assignment`; `misc` (e.g., `ClassVar`); `override` (method replacing a variable) | `reportIncompatibleVariableOverride`; `reportIncompatibleMethodOverride` (replacing a method) |
| `incompatible-method-override` | `override` | `reportIncompatibleMethodOverride` |
| `incompatible-mutable-override` (narrowing a writable attribute) | `mutable-override` | `reportIncompatibleVariableOverride` |
| `incompatible-property-override` | `override`; `misc` (removing a setter) | `reportIncompatibleMethodOverride`; `reportIncompatibleVariableOverride` (replacing a variable) |
| `incompatible-property-override` (variable replacing a property) | `assignment`; `mutable-override` | `reportIncompatibleMethodOverride` |
| `inconsistent-mro` | `misc` | `reportGeneralTypeIssues` |
| `inconsistent-overload-decorator` (`@staticmethod` or `@classmethod`) | `misc` | `reportInconsistentOverload` |
| `inconsistent-overload-implementation` | `misc` | `reportInconsistentOverload` |
| `index-out-of-bounds` | `misc` | `reportGeneralTypeIssues` |
| `invalid-argument-type` | `arg-type`; `index`; `type-var` | `reportArgumentType` |
| `invalid-argument-type` (wrong value type when creating a `TypedDict`) | `typeddict-item` | `reportArgumentType`; `reportAssignmentType`; `reportReturnType` |
| `invalid-argument-type` (deleting an undeclared TypedDict key) | `typeddict-item` | `reportGeneralTypeIssues` |
| `invalid-assignment` | `assignment`; `list-item`; `dict-item` | `reportAssignmentType` |
| `invalid-assignment` (assigning a function with an incompatible signature to a method) | `method-assign` (rejects all method assignments) | `reportAttributeAccessIssue` |
| `invalid-assignment` (assigning to a TypedDict item) | `typeddict-item` | `reportGeneralTypeIssues` |
| `invalid-assignment` (`ReadOnly` TypedDict keys) | `typeddict-readonly-mutated` | `reportTypedDictNotRequiredAccess` (mutations of `ReadOnly` TypedDict keys only) |
| `invalid-attribute-access` | `misc` | `reportAttributeAccessIssue` |
| `invalid-await` | `misc` | `reportGeneralTypeIssues` |
| `invalid-base` | `valid-type`; `misc` | `reportGeneralTypeIssues` |
| `invalid-context-manager` | `misc`; `attr-defined`; `union-attr` | `reportGeneralTypeIssues`; `reportOptionalContextManager` |
| `invalid-dataclass` | `misc` | `reportGeneralTypeIssues` (when `slots=True` conflicts with `__slots__` only) |
| `invalid-dataclass-field-order` | `misc` | `reportGeneralTypeIssues` |
| `invalid-dataclass-post-init` | `override` | `reportGeneralTypeIssues` |
| `invalid-exception-caught` | `misc` | `reportGeneralTypeIssues` |
| `invalid-explicit-override` | `misc` | `reportGeneralTypeIssues` |
| `invalid-explicit-return` | `return-value`; `misc` (`Never` or `NoReturn`) | `reportReturnType`; `reportGeneralTypeIssues` (`Never` or `NoReturn`) |
| `invalid-frozen-dataclass-subclass` | `misc` | `reportGeneralTypeIssues` |
| `invalid-generator-return-type` | `misc` | `reportInvalidTypeForm` (annotation); `reportReturnType` (`yield`) |
| `invalid-generic-class` (type-variable variance in methods) | `misc` | `reportGeneralTypeIssues` |
| `invalid-implicit-return` | `return`; `misc` (`Never` or `NoReturn`) | `reportReturnType` |
| `invalid-implicit-return-in-function-with-stub-body` | `empty-body` | `reportReturnType` (`...` bodies are exempt) |
| `invalid-init-type-variable` |  | `reportInvalidTypeVarUse` |
| `invalid-legacy-type-variable` | `misc`; `valid-type` | `reportGeneralTypeIssues`; `reportInvalidTypeForm` |
| `invalid-match-pattern` (class-pattern positional argument count only) | `misc` | `reportGeneralTypeIssues` |
| `invalid-metaclass` | `metaclass` |  |
| `invalid-module-getattr-call` |  |  |
| `invalid-named-tuple` (field names starting with an underscore only) | `misc` | `reportGeneralTypeIssues` |
| `invalid-newtype` | `valid-newtype`; `misc` | `reportGeneralTypeIssues`; `reportArgumentType` |
| `invalid-parameter-default` | `assignment` | `reportArgumentType` |
| `invalid-protocol` | `misc` | `reportGeneralTypeIssues` |
| `invalid-raise` | `misc` | `reportGeneralTypeIssues` |
| `invalid-type-arguments` | `misc`; `type-var` | `reportInvalidTypeArguments` |
| `invalid-type-form` | `valid-type` | `reportInvalidTypeForm`; `reportGeneralTypeIssues` |
| `invalid-type-guard-definition` | `valid-type` | `reportGeneralTypeIssues` (no input parameter) |
| `invalid-type-variable-bound` | `valid-type`; `misc` | `reportGeneralTypeIssues` |
| `invalid-type-variable-constraints` | `valid-type`; `misc` | `reportGeneralTypeIssues` |
| `invalid-type-variable-default` | `misc` | `reportGeneralTypeIssues` |
| `invalid-typed-dict-field` | `misc` | `reportIncompatibleVariableOverride` |
| `invalid-typed-dict-header` (custom metaclasses only) | `call-arg` | `reportGeneralTypeIssues` |
| `invalid-typed-dict-key` (reads and writes of string literals naming undeclared keys) | `typeddict-item` (reads); `typeddict-unknown-key` (writes) | `reportGeneralTypeIssues` |
| `invalid-typed-dict-key` (reads and writes of non-string keys) | `literal-required` (reads and writes); `typeddict-item` (additional error on writes) | `reportGeneralTypeIssues` |
| `invalid-typed-dict-statement` (methods in a TypedDict body) | `misc` | `reportGeneralTypeIssues` |
| `invalid-yield` | `misc` | `reportReturnType` |
| `isinstance-against-protocol` | `misc` | `reportArgumentType`; `reportGeneralTypeIssues` |
| `isinstance-against-typed-dict` | `misc` | `reportArgumentType`; `reportGeneralTypeIssues` |
| `lost-keyword-for-regular-parameter` |  | `reportIncompatibleMethodOverride` |
| `mismatched-enum-name` | `misc` |  |
| `mismatched-namedtuple-name` | `name-match` |  |
| `mismatched-newtype-name` | `misc` | `reportGeneralTypeIssues`; `reportArgumentType` (non-literal names) |
| `mismatched-paramspec-name` | `misc` | `reportGeneralTypeIssues` |
| `mismatched-sentinel-name` |  | `reportGeneralTypeIssues` |
| `mismatched-type-alias-name` | `misc` | `reportGeneralTypeIssues` |
| `mismatched-typeddict-name` | `name-match`; `misc` (non-literal names) | `reportGeneralTypeIssues`; `reportArgumentType` (non-literal names) |
| `mismatched-typevar-name` | `misc` | `reportGeneralTypeIssues` |
| `mismatched-typevartuple-name` | `misc` | `reportGeneralTypeIssues` |
| `misplaced-overload-decorator` (`@final` or `@override`) | `misc` (`@final` only) | `reportInconsistentOverload` |
| `missing-argument` | `call-arg` | `reportCallIssue` |
| `missing-attribute` | `attr-defined`; `union-attr` (attribute missing from every union member) | `reportAttributeAccessIssue`; `reportFunctionMemberAccess`; `reportOptionalMemberAccess` |
| `missing-attribute` (`module.name` when a stub doesn't re-export `name`) | `attr-defined` | `reportAttributeAccessIssue` |
| `missing-module-member` | `attr-defined` | `reportAttributeAccessIssue` |
| `missing-overload-implementation` | `no-overload-impl` | `reportNoOverloadImplementation` |
| `missing-override-decorator` | `explicit-override` | `reportImplicitOverride` |
| `missing-type-argument` | `type-arg` | `reportMissingTypeArgument` |
| `missing-typed-dict-key` (keyword arguments) | `typeddict-item` | `reportCallIssue` |
| `missing-typed-dict-key` (dictionary literals) | `typeddict-item` | `reportArgumentType`; `reportAssignmentType`; `reportReturnType` |
| `missing-union-attribute` | `union-attr` | `reportAttributeAccessIssue`; `reportFunctionMemberAccess`; `reportOptionalMemberAccess` |
| `no-matching-overload` | `call-overload` | `reportCallIssue` |
| `non-literal-typed-dict-key` (subscripts of type `str`) | `literal-required` |  |
| `not-callable` | `operator`; `misc` (calls to `None`) | `reportCallIssue`; `reportOptionalCall` |
| `not-iterable` | `misc`; `attr-defined`; `union-attr` | `reportGeneralTypeIssues`; `reportOptionalIterable` |
| `not-subscriptable` | `index` | `reportIndexIssue`; `reportOptionalSubscript` |
| `override-of-final-method` | `misc` | `reportIncompatibleMethodOverride` |
| `override-of-final-variable` | `misc` | `reportGeneralTypeIssues` |
| `parameter-already-assigned` | `misc`; `call-arg` | `reportCallIssue` |
| `positional-only-parameter-as-kwarg` | `call-arg` | `reportCallIssue` |
| `possibly-missing-attribute` |  |  |
| `possibly-unresolved-reference` | `possibly-undefined` | `reportPossiblyUnboundVariable` |
| `redundant-cast` | `redundant-cast` | `reportUnnecessaryCast` |
| `redundant-condition` (guaranteed truthiness only) | `truthy-bool` |  |
| `redundant-condition` (function objects only) | `truthy-function` | `reportUnnecessaryComparison` |
| `redundant-condition` (some boolean tests of `None`-returning calls only) | `func-returns-value` |  |
| `redundant-condition`, `redundant-condition-strict` | `redundant-expr` (unlike mypy, ty checks `and`/`or` only in boolean conditions such as `if` tests, not when computing values) |  |
| `redundant-condition`, `redundant-condition-strict` | `comparison-overlap` (in boolean conditions such as `if` tests; other cases are not yet implemented) | `reportUnnecessaryComparison`; `reportUnnecessaryContains` (both in boolean conditions such as `if` tests) |
| `redundant-condition`, `redundant-condition-strict` | `unreachable` (in boolean conditions such as `if` tests that lead to unreachable code; other cases are not yet implemented) | `reportUnreachable` (in boolean conditions such as `if` tests that lead to unreachable code only) |
| `redundant-condition-strict` |  | `reportUnnecessaryIsInstance` (in boolean conditions such as `if` tests) |
| `renamed-rule-in-ignore-comment` |  |  |
| `single-overload` | `misc` | `reportInconsistentOverload` |
| `subclass-of-final-class` | `misc` | `reportGeneralTypeIssues` |
| `suspicious-type-is-narrowing` (incompatible `TypeIs` target that may overlap the input) | `narrowed-type-not-subtype` | `reportGeneralTypeIssues` |
| `too-many-positional-arguments` | `call-arg` | `reportCallIssue` |
| `truthiness-test-of-callable` | `truthy-function` | `reportUnnecessaryComparison` |
| `truthiness-test-of-iterable` | `truthy-iterable`; `truthy-bool` |  |
| `truthiness-test-of-none-union` |  |  |
| `type-assertion-failure` | `assert-type` | `reportAssertTypeFailure` |
| `unbound-type-variable` | `valid-type` | `reportGeneralTypeIssues` |
| `undefined-reveal` | `unimported-reveal` |  |
| `unknown-argument` | `call-arg` | `reportCallIssue` |
| `unknown-rule-in-ignore-comment` |  |  |
| `unknown-typed-dict-constructor-key` (keyword arguments) | `typeddict-unknown-key` | `reportCallIssue` |
| `unknown-typed-dict-constructor-key` (dictionary literals) | `typeddict-unknown-key`; `misc` (keys other than string literals) | `reportArgumentType`; `reportAssignmentType`; `reportReturnType` |
| `unknown-typed-dict-constructor-key` (unpacking a `dict` into a closed `TypedDict`) | `typeddict-item` |  |
| `unresolved-reference` | `name-defined`; `used-before-def` | `reportUndefinedVariable`; `reportUnboundVariable` |
| `unsound-assignment` (variables only) |  |  |
| `unsound-return` | `no-any-return` |  |
| `unsound-yield` |  |  |
| `unsupported-operator` | `operator` | `reportOperatorIssue`; `reportOptionalOperand` |
| `unused-awaitable` (native coroutines only) | `unused-coroutine`; `unused-awaitable` | `reportUnusedCoroutine`; `reportUnusedCallResult` (discarded native coroutine calls only) |
| `unused-ignore-comment` (`# ty: ignore`) | `unused-ignore` | `reportUnnecessaryTypeIgnoreComment` |
| `unused-type-ignore-comment` (`# type: ignore`) | `unused-ignore` | `reportUnnecessaryTypeIgnoreComment` |
| No direct equivalent planned for passing abstract classes where concrete classes are required | `type-abstract` |  |
| None yet for calling abstract methods through `super()` | `safe-super` | `reportAbstractUsage` |
| Ruff `F631` |  | `reportAssertAlwaysTrue` |
| Ruff `B006`; Ruff `B008` (partial coverage; immutable annotations and calls are excluded) |  | `reportCallInDefaultInitializer` |
| None yet (tracked in Ruff #10137) |  | `reportConstantRedefinition` |
| Ruff `F811`; Ruff `I001` (partial coverage; separate import blocks may be missed) |  | `reportDuplicateImport` |
| Ruff `ISC001`; Ruff `ISC002` |  | `reportImplicitStringConcatenation` |
| None yet (tracked in #3647) |  | `reportImportCycles` |
| None yet |  | `reportIncompleteStub` |
| None yet (tracked in #3651) |  | `reportInconsistentConstructor` |
| Ruff `W605` |  | `reportInvalidStringEscapeSequence` |
| Ruff `PYI010`; Ruff `PYI017`; Ruff `PYI048`; Ruff `PYI052` |  | `reportInvalidStubStatement` |
| None yet for other cases (tracked in #1017, #3636, #3637) | `type-var` | `reportInvalidTypeVarUse` |
| None yet (tracked in #1060) | `exhaustive-match` | `reportMatchNotExhaustive` |
| None yet (tracked in #1577) |  | `reportMissingModuleSource` |
| None yet (tracked in #3652) |  | `reportMissingSuperCall` |
| None yet (tracked in #3638) | `import-untyped` | `reportMissingTypeStubs` |
| None yet (tracked in #103) | `overload-cannot-match`; `overload-overlap` | `reportOverlappingOverload` |
| None yet for non-re-exported names in runtime files (tracked in #200) | `attr-defined`; (extended by `--no-implicit-reexport`) | `reportPrivateImportUsage`; `reportPrivateLocalImportUsage` (basedpyright only) |
| Ruff `SLF001`; Ruff `PLC2701` (partial coverage; `PLC2701` requires preview) |  | `reportPrivateUsage` |
| None yet (tracked in #3633) |  | `reportPropertyTypeMismatch` |
| Ruff `N804`; Ruff `N805` |  | `reportSelfClsParameterName` |
| Ruff `PYI033` (`.py` files require preview) |  | `reportTypeCommentUsage` |
| None yet for accessing non-required keys (tracked in #2810) |  | `reportTypedDictNotRequiredAccess` |
| None yet (tracked in #3781) |  | `reportUnhashable` |
| None yet (tracked in #2954) |  | `reportUninitializedInstanceVariable` |
| None yet |  | `reportUnknownArgumentType`; `reportUnknownLambdaType`; `reportUnknownMemberType` |
| None yet | `var-annotated` |  |
| None yet |  | `reportUnknownVariableType` |
| Ruff `F822`; Ruff `PLE0604`; Ruff `PLE0605`; Ruff `PYI056` |  | `reportUnsupportedDunderAll` |
| None yet |  | `reportUntypedBaseClass`; `reportUntypedClassDecorator` |
| Ruff `PYI024` |  | `reportUntypedNamedTuple` |
| None yet |  | `reportUnusedClass`; `reportUnusedFunction` |
| None yet for other discarded call results |  | `reportUnusedCallResult` |
| Ruff `ARG` rules |  | `reportUnusedParameter` (basedpyright only) |
| Ruff `B025` (duplicate exception handlers only; other cases tracked in #3701) |  | `reportUnusedExcept` |
| Ruff `B015`; Ruff `B018` |  | `reportUnusedExpression` |
| Ruff `F401` |  | `reportUnusedImport` |
| Ruff `F841` (function-local variables only) |  | `reportUnusedVariable` |
| Ruff `F403` |  | `reportWildcardImportFromLibrary` |
| Ruff `ANN401` (function annotations only) | `explicit-any` | `reportExplicitAny` (basedpyright only) |
| None yet for other uses of `None`-returning calls | `func-returns-value` |  |
| None yet | `no-any-unimported` |  |
| None yet (tracked in #4381) | `no-untyped-call` |  |
| Ruff `F505`; Ruff `F507` (missing names or wrong argument counts only) | `str-format` (partial coverage) |  |
| Ruff `F522`; Ruff `F523`; Ruff `F524` (missing or extra arguments only) | `str-format` (partial coverage) |  |
| Ruff `ANN` rules | `no-untyped-def` | `reportMissingParameterType`; `reportUnknownParameterType` |

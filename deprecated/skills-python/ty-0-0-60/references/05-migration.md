# Migration from mypy / pyright

## Key differences

- **Suppression syntax**: mypy uses `# type: ignore[code]`, pyright uses
  `# pyright: ignore[reportXyz]`, ty uses `# ty: ignore[rule]`.
- **Severity levels**: ty uses `ignore`, `warn`, `error`. pyright's `information`
  and `hint` map to `warn`.
- **Unannotated functions**: ty checks them unconditionally (no equivalent to
  mypy's `check_untyped_defs`).
- **No strict mode**: ty's default mode is stricter than mypy/pyright defaults.
  No flags like `--check-untyped-defs` or `strictListInference` — these are ty's
  default behavior.

## Suppression mapping

| mypy | pyright | ty |
|------|---------|-----|
| `# type: ignore[code]` | `# pyright: ignore[reportXyz]` | `# ty: ignore[rule]` |
| `disable_error_code = [...]` | `reportXyz = "none"` | `<rule> = "ignore"` |

## Recommended strict configuration

```toml
[tool.ty.rules]
missing-type-argument = "error"
possibly-unresolved-reference = "warn"

[tool.ruff.lint]
extend-select = ["ANN", "PYI"]
preview = true
```

Pair ty with Ruff's ANN (annotation) and PYI (stub) rules for comprehensive
type annotation enforcement.

## Rule mapping

### ty rules with mypy/pyright equivalents

| ty rule | mypy code | pyright diagnostic |
|---------|-----------|-------------------|
| `call-abstract-method` | — | `reportAbstractUsage` |
| `call-non-callable` | `operator` | `reportCallIssue` |
| `conflicting-declarations` | `no-redef` | `reportRedeclaration` |
| `conflicting-metaclass` | `metaclass` | `reportGeneralTypeIssues` |
| `deprecated` | `deprecated` | `reportDeprecated` |
| `duplicate-base` | `misc` | `reportGeneralTypeIssues` |
| `empty-body` | `empty-body` | — |
| `inconsistent-mro` | `misc` | `reportGeneralTypeIssues` |
| `index-out-of-bounds` | `misc` | `reportGeneralTypeIssues` |
| `invalid-argument-type` | `arg-type`, `index` | `reportArgumentType` |
| `invalid-assignment` | `assignment` | `reportAssignmentType` |
| `invalid-attribute-access` | `misc` | `reportAttributeAccessIssue` |
| `invalid-await` | `misc` | `reportGeneralTypeIssues` |
| `invalid-base` | `valid-type` | `reportGeneralTypeIssues` |
| `invalid-context-manager` | `misc`, `attr-defined` | `reportGeneralTypeIssues` |
| `invalid-exception-caught` | `misc` | `reportGeneralTypeIssues` |
| `invalid-key` | `typeddict-item` | `reportAssignmentType` |
| `invalid-metaclass` | `metaclass` | — |
| `invalid-method-override` | `override` | `reportIncompatibleMethodOverride` |
| `invalid-overload` | `no-overload-impl` | `reportNoOverloadImplementation` |
| `invalid-parameter-default` | `assignment` | `reportArgumentType` |
| `invalid-raise` | `misc` | `reportGeneralTypeIssues` |
| `invalid-return-type` | `return-value` | `reportReturnType` |
| `invalid-type-arguments` | `misc`, `type-var` | `reportInvalidTypeArguments` |
| `invalid-type-form` | `valid-type` | `reportInvalidTypeForm` |
| `missing-argument` | `call-arg` | `reportCallIssue` |
| `missing-override-decorator` | `explicit-override` | `reportImplicitOverride` |
| `missing-type-argument` | `type-arg` | `reportMissingTypeArgument` |
| `missing-typed-dict-key` | `typeddict-item` | `reportAssignmentType` |
| `no-matching-overload` | `call-overload` | `reportCallIssue` |
| `not-iterable` | `misc`, `attr-defined` | `reportGeneralTypeIssues` |
| `not-subscriptable` | `index` | `reportIndexIssue` |
| `parameter-already-assigned` | `misc`, `call-arg` | `reportCallIssue` |
| `possibly-missing-attribute` | — | — |
| `possibly-unresolved-reference` | `possibly-undefined` | `reportPossiblyUnboundVariable` |
| `redundant-cast` | `redundant-cast` | `reportUnnecessaryCast` |
| `too-many-positional-arguments` | `call-arg` | `reportCallIssue` |
| `type-assertion-failure` | `assert-type` | `reportAssertTypeFailure` |
| `undefined-reveal` | `unimported-reveal` | — |
| `unknown-argument` | `call-arg` | `reportCallIssue` |
| `unresolved-attribute` | `attr-defined`, `union-attr` | `reportAttributeAccessIssue` |
| `unresolved-import` | `import-not-found` | `reportMissingImports` |
| `unresolved-reference` | `name-defined` | `reportUndefinedVariable` |
| `unsupported-operator` | `operator` | `reportOperatorIssue` |
| `unused-awaitable` | `unused-coroutine` | `reportUnusedCoroutine` |
| `unused-ignore-comment` | `unused-ignore` | `reportUnnecessaryTypeIgnoreComment` |

### Checks not yet in ty (use Ruff or wait)

| mypy code | pyright diagnostic | Status |
|-----------|-------------------|--------|
| `exhaustive-match` | `reportMatchNotExhaustive` | [#1060](https://github.com/astral-sh/ty/issues/1060) |
| `unreachable` | `reportUnreachable` | [#1948](https://github.com/astral-sh/ty/issues/1948) |
| `import-untyped` | `reportMissingTypeStubs` | [#3638](https://github.com/astral-sh/ty/issues/3638) |
| `overload-overlap` | `reportOverlappingOverload` | [#103](https://github.com/astral-sh/ty/issues/103) |
| — | `reportPrivateImportUsage` | [#200](https://github.com/astral-sh/ty/issues/200) |
| — | `reportPropertyTypeMismatch` | [#3633](https://github.com/astral-sh/ty/issues/3633) |
| — | `reportConstantRedefinition` | [Ruff #10137](https://github.com/astral-sh/ruff/issues/10137) |
| — | `reportImportCycles` | [#3647](https://github.com/astral-sh/ty/issues/3647) |
| — | `reportInconsistentConstructor` | [#3651](https://github.com/astral-sh/ty/issues/3651) |
| — | `reportMissingSuperCall` | [#3652](https://github.com/astral-sh/ty/issues/3652) |
| — | `reportUninitializedInstanceVariable` | [#2954](https://github.com/astral-sh/ty/issues/2954) |
| `no-untyped-def` | `reportMissingParameterType` | Use Ruff `ANN` rules |

### Checks covered by Ruff instead

| pyright diagnostic | Ruff rule(s) |
|-------------------|-------------|
| `reportDuplicateImport` | `F811`, `I001` |
| `reportInvalidStringEscapeSequence` | `W605` |
| `reportInvalidStubStatement` | `PYI010`, `PYI017`, `PYI048`, `PYI052` |
| `reportUnsupportedDunderAll` | `F822`, `PLE0604`, `PLE0605`, `PYI056` |
| `reportUntypedNamedTuple` | `PYI024` |
| `reportUnusedExpression` | `B018` |
| `reportWildcardImportFromLibrary` | `F403` |
| `reportSelfClsParameterName` | `N804`, `N805` |
| `reportTypeCommentUsage` | `PYI033` (preview) |

## Migration steps

1. **Install ty**: `uv add --dev ty` or `pip install ty`
2. **Run initial check**: `ty check` — review diagnostics
3. **Replace suppression comments**: `type: ignore[code]` → `ty: ignore[rule]`
4. **Configure rules**: map mypy/pyright settings to `[tool.ty.rules]`
5. **Enable stricter rules**: `missing-type-argument = "error"`, `possibly-unresolved-reference = "warn"`
6. **Add Ruff ANN rules**: for missing annotation enforcement
7. **Set up LSP**: install ty extension or configure `ty server`
8. **Remove mypy/pyright**: once ty covers all needed checks

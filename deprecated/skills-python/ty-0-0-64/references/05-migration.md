# Migration from mypy or pyright

## Key differences

- ty checks function bodies unconditionally (no `--check-untyped-defs` equivalent needed)
- ty has no `--strict` flag — default mode is already strict
- ty does not have `disallow_untyped_defs` / `no-untyped-def` equivalents
- ty does not have `strictListInference` — strict inference is the default
- ty uses `--error`, `--warn`, `--ignore` instead of `--select`/`--ignore`
- ty supports `type: ignore` and `ty: ignore[rule]` suppression comments

## Recommended strict configuration

Approximate mypy/pyright `--strict` mode:

```toml
[tool.ty.rules]
missing-type-argument = "error"
possibly-unresolved-reference = "warn"

[tool.ruff.lint]
extend-select = ["ANN", "PYI"]
preview = true
```

Even stricter (beyond mypy/pyright strict mode):

```toml
[tool.ty.rules]
blanket-ignore-comment = "error"
missing-type-argument = "error"
possibly-unresolved-reference = "warn"
unsupported-dynamic-base = "warn"
division-by-zero = "warn"
possibly-missing-attribute = "warn"
possibly-missing-import = "warn"

[tool.ty.analysis]
strict-equality-semantics = true

[tool.ruff.lint]
extend-select = ["ANN", "PYI", "PGH003"]
preview = true
```

## Rule mapping

### ty rules with mypy equivalents

| ty rule | mypy code | pyright diagnostic |
|---------|-----------|-------------------|
| `call-abstract-method` | — | `reportAbstractUsage` |
| `call-non-callable` | `operator` | `reportCallIssue` |
| `conflicting-declarations` | `no-redef` | `reportRedeclaration` |
| `conflicting-metaclass` | `metaclass` | `reportGeneralTypeIssues` |
| `deprecated` | `deprecated` | `reportDeprecated` |
| `empty-body` | `empty-body` | — |
| `invalid-argument-type` | `arg-type` | `reportArgumentType` |
| `invalid-assignment` | `assignment` | `reportAssignmentType` |
| `invalid-attribute-access` | `misc` | `reportAttributeAccessIssue` |
| `invalid-await` | `misc` | `reportGeneralTypeIssues` |
| `invalid-base` | `valid-type` | `reportGeneralTypeIssues` |
| `invalid-method-override` | `override` | `reportIncompatibleMethodOverride` |
| `invalid-overload` | `no-overload-impl` | `reportNoOverloadImplementation` |
| `invalid-return-type` | `return-value` | `reportReturnType` |
| `invalid-type-arguments` | `misc` | `reportInvalidTypeArguments` |
| `invalid-type-form` | `valid-type` | `reportInvalidTypeForm` |
| `missing-argument` | `call-arg` | `reportCallIssue` |
| `missing-override-decorator` | `explicit-override` | `reportImplicitOverride` |
| `missing-type-argument` | `type-arg` | `reportMissingTypeArgument` |
| `no-matching-overload` | `call-overload` | `reportCallIssue` |
| `not-iterable` | `misc` | `reportGeneralTypeIssues` |
| `not-subscriptable` | `index` | `reportIndexIssue` |
| `possibly-unresolved-reference` | `possibly-undefined` | `reportPossiblyUnboundVariable` |
| `redundant-cast` | `redundant-cast` | `reportUnnecessaryCast` |
| `type-assertion-failure` | `assert-type` | `reportAssertTypeFailure` |
| `unresolved-attribute` | `attr-defined` | `reportAttributeAccessIssue` |
| `unresolved-import` | `import-not-found` | `reportMissingImports` |
| `unresolved-reference` | `name-defined` | `reportUndefinedVariable` |
| `unsupported-operator` | `operator` | `reportOperatorIssue` |
| `unused-awaitable` | `unused-coroutine` | `reportUnusedCoroutine` |
| `unused-ignore-comment` | `unused-ignore` | `reportUnnecessaryTypeIgnoreComment` |

### Checks not yet in ty

| Feature | mypy | pyright | Status |
|---------|------|---------|--------|
| Constant redefinition | — | `reportConstantRedefinition` | Tracked in Ruff |
| Import cycles | — | `reportImportCycles` | Tracked |
| Incomplete stubs | — | `reportIncompleteStub` | Not yet |
| Inconsistent constructor | — | `reportInconsistentConstructor` | Tracked |
| Invalid TypeVar use | `type-var` | `reportInvalidTypeVarUse` | Tracked |
| Exhaustive match | `exhaustive-match` | `reportMatchNotExhaustive` | Tracked |
| Missing super call | — | `reportMissingSuperCall` | Tracked |
| Import untyped | `import-untyped` | `reportMissingTypeStubs` | Tracked |
| Overlapping overloads | `overload-overlap` | `reportOverlappingOverload` | Tracked |
| Private import usage | `attr-defined` | `reportPrivateImportUsage` | Tracked |
| Property type mismatch | — | `reportPropertyTypeMismatch` | Tracked |
| Unreachable code | `unreachable` | `reportUnreachable` | Tracked |
| no-any-return | `no-any-return` | — | Not yet |

### Checks covered by Ruff instead

| Check | Ruff rule(s) |
|-------|-------------|
| Duplicate imports | `F811`, `I001` |
| Self/cls naming | `N804`, `N805` |
| Blanket type: ignore | `PGH003` |
| Invalid stub statements | `PYI010`, `PYI017`, `PYI048`, `PYI052` |
| Untyped NamedTuple | `PYI024` |
| Type comment usage | `PYI033` (preview) |
| Unsupported `__all__` | `F822`, `PLE0604`, `PLE0605`, `PYI056` |
| Unused expression | `B018` |
| Wildcard import | `F403` |
| Missing type annotations | `ANN` rules |

## Suppression comment migration

### mypy → ty

```python
# mypy
x = bad_call()  # type: ignore[arg-type]

# ty equivalent
x = bad_call()  # ty: ignore[invalid-argument-type]
# or keep standard format:
x = bad_call()  # type: ignore[ty:invalid-argument-type]
```

### pyright → ty

pyright uses `# pyright: ignore[reportArgumentType]`. Replace with ty rules:

```python
# pyright
x = bad_call()  # pyright: ignore[reportArgumentType]

# ty
x = bad_call()  # ty: ignore[invalid-argument-type]
```

## Configuration migration

### mypy `mypy.ini` → `ty.toml`

```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
disallow_untyped_defs = True
```

```toml
# ty.toml
[environment]
python-version = "3.11"

[rules]
missing-type-argument = "error"
```

### pyright `pyrightconfig.json` → `ty.toml`

```json
{
  "pythonVersion": "3.11",
  "reportMissingTypeArgument": "error",
  "reportUnusedVariable": "warning"
}
```

```toml
# ty.toml
[environment]
python-version = "3.11"

[rules]
missing-type-argument = "error"
```

## CI migration

### GitHub Actions

```yaml
# Before (mypy)
- run: pip install mypy && mypy src/

# After (ty)
- run: uvx ty@0.0.64 check src/
```

```yaml
# Before (pyright)
- run: npx pyright src/

# After (ty)
- run: uvx ty@0.0.64 check src/
```

### pre-commit

```yaml
# Before
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v0.900
  hooks:
    - id: mypy

# After
- repo: https://github.com/astral-sh/ty-pre-commit
  rev: 0.0.64
  hooks:
    - id: ty
```

## Using ty alongside Ruff

ty handles type checking; Ruff handles linting and formatting. Together they replace
mypy + Flake8 + Black + isort:

```toml
# pyproject.toml
[tool.ty.rules]
missing-type-argument = "error"

[tool.ruff.lint]
select = ["E", "F", "B", "UP", "I"]

[tool.ruff.format]
quote-style = "double"
```

```bash
ruff check --fix && ruff format && ty check
```

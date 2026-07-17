# Migrating from mypy or pyright

## Key Differences

### Suppression comments

| Tool | Syntax |
|------|--------|
| mypy | `# type: ignore[code]` |
| pyright | `# pyright: ignore[reportXyz]` |
| ty | `# ty: ignore[rule]` |

ty also supports standard `type: ignore` and `type: ignore[ty:rule]` by default.

### Rule configuration

| Tool | Config syntax |
|------|---------------|
| mypy | `disable_error_code = ["code"]` |
| pyright | `reportXyz = "none"` in `pyrightconfig.json` |
| ty | `<rule> = "ignore"` under `[tool.ty.rules]` |

### Severity levels

ty uses three levels: `ignore`, `warn`, `error`. Pyright's `"information"` and `"hint"` map to `warn`.

### Stricter defaults

ty is stricter than mypy/Pyright by default:
- Untyped function bodies are always checked (no `--check-untyped-defs` needed)
- List inference is strict (no `strictListInference` flag — it's the default)
- Nearly all rules are enabled by default

### No direct equivalents

- **`disallow_untyped_defs` / `no-untyped-def`** (mypy): ty does not have this rule. Use Ruff's `ANN` rules instead.
- **`check_untyped_defs`** (mypy): always on in ty, not configurable.
- **`--strict`**: ty has no strict mode flag. See recommended config below.

## Recommended "Strict" Configuration

To approximate strict mode from other checkers:

```toml
[tool.ty.terminal]
error-on-warning = true

[tool.ty.rules]
missing-type-argument = "error"
possibly-unresolved-reference = "warn"

[tool.ruff.lint]
extend-select = ["ANN", "PYI"]
```

This enables all disabled-by-default ty rules and adds Ruff annotation checks.

## Rule Mappings (Selected)

### Type errors

| ty rule | mypy code | pyright setting |
|---------|-----------|-----------------|
| `invalid-argument-type` | `arg-type`, `index` | `reportArgumentType` |
| `invalid-assignment` | `assignment` | `reportAssignmentType` |
| `invalid-return-type` | `return-value` | `reportReturnType` |
| `missing-argument` | `call-arg` | `reportCallIssue` |
| `unresolved-import` | `import-not-found` | `reportMissingImports` |
| `unresolved-reference` | `name-defined` | `reportUndefinedVariable` |
| `unresolved-attribute` | `attr-defined` | `reportAttributeAccessIssue` |
| `unsupported-operator` | `operator` | `reportOperatorIssue` |

### Structural checks

| ty rule | mypy code | pyright setting |
|---------|-----------|-----------------|
| `call-non-callable` | `operator` | `reportCallIssue` |
| `invalid-method-override` | `override` | `reportIncompatibleMethodOverride` |
| `unused-awaitable` | `unused-coroutine` | `reportUnusedCoroutine` |
| `deprecated` | `deprecated` | `reportDeprecated` |

### Not yet in ty (use Ruff or wait)

| Feature | Status |
|---------|--------|
| Exhaustive `match` checking | Tracked in [#1060](https://github.com/astral-sh/ty/issues/1060) |
| Import cycle detection | Tracked in [#3647](https://github.com/astral-sh/ty/issues/3647) |
| Unreachable code detection | Tracked in [#1948](https://github.com/astral-sh/ty/issues/1948) |
| `__all__` validation | Use Ruff `F822`, `PLE0604`, `PLE0605` |
| Missing type stubs warning | Tracked in [#3638](https://github.com/astral-sh/ty/issues/3638) |
| Property type mismatch | Tracked in [#3633](https://github.com/astral-sh/ty/issues/3633) |

See the [full mapping table](https://docs.astral.sh/ty/coming-from-mypy-or-pyright/) for complete coverage.

## Migration Steps

1. Install ty: `uv add --dev ty`
2. Run `ty check` to see baseline diagnostics
3. Replace `# type: ignore[code]` with `# ty: ignore[rule]` (or keep `type: ignore` since ty supports it)
4. Move rule config from mypy/pyright config to `[tool.ty.rules]` in `pyproject.toml` or `ty.toml`
5. Enable stricter rules incrementally as you fix issues
6. Optionally add Ruff `ANN` rules for annotation coverage

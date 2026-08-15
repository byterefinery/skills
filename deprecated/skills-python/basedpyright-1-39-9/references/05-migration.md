# Migration Reference

## From pyright

### Installation

```bash
# Remove pyright
pip uninstall pyright
# Or if installed via npm:
npm uninstall pyright

# Install basedpyright
pip install basedpyright
```

### Config file

basedpyright reads `[tool.pyright]` for backward compatibility. To use basedpyright-specific
features, rename to `[tool.basedpyright]`:

```toml
# Before
[tool.pyright]
typeCheckingMode = "basic"

# After
[tool.basedpyright]
typeCheckingMode = "recommended"
```

### Default changes

| Setting | pyright default | basedpyright default |
|---------|----------------|---------------------|
| `typeCheckingMode` | `"basic"` | `"recommended"` |
| `failOnWarnings` | `false` | `true` |
| `pythonPlatform` | current OS | `"All"` |
| `enableTypeIgnoreComments` | `true` | `false` |
| `pythonPath` | system Python | auto-detect `.venv` |

### Steps

1. Replace `pyright` with `basedpyright` in your dependency
2. Rename `[tool.pyright]` to `[tool.basedpyright]` in `pyproject.toml` (optional but recommended)
3. Run `basedpyright --writebaseline` to capture existing errors
4. Commit the baseline file
5. Update CI to use `basedpyright` instead of `pyright`
6. Update editor extension to `detachhead.basedpyright`

### Config file compatibility

- `pyrightconfig.json` works unchanged
- `[tool.pyright]` section still works but `[tool.basedpyright]` is preferred
- `pyright: strict` and `pyright: ignore` comments work unchanged

## From mypy

### Key differences

| Feature | mypy | basedpyright |
|---------|------|--------------|
| Engine | Python | TypeScript (Node bundled) |
| Config | `mypy.ini`, `pyproject.toml` | `pyrightconfig.json`, `pyproject.toml` |
| Strictness | Opt-in via flags | `"recommended"` mode by default |
| Baseline | No native support | Built-in baseline |
| LSP | mypy-based servers | Built-in language server |
| Performance | Slower on large projects | Fast, parallel with `--threads` |
| `Any` handling | `--disallow-any-*` flags | `reportAny`, `reportExplicitAny` |
| Ignore comments | `# type: ignore` | `# pyright: ignore[rule]` (safer) |

### Config mapping

```toml
# mypy (pyproject.toml)
[tool.mypy]
python_version = "3.11"
strict = true
disallow_untyped_defs = true
disallow_any_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true

# basedpyright equivalent
[tool.basedpyright]
pythonVersion = "3.11"
typeCheckingMode = "recommended"
reportAny = "warning"
reportExplicitAny = "warning"
reportIgnoreCommentWithoutRule = "error"
```

### Steps

1. Install basedpyright: `pip install basedpyright`
2. Create `[tool.basedpyright]` section (see mapping above)
3. Replace `# type: ignore` with `# pyright: ignore[rule]`
4. Run `basedpyright --writebaseline` to capture existing errors
5. Commit baseline
6. Update CI/editor config

### Type system differences

- **basedpyright uses `Unknown`** — distinguishes `Any` from untyped code vs explicit `Any`
- **`Protocol` support** — both support structural subtyping
- **TypedDict** — both support, basedpyright has stricter checking
- **Type narrowing** — basedpyright has `strictGenericNarrowing` for tighter generic narrowing
- **`@override`** — basedpyright has `reportImplicitOverride` rule

## From basic mode

If you're already using pyright/basedpyright in `"basic"` mode and want to adopt
stricter checking:

1. Set `typeCheckingMode = "recommended"` in config
2. Run `basedpyright --writebaseline`
3. Commit baseline
4. New code is checked strictly; old code errors are baselined
5. Over time, fix old code and baseline auto-updates

## Switching type checking modes

| From | To | Notes |
|------|-----|-------|
| `"off"` | `"recommended"` | Biggest jump. Use baseline. |
| `"basic"` | `"recommended"` | Moderate change. Many new warnings. |
| `"standard"` | `"recommended"` | Smaller change. Some new rules. |
| `"recommended"` | `"all"` | Warnings become errors. |
| `"all"` | `"recommended"` | Errors become warnings. |

When switching to a stricter mode, always use `--writebaseline` first to capture
the current error state.

# Migration Guides

## From Flake8

Ruff is designed as a drop-in replacement for Flake8 with common plugins.

### Mapping Flake8 plugins to Ruff rule codes

| Flake8 Plugin | Ruff Prefix |
|---------------|-------------|
| Pyflakes | `F` |
| pycodestyle (errors) | `E` |
| pycodestyle (warnings) | `W` |
| flake8-bugbear | `B` |
| flake8-comprehensions | `C4` |
| flake8-return | `RET` |
| flake8-simplify | `SIM` |
| flake8-print | `T20` |
| flake8-quotes | `Q` |
| flake8-annotations | `ANN` |
| flake8-bandit | `S` |
| flake8-pytest-style | `PT` |
| flake8-pyi | `PYI` |
| flake8-django | `DJ` |
| flake8-errmsg | `EM` |
| flake8-no-pep420 | `INP` |
| flake8-pie | `PIE` |
| flake8-raise | `RSE` |
| flake8-self | `SLF` |
| flake8-slots | `SLOT` |
| flake8-super | `UP038` (in pyupgrade) |
| flake8-tidy-imports | `TID` |
| flake8-type-checking | `TCH` |
| flake8-use-pathlib | `PTH` |
| mccabe | `C90` |
| pep8-naming | `N` |
| pyupgrade | `UP` |
| pydocstyle | `D` |
| eradicate | `ERA` |
| flynt | `FLY` |
| tryceratops | `TRY` |
| pandas-vet | `PD` |
| perflint | `PERF` |
| refurb | `FURB` |

### Step-by-step migration

1. **Install Ruff**: `pip install ruff`

2. **Run with defaults** to see what catches:
   ```bash
   ruff check .
   ```

3. **Enable equivalent rules** from your Flake8 config:
   ```toml
   [tool.ruff.lint]
   select = ["E", "F", "W", "B", "C4", "SIM", "UP", "I", "N"]
   ```

4. **Map `per-file-ignores`** from Flake8's `per-file-ignores`:
   ```toml
   [tool.ruff.lint.per-file-ignores]
   "__init__.py" = ["E402", "F401"]
   ```

5. **Remove Flake8** from your toolchain once Ruff passes on all files.

### What Ruff does not replace

- Custom Flake8 plugins (Ruff does not support third-party plugins)
- Some niche Flake8 plugins not yet re-implemented
- Flake8's `--max-line-length` on a per-file basis (use `per-file-ignores` + `E501`)

## From Black

Ruff's formatter is designed as a near-drop-in replacement for Black.

### Compatibility

- >99.9% of lines formatted identically on Black-formatted codebases
- Same default line length (88)
- Same quote normalization (double quotes by default)
- Same magic trailing comma behavior

### Known deviations

- **Trailing comments**: Ruff expands statements with trailing comments instead of
  collapsing them (preserves comment proximity)
- **Pragma comments**: Ruff ignores pragma comments (`# type`, `# noqa`, `# pyright`)
  when computing line width
- **Line width**: Ruff uses Unicode width for all tokens; Black uses character width
  for non-string tokens

### Migration steps

1. **Format with Ruff**: `ruff format .`

2. **Review diff**: Most changes should be minimal on Black-formatted code

3. **Replace Black in toolchain** with `ruff format`

4. **Remove Black** from dependencies and pre-commit hooks

### Config parity

| Black Setting | Ruff Equivalent |
|---------------|-----------------|
| `line-length` | `line-length` |
| `target-version` | `target-version` |
| `skip-string-normalization` | `preview` (partial) |
| `skip-magic-trailing-comma` | `skip-magic-trailing-comma` |
| `preview` | `--preview` / `preview` |
| `pyi` mode | Not needed (auto-detected) |
| `fast` | Not needed (no AST safety check) |

## From isort

Ruff's `I` rules replace isort entirely.

### Config mapping

| isort Setting | Ruff Equivalent |
|---------------|-----------------|
| `profile` | `target-version` + rule selection |
| `known_first_party` | `lint.isort.known-first-party` |
| `known_third_party` | `lint.isort.known-third-party` |
| `sections` | `lint.isort.section-order` |
| `no_lines_before` | `lint.isort.no-lines-before` |
| `force_sort_within_sections` | Not directly supported |
| `combine_as_imports` | `lint.isort.combine-as-imports` |

### Migration

1. Enable `I` rules: `extend-select = ["I"]`
2. Set `src = ["src"]` if using a src layout
3. Run `ruff check --fix` to auto-sort imports
4. Remove isort from toolchain

## From Pylint

Ruff's `PL` rules cover a subset of Pylint. Full Pylint replacement is not possible
due to Pylint's deeper type inference.

### Coverage

Ruff implements 209+ Pylint rules across `PLC`, `PLE`, `PLR`, `PLW`, `PLN` prefixes.

### Migration approach

1. Enable `PL` rules gradually: `extend-select = ["PL"]`
2. Use `per-file-ignores` for rules too strict for your project
3. Keep Pylint alongside Ruff initially for rules Ruff doesn't cover
4. Consider using a type checker (mypy, pyright) alongside Ruff

## From pyupgrade

Ruff's `UP` rules replace pyupgrade.

### Migration

1. Enable `UP` rules: `extend-select = ["UP"]`
2. Set `target-version` to match your minimum Python version
3. Run `ruff check --fix` to apply upgrades
4. Remove pyupgrade from toolchain

## Consolidated toolchain

A typical post-migration setup:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "B", "C4", "SIM", "UP", "I", "N", "ANN", "PT"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]
"tests/**" = ["S101"]
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

This replaces: Flake8 + plugins, Black, isort, pyupgrade, autoflake, pydocstyle.

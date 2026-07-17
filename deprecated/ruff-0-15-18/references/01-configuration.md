# Configuration

## Config File Formats

Ruff supports three config file formats, all using equivalent schemas:

| File | Section prefix | Use case |
|---|---|---|
| `pyproject.toml` | `[tool.ruff]` | Project-wide config alongside other tool settings |
| `ruff.toml` | none (top-level) | Dedicated ruff config |
| `.ruff.toml` | none (top-level) | Local/ignored ruff config (highest precedence) |

### Precedence

When multiple config files exist in the same directory: `.ruff.toml` > `ruff.toml` > `pyproject.toml`.

## Config File Discovery

Ruff searches upward from each analyzed file's directory for the nearest config file. The closest match wins — settings are **not** merged across levels. Use `extend` to inherit from a parent config.

### Discovery rules

1. Ruff ignores `pyproject.toml` files lacking `[tool.ruff]`.
2. `--config path` applies to all files; relative paths resolve from CWD.
3. If no config file is found, Ruff falls back to defaults (or user-level config at `${config_dir}/ruff/pyproject.toml`).
4. CLI flags override all config file settings.

### Extending a parent config

```toml
[tool.ruff]
extend = "../pyproject.toml"
line-length = 100
```

## Top-Level Settings

| Setting | Default | Description |
|---|---|---|
| `line-length` | 88 | Line length limit for lint and format |
| `indent-width` | 4 | Number of spaces per indent level |
| `target-version` | inferred from `requires-python` | Minimum Python version (`py37`–`py315`) |
| `exclude` | standard dirs (`.git`, `.venv`, etc.) | Glob patterns to exclude |
| `extend-exclude` | `[]` | Additional excludes on top of defaults |
| `extend-include` | `[]` | Additional file patterns to include |
| `include` | `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml` | File patterns to include |
| `respect-gitignore` | `true` | Skip files in `.gitignore` |
| `force-exclude` | `false` | Apply excludes even for directly-passed files |
| `preview` | `false` | Enable preview features globally |
| `required-version` | none | Require specific ruff version |
| `cache-dir` | `.ruff_cache` | Custom cache directory |
| `builtins` | `[]` | List of builtin names for the linter |
| `namespace-packages` | `false` | Enable namespace package support |
| `src` | `["."]` | Source roots for first-party import detection |
| `per-file-target-version` | `{}` | Override target-version per file glob |

### Example

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]
respect-gitignore = true
```

## Lint Settings (`[tool.ruff.lint]`)

### Rule selection

| Setting | Description |
|---|---|
| `select` | Explicit rule set (replaces defaults) |
| `extend-select` | Add rules on top of defaults or parent `select` |
| `ignore` | Disable specific rules |
| `extend-ignore` | Add ignores on top of inherited `ignore` |
| `fixable` | Rules that can be auto-fixed (default: `["ALL"]`) |
| `unfixable` | Rules to exclude from auto-fix |
| `preview` | Enable preview lint rules |

### Per-file ignores

```toml
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]
"tests/**/*.py" = ["S101", "T201"]
```

### Plugin-specific settings

Plugin configurations live as subsections:

```toml
[tool.ruff.lint.flake8-quotes]
docstring-quotes = "double"
inline-quotes = "single"

[tool.ruff.lint.isort]
known-first-party = ["my_package"]
known-third-party = ["requests"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.pycodestyle]
max-line-length = 120
```

Use `ruff config` to list all available settings, and `ruff config <key>` to describe a specific option.

## Format Settings (`[tool.ruff.format]`)

| Setting | Default | Description |
|---|---|---|
| `quote-style` | `"double"` | `"double"`, `"single"`, or `"preserve"` |
| `indent-style` | `"space"` | `"space"` or `"tab"` |
| `skip-magic-trailing-comma` | `false` | Respect magic trailing commas like Black |
| `line-ending` | `"auto"` | `"auto"`, `"lf"`, `"crlf"`, or `"cr"` |
| `docstring-code-format` | `false` | Format code examples in docstrings |
| `docstring-code-line-length` | `"dynamic"` | Line length for docstring code snippets |
| `preview` | inherited from top-level | Enable preview formatting |

### Example

```toml
[tool.ruff.format]
quote-style = "single"
indent-style = "space"
docstring-code-format = true
```

## Analyze Settings (`[tool.ruff.analyze]`)

Settings for `ruff analyze graph`:

| Setting | Default | Description |
|---|---|---|
| `type-checking.imports` | `[]` | Modules to treat as type-checking imports |

## CLI Overrides

Individual settings can be overridden from the command line:

```bash
# Override a single setting
ruff check --config "lint.line-length = 100"
ruff format --config "format.quote-style = 'single'"

# Ignore all config files
ruff check --isolated
```

Environment variables:

| Variable | Description |
|---|---|
| `RUFF_OUTPUT_FORMAT` | Default output format |
| `RUFF_OUTPUT_FILE` | Default output file path |
| `RUFF_NO_CACHE` | Disable cache reads |
| `RUFF_CACHE_DIR` | Custom cache directory |

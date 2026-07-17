# Configuration Reference

## Config file formats

Ruff supports three config file formats. All are searched from the target file's
directory up to the repo root (`.git` boundary). The closest config wins.

### pyproject.toml

Settings go under `[tool.ruff]`:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
src = ["src"]
exclude = ["migrations/", "vendor/"]

[tool.ruff.lint]
select = ["E", "F", "B", "UP", "I"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### ruff.toml

Same settings, no `[tool.ruff]` prefix:

```toml
line-length = 88
target-version = "py311"

[lint]
select = ["E", "F", "B", "UP", "I"]

[format]
quote-style = "double"
```

### .ruff.toml

Identical to `ruff.toml` but hidden (dotfile). Useful for keeping config out of
directory listings.

## Top-level settings

| Setting | Default | Description |
|---------|---------|-------------|
| `line-length` | `88` | Max line length (shared by linter and formatter) |
| `indent-width` | `4` | Number of spaces per indentation level |
| `target-version` | `"py38"` | Minimum Python version (`py37`, `py38`, ..., `py313`) |
| `exclude` | *(see defaults)* | Directories/files to exclude |
| `extend` | `""` | Path to parent config to inherit from |
| `src` | `["."]` | Source directories for first-party import detection |
| `builtins` | `[]` | Additional builtin names |
| `namespace-packages` | `[]` | Treat these paths as namespace packages |
| `respect-gitignore` | `true` | Respect `.gitignore` files |
| `fix` | `false` | Apply fixes (equivalent to `--fix`) |
| `show-fixes` | `false` | Show violations with available fixes |

## Lint settings (`[lint]` / `[tool.ruff.lint]`)

| Setting | Default | Description |
|---------|---------|-------------|
| `select` | `["E4", "E7", "E9", "F"]` | Rule codes to enable |
| `ignore` | `[]` | Rule codes to ignore |
| `extend-select` | `[]` | Additional rules on top of `select` |
| `fixable` | `["ALL"]` | Rules that can be auto-fixed |
| `unfixable` | `[]` | Rules that should not be auto-fixed |
| `external` | `[]` | External rule codes to allow with `# noqa` |
| `dummy-variable-rgx` | `^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$` | Regex for allowed dummy variables |
| `explicit-string-rules` | `false` | Apply string rules to explicit strings |
| `ignore-init-module-imports` | `false` | Ignore unused import errors in `__init__.py` |
| `logger-objects` | `[]` | Additional logger object names |
| `task-tags` | `["TODO", "FIXME", "XXX"]` | Tags recognized as task comments |

## Format settings (`[format]` / `[tool.ruff.format]`)

| Setting | Default | Description |
|---------|---------|-------------|
| `quote-style` | `"double"` | `"double"` or `"single"` |
| `indent-style` | `"space"` | `"space"` or `"tab"` |
| `skip-magic-trailing-comma` | `false` | Whether to respect magic trailing commas |
| `line-ending` | `"auto"` | `"auto"`, `"lf"`, `"cr"`, `"crlf"` |
| `docstring-code-format` | `false` | Format code examples in docstrings |
| `docstring-code-line-length` | `"dynamic"` | Line length for docstring code (`"dynamic"` or integer) |

## Plugin-specific settings

### pydocstyle (`[lint.pydocstyle]`)

```toml
[tool.ruff.lint.pydocstyle]
convention = "google"       # "google", "numpy", or "pep257"
ignore-decorators = []       # Decorators that suppress docstring requirements
property-decorators = ["property"]
```

### isort (`[lint.isort]`)

```toml
[tool.ruff.lint.isort]
known-first-party = ["my_package"]
known-third-party = []
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
no-lines-before = []
forced-separate = []
combine-as-imports = false
split-on-trailing-comma = true
relative-imports-order = "closest-to-furthest"
extra-standard-library = []
```

### flake8-quotes (`[lint.flake8-quotes]`)

```toml
[tool.ruff.lint.flake8-quotes]
docstring-quotes = "double"
inline-quotes = "double"
multiline-quotes = "double"
```

### flake8-bugbear (`[lint.flake8-bugbear]`)

```toml
[tool.ruff.lint.flake8-bugbear]
# B008: Allow function calls in default arguments
extend-immutable-calls = ["fastapi.Query", "fastapi.Path"]
```

### flake8-errmsg (`[lint.flake8-errmsg]`)

```toml
[tool.ruff.lint.flake8-errmsg]
max-string-length = 79
```

### flake8-import-conventions (`[lint.flake8-import-conventions]`)

```toml
[tool.ruff.lint.flake8-import-conventions.assigned]
numpy = "np"
pandas = "pd"

[tool.ruff.lint.flake8-import-conventions.banned]
"*" = "Wildcard imports are banned"
```

### flake8-annotations (`[lint.flake8-annotations]`)

```toml
[tool.ruff.lint.flake8-annotations]
allow-star-arg-any = false
ignore-fully-untyped = false
mypy-init-return-value = true
suppress-dummy-args = true
suppress-none-returning = true
```

### flake8-comprehensions (`[lint.flake8-comprehensions]`)

```toml
[tool.ruff.lint.flake8-comprehensions]
allow-dict-calls-with-kwargs = false
```

### flake8-pytest-style (`[lint.flake8-pytest-style]`)

```toml
[tool.ruff.lint.flake8-pytest-style]
fixture-parentheses = true
mark-parentheses = true
parametrize-names-type = "csv"
parametrize-values-type = "list"
parametrize-values-row-type = "tuple"
```

## Per-file ignores

```toml
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]
"tests/**" = ["S101"]
"scripts/**" = ["T201"]
"migrations/**" = ["ALL"]
```

Glob patterns use `globset` syntax. `**` matches across directory boundaries.

## Extending configs

```toml
# Child config
extend = "../ruff.toml"

# Override specific settings
line-length = 100

[lint]
extend-select = ["B"]
```

The `extend` field loads and merges settings from another config file. Relative
paths are resolved relative to the config file containing the `extend` directive.

## Cache

Ruff caches analysis results to avoid re-checking unchanged files.

| Setting | Description |
|---------|-------------|
| `--no-cache` | Disable caching |
| `RUFF_CACHE_DIR` | Override cache directory |
| `--cache-dir <path>` | Set cache directory via CLI |

Default cache location: `.ruff_cache` in the project root.

## Viewing resolved settings

```bash
ruff check --show-settings path/to/file.py
ruff format --show-settings path/to/file.py
```

This shows the fully resolved configuration for a specific file, including
inherited settings and applied overrides.

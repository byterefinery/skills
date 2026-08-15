# Configuration

## Config File Formats

Ruff reads three config file types (same schema, different section prefixes):

| File | Section prefix |
|------|---------------|
| `pyproject.toml` | `[tool.ruff]` |
| `ruff.toml` | none |
| `.ruff.toml` | none |

Priority when multiple files exist in the same directory: `.ruff.toml` > `ruff.toml` > `pyproject.toml`.

## Config File Discovery

Ruff walks up the directory tree from each source file, finding the nearest config file. The closest config wins entirely — settings are not merged across files.

Exceptions:
1. `pyproject.toml` files without `[tool.ruff]` are skipped
2. `--config path/to/ruff.toml` applies to all files; relative paths resolve from current working directory
3. If no config is found, Ruff checks `${config_dir}/ruff/pyproject.toml` (user-level config)
4. CLI flags override all config files

### Extending configs

Use `extend` to inherit from another config file:

```toml
extend = "../ruff.toml"
line-length = 100
```

The project root is the directory containing the config file (not the extended file).

## Default Configuration

When no config is found, Ruff uses these defaults:

```toml
exclude = [".git", ".venv", "node_modules", "build", "dist", ...]
line-length = 88
indent-width = 4
target-version = "py310"

[lint]
# F, E, B, UP, RUF rules enabled (see default-rules docs for full list)
ignore = []
fixable = ["ALL"]
unfixable = []
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = false
docstring-code-line-length = "dynamic"
```

## Target Version

```toml
target-version = "py310"  # py37, py38, py39, py310, py311, py312, py313, py314, py315
```

Controls which lint rules and formatter behaviors apply. When omitted, Ruff infers from `requires-python` in `pyproject.toml`.

Inference rules:
1. `--config` provided: no inference
2. Config found in hierarchy: infer from `requires-python` in same-directory `pyproject.toml`
3. User-level config: infer from first `pyproject.toml` in ancestor of working directory
4. No config: infer from first `pyproject.toml` in ancestor of working directory

## File Discovery

Default file patterns: `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`. In preview mode, also `*.pyw`.

```toml
include = ["src/**/*.py", "scripts/**/*.py"]
extend-include = ["*.ipy"]           # add to defaults
extend-exclude = ["vendor/", "*.ipynb"]  # add to default excludes
respect-gitignore = true             # skip files in .gitignore
```

### Extension mappings

```toml
extension = { ipy = "ipynb", pyw = "python" }
```

In preview mode, map `.mdx`/`.qmd` as markdown for code block formatting:

```toml
extension = { mdx = "markdown", qmd = "markdown" }
```

## Source Directories

```toml
src = ["src"]  # first-party import detection
```

Default: project root + `src/`. For non-standard layouts, set explicitly.

When extending configs from subdirectories:

```toml
# tests/ruff.toml
extend = "../ruff.toml"
src = ["../src"]
```

## CLI Overrides

### Dedicated flags

Some settings have dedicated CLI flags:

```bash
ruff check --select E,F --ignore E501 --target-version py310 --line-length 100
```

### `--config` key-value pairs

Override individual settings without a config file:

```bash
ruff check --config "lint.dummy-variable-rgx = '__.*'"
ruff check --config "lint.per-file-ignores = {'some_file.py' = ['F841']}"
ruff format --config "format.quote-style = 'single'"
```

Linter settings need `lint.` prefix; formatter settings need `format.` prefix.

Dedicated flags take priority over `--config` for the same setting:

```bash
ruff format --line-length=90 --config "line-length=100"  # uses 90
```

### `--isolated`

Ignore all configuration files entirely:

```bash
ruff check --isolated
```

### Argfiles

Read arguments from a file (useful for long file lists):

```bash
ruff check @args.txt
```

`args.txt`:
```
--select
F401
--quiet
path/to/code1/
path/to/code2/
```

## Environment Variables

- `RUFF_OUTPUT_FORMAT` — default output format
- `RUFF_OUTPUT_FILE` — default output file
- `RUFF_NO_CACHE` — disable cache reads
- `RUFF_CACHE_DIR` — custom cache directory

## Preview Mode

Preview enables unstable features. Configurable independently for lint and format:

```toml
[lint]
preview = true

[format]
preview = true
```

Or via CLI: `ruff check --preview`, `ruff format --preview`.

Preview rules require preview mode to be active — selecting the rule code alone does not enable it.

```toml
[lint]
preview = true
explicit-preview-rules = true  # opt into each preview rule individually
```

## Debugging Configuration

```bash
ruff check path/to/file.py --show-files     # list discovered files
ruff check path/to/file.py --show-settings  # show resolved settings
ruff config line-length                     # describe a config option
ruff linter                                 # list upstream linters
```

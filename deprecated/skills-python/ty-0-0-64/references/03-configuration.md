# Configuration Reference

## Configuration file discovery

ty searches for config in this order:
1. `ty.toml` in current directory (or nearest parent)
2. `pyproject.toml` with `[tool.ty]` section
3. User-level: `~/.config/ty/ty.toml` (Linux/macOS) or `%APPDATA%\ty\ty.toml` (Windows)

`ty.toml` takes precedence over `pyproject.toml` in the same directory. CLI flags override all files.

## Full configuration schema

### `[rules]`

Dict mapping rule names to severity (`"ignore"`, `"warn"`, `"error"`). Key `"all"` sets default for all rules.

```toml
[rules]
possibly-unresolved-reference = "warn"
division-by-zero = "ignore"
```

### `[analysis]`

#### `allowed-unresolved-imports`
List of module glob patterns to suppress `unresolved-import` for.

```toml
[analysis]
allowed-unresolved-imports = ["test.**", "!test.foo"]
```

Glob patterns: `*` matches within component, `**` matches any components, `!` prefix excludes.

#### `replace-imports-with-any`
Module globs whose imports are replaced with `typing.Any` (even if resolvable).

```toml
[analysis]
replace-imports-with-any = ["pandas.**", "numpy.**"]
```

#### `respect-type-ignore-comments`
Whether to honor `type: ignore` comments. Default: `true`. Set to `false` when using ty alongside other checkers.

```toml
[analysis]
respect-type-ignore-comments = false
```

#### `strict-equality-semantics`
Conservative equality narrowing. Default: `false`. Prevents narrowing `str` to `Literal["a"]` after `x == "a"`.

```toml
[analysis]
strict-equality-semantics = true
```

### `[environment]`

#### `extra-paths`
Additional module resolution paths (like `MYPYPATH`).

```toml
[environment]
extra-paths = ["./shared/my-search-path"]
```

#### `python`
Explicit Python environment path.

```toml
[environment]
python = "./.venv"
```

#### `root`
First-party module roots. Auto-detects `src/`, `python/`, and `<project>/<project>/`.

```toml
[environment]
root = ["./app"]
```

#### `python-version`
Target Python version: `3.7` through `3.15`.

```toml
[environment]
python-version = "3.11"
```

#### `python-platform`
Target platform: `linux`, `darwin`, `win32`, or `all`.

```toml
[environment]
python-platform = "linux"
```

### `[src]`

#### `include`
Files/directories to check (gitignore-like globs).

```toml
[src]
include = ["src", "tests"]
```

#### `exclude`
Files/directories to exclude. Default exclusions include `.git/`, `.venv/`, `node_modules/`, `__pycache__/`, etc.

```toml
[src]
exclude = ["generated", "*.proto", "tests/fixtures/**", "!tests/fixtures/important.py"]
```

Use `!pattern` to negate (re-include).

#### `exclude-scripts`
Exclude PEP 723 inline script files unless passed explicitly. Default: `false`.

```toml
[src]
exclude-scripts = true
```

#### `respect-ignore-files`
Exclude files listed in `.gitignore`/`.ignore`. Default: `true`.

```toml
[src]
respect-ignore-files = false
```

### `[terminal]`

#### `error-on-warning`
Exit code 1 on warnings. Default: `true`.

```toml
[terminal]
error-on-warning = false
```

#### `output-format`
Output format: `full`, `concise`, `github`, `gitlab`, `junit`. Default: `full`.

```toml
[terminal]
output-format = "concise"
```

## Overrides

Per-path configuration overrides:

```toml
[[overrides]]
path = "tests/**"

[overrides.rules]
possibly-missing-attribute = "ignore"

[overrides.analysis]
allowed-unresolved-imports = ["test_fixtures.**"]
```

## CLI overrides

```bash
ty check --config 'python-version = "3.11"'
ty check --config-file ./custom-ty.toml
```

`--config` takes a TOML `KEY = VALUE` pair and overrides all files.

## Environment variables

| Variable | Description |
|----------|-------------|
| `TY_CONFIG_FILE` | Path to `ty.toml` config file |
| `TY_OUTPUT_FORMAT` | Output format (same as `--output-format`) |
| `PYTHONPATH` | Additional module search paths |
| `VIRTUAL_ENV` | Active virtual environment path |

## `pyproject.toml` format

All settings nest under `[tool.ty]`:

```toml
[tool.ty.rules]
missing-type-argument = "error"

[tool.ty.analysis]
allowed-unresolved-imports = ["test.**"]

[tool.ty.environment]
extra-paths = ["./shared"]

[tool.ty.src]
include = ["src", "tests"]
exclude = ["src/generated"]

[tool.ty.terminal]
error-on-warning = false
```

# Configuration Reference

## Config File Discovery

ty searches for configuration in this order:
1. `ty.toml` in current directory or nearest parent (takes precedence)
2. `[tool.ty]` section in `pyproject.toml`
3. User-level `~/.config/ty/ty.toml` (Linux/macOS), `$XDG_CONFIG_HOME/ty/ty.toml`, or `%APPDATA%\ty\ty.toml` (Windows)

Project config overrides user config. CLI flags override all files.

## `ty.toml` vs `pyproject.toml`

If both `ty.toml` and `pyproject.toml` exist in the same directory, only `ty.toml` is read. The `[tool.ty]` section in `pyproject.toml` is ignored.

In `ty.toml`, settings are at the root level. In `pyproject.toml`, they go under `[tool.ty]`.

## Settings Reference

### `[rules]`

Map of rule names to severities: `"error"`, `"warn"`, or `"ignore"`. Use key `all` for global default.

```toml
[rules]
all = "warn"
possibly-unresolved-reference = "ignore"
redundant-cast = "ignore"
```

### `[analysis]`

**`allowed-unresolved-imports`** — List of module glob patterns to suppress `unresolved-import`. Use `!` prefix to negate.

```toml
[analysis]
allowed-unresolved-imports = ["test.**", "!test.foo"]
```

Glob syntax: `*` matches within a component, `**` matches any number of components.

**`replace-imports-with-any`** — Replace module types with `typing.Any` unconditionally.

```toml
[analysis]
replace-imports-with-any = ["pandas.**", "numpy.**"]
```

**`respect-type-ignore-comments`** — Whether standard `type: ignore` comments suppress ty errors. Default: `true`.

### `[environment]`

**`python-version`** — Target Python version string (`"3.7"` through `"3.15"`). Affects syntax validation and stdlib types. Default: inferred from `requires-python`, then venv metadata, then `"3.14"`.

**`python-platform`** — Target platform: `"win32"`, `"darwin"`, `"linux"`, `"android"`, `"ios"`, or `"all"`. Affects `sys.platform`-conditional types. Default: current platform.

**`python`** — Path to Python interpreter, venv directory, or `sys.prefix`. Used for third-party module resolution.

**`extra-paths`** — Additional module search paths (like mypy's `MYPYPATH`).

**`root`** — List of directories for first-party module discovery. Default detection includes `.`, `./src`, `./python`, and `./<project-name>` if applicable.

**`typeshed`** — Custom typeshed directory path for stdlib stubs.

### `[src]`

**`include`** — Glob patterns for files to check. Default: all Python files in project.

**`exclude`** — Gitignore-style globs to exclude. Default excludes: `.git`, `node_modules`, `.venv`, `__pycache__`, `.mypy_cache`, `.tox`, `dist`, `build`, etc. Use `!"pattern"` to re-include.

**`respect-ignore-files`** — Respect `.gitignore` and `.ignore` files. Default: `true`.

### `[terminal]`

**`output-format`** — Output format: `"full"`, `"concise"`, `"github"`, `"gitlab"`, `"junit"`. Default: `"full"`.

**`error-on-warning`** — Exit 1 if any warnings exist. Default: `false`.

### `[[overrides]]`

Per-glob configuration overrides. Multiple overrides can match the same file; later entries take precedence.

```toml
[[overrides]]
include = ["tests/**"]
exclude = ["tests/fixtures/**"]

[overrides.rules]
possibly-unresolved-reference = "ignore"

[overrides.analysis]
allowed-unresolved-imports = ["mock.**"]
```

Each override supports: `include`, `exclude`, `rules`, and nested `analysis` settings.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TY_CONFIG_FILE` | Path to a `ty.toml` config file |
| `TY_OUTPUT_FORMAT` | Default output format |
| `VIRTUAL_ENV` | Virtual environment path (auto-detected) |

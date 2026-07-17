# Configuration Reference

## File discovery

ty searches for configuration files from the current directory upward:

1. `ty.toml` — dedicated config, takes precedence over `pyproject.toml`
2. `pyproject.toml` — reads `[tool.ty]` section only
3. User-level: `~/.config/ty/ty.toml` (Unix) or `%APPDATA%\ty\ty.toml` (Windows)

When `ty.toml` and `pyproject.toml` both exist in the same directory, only `ty.toml`
is read. The `[tool.ty]` section in `pyproject.toml` is ignored.

Project-level settings override user-level settings. Arrays are merged (project values
appear later); scalars are replaced entirely.

CLI flags take precedence over all config files.

## `[rules]`

Map of rule names to severity levels (`"ignore"`, `"warn"`, `"error"`). Use `"all"` to
set a default for all rules.

```toml
[rules]
all = "error"
division-by-zero = "ignore"
possibly-unresolved-reference = "warn"
```

## `[analysis]`

### `allowed-unresolved-imports`

Glob patterns for modules whose `unresolved-import` diagnostics should be suppressed.

```toml
[analysis]
allowed-unresolved-imports = ["test.**", "!test.foo"]
```

Glob syntax: `*` matches within a component, `**` matches any components, `!` negates.
Later entries take precedence.

### `replace-imports-with-any`

Replace imports of matching modules with `typing.Any`, even if the module is resolvable.
Import diagnostics are unconditionally suppressed.

```toml
[analysis]
replace-imports-with-any = ["pandas.**", "numpy.**"]
```

### `respect-type-ignore-comments`

Whether `type: ignore` comments suppress ty diagnostics. Default: `true`.

```toml
[analysis]
respect-type-ignore-comments = false
```

### `strict-literal-narrowing`

When `true`, equality checks like `value == "a"` do not narrow `str` to `Literal["a"]`.
Prevents unsound narrowing for subclasses of builtins (e.g., `StrEnum`, `IntEnum`).
Default: `false`.

```toml
[analysis]
strict-literal-narrowing = true
```

## `[environment]`

### `python`

Path to Python interpreter, virtual environment directory, or `sys.prefix`.

```toml
[environment]
python = "./.venv"
# or
python = "./.venv/bin/python3"
# or
python = "/usr"
```

### `python-version`

Target Python version: `"3.7"` through `"3.15"`. Affects allowed syntax and stdlib
type definitions. Default: inferred from `requires-python`, then environment, then `3.14`.

```toml
[environment]
python-version = "3.12"
```

### `python-platform`

Target platform: `"win32"`, `"darwin"`, `"linux"`, `"android"`, `"ios"`, `"all"`.
Affects `sys.platform`-based reachability and platform-specific stdlib types.

```toml
[environment]
python-platform = "linux"
```

### `root`

List of directories for first-party module resolution (priority order).

```toml
[environment]
root = ["./src", "./lib"]
```

Auto-detected: `.`, `./src`, `./python`, `./<project-name>/<project-name>`.

### `extra-paths`

Additional module search paths, placed before `site-packages`. Similar to mypy's
`MYPYPATH`.

```toml
[environment]
extra-paths = ["./shared/stubs"]
```

### `typeshed`

Path to a custom typeshed directory. Falls back to bundled stubs.

```toml
[environment]
typeshed = "/path/to/typeshed"
```

## `[src]`

### `include`

Files/directories to check. Gitignore-like glob syntax, anchored to project root.
Default: all Python files in project.

```toml
[src]
include = ["src", "tests"]
```

### `exclude`

Files/directories to skip. Default exclusions include `.venv/`, `node_modules/`,
`.git/`, `__pycache__/`, `dist/`, etc.

```toml
[src]
exclude = ["generated/", "*.proto", "!generated/important.py"]
```

### `respect-ignore-files`

Exclude files listed in `.gitignore`, `.ignore`, etc. Default: `true`.

```toml
[src]
respect-ignore-files = false
```

## `[terminal]`

### `output-format`

Diagnostic output format: `"full"`, `"concise"`, `"github"`, `"gitlab"`, `"junit"`.
Default: `"full"`.

```toml
[terminal]
output-format = "concise"
```

### `error-on-warning`

Exit with code 1 even if all diagnostics are warnings. Default: `true`.

```toml
[terminal]
error-on-warning = false
```

## `[[overrides]]`

Per-file rule overrides using glob patterns. Later overrides take precedence.

```toml
[[overrides]]
include = ["tests/**", "**/test_*.py"]

[overrides.rules]
possibly-unresolved-reference = "ignore"
possibly-missing-attribute = "warn"

[[overrides]]
include = ["generated/**"]
exclude = ["generated/important.py"]

[overrides.rules]
all = "ignore"
```

Overrides can also include `analysis` settings:

```toml
[[overrides]]
include = ["src/legacy/**"]

[overrides.analysis]
allowed-unresolved-imports = ["old_lib.**"]
strict-literal-narrowing = true
```

## CLI config override

```bash
ty check --config 'rules.possibly-unresolved-reference = "warn"'
ty check --config-file /path/to/ty.toml
```

## Deprecated settings

- `src.root` — use `environment.root` instead

## Full config example

```toml
# ty.toml
[rules]
all = "error"
division-by-zero = "ignore"
blanket-ignore-comment = "warn"
possibly-unresolved-reference = "warn"
missing-type-argument = "error"

[analysis]
allowed-unresolved-imports = ["test.**"]
replace-imports-with-any = []
respect-type-ignore-comments = true
strict-literal-narrowing = false

[environment]
python-version = "3.12"
python = "./.venv"
python-platform = "linux"
root = ["./src"]
extra-paths = []

[src]
include = ["src", "tests"]
exclude = ["generated/", "migrations/"]
respect-ignore-files = true

[terminal]
output-format = "full"
error-on-warning = true

[[overrides]]
include = ["tests/**"]

[overrides.rules]
possibly-unresolved-reference = "ignore"
possibly-missing-attribute = "warn"
```

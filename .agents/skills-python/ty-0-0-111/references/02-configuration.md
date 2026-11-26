# Configuration (ty 0.0.111)

Source: `docs/configuration.md` and `docs/reference/configuration.md` in the ty repository at tag 0.0.111 (https://github.com/astral-sh/ty/tree/0.0.111).

- [Configuration files and precedence](#configuration-files-and-precedence)
- [Top-level options](#top-level-options)
- [analysis](#analysis)
- [environment](#environment)
- [overrides](#overrides)
- [project-manager](#project-manager)
- [src](#src)
- [terminal](#terminal)

## Configuration files and precedence

- Project config: `[tool.ty]` table in `pyproject.toml`, or a `ty.toml` file with the identical structure minus the `[tool.ty]` prefix. Searched in the current directory and up the directory tree. If a `pyproject.toml` has no `[tool.ty]` table, ty may still read `project.name` and `project.requires-python` from it, then continues searching for ty-specific configuration.
- **`ty.toml` takes precedence over `pyproject.toml`** — if both are present in a directory, only `ty.toml` is read; the `[tool.ty]` section is ignored.
- User-level config: `~/.config/ty/ty.toml` (or `$XDG_CONFIG_HOME/ty/ty.toml`) on macOS/Linux, `%APPDATA%\ty\ty.toml` on Windows; must use `ty.toml` format. Project and user settings merge, with project-level values winning; arrays merge with project entries appended.
- Command-line settings take precedence over persistent configuration; `--config KEY=VALUE` overrides beat all configuration files.

## Top-level options

| Option | Default | Type | Notes |
|---|---|---|---|
| `baseline` | `null` | `str` | Path to a JSON file recording existing diagnostics (preview; format may change). Relative paths resolve against the project root. Create/update with `ty check --update-baseline` |
| `rules` | `{...}` | `dict[RuleName \| "all", "ignore" \| "warn" \| "error"]` | Rule levels; `all` sets a default severity for all rules. By default ty exits 1 if it emits any warning or error |

```toml
# pyproject.toml                    # ty.toml
[tool.ty.rules]                     [rules]
division-by-zero = "ignore"         division-by-zero = "ignore"
possibly-unresolved-reference = "warn"
```

## analysis

| Option | Default | Type | Notes |
|---|---|---|---|
| `allowed-unresolved-imports` | `[]` | `list[str]` | Module glob patterns for which `import-not-found` and `missing-module-member` are suppressed. `*` matches characters except `.`; `**` matches any number of module components (`foo.**`); `!` prefix excludes. Later entries win |
| `replace-imports-with-any` | `[]` | `list[str]` | Module glob patterns whose imports are replaced with `typing.Any` **even if the module resolves**; import diagnostics unconditionally suppressed for matching modules. Same glob syntax, `!` prefix, later entries win |
| `respect-type-ignore-comments` | `true` | `bool` | When `false`, `# type: ignore` comments are treated as ordinary comments (use `# ty: ignore` instead) |
| `return-type-inference` | `"never"` | `"never" \| "always"` | When to infer return types for functions without an explicit annotation. `"always"` never overrides explicit annotations; lambdas are always inferred; generator/async return types are currently not inferred |
| `strict-equality-semantics` | `false` | `bool` | Stricter behavior for type inference and narrowing of equality comparisons |
| `strict-generic-narrowing` | `false` | `bool` | Stricter narrowing of generic types |

```toml
# pyproject.toml                    # ty.toml
[tool.ty.analysis]                  [analysis]
replace-imports-with-any = ["pandas.**", "numpy.**"]
```

## environment

| Option | Default | Type | Notes |
|---|---|---|---|
| `extra-paths` | `[]` | `list[str]` | Paths with first priority in module resolution (similar to mypy's `MYPYPATH`, pyright's `stubPath`). Advanced option for unconventional module locations |
| `python` | `null` | `str` | Path to interpreter (`.venv/bin/python3`), venv directory (`.venv`), or system `sys.prefix` (`/usr`). Otherwise discovery order: `VIRTUAL_ENV`, active non-`base` Conda/Pixi with Python, project-root `.venv`, active `base` Conda, `python3`/`python` on `PATH`. Scripts with inline metadata use their own environment |
| `python-platform` | `<current-platform>` | `"win32" \| "darwin" \| "android" \| "ios" \| "linux" \| "all" \| str` | Target platform; enables `sys.platform` conditionals. `all` assumes any platform |
| `python-version` | `"3.15"` | `"3.7"`–`"3.15"` (as `"M.m"` strings) | Target Python version. Inference order when unset: `project.requires-python` minimum → active/configured environment → built-in default. Officially supported: 3.10+; 3.7-3.9 may give false positives/negatives. Scripts use inline `environment.python-version` first, then `requires-python`, then inherit the project's |
| `root` | `null` | `list[str]` | First-party module roots in priority order (first = highest). Default detection: project root always; plus `./src`, `./<project-name>` (if nested dir exists), `./python` when they exist and are not packages. Scripts have no first-party roots by default (`root = ["."]` to import siblings) |
| `typeshed` | `null` | `str` | Custom typeshed directory for stdlib stubs; otherwise the vendored stubs bundled in the binary |

```toml
# pyproject.toml                    # ty.toml
[tool.ty.environment]               [environment]
python = "./custom-venv"            python = "./custom-venv"
python-version = "3.12"             python-version = "3.12"
```

## overrides

Array of per-file-configuration blocks; multiple overrides can match one file, later ones take precedence. Override rules take precedence over global rules for matching files.

| Option | Default | Notes |
|---|---|---|
| `include` | `["**"]` (all files) | gitignore-like patterns selecting files for this override |
| `exclude` | `[]` | Patterns to exclude from this override; take precedence over include within the same override |
| `rules` | `{...}` | Rule levels merged over global rules (`all` allowed) |
| `analysis.*` | as global | Per-override copies of the analysis options (`allowed-unresolved-imports`, `replace-imports-with-any`, `respect-type-ignore-comments`, `return-type-inference`, `strict-equality-semantics`, `strict-generic-narrowing`) |

```toml
# Relax rules in tests
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "warn"

# Ignore a rule in generated files but keep it for one important file
[[tool.ty.overrides]]
include = ["generated/**"]
exclude = ["generated/important.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "ignore"
```

(`ty.toml`: `[[overrides]]` / `[overrides.rules]`.)

## project-manager

Both settings are **preview** and may change between releases.

| Option | Default | Type | Notes |
|---|---|---|---|
| `project` | `"none"` | `"uv" \| "none"` | `"none"`: ty discovers the workspace and Python environment itself. `"uv"`: ty uses uv to discover the workspace root, environment, and dependency metadata (environment must already be synchronized; ty does not install project dependencies; uv may update the lockfile). Requires uv 0.12.3+. Explicit `TY_UV` takes precedence; an untrusted editor workspace disables uv |
| `script` | `"none"` | `"uv" \| "none"` | For PEP 723 scripts. `"none"`: look for the script's packages in the project's Python environment. `"uv"`: each script gets its own environment; uv installs its declared dependencies. Requires uv 0.12.3+. A script's inline `[tool.ty] project-manager.script` takes precedence; otherwise the script inherits the project's value. `uv check` sets `TY_UV=1`, always enabling script sync |

```toml
# pyproject.toml                    # ty.toml
[tool.ty.project-manager]           [project-manager]
script = "uv"                       script = "uv"
```

## src

| Option | Default | Notes |
|---|---|---|
| `include` | `null` | Files/directories to check (gitignore-like, reversed: including a directory includes its contents). `exclude` takes precedence over `include` |
| `exclude` | `null` | Patterns to exclude. Default excludes (negate with a leading `!` to re-include): `**/.bzr/`, `**/.direnv/`, `**/.eggs/`, `**/.git/`, `**/.git-rewrite/`, `**/.hg/`, `**/.mypy_cache/`, `**/.nox/`, `**/.pants.d/`, `**/.pytype/`, `**/.ruff_cache/`, `**/.svn/`, `**/.tox/`, `**/.venv/`, `**/__pypackages__/`, `**/_build/`, `**/buck-out/`, `**/dist/`, `**/node_modules/`, `**/venv/` |
| `exclude-scripts` | `false` | Exclude PEP 723 inline-metadata files unless explicitly passed on the command line |
| `respect-ignore-files` | `true` | Also exclude files ignored by `.ignore`, `.gitignore`, `.git/info/exclude`, and global gitignore files |

All patterns anchored relative to the project root (`src` matches only `<project_root>/src`); `**` must be a single path component.

```toml
[tool.ty.src]
include = ["src", "tests"]
exclude = ["src/generated", "!dist"]
```

## terminal

| Option | Default | Type | Notes |
|---|---|---|---|
| `error-on-warning` | `true` | `bool` | Exit code 1 even if all diagnostics are only `warning` severity. Set `false` to exit 0 when only warnings exist |
| `output-format` | `full` | `full \| concise \| github \| gitlab \| junit \| sarif` | Diagnostic output format (same values as `--output-format`) |

```toml
[tool.ty.terminal]
error-on-warning = false
output-format = "concise"
```

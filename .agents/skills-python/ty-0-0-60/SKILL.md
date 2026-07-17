---
name: ty-0-0-60
description: >
  ty 0.0.60 — extremely fast Python type checker and language server written in Rust,
  by Astral (creators of uv and Ruff). Use this skill whenever the user mentions ty,
  ty check, ty server, Python type checking, replacing mypy or pyright, ty.toml
  configuration, type narrowing, intersection types, or any Python static analysis
  task. Covers installation, type checking, configuration, rules, suppression,
  language server, editor integration, migration from mypy/pyright, and type system
  features.
metadata:
  tags:
    - python
    - typing
    - type-checking
    - static-analysis
    - lsp
---

# ty 0.0.60

## Overview

ty is an extremely fast Python type checker and language server, written in Rust by
Astral (creators of uv and Ruff). It is 10x–100x faster than mypy and Pyright, with
fine-grained incremental analysis for instant IDE feedback.

Version 0.0.60 (released 2026-07-15) brings unified generic call inference, support
for `type[Protocol]`, class and static protocol methods, PEP 695 alias resolution in
`type[...]`, own-line suppression comments, and improved Pydantic support.

ty uses `0.0.x` versioning — it is in beta and breaking changes (including to
diagnostics) may occur between any two versions.

ty is installed via `pip install ty`, `uv tool install ty`, the standalone installer,
or `uvx ty` for quick use without installation. It is invoked via the `ty` CLI.

## Usage

### Installation

```bash
pip install ty
uv tool install ty
uvx ty check                         # Quick run without install
pipx install ty
# Standalone installer:
curl -LsSf https://astral.sh/ty/install.sh | sh
# Docker:
COPY --from=ghcr.io/astral-sh/ty:0.0.60 /ty /bin/
```

### Type checking

```bash
ty check                              # Check current directory
ty check path/to/code/                # Check specific directory
ty check file.py                      # Check a single file
ty check --watch                      # Watch mode, recheck on changes
ty check --fix                        # Apply auto-fixes
ty check --python .venv/bin/python    # Specify Python interpreter
ty check --python-version 3.12        # Target Python version
ty check --output-format concise      # Compact output
ty check --output-format github       # GitHub Actions annotations
ty check --verbose                    # Verbose output
ty check --no-progress                # Hide progress indicators
```

### Language server

```bash
ty server                             # Start LSP (stdio)
```

### Other commands

```bash
ty version                            # Show version
ty version --output-format json       # JSON version info
ty explain rule unresolved-import     # Explain a specific rule
ty explain rule                       # Explain all rules
ty generate-shell-completion bash     # Generate shell completions
```

### Configuration files

ty reads `pyproject.toml` (under `[tool.ty]`) or `ty.toml`. It searches from the
current directory upward. `ty.toml` takes precedence over `pyproject.toml` when both
exist in the same directory. User-level config: `~/.config/ty/ty.toml`.

#### pyproject.toml

```toml
[tool.ty]

[tool.ty.rules]
possibly-unresolved-reference = "warn"
division-by-zero = "ignore"

[tool.ty.analysis]
allowed-unresolved-imports = ["test.**"]

[tool.ty.environment]
python-version = "3.12"
python = "./.venv"
root = ["./src"]

[tool.ty.src]
exclude = ["generated/"]
respect-ignore-files = true

[tool.ty.terminal]
output-format = "concise"
error-on-warning = false

[[tool.ty.overrides]]
include = ["tests/**"]
[tool.ty.overrides.rules]
possibly-unresolved-reference = "ignore"
```

#### ty.toml

```toml
[rules]
possibly-unresolved-reference = "warn"

[analysis]
allowed-unresolved-imports = ["test.**"]

[environment]
python-version = "3.12"
root = ["./src"]

[src]
exclude = ["generated/"]
```

### Rule levels

Each rule has a configurable severity:

- `error` — reported as error, ty exits with code 1
- `warn` — reported as warning; exit code depends on `terminal.error-on-warning`
- `ignore` — rule is disabled

Set via CLI:

```bash
ty check --error all                  # All rules as errors
ty check --warn unused-ignore-comment
ty check --ignore redundant-cast
```

### Suppression comments

```python
value = unknown  # ty: ignore[unresolved-reference]
# ty: ignore[unresolved-reference]    # File-level suppression (before any code)
result = calc()  # type: ignore[ty:unresolved-reference]  # Standard format
```

ty supports both `# ty: ignore[rule]` and `# type: ignore[ty:rule]`. It also supports
`@no_type_check` decorator to suppress all violations inside a function.

### Environment variables

- `TY_CONFIG_FILE` — path to ty.toml config file
- `TY_OUTPUT_FORMAT` — default output format
- `TY_LOG` — log level for verbose output (e.g., `ty=debug`)
- `TY_MAX_PARALLELISM` — limit parallel tasks
- `VIRTUAL_ENV` — detect active virtual environment
- `PYTHONPATH` — additional module search paths
- `CONDA_PREFIX` / `CONDA_DEFAULT_ENV` — detect Conda environment

### Exit codes

- `0` — no diagnostics (or only warnings with `error-on-warning = false`)
- `1` — error-level diagnostics found (or warnings with `error-on-warning = true`)

### CLI flags for exit control

```bash
ty check --exit-zero                  # Always exit 0
ty check --exit-zero-on-warning       # Exit 0 if no errors (warnings OK)
ty check --error-on-warning           # Exit 1 on any warning
```

## Gotchas

- **`ty.toml` takes precedence over `pyproject.toml`** — if both exist in the same
  directory, ty reads `ty.toml` and ignores `[tool.ty]` in `pyproject.toml`. Do not
  maintain configs in both files in the same directory.

- **`pyproject.toml` requires `[tool.ty]` section** — ty ignores `pyproject.toml`
  files that lack a `[tool.ty]` section and continues searching parent directories.
  An empty `[tool.ty]` table is sufficient to stop the search.

- **Config files do not merge implicitly** — ty uses the closest config file found
  walking up the directory tree. Settings from parent configs are not inherited.
  Project-level config takes precedence over user-level (`~/.config/ty/ty.toml`).

- **`ty` is not a linter** — it is a type checker only. Use Ruff for linting,
  formatting, and import sorting. ty does not replace Flake8, Black, or isort.

- **Python version defaults to `requires-python`** — ty reads `project.requires-python`
  from `pyproject.toml` to determine the target version. If absent, it falls back to
  the active environment's version, then to `3.14`. Set `python-version` explicitly
  if your project targets a specific version.

- **ty checks unannotated functions by default** — unlike mypy's `check_untyped_defs`,
  ty always checks function bodies regardless of annotations. There is no equivalent
  setting to disable this behavior.

- **`--python` accepts interpreters, venv dirs, or sys.prefix** — pass `.venv`,
  `.venv/bin/python`, or `/usr` — ty handles all three forms.

- **`--force-exclude` enforces exclusions on explicit paths** — by default, paths
  passed directly to `ty check` bypass exclude filters. Use `--force-exclude` to
  enforce exclusions even for explicit paths.

- **`allowed-unresolved-imports` uses glob patterns** — `*` matches within a component
  (not across `.`), `**` matches any number of components. Prefix with `!` to negate.
  Later entries take precedence.

- **`replace-imports-with-any` vs `allowed-unresolved-imports`** — the former replaces
  the module's type with `Any` even if resolvable; the latter only suppresses
  `unresolved-import` when the module truly can't be found.

- **`strict-literal-narrowing` preserves broad types** — when enabled, `value == "a"`
  does not narrow `str` to `Literal["a"]`. Useful when dealing with subclasses of
  `str`/`int` (e.g., `StrEnum`, `IntEnum`) where literal narrowing is unsound.

- **`respect-type-ignore-comments` defaults to `true`** — ty respects standard
  `type: ignore` comments by default. Set to `false` if you want to require
  `ty: ignore` exclusively (useful when migrating from another checker).

- **`src.root` is deprecated** — use `environment.root` instead. The old setting
  still works but will be removed.

- **`--watch` uses fine-grained incrementality** — ty rechecks only affected files
  and their dependents, not the entire project. This makes watch mode very efficient.

- **ty uses bundled typeshed stubs** — it ships with vendored typeshed. Use
  `--typeshed` to override with a custom typeshed directory.

- **`--add-ignore` adds blanket suppressions** — running `ty check --add-ignore`
  adds `# ty: ignore` comments without specific rule codes. Consider enabling
  `blanket-ignore-comment` rule to enforce specific codes.

- **Intersection types are first-class** — ty uses `A & B` internally for type
  narrowing via `isinstance`. Use `ty_extensions.Intersection` (type-checking only)
  for explicit intersection annotations.

- **`ty_extensions` is type-checking only** — `from ty_extensions import Intersection`
  works at type-checking time but will fail at runtime. Guard with `TYPE_CHECKING`.

- **`0.0.x` versioning means breaking changes anytime** — diagnostics, rule names,
  and behavior may change between patch versions. Pin ty in production CI.

- **ty is developed inside the Ruff repository** — PRs for ty go to the Ruff repo,
  under the `ruff/` submodule. The ty repo tracks releases only.

## References

- [01-configuration](references/01-configuration.md) — Full settings reference, config patterns, overrides
- [02-rules](references/02-rules.md) — Complete rules list, severity defaults, suppression patterns
- [03-type-system](references/03-type-system.md) — Intersection types, redeclarations, reachability, narrowing
- [04-language-server](references/04-language-server.md) — LSP features, editor setup, notebook support
- [05-migration](references/05-migration.md) — Migrating from mypy/pyright, rule mapping table

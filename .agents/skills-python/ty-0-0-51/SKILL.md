---
name: ty-0-0-51
description: Run ty (Astral's Python type checker, v0.0.51) for type checking, rule diagnostics, and language server integration. Use when the user mentions ty type checking, Python type errors, ty check, ty rules, ty suppression, migrating from mypy or pyright to ty, configuring ty.toml or pyproject.toml type checking, or setting up a Python language server. ty is 10x-100x faster than mypy/Pyright and supports intersection types, redeclarations, and reachability-based analysis.
metadata:
  tags:
    - python
    - type-checking
    - linter
---

# ty 0.0.51

## Overview

ty is an extremely fast Python type checker and language server written in Rust, created by Astral (the team behind uv and Ruff). Version 0.0.51 uses `0.0.x` versioning — the API is not yet stable, and breaking changes including diagnostic changes may occur between versions.

Key capabilities:
- **Type checking** — `ty check` scans Python files for type errors with rich diagnostics
- **Language server** — `ty server` provides IDE features (completions, go-to-definition, inlay hints, hover, rename, etc.)
- **Rule configuration** — configurable rule severities (`error`, `warn`, `ignore`) via CLI flags or config files
- **Suppression comments** — `# ty: ignore[rule]` inline suppression; also supports standard `type: ignore`
- **Watch mode** — `ty check --watch` for incremental rechecking on file changes

## Usage

### Quick start

Run ty without installing via uvx:

```bash
uvx ty check
```

Or add as a dev dependency:

```bash
uv add --dev ty
uv run ty check
```

### Type checking

```bash
# Check current project (default)
ty check

# Check specific files or directories
ty check src/ tests/test_main.py

# Watch mode (incremental recheck on changes)
ty check --watch

# Quiet output
ty check --quiet

# Verbose output
ty check --verbose
```

### Rule severity control

```bash
# Treat specific rules as errors
ty check --error possibly-missing-attribute --error possibly-missing-import

# Downgrade rules to warnings
ty check --warn unused-ignore-comment

# Disable rules
ty check --ignore redundant-cast

# Set all rules to error level
ty check --error all
```

### Environment and module resolution

```bash
# Specify Python environment explicitly
ty check --python .venv
ty check --python .venv/bin/python3

# Add extra search paths (like MYPYPATH)
ty check --extra-search-path ./shared-stubs

# Target a specific Python version
ty check --python-version 3.12

# Target a specific platform
ty check --python-platform linux
```

### Output formats

```bash
# Default verbose output (full)
ty check

# Concise one-per-line output
ty check --output-format concise

# GitHub Actions annotations
ty check --output-format github

# GitLab Code Quality JSON
ty check --output-format gitlab

# JUnit XML report
ty check --output-format junit
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | No error-level violations |
| `1` | Error-level violations found |
| `2` | Invalid CLI options, config errors, or IO errors |
| `101` | Internal error |

Use `--exit-zero` to always exit 0, or `--error-on-warning` to treat warnings as failures.

### Explaining rules

```bash
# Explain a specific rule
ty explain rule unresolved-import

# List all rules
ty explain rule
```

### Language server

Start the LSP server for editor integration:

```bash
ty server
```

Supported LSP features: diagnostics, completions, go-to-definition/declaration/type-definition, find-references, hover, inlay hints, signature help, rename, document highlight, semantic tokens, code folding, notebook support, call/type hierarchy, selection range, and fine-grained incremental updates.

### Shell autocompletion

```bash
# Bash
eval "$(ty generate-shell-completion bash)"

# Zsh
eval "$(ty generate-shell-completion zsh)"

# Fish
ty generate-shell-completion fish | source
```

## Configuration

ty reads configuration from `ty.toml` (preferred) or `[tool.ty]` in `pyproject.toml`. User-level config lives at `~/.config/ty/ty.toml`. Project config overrides user config; CLI flags override both.

### Config file structure

```toml title="ty.toml"
# Rule severities
[rules]
all = "warn"
possibly-unresolved-reference = "ignore"
redundant-cast = "ignore"

# Analysis settings
[analysis]
allowed-unresolved-imports = ["test.**", "!test.foo"]
replace-imports-with-any = ["pandas.**"]

# Environment settings
[environment]
python-version = "3.12"
python-platform = "linux"
python = "./.venv"
extra-paths = ["./shared-stubs"]
root = [".", "./src"]

# File inclusion/exclusion (gitignore-style globs)
[src]
include = ["src", "tests"]
exclude = ["generated/**", "*.proto"]
respect-ignore-files = true

# Terminal settings
[terminal]
output-format = "concise"
error-on-warning = true

# Per-file overrides
[[overrides]]
include = ["tests/**"]

[overrides.rules]
possibly-unresolved-reference = "ignore"
```

### Key configuration sections

- **`rules`** — Set severities: `rule-name = "error" | "warn" | "ignore"`. Use `all` for global default.
- **`analysis`** — `allowed-unresolved-imports` suppresses `unresolved-import` for glob patterns; `replace-imports-with-any` replaces module types with `Any`; `respect-type-ignore-comments` controls whether standard `type: ignore` works (default `true`).
- **`environment`** — `python-version` (3.7–3.15), `python-platform`, `python` path, `extra-paths`, `root` for first-party module discovery, `typeshed` for custom stubs.
- **`src`** — `include`/`exclude` globs, `respect-ignore-files`. Default excludes cover `.git`, `node_modules`, `.venv`, `__pycache__`, etc. Use `!"pattern"` to re-include.
- **`terminal`** — `output-format` (`full`, `concise`, `github`, `gitlab`, `junit`), `error-on-warning`.
- **`overrides`** — Per-glob rule and analysis overrides. Later overrides take precedence.

## Gotchas

- **ty is in beta (0.0.x)** — breaking changes can happen between any two versions. Pin your version in production (`uv add --dev ty==0.0.51`).
- **No `--strict` flag** — ty is stricter than mypy/Pyright by default. There is no equivalent to `--check-untyped-defs` or `strictListInference` because these are ty's default behavior. To approximate strict mode, enable disabled-by-default rules:
  ```toml
  [tool.ty.rules]
  missing-type-argument = "error"
  possibly-unresolved-reference = "warn"
  ```
- **`ty.toml` takes precedence over `pyproject.toml`** — if both exist in the same directory, only `ty.toml` is read. The `[tool.ty]` section in `pyproject.toml` is ignored.
- **Venv discovery order**: `VIRTUAL_ENV` env var → `.venv` in project root → `python3`/`python` on PATH. Use `--python` to override.
- **Python version fallback**: checks `requires-python` in `pyproject.toml` first, then infers from venv metadata, then falls back to 3.14.
- **Glob patterns are anchored** — `src` matches `<project_root>/src` only, not `<project_root>/lib/src`. Use `**/src` for unanchored matching (note: can slow file discovery).
- **Suppression comment syntax**: use `# ty: ignore[rule]`, not `# type: ignore[rule]` (unless `respect-type-ignore-comments = true`, in which case `type: ignore[ty:rule]` also works). Always specify rule names to avoid suppressing unrelated errors.
- **Redeclarations are allowed** — ty permits reusing a symbol name with a different type within the same scope, unlike mypy which would flag this as an error.
- **Intersection types** — ty supports `A & B` intersection types via `isinstance` narrowing and the `ty_extensions.Intersection` type-checking-only import. This is unique among Python type checkers.
- **`@no_type_check` only works on functions** — decorating a class with `@no_type_check` is not supported.

## References

- [01-cli-reference](references/01-cli-reference.md) — CLI commands, flags, and options
- [02-configuration](references/02-configuration.md) — Config file format, sections, and settings
- [03-type-system](references/03-type-system.md) — Redeclarations, intersection types, reachability analysis
- [04-rules](references/04-rules.md) — Rule list, severities, and suppression
- [05-editor-integration](references/05-editor-integration.md) — VS Code, Neovim, Zed, PyCharm, Emacs setup
- [06-migration](references/06-migration.md) — Migrating from mypy or pyright to ty

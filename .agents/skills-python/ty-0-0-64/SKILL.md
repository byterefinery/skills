---
name: ty-0-0-64
description: >
  ty 0.0.64 — extremely fast Python type checker and language server written in Rust,
  backed by Astral (creators of uv and Ruff). Use this skill whenever the user mentions
  ty, ty check, ty server, Python type checking, replacing mypy or pyright, ty.toml
  configuration, ty language server, ty editor integration, ty suppression comments,
  or any Python static type analysis task. Covers installation, CLI usage, configuration,
  rules, suppression, editor/LSP integration, type system features, and migration from
  mypy or pyright.
metadata:
  tags:
    - python
    - type-checking
    - lsp
    - static-analysis
---

# ty 0.0.64

## Overview

ty is an extremely fast Python type checker and language server, written in Rust. It is
10x-100x faster than mypy and Pyright, with comprehensive diagnostics, configurable rule
levels, and a full-featured LSP with fine-grained incremental analysis.

ty supports Python 3.7 through 3.15 as target versions, with first-class support for
3.10+. It provides unique type system features including intersection types, redeclarations,
reachability-based type analysis, and `ty_extensions` for ty-specific annotations.

Version 0.0.64 (released 2026-07-27) adds `--exclude-scripts`/`--include-scripts` flags,
uv workspace root discovery, `textDocument/implementation` LSP support, NumPy docstring
rendering, improved identity narrowing for NewTypes, `TypeVarTuple` and `Unpack` support,
and tagged union narrowing via identity comparisons.

ty is invoked via the `ty` CLI. It can be run without installation via `uvx ty check`.

## Usage

### Installation

```bash
# Quick start without installation
uvx ty check

# Add as dev dependency (recommended for projects)
uv add --dev ty
uv run ty check

# Global install
uv tool install ty@latest
pipx install ty
pip install ty

# Standalone installer
curl -LsSf https://astral.sh/ty/0.0.64/install.sh | sh

# Docker
COPY --from=ghcr.io/astral-sh/ty:0.0.64 /ty /bin/
```

### Type checking

```bash
ty check                              # Check project root
ty check src/ tests/                  # Check specific paths
ty check --watch                      # Watch mode, recheck on changes
ty check --fix                        # Apply auto-fixes
ty check --python .venv               # Specify Python environment
ty check --python-version 3.11        # Target Python version
ty check --output-format concise      # Compact output
ty check --output-format github       # GitHub Actions annotations
ty check --verbose                    # Verbose output
ty check --add-ignore                 # Add ty: ignore comments to suppress errors
ty check --explain rule               # Explain a specific rule
ty check --error all                  # Treat all rules as errors
ty check --ignore unresolved-import   # Disable a rule
ty check --warn missing-type-argument # Set rule to warning
```

### Language server

```bash
ty server                             # Start LSP (stdio, for editors)
```

### Rule explanation

```bash
ty explain rule                       # List all rules
ty explain rule invalid-assignment    # Explain a specific rule
ty explain rule --output-format json  # JSON output
```

### Configuration files

ty reads `ty.toml` (preferred) or `pyproject.toml` (`[tool.ty]` section), searching
up from the current directory. User-level config at `~/.config/ty/ty.toml`.

#### ty.toml

```toml
[rules]
missing-type-argument = "error"
possibly-unresolved-reference = "warn"
redundant-cast = "ignore"

[analysis]
allowed-unresolved-imports = ["test.**"]
strict-equality-semantics = false

[environment]
extra-paths = ["./shared"]
root = ["./app"]

[src]
include = ["src", "tests"]
exclude = ["src/generated", "*.proto"]
respect-ignore-files = true

[terminal]
error-on-warning = true
output-format = "full"
```

#### pyproject.toml

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
```

### Rule levels

Each rule has a severity: `error` (exit code 1), `warn` (warning), or `ignore` (disabled).
Default: most rules enabled at `warn` level. Set `terminal.error-on-warning = false` to exit
0 on warnings-only.

```bash
ty check --error invalid-assignment --warn missing-type-argument --ignore redundant-cast
```

### Suppression comments

```python
# ty: ignore[invalid-argument-type]       # File-level suppression
result = bad_call("x")  # ty: ignore[invalid-argument-type]  # Line-level
result = bad_call("x")  # type: ignore[ty:invalid-argument-type]  # Standard format
```

Standard `type: ignore` is also supported. Combine with other checkers:
`# type: ignore[arg-type, ty:invalid-argument-type]`.

### Editor integration

- **VS Code** — Install the [ty extension](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty)
- **Neovim** — Use `nvim-lspconfig`, then `vim.lsp.enable('ty')`
- **Zed** — Built-in, set `"language_servers": ["ty", "ruff"]` in Python config
- **PyCharm** — Native support from 2025.3, enable in **Python | Tools | ty**
- **Emacs** — Use Eglot: `("ty" "server")` for `python-base-mode`

### Shell completion

```bash
# Bash
echo 'eval "$(ty generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(ty generate-shell-completion zsh)"' >> ~/.zshrc

# Fish
echo 'ty generate-shell-completion fish | source' > ~/.config/fish/completions/ty.fish
```

### Exit codes

- `0` — no error-level diagnostics (warnings may still appear)
- `1` — error-level diagnostics found
- Use `--exit-zero` to always return 0, `--error-on-warning` to fail on warnings

## Gotchas

- **`ty.toml` takes precedence over `pyproject.toml`** — if both exist in the same
  directory, only `ty.toml` is read; `[tool.ty]` in `pyproject.toml` is ignored.

- **No `--strict` mode** — ty's default mode is already strict. Use individual rule
  settings for tighter checking. See the migration reference for recommended strict configs.

- **`--python` vs environment discovery** — ty auto-discovers `.venv` and `VIRTUAL_ENV`.
  Only use `--python` when the environment is in an unusual location.

- **`--select` does not exist** — unlike Ruff, ty does not use `--select`. Use `--error`,
  `--warn`, `--ignore` to control individual rules, or `--error all` for everything.

- **`type: ignore` suppresses all ty rules** — use `ty: ignore[rule]` for targeted
  suppression. Standard `type: ignore` without codes silences everything on that line.

- **`unused-ignore-comment` cannot use bare suppression** — it only responds to
  `# ty: ignore[unused-ignore-comment]`, not bare `# ty: ignore`.

- **`@no_type_check` on classes is not supported** — decorating a class with
  `@no_type_check` has no effect; only functions are supported.

- **Python 3.7-3.9 may produce false results** — these versions lack bundled stdlib
  stubs, so ty may emit false negatives or positives. Target 3.10+ for reliable results.

- **`src` directory auto-detected** — ty automatically includes `./src`, `./python`,
  and `./<project-name>/<project-name>` layouts. Override with `environment.root`.

- **`.gitignore` respected by default** — files in `.gitignore` are excluded. Disable
  with `respect-ignore-files = false` or `--no-respect-ignore-files`.

- **ty is not a linter** — it does type checking only. Use Ruff for linting, formatting,
  and import sorting alongside ty.

- **`--add-ignore` adds `ty: ignore` with space after colon** — the format is
  `# ty: ignore[rule]` (space after colon), matching ty's own comment style.

- **`--exclude-scripts` excludes PEP 723 inline scripts** — files with `/// script`
  metadata are skipped unless passed explicitly on the command line.

- **`allowed-unresolved-imports` uses module globs** — patterns like `test.**` match
  `test` and all submodules. Use `!` prefix to exclude specific modules from the pattern.

- **`ty_extensions` only available at type-checking time** — `Intersection` from
  `ty_extensions` must be imported behind `if TYPE_CHECKING:` guard.

- **`strict-equality-semantics` changes narrowing behavior** — when enabled, ty no
  longer narrows `str` to `Literal["a"]` after `x == "a"` checks, preventing unsound
  inference from subclasses that override `__eq__`.

## References

- [01-type-system](references/01-type-system.md) — Intersection types, redeclarations, reachability analysis, ty_extensions
- [02-rules](references/02-rules.md) — Complete rules reference with severity levels and examples
- [03-configuration](references/03-configuration.md) — Full configuration settings, environment, overrides, per-file patterns
- [04-language-server](references/04-language-server.md) — LSP features, editor settings, fine-grained incrementality
- [05-migration](references/05-migration.md) — Migrating from mypy or pyright, rule mapping table, strict config patterns
- [06-suppression](references/06-suppression.md) — Suppression comments, type: ignore, @no_type_check, unused-ignore-comment

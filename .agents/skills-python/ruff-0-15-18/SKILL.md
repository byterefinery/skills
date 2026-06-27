---
name: ruff-0-15-18
description: >
  Ruff 0.15.18 — extremely fast Python linter and code formatter written in Rust.
  Use this skill whenever the user mentions ruff, linting Python, formatting Python code,
  ruff check, ruff format, pyproject.toml lint config, Flake8 replacement, Black replacement,
  isort replacement, or any Python code quality task involving ruff configuration, rule selection,
  or CI integration. Covers `ruff check`, `ruff format`, `ruff rule`, `ruff config`,
  `ruff analyze graph`, and `ruff server` (LSP).
metadata:
  tags:
    - python
    - linting
    - formatting
    - code-quality
---

# ruff 0.15.18

## Overview

Ruff is an extremely fast Python linter and code formatter written in Rust, designed as a drop-in
replacement for Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade, autoflake,
and more — executing tens to hundreds of times faster than any individual tool.

Version 0.15.18 supports Python 3.7 through 3.15, includes over 900 built-in lint rules across
30+ linter plugins (Pyflakes, pycodestyle, flake8-bugbear, isort, etc.), and a Black-compatible
formatter. New in this release: `ruff analyze graph` for dependency mapping, human-readable rule
names in CLI output, and improved `__init__.py` import fix safety in preview mode.

## Usage

### Installation

```bash
# Via uv (recommended)
uv tool install ruff@0.15.18

# Or ephemeral via uvx
uvx ruff check        # Lint current directory
uvx ruff format       # Format current directory

# Via pip
pip install ruff==0.15.18

# Standalone installer (macOS/Linux)
curl -LsSf https://astral.sh/ruff/0.15.18/install.sh | sh
```

### Core Commands

```bash
# Linting
ruff check                    # Lint current directory
ruff check --fix              # Lint and auto-fix
ruff check --fix --unsafe-fixes   # Include unsafe fixes
ruff check --diff             # Show diff without writing
ruff check --select E,F,B     # Enable specific rule categories
ruff check --ignore E501      # Ignore specific rules
ruff check --statistics       # Show violation counts per rule
ruff check --add-noqa         # Auto-add noqa comments

# Formatting
ruff format                   # Format in-place
ruff format --check           # Check without writing (non-zero exit if changes needed)
ruff format --diff            # Show formatting diff

# Inspection
ruff rule F401                # Explain a specific rule
ruff rule --all               # List all rules
ruff config                   # List all config options
ruff config line-length       # Describe a specific option
ruff linter                   # List supported upstream linters

# Analysis
ruff analyze graph            # Generate dependency/dependent graph

# LSP
ruff server                   # Run language server (for editor integration)
```

### Configuration Files

Ruff reads configuration from `pyproject.toml`, `ruff.toml`, or `.ruff.toml` (precedence: `.ruff.toml` > `ruff.toml` > `pyproject.toml`).

**Minimal `pyproject.toml`:**

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "B", "UP", "SIM", "I"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
```

**Equivalent `ruff.toml`:**

```toml
line-length = 88
target-version = "py312"

[lint]
select = ["E", "F", "B", "UP", "SIM", "I"]
ignore = ["E501"]

[format]
quote-style = "double"
```

### Rule Selection

- Use `select` for an explicit rule set (preferred over `extend-select`).
- Use `ALL` cautiously — it enables all rules and picks up new rules on upgrade.
- Start small (`select = ["E", "F"]`) and add categories incrementally.
- Preview rules require `preview = true` in config or `--preview` flag.

### Per-File Ignores

```toml
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402"]
"**/{tests,docs}/*" = ["E402", "S101"]
```

### Extending Parent Config

```toml
[tool.ruff]
extend = "../pyproject.toml"
line-length = 100
```

### CLI Overrides

```bash
# Override a single setting without a config file
ruff check --config "lint.line-length = 100"

# Ignore all config files
ruff check --isolated
```

## Gotchas

- **`select` on CLI replaces config `select`** — running `ruff check --select F401` enforces only `F401`, not the union of CLI and config rules. Use `--extend-select` to add to the config set instead.
- **Preview rules need explicit opt-in** — selecting a preview rule code (e.g., via `extend-select`) does nothing unless `preview = true` is also enabled for lint or format.
- **Config file discovery uses closest match, not cascade** — Ruff picks the nearest config file and ignores parent configs. Use `extend = "../path"` to inherit settings explicitly.
- **Files passed directly bypass excludes** — `ruff check /path/to/excluded/file.py` always lints the file unless `--force-exclude` is also set.
- **`.ruff.toml` takes precedence** — if multiple config file types exist in the same directory, `.ruff.toml` > `ruff.toml` > `pyproject.toml`.
- **`pyproject.toml` needs `[tool.ruff]` section** — Ruff ignores `pyproject.toml` files that lack this section during config discovery.
- **Formatter is Black-compatible but not interchangeable long-term** — Ruff's formatter differs from Black in a few conscious ways. Do not mix them on the same codebase over time.
- **`--fix` excludes unsafe fixes by default** — use `--unsafe-fixes` to include fixes that may change semantics (e.g., refactoring patterns).
- **Jupyter notebooks are linted/formatted by default** — exclude with `[tool.ruff.format] exclude = ["*.ipynb"]` if formatting notebooks causes issues.
- **`target-version` inferred from `requires-python`** — if no config specifies `target-version`, Ruff falls back to the `requires-python` field in a nearby `pyproject.toml`.

## References

- [01-configuration](references/01-configuration.md) — Config file formats, discovery rules, all settings
- [02-linter-rules](references/02-linter-rules.md) — Rule categories, selection strategies, fix behavior
- [03-formatter](references/03-formatter.md) — Formatter options, Black compatibility, docstring formatting
- [04-ci-integration](references/04-ci-integration.md) — GitHub Actions, GitLab CI, pre-commit hooks
- [05-editor-setup](references/05-editor-setup.md) — VS Code, Neovim, PyCharm, LSP configuration

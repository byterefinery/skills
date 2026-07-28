---
name: ruff-0-4-10
description: >
  Ruff 0.4.10 — extremely fast Python linter and code formatter written in Rust.
  Use this skill whenever the user mentions ruff, ruff check, ruff format, Python
  linting, Python formatting, replacing Flake8/Black/isort/pyupgrade, pyproject.toml
  ruff config, ruff.toml, pre-commit ruff hooks, or any Python code quality task.
  Covers installation, linting (`ruff check`), formatting (`ruff format`), rule
  selection, configuration, fixes, pre-commit integration, CI, and migration from
  other tools.
metadata:
  tags:
    - python
    - linting
    - formatting
    - code-quality
---

# ruff 0.4.10

## Overview

Ruff is an extremely fast Python linter and code formatter, written in Rust. It
replaces Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade,
autoflake, and more — all in a single tool executing 10-100x faster than
individual tools.

Version 0.4.10 includes over 800 built-in lint rules with native re-implementations
of popular Flake8 plugins (flake8-bugbear, flake8-comprehensions, flake8-pytest-style,
and many more), plus a built-in formatter designed as a Black drop-in replacement.

Ruff is installed via `pip install ruff`, available through Homebrew, Conda, and
various package managers. It is invoked via the `ruff` CLI.

## Usage

### Installation

```bash
pip install ruff
pipx install ruff
# Or via Homebrew:
brew install ruff
```

### Linting

```bash
ruff check                          # Lint current directory
ruff check path/to/code/            # Lint specific directory
ruff check path/to/file.py          # Lint a single file
ruff check --fix                    # Lint and auto-fix fixable errors
ruff check --unsafe-fixes           # Also apply unsafe fixes
ruff check --watch                  # Re-lint on file changes
ruff check --statistics             # Show violation counts by rule
ruff check --output-format concise  # Compact output
ruff check --output-format json     # JSON output (CI/tooling)
ruff check --select E,F,B,UP        # Enable specific rule categories
ruff check --ignore E501            # Ignore specific rules
ruff check --extend-select I        # Add rules on top of defaults
ruff check --add-noqa               # Add noqa comments to all violations
ruff check --show-files             # List files Ruff will inspect
ruff check --show-settings          # Show resolved settings for a path
```

### Formatting

```bash
ruff format                         # Format current directory
ruff format path/to/code/           # Format specific directory
ruff format path/to/file.py         # Format a single file
ruff format --check                  # Check without writing
ruff format --diff                   # Show diff of changes
ruff format --preview                # Use preview formatting rules
```

### Combined lint + format

```bash
ruff check --fix && ruff format     # Fix lint issues then format
```

### Configuration files

Ruff reads `pyproject.toml`, `ruff.toml`, or `.ruff.toml` — walking up from the
target files to the repo root. The closest config wins (no implicit merging, but
`extend` supports explicit inheritance).

#### pyproject.toml

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
exclude = ["migrations/", "vendor/"]

[tool.ruff.lint]
select = ["E", "F", "B", "UP", "I", "SIM"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]
"tests/**" = ["S101"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
```

#### ruff.toml

```toml
line-length = 88
target-version = "py311"

[lint]
select = ["E", "F", "B", "UP", "I", "SIM"]
ignore = ["E501"]

[lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]

[format]
quote-style = "double"
```

### Rule selection

Ruff mirrors Flake8's rule codes: one-to-three letter prefix + three digits
(e.g., `F401`, `E501`, `B006`). Prefixes map to rule sources:

| Prefix | Source |
|--------|--------|
| `E`, `W` | pycodestyle |
| `F` | Pyflakes |
| `B` | flake8-bugbear |
| `C90` | McCabe complexity |
| `I` | isort |
| `N` | pep8-naming |
| `UP` | pyupgrade |
| `ANN` | flake8-annotations |
| `S` | flake8-bandit |
| `SIM` | flake8-simplify |
| `PL` | Pylint |
| `RUF` | Ruff-specific |

Default enabled rules: `E4`, `E7`, `E9`, `F` (narrow, focused on errors).

Recommended starting set for new projects: `["E", "F", "B", "UP", "I"]`.

### Per-file ignores

```toml
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402", "F401"]
"tests/**" = ["S101"]
"migrations/**" = ["ALL"]
```

### Inline controls

```python
import os  # noqa: F401          # Ignore specific rule on this line
import sys  # noqa                # Ignore all rules on this line
# ruff: noqa                      # Ignore all rules for the entire file
# ruff: noqa: E501                # Ignore specific rule for the entire file
```

### pre-commit integration

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

### GitHub Actions

```yaml
- uses: chartboost/ruff-action@v1
  with:
    version: '0.4.10'
```

### Exit codes

- `0` — success (no violations, or all fixed)
- `1` — violations found
- `2` — error (e.g., file not found, parse error)

### stdin / stdout

```bash
echo "print ( 'hi' )" | ruff check -
echo "print ( 'hi' )" | ruff format -
ruff check --stdin-filename foo.py - < foo.py
```

### VS Code

Install the [Ruff VS Code extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).
Configure via `.vscode/settings.json`:

```json
{
  "ruff.path": ["venv", "bin", "ruff"],
  "ruff.formatting": true,
  "ruff.linting": true
}
```

## Gotchas

- **`pyproject.toml` requires `[tool.ruff]` section** — Ruff ignores `pyproject.toml`
  files that lack a `[tool.ruff]` section during config discovery. Use `ruff.toml` or
  `.ruff.toml` if you want a dedicated config file without the tool prefix.

- **Config files do not merge implicitly** — Ruff uses the closest config file in the
  directory hierarchy; parent configs are ignored. Use `extend = "../ruff.toml"` for
  explicit inheritance.

- **`--select` on CLI overrides config** — passing `--select F401` on the command line
  replaces the config's `select`, it does not add to it. Use `--extend-select` to add
  rules on top of the config's selection.

- **`--exclude` vs `--extend-exclude`** — `--exclude` replaces default exclusions;
  `--extend-exclude` adds to them. In config, use `extend-exclude` to keep defaults.

- **`E501` conflicts with formatter** — Ruff's formatter (and Black) make best-effort
  attempts to fit lines within `line-length`, but cannot always do so (e.g., long
  strings, comments). Only enable `E501` if you accept that some violations may be
  unfixable.

- **`--fix` only applies safe fixes by default** — unsafe fixes (those that may change
  behavior) require `--unsafe-fixes`. Review the fix safety classification for rules
  you enable auto-fix on.

- **`target-version` affects lint rules** — setting `target-version = "py311"` enables
  pyupgrade rules that modernize syntax to Python 3.11. Without it, Ruff defaults to
  py38 and may miss modernization opportunities.

- **`src` paths for first-party detection** — if your code lives under `src/`, set
  `src = ["src"]` in config so isort rules (`I`) correctly distinguish first-party
  from third-party imports.

- **Cache directory** — Ruff caches analysis results. Set `RUFF_CACHE_DIR` to override,
  or use `--no-cache` for deterministic CI runs.

- **Jupyter notebook support** — Ruff handles `.ipynb` files natively. Cell magics are
  skipped. Use `--extension IPYNB:py` if needed.

- **`ruff.toml` vs `.ruff.toml`** — both are valid; `.ruff.toml` is hidden (dotfile)
  which some teams prefer. They are functionally identical.

- **`ALL` enables everything including conflicting rules** — when using `select = ["ALL"]`,
  Ruff auto-disables conflicting pydocstyle rules (e.g., D203 vs D211). Be aware that
  new rules added in future Ruff versions will also be enabled.

- **pre-commit passes files directly** — like Black, pre-commit bypasses file discovery,
  so `exclude` in config does not filter pre-commit's file list. Use pre-commit's
  `exclude` key or Ruff's `force-exclude` instead.

- **`--add-noqa` is additive** — running `ruff check --add-noqa` adds noqa comments
  without removing existing ones. Run `ruff check --dummy-select-regex` or manually
  clean up stale noqa comments.

- **Ruff is not a type checker** — it catches unused imports, syntax errors, and style
  issues. It does not do type inference. Use alongside mypy, pyright, or pyre for
  type checking.

## References

- [01-rule-categories](references/01-rule-categories.md) — Full rule code prefixes and categories
- [02-configuration](references/02-configuration.md) — Complete settings reference and config patterns
- [03-migration](references/03-migration.md) — Migrating from Flake8, Black, isort, Pylint
- [04-ci-integration](references/04-ci-integration.md) — CI/CD setups, pre-commit, GitHub Actions, GitLab

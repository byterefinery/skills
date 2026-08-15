---
name: ruff-0-16-0
description: Lint and format Python code with Ruff 0.16.0. Use when the user mentions ruff, Python linting, Python formatting, replacing Flake8/Black/isort/pyupgrade, ruff check, ruff format, pyproject.toml lint config, ruff.toml, noqa comments, rule selection, or any Python code quality task.
license: MIT
compatibility: Requires Ruff 0.16.0 installed (via pip, uv, standalone installer, or package manager). Python 3.7+ source code support.
metadata:
  tags:
    - python
    - linting
    - formatting
    - code-quality
---

# ruff 0.16.0

## Overview

Ruff is an extremely fast Python linter and code formatter written in Rust. It replaces Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade, autoflake, and more, executing 10-100x faster than any individual tool. Ruff 0.16.0 supports over 900 lint rules and provides Black-compatible formatting via a unified CLI.

Two primary subcommands:
- **`ruff check`** — lint Python files, with automatic fix support
- **`ruff format`** — format Python files (Black-compatible)

Ruff can be used as linter-only, formatter-only, or both. It supports `pyproject.toml`, `ruff.toml`, and `.ruff.toml` configuration files with hierarchical discovery.

## Usage

### Linting

```bash
ruff check                          # lint current directory
ruff check src/                     # lint specific path
ruff check --fix                    # lint and apply safe fixes
ruff check --fix --unsafe-fixes     # include unsafe fixes
ruff check --select E,F,B,UP        # enable specific rule categories
ruff check --ignore E501            # disable specific rule
ruff check --add-noqa               # add noqa comments to existing violations
ruff check --show-files             # list files that would be checked
ruff check --show-settings          # show resolved settings for a file
ruff check --output-format json     # machine-readable output
ruff check --watch                  # re-lint on file changes
```

### Formatting

```bash
ruff format                         # format current directory
ruff format src/                    # format specific path
ruff format --check                 # check without writing (CI-friendly)
ruff format --diff                  # show diff of changes
ruff format --line-length 100       # override line length
```

### Rule selection

Ruff uses Flake8-style rule codes (e.g., `F401`, `E501`, `B006`). Rule categories include `E`/`W` (pycodestyle), `F` (Pyflakes), `B` (flake8-bugbear), `UP` (pyupgrade), `I` (isort), `D` (pydocstyle), `SIM` (flake8-simplify), and many more.

By default, Ruff enables `F`, `E`, `B`, `UP`, and `RUF` rules, omitting stylistic rules that overlap with the formatter. Start with defaults and expand:

```toml
[lint]
select = ["E", "F", "B", "UP", "I", "SIM"]
```

Use `extend-select` to add rules on top of defaults; `select` replaces the entire set.

### Configuration files

Ruff discovers config in `pyproject.toml` (under `[tool.ruff]`), `ruff.toml`, or `.ruff.toml`. Config files cascade — the closest file to a given source file wins (no merging). Use `extend` to inherit from a parent config.

```toml
# ruff.toml
line-length = 88
target-version = "py310"

[lint]
select = ["E", "F", "B", "UP"]
ignore = ["E501"]

[lint.per-file-ignores]
"__init__.py" = ["E402"]

[format]
quote-style = "double"
indent-style = "space"
```

### Error suppression

```python
x = 1  # noqa: F841                    # line-level
# ruff: noqa: F841                     # file-level (place near top)
# ruff: disable[E501]                  # block-level start
long_line = "..."
# ruff: enable[E501]                   # block-level end
```

### Pre-commit integration

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.16.0
  hooks:
    - id: ruff-check
      args: [--fix]
    - id: ruff-format
```

## Gotchas

- **`select` replaces, `extend-select` adds.** Using `select = ["E", "F"]` disables all default rules not in E/F. Use `extend-select` to add rules on top of defaults.
- **Config files do not merge.** The closest config file to a source file wins entirely. Use `extend = "../ruff.toml"` to inherit settings from a parent config.
- **Stylistic rules conflict with the formatter.** Rules like `W191`, `E111`, `Q000`-`Q004`, `COM812`, `COM819`, `ISC002` can fight the formatter. None are in the default set, but enabling categories like `Q` or `W` pulls them in. Disable conflicting rules when using both linter and formatter.
- **`--fix` only applies safe fixes by default.** Unsafe fixes (which may change runtime behavior) require `--unsafe-fixes`. Ruff shows hints when unsafe fixes are available.
- **`# noqa` on multi-line statements covers the entire logical line.** Place `# noqa` at the end of the closing line (e.g., after triple-quote for docstrings) to suppress the full statement.
- **`ruff format` does not sort imports.** Import sorting is a linter rule (`I` category). Run `ruff check --select I --fix` then `ruff format` for both.
- **`target-version` controls lint rules and formatter behavior.** If omitted, Ruff infers from `requires-python` in `pyproject.toml`. Set explicitly for consistent behavior: `target-version = "py310"`.
- **Jupyter notebooks are linted and formatted by default.** Exclude them from one tool with section-specific `exclude`: `[format] exclude = ["*.ipynb"]`.
- **`ruff check` exit codes:** 0 = no violations or all fixed, 1 = violations found, 2 = abnormal termination. Use `--exit-zero` to always exit 0, `--exit-non-zero-on-fix` to signal when files were modified.
- **`ruff format --check` exit codes:** 0 = all files formatted, 1 = some files would be reformatted, 2 = abnormal termination.
- **Preview rules require `--preview` or `preview = true`.** Selecting a preview rule code alone does not enable it — preview mode must be active. Preview mode can be configured independently for lint and format.
- **F-string formatting differs from Black.** Ruff formats the expression parts inside `{...}` of f-strings. This is a known deviation from Black.
- **`.ruff.toml` takes precedence over `ruff.toml`, which takes precedence over `pyproject.toml`.** When multiple config files exist in the same directory, this priority order applies.
- **`src` directories control first-party import detection.** Default is project root + `src/`. Set explicitly for non-standard layouts: `src = ["src", "lib"]`.
- **`--config` can override individual settings.** Use `--config "lint.line-length = 100"` to override a single setting without a config file. Linter-specific settings need `lint.` prefix, formatter settings need `format.` prefix.

## References

- [01-linter](references/01-linter.md) — Rule selection, fix safety, error suppression, exit codes
- [02-formatter](references/02-formatter.md) — Formatting, Black compatibility, style config, docstring formatting, known deviations
- [03-configuration](references/03-configuration.md) — Config files, discovery, hierarchical config, CLI overrides, target version
- [04-integrations](references/04-integrations.md) — Pre-commit, editors, CI/CD, Docker, GitHub Actions, shell completion

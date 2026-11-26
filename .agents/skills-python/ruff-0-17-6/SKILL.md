---
name: ruff-0-17-6
description: >
  Ruff 0.17.6 — an extremely fast Python linter and code formatter, written in
  Rust. Use this skill whenever the user mentions ruff, linting Python code,
  ruff check, ruff format, ruff configuration, pyproject.toml or ruff.toml
  ruff config, rule codes (F401, E501, UP, B...), noqa or inline suppression
  comments, or any Python lint/format task. Covers `uvx ruff@0.17.6`,
  installation, configuration discovery, rule selection, safe and unsafe
  fixes, error suppression, formatter options, Jupyter and Markdown support,
  and pre-commit / GitHub Actions integration.
metadata:
  tags:
    - python
    - linting
    - formatting
    - code-quality
---

# ruff 0.17.6

## Overview

Ruff is an extremely fast Python linter and code formatter, written in Rust. It is a
drop-in replacement for Flake8 (plus dozens of plugins), isort, pydocstyle, pyupgrade,
autoflake, and Black, all behind a single CLI. It bundles 900+ lint rules re-implemented
as first-party features and a formatter that emits near-identical output to Black
(> 99.9% of lines identical on large Black-formatted projects like Django and Zulip).

Version 0.17.6 was released on 2026-11-19. Ruff uses a custom versioning scheme —
not semver: the **minor** version number carries breaking changes, the **patch**
number carries bug fixes. Support extends to Python 3.15 (`target-version` accepts
`py37` through `py315`).

The two primary commands:

- `ruff check` — the linter (rule selection, fixes, suppression)
- `ruff format` — the formatter (Black-compatible style)

## Usage

### Ephemeral execution (recommended)

```bash
uvx ruff@0.17.6 check          # Lint current directory (and subdirectories)
uvx ruff@0.17.6 check --fix    # Lint and apply safe fixes
uvx ruff@0.17.6 format         # Format all files in place
uvx ruff@0.17.6 format --check # CI check without writing files
```

### Persistent installation

```bash
uv tool install ruff@latest    # Global install via uv
uv add --dev ruff              # Add to a project
pip install ruff               # Via pip
pipx install ruff              # Via pipx
# Standalone installers (no Python needed):
curl -LsSf https://astral.sh/ruff/install.sh | sh
curl -LsSf https://astral.sh/ruff/0.17.6/install.sh | sh   # pinned version
# Also available via Homebrew, Conda (conda-forge), and Docker
# (ghcr.io/astral-sh/ruff, tagged per release).
```

### Linting — `ruff check`

```bash
ruff check                          # Lint current directory recursively
ruff check path/to/code/            # Lint a specific tree
ruff check file.py                  # Lint one file
ruff check --fix                    # Apply safe fixes
ruff check --fix --unsafe-fixes     # Also apply unsafe fixes (may change behavior)
ruff check --watch                  # Re-lint on file changes
ruff check --diff                   # Show fixes as a diff without writing
ruff check --select F401,E501       # Replace the rule set with exactly these
ruff check --extend-select B        # Add flake8-bugbear rules to the configured set
ruff check --statistics             # Count violations per rule
ruff check --output-format json     # concise, json, json-lines, junit, github, gitlab,
                                    # pylint, rdjson, azure, sarif, grouped
ruff check --add-noqa               # Auto-add # noqa directives to failing lines
ruff check - --stdin-filename x.py  # Lint stdin
ruff check @args.txt                # Read arguments from a file (one per line)
ruff rule F401                      # Explain a rule (rule <code> / --all / <name>)
```

Exit codes (shared with `ruff format`): `0` clean (or all violations fixed),
`1` violations found, `2` invalid configuration, invalid CLI options, or internal error.
`--exit-zero` forces `0` even with violations; `--exit-non-zero-on-fix` exits `1` if
anything was fixed even when no violations remain.

### Formatting — `ruff format`

```bash
ruff format                 # Format all discovered files in place
ruff format --check src/    # Exit non-zero if any file would change (no writes)
ruff format --diff          # Show the diff instead of writing
ruff format --line-length 100
ruff format --preview       # Preview formatting style
```

The formatter does **not** sort imports. To sort imports and format:

```bash
ruff check --select I --fix
ruff format
```

### Configuration

Ruff reads the **closest** `pyproject.toml`, `ruff.toml`, or `.ruff.toml` in the file's
directory or any parent. In `pyproject.toml`, settings live under `[tool.ruff]` (and
`[tool.ruff.lint]`, `[tool.ruff.format]`); in `ruff.toml` the `tool.ruff` prefix is
omitted. Config files are not merged across the tree — the closest one wins — so use the
`extend` key to inherit another config file.

```toml
# pyproject.toml
[tool.ruff]
line-length = 88            # default, same as Black
target-version = "py311"    # default; inferred from requires-python when unset

[tool.ruff.lint]
extend-select = ["B"]       # add flake8-bugbear to the default rule set
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["E402"]
"**/{tests,docs,tools}/*" = ["E402"]

[tool.ruff.format]
quote-style = "single"      # default is "double"
```

Key defaults if no config exists: `line-length = 88`, `indent-width = 4`,
`target-version = "py311"`, the standard exclude list (`.git`, `venv`, `build`,
`dist`, `node_modules`, `site-packages`, ...), `fixable = ["ALL"]`, and the default rule
set — `F`, `E`, `B`, `UP`, `RUF` categories plus many more, omitting stylistic rules
that overlap with a formatter. Any setting can be overridden from the CLI, e.g.
`ruff check --select F401 --quiet`, or via the catch-all
`--config "lint.per-file-ignores = {'some_file.py' = ['F841']}"`.
`--isolated` ignores all configuration files.

### Rule selection model

Rule codes are Flake8-style (a letter prefix plus digits, e.g. `F401`); selectors accept
a full code, a prefix (`F`), a linter group, or `ALL`. Precedence when reconciling
sources: CLI > current config > inherited config, and `--select` **replaces** the
configured set while `--extend-select` adds to it. In preview mode, selectors and
suppression comments also accept human-readable rule names (e.g. `unused-import`), and
rule categories (`correctness`, `suspicious`, `complexity`, `performance`, `style`,
`security`, `formatting`, `pedantic`, `restriction`) are selectable.

## Gotchas

- **`--select` replaces, it does not extend** — `ruff check --select F401` enforces
  *only* F401, dropping the configured rule set. Use `--extend-select` to add rules on
  top of the configured set.

- **`pyproject.toml` needs the `[tool.ruff]` prefix** — `[lint]` and `[format]` only
  work in `ruff.toml`/`.ruff.toml`. In `pyproject.toml` they must be
  `[tool.ruff.lint]` / `[tool.ruff.format]`.

- **Config files are not merged** — Ruff uses the closest config file only; parent
  configs are ignored. Use `extend = "../pyproject.toml"` for inheritance. If several
  config files exist in the same directory, `.ruff.toml` > `ruff.toml` > `pyproject.toml`.

- **The formatter does not sort imports** — `ruff format` leaves import order alone.
  Run `ruff check --select I --fix` first (issue #8232 tracks a unified command).

- **`E501` and the formatter disagree by design** — the formatter makes only a
  best-effort attempt to stay under `line-length`, so formatted code can still trip
  `E501`. Do not add `E501` to `select` when using `ruff format`.

- **Markdown files are formatted by default** — `*.md` is in the default file discovery
  set and Python code blocks inside Markdown are formatted. Disable with
  `extend-exclude = ["*.md"]` in `[tool.ruff]` if you only want `.py` formatting.

- **Jupyter notebooks are linted and formatted by default** (since 0.6.0). Scope
  exclusions per tool to keep one and drop the other, e.g. `[tool.ruff.format]`
  `exclude = ["*.ipynb"]` formats only `.py` files.

- **Unsafe fixes are not applied by default** — `--fix` applies safe fixes only.
  Add `--unsafe-fixes` to include fixes that may change runtime behavior or remove
  comments. Per-rule overrides exist via `lint.extend-safe-fixes` /
  `lint.extend-unsafe-fixes` (promote/demote specific codes).

- **Preview rules require preview mode** — selecting a preview rule by exact code (or
  prefix, or `ALL`) does nothing unless `--preview` / `preview = true` is enabled.
  Lint and format preview are independent (`[lint] preview` vs `[format] preview`).

- **Files passed directly bypass exclusions** — `ruff check excluded/file.py` always
  analyzes the file unless `--force-exclude` is set. `.gitignore` and other ignore files
  are respected during directory discovery by default (`--no-respect-gitignore` to stop).

- **`# fmt: skip` and `# fmt: off` are statement-scoped** — placing them inside a
  multi-line expression (e.g. between list entries) has no effect. Apply them to the
  entire statement, outside the brackets.

- **Suppression comments have distinct syntaxes** — inline is `# noqa: F841` (Flake8
  style, case-insensitive); line-level is `# ruff: ignore[F841]` on the line *above*;
  block-level is `# ruff: disable[F841]` ... `# ruff: enable[F841]` (codes must match,
  in order); file-level is `# ruff: noqa` or `# ruff: noqa: F841` on its own line.
  `# flake8: noqa` is also honored.

- **Track down stale noqa comments** — enable RUF100 (`unused-noqa`) with
  `--extend-select RUF100` to flag suppression comments that no longer match a
  violation; `--fix` removes them automatically.

- **Formatter-conflicting lint rules** — if you enable `Q`, `COM812`/`COM819`, `D203`,
  `D206`, `D300`, `W191`, `E111`, `E114`, or `E117` alongside `ruff format`, the two
  tools can fight. `ruff format` prints a warning when it detects such a conflict —
  keep the warning-free state.

- **`target-version` is inferred** — when no config sets it, Ruff reads
  `requires-python` from a nearby `pyproject.toml` (behavior can vary by working
  directory). Set it explicitly for reproducible results.

- **`--config` with a file path resolves relative paths against the CWD**, not the
  directory containing the file.

## References

- [01-configuration](references/01-configuration.md) — config file discovery, `extend`, defaults, CLI `--config`, argfiles, file discovery, notebooks
- [02-fixes-and-suppression](references/02-fixes-and-suppression.md) — fix safety levels, `noqa` / `ruff: ignore` / `disable`-`enable` spec, RUF100, `--add-noqa`
- [03-formatter](references/03-formatter.md) — formatter options, docstring and Markdown code formatting, Black deviations, conflicting rules, exit codes
- [04-integrations](references/04-integrations.md) — installation methods, pre-commit, GitHub Actions, versioning policy

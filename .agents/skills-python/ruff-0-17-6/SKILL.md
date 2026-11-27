---
name: ruff-0-17-6
description: >
  Ruff 0.17.6 — an extremely fast Python linter and code formatter. Use this
  skill whenever the user mentions ruff, Python linting, ruff check, ruff
  format, ruff configuration (ruff.toml or pyproject.toml [tool.ruff]), lint
  rule selection, noqa suppressions, unsafe fixes, preview mode, or Python
  formatting. Covers the check and format commands, linter groups, rule
  categories, fix safety, the editor language server, pre-commit, and CI
  integrations.
license: MIT
compatibility: Requires the ruff 0.17.6 binary — install with `uv tool install ruff`, `pip install ruff`, `uvx ruff`, or the standalone installers at astral.sh/ruff (single binary, no Python runtime needed)
metadata:
  tags:
    - python
    - linting
    - formatting
    - code-quality
---

# ruff 0.17.6

## Overview

Ruff is an extremely fast Python linter and code formatter. The linter is a
drop-in replacement for Flake8 (plus dozens of plugins), isort, pydocstyle,
pyupgrade, and autoflake; the formatter is a drop-in replacement for Black with
an excessive focus on performance. It enforces 900+ lint rules split across 59
built-in linter groups.

Two primary entrypoints:

- `ruff check` — lint files (optionally auto-fix with `--fix`)
- `ruff format` — format files (Black-compatible style)

Utility commands: `ruff rule` (explain a rule or all rules), `ruff config`
(list/describe configuration options), `ruff linter` (list supported upstream
linters), `ruff clean` (clear caches), `ruff server` (run the built-in LSP
language server), `ruff analyze` (run analysis over Python source code),
`ruff version`.

Version 0.17.6 (released 2026-11-19) is a patch release: fixes `F823` false
negative on multiple assignment, `RUF072` fix producing a syntax error for
inline `try` bodies, `B033`/`RUF068` parenthesized duplicate items,
`PLR1733`/`PLR1736` false positive when a collection is modified in a loop,
`F841` now ignores `__traceback_hide__`, `SIM208` fixes drop redundant `bool`
wrappers, relative imports from `__future__` are treated as ordinary imports,
plus a new preview-mode fix for `TC010` and performance improvements (JSON
diagnostics streamed, notebook decoding, qualified-name short-circuiting).

## Usage

```bash
# Lint the current directory (config auto-discovered)
ruff check

# Lint specific paths, auto-fixing safe violations
ruff check --fix src/

# Lint and also apply unsafe fixes
ruff check --fix --unsafe-fixes

# Format everything in place / CI check without writing
ruff format
ruff format --check
ruff format --diff

# Explain a rule; list linter groups; clear cache
ruff rule F401
ruff linter
ruff clean
```

Configuration lives in the first `ruff.toml`, `.ruff.toml`, or `pyproject.toml`
(with `[tool.ruff]`) found in the file's directory or any parent directory — the
closest config wins, configs are not merged. Quick example:

```toml
# ruff.toml (or [tool.ruff.*] in pyproject.toml)
line-length = 88
target-version = "py310"

[lint]
select = ["E", "F", "I", "UP", "B"]

[lint.per-file-ignores]
"__init__.py" = ["E402", "F401", "F403"]
```

Typical workflows:

- Introduce linting: run `ruff check` with the default rule set (a great
  starting point — catches unused imports and common errors with zero config),
  then narrow/extend via `select`/`extend-select`.
- Migrate an existing codebase to a new rule: `ruff check --select <CODE>
  --add-noqa` stamps `# noqa` on every existing violation so only new ones fail.
- Sort imports, then format: `ruff check --select I --fix` followed by
  `ruff format` (the formatter does not sort imports).
- CI: `ruff check --output-format=github` (GitHub) or `--output-format=gitlab`
  with `--output-file=code-quality-report.json` (GitLab code-quality report).

Full details in the references below.

## Gotchas

- **`select` replaces the default rule set; `extend-select` adds to it.** Use
  `extend-select = ["B"]` to keep defaults and add flake8-bugbear; `select =
  ["B"]` would disable everything else. CLI options override config-file
  settings, and the current config's `select` is the basis on top of which
  `extend-select`/`ignore` adjustments are applied.
- **Preview rules need preview mode.** A rule in preview is not enabled by
  selecting its code, its prefix, or `ALL` unless `preview = true` (or
  `--preview`) is also set. `explicit-preview-rules = true` forces per-rule
  opt-in even with preview on. Deprecated rules are disabled under preview.
- **`--fix` applies only safe fixes by default.** Fixes are labeled safe or
  unsafe (unsafe can change runtime behavior or drop comments); add
  `--unsafe-fixes` to include them. Per-rule overrides: `lint.extend-safe-fixes`
  and `lint.extend-unsafe-fixes`.
- **The formatter does not sort imports.** Run `ruff check --select I --fix`
  before `ruff format`; there is no unified command yet.
- **Formatted code can still exceed `line-length`** (best-effort wrapping), so
  `E501` may fire after formatting. Also avoid formatter-conflicting rules
  (`W191`, `E111`, `E114`, `E117`, `D203`, `D206`, `D300`, `Q000`–`Q004`,
  `COM812`, `COM819`, `ISC002` without `ISC001`) and incompatible isort settings
  (`force-single-line`, `force-wrap-aliases`, `lines-after-imports`,
  `lines-between-types`, `split-on-trailing-comma`); `ruff format` warns when
  any are enabled.
- **Configs do not cascade/merge** — the closest config file wins; parent
  configs are ignored. Use the `extend` field to inherit another file. In one
  directory, `.ruff.toml` beats `ruff.toml`, which beats `pyproject.toml`. A
  `pyproject.toml` without a `[tool.ruff]` section is ignored.
- **`# fmt: off`/`# fmt: on` are statement-level**, not expression-level —
  inside a list literal they do nothing; put the comment before the whole
  statement. `# fmt: skip` covers a case header, decorator, def, class, or the
  preceding statements on the same logical line; at the end of an expression it
  has no effect.
- **Files passed on the CLI are always analyzed** (even if excluded/ignored)
  unless `--force-exclude` is set; gitignore-based skipping applies to
  discovery, not explicit paths.
- **Exit codes** — `ruff check`: 0 clean (or all fixed), 1 violations, 2
  invalid config/CLI/internal error; `--exit-zero` and
  `--exit-non-zero-on-fix` alter this. `ruff format` exits 0 even when it
  formats files; `--check`/`--diff` exit 1 when any file would change.
- **`noqa` placement matters** — for an import block, `# noqa: CODE` goes on
  the *first* line of the block to cover all imports; for multi-line strings it
  goes after the closing quotes; file-level suppression is `# ruff: noqa` (own
  line), not `# noqa`.
- **Unmatched `# ruff: disable[X]` creates an implicit range** (until the
  enclosing scope ends) and triggers the `RUF104` diagnostic — prefer explicit
  `# ruff: enable[X]`.
- **`target-version` is inferred** from `requires-python` in a nearby
  `pyproject.toml` when no config sets it; pass `--config` directly and no
  inference happens.
- **`--config` takes either a path or a TOML `key = value` pair**; linter
  settings need the `lint.` prefix, formatter settings `format.`. A dedicated
  flag (e.g., `--line-length`) beats a `--config` override of the same option.

## References

- [01-cli](references/01-cli.md) — `ruff check` and `ruff format` flags, utility commands, output formats, env vars, argfiles, exit codes
- [02-configuration](references/02-configuration.md) — config file discovery, schema, defaults, per-file-ignores, `--config` overrides, target-version inference
- [03-rules](references/03-rules.md) — the 59 linter groups, rule selection semantics, rule categories, preview rules, 0.17.6 rule changes
- [04-fixes-and-suppression](references/04-fixes-and-suppression.md) — fix safety, fixable/unfixable, `noqa`/`ignore`/`disable`/`enable`/`file-ignore`, `RUF100`, `--add-noqa`/`--add-ignore`
- [05-formatter](references/05-formatter.md) — Black compatibility, f-string formatting, docstring code, Markdown, notebooks, `fmt:` comments, exit codes
- [06-integrations](references/06-integrations.md) — pre-commit, GitHub Actions, GitLab CI, Docker, editor LSP, shell completions

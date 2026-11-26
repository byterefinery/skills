---
name: ty-0-0-111
description: Extremely fast Python type checker and language server (ty 0.0.111) written in Rust by Astral. Use when the user wants to type-check Python code with ty, run ty check or ty server, configure ty in pyproject.toml or ty.toml, set rule severity, suppress diagnostics with ty or type ignore comments, control the target Python version or platform, resolve import errors, manage PEP 723 inline-metadata scripts, create diagnostic baselines, or migrate from mypy or Pyright. Covers installation, CLI reference, 163 rules, configuration, suppression, and exit codes.
license: MIT
compatibility: Requires the ty 0.0.111 binary (uvx ty, uv tool install ty, pip install ty, or the standalone installer); the standalone build does not require a Python interpreter
metadata:
  tags:
    - python
    - type-checking
    - cli
    - linter
---

# ty 0.0.111

## Overview

ty is an extremely fast Python type checker and language server, written in Rust, by Astral (creators of uv and Ruff). It is 10x-100x faster than mypy or Pyright (e.g. type-checks home-assistant/core uncached in seconds) and is designed for gradual adoption — redeclarations and partially typed code are supported.

Commands (all documented in [01-cli-reference](references/01-cli-reference.md)):

- `ty check [PATH]...` — type check a project or given paths; supports `--fix`, rule severities, watch mode, baselines, and CI output formats
- `ty server` — language server for editor integration (diagnostics, completions, hover, go-to-definition, inlay hints, fine-grained incrementality)
- `ty explain rule [RULE]` — explain one rule or all of them (`--output-format json` for machine-readable)
- `ty version`, `ty generate-shell-completion <SHELL>` — utilities

Status is **beta** (0.0.x): breaking changes, including to diagnostics, may occur between any two versions. Officially supported target: Python 3.10+; 3.7-3.9 can be selected but may give false positives/negatives because the bundled stdlib stubs do not fully describe those versions.

## Usage

### Getting started

```bash
uvx ty check                          # try without installing
uv add --dev ty && uv run ty check    # pin a version in the project (recommended)
uv tool install ty@latest             # or install globally (upgrade with uv tool upgrade ty)
pipx install ty                       # or pip install ty
curl -LsSf https://astral.sh/ty/install.sh | sh   # standalone installer (no Python needed)
```

```bash
ty check                 # check the project (all Python files under the project root or cwd)
ty check src file.py     # check specific files/directories
ty check --watch         # re-check incrementally as files change
ty check --fix           # apply fixes to resolve errors
ty explain rule invalid-assignment   # explain one rule (omit RULE for all)
```

Docker: `COPY --from=ghcr.io/astral-sh/ty:latest /ty /bin/` (tags: `latest`, `{major}.{minor}.{patch}` like `0.0.111`, `{major}.{minor}`).

**Environment discovery** — ty resolves third-party imports through, in order: an active virtualenv (`VIRTUAL_ENV`), an active non-`base` Conda/Pixi env containing Python, a `.venv` at the project root, an active `base` Conda env, then a `python3`/`python` binary on `PATH`. `PYTHONPATH` directories are added just before the environment's `site-packages`. Run via `uv run` or with an activated env and discovery just works; otherwise point `--python` (alias `--venv`) at an interpreter, a venv directory, or a `sys.prefix` directory.

**First-party module roots** — the project root plus, if they exist and are not packages: `./src`, `./<project-name>` (if `./<project-name>/<project-name>` exists), `./python` — searched before the project root in that order. Configure with `environment.root`.

### Configuration

- Project config: `[tool.ty]` table in `pyproject.toml`, or a `ty.toml` file (same structure, no `[tool.ty]` prefix). Searched in the cwd and up the directory tree. **`ty.toml` wins over `pyproject.toml`** when both exist in one directory.
- User config: `~/.config/ty/ty.toml` (or `$XDG_CONFIG_HOME/ty/ty.toml`; Windows `%APPDATA%\ty\ty.toml`); project settings take precedence, arrays merge.
- Command line: `--config KEY=VALUE` overrides a single option and always wins; `--config-file PATH` (or `TY_CONFIG_FILE`) forces a specific `ty.toml`-format file.

```toml
# pyproject.toml
[tool.ty.rules]
division-by-zero = "ignore"
possibly-unresolved-reference = "warn"
```

Full option reference with defaults: [02-configuration](references/02-configuration.md).

### Rule levels

Every rule has a level — `error`, `warn`, or `ignore`. Set levels on the command line (`--warn`, `--error`, `--ignore`; repeatable, `all` targets every rule, later options override earlier ones) or in the `[tool.ty.rules]` section (`all` works there too). All 163 rules with default levels: [03-rules](references/03-rules.md), or query any rule live with `ty explain rule <name>`.

Exit code behavior: **`terminal.error-on-warning` defaults to `true`, so by default any warning also exits 1**. For a warnings-are-ok CI gate, pass `--exit-zero-on-warning` (exit 1 only on error-level findings) or set `terminal.error-on-warning = false`. `--error-on-warning` cannot be combined with `--exit-zero` or `--exit-zero-on-warning`.

| Exit code | Meaning |
|---|---|
| 0 | no warning-or-higher diagnostics |
| 1 | warning- or error-level diagnostics found |
| 2 | invalid CLI options, invalid configuration, or IO error |
| 101 | internal error |

### Suppressing diagnostics

Inline, at the end of the offending line (for multi-line violations, the first or last line):

```py
a = 10 + "test"  # ty: ignore[unsupported-operator]
```

- Enumerate rules with commas `# ty: ignore[missing-argument, invalid-argument-type]`; always name the rules — a bare `# ty: ignore` suppresses everything on the line.
- Whole file: `# ty: ignore[<rule>]` on its own line before any Python code.
- Standard `type: ignore` (all on the line) and `type: ignore[ty:<rule>]` are respected, so mypy/ty suppressions can coexist in one comment; `@no_type_check` suppresses an entire function (not classes). Unused suppression comments are warned about by default. Details: [04-suppression](references/04-suppression.md).

**Baselines** (preview) — for legacy code, record existing violations in a JSON file so only new violations fail the run: `ty check --update-baseline --baseline ty-baseline.json`, then pass `--baseline ty-baseline.json` or set `baseline` in config. Update after fixing violations or file renames.

### PEP 723 standalone scripts

Files with `# /// script` inline metadata are checked as part of the project by default (`src.exclude-scripts` defaults to `false`; CLI `--exclude-scripts` excludes them unless passed explicitly). By default ty looks for their dependencies in the project's Python environment; to give each script its own uv-managed environment (preview, requires uv 0.12.3+), set `project-manager.script = "uv"` — or pass `--config 'project-manager.script="uv"'` for one invocation, or use `uv check --script example.py`. A script can carry its own `[tool.ty]` table in the inline metadata, which replaces project settings for that script.

### Output and CI

`--output-format` (env `TY_OUTPUT_FORMAT`): `full` (default, with context and hints), `concise` (one per line), `github`, `gitlab`, `junit`, `sarif` — the last four for CI reports. `--quiet` (or `-qq` for silent) reduce chatter; `--no-progress` hides spinners; `--color auto|always|never` controls color (also via `NO_COLOR`, `FORCE_COLOR`, `CLICOLOR`).

## Gotchas

- **Warnings fail by default** — `terminal.error-on-warning` defaults to `true`, so a run with only warnings exits 1. Use `--exit-zero-on-warning` or set it to `false` for a warnings-tolerant CI gate.
- **`ty.toml` beats `pyproject.toml`** — if both exist in the same directory, the `[tool.ty]` section is ignored entirely.
- **Positional paths bypass excludes** — paths passed directly to `ty check` are checked even if `src.exclude` or `.gitignore`/`.ignore` would ignore them; use `--force-exclude` to enforce exclusions anyway. `--respect-ignore-files` (default on) honors ignore files for non-explicit paths.
- **Glob patterns are anchored** — `src` only matches `<project_root>/src`, not `<project_root>/test/src`; use `**/src` to match any directory named `src`. `**` must form a single path component (`**a` and `b**` are invalid errors), as is any run of more than two `*`. A prefix include like `**/src` can notably slow file discovery.
- **Default `python-version` is `"3.15"`** — inference order: CLI/config first, then the *minimum* of `project.requires-python` in `pyproject.toml`, then the active environment, then the built-in default. Targeting below 3.10 risks stdlib false positives/negatives.
- **PEP 723 scripts are special** — they use their own Python environment (not the project's `.venv`), their own `requires-python`/`python-version`, and their inline `[tool.ty]` table (if present) replaces project settings entirely, even when empty. Dependency sync via uv is **off by default** (`project-manager.script = "none"`); missing imports in scripts usually mean the packages are not installed in the discovered environment.
- **Beta API** — 0.0.x means diagnostics, rules, and config options can change between versions; pin the version (`uv add --dev 'ty==0.0.111'` or `uv tool install ty@0.0.111`) where reproducibility matters. Baselines and `project-manager` settings are preview and may change.
- **No strict mode exists** — ty's default is already stricter than mypy/Pyright defaults (checks untyped function bodies unconditionally, infers `[1, "foo"]` as `list[int | str]`); there is no `--check-untyped-defs` or `strictListInference` equivalent. To approximate strict, see [05-migration](references/05-migration.md).
- **`unresolved-import` is usually an environment problem** — before disabling rules, verify env discovery (`.venv`, `VIRTUAL_ENV`, `--python`). `analysis.allowed-unresolved-imports` suppresses errors for specific unresolvable modules; `analysis.replace-imports-with-any` types matching modules as `Any` even when resolvable.

## References

- [01-cli-reference](references/01-cli-reference.md) — full options for `ty check`, `ty server`, `ty explain`, `ty version`, `ty generate-shell-completion`, plus environment variables
- [02-configuration](references/02-configuration.md) — all configuration options with defaults: baseline, rules, analysis, environment, overrides, project-manager, src, terminal
- [03-rules](references/03-rules.md) — all 163 rules with their default levels and one-line descriptions
- [04-suppression](references/04-suppression.md) — suppression comments, standard `type: ignore`, `@no_type_check`, unused-ignore rules, baselines
- [05-migration](references/05-migration.md) — coming from mypy or Pyright: migration tips, strict-mode approximation, rule mapping table

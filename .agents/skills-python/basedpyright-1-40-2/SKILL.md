---
name: basedpyright-1-40-2
description: >
  BasedPyright 1.40.2 — strict, opinionated fork of the Pyright Python type checker.
  Installs from PyPI without Node.js and re-implements Pylance features for any LSP
  editor. Use this skill whenever the user mentions basedpyright, pyright, Python type
  checking, static typing, type annotations, pyrightconfig.json, [tool.basedpyright],
  or Python type errors. Covers installation via uv or pip, CLI usage and exit codes,
  the strict-by-default recommended mode, basedpyright-exclusive diagnostic rules,
  baselining legacy code, pyright ignore comments, configuration, import resolution
  and type stubs, IDE setup, and CI integration.
metadata:
  tags:
    - python
    - type-checking
    - static-analysis
    - pylance
---

# basedpyright 1.40.2

## Overview

BasedPyright is a strict, opinionated fork of Pyright (Microsoft's Python static type
checker); a new basedpyright release follows each upstream Pyright release within a day.
It installs from PyPI without Node.js (the `basedpyright` CLI and
`basedpyright-langserver` LSP executables), re-implements Pylance-exclusive features so
they work in any LSP editor, and is strict by default.

Key differences from plain Pyright:

- **Strict by default** — `typeCheckingMode` defaults to `"recommended"`, which enables
  every diagnostic rule as `"error"` or `"warning"`, and `failOnWarnings` is on, so even
  warnings fail the CLI (exit code 1). Disable with `failOnWarnings: false`.
- **New basedpyright-exclusive diagnostic rules** — `reportAny`, `reportExplicitAny`,
  `reportInvalidCast`, `reportImplicitRelativeImport`, `reportImplicitAbstractClass`, and
  more. Details in [01-diagnostic-rules](references/01-diagnostic-rules.md).
- **`# type: ignore` is disabled by default** — use `# pyright: ignore[rule]` instead.
- **Baselining** — adopt strict checking in a legacy codebase without fixing old code.
  Existing errors are frozen in `./.basedpyright/baseline.json`; the file auto-updates as
  errors are fixed, and CI runs in lock mode by default.
- **Sane environment defaults** — `pythonPlatform` defaults to `"All"` (not the host OS)
  and the Python interpreter falls back to a `.venv` folder at the project root, making
  the confusing `venv`/`venvPath` settings unnecessary (they are discouraged).
- **`typeCheckingMode: "off"` is literally off** — all type-checking rules disabled,
  while Python syntax and semantic errors are still reported.
- **Pylance features in any editor** — Jupyter notebook type checking (even from the
  CLI), import suggestion and ignore-comment code actions, semantic highlighting, inlay
  hints, docstrings for compiled builtin modules, renaming across modules.
- **Built-in CI integration** — GitHub Actions pull-request annotations out of the box;
  GitLab code-quality reports via `--gitlabcodequality`.

It deliberately does **not** support the Type Server Protocol.

## Usage

### Installation

```bash
# PyPI (recommended — no Node.js needed)
uv add --dev basedpyright        # project dev dependency
uv tool install basedpyright     # global CLI + language server
pip install basedpyright

# Alternatives
conda install conda-forge::basedpyright
brew install basedpyright
npm install basedpyright         # only if the PyPI wheel can't be used
```

Once installed, `basedpyright` (CLI) and `basedpyright-langserver` (LSP) are on PATH.

### Command line

```bash
basedpyright                    # check project per pyrightconfig.json / [tool.basedpyright]
basedpyright path/to/file.py    # explicit files override config include paths
basedpyright --outputjson       # machine-readable diagnostics
basedpyright -w                 # watch mode, incremental re-analysis
basedpyright --level warning    # minimum diagnostic level to report
basedpyright --pythonpath .venv/bin/python   # pin interpreter (preferred over --venvpath)
```

Key flags: `--createstub <IMPORT>`, `--verifytypes <IMPORT>` (check completeness of a
`py.typed` package's types), `--dependencies`, `--threads [N]` (experimental parallelism),
`--stats`, `--verbose`, `--pythonversion 3.12`, `--pythonplatform All`.

Exit codes: `0` no errors, `1` errors reported (or warnings with `failOnWarnings`),
`2` fatal error, `3` config file unreadable, `4` illegal CLI parameters.

### Configuration

Config lives in `pyrightconfig.json` at the project root or a `[tool.basedpyright]`
section of `pyproject.toml` (`[tool.pyright]` also works for compatibility). A
`pyrightconfig.json` always takes precedence over `pyproject.toml`. Minimal example:

```jsonc
{
  "include": ["src"],
  "exclude": ["**/node_modules", "**/__pycache__"],
  "typeCheckingMode": "recommended",
  "failOnWarnings": true,
  "pythonVersion": "3.12"
}
```

Per-file control via comments: `# pyright: strict`, `# pyright: basic`, or individual
overrides like `# pyright: reportPrivateUsage=warning`. Line suppression:
`# pyright: ignore[reportUnreachable]` (always include the rule name so future, different
errors on that line still surface). Full config reference in
[02-configuration](references/02-configuration.md).

### Baseline workflow for legacy code

```bash
basedpyright --writebaseline    # freeze existing errors into ./.basedpyright/baseline.json
```

Commit the baseline file. Afterwards only new or modified code reports; fixed errors are
removed from the baseline automatically locally, while CI runs in lock mode (non-zero exit
if the baseline is stale). See [02-configuration](references/02-configuration.md) for
`--baselinemode auto|lock|discard`.

## Gotchas

- **Warnings fail the CLI by default** — `failOnWarnings` is on, so a run that looks "clean"
  in your head can still exit 1. Set `"failOnWarnings": false` if you only want hard errors
  to block CI.
- **`# type: ignore` does nothing out of the box** — `enableTypeIgnoreComments` is disabled
  by default; use `# pyright: ignore[rule]`. Enabling `type: ignore` support is explicitly
  discouraged.
- **Use `--pythonpath`, not `--venvpath`/`venvPath`** — the venv settings are discouraged;
  basedpyright already auto-detects `./.venv` at the project root when no interpreter is set.
- **`reportInvalidCast` fires on dict → TypedDict casts** — even though this is a common
  pattern, type checkers treat `TypedDict` as unrelated to `dict`, so the cast errors under
  that rule.
- **Baseline file is a lockfile in CI** — CI defaults to lock mode; if contributors fix code
  without updating the baseline, CI fails until they commit the updated file.
- **`typeCheckingMode: "off"` still reports syntax/semantic errors** — it only disables
  type-checking rules, unlike pyright which still emits some warnings in off mode.

## References

- [01-diagnostic-rules](references/01-diagnostic-rules.md) — basedpyright-exclusive diagnostic rules and what each catches
- [02-configuration](references/02-configuration.md) — config file options, environment settings, baseline modes
- [03-imports-and-stubs](references/03-imports-and-stubs.md) — import resolution, interpreter selection, type stubs
- [04-ides-and-ci](references/04-ides-and-ci.md) — language server setup in editors and CI integration

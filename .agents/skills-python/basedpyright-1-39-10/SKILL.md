---
name: basedpyright-1-39-10
description: >
  BasedPyright 1.39.10 — strict, opinionated fork of the Pyright Python type checker.
  Installs from PyPI without Node.js and re-implements Pylance features for any LSP
  editor. Use this skill whenever the user mentions basedpyright, pyright, Python type
  checking, static typing, type annotations, pyrightconfig.json, [tool.basedpyright],
  or Python type errors. Covers installation via uv or pip, CLI usage and exit codes,
  the strict-by-default recommended mode, 14 basedpyright-exclusive diagnostic rules,
  baselining legacy code, pyright ignore comments, configuration, import resolution and
  type stubs, IDE setup, and CI integration.
metadata:
  tags:
    - python
    - type-checking
    - static-analysis
    - pylance
---

# basedpyright 1.39.10

## Overview

BasedPyright is a strict, opinionated fork of Pyright (Microsoft's Python static type
checker); a new basedpyright release follows each upstream Pyright release within a day.
It installs from PyPI without Node.js (the `basedpyright` CLI and
`basedpyright-langserver` LSP executables), re-implements Pylance-exclusive features so
they work in any LSP editor, and is strict by default.

Key differences from plain Pyright:

- **Strict by default** — `typeCheckingMode` defaults to `"recommended"`, which enables
  every diagnostic rule as `"error"` or `"warning"`, and `failOnWarnings` is on, so even
  warnings fail the CLI.
- **14 new diagnostic rules** — `reportAny`, `reportExplicitAny`, `reportInvalidCast`,
  `reportImplicitRelativeImport`, `reportImplicitAbstractClass`, and more, all on by
  default. Details in [01-diagnostic-rules](references/01-diagnostic-rules.md).
- **`# type: ignore` is disabled by default** in the default modes — use
  `# pyright: ignore[rule]` instead.
- **Baselining** — adopt strict checking in a legacy codebase without fixing old code.
  Existing errors are frozen in `./.basedpyright/baseline.json` and only new or modified
  code reports.
- **Sane environment defaults** — `pythonPlatform` defaults to `"All"` (not the host OS)
  and the Python interpreter falls back to a `.venv` folder at the project root, making
  the confusing `venv`/`venvPath` settings unnecessary (they are discouraged).
- **`typeCheckingMode: "off"` is literally off** — all rules disabled, while Python
  syntax and semantic errors are still reported.
- **Pylance features in any editor** — Jupyter notebook type checking (even from the
  CLI), import suggestion and ignore-comment code actions, semantic highlighting, inlay
  hints, docstrings for compiled builtin modules, renaming across modules.
- **Built-in CI integration** — GitHub Actions pull-request annotations out of the box;
  GitLab code-quality reports via `--gitlabcodequality`.

It deliberately does **not** support the Type Server Protocol.

## Usage

### Installation

```bash
uv add --dev basedpyright        # recommended, project dev dependency
uv tool install basedpyright     # global install
pip install basedpyright
# also available: conda install conda-forge::basedpyright, brew install basedpyright
```

Adding it as a project dev dependency is recommended so the VS Code extension and the
CLI use the same pinned version and never disagree. The PyPI package requires
Python 3.8+; `npm install basedpyright` is a fallback only for OSes or older Python
versions the PyPI package does not support.

### CLI

```bash
basedpyright                  # check the project (pyrightconfig.json or [tool.basedpyright])
basedpyright src/ main.py     # explicit paths override the config's include
basedpyright -w               # watch mode with incremental re-analysis
basedpyright --outputjson     # machine-readable JSON diagnostics
basedpyright --level warning  # minimum severity to report
basedpyright --createstub django  # draft .pyi stubs for an import
basedpyright --verifytypes pkg     # check typing completeness of a py.typed package
basedpyright --version
```

Exit codes — `0` clean; `1` errors reported (warnings too, since `failOnWarnings` is
on by default); `2` fatal error; `3` config file unreadable or unparsable; `4` bad CLI
arguments. The full flag table, JSON schema, and GitLab report output are in
[02-configuration](references/02-configuration.md).

### Configuration

Configure in `pyrightconfig.json` at the project root or in a `[tool.basedpyright]`
table in `pyproject.toml` (a `[tool.pyright]` table is also read for compatibility;
`pyrightconfig.json` wins when both exist). Commit the config so editor and CLI behave
identically for everyone. Minimal example:

```toml
[tool.basedpyright]
include = ["src"]
# reportMissingTypeStubs = "none"   # override any individual rule
```

Useful basedpyright-exclusive settings — `failOnWarnings` (default on in
`recommended`), `allowedUntypedLibraries` (silence unknown-type rules for named untyped
libraries), `baselineFile`, `strictGenericNarrowing` (default on in `recommended`),
`enableBasedFeatures` (unlocks extra `dataclass_transform` options; keep off in public
libraries). The full setting reference is in
[02-configuration](references/02-configuration.md).

### Suppression comments

```python
# pyright: strict                          # strict mode for this file
# pyright: reportPrivateUsage=false         # per-file rule override
# pyright: reportMissingTypeStubs=warning   # per-file severity

value = get_thing()  # pyright: ignore[reportAny]
```

Always bracket a rule name — `reportIgnoreCommentWithoutRule` is on by default in
`recommended`, and bare `# pyright: ignore` suppresses everything on the line. Do not
enable `enableTypeIgnoreComments` or use `# type: ignore`; those comments bypass
rule-name validation and are off in the default modes.
`reportUnnecessaryTypeIgnoreComment` (on by default in `recommended`) flags stale
comments so they can be deleted.

### Baseline (legacy code adoption)

```bash
basedpyright --writebaseline   # freeze current errors in ./.basedpyright/baseline.json
```

Commit the baseline file; from then on only new or modified code reports errors. The
file shrinks automatically as errors are fixed, in both the CLI and the editor. In CI
the baseline is locked and the run fails if it is stale. Rerun `--writebaseline` only
when intentionally baselining new errors, e.g. after enabling a rule. Baseline matching
uses file path + rule + column, so adding or removing lines is safe, but moving code
can resurface baselined errors — regenerate the baseline in that case.

### IDE and language server

```bash
basedpyright-langserver --stdio   # for any LSP client
```

- **Neovim** — `vim.lsp.enable("basedpyright")` (nvim-lspconfig)
- **VS Code / VSCodium** — the `detachhead.basedpyright` extension uses the PyPI
  package from your environment; see the gotchas for the `ms-python` requirement
- **Emacs** — default server in lsp-bridge, or eglot / lsp-pyright
- **Zed / PyCharm / Vim / Sublime / Helix** — see
  [04-ides-and-ci](references/04-ides-and-ci.md)

Useful LSP commands — "Organize Imports" (ruff is recommended for import sorting
instead), "Restart Server" (after installing new stubs or packages), and "Write new
errors to baseline".

### CI

GitHub Actions — just run `basedpyright`; it detects the environment and annotates
pull requests automatically, no wrapper action needed.

GitLab:

```yaml
basedpyright:
  script: basedpyright --gitlabcodequality report.json
  artifacts:
    reports:
      codequality: report.json
```

## Gotchas

- **Everything is on by default** — `recommended` enables every rule; expect a flood on
  a legacy project. Use baselining or override individual rules to `"none"`/`"warning"`
  rather than dropping `typeCheckingMode` to a pyright mode, which also disables the
  basedpyright rules, `failOnWarnings`, and `strictGenericNarrowing`.
- **Warnings fail the build** — `failOnWarnings` is on in `recommended` and `all`; set
  `"failOnWarnings": false` to phase in fixes.
- **`hint` is invisible in the CLI** — rules at `"hint"` severity are language-server
  only (e.g. `reportUnusedParameter` in the pyright modes); the CLI never reports them
  and they never fail the build. Use `"none"` to silence everywhere.
- **`# type: ignore` does nothing in the default modes** — `enableTypeIgnoreComments`
  is off in `recommended`/`all` (back on in `basic`/`standard`/`strict`); porting a
  pyright project means converting those comments to `# pyright: ignore[...]`.
- **`strictGenericNarrowing` is on in `recommended`/`all` but off in `strict`** —
  narrowing `isinstance(x, list)` on `object` yields `list[object]` or
  `list[<bound>]` instead of `list[Unknown]`; expect stricter inferred types in the
  default modes.
- **Baseline auto-update differs by environment** — locally the baseline shrinks
  automatically; in CI it is locked and a stale baseline fails the run.
  `--baselinemode` (experimental) offers `auto`/`lock`/`discard` if more control is
  needed.
- **Baselined errors resurface when moving code** — matching is path + rule + column
  only; regenerate with `--writebaseline` rather than scattering ignore comments.
- **`reportImplicitAbstractClass` (error by default)** — a subclass of an `ABC` is
  implicitly abstract; to keep it abstract it must also inherit `ABC` explicitly
  (`class Impl(AbstractFoo, ABC)`), otherwise instantiating it errors.
- **`reportInvalidCast` (error by default) flags `dict` to `TypedDict` casts** —
  `TypedDict` is a non-overlapping subtype of `Mapping` for the checker, so the common
  `cast(MyDict, d)` idiom errors; build the TypedDict explicitly or disable the rule.
- **`reportImplicitRelativeImport` (error by default)** — inside a package,
  `import sibling` works when run as a script but crashes when imported as a module;
  use `from . import sibling`.
- **Re-exports need the redundant alias** — importing a non-exported name from your own
  modules errors (`reportPrivateLocalImportUsage`) unless it is re-exported as
  `from .m import x as x`.
- **`venv`/`venvPath`/`--venvpath` are discouraged** — `pythonPath` (or the automatic
  `./.venv` detection) is the recommended mechanism.
- **`pythonPlatform` defaults to `"All"`** — expect diagnostics about
  platform-specific imports that host-OS-only setups would not flag.
- **`reportIncompatibleUnannotatedOverride` is off even in `recommended`** (on in
  `all`, for now) — use `reportUnannotatedClassAttribute` (warning by default in
  `recommended`) for equivalent protection.
- **Extra `dataclass_transform` options need `enableBasedFeatures`** — `skip_replace`
  (and `frozen_default`) are ignored unless `enableBasedFeatures = true`; keep it off
  when shipping libraries for pyright users.
- **The VS Code extension crashes without `ms-python`** when basedpyright is installed
  in a virtual environment — install the Python extension or set
  `"basedpyright.importStrategy": "useBundled"`.
- **A committed config overrides editor settings** — if `pyrightconfig.json` or a
  basedpyright/pyright pyproject table exists, discouraged language-server settings
  (e.g. in VS Code `settings.json`) are ignored.
- **The language server analyzes only open files by default**
  (`basedpyright.analysis.diagnosticMode: "openFilesOnly"`), while the CLI checks the
  whole workspace — editor and CI can disagree on file coverage.
- **`--createstub` drafts need cleanup** — generated stubs drop unreferenced re-export
  imports and `try`-wrapped imports; review them before committing under `stubPath`
  (default `./typings`).
- **Type Server Protocol is unsupported by design** — do not point
  `pyright-typeserver` clients at basedpyright; use the LSP or CLI.
- **The "Organize Imports" command has no CLI counterpart** — the docs recommend ruff
  for import sorting when CI validation is needed.

## References

- [01-diagnostic-rules](references/01-diagnostic-rules.md) — the six type-checking modes, the full default-severity table, and the 14 basedpyright-exclusive rules with examples
- [02-configuration](references/02-configuration.md) — config files, every setting, the full CLI flag table, JSON output, environment variables, locales
- [03-imports-and-stubs](references/03-imports-and-stubs.md) — import resolution order, Python environment configuration, editable installs, type stubs and `--createstub`
- [04-ides-and-ci](references/04-ides-and-ci.md) — per-editor setup, language-server settings and commands, Pylance feature parity, GitHub/GitLab CI, prek hook

# IDE Setup and CI Integration

## Language server in editors

`basedpyright-langserver` (installed alongside the CLI via PyPI) is a standard LSP server;
most editor plugins require it to be on PATH.

### VS Code / VSCodium

Install the `detachhead.basedpyright` extension (VS Code Marketplace or open VSX). It
auto-detects the PyPI package in your Python environment. Recommend the extension in
`.vscode/extensions.json`:

```json
{ "recommendations": ["detachhead.basedpyright"] }
```

Known issue: if `basedpyright` is installed in a venv and the Microsoft Python extension
(`ms-python`) is not installed, the VS Code extension crashes on load (auto interpreter
detection comes from `ms-python`). Workarounds: install `ms-python`, or set
`"basedpyright.importStrategy": "useBundled"` in `.vscode/settings.json`.

Using basedpyright alongside Pylance is not recommended; if you must, disable pylance's
type checking (`python.analysis.typeCheckingMode: "off"`) and basedpyright's language
services (`basedpyright.disableLanguageServices: true`).

### Neovim

Use the built-in `nvim-lspconfig` adapter (Neovim 0.11+):

```lua
vim.lsp.enable("basedpyright")
```

The LSP server command comes from the PyPI package (or Mason.nvim).

## CI integration

### GitHub Actions — automatic, no setup

basedpyright detects it is running in a GitHub Action and emits [workflow commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions),
so diagnostics appear as annotations on the affected lines of pull requests with no
third-party action or boilerplate:

```yaml
jobs:
  check:
    steps:
      - run: ... # checkout, install deps
      - run: basedpyright
```

Note CI also defaults baseline mode to `lock` (see 02-configuration.md) — a stale
`baseline.json` fails the job until it's committed.

### GitLab code quality report

```yaml
basedpyright:
  script: basedpyright --gitlabcodequality report.json
  artifacts:
    reports:
      codequality: report.json
```

## JSON output for custom tooling

`--outputjson` emits `version`, `time`, `generalDiagnostics[]` (each with `file`,
`severity`, `message`, optional `rule`, and zero-based `range`), and a `summary` with
`filesAnalyzed`, `errorCount`, `warningCount`, `informationCount`, `timeInSec`.

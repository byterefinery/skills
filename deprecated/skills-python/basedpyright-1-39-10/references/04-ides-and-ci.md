# IDEs, language server, and CI

## Contents

- [Pinning the version](#pinning-the-version)
- [Editor setup](#editor-setup)
- [Language server settings](#language-server-settings)
- [Language server commands](#language-server-commands)
- [Pylance feature parity](#pylance-feature-parity)
- [CI](#ci)
- [prek hook](#prek-hook)

## Pinning the version

Install and pin basedpyright as a project dev dependency
(`uv add --dev basedpyright`) and point editors at that version. The VS Code extension
uses the PyPI package from your environment automatically, and Zed can be pinned via
`.zed/settings.json`:

```json
{
  "lsp": {
    "basedpyright": {
      "binary": {
        "path": ".venv/bin/basedpyright-langserver",
        "arguments": ["--stdio"]
      }
    }
  }
}
```

Commit such files so editor and CI use the same version.

## Editor setup

All of these need the `basedpyright-langserver` executable from the PyPI package
(plus an LSP client where noted).

### VS Code / VSCodium

Install the `detachhead.basedpyright` extension (marketplace / VSX registry). Commit a
recommendation file:

```json
{ "recommendations": ["detachhead.basedpyright"] }
```

Known issue — if basedpyright is installed in a virtual environment and the
`ms-python` extension is not installed, the extension crashes on load. Workarounds:
install `ms-python`, or set `"basedpyright.importStrategy": "useBundled"`.

If you keep Pylance installed for features not yet ported, disable its type checking
and basedpyright's language services so they do not conflict:

```json
{
  "python.analysis.typeCheckingMode": "off",
  "python.languageServer": "Pylance",
  "basedpyright.disableLanguageServices": true
}
```

### Neovim

With `nvim-lspconfig` (or Mason):

```lua
vim.lsp.enable("basedpyright")  -- Neovim 0.11+

-- legacy 0.10
require("lspconfig").basedpyright.setup{}
```

### Vim, Sublime, Emacs, PyCharm, Helix, Zed

- **Vim** — `coc-basedpyright`
- **Sublime Text** — `LSP` + `LSP-basedpyright` via Package Control
- **Emacs** — lsp-bridge (basedpyright is the default Python server), eglot
  (`"basedpyright-langserver" "--stdio"`), or lsp-pyright
  (`(setq lsp-pyright-langserver-command "basedpyright")`)
- **PyCharm** — enable the basedpyright external tool under
  Python > Tools > External Tools; commit `.idea/pyLspTools.xml` (use
  `git add -f`, the directory is hidden by default)
- **Helix** — add `language-servers = [ "basedpyright" ]` to the python language
  config; verify with `hx --health python`
- **Zed** — basedpyright is the default Python language server; pin the binary in
  `.zed/settings.json` (see above)

## Language server settings

Settings prefixed `python.*` are **not** supported (except `python.pythonPath` and
`python.venvPath`) — use `basedpyright.*`.

General:

| Setting | Default | Notes |
|---|---|---|
| `basedpyright.disableLanguageServices` | false | Keep type checking only; use another LSP for hover/completion/definitions |
| `basedpyright.disableOrganizeImports` | false | Avoid fighting another import-sorting extension |
| `basedpyright.disableTaggedHints` | false | Disable grey-out / strikethrough hint styling |
| `basedpyright.analysis.autoImportCompletions` | true | Auto-import completions while typing (does not affect the `reportUndefinedVariable` import-suggestion code actions — disable that rule to turn those off) |
| `basedpyright.analysis.autoSearchPaths` | true | Auto-add `src`-like paths when no execution environments are defined |
| `basedpyright.analysis.diagnosticMode` | `openFilesOnly` | `openFilesOnly` or `workspace` (analyzes the whole project like the CLI) |
| `basedpyright.analysis.logLevel` | `Information` | `Error`, `Warning`, `Information`, or `Trace` |
| `python.pythonPath` | — | Interpreter path (VS Code Python extension picker works) |

BasedPyright-exclusive analysis settings:

| Setting | Default | Notes |
|---|---|---|
| `basedpyright.analysis.inlayHints.variableTypes` | true | Hints on variable assignments |
| `basedpyright.analysis.inlayHints.callArgumentNames` | true | Hints on call arguments |
| `basedpyright.analysis.inlayHints.callArgumentNamesMatching` | false | Argument hints when the variable already matches the parameter name |
| `basedpyright.analysis.inlayHints.functionReturnTypes` | true | Hints on return types |
| `basedpyright.analysis.inlayHints.genericTypes` | true | Hints on inferred generic type arguments |
| `basedpyright.analysis.useTypingExtensions` | false | Rely on `typing_extensions` for older targets (e.g. `@override`) |
| `basedpyright.analysis.fileEnumerationTimeout` | 10 | Seconds before a "slow enumeration" warning |
| `basedpyright.analysis.autoFormatStrings` | true | Insert `f` when typing `{` inside a string (Pylance `autoFormatStrings`) |
| `basedpyright.analysis.configFilePath` | — | Directory/file holding the config; useful for monorepos where the config is in a subdirectory |
| `basedpyright.analysis.baselineMode` | `auto` | `auto` removes fixed errors from the baseline on save; `discard` prevents automatic updates |

Discouraged (use a committed config file instead, so editor and CLI match and the
setup is shareable): `basedpyright.analysis.diagnosticSeverityOverrides` (map of rule
to `"error"`/`"warning"`/`"information"`/`"none"`/bool), `exclude`, `extraPaths`,
`ignore`, `include`, `stubPath`, `typeCheckingMode` (old name `basedpyright.typeCheckingMode`
still honored), `typeshedPaths` (only the first path is used),
`useLibraryCodeForTypes`, `basedpyright.analysis.baselineFile`. If a
`pyrightconfig.json` or basedpyright/pyright pyproject table exists, these are
ignored.

## Language server commands

Available from, e.g., the VS Code command palette:

- **Organize Imports** — sort module-level imports into built-in / third-party / local
  groups, alphabetical, rewrapped to fit the line length. No CLI equivalent exists to
  validate it; the docs recommend ruff for import sorting.
- **Restart Server** — discard cached type information and re-analyze; useful after
  installing new stubs or libraries.
- **Write new errors to baseline** — add new errors to the baseline file (the editor
  removes fixed ones automatically on save).

## Pylance feature parity

Features re-implemented from Pylance (usable in any LSP editor):

- Jupyter notebook support in the language server, **and** notebook type checking from
  the CLI (pyright cannot)
- Import suggestion **code actions** (quick fixes), not just completions
- `# pyright: ignore` code actions
- Semantic highlighting, including PEP 695 `type` keywords and `Final` variables
  colored read-only
- Inlay hints, including double-click to insert (also on `Callable` types)
- Docstrings for compiled builtin modules, scraped via docify for all supported
  Python versions and platforms and bundled with the package (regenerate for your own
  compiled third-party modules with `python -m docify path/to/stubs --in-place`)
- Renaming packages/modules updates all usages
- Fixed multi-line parameter descriptions in docstring hovers
- `autoFormatStrings` (f-string auto-insert on `{`)
- Hover and go-to-definition on operators
- Go to / Find All Implementations

Missing Pylance features are tracked under the "pylance parity" label in the issue
tracker.

## CI

**GitHub Actions** — no wrapper needed; basedpyright detects the Actions environment
and emits workflow commands so errors appear on the affected PR lines:

```yaml
jobs:
  check:
    steps:
      - run: ...  # checkout, install dependencies
      - run: basedpyright
```

**GitLab** — see the `--gitlabcodequality` recipe in
[02-configuration](02-configuration.md#gitlab-code-quality-report).

In CI the baseline file is locked: a stale baseline fails the run, which keeps
contributors from silently re-introducing fixed errors.

## prek hook

[prek](https://github.com/j178/prek) (Rust pre-commit) mirror for those who want a
commit hook:

```yaml
repos:
  - repo: https://github.com/DetachHead/basedpyright-prek-mirror
    rev: <basedpyright version>
    hooks:
      - id: basedpyright
```

The docs' preferred alternatives: an IDE integration (errors while writing, not at
commit time), or CI (already first-class via the PyPI package).

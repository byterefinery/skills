# Language Server

## Starting the server

```bash
ty server
```

Runs as a stdio-based LSP server. Connect via any LSP-compatible editor.

## Supported LSP features

| Feature | Status |
|---------|--------|
| Diagnostics (`textDocument/diagnostic`) | ✅ Pull and push models |
| Go to Definition (`textDocument/definition`) | ✅ |
| Go to Declaration (`textDocument/declaration`) | ✅ |
| Go to Type Definition (`textDocument/typeDefinition`) | ✅ |
| Find References (`textDocument/references`) | ✅ |
| Completions (`textDocument/completion`) | ✅ With auto-import |
| Hover (`textDocument/hover`) | ✅ Types, signatures, docstrings |
| Inlay Hints (`textDocument/inlayHint`) | ✅ Double-click to insert |
| Signature Help (`textDocument/signatureHelp`) | ✅ |
| Rename (`textDocument/rename`) | ✅ Workspace-wide |
| Code Actions (`textDocument/codeAction`) | ✅ Quick fixes, add import |
| Document Highlight (`textDocument/documentHighlight`) | ✅ |
| Document Symbols (`textDocument/documentSymbol`) | ✅ |
| Workspace Symbols (`workspace/symbol`) | ✅ |
| Folding Ranges (`textDocument/foldingRange`) | ✅ Docstrings tagged as comments |
| Selection Range (`textDocument/selectionRange`) | ✅ |
| Semantic Tokens (`textDocument/semanticTokens`) | ✅ |
| Call Hierarchy (`callHierarchy/*`) | ✅ |
| Type Hierarchy (`typeHierarchy/*`) | ✅ |
| Workspace Diagnostics (`workspace/diagnostic`) | ✅ |
| Notebook Documents (`notebookDocument/*`) | ✅ `.ipynb` support |
| Code Lens (`textDocument/codeLens`) | ❌ |
| Document Color (`textDocument/documentColor`) | ❌ |
| Document Link (`textDocument/documentLink`) | ❌ |
| Implementation (`textDocument/implementation`) | ❌ ([#3514](https://github.com/astral-sh/ty/issues/3514)) |
| Will Rename Files (`workspace/willRenameFiles`) | ❌ ([#1560](https://github.com/astral-sh/ty/issues/1560)) |

Formatting is handled by Ruff, not ty.

## Fine-grained incrementality

ty updates only affected parts of the codebase on edits, down to individual definitions.
This provides instant feedback (milliseconds) even on large projects. Dependencies on
3rd-party code are also skipped when not relevant.

## Diagnostics

- Updated as you type
- `diagnosticMode` setting controls open-files-only vs entire workspace
- Pull model (on-demand) preferred for modern editors; push model also supported

## Inlay hints

Display inline type hints for unannotated variables and parameters. Double-click to
insert annotations. Click on parts of hints for go-to-definition.

## Code completions

- Variables, functions, classes, modules in scope
- Auto-import suggestions for unimported symbols
- Accepting completion adds import automatically

## Code actions

- Add missing imports
- Quick fixes for diagnostics
- Rename symbols workspace-wide

## Notebook support

ty supports `.ipynb` files with full language server features. Each cell is analyzed
in context, with diagnostics and completions working across cells.

## Editor setup

### VS Code

Install [ty extension](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty)
from the marketplace. It automatically disables the Python extension's language server.

To use ty only for type checking (keep Pylance for other features):

```jsonc
{
  "python.languageServer": "Pylance",
  "ty.disableLanguageServices": true
}
```

### Neovim (>= 0.11)

```lua
vim.lsp.config('ty', {
  settings = { ty = { /* ty settings */ } }
})
vim.lsp.enable('ty')
```

### Neovim (< 0.11)

```lua
require('lspconfig').ty.setup({
  settings = { ty = { /* ty settings */ } }
})
```

### Zed

Built-in, no extension needed. Enable in `settings.json`:

```json
{
  "languages": {
    "Python": {
      "language_servers": ["ty", "ruff"]
    }
  }
}
```

Override binary path:

```json
{
  "lsp": {
    "ty": {
      "binary": {
        "path": "/home/user/.local/bin/ty",
        "arguments": ["server"]
      }
    }
  }
}
```

### PyCharm (>= 2025.3)

Go to **Python | Tools | ty** in Settings. Enable and select execution mode:
- **Interpreter**: searches in your Python interpreter
- **Path**: searches `$PATH` or specify manually

### Emacs

```elisp
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '((python-base-mode :language-id "python") . ("ty" "server"))))
(add-hook 'python-base-mode-hook 'eglot-ensure)
```

### Generic LSP

Any LSP-compatible editor can connect to `ty server`. Configure your editor to run
`ty server` as the language server for Python files.

## Editor settings

ty accepts settings via the LSP `initialize` and `workspace/didChangeConfiguration`
messages. Settings mirror the config file structure under the `ty` key.

## LSP extensions

### Full diagnostic output

Client capability: `{ "fullDiagnosticOutput": boolean }`

When enabled, diagnostics include a `rendered` field with ANSI-styled multiline
output and `diagnostic_id` with the original rule name.

# Language Server

## Starting the server

```bash
ty server
```

Communicates over stdin/stdout using the Language Server Protocol.

## Supported LSP features

### Diagnostics
- Pull and push diagnostic models
- `diagnosticMode` setting: open files only or full workspace
- Diagnostics updated as you type with fine-grained incrementality

### Code navigation
- **Go to Definition** — jump to symbol definition
- **Go to Declaration** — navigate to declaration site (may differ for stubs)
- **Go to Type Definition** — navigate to the type of a symbol
- **Find all references** — workspace-wide symbol usage
- **Document and workspace symbols** — file outline and workspace search
- **Call hierarchy** — incoming and outgoing calls
- **Type hierarchy** — supertypes and subtypes

### Completions
- Variables, functions, classes, modules in scope
- Auto-import suggestions for unimported symbols
- Accepting completions auto-adds import statements

### Code actions
- **Add import** — auto-add missing imports
- **Quick fixes** — resolve diagnostics
- **Rename symbol** — safe rename across codebase
- **Selection range** — expand/shrink selection by syntax

### Contextual information
- **Hover** — type, documentation, signatures, variance info
- **Inlay hints** — inline type hints, parameter names (double-click to insert)
- **Signature help** — function parameters with types
- **Document highlight** — highlight all occurrences of a symbol
- **Semantic highlighting** — semantics-based syntax highlighting

### Other
- **Code folding** — Python-specific folding, docstrings tagged as comments
- **Notebook support** — `.ipynb` files with cross-cell analysis

## Not supported

- `textDocument/codeLens`
- `textDocument/documentColor`
- `textDocument/documentLink`
- `textDocument/implementation` (added in 0.0.64)
- `workspace/willRenameFiles`

## Fine-grained incrementality

ty updates only affected parts of the codebase on file changes, down to individual definitions.
This provides instant feedback (milliseconds) even on large projects. Third-party dependencies
are skipped when not relevant to the current codebase.

## Editor settings

Settings are passed via LSP initialization or editor configuration.

### VS Code

```jsonc
{
  "ty.disableLanguageServices": false,  // Use ty for full LSP
}
```

To use ty only for type checking with another LSP for other features:

```jsonc
{
  "python.languageServer": "Pylance",
  "ty.disableLanguageServices": true,
}
```

### Neovim (>= 0.11)

```lua
vim.lsp.config('ty', {
  settings = {
    ty = {
      -- ty language server settings
    }
  }
})
vim.lsp.enable('ty')
```

### Neovim (< 0.11)

```lua
require('lspconfig').ty.setup({
  settings = {
    ty = {
      -- ty language server settings
    }
  }
})
```

### Zed

```json
{
  "languages": {
    "Python": {
      "language_servers": ["ty", "ruff"]
    }
  },
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

1. Settings → **Python | Tools | ty** → Enable
2. Choose **Interpreter** mode (searches in your interpreter) or **Path** mode
3. Select enabled options

### Emacs (Eglot)

```elisp
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '((python-base-mode :language-id "python") . ("ty" "server"))))
(add-hook 'python-base-mode-hook 'eglot-ensure)
```

## LSP extensions

### Full diagnostic output

Client capability: `{ "fullDiagnosticOutput": boolean }`

When enabled, diagnostics include `data.rendered` (ANSI-styled multiline rendering) and
`data.diagnostic_id` (original rule identifier).

```ts
interface Diagnostic {
    data?: {
        rendered?: string;       // ANSI-styled multiline output
        diagnostic_id?: string;  // Original ty rule identifier
    };
}
```

## Docstring rendering

ty renders structured docstrings as Markdown in hover tooltips:
- **Google style** — supported since 0.0.61
- **NumPy style** — supported since 0.0.64
- **reST/Sphinx style** — standard support

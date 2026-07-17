# Editor Integration

## VS Code

Install the official [ty extension](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty) from the Marketplace.

The extension automatically sets `python.languageServer` to `"None"` to avoid running two Python language servers simultaneously.

To use ty only for type checking with another LSP (e.g., Pylance):

```jsonc
{
  "python.languageServer": "Pylance",
  "ty.disableLanguageServices": true
}
```

## Neovim

### Neovim >= 0.11 (with nvim-lspconfig)

```lua
vim.lsp.config('ty', {
  settings = {
    ty = {
      -- language server settings
    }
  }
})

vim.lsp.enable('ty')
```

### Neovim < 0.11

```lua
require('lspconfig').ty.setup({
  settings = {
    ty = {
      -- language server settings
    }
  }
})
```

## Zed

ty is included with Zed by default. To make it the primary Python LSP:

```json
{
  "languages": {
    "Python": {
      "language_servers": ["ty", "ruff"]
    }
  }
}
```

Override the binary path:

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

## PyCharm

Starting with version 2025.3, go to **Python | Tools | ty** in Settings and enable it. Choose **Interpreter** mode (searches installed packages) or **Path** mode (uses `$PATH`).

## Emacs

Using built-in Eglot (Emacs 29+):

```elisp
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '((python-base-mode :language-id "python") . ("ty" "server"))))

(add-hook 'python-base-mode-hook 'eglot-ensure)
```

For Flycheck integration, use the [flycheck-eglot](https://github.com/flycheck/flycheck-eglot) package.

## Generic LSP Setup

For any editor supporting the Language Server Protocol, start the server with:

```bash
ty server
```

Connect your editor's LSP client to this process via stdin/stdout.

## Supported LSP Features

| Feature | Status |
|---------|--------|
| Diagnostics (pull and push) | ✅ |
| Go to Definition / Declaration / Type Definition | ✅ |
| Find All References | ✅ |
| Completions with auto-import | ✅ |
| Hover (types, docstrings, signatures) | ✅ |
| Inlay Hints (clickable) | ✅ |
| Signature Help | ✅ |
| Rename Symbol | ✅ |
| Document Highlight | ✅ |
| Semantic Tokens | ✅ |
| Code Folding | ✅ |
| Selection Range | ✅ |
| Call Hierarchy | ✅ |
| Type Hierarchy | ✅ |
| Notebook (`.ipynb`) Support | ✅ |
| Code Actions / Quick Fixes | ✅ |

Not supported: Code Lens, Document Color, Document Link, Implementation. Formatting is handled by Ruff.

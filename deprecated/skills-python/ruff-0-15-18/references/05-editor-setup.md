# Editor Setup

## VS Code

Install the [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

Settings in `.vscode/settings.json`:

```json
{
    "python.analysis.typeCheckingMode": "basic",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit"
        }
    }
}
```

The extension uses `ruff` from your PATH or virtual environment. Set the binary path:

```json
{
    "ruff.path": ["/home/user/.venv/bin/ruff"]
}
```

## Neovim

### With nvim-lspconfig

```lua
-- lsp.lua
require("lspconfig").pyright.setup({})

-- Or use ruff as the language server directly
require("lspconfig").ruff.setup({})
```

### With none-ls (deprecated, use nvim-lsp)

For older setups using `none-ls.nvim`:

```lua
local null_ls = require("null-ls")
null_ls.setup({
  sources = {
    null_ls.builtins.diagnostics.ruff.with({
      extra_args = { "--select", "E,F,B" },
    }),
    null_ls.builtins.formatting.ruff.with({
      extra_args = { "--preview" },
    }),
  },
})
```

### With conform.nvim

```lua
require("conform").setup({
  formatters_by_ft = {
    python = { "ruff_format" },
  },
})
```

## PyCharm / IntelliJ

Install the [Ruff plugin](https://plugins.jetbrains.com/plugin/20741-ruff). Configure in Settings → Tools → Ruff:

- Path to ruff executable
- Additional arguments (e.g., `--select E,F,B`)
- Enable "Run on save" for auto-fix

## Vim

Using ALE (Asynchronous Lint Engine):

```vim
let g:ale_linters = {
\   'python': ['ruff'],
\}
let g:ale_python_ruff_executable = 'ruff'
let g:ale_python_ruff_args = ['check', '--output-format=text']
```

Using CoC:

```json
{
  "coc.source.ruff.command": "ruff",
  "coc.source.ruff.arguments": ["check", "--output-format=json"]
}
```

## Emacs

Using `eglot` with `ruff server`:

```elisp
(add-to-list 'eglot-server-programs
             '((python-mode py-mode) ("ruff" "server")))
```

Or using `flycheck`:

```elisp
(with-eval-after-load 'flycheck
  (flycheck-add-next-checker 'python-pyflakes 'python-ruff))
```

## Helix

In `config.toml`:

```toml
[language-server.ruff]
command = "ruff"
args = ["server"]
```

In `languages.toml`:

```toml
[[language]]
name = "python"
language-servers = [{ name = "ruff" }]
formatter = { command = "ruff", args = ["format", "-"] }
```

## General LSP Notes

- `ruff server` provides both linting diagnostics and formatting via LSP protocol.
- Preview mode can be enabled with `--preview` flag on the server.
- The server reads the same config files (`pyproject.toml`, `ruff.toml`, `.ruff.toml`) as the CLI.
- For projects using virtual environments, ensure the editor activates the correct environment so it finds the right `ruff` binary and config.

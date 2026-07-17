# Installation and Setup Reference

## Installation Methods

### PyPI (Recommended)

Unlike pyright, basedpyright ships as a PyPI package, so no Node.js is needed.

```bash
# Add as dev dependency (recommended — pins version per project)
uv add --dev basedpyright

# Global install
uv tool install basedpyright

# pip
pip install basedpyright
```

After installation, two commands are available:
- `basedpyright` — CLI type checker
- `basedpyright-langserver` — Language server (LSP) for IDE integration

### Conda
```bash
conda install conda-forge::basedpyright
```

### Homebrew
```bash
brew install basedpyright
```

### NPM (Fallback)

The npm package is available but not recommended. Use it only if your OS is unsupported by the PyPI wheel or you're on Python <3.8.

```bash
npm install basedpyright
```

## IDE Setup

### VS Code / VSCodium

Install the extension:
- VS Code: [Marketplace](https://marketplace.visualstudio.com/items?itemName=detachhead.basedpyright)
- VSCodium: [Open VSX](https://open-vsx.org/extension/detachhead/basedpyright)

Pin as a recommended extension:
```json title=".vscode/extensions.json"
{
  "recommendations": ["detachhead.basedpyright"]
}
```

**Known issue**: If `basedpyright` is installed in a venv but the Microsoft Python extension (`ms-python`) is not installed, the VS Code extension will crash. Workarounds:
1. Install `ms-python`
2. Set `"basedpyright.importStrategy": "useBundled"` in `.vscode/settings.json`

### Neovim

Requires `nvim-lspconfig`. For Neovim 0.11+:

```lua
vim.lsp.enable("basedpyright")
```

For Neovim 0.10 (legacy):

```lua
local lspconfig = require("lspconfig")
lspconfig.basedpyright.setup{}
```

Configuration example:
```lua
return {
  settings = {
    basedpyright = {
      analysis = {
        diagnosticMode = "openFilesOnly",
        inlayHints = {
          callArgumentNames = true,
          variableTypes = true,
          functionReturnTypes = true,
          genericTypes = true
        }
      }
    }
  }
}
```

### Emacs

**lsp-bridge**: basedpyright is the default Python language server — no extra config needed.

**eglot**:
```emacs-lisp
(add-to-list 'eglot-server-programs
            '((python-mode python-ts-mode)
            "basedpyright-langserver" "--stdio"))
```

**lsp-mode** (with `lsp-pyright`, commit after `0c0d72a`):
```emacs-lisp
(setq lsp-pyright-langserver-command "basedpyright")
```

### Helix

```toml title="languages.toml"
[[language]]
name = "python"
language-servers = [ "basedpyright" ]
```

Verify with: `hx --health python`

### Zed

basedpyright is the default Python language server in Zed. Pin to project-local version:

```json title=".zed/settings.json"
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

### PyCharm

1. Go to **Python > Tools > Pyright** in Settings
2. Enable the checkbox
3. Select **Interpreter** mode (recommended) — PyCharm searches for basedpyright in your interpreter
4. Click _Install basedpyright_ if needed

Commit `.idea/pyLspTools.xml` so teammates get the same config.

### Sublime Text

Install via Package Control: `LSP` + `LSP-basedpyright`.

## Language Server Settings

Settings can be configured per-IDE or via a config file (preferred). Config files take precedence over language server settings when present.

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `basedpyright.analysis.diagnosticMode` | `"openFilesOnly"` | Analyze only open files or entire workspace |
| `basedpyright.analysis.diagnosticSeverityOverrides` | — | Override severity per rule |
| `basedpyright.analysis.inlayHints.variableTypes` | `true` | Show inlay hints on variable assignments |
| `basedpyright.analysis.inlayHints.callArgumentNames` | `true` | Show inlay hints on function arguments |
| `basedpyright.analysis.inlayHints.functionReturnTypes` | `true` | Show inlay hints on return types |
| `basedpyright.analysis.inlayHints.genericTypes` | `true` | Show inlay hints on inferred generics |
| `basedpyright.analysis.autoFormatStrings` | `true` | Auto-insert `f` when typing `{` in strings |
| `basedpyright.analysis.useTypingExtensions` | `false` | Use `typing_extensions` for older Python targets |
| `basedpyright.analysis.configFilePath` | — | Path to config file (useful for monorepos) |
| `basedpyright.disableLanguageServices` | `false` | Disable hover, completion, etc. (type-check only) |
| `basedpyright.disableTaggedHints` | `false` | Disable grayed-out/strikethrough hints |

### Monorepo Setup

For projects where Python code lives in a subdirectory:

```json title=".vscode/settings.json"
{
  "basedpyright.analysis.configFilePath": "${workspaceFolder}/backend"
}
```

## Pre-commit Hook (Optional)

```yaml title=".pre-commit-config.yaml"
repos:
  - repo: https://github.com/DetachHead/basedpyright-prek-mirror
    rev: v1.39.8
    hooks:
      - id: basedpyright
```

Note: [prek](https://github.com/j178/prek) is recommended over pre-commit (faster, Rust-based drop-in replacement).

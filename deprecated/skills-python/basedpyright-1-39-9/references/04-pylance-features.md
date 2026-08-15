# Pylance Features Reference

basedpyright re-implements features exclusive to Microsoft's closed-source Pylance
extension, making them available in any LSP-compatible editor.

## Jupyter Notebook Support

- **Language server**: Full diagnostics, hover, go-to-definition in `.ipynb` files
- **CLI**: Type-check notebooks from command line (unique to basedpyright, not in pyright)

```bash
basedpyright                              # Checks .ipynb files in project
basedpyright path/to/notebook.ipynb       # Check specific notebook
```

Output includes cell references:

```
notebook.ipynb - cell 1
  notebook.ipynb:1:1:12 - error: Type "Literal['']" is not assignable to declared type "int" (reportAssignmentType)
```

## Code Actions

### Import suggestions

Quick-fix code actions that suggest imports for unresolved symbols. Available as
editor quick fixes, not just autocomplete.

### Ignore comment insertion

Quick-fix to add `# pyright: ignore[rule]` with the specific rule code. Only offers
`pyright: ignore`, never `type: ignore`.

## Semantic Highlighting

- Standard semantic tokens for classes, functions, variables, parameters
- `Final` variables highlighted as read-only
- Python 3.12 `type` keyword support
- Improved token classification over pyright

## Inlay Hints

- Parameter name hints
- Variable type hints
- Generic type hints
- Function return type hints
- **Double-click to insert**: Click an inlay hint to insert it as an explicit annotation
- Works on `Callable` types (unlike Pylance)

## Docstrings for Compiled Builtins

basedpyright uses [docify](https://github.com/atoerien/docify) to pre-scrape docstrings
from compiled builtin modules for all supported Python versions and platforms (macOS,
Windows, Linux). These are bundled in the typeshed stubs.

To add docstrings to third-party compiled module stubs:

```bash
python -m docify path/to/stubs --in-place
# Or for current platform/version only:
python -m docify path/to/typeshed/stdlib --if-needed --in-place
```

## Rename Packages and Modules

Rename a package or module and update all import references across the project,
just like Pylance.

## Go to Implementations

Find all implementations of a method or protocol across the codebase.

## Hover on Operators

Hover over operators (`+`, `-`, `*`, etc.) to see the resolved method (e.g.,
`__add__`, `__sub__`) and its signature. Go to definition also works.

## Multi-line Docstring Parameters

Fixed parsing of multi-line parameter descriptions in docstrings. All lines of a
parameter description are shown on hover, not just the first line.

## Auto f-string Conversion

When typing `{` inside a string literal, automatically convert to f-string.
Controlled by `autoFormatStrings` language server setting.

## Pylance Features Not Yet in basedpyright

Check the [open issues](https://github.com/DetachHead/basedpyright/issues?q=is:issue+is:open+pylance+label:%22pylance+parity%22)
for the current parity status.

## IDE-Specific Setup

### VS Code / VSCodium

Install `detachhead.basedpyright` extension. Auto-detects PyPI package in your
Python environment.

```json title=".vscode/extensions.json"
{
    "recommendations": ["detachhead.basedpyright"]
}
```

If using without `ms-python` extension, set:

```json
{
    "basedpyright.importStrategy": "useBundled"
}
```

### Neovim

```lua
-- Neovim 0.11+
vim.lsp.enable("basedpyright")

-- Neovim 0.10 (legacy)
local lspconfig = require("lspconfig")
lspconfig.basedpyright.setup{}
```

### Emacs

```emacs-lisp
;; eglot
(add-to-list 'eglot-server-programs
            '((python-mode python-ts-mode)
            "basedpyright-langserver" "--stdio"))

;; lsp-mode (with lsp-pyright)
(setq lsp-pyright-langserver-command "basedpyright")

;; lsp-bridge: basedpyright is the default, no config needed
```

### PyCharm

Settings > Python > Tools > Pyright > Enable. Use **Interpreter** mode to search
for basedpyright in your virtual environment.

Commit `.idea/pyLspTools.xml` for team consistency.

### Helix

```toml
[[language]]
name = "python"
language-servers = [ "basedpyright" ]
```

### Zed

basedpyright is the default Python LSP. Pin to project version:

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

### Sublime Text

Install `LSP` and `LSP-basedpyright` via Package Control.

### Vim

Install `coc-basedpyright` for coc.nvim.

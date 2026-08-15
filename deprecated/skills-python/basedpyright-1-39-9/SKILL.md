---
name: basedpyright-1-39-9
description: >
  basedpyright 1.39.9 — strict static type checker for Python, fork of pyright with
  improved defaults, new diagnostic rules, baseline support, and Pylance features
  available in any editor. Use this skill whenever the user mentions basedpyright,
  pyright, Python type checking, static analysis, type stubs, pyrightconfig.json,
  typeCheckingMode, LSP type checking, or migrating from mypy/pyright. Covers
  installation (PyPI, no Node required), CLI usage, configuration, baseline workflow,
  new diagnostic rules, language server setup, and migration from pyright or mypy.
license: MIT
compatibility: Requires Python 3.8+
metadata:
  tags:
    - python
    - type-checking
    - static-analysis
    - lsp
---

# basedpyright 1.39.9

## Overview

basedpyright is a fork of Microsoft's pyright with stricter defaults, new diagnostic
rules, baseline support for gradual adoption, and Pylance-exclusive features
re-implemented for any LSP-compatible editor. Unlike pyright, it installs from PyPI
without needing Node.js, and the VS Code extension uses the same version as the CLI
so editor and CI always agree.

Key differentiators from pyright:

- **`typeCheckingMode` defaults to `"recommended"`** — all diagnostic rules enabled
  by default (warnings for less severe rules, errors for likely runtime issues)
- **`failOnWarnings` enabled by default** — warnings cause non-zero exit in CLI
- **`pythonPlatform` defaults to `"All"`** — assumes cross-platform code
- **Auto-detects `.venv`** — no manual `venv`/`venvPath` config needed
- **`# type: ignore` disabled by default** — enforces safer `# pyright: ignore` with rule codes
- **13+ new diagnostic rules** — `reportAny`, `reportExplicitAny`,
  `reportIgnoreCommentWithoutRule`, `reportPrivateLocalImportUsage`,
  `reportImplicitRelativeImport`, `reportInvalidCast`, `reportUnsafeMultipleInheritance`,
  `reportUnusedParameter`, `reportImplicitAbstractClass`, `reportEmptyAbstractUsage`,
  `reportIncompatibleUnannotatedOverride`, `reportUnannotatedClassAttribute`,
  `reportInvalidAbstractMethod`, `reportSelfClsDefault`
- **Baseline support** — adopt strict rules in existing codebases without fixing old code
- **Pylance features in any editor** — Jupyter notebook CLI support, import suggestion
  code actions, semantic highlighting, inlay hints, docstrings for compiled builtins,
  rename packages/modules, go to implementations, hover on operators

## Usage

### Installation

```bash
# PyPI (recommended, no Node.js needed)
pip install basedpyright
uv add --dev basedpyright

# Homebrew
brew install basedpyright

# Conda
conda install conda-forge::basedpyright

# npm (fallback only)
npm install basedpyright
```

### CLI

```bash
basedpyright                           # Check current directory
basedpyright path/to/code/             # Check specific directory
basedpyright path/to/file.py           # Check a single file
basedpyright -p pyrightconfig.json     # Use specific config file
basedpyright --outputjson              # JSON output (CI/tooling)
basedpyright --writebaseline           # Write new errors to baseline file
basedpyright --threads                 # Parallel type checking
basedpyright --verbose                 # Verbose diagnostics
basedpyright --stats                   # Performance stats
basedpyright --version                 # Print version
basedpyright --pythonversion 3.11      # Target Python version
basedpyright --pythonplatform Linux    # Target platform
basedpyright --dependencies            # Emit import dependency info
basedpyright --createstub mymodule     # Create type stub for import
basedpyright --verifytypes mymodule    # Verify py.typed package completeness
basedpyright -w                         # Watch mode (re-check on changes)
basedpyright --gitlabcodequality out.json  # GitLab code quality report
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | No errors reported |
| 1 | One or more errors reported |
| 2 | Fatal error (no errors/warnings reported) |
| 3 | Config file could not be read or parsed |
| 4 | Illegal command-line parameters |

### Baseline workflow

Baseline lets you adopt strict rules in existing codebases without fixing old code:

```bash
# 1. Generate baseline from existing errors
basedpyright --writebaseline

# 2. Commit .basedpyright/baseline.json

# 3. Run normally — only new/modified code errors are reported
basedpyright

# Baseline auto-updates as errors are fixed over time
# Use --writebaseline to intentionally baseline new rule violations
```

In CI, baseline defaults to `lock` mode (never writes, fails if baseline needs updating).
Locally, it defaults to `auto` mode (only updates when errors are removed).

### Configuration

#### pyproject.toml (recommended)

```toml
[tool.basedpyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__"]
ignore = ["src/legacy"]

pythonVersion = "3.11"
pythonPlatform = "All"

typeCheckingMode = "recommended"
failOnWarnings = true

# basedpyright-specific settings
baselineFile = ".basedpyright/baseline.json"
allowedUntypedLibraries = ["untyped-lib"]
strictGenericNarrowing = true

reportAny = "warning"
reportExplicitAny = "warning"
reportIgnoreCommentWithoutRule = "error"
reportPrivateLocalImportUsage = "error"
reportImplicitRelativeImport = "error"
reportInvalidCast = "error"
reportUnsafeMultipleInheritance = "error"
reportUnusedParameter = "warning"
reportIncompatibleUnannotatedOverride = "error"

executionEnvironments = [
    { root = "src", pythonVersion = "3.11" },
    { root = "tests", pythonVersion = "3.11", reportPrivateUsage = false },
]
```

#### pyrightconfig.json

```json
{
    "include": ["src"],
    "exclude": ["**/node_modules", "**/__pycache__"],
    "pythonVersion": "3.11",
    "pythonPlatform": "All",
    "typeCheckingMode": "recommended",
    "failOnWarnings": true,
    "reportAny": "warning",
    "reportExplicitAny": "warning"
}
```

`pyrightconfig.json` takes precedence over `pyproject.toml` if both exist.
`[tool.pyright]` section is also supported for backward compatibility.

### Diagnostic severity levels

- `"error"` — causes CLI exit code 1
- `"warning"` — causes CLI exit code 1 when `failOnWarnings` is true (default)
- `"information"` — never causes CLI to fail
- `"hint"` — only visible in language server (greyed out/strikethrough)
- `"none"` — diagnostic disabled entirely

### File-level controls

```python
# pyright: strict                    # Enable strict mode for this file
# pyright: basic                     # Use basic defaults for this file
# pyright: strict, reportPrivateUsage=false  # Strict with overrides
```

### Line-level suppression

```python
result = some_call()  # pyright: ignore[reportAny]
```

`# pyright: ignore` with rule codes is preferred over `# type: ignore`.
The latter is disabled by default in basedpyright.

### Language server

```bash
basedpyright-langserver --stdio
```

Configure in your editor's LSP settings. The server supports:

- Diagnostics with severity colors
- Import suggestion code actions
- `# pyright: ignore` code actions
- Semantic highlighting (including `Final` as read-only, `type` keyword)
- Inlay hints (double-click to insert)
- Go to implementations
- Rename packages and modules
- Hover on operators
- Jupyter notebook support
- Auto f-string conversion (`autoFormatStrings` setting)
- Docstrings for compiled builtin modules

### IDE setup

- **VS Code** — install `detachhead.basedpyright` extension
- **Neovim** — `vim.lsp.enable("basedpyright")` (0.11+) or `lspconfig.basedpyright.setup{}`
- **Zed** — default Python LSP, pin via `.zed/settings.json`
- **Helix** — add `basedpyright` to language servers in languages.toml
- **Emacs** — lsp-bridge (default), eglot, or lsp-mode
- **PyCharm** — native support in Settings > Python > Tools > Pyright
- **Sublime Text** — LSP + LSP-basedpyright packages
- **Vim** — coc-basedpyright

## Gotchas

- **`typeCheckingMode` is `"recommended"` by default** — all rules are enabled. Use
  `typeCheckingMode = "off"` to disable all diagnostic rules (pyright still reports
  some warnings in `"off"` mode, basedpyright does not). Use baseline to adopt
  gradually in existing codebases.

- **`failOnWarnings` is true by default** — warnings cause non-zero exit code. Set
  `failOnWarnings = false` if you only want errors to fail CI. The `--warnings` CLI
  flag is redundant unless you disabled `failOnWarnings`.

- **`# type: ignore` is disabled by default** — basedpyright requires `# pyright: ignore`
  with specific rule codes. Enable `enableTypeIgnoreComments = true` if you need legacy
  compatibility, but prefer `pyright: ignore` for safety.

- **`pythonPlatform` defaults to `"All"`** — unlike pyright which assumes the current OS,
  basedpyright assumes your code runs anywhere. Set `pythonPlatform = "Linux"` if your
  code is truly platform-specific.

- **Auto-detects `.venv`** — if no `pythonPath`/`venv`/`venvPath` is set, basedpyright
  checks for `.venv/` in the project root. This covers the common uv/pipx workflow.

- **`allowedUntypedLibraries` suppresses unknown-type rules** — use this instead of
  globally disabling `reportUnknownVariableType` when working with untyped third-party
  packages. It only suppresses the rule for specific modules.

- **`strictGenericNarrowing` changes isinstance narrowing** — when enabled, narrowing
  generics with `isinstance` resolves type parameters to the bound/constraint instead
  of `Any`. Enable for stricter generic checking.

- **`enableBasedFeatures` is off by default** — enables extra `dataclass_transform`
  features. Keep disabled if developing libraries for users who may use pyright.

- **Baseline auto-updates locally, locks in CI** — running `basedpyright` locally
  removes fixed errors from the baseline automatically. In CI, it defaults to lock mode
  and fails if the baseline needs updating. Use `--writebaseline` to intentionally
  update, or `--baselinemode=auto` to force local behavior in CI.

- **`pyrightconfig.json` overrides `pyproject.toml`** — if both exist, only the JSON
  config is used. Pick one and stick with it.

- **`[tool.pyright]` vs `[tool.basedpyright]`** — both are supported, but `[tool.basedpyright]`
  is preferred. The `pyright` section exists for backward compatibility.

- **Diagnostic categories `"unreachable"`, `"unused"`, `"deprecated"` are deprecated** —
  use `"hint"` instead. They still work as aliases but may be removed.

- **`reportUnreachable` vs `enableReachabilityAnalysis`** — use `reportUnreachable`
  (a proper diagnostic rule) instead of `enableReachabilityAnalysis` (which only emits
  tagged hints in the language server and has no CLI effect).

- **`reportAny` vs `reportUnknown*` rules** — `reportAny` catches all `Any` types,
  including explicit ones. The `reportUnknown*` rules only catch `Any` from untyped
  code. Use `reportAny` for a complete ban, `reportExplicitAny` to ban direct `Any` usage.

- **`reportIncompatibleUnannotatedOverride` disabled in `"recommended"`** — disabled by
  default due to potential performance impact. Enable manually if needed, or use
  `reportUnannotatedClassAttribute` as a lighter alternative.

- **`--threads` is experimental** — parallelizes type checking across files. Use without
  a number to auto-detect thread count based on CPU cores (minimum 4 cores).

- **`--venvpath` is discouraged** — use `--pythonpath` to point directly at the
  interpreter. The `.venv` auto-detection covers most workflows.

- **`reportPrivateImportUsage` vs `reportPrivateLocalImportUsage`** — the former only
  checks third-party `py.typed` modules; the latter also checks your own code. Use both
  for complete private import enforcement.

- **`reportImplicitRelativeImport` catches `import sibling`** — `import foo` inside a
  package should be `from . import foo` or `from .foo import ...`. Absolute imports
  must specify the full path.

- **`reportInvalidCast` flags `TypedDict` casts** — casting `dict` to `TypedDict` triggers
  this rule since they don't overlap in the type system. Use proper construction or
  suppress with `# pyright: ignore[reportInvalidCast]`.

- **`reportUnsafeMultipleInheritance` allows lenient `reportMissingSuperCall`** — when
  unsafe multiple inheritance is banned, missing `super()` calls are only reported for
  classes with actual base classes (not standalone classes).

- **`reportImplicitAbstractClass` requires explicit `ABC`** — subclasses of abstract
  classes must also extend `ABC` to remain abstract. This prevents accidental concrete
  classes that fail at instantiation.

- **`reportSelfClsDefault` catches `def foo(self=1)`** — default values on `self`/`cls`
  are almost always mistakes and are flagged.

- **`deprecateTypingAliases` for Python 3.9+** — flags `typing.List` in favor of
  `list`, `typing.Dict` for `dict`, etc. Only active when `pythonVersion >= "3.9"`.

- **`disableBytesTypePromotions` follows PEP 688** — by default, `bytearray` and
  `memoryview` are not subtypes of `bytes`. Enable legacy behavior with this flag.

- **Jupyter notebooks supported in CLI** — unlike pyright, basedpyright can type-check
  `.ipynb` files from the command line, not just the language server.

- **`strict` paths in config** — use `"strict": ["src/core"]` to apply strict mode to
  specific directories without `# pyright: strict` comments in every file.

## References

- [01-diagnostic-rules](references/01-diagnostic-rules.md) — Complete diagnostic rules reference, defaults by mode
- [02-configuration](references/02-configuration.md) — Full config settings, execution environments, environment variables
- [03-baseline](references/03-baseline.md) — Baseline workflow, modes, CI integration
- [04-pylance-features](references/04-pylance-features.md) — Pylance parity features, IDE-specific setup
- [05-migration](references/05-migration.md) — Migrating from pyright, mypy, or basic mode

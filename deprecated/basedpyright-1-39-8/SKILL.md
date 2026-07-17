---
name: basedpyright-1-39-8
description: >
  Static type checking for Python via basedpyright — a fork of pyright with stricter defaults, new diagnostic rules, baseline support, pylance features in open-source, and improved CI integration. Use when the user mentions basedpyright, pyright, type checking, static analysis, type stubs, pyrightconfig, or wants to configure/resolve Python type errors.
---

# basedpyright 1.39.8

## Overview

basedpyright is a fork of [pyright](https://github.com/microsoft/pyright) that provides stricter defaults, new diagnostic rules, baseline support for incremental adoption, and re-implements Pylance-exclusive features in open-source. It ships as a PyPI package (`basedpyright`), making it easy to install alongside Python tooling without needing Node.js.

Key differences from upstream pyright:
- Default `typeCheckingMode` is `"recommended"` (all rules enabled as warnings/errors)
- New diagnostic rules: `reportAny`, `reportExplicitAny`, `reportInvalidCast`, `reportUnsafeMultipleInheritance`, and more
- Baseline support — adopt strict checks incrementally without fixing all existing errors first
- Built-in GitHub Actions annotations and GitLab code quality reports
- Pylance features (Jupyter, inlay hints, semantic highlighting, import suggestions) available to all LSP clients
- `enableTypeIgnoreComments` disabled by default; prefer `# pyright: ignore[rule]`
- Defaults `pythonPlatform` to `"All"` instead of the current OS
- Auto-detects `.venv` at project root as the Python environment
- Exits with code 3 on invalid configuration (pyright silently ignores bad settings)

## Usage

### Installation

```bash
# Via uv (recommended)
uv add --dev basedpyright

# Or globally
uv tool install basedpyright

# Via pip
pip install basedpyright
```

### Running the CLI

```bash
# Basic type check
basedpyright

# With verbose import resolution logs
basedpyright --verbose

# JSON output (for CI parsing)
basedpyright --outputjson

# Watch mode
basedpyright --watch

# Multi-threaded (experimental)
basedpyright --threads

# Baseline: write current errors to baseline
basedpyright --writebaseline
```

### Configuration

Place a `pyrightconfig.json` at the project root, or add a `[tool.basedpyright]` section to `pyproject.toml`. A config file always takes precedence over language server settings.

Minimal config:
```json
{
  "include": ["src"],
  "exclude": ["**/node_modules", "**/__pycache__"]
}
```

See reference files for full configuration options.

## Gotchas

- **`typeCheckingMode: "recommended"` is the default** — unlike pyright's `"basic"`, all diagnostic rules are enabled. Less severe rules are warnings, but `failOnWarnings` defaults to `true`, so the CLI exits non-zero on any warning. Set `failOnWarnings: false` if you only want hard errors to fail CI.

- **`enableTypeIgnoreComments` is disabled by default** — `# type: ignore` comments are ignored. Use `# pyright: ignore[ruleName]` instead, which requires specifying the rule and is safer. If migrating from pyright, you may need to replace `type: ignore` comments or enable the setting.

- **`pythonPlatform` defaults to `"All"`** — basedpyright assumes your code runs on any OS, not just the current one. This catches platform-specific type issues earlier but may surface false positives if your code is truly platform-specific. Override with `"Linux"`, `"Darwin"`, or `"Windows"` as needed.

- **Baseline file is auto-updated** — when errors are fixed, the baseline file (`.basedpyright/baseline.json`) is automatically updated to remove them. In CI, baseline defaults to lock mode (never writes). Use `--writebaseline` to intentionally update, or `--baselinemode=auto` to force local behavior in CI.

- **Config errors exit with code 3** — typos in config keys cause a hard failure, unlike pyright which silently ignores them. This is intentional but can be surprising when migrating configs from pyright (e.g., `mode` → `typeCheckingMode`).

- **`reportAny` catches all `Any` usage** — this new rule fires on expressions typed as `Any`, including explicit `Any` annotations that the older `reportUnknown*` rules miss. Use `allowedUntypedLibraries` to suppress for specific third-party modules.

- **`--venvpath` is discouraged** — basedpyright auto-detects `.venv` at project root. Use `--pythonpath` pointing to the interpreter instead, which is more robust.

- **`reportInvalidCast` flags `dict` → `TypedDict` casts** — casting a regular `dict` to a `TypedDict` triggers this rule because type checkers treat them as unrelated types. Narrow with runtime checks or use `# pyright: ignore[reportInvalidCast]`.

- **`strictGenericNarrowing` changes `isinstance` narrowing** — when enabled, `isinstance(x, list)` narrows to `list[object]` instead of `list[Unknown]`. This is more accurate but may surface new errors in code that relied on the looser behavior.

## References

- [01-installation-and-setup](references/01-installation-and-setup.md) — Installation methods, IDE configuration, language server setup
- [02-configuration](references/02-configuration.md) — Config files, environment options, execution environments, CLI flags
- [03-diagnostic-rules](references/03-diagnostic-rules.md) — All diagnostic rules organized by category with default severities
- [04-basedpyright-specific-features](references/04-basedpyright-specific-features.md) — New rules, baseline, better defaults, pylance features, CI integration
- [05-type-system](references/05-type-system.md) — Type concepts, inference, narrowing, generics, type guards
- [06-import-resolution-and-stubs](references/06-import-resolution-and-stubs.md) — Import resolution order, type stubs, editable installs

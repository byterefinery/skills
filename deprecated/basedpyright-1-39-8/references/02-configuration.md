# Configuration Reference

## Config File Formats

basedpyright supports two config file formats. A `pyrightconfig.json` takes precedence over `pyproject.toml` if both exist.

### pyrightconfig.json

```json title="pyrightconfig.json"
{
  "include": ["src"],
  "exclude": ["**/node_modules", "**/__pycache__", "src/experimental"],
  "ignore": ["src/legacy"],
  "strict": ["src/core"],

  "defineConstant": { "DEBUG": true },

  "stubPath": "src/stubs",
  "pythonVersion": "3.12",
  "pythonPlatform": "Linux",

  "typeCheckingMode": "recommended",
  "failOnWarnings": true,

  "executionEnvironments": [
    {
      "root": "src/tests",
      "reportPrivateUsage": false,
      "extraPaths": ["src"]
    }
  ]
}
```

### pyproject.toml

```toml title="pyproject.toml"
[tool.basedpyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__"]
strict = ["src/core"]

pythonVersion = "3.12"
pythonPlatform = "Linux"
typeCheckingMode = "recommended"
failOnWarnings = true

[tool.basedpyright.executionEnvironments]
root = "src/tests"
reportPrivateUsage = false
```

The `[tool.pyright]` section is also supported for backwards compatibility.

## Environment Options

| Setting | Type | Description |
|---------|------|-------------|
| `include` | array of paths | Directories/files to analyze. Defaults to config file's directory. Supports wildcards: `**`, `*`, `?` |
| `exclude` | array of paths | Paths to exclude. Auto-excludes: `**/node_modules`, `**/__pycache__`, `**/.*`, and all venv directories |
| `strict` | array of paths | Files/dirs using strict mode (equivalent to `# pyright: strict`). Most rules enabled as errors |
| `ignore` | array of paths | Suppress all diagnostics for these paths (still included in analysis) |
| `extends` | path | Base config file to inherit from. Supports multiple levels of inheritance |
| `defineConstant` | map | Assume identifiers have constant values, e.g., `{ "DEBUG": true }`. Affects reachability analysis |
| `pythonVersion` | string | Target Python version (`"3.8"`, `"3.12"`). Errors on unsupported features. Defaults to current interpreter |
| `pythonPlatform` | string | Target platform: `"Windows"`, `"Darwin"`, `"Linux"`, `"iOS"`, `"Android"`, `"All"`. Default: `"All"` |
| `typeshedPath` | path | Custom typeshed directory (for contributing to typeshed) |
| `stubPath` | path | Directory for custom `.pyi` stub files. Default: `"./typings"` |
| `extraPaths` | array of paths | Additional module search paths |
| `useLibraryCodeForTypes` | boolean | Analyze library source for types when no stubs exist. Default: `true` |
| `verboseOutput` | boolean | Verbose logging for debugging import resolution |

### basedpyright-exclusive environment settings

| Setting | Type | Description |
|---------|------|-------------|
| `failOnWarnings` | boolean | Exit non-zero on warnings. Default: `true` in `"recommended"` mode |
| `allowedUntypedLibraries` | array of strings | Suppress unknown-type rules for specific modules, e.g., `["requests", "lib.sub"]` |
| `baselineFile` | path | Path to baseline file. Default: `./.basedpyright/baseline.json` |

### Discouraged settings

| Setting | Why discouraged |
|---------|-----------------|
| `venvPath` | basedpyright auto-detects `.venv`. Use `--pythonpath` instead |
| `venv` | Same reason — prefer `--pythonpath` pointing to the interpreter |

## Type Evaluation Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `strictListInference` | `false` | Infer `list[int \| float]` instead of `list[Any]` for mixed lists |
| `strictDictionaryInference` | `false` | Strict inference for dict keys/values |
| `strictSetInference` | `false` | Strict inference for set elements |
| `analyzeUnannotatedFunctions` | `false` | Report errors in unannotated functions |
| `strictParameterNoneValue` | `false` | Require explicit `Optional` when default is `None` |
| `deprecateTypingAliases` | `false` | Flag deprecated typing aliases (Python 3.9+) |
| `enableExperimentalFeatures` | `false` | Enable proposed/exploratory typing features |
| `disableBytesTypePromotions` | `false` | Disable legacy `bytearray`/`memoryview` as `bytes` subtypes |
| `strictGenericNarrowing` | `false` | Narrow generics to bound/constraint instead of `Unknown` on `isinstance` |
| `enableBasedFeatures` | `false` | Enable basedpyright-specific features (e.g., extra `dataclass_transform` options) |

### Discouraged type evaluation settings

| Setting | Why discouraged |
|---------|-----------------|
| `enableTypeIgnoreComments` | `# type: ignore` is unsafe — disabled by default. Use `# pyright: ignore[rule]` |
| `enableReachabilityAnalysis` | Use `reportUnreachable` rule instead, which is more accurate |

## Execution Environments

Define different settings per subdirectory. Search order matches first root containing the file.

```json
{
  "executionEnvironments": [
    {
      "root": "src/web",
      "pythonVersion": "3.10",
      "pythonPlatform": "Windows",
      "extraPaths": ["src/shared"],
      "reportMissingImports": "warning"
    },
    {
      "root": "src/tests",
      "reportPrivateUsage": false,
      "extraPaths": ["src"]
    },
    {
      "root": "src"
    }
  ]
}
```

Each environment can override:
- `root` (required) — root path for this environment
- `extraPaths` — additional search paths
- `pythonVersion` — Python version for this environment
- `pythonPlatform` — target platform
- Any diagnostic rule setting

## Diagnostic Categories

| Category | CLI behavior | LSP behavior |
|----------|-------------|--------------|
| `"error"` | Exit code 1 | Red squiggles |
| `"warning"` | Exit 1 if `failOnWarnings: true` | Yellow squiggles |
| `"information"` | Never fails | Blue info |
| `"hint"` | No effect (ignored in CLI) | Grayed out / strikethrough via diagnostic tags |
| `"none"` | Disabled entirely | Hidden |

Note: `"unreachable"`, `"unused"`, `"deprecated"` are deprecated aliases for `"hint"`.

## File-level Comments

```python
# pyright: strict
```
Enable strict mode for a single file.

```python
# pyright: basic, reportPrivateUsage=false
```
Override specific settings per file.

```python
# pyright: reportPrivateUsage=warning, reportOptionalCall=error
```
Set diagnostic levels per file.

## Line-level Suppression

```python
x = foo()  # pyright: ignore[reportUnknownVariableType]
```

Prefer `# pyright: ignore[ruleName]` over `# type: ignore`:
- `type: ignore` suppresses all checkers, not just basedpyright
- `type: ignore` accepts invalid rule names silently
- `type: ignore` is disabled by default in basedpyright

## CLI Flags

| Flag | Description |
|------|-------------|
| `--createstub <IMPORT>` | Create type stub file(s) for import |
| `--dependencies` | Emit import dependency information |
| `--ignoreexternal` | Ignore external imports for `--verifytypes` |
| `--level <LEVEL>` | Minimum diagnostic level (`error` or `warning`) |
| `--outputjson` | Output results in JSON format |
| `--gitlabcodequality` | Output GitLab code quality report |
| `--writebaseline` | Write new errors to the baseline file |
| `--baselinefile <FILE>` | Path to baseline file (default: `.basedpyright/baseline.json`) |
| `--baselinemode <MODE>` | Baseline mode: `auto`, `lock`, `discard` |
| `-p, --project <PATH>` | Config file or directory |
| `--pythonpath <FILE>` | Path to Python interpreter (preferred over `--venvpath`) |
| `--pythonplatform <PLATFORM>` | Analyze for platform |
| `--pythonversion <VERSION>` | Analyze for version |
| `--skipunannotated` | Skip type analysis of unannotated functions |
| `--stats` | Print performance stats |
| `-t, --typeshedpath <DIR>` | Custom typeshed directory |
| `--threads [N]` | Parallelize across N threads (experimental) |
| `-v, --venvpath <DIR>` | Directory containing venvs (discouraged) |
| `--verbose` | Verbose diagnostics |
| `--verifytypes <IMPORT>` | Verify completeness of types in py.typed package |
| `--version` | Print version and exit |
| `--warnings` | Exit 1 on warnings (redundant — enabled by default) |
| `-w, --watch` | Watch mode — reanalyze on file changes |
| `-` | Read file/directory list from stdin |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No errors reported |
| 1 | One or more errors/warnings reported |
| 2 | Fatal error (no errors/warnings) |
| 3 | Config file could not be read or parsed (includes invalid keys) |
| 4 | Illegal command-line parameters |

## Baseline Modes

| Mode | Behavior |
|------|----------|
| `auto` | Update baseline only when errors are removed and no new ones added. Default locally |
| `lock` | Never write to baseline, exit non-zero if baseline needs updating. Default in CI |
| `discard` | Read baseline but never update. Exit 0 unless new diagnostics surface |

The `--writebaseline` flag always updates the baseline file regardless of mode.

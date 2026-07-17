# Configuration Reference

## Config File Precedence

1. `pyrightconfig.json` (highest priority, if present)
2. `[tool.basedpyright]` in `pyproject.toml`
3. `[tool.pyright]` in `pyproject.toml` (backward compatibility)
4. Language server settings (lowest priority, ignored if config file exists)

## Environment Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `include` | array of paths | `[workspace root]` | Directories/files to consider |
| `exclude` | array of paths | `["**/node_modules", "**/__pycache__", "**/.*"]` | Directories/files to exclude |
| `strict` | array of paths | `[]` | Paths using strict analysis |
| `extends` | path | — | Base config file to inherit from |
| `defineConstant` | map | `{}` | Constants assumed to have fixed values |
| `typeshedPath` | path | bundled | Custom typeshed directory |
| `stubPath` | path | `./typings` | Custom type stub directory |
| `verboseOutput` | boolean | `false` | Verbose logging |
| `extraPaths` | array of strings | `[]` | Additional module search paths |
| `pythonVersion` | string | current interpreter | Target Python version (`"3.11"`) |
| `pythonPlatform` | string | `"All"` | Target platform |
| `executionEnvironments` | array of objects | `[]` | Per-directory config overrides |
| `useLibraryCodeForTypes` | boolean | `true` | Analyze library code for types |

### basedpyright-exclusive environment settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `failOnWarnings` | boolean | `true` | Exit code 1 on warnings |
| `allowedUntypedLibraries` | array of strings | `[]` | Suppress unknown-type rules for specific modules |
| `baselineFile` | path | `./.basedpyright/baseline.json` | Baseline file path |

### Discouraged settings

| Setting | Reason |
|---------|--------|
| `venvPath` | Use `--pythonpath` or rely on `.venv` auto-detection |
| `venv` | Use `--pythonpath` or rely on `.venv` auto-detection |

## Execution Environment Options

```toml
executionEnvironments = [
    { root = "src/web", pythonVersion = "3.11", extraPaths = ["src/libs"] },
    { root = "tests", reportPrivateUsage = false },
    { root = "src" },  # catch-all, must be last
]
```

| Setting | Required | Description |
|---------|----------|-------------|
| `root` | Yes | Root path for this environment |
| `extraPaths` | No | Additional search paths |
| `pythonVersion` | No | Python version for this environment |
| `pythonPlatform` | No | Platform for this environment |

Any diagnostic rule can also be specified per-environment as an override.

## Type Evaluation Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `strictListInference` | boolean | `false` | Strict list type inference |
| `strictDictionaryInference` | boolean | `false` | Strict dict type inference |
| `strictSetInference` | boolean | `false` | Strict set type inference |
| `analyzeUnannotatedFunctions` | boolean | `false` | Analyze unannotated functions |
| `strictParameterNoneValue` | boolean | `false` | Require explicit `Optional` for `None` defaults |
| `deprecateTypingAliases` | boolean | `false` | Deprecate `typing.List` etc. (3.9+) |
| `enableExperimentalFeatures` | boolean | `false` | Enable experimental features |
| `disableBytesTypePromotions` | boolean | `false` | No `bytearray`/`memoryview` → `bytes` promotion |

### basedpyright-exclusive evaluation settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `strictGenericNarrowing` | boolean | `false` | Narrow generics to bound on isinstance |
| `enableBasedFeatures` | boolean | `false` | Extra dataclass_transform features |

## Discouraged settings

| Setting | Alternative |
|---------|-------------|
| `enableTypeIgnoreComments` | Use `# pyright: ignore[rule]` instead |
| `enableReachabilityAnalysis` | Use `reportUnreachable` instead |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LC_ALL` | Override locale (highest priority) |
| `LC_MESSAGES` | Override locale |
| `LANG` | Override locale |
| `LANGUAGE` | Override locale (lowest priority) |

Locale specifiers: `xx-xx` or `xx_XX` format (e.g., `en-us`, `zh_CN`, `de`).

## Language Server Settings

Configure via your editor's LSP settings under `basedpyright.analysis.*`:

| Setting | Description |
|---------|-------------|
| `openFilesOnly` | Only check open files (default: false) |
| `autoFormatStrings` | Auto-convert to f-string on `{` inside strings |
| `typeCheckingMode` | Override type checking mode |
| `pythonPath` | Path to Python interpreter |
| `venvPath` | Directory containing virtual environments |
| `venv` | Virtual environment name |
| `extraPaths` | Additional search paths |
| `pythonVersion` | Target Python version |
| `pythonPlatform` | Target platform |
| `stubPath` | Custom stub directory |
| `useLibraryCodeForTypes` | Use library source for types |
| `disableLanguageServices` | Disable language services (type-check only) |
| `importStrategy` | `"fromEnvironment"` or `"useBundled"` |
| `showInlayHints` | Show inlay hints |
| `autoImportCompletions` | Show auto-import completions |

### Discouraged language server settings

If a `pyproject.toml` or `pyrightconfig.json` exists, these settings are ignored:
- `pythonPath`, `venvPath`, `venv` — use config file instead
- Environment configuration options should be in the project config, not per-user

## Sample Configurations

### Minimal (rely on defaults)

```toml
[tool.basedpyright]
pythonVersion = "3.11"
```

### Strict new project

```toml
[tool.basedpyright]
pythonVersion = "3.11"
typeCheckingMode = "all"
strict = ["src"]
```

### Gradual adoption with baseline

```toml
[tool.basedpyright]
pythonVersion = "3.11"
typeCheckingMode = "recommended"
failOnWarnings = true
baselineFile = ".basedpyright/baseline.json"
allowedUntypedLibraries = ["legacy-lib", "untyped-sdk"]
```

### Multi-environment

```toml
[tool.basedpyright]
pythonVersion = "3.11"
pythonPlatform = "All"

[[tool.basedpyright.executionEnvironments]]
root = "src"
pythonVersion = "3.11"

[[tool.basedpyright.executionEnvironments]]
root = "tests"
pythonVersion = "3.11"
reportPrivateUsage = false

[[tool.basedpyright.executionEnvironments]]
root = "scripts"
pythonVersion = "3.10"
typeCheckingMode = "off"
```

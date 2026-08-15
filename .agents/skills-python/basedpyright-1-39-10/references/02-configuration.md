# Configuration

## Contents

- [Config files](#config-files)
- [Environment options](#environment-options)
- [Type evaluation settings](#type-evaluation-settings)
- [Execution environments](#execution-environments)
- [Sample configs](#sample-configs)
- [Command-line reference](#command-line-reference)
- [JSON output](#json-output)
- [GitLab code quality report](#gitlab-code-quality-report)
- [Baseline CLI options](#baseline-cli-options)
- [Environment variables and locales](#environment-variables-and-locales)

## Config files

- `pyrightconfig.json` at the project root, or a `[tool.basedpyright]` table in
  `pyproject.toml`. A `[tool.pyright]` table is also read for backwards compatibility.
  `pyrightconfig.json` always takes precedence over `pyproject.toml` when both exist.
- Multi-root workspaces are supported; each root can have its own config.
- Relative paths are relative to the config file's location. Shell variables and `~`
  are not supported — prefer relative paths so the config is shareable.
- If a config file exists, discouraged language-server settings (e.g. in VS Code
  `settings.json`) are ignored.

## Environment options

These control the environment used for checking: how source files and imports are
found, and which Python version/platform rules apply.

| Setting | Type | Notes |
|---|---|---|
| `include` | array of paths | Directories/files that are part of the project. Wildcards `**`, `*`, `?` supported. Defaults to the config file's directory |
| `exclude` | array of paths | Override `include`. Defaults to `**/node_modules`, `**/__pycache__`, `**/.*`; venv directories are always excluded. Excluded files are still analyzed if imported by included files |
| `strict` | array of paths | Paths checked in strict mode, same as adding `# pyright: strict` to each file |
| `extends` | path | Another `.json`/`.toml` used as base config; top-level keys here override the base. Multi-level inheritance supported |
| `defineConstant` | map of identifier to bool/string | Assume identifiers hold a constant value (e.g. `{ "DEBUG": true }`) for reachability analysis |
| `typeshedPath` | path | Use a different typeshed copy (bundled typeshed is used otherwise) |
| `stubPath` | path | Directory of custom type stubs, one subdirectory per package. Default `./typings` (`typingsPath` is deprecated) |
| `verboseOutput` | boolean | Verbose logging, useful for import-resolution problems |
| `extraPaths` | array of paths | Additional module search paths |
| `pythonVersion` | string `"M.m"` | Analyze for a specific Python version; errors on newer syntax, tailors version-conditional stubs. Defaults to the configured interpreter's version |
| `pythonPlatform` | `"Windows"`/`"Darwin"`/`"Linux"`/`"iOS"`/`"Android"`/`"All"` | basedpyright defaults to `"All"` (pyright defaults to the host OS) |
| `executionEnvironments` | array of objects | Per-subtree environments, see below |
| `useLibraryCodeForTypes` | boolean | Read/analyze untyped library source for types (default `true`) |

BasedPyright-exclusive:

| Setting | Type | Notes |
|---|---|---|
| `failOnWarnings` | boolean | Non-zero CLI exit on warnings. Default on in `recommended`/`all` (no effect in the language server). Equivalent to `--warnings` |
| `allowedUntypedLibraries` | array of module names | Suppresses `reportUnknownVariableType`, `reportUnknownMemberType`, `reportMissingTypeStubs` for the listed modules, e.g. `["library", "module.submodule"]` |
| `baselineFile` | path | Baseline file location. Default `./.basedpyright/baseline.json` |

Discouraged (still supported for compatibility):

| Setting | Type | Notes |
|---|---|---|
| `venvPath` | path | Directory containing venvs; used with `venv` |
| `venv` | string | Name of the venv to use, paired with `venvPath` |

basedpyright prefers `pythonPath` (or its automatic `./.venv` detection) over these.

## Type evaluation settings

| Setting | Type | Notes |
|---|---|---|
| `strictListInference` | boolean | `[1, 'a']` infers `list[int \| str]` instead of `list[Any]` |
| `strictDictionaryInference` | boolean | Same for dict keys/values |
| `strictSetInference` | boolean | Same for sets |
| `analyzeUnannotatedFunctions` | boolean | Analyze functions with no annotations (default `true`; also needed for completions) |
| `strictParameterNoneValue` | boolean | A `None` default requires an explicit `Optional` in the annotation |
| `deprecateTypingAliases` | boolean | Flag PEP 585-deprecated `typing` aliases (`typing.List` etc.); on in `recommended`/`all` |
| `enableExperimentalFeatures` | boolean | Undocumented, unstable typing proposals — experimentation only |
| `disableBytesTypePromotions` | boolean | Disables legacy `bytearray`/`memoryview` as `bytes` subtypes (PEP 688) |

BasedPyright-exclusive:

| Setting | Type | Notes |
|---|---|---|
| `strictGenericNarrowing` | boolean | Narrow generics to their bound/constraint (or `object`) instead of `Unknown` under `isinstance`. On in `recommended`/`all`, off in `strict` |
| `enableBasedFeatures` | boolean | Unlocks basedpyright-only typing features not in the type system standard, currently the extra `dataclass_transform` options. Off in all modes; keep off in libraries whose users may run pyright |

Extra `dataclass_transform` keyword options (require `enableBasedFeatures = true`):
`skip_replace=True` disables synthesis of the `__replace__` method (it interferes with
variance inference of frozen dataclasses); `frozen_default` is used the same way.
Example:

```python
from typing import dataclass_transform

@dataclass_transform(skip_replace=True, frozen_default=True)
def frozen[T: type](t: T) -> T:
    return dataclass(frozen=True, slots=True)(t)
```

Discouraged:

| Setting | Type | Notes |
|---|---|---|
| `enableTypeIgnoreComments` | boolean | Enables `# type: ignore` support; off by default in `recommended`/`all`. Use `# pyright: ignore[rule]` instead — those are validated against real rule names |
| `enableReachabilityAnalysis` | boolean | Tagged-hint reporting of unreachable code; superseded by the `reportUnreachable` rule |

The full per-rule severity table for every mode is in
[01-diagnostic-rules](01-diagnostic-rules.md); any `reportXxx` rule can be set to a
boolean or `"none"`/`"hint"`/`"information"`/`"warning"`/`"error"`.

## Execution environments

`executionEnvironments` maps subtrees to different analysis environments. Each source
file belongs to at most one environment — the first whose `root` contains it.

Per-environment settings:

- `root` (required) — root path for the code in this environment
- `extraPaths` — search paths for imports of files in this environment (overrides the
  global `extraPaths` for those files)
- `pythonVersion` / `pythonPlatform` — override the globals
- any type-check diagnostic setting — per-environment rule overrides

## Sample configs

`pyrightconfig.json`:

```json
{
  "include": ["src"],
  "exclude": ["**/node_modules", "**/__pycache__", "src/experimental"],
  "ignore": ["src/oldstuff"],
  "defineConstant": { "DEBUG": true },
  "stubPath": "src/stubs",
  "reportMissingImports": "error",
  "reportMissingTypeStubs": false,
  "pythonVersion": "3.12",
  "pythonPlatform": "All",
  "executionEnvironments": [
    { "root": "src/tests", "reportPrivateUsage": false, "extraPaths": ["src/tests/e2e"] },
    { "root": "src" }
  ]
}
```

`pyproject.toml`:

```toml
[tool.basedpyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__"]
reportMissingTypeStubs = "none"
pythonVersion = "3.12"
allowedUntypedLibraries = ["some_untyped_lib"]
```

`ignore` suppresses diagnostics for the given paths even if the files are otherwise
included.

## Command-line reference

`basedpyright [options] [files...]` — explicit files override the config's `include`.

| Flag | Description |
|---|---|
| `--createstub <IMPORT>` | Create draft type stub file(s) for the import |
| `--dependencies` | Emit import dependency information |
| `-h, --help` | Show help |
| `--ignoreexternal` | Ignore external imports for `--verifytypes` |
| `--level <LEVEL>` | Minimum diagnostic level to report (`error` or `warning`) |
| `--outputjson` | Output results as JSON |
| `--gitlabcodequality <FILE>` | Write a GitLab code quality report to FILE |
| `--writebaseline` | Write new errors to the baseline file (recommended baseline control) |
| `--baselinefile <FILE>` | Baseline file path (default `./.basedpyright/baseline.json`) |
| `--baselinemode <MODE>` | Experimental — `auto`, `lock`, or `discard` (see below) |
| `-p, --project <FILE OR DIR>` | Use the config file at this location |
| `--pythonpath <FILE>` | Path to the Python interpreter (preferred over `--venvpath`; not combinable with it) |
| `--pythonplatform <PLATFORM>` | Analyze for a platform (Darwin, Linux, Windows, iOS, Android) |
| `--pythonversion <VERSION>` | Analyze for a version (e.g. `3.12`) |
| `--skipunannotated` | Skip type analysis of unannotated functions |
| `--stats` | Print detailed performance stats |
| `-t, --typeshedpath <DIR>` | Use typeshed stubs from this directory |
| `--threads [N]` | Experimental — parallelize across up to N threads (default: logical CPU count if >= 4, else 1) |
| `-v, --venvpath <DIR>` | Directory containing virtual environments (discouraged) |
| `--verbose` | Emit verbose diagnostics (import resolution debugging) |
| `--verifytypes <IMPORT>` | Verify completeness of types in a `py.typed` package |
| `--version` | Print version and exit |
| `--warnings` | Exit 1 on warnings (redundant unless `failOnWarnings` is disabled) |
| `-w, --watch` | Keep running and re-analyze modified files incrementally |
| `-` | Read the file/directory list from stdin |

Exit codes: `0` no errors; `1` one or more errors (or warnings with
`failOnWarnings`/`--warnings`); `2` fatal error with nothing reported; `3` config file
could not be read or parsed; `4` illegal command-line parameters.

## JSON output

With `--outputjson`, diagnostics are emitted as:

```json
{
  "version": "1.39.10",
  "time": "...",
  "generalDiagnostics": [
    {
      "file": "src/foo.py",
      "cell": "1",
      "severity": "error",
      "message": "...",
      "rule": "reportAssignmentType",
      "range": {
        "start": { "line": 0, "character": 0 },
        "end": { "line": 0, "character": 10 }
      }
    }
  ],
  "summary": {
    "filesAnalyzed": 1,
    "errorCount": 1,
    "warningCount": 0,
    "informationCount": 0,
    "timeInSec": 0.1
  }
}
```

Line/character numbers are zero-based. `cell` appears for Jupyter notebooks. `rule` is
present only for diagnostics tied to a toggleable rule.

## GitLab code quality report

`--gitlabcodequality <FILE>` writes a GitLab code quality report. In `.gitlab-ci.yml`:

```yaml
basedpyright:
  script: basedpyright --gitlabcodequality report.json
  artifacts:
    reports:
      codequality: report.json
```

GitHub Actions needs no wrapper — basedpyright auto-detects the environment and emits
workflow commands that annotate pull requests.

## Baseline CLI options

- Default behavior — locally, the baseline file updates automatically when diagnostics
  are removed (and no new ones are added); in CI it is locked (never written) and the
  run exits non-zero if it needs updating.
- `--writebaseline` — always update the baseline, even if new errors are added. Use it
  to intentionally baseline new errors (e.g. after enabling a rule).
- `--baselinemode` (experimental, prefer `--writebaseline`):
  - `auto` — update only when diagnostics were removed and none were added (the local default)
  - `lock` — never write; exit non-zero if the baseline is stale (the CI default)
  - `discard` — read the baseline but never update it; exit 0 unless new diagnostics surfaced

## Environment variables and locales

- `PYRIGHT_TMPDIR` — absolute path used when the platform temp directory is missing or
  unwritable (remote/server environments); created if needed.

Locale of diagnostic messages (priority order): `LC_ALL`, `LC_MESSAGES`, `LANG`,
`LANGUAGE`. Both `xx-xx` and `xx_XX` forms are accepted. In VS Code the editor's locale
takes precedence.

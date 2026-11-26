# Configuration Reference

Config lives in `pyrightconfig.json` (project root) or `[tool.basedpyright]` in
`pyproject.toml`; `[tool.pyright]` also works for compatibility. `pyrightconfig.json`
always takes precedence over `pyproject.toml`. Relative paths are relative to the config
file's location; shell variables and `~` are not supported.

## Environment options

- **include** — directories/files in the project (default: config file's directory). Glob
  patterns `*`, `**`, `?` supported.
- **exclude** — overrides include; defaults also exclude `**/node_modules`,
  `**/__pycache__`, hidden dirs, and auto-detected venvs. Your entries are added on top.
- **strict** — paths checked in strict mode (same as `# pyright: strict`).
- **extends** — inherit from another `.json`/`.toml` config; top-level keys here win.
- **defineConstant** — map of identifiers assumed constant for reachability analysis,
  e.g. `{ "DEBUG": true }`.
- **extraPaths** — additional module search paths (globs allowed).
- **pythonVersion** — `"M.m"` string; errors on language features newer than this.
- **pythonPlatform** — `Windows`, `Darwin`, `Linux`, `iOS`, `Android`, or `All`
  (basedpyright default is `All`; pyright defaults to the host OS).
- **typeshedPath** / **stubPath** — override bundled typeshed stubs / custom stub dir
  (default `./typings`).
- **executionEnvironments** — per-subdirectory environments with their own paths, version,
  and platform.
- **useLibraryCodeForTypes** — analyze untyped library source for type info (default true).

### basedpyright-exclusive settings

- **failOnWarnings** (default `true`) — non-zero CLI exit on warnings. Equivalent to
  `--warnings`.
- **allowedUntypedLibraries** — list of module names whose unknown-type imports suppress
  `reportUnknownVariableType`, `reportUnknownMemberType`, and `reportMissingTypeStubs`.
  Useful for third-party packages without proper typing.
- **baselineFile** — baseline path, default `./.basedpyright/baseline.json`.

### Discouraged in basedpyright

- **venvPath** / **venv** — use `--pythonpath`/`pythonPath`; basedpyright auto-detects
  `./.venv` at project root.
- **enableTypeIgnoreComments** — `# type: ignore` support, off by default; prefer
  `# pyright: ignore[rule]`.
- **enableReachabilityAnalysis** — prefer the `reportUnreachable` rule instead.

## Type evaluation settings

- **strictListInference** / **strictDictionaryInference** / **strictSetInference** — infer
  `list[int | str | float]` instead of `list[Any]` for mixed-literal collections.
- **analyzeUnannotatedFunctions** — check functions with no annotations at all.
- **strictParameterNoneValue** — require explicit `Optional` when a default is `None`.
- **deprecateTypingAliases** — flag PEP 585-deprecated typing aliases (Python 3.9+).
- **enableExperimentalFeatures** — opt into proposed/exploratory typing features.
- **strictGenericNarrowing** (basedpyright) — when narrowing a generic whose parameters are
  unknown, resolve to the bound/constraint instead of `Any`.
- **enableBasedFeatures** (basedpyright) — basedpyright-specific behavior not in the Python
  type system (currently extra `dataclass_transform` features). Keep off if your library
  targets plain-pyright users.

## typeCheckingMode

Values: `"off"`, `"basic"`, `"standard"`, `"strict"`, `"recommended"` (default), `"all"`.
In basedpyright, `"off"` truly disables all type-checking rules (syntax/semantic errors
still reported). Individual rules can be overridden per-rule with severity values
`"error"`, `"warning"`, `"information"`, `"hint"`, or `"none"`.

## Diagnostic categories

- `error` — CLI exit 1
- `warning` — CLI exit 1 only if `failOnWarnings` (default on)
- `information` — never fails CLI
- `hint` — language server only, not reported by the CLI; baselined diagnostics are hints
- `none` — disabled

`"unreachable"`, `"unused"`, `"deprecated"` are deprecated aliases for `"hint"`.

## Baseline modes

Baseline freezes existing errors so only new/modified code reports. Create with
`basedpyright --writebaseline`; commit the resulting file. Fixed errors are removed from
the baseline automatically in local runs.

- **Default / `--baselinemode=auto`** — locally, the baseline is updated when diagnostics
  are removed and none added. In CI (auto-detected), behavior is `lock`.
- **`--writebaseline`** — always update the baseline file, even if new errors appear. Use
  deliberately when enabling a new rule or re-baselining.
- **`--baselinemode=lock`** — never write; exit non-zero if the baseline is stale. This is
  the CI default: contributors must commit an updated baseline after fixing code.
- **`--baselinemode=discard`** — read but never update the baseline; exit 0 unless new
  diagnostics surface.

Each baselined error matches by file path (relative to project root), diagnostic rule name,
and column position (not line, so adding/removing lines doesn't resurface errors).

## Sample config files

`pyrightconfig.json`:

```json
{
    "include": ["src"],
    "exclude": ["**/node_modules", "**/__pycache__"],
    "typeCheckingMode": "recommended",
    "failOnWarnings": true,
    "pythonVersion": "3.12",
    "allowedUntypedLibraries": ["legacy_lib"]
}
```

`pyproject.toml`:

```toml
[tool.basedpyright]
include = ["src"]
typeCheckingMode = "recommended"
failOnWarnings = true
pythonVersion = "3.12"
```

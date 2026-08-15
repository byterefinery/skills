# Baseline Reference

## Overview

Baseline allows gradual adoption of strict type checking in existing codebases. It
generates a file tracking existing errors so only new/modified code errors are reported.

## Workflow

### 1. Generate baseline

```bash
basedpyright --writebaseline
```

Creates `.basedpyright/baseline.json` with all current errors.

### 2. Commit the baseline file

```bash
git add .basedpyright/baseline.json
git commit -m "Add basedpyright baseline"
```

### 3. Run normally

```bash
basedpyright
```

Only errors in new or modified code are reported. Existing baselined errors are
shown as hints in the language server (greyed out).

### 4. Baseline auto-updates

As you fix errors, running `basedpyright` locally automatically removes them from
the baseline:

```
> basedpyright
updated ./.basedpyright/baseline.json with 195 errors (went down by 5)
0 errors, 0 warnings, 0 notes
```

## Baseline Modes

### CLI behavior

| Context | Default mode | Behavior |
|---------|-------------|----------|
| Local (no CI) | `auto` | Updates baseline when errors removed, fails if new errors added |
| CI environment | `lock` | Never writes, fails if baseline needs updating |

### `--writebaseline` flag

- **Not specified**: Uses default behavior (auto locally, lock in CI)
- **Specified**: Always updates baseline, even if new errors are added

### `--baselinemode` (experimental)

| Mode | Behavior |
|------|----------|
| `auto` | Updates baseline only when errors are removed (no new errors) |
| `lock` | Never writes, fails if baseline needs updating |
| `discard` | Reads baseline but never updates, ignores stale entries |

```bash
basedpyright --baselinemode=auto    # Force local behavior in CI
basedpyright --baselinemode=lock    # Lock behavior locally
basedpyright --baselinemode=discard # Read-only baseline
```

## Baseline File Format

```json
{
    "version": "1.39.9",
    "diagnostics": [
        {
            "file": "src/module.py",
            "rule": "reportAny",
            "column": 12
        }
    ]
}
```

Each diagnostic is matched by:
- **File path** — relative to project root
- **Rule name** — diagnostic rule (e.g., `reportAny`)
- **Column** — column position only (not line), preventing resurfacing when lines are added/removed

## Common Scenarios

### Enabling a new rule and baselining its errors

```bash
# 1. Enable the new rule in config
# 2. Run with --writebaseline to capture its violations
basedpyright --writebaseline
# 3. Commit the updated baseline
git add .basedpyright/baseline.json
git commit -m "Enable reportAny with baseline"
```

### Error resurfaced after moving code

```bash
# Regenerate baseline to fix stale entries
basedpyright --writebaseline
```

### Disabling automatic baseline updates

Set `baselineMode` in language server settings or use `--baselinemode=discard` in CLI.
Alternative: use a pre-commit hook to update baseline at commit time.

### Custom baseline file path

```toml
[tool.basedpyright]
baselineFile = ".typecheck-baseline.json"
```

Or via CLI:

```bash
basedpyright --baselinefile .custom-baseline.json
```

## CI Integration

### GitHub Actions

```yaml
- name: Type check
  run: uv run basedpyright
  # In CI, baseline defaults to lock mode
  # Fails if baseline needs updating (errors removed but not committed)
```

### GitLab CI

```yaml
basedpyright:
  script: basedpyright
  # Lock mode by default in CI
  # Optionally combine with code quality report:
  # basedpyright --gitlabcodequality report.json
```

### Pre-commit hook

```yaml
repos:
  - repo: local
    hooks:
      - id: basedpyright
        name: basedpyright
        entry: uv run basedpyright
        language: system
        types: [python]
        pass_filenames: false
```

## Baseline vs `# pyright: ignore`

| | Baseline | `# pyright: ignore` |
|---|---------|---------------------|
| Scope | Entire project | Single line |
| Use case | Adopt strict rules gradually | Suppress false positives |
| Maintenance | Auto-updates as errors fixed | Manual cleanup |
| Visibility | Hints in editor | Completely hidden |

Use baseline for adopting new rules across an existing codebase. Use `# pyright: ignore[rule]`
for suppressing specific false positives or known limitations.

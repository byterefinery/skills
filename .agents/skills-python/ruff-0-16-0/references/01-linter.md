# Linter

## Rule Selection

Ruff mirrors Flake8's rule code system: one-to-three letter prefix + three digits (e.g., `F401`). Prefixes indicate the rule source:

| Prefix | Source |
|--------|--------|
| `E`/`W` | pycodestyle |
| `F` | Pyflakes |
| `B` | flake8-bugbear |
| `UP` | pyupgrade |
| `I` | isort |
| `D` | pydocstyle |
| `SIM` | flake8-simplify |
| `N` | pep8-naming |
| `C9` | mccabe |
| `RUF` | Ruff-specific |

### Select vs Extend-Select

```toml
# Replaces all defaults — only E and F rules enabled
select = ["E", "F"]

# Adds B and UP on top of defaults
extend-select = ["B", "UP"]
```

CLI equivalents: `--select E,F` vs `--extend-select B,UP`.

### Ignore

```toml
ignore = ["E501"]              # disable line-too-long everywhere
```

### Per-file ignores

```toml
[lint.per-file-ignores]
"__init__.py" = ["E402"]
"**/{tests,docs}/*" = ["D"]
```

### Fixable / Unfixable

```toml
fixable = ["ALL"]              # all rules eligible for --fix
unfixable = ["F401"]           # never auto-fix unused imports
```

### ALL selector

`select = ["ALL"]` enables every rule. Conflicting pydocstyle rules are auto-disabled. Use with discretion — new rules are implicitly enabled on upgrade.

## Fix Safety

Ruff classifies fixes as **safe** (preserves runtime behavior) and **unsafe** (may change behavior, exception types, or remove comments).

```bash
ruff check --fix               # safe fixes only
ruff check --fix --unsafe-fixes  # include unsafe fixes
```

Unsafe fix example: `list(...)[0]` → `next(iter(...))` changes `IndexError` to `StopIteration` on empty collections.

Adjust per-rule safety:

```toml
extend-safe-fixes = ["F601"]       # promote to safe
extend-unsafe-fixes = ["UP034"]    # demote to unsafe
```

## Error Suppression

### Line-level noqa

```python
x = 1  # noqa: F841                # specific rule
x = 1  # noqa: E741, F841          # multiple rules
x = 1  # noqa                       # all rules on this line
```

For multi-line strings, place `noqa` after the closing quotes:

```python
"""Long docstring that exceeds line length and should not trigger E501."""  # noqa: E501
```

### Line-level ignore (own-line)

```python
# ruff: ignore[ARG001]  # covers entire function signature
def foo(
    arg1,
    arg2,
):
    pass
```

### Block-level disable/enable

```python
# ruff: disable[E501]
VALUE_1 = "Lorem ipsum dolor sit amet ..."
VALUE_2 = "Lorem ipsum dolor sit amet ..."
# ruff: enable[E501]
```

Without a matching `enable`, the range extends implicitly to the next dedented scope (triggers `RUF104` warning).

### File-level noqa

```python
# ruff: noqa                    # suppress all rules
# ruff: noqa: F841              # suppress specific rule
# ruff: file-ignore[F401, ARG001]  # suppress specific rules
```

Ruff also respects `# flake8: noqa`.

### isort action comments

```python
# isort: skip_file
# isort: on / # isort: off
# isort: skip
# isort: split
```

Ruff also recognizes `# ruff: isort: skip_file` variants.

## Unused Suppressions

Enable `RUF100` to detect `noqa` comments that no longer suppress any active violations:

```bash
ruff check --extend-select RUF100       # flag unused noqa
ruff check --extend-select RUF100 --fix # remove unused noqa
```

## Adding Suppressions to Existing Code

When introducing a new rule to an existing codebase:

```bash
ruff check --select UP035 --add-noqa .   # add noqa to existing violations
ruff check --select UP035 --add-ignore . # add ruff: ignore comments
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No violations, or all violations fixed |
| 1 | Violations found |
| 2 | Abnormal termination (bad config, invalid CLI, internal error) |

Flags:
- `--exit-zero` — always exit 0 (even with violations)
- `--exit-non-zero-on-fix` — exit 1 if files were modified via fix

## Output Formats

```bash
ruff check --output-format concise    # file:line:col: code message
ruff check --output-format full       # default, with source snippet
ruff check --output-format json       # machine-readable JSON
ruff check --output-format json-lines # NDJSON
ruff check --output-format github     # GitHub Actions annotations
ruff check --output-format gitlab     # GitLab CI
ruff check --output-format pylint     # Pylint-compatible
ruff check --output-format sarif      # SARIF (static analysis)
ruff check --output-format rdjson     # Diagnostic JSON (Ruff Dev)
ruff check --output-format azure      # Azure Pipelines
ruff check --output-format junit      # JUnit XML
ruff check --output-format grouped   # grouped by file
```

## Rule Documentation

```bash
ruff rule F401          # explain a single rule
ruff rule F401 --output-format full  # with fix example
ruff linter             # list all supported upstream linters
```

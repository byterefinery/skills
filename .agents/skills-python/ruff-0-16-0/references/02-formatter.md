# Formatter

## Overview

Ruff's formatter is a drop-in replacement for Black, targeting >99.9% identical output on existing Black-formatted code. It differs from Black in a few conscious ways documented below.

```bash
ruff format                   # format in-place
ruff format --check           # check without writing (CI)
ruff format --diff            # show diff
ruff format --line-length 100 # override line length
```

## Configuration

```toml
[format]
quote-style = "double"           # "double" or "single"
indent-style = "space"           # "space" or "tab"
skip-magic-trailing-comma = false  # respect trailing commas for grouping
line-ending = "auto"             # "auto", "line-feed", "carriage-return", "carriage-return-line-feed"
docstring-code-format = false    # format code examples in docstrings
docstring-code-line-length = "dynamic"  # or a fixed integer
```

## Format Suppression

```python
# fmt: off
not_formatted = 3
# fmt: on

a = [1, 2, 3]  # fmt: skip   # skip this statement
```

Ruff also recognizes YAPF's `# yapf: disable` / `# yapf: enable`.

`# fmt: skip` applies to case headers, decorators, function/class definitions, or the preceding statement on the same logical line. It does not work inside expressions — apply it to the full statement.

## Docstring Code Formatting

When `docstring-code-format = true`, Ruff formats Python code examples inside docstrings:

- Python doctest format
- Markdown fenced code blocks (`python`, `py`, `python3`, `py3`, or no language)
- reStructuredText literal blocks
- reStructuredText `code-block` / `sourcecode` directives

Invalid Python code blocks are skipped automatically.

## Markdown Code Formatting

Ruff formats Python code blocks in `.md` files. Recognized info strings: `python`, `py`, `python3`, `py3`, `pyi`. Also supports Quarto-style `{python}` blocks.

Suppress with HTML comments:

```markdown
<!-- fmt:off -->
```py
print( 'hello' )
```
<!-- fmt:on -->
```

Also recognizes `<!-- blacken-docs:off -->` / `<!-- blacken-docs:on -->`.

To include Markdown in pre-commit, add `types_or: [python, pyi, jupyter, markdown]`.

To disable Markdown formatting:

```toml
extend-exclude = ["*.md"]
```

## Conflicting Lint Rules

When using both linter and formatter, avoid these rules that conflict with formatting:

- `W191` (tab-indentation)
- `E111`, `E114`, `E117` (indentation rules)
- `D203`, `D206` (docstring indentation)
- `D300` (triple-single-quotes)
- `Q000`-`Q004` (quote rules)
- `COM812`, `COM819` (trailing comma rules)
- `ISC002` (without `ISC001` and `allow-multiline = false`)

`E501` (line-too-long) can be used alongside the formatter, but the formatter only makes best-effort attempts to wrap lines.

Incompatible isort settings:
- `force-single-line`
- `force-wrap-aliases`
- `lines-after-imports`
- `lines-between-types`
- `split-on-trailing-comma`

## Exit Codes

`ruff format`:
| Code | Meaning |
|------|---------|
| 0 | Success (files formatted) |
| 1 | Success + `--exit-non-zero-on-format` was set |
| 2 | Abnormal termination |

`ruff format --check`:
| Code | Meaning |
|------|---------|
| 0 | All files already formatted |
| 1 | Some files would be reformatted |
| 2 | Abnormal termination |

## Known Deviations from Black

### F-string formatting

Ruff formats expression parts inside `{...}` of f-strings. Black does not. For nested f-strings, Ruff alternates quote styles (or uses `nested-string-quote-style = "preferred"` for Python 3.12+).

### Line breaks in f-strings

Ruff only splits f-string expressions across lines if there was already a line break within the `{...}` parts.

### Fluent layout for method chains

In preview mode, Ruff uses a different fluent layout for long method chains, breaking before the first attribute rather than after:

```python
# Ruff preview
x = (
    df
    .filter(cond)
    .agg(func)
    .merge(other)
)

# Black / Ruff stable
x = (
    df.filter(cond)
    .agg(func)
    .merge(other)
)
```

## Import Sorting

The formatter does not sort imports. Use the linter's `I` rules:

```bash
ruff check --select I --fix   # sort imports
ruff format                   # then format
```

## Preview Style

Formatter preview changes are gated behind `--preview` or `preview = true` in `[format]` section. Changes stabilize through minor releases.

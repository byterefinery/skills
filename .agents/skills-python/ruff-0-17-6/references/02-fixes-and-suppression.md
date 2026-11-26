# Ruff — Fixes and Suppression

## Fixes

`ruff check --fix` applies automatic fixes. Ruff labels fixes as **safe** or
**unsafe**: safe fixes preserve runtime behavior (they only remove comments when
deleting entire statements or expressions); unsafe fixes may change runtime
behavior, remove comments, or both (e.g. the `RUF015` fix changes the exception
raised on empty collections from `IndexError` to `StopIteration`).

- `--fix` — apply safe fixes only (default behavior).
- `--unsafe-fixes` — additionally apply unsafe fixes.
- `--fix-only` — apply fixes but do not report or exit non-zero for leftover
  violations (implies `--fix`).
- `--diff` — output fixes as a diff instead of writing (implies `--fix-only`).
- `--show-fixes` — enumerate fixed violations.
- The `full` output format always *displays* all suggested fixes (including unsafe
  and display-only ones), regardless of `unsafe-fixes`.

Per-rule safety overrides in config:

```toml
[tool.ruff.lint]
extend-safe-fixes = ["F601"]    # promote: F601 fixes become safe
extend-unsafe-fixes = ["UP034"] # demote: UP034 fixes become unsafe
```

Restricting which rules are fixable at all:

```toml
[tool.ruff.lint]
fixable = ["ALL"]
unfixable = ["F401"]   # no auto-fix for unused imports
```

## Suppression comments

Four levels: inline (`noqa`), line-level (`ruff: ignore`), block-level
(`ruff: disable` / `ruff: enable`), file-level (`ruff: noqa` / `ruff: file-ignore`).

### Inline — `# noqa`

Flake8-style, case-insensitive, on the violating line (or the line before a
multi-line construct's end):

```python
x = 1  # noqa               # ignore all violations on this line
i = 1  # noqa: E741, F841   # ignore specific codes
x = 1  # noqa: F841
```

- Multi-line strings: the `noqa` goes after the closing triple quote and applies
  to the entire string.
- Import blocks: `noqa` on the **first line** of the block applies to all imports
  in the block (`import os  # noqa: I001`).
- Missing delimiter warning: `# noqa: F401F841` is interpreted as two codes with a
  warning.

### Line-level — `# ruff: ignore[...]`

Case-sensitive `#ruff:`, on its own line. Placed **above the first line** of a
logical line, it covers the entire logical line (multi-line statement or suite
header); placed inside a multi-line statement, it covers only that physical line:

```python
# ruff: ignore[ARG001]  # covers the entire function signature
def foo(
    arg1,
    arg2,
):
    pass
```

Ignore comments stack and can be interleaved with other comments.

### Block-level — `# ruff: disable[...]` / `# ruff: enable[...]`

```python
# ruff: disable[E501]
VALUE_1 = "Lorem ipsum dolor sit amet ..."
VALUE_2 = "Lorem ipsum dolor sit amet ..."
# ruff: enable[E501]
```

- Codes must match exactly, in the same order, and at matching indentation.
- Without a matching `enable`, the range is *implicit* — it ends at the next
  logical scope indented less than the `disable` comment. Implicit ranges produce
  a `RUF104` diagnostic (disable it or add inline `noqa` to the `disable` line if
  intended).
- Cannot enable or select rules that aren't already selected; `enable` only
  terminates a matching `disable`. No blanket suppression (at least one code).

### File-level

Anywhere in the file (own line, preferably near the top):

```python
# ruff: noqa              # ignore everything in this file
# ruff: noqa: F841        # ignore F841 file-wide
# ruff: file-ignore[F401, ARG001]
```

Ruff also honors Flake8's `# flake8: noqa` as equivalent to `# ruff: noqa`.

In preview mode, `ruff: ignore`, `ruff: file-ignore`, `ruff: disable`, and
`ruff: enable` accept human-readable rule names (e.g. `unused-import`) in place of
codes.

## Unused and added suppressions

- **RUF100 (`unused-noqa`)** — flags suppression comments whose codes no longer
  match any violation:
  `ruff check --extend-select RUF100` (add `--fix` to *remove* stale comments).
- **`--add-noqa`** — automatically adds `# noqa` directives to all failing lines
  (useful when adopting a new rule on an existing codebase):
  `ruff check --select UP035 --add-noqa .`
- **`--add-ignore`** — same, but adds `# ruff: ignore` comments (uses rule *names*
  instead of codes in preview mode).

## isort action comments

Ruff respects isort action comments: `# isort: skip_file`, `# isort: on`,
`# isort: off`, `# isort: skip`, `# isort: split` (and `# ruff: isort: ...`
variants). Unlike isort, Ruff does not respect action comments inside docstrings.

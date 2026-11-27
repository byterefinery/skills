# Ruff 0.17.6 — Fixes and error suppression

Contents:
- [Automatic fixes](#automatic-fixes)
- [Fix safety](#fix-safety)
- [Controlling which rules can fix](#controlling-which-rules-can-fix)
- [Suppression overview](#suppression-overview)
- [Line-level — `# noqa`](#line-level--noqa)
- [Logical-line — `# ruff: ignore[CODE]`](#logical-line--ruff-ignorecode)
- [Block-level — `# ruff: disable[CODE]` / `enable[CODE]`](#block-level--ruff-disablecode--enablecode)
- [File-level](#file-level)
- [isort action comments](#isort-action-comments)
- [Detecting and inserting suppressions](#detecting-and-inserting-suppressions)

## Automatic fixes

`ruff check --fix` applies fixes for all enabled rules that support them and
for which fixing is allowed (see below). Many rules are fixable: removing
unused imports, reformatting docstrings, rewriting type annotations to newer
syntax, sorting imports (`I` rules), and more.

- `--fix` — apply fixes (safe only by default)
- `--fix-only` — apply fixes without reporting/exit-non-zero on leftovers
- `--diff` — show a diff of fixes without writing files (implies `--fix-only`)
- `--show-fixes` — enumerate fixed violations
- The `full` output format shows all suggested fixes (including ones that
  need manual review); the `json` format includes fix safety under the
  `applicability` field.

## Fix safety

Fixes are labeled **safe** or **unsafe**:

- Safe fixes preserve runtime behavior and only remove comments when deleting
  entire statements/expressions.
- Unsafe fixes can change runtime behavior, remove comments, or both. Example:
  `RUF015` rewrites `list(...)[0]` to `next(iter(...))` — a possible speedup,
  but on an empty collection the exception changes from `IndexError` to
  `StopIteration`, so the fix is unsafe.

Ruff applies only safe fixes by default. Enable unsafe fixes with
`--unsafe-fixes` (CLI) or `unsafe-fixes = true` (config). A hint to use
`--unsafe-fixes` is shown when unsafe fixes are available but not applied;
silence it by setting `unsafe-fixes = false` or passing `--no-unsafe-fixes`.

Per-rule overrides (prefixes work too):

```toml
[lint]
# Promote F601's unsafe fixes to safe; demote UP034's safe fixes to unsafe
extend-safe-fixes = ["F601"]
extend-unsafe-fixes = ["UP034"]
```

## Controlling which rules can fix

Use `fixable` / `unfixable` (and `extend-fixable`) to limit fixing:

```toml
[lint]
fixable = ["ALL"]       # fix everything eligible
unfixable = ["F401"]    # ...except unused-imports

# or the inverse
fixable = ["F401"]      # only F401 is fixable
```

CLI equivalents: `--fixable`, `--unfixable`, `--extend-fixable`.

## Suppression overview

| Mechanism | Scope | Syntax |
|---|---|---|
| `lint.ignore` | project (config or CLI) | `ignore = ["E501"]` |
| `lint.per-file-ignores` | files matching a pattern | `"**/tests/*" = ["E402"]` |
| `# noqa` | single physical line (or import block / string) | `x = 1  # noqa: F841` |
| `# ruff: ignore[CODE]` | one logical line | comment above the first line |
| `# ruff: disable[CODE]` … `# ruff: enable[CODE]` | code block / scope | paired comments |
| `# ruff: noqa` / `# ruff: noqa: CODE` | entire file | own line, any position (top preferred) |
| `# ruff: file-ignore[CODE]` | entire file, specific rules | own line at module scope, top preferred |

In preview mode, `ruff: ignore`, `ruff: file-ignore`, `ruff: disable`, and
`ruff: enable` accept human-readable rule names (e.g. `unused-import`) instead
of codes.

## Line-level — `# noqa`

Flake8-style inline suppression, case-insensitive `#noqa`:

```python
x = 1  # noqa: F841          # one rule
i = 1  # noqa: E741, F841   # multiple rules
x = 1  # noqa                # blanket: all violations on the line
```

- A blanket `noqa` is `#noqa` followed by end-of-comment, `#`, or whitespace
  plus a non-`:` character; a code-list `noqa` is `#noqa:` followed by codes
  (uppercase letters + digits, separated by commas/whitespace). Missing
  delimiters (e.g. `F401F841`) are interpreted but warn.
- Multi-line strings: put `# noqa: CODE` after the closing triple quote — it
  applies to the entire string.
- Import blocks: put `# noqa: CODE` on the **first line** of the block — it
  applies to all imports in the block.

## Logical-line — `# ruff: ignore[CODE]`

`# ruff: ignore[CODE]` (case-sensitive `#ruff:`) covers one **logical** line
(a multi-line statement or suite header):

```python
# ruff: ignore[ARG001]  # placed above the first line: covers the whole signature
def foo(
    arg1,
    arg2,
):
    pass
```

If the comment is inside a multi-line statement or at the end of a line, it
covers only that single physical line. Ignore comments can be stacked with
other comments and still cover the next logical line. Codes are
comma-separated with an optional trailing comma.

## Block-level — `# ruff: disable[CODE]` / `enable[CODE]`

Suppress violations within a range:

```python
# ruff: disable[E501]
VALUE_1 = "Lorem ipsum dolor sit amet ..."
# ruff: enable[E501]
```

- `disable` and `enable` must have **matching codes in the same order** and
  matching indentation within a logical block.
- With no matching `enable`, Ruff treats it as an **implicit range** ending at
  the logical scope indented less than the `disable` comment. Ruff emits
  `RUF104` for implicit ranges — prefer explicit ranges (or disable `RUF104` /
  add an inline `noqa` to the `disable` line if implicit is intended).
- No blanket suppression: at least one code is required.
- Range suppressions cannot select rules not already enabled by configuration
  or CLI; `enable` only terminates a preceding matching `disable`.

## File-level

Own-line comments, preferably near the top of the file:

```python
# ruff: noqa            # ignore all violations in this file
# ruff: noqa: F841      # ignore specific rules in this file
# ruff: file-ignore[F401, ARG001]  # same idea, bracket syntax, module scope
```

`# flake8: noqa` is respected and treated as equivalent to `# ruff: noqa`.
File-level comments must be on their own line (to disambiguate from inline
`# noqa`).

## isort action comments

Ruff respects isort's action comments for import sorting, plus `# ruff:`-
prefixed variants (`# ruff: isort: skip_file`, etc.):

- `# isort: skip_file`
- `# isort: on` / `# isort: off`
- `# isort: skip`
- `# isort: split`

Unlike isort, Ruff does not respect these action comments inside docstrings.

## Detecting and inserting suppressions

- **Unused suppressions** — the `RUF100` (`unused-noqa`) rule flags noqa/ignore
  comments that no longer suppress anything. Enable with
  `ruff check --extend-select RUF100`; remove them automatically with
  `ruff check --extend-select RUF100 --fix`.
- **Stamping existing violations** — when enabling a new rule on an existing
  codebase, add suppression comments to all current violations so only new
  ones fail:
  - `ruff check --add-noqa` — adds `# noqa` directives (optionally with a
    reason: `--add-noqa="legacy code"`)
  - `ruff check --add-ignore` — adds `# ruff: ignore[...]` comments; in
    preview mode these use human-readable rule names
  - Combine with `--select` to scope to one rule:
    `ruff check --select UP035 --add-noqa .`
- **Ignoring all `# noqa`** — `ruff check --ignore-noqa` lints as if no inline
  noqa comments existed.

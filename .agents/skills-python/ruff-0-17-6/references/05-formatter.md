# Ruff 0.17.6 — Formatter

Contents:
- [Basics](#basics)
- [Black compatibility and known deviations](#black-compatibility-and-known-deviations)
- [Configuration](#configuration)
- [F-string formatting](#f-string-formatting)
- [Docstring code formatting](#docstring-code-formatting)
- [Markdown formatting](#markdown-formatting)
- [Format suppression comments](#format-suppression-comments)
- [Conflicting lint rules and settings](#conflicting-lint-rules-and-settings)
- [Import sorting](#import-sorting)

## Basics

```bash
ruff format                    # format all files in the current directory
ruff format path/to/code/      # format a directory (recursive)
ruff format path/to/file.py    # format a single file
ruff format --check            # CI mode: exit 1 if any file would change, write nothing
ruff format --diff             # print diffs instead of writing
ruff format --exit-non-zero-on-format  # exit 1 if anything was formatted
```

The formatter is a drop-in replacement for Black: it adheres to Black's stable
code style (88-char default line length, magic trailing commas, double quotes,
space indentation, auto line endings), with an excessive focus on performance.
Over extensive Black-formatted projects (Django, Zulip) more than 99.9% of
lines are formatted identically. Unlike Black, it also supports configuring
quote style, indent style, line endings, and docstring code formatting — but
exposes no other style options.

The `--range <start_line>:<start_column>-<end_line>:<end_column>` flag formats
only the given range (boundaries may be extended to fully enclose a logical
line) — primarily an editor option.

## Black compatibility and known deviations

Ruff targets Black compatibility so adoption is minimally disruptive, but it
is not intended to be used interchangeably with Black forever: the formatter
differs from Black in a few conscious ways (the "Known deviations" page of the
Ruff docs enumerates them). Deviations are limited to cases where Ruff's
behavior was deemed more consistent or significantly simpler to support with
negligible end-user impact. Unintentional deviations are tracked in Ruff's
issue tracker under the `formatter` label.

Preview formatting style: formatter changes land under
`[format] preview = true` (or `ruff format --preview`) and are promoted to
stable through minor releases.

## Configuration

Formatter settings live under `[format]` / `[tool.ruff.format]`:

```toml
[format]
quote-style = "single"          # "double" (default, like Black) or "single"
indent-style = "space"          # "space" (default) or "tab"
line-length = 100               # via top-level line-length, or --line-length
skip-magic-trailing-comma = false
line-ending = "auto"            # auto-detect; like Black
docstring-code-format = false   # opt in to format code examples in docstrings
docstring-code-line-length = "dynamic"
preview = false                 # unstable formatting style
```

There is a dedicated `--line-length` CLI flag for `ruff format`; other options
need config or `--config "format.quote-style = 'single'"`.

## F-string formatting

_Stabilized in Ruff 0.9.0._ Unlike Black, Ruff formats the expression parts
of f-strings (inside `{...}`) — a known deviation from Black.

Quotes: Ruff uses the configured quote style for f-string expressions unless
doing so would produce invalid syntax for the target Python version or require
more backslash escapes. It preserves the original quote style when, e.g., a
self-documenting f-string (`f'{x=}'`) contains a literal with the configured
quote style on Python < 3.12, or a format specifier contains the configured
quote style (any version). Nested f-strings alternate quote styles by default
(outermost uses the configured style); with target 3.12+ and
`nested-string-quote-style = "preferred"`, the configured style is reused.

Line breaks: expression parts only split across multiple lines if there was
already a line break within any expression part (PEP 701, Python 3.12+); a
long single-line expression stays on one line even past the line length.

## Docstring code formatting

Opt-in (`docstring-code-format = true`): the formatter reformats Python code
examples in docstrings. Recognized formats:

- doctest blocks
- CommonMark fenced code blocks with info strings `python`, `py`, `python3`,
  `py3` (no info string → assumed Python)
- reStructuredText literal blocks
- reStructuredText `code-block` / `sourcecode` directives (same language names)

Blocks that don't parse as valid Python, or that would become invalid after
formatting, are skipped. `docstring-code-line-length` defaults to `dynamic`
(the surrounding code's line length; safe inside indented docstrings) or a
fixed integer.

## Markdown formatting

Ruff formats Python fenced code blocks in Markdown files: info strings
`python`, `py`, `python3`, `py3`, `pyi`, `pycon` (`pyi` blocks formatted like
stub files, `pycon` like REPL sessions), plus Quarto-style `{python}` blocks.
Non-Python or unparseable blocks are skipped.

- Suppression: `<!-- fmt:off -->` … `<!-- fmt:on -->` HTML comments around
  code blocks (an unmatched `off` covers the rest of the document); the
  blacken-docs variants `<!-- blacken-docs:off/on -->` are recognized too.
- Non-`.md` extensions: map them with `extension = { mdx = "markdown", qmd = "markdown" }`.
- Disable Markdown formatting: `extend-exclude = ["*.md"]`.
- In `ruff-pre-commit`, add `markdown` to `types_or` to include Markdown
  files.

## Format suppression comments

Like Black, Ruff supports:

- `# fmt: off` / `# fmt: on` — **statement-level** only. Inside an expression
  (e.g. within a list literal) they have no effect; move the comment before
  the whole statement. YAPF's `# yapf: disable` / `# yapf: enable` are
  treated equivalently.
- `# fmt: skip` — suppresses formatting for a case header, decorator, function
  definition, class definition, or the preceding statements on the same
  logical line (e.g. `a = [1,2,3,4,5]  # fmt: skip`). At the end of an
  expression (inside a call/list) it has no effect.

## Conflicting lint rules and settings

Using the formatter alongside the linter: the goal is that formatting never
introduces new lint errors, provided conflicting rules are off. Avoid/ignore
these lint rules when using `ruff format`:

- `W191` tab-indentation
- `E111` indentation-with-invalid-multiple
- `E114` indentation-with-invalid-multiple-comment
- `E117` over-indented
- `D203` incorrect-blank-line-before-class
- `D206` docstring-tab-indentation
- `D300` triple-single-quotes
- `Q000`–`Q004` (flake8-quotes: inline string, multiline string, docstring,
  avoidable/unnecessary escaped quote)
- `COM812` missing-trailing-comma, `COM819` prohibited-trailing-comma
- `ISC002` multi-line-implicit-string-concatenation — unless used with
  `ISC001` and `flake8-implicit-str-concat.allow-multiline = false`

`E501` (line-too-long) can coexist, but wrapping is best-effort — formatted
code may exceed the line length.

Avoid these isort settings at non-default values (incompatible with the
formatter's import handling): `force-single-line`, `force-wrap-aliases`,
`lines-after-imports`, `lines-between-types`, `split-on-trailing-comma`.

When any of these is enabled, `ruff format` emits a warning; a warning-free
`ruff format` run means your config is compatible.

## Import sorting

The formatter does **not** sort imports. To sort and format:

```bash
ruff check --select I --fix   # isort rules
ruff format
```

A unified lint+format command is planned but not available in 0.17.6.

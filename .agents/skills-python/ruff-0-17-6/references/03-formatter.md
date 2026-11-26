# Ruff — Formatter

The Ruff formatter is a drop-in replacement for Black, available via `ruff format`.
It targets Black's stable style: > 99.9% of lines are formatted identically on
extensive Black-formatted projects (Django, Zulip), and it intentionally emits
near-identical output on existing Black-formatted code. It is **not** intended to
be used interchangeably with Black on an ongoing basis — a few conscious
deviations exist (see `docs/formatter/black.md` in the ruff repo: "Known
deviations from Black").

## Entry points and exit codes

```bash
ruff format                 # format in place
ruff format --check path/   # no writes; exit 1 if any file would change
ruff format --diff          # no writes; print the diff
```

`ruff format` exit codes: `0` success (whether or not files were formatted);
`1` success with at least one file formatted **and** `--exit-non-zero-on-format`
passed; `2` invalid configuration, invalid CLI options, or internal error.
`ruff format --check`: `0` nothing would change, `1` one or more files would
change, `2` abnormal termination.

## Configuration

Deliberately limited (like Black), but with a few options Black lacks:

```toml
[tool.ruff]
line-length = 100              # shared with the linter

[tool.ruff.format]
quote-style = "double"         # "double" (default) or "single"
indent-style = "space"         # "space" (default) or "tab"
line-ending = "auto"           # auto, lf, crlf, crcf
skip-magic-trailing-comma = false
docstring-code-format = false  # opt-in: format Python in docstrings
docstring-code-line-length = "dynamic"
```

`--line-length` and `--preview` are the main dedicated CLI flags; `--extension`
maps custom extensions to languages (`--extension ipy:ipynb`).

## Docstring code formatting

With `docstring-code-format = true`, Python code examples inside docstrings are
formatted. Recognized formats: doctest, CommonMark fenced blocks with info string
`python`/`py`/`python3`/`py3` (fences *without* an info string count too),
reStructuredText literal blocks, and `code-block`/`sourcecode` directives.
Snippets that don't parse as valid Python — or would reformat into invalid Python
— are skipped. `docstring-code-line-length` defaults to `"dynamic"` (respect the
surrounding code's `line-length`); a fixed number can also be given.

## Markdown formatting

`*.md` is in the default discovery set, so `ruff format` formats Python code
blocks in Markdown by default:

- Fenced blocks with info string `python`, `py`, `python3`, `py3`, `pyi`, or
  `pycon` (`pyi` formatted like stub files, `pycon` like REPL sessions); Quarto
  `{python}` blocks supported.
- Blocks wrapped in `<!-- fmt:off -->` ... `<!-- fmt:on -->` (or
  `<!-- blacken-docs:off -->` / `:on`) are skipped; an unmatched `off` covers the
  rest of the document.
- Custom extensions map via `extension = { mdx = "markdown", qmd = "markdown" }`.
- To **disable** Markdown formatting entirely:
  `[tool.ruff] extend-exclude = ["*.md"]`.
- Via `ruff-pre-commit`, Markdown must be opted into explicitly:
  `types_or: [python, pyi, jupyter, markdown]` on the hook.

## Format suppression

`# fmt: on`, `# fmt: off`, `# fmt: skip` (Black-compatible; YAPF's
`# yapf: disable` / `# yapf: enable` are also recognized).

- `on`/`off` are enforced at **statement level** — comments between list entries
  have no effect; put them around the whole statement.
- `# fmt: skip` suppresses a case header, decorator, `def`/`class` line, or the
  preceding statements on the same logical line — again, statement-scoped, not
  expression-scoped.

## F-string formatting

Unlike Black, Ruff formats the expression parts of f-strings (stabilized in
0.9.0). Quote rules: uses the configured quote style unless doing so would be
invalid for the target Python version or require more backslash escapes; nested
f-strings alternate quote styles below Python 3.12 (on 3.12+ with
`nested-string-quote-style = "preferred"` the configured style is reused).
Line breaks: Ruff only splits an f-string expression across lines if the original
expression already contained a line break.

## Fluent layout for method chains (preview)

Under `format.preview = true`, long method chains break *before* the first
attribute instead of after the previous call:

```python
x = (
    df
    .filter(cond)
    .agg(func)
    .merge(other)
)
```

Stable style (and Black) break after the call.

## Import sorting

The formatter does **not** sort imports. Run:

```bash
ruff check --select I --fix
ruff format
```

A unified lint-and-format command is planned (ruff issue #8232).

## Conflicting lint rules

The formatter and these lint rules can conflict — avoid them when using
`ruff format` (none are in the default rule set; `ruff format` prints a warning
if an incompatible rule or setting is enabled):

- `W191`, `E111`, `E114`, `E117` (indentation)
- `D203`, `D206`, `D300` (docstring style)
- `Q000`–`Q004` (quotes)
- `COM812`, `COM819` (trailing commas)
- `ISC002` (unless used with `ISC001` and
  `flake8-implicit-str-concat.allow-multiline = false`)

`E501` *can* be used alongside the formatter, but the formatter only makes a
best-effort attempt to wrap at `line-length`, so formatted code may still exceed
it.

Incompatible isort settings (formatter conflicts on non-default values):
`force-single-line`, `force-wrap-aliases`, `lines-after-imports`,
`lines-between-types`, `split-on-trailing-comma`.

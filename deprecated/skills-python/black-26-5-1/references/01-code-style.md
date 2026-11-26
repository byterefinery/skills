# Black Code Style — Detailed Reference

## Line wrapping

Black ignores previous formatting and applies uniform whitespace. For expressions that
exceed line length, it decomposes using matching brackets, putting each bracket pair's
contents on separate indented lines.

```python
# in:
ImportantClass.important_method(exc, limit, lookup_lines, capture_locals, extra_argument)

# out:
ImportantClass.important_method(
    exc, limit, lookup_lines, capture_locals, extra_argument
)
```

Comma-separated contents (args, dict items, list elements) are split one-per-line when
they can't fit. Closing brackets are always dedented, and trailing commas are always
added — this produces minimal diffs when elements are added or removed.

## Line length

Default is 88 characters (10% over 80). Black tries to respect `--line-length` but may
exceed it in rare cases where no valid formatting fits within the limit. Lines over 100
characters are harder to review side-by-side and harder for people with sight
disabilities.

## Empty lines

- Single empty lines inside functions are preserved
- Single and double empty lines at module level are preserved (as left by the author)
- Empty lines inside parenthesized expressions are removed
- One blank line before/after inner functions, two before/after module-level functions
  and classes
- No blank lines between class/function definitions and preceding standalone comments

## Comments

- Two spaces between code and inline comment; one space after `#`
- Shebangs (`#!`), doc comments (`#:`), section comments (long hash runs), and Spyder
  cells are preserved with their specific spacing
- Non-breaking spaces after `#` are preserved
- Comments may move due to formatting changes

## Trailing commas

Always added to split comma-separated expressions. The **magic trailing comma** is a
pragmatic exception: a pre-existing trailing comma tells Black to always explode the
bracket pair into one item per line, even if it would fit on one line. Remove the
trailing comma to let Black collapse it.

## Strings

- Double quotes (`"`) preferred over single quotes (`'`)
- String prefixes lowercased (except `R"..."` which is preserved for regex highlighting)
- Unicode `u` prefix removed (meaningless in Python 3)
- Multiple prefixes: `r` first (`rf"..."` not `fr"..."`)
- Escape sequences normalized to lowercase (`\uabcd` not `\uABCD`), except `\N{...}`
- Docstrings: indentation corrected, trailing whitespace removed, tabs converted to
  spaces in leading whitespace

## Numeric literals

- Syntactic parts lowercase (`0xAB` not `0XAB`)
- Exponent notation lowercase (`1e10` not `1E10`)

## Binary operators

Line breaks occur **before** binary operators (PEP 8 compliant since April 2016).
Unary operators (`+`, `-`, `~`) and simple power operators have no surrounding spaces:

```python
a = x**y          # simple operands — no spaces
f = 2 ** get_exp()  # complex operands — spaces
```

## Slices

`:` treated as lowest-priority binary operator. Simple expressions have no spaces
(`ham[lower:upper]`); complex expressions have spaces (`ham[lower : upper + offset]`).

## Parentheses

Optional parentheses are removed when the statement fits on one line or the inner
expression has no delimiters to split on. Added when needed for multi-line formatting.
Does not add/remove nested parentheses used for logical clarity.

## Call chains

Dots following calls or indexing are treated as low-priority delimiters:

```python
result = (
    session.query(models.Customer.id)
    .filter(
        models.Customer.account_id == account_id,
    )
    .order_by(models.Customer.id.asc())
    .all()
)
```

## Typing stub files (`.pyi`)

- `...` on same line as signature preferred
- No vertical whitespace between consecutive module-level items or class members
- Single blank line between top-level class definitions

## Line endings

Normalized based on the first line ending found in the file (`\n` or `\r\n`).

## Form feed characters

Retained on otherwise empty lines at module level. Only one form feed per group of
consecutive empty lines; placed on the second line when two empty lines exist.

## AST safety check

With `--safe` (default), Black verifies the AST before and after formatting is
semantically equivalent. Three limited exceptions:

1. Docstring whitespace cleanup (all real-world docstring usage sanitizes this anyway)
2. Optional parentheses on `del` statements (semantically equivalent)
3. Comment movement (including type comments in Python 3.8+)

Use `--fast` to skip this check for performance on large codebases.

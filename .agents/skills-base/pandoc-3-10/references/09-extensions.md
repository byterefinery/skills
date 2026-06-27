# Extensions Reference

Extensions fine-tune reader and writer behavior. Enable with `+EXTENSION`, disable with `-EXTENSION` appended to the format name.

## Syntax

```bash
# Enable footnotes in strict markdown
pandoc -f markdown_strict+footnotes input.md

# Disable footnotes and pipe tables
pandoc -f markdown-footnotes-pipe_tables input.md

# Multiple extensions
pandoc -f markdown+footnotes+autolink_bare_uris+yaml_metadata input.md

# Mix enable and disable
pandoc -f markdown-footnotes+raw_html input.md
```

## Listing Extensions

```bash
# See all extensions for a format
pandoc --list-extensions=markdown
pandoc --list-extensions=latex
pandoc --list-extensions=gfm
pandoc --list-extensions=html
```

Output shows each extension, whether it is enabled by default (`+`), and which readers/writers support it.

## Cross-Format Extensions

### `smart` — Typography

Interprets straight quotes as curly quotes, `---` as em-dashes, `--` as en-dashes, `...` as ellipses. Inserts nonbreaking spaces after abbreviations.

| | Input | Output | Default on |
|---|---|---|---|
| Formats | markdown, latex, context, mediawiki, org, rst, twiki, html | markdown, latex, context, org, rst | markdown, latex, context |

### `auto_identifiers` — Heading Identifiers

Auto-generates unique identifiers from heading text for internal links.

| | Input | Output | Default on |
|---|---|---|---|
| Formats | markdown, latex, rst, mediawiki, textile, man | markdown, muse | markdown, muse, man |

### `ascii_identifiers` — ASCII-Only Identifiers

Like `auto_identifiers` but produces only ASCII characters (transliterates Unicode).

### `gfm_auto_identifiers` — GFM-Style Identifiers

GitHub-compatible identifier generation (lowercase, spaces to hyphens, strips punctuation).

### `empty_paragraphs` — Empty Paragraphs

Preserves empty paragraphs. By default, empty paragraphs are removed.

### `native_numbering` — Native Numbered Headings

Uses native numbered heading syntax of the target format instead of generic numbering.

### `xrefs_name` / `xrefs_number` — Cross-References

Cross-references by name or number.

## Markdown-Specific Extensions

These extensions are primarily used with pandoc's Markdown reader and writer. See the Pandoc User's Guide "Pandoc's Markdown" section for full syntax details.

### Math Input

| Extension | Description |
|---|---|
| `tex_math_dollars` | `$...$` inline, `$$...$$` display (default on) |
| `tex_math_single_backslash` | `\(...\)` and `\[...,]` delimiters |
| `tex_math_double_backslash` | `\\[...\\]` delimiters |

### Raw HTML/TeX

| Extension | Description |
|---|---|
| `raw_html` | Allow raw HTML in markdown (default on) |
| `raw_tex` | Allow raw LaTeX/Tex fragments (default on) |

### Code Blocks

| Extension | Description |
|---|---|
| `backtick_code_blocks` | Fenced code blocks with ```` ``` ```` (default on) |
| `fenced_code_attributes` | Attributes on fenced code blocks `{.python #id}` (default on) |
| `inline_code_attributes` | Attributes on inline code `` `code`{.keyword} `` |

### Tables

| Extension | Description |
|---|---|
| `simple_tables` | Simple aligned tables with dashes (default on) |
| `multiline_tables` | Tables spanning multiple lines (default on) |
| `grid_tables` | ASCII grid tables with `+---+` borders (default on) |
| `pipe_tables` | PHP Markdown Extra pipe tables `| col |` (default on) |
| `table_captions` | Table captions with `Table:` prefix (default on) |
| `table_attributes` | Attributes on table captions |

### Headings

| Extension | Description |
|---|---|
| `blank_before_header` | Require blank line before headings (default on) |
| `space_in_atx_header` | Require space after `#` in ATX headings (default on) |
| `header_attributes` | Attributes `{#id .class key=val}` on headings (default on) |
| `explicit_math_ids` | Explicit identifiers for math blocks |

### Lists

| Extension | Description |
|---|---|
| `fancy_lists` | Advanced list attributes and styles (default on) |
| `definition_lists` | Definition lists with `term: definition` (default on) |

### Inline Formatting

| Extension | Description |
|---|---|
| `emphasis` | `*italic*` and `_italic_` (default on) |
| `strikeout` | `~~strikethrough~~` (default on) |
| `superscript` | `^superscript^` (default on) |
| `subscript` | `~subscript~` |
| `auto_identifiers` | Auto-generated heading IDs (default on) |
| `footnotes` | Reference-style footnotes `[^1]` (default on) |
| `inline_notes` | Inline footnotes `^[text]` (default on) |
| `citations` | Citation syntax `@key` (default on) |
| `markdown_in_html_blocks` | Parse markdown inside HTML blocks |
| `escaped_line_breaks` | Backslash + newline = hard break (default on) |

### Metadata

| Extension | Description |
|---|---|
| `yaml_metadata_block` | YAML front matter between `---` (default on) |
| `multiline_metadata_keys` | Multiline values in metadata |

### Links and Images

| Extension | Description |
|---|---|
| `autolink_bare_uris` | Auto-link bare URLs |
| `implicit_header_references` | Auto-links to headings (default on) |
| `raw_attribute` | Raw format-specific content with attributes |

### Other

| Extension | Description |
|---|---|
| `abbreviations` | Abbreviation hints `*[HTML]: HyperText Markup Language` |
| `angle_brackets_escapes` | Escape `<` and `>` with backslash |
| `hard_line_breaks` | Single newlines become hard breaks |
| `mark` | `==highlighted==` text |
| `underline` | Underlined text (format-dependent) |
| `attributes` | General attributes support |
| `raw_markdown` | Allow raw markdown in certain contexts |

## Extension Examples

```bash
# Strict markdown with just footnotes added
pandoc -f markdown_strict+footnotes input.md

# Pandoc markdown without raw HTML
pandoc -f markdown-raw_html input.md

# GFM with pandoc extensions layered on
pandoc -f gfm+footnotes+citations+math input.md

# LaTeX input with smart typography
pandoc -f latex+smart -t html paper.tex

# Output markdown without raw HTML
pandoc -f latex -t markdown-raw_html paper.tex -o paper.md

# Disable emphasis underscores (only asterisks)
pandoc -f markdown-emphasis input.md
```

## Extension Defaults by Format

| Format | Key defaults |
|---|---|
| `markdown` | Most extensions on; full feature set |
| `markdown_strict` | Only basic Markdown.pl features |
| `commonmark` | CommonMark spec only; no tables, footnotes, math |
| `gfm` | CommonMark + strikethrough, tables, task lists, autolinks |
| `commonmark_x` | CommonMark + many pandoc extensions |
| `latex` | `smart` on; `auto_identifiers` available |
| `html` | `raw_html` on |

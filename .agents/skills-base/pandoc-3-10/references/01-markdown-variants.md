# Markdown Variants Reference

Pandoc supports multiple Markdown dialects as both input and output formats. Each variant has different extension defaults and syntax support.

## Supported Variants

| Format name | Description | Input | Output |
|---|---|---|---|
| `markdown` | Pandoc's extended Markdown (default) | Yes | Yes |
| `markdown_strict` | Original Markdown.pl syntax | Yes | No |
| `markdown_phpextra` | PHP Markdown Extra | Yes | Yes |
| `markdown_mmd` | MultiMarkdown | Yes | Yes |
| `markdown_github` | Deprecated GitHub-Flavored Markdown | Yes | No |
| `commonmark` | CommonMark specification | Yes | Yes |
| `gfm` | GitHub-Flavored Markdown (current) | Yes | Yes |
| `commonmark_x` | CommonMark with pandoc extensions | Yes | Yes |

## Pandoc's Markdown (`markdown`)

The default and most feature-rich variant. Extends original Markdown with:

- **Tables**: simple, multiline, grid, and pipe tables
- **Footnotes**: reference-style `[^1]` and inline `^[...]`
- **Math**: `$inline$` and `$$display$$` TeX math
- **Citations**: `@key` syntax with CSL bibliography support
- **Definition lists**: term followed by `:` and definition
- **Metadata blocks**: YAML, TOML, or JSON between `---` delimiters
- **Header attributes**: `{#id .class key="value"}`
- **Smart typography**: curly quotes, em-dashes, ellipses (default on)
- **Strikethrough**: `~~text~~`
- **Superscript/subscript**: `^text^` and ~~~text~~~
- **Pipe tables**: `| col1 | col2 |` syntax

```bash
# Convert from pandoc markdown to other formats
pandoc -f markdown -t html notes.md
pandoc -f markdown -t latex notes.md
pandoc -f markdown -t docx notes.md
```

## GitHub-Flavored Markdown (`gfm`)

Based on CommonMark with GitHub-specific extensions:

- **Strikethrough**: `~~text~~`
- **Tables**: pipe-table syntax only
- **Task lists**: `- [ ]` and `- [x]`
- **Autolinks**: URLs auto-linked
- **Footnotes**: supported (GitHub feature)
- **Description**: strikethrough, tables, task lists

```bash
# Pandoc Markdown → GFM
pandoc -f markdown -t gfm README.md -o README-gfm.md

# GFM → HTML
pandoc -f gfm -t html README-gfm.md

# GFM → LaTeX (tables preserved)
pandoc -f gfm -t latex README-gfm.md -o README.tex
```

## CommonMark (`commonmark`)

Strict adherence to the CommonMark specification. Minimal extensions:

- No tables, footnotes, math, or citations by default
- Clean, predictable parsing
- Good for interoperability between tools

```bash
# Convert to strict CommonMark
pandoc -f markdown -t commonmark draft.md -o draft.cm.md

# CommonMark → HTML
pandoc -f commonmark -t html draft.cm.md
```

## CommonMark with Extensions (`commonmark_x`)

CommonMark base with many pandoc extensions layered on:

- Tables, footnotes, math, citations, definition lists
- Smart typography
- Header attributes
- Useful when you want CommonMark parsing rules but with extended syntax

```bash
# Parse extended content as CommonMark + extensions
pandoc -f commonmark_x -t html extended.md

# Convert pandoc markdown to commonmark_x
pandoc -f markdown -t commonmark_x notes.md
```

## PHP Markdown Extra (`markdown_phpextra`)

Adds to basic Markdown:

- **Tables**: pipe-table syntax (same as GFM)
- **Footnotes**: reference-style
- **Definition lists**
- **Header attributes**
- **Abbreviations**: `*HTML*: HyperText Markup Language`

```bash
# PHP Extra → Pandoc Markdown
pandoc -f markdown_phpextra -t markdown blog.md

# Pandoc Markdown → PHP Extra (bi-directional)
pandoc -f markdown -t markdown_phpextra blog.md -o blog.phpextra.md

# PHP Extra → HTML
pandoc -f markdown_phpextra -t html blog.md
```

## MultiMarkdown (`markdown_mmd`)

Fletcher Penney's extension of Markdown:

- **Bibliography and citation support**
- **Document metadata** (title, author, etc.)
- **Image scaling** via attributes
- **Math** (LaTeX delimiters)
- **Tables**

```bash
# MultiMarkdown → Pandoc Markdown
pandoc -f markdown_mmd -t markdown notes.md

# Pandoc Markdown → MultiMarkdown
pandoc -f markdown -t markdown_mmd notes.md -o notes.mmd.md
```

## Strict Markdown (`markdown_strict`)

Original Markdown.pl syntax. No extensions:

- No tables, footnotes, math, or citations
- Setext and ATX headings only
- Basic inline formatting (bold, italic, links, images)
- Useful for maximum compatibility with basic Markdown readers

```bash
# Strip pandoc extensions → strict Markdown
pandoc -f markdown -t markdown_strict extended.md -o strict.md

# Note: markdown_strict is input-only; use commonmark for output
pandoc -f markdown_strict -t html simple.md
```

## Deprecated `markdown_github`

Old GitHub-Flavored Markdown reader. Less accurate than `gfm`. Use only if you need extensions not supported by the current `gfm` reader.

## Listing Extensions per Format

See which extensions each format supports and which are enabled by default:

```bash
pandoc --list-extensions=markdown
pandoc --list-extensions=gfm
pandoc --list-extensions=commonmark
pandoc --list-extensions=latex
```

## Converting Between Variants: Strategy

1. **Rich → Simple**: `pandoc -f markdown -t commonmark` strips pandoc-specific features
2. **Simple → Rich**: `pandoc -f commonmark -t markdown` adds pandoc extensions capability
3. **Flavor swap**: `pandoc -f gfm -t markdown_phpextra` preserves shared features (tables, footnotes)
4. **Always inspect output** when converting between variants, as feature parity is not guaranteed

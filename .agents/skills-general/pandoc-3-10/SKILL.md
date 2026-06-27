---
name: pandoc-3-10
description: Convert documents between formats using Pandoc 3.10. Use when the user mentions pandoc, document conversion, format transformation, or needs to convert between Markdown, HTML, LaTeX, PDF, Word (docx), OpenDocument (odt), PowerPoint (pptx), Excel (xlsx), CSV, TSV, EPUB, reStructuredText, Org mode, AsciiDoc, RTF, Textile, CommonMark, GFM, or any markup/format conversion task. Also use when user asks about pandoc filters, templates, defaults files, citeproc, or Lua filters.
metadata:
  tags:
    - document-conversion
    - markdown
    - latex
    - pdf
    - office-documents
---

# pandoc 3.10

## Overview

Pandoc is a universal document converter that transforms content between over 50 markup and word processing formats. It parses input into an abstract syntax tree (AST), then renders it to the target format. Conversions from pandoc's Markdown to any format are high-fidelity; conversions from more expressive formats (LaTeX, docx) to simpler ones may be lossy.

Core workflow: `pandoc -f INPUT_FORMAT -t OUTPUT_FORMAT [options] -o output input`

Formats auto-detect from file extensions when `-f`/`-t` are omitted. List available formats with `pandoc --list-input-formats` and `pandoc --list-output-formats`.

## Usage

### Basic Conversions

```bash
# Markdown to HTML (auto-detected from extensions)
pandoc -o output.html input.md

# Explicit format specification
pandoc -f markdown -t latex hello.txt

# Multiple input files concatenated
pandoc -o combined.pdf chapter1.md chapter2.md chapter3.md

# Pipe through stdin/stdout
cat notes.md | pandoc -t html | less
```

### PDF Output

Pandoc produces PDFs via intermediate formats. Specify `.pdf` output and optionally choose an engine:

```bash
# Default: Markdown → LaTeX → PDF (pdflatex)
pandoc -o report.pdf report.md

# Use xelatex for full Unicode/font support
pandoc -o report.pdf report.md --pdf-engine=xelatex

# HTML → PDF via weasyprint (no LaTeX needed)
pandoc -t html -o report.pdf report.md --pdf-engine=weasyprint

# Debug: inspect the intermediate LaTeX
pandoc -s -o report.tex report.md
pdflatex report.tex
```

**PDF engines**: `pdflatex`, `xelatex`, `lualatex`, `latexmk`, `tectonic`, `wkhtmltopdf`, `weasyprint`, `pagedjs-cli`, `prince`, `context`, `groff`, `pdfroff`, `typst`.

### Word Documents (docx) — Bi-directional

```bash
# Markdown → Word docx
pandoc -f markdown -t docx document.md -o document.docx

# Word docx → Markdown (preserves headings, lists, tables, bold/italic, code)
pandoc -f docx -t markdown document.docx -o document.md

# Word docx → HTML (standalone with CSS)
pandoc -s -f docx -t html document.docx -o document.html

# Word docx → plain text
pandoc -f docx -t plain document.docx

# Custom styling via reference docx
pandoc -o styled.docx document.md --reference-doc=template.docx
```

Round-trip `markdown → docx → markdown` preserves: bold, italic, inline code, lists (ordered/unordered), tables, block quotes, links, math (`$...$`, `$$...$$`). YAML front matter becomes heading + paragraph text.

### Excel Spreadsheets (xlsx) — Input Only

**xlsx is input-only** (no output format). Each sheet becomes a level-2 heading + pipe table. First row = header, remaining rows = body. Bold/italic cell formatting preserved.

```bash
# All sheets → Markdown (each sheet = ## heading + table)
pandoc -f xlsx -t markdown data.xlsx -o data.md

# All sheets → HTML (each sheet = <h2> + <table>)
pandoc -f xlsx -t html data.xlsx -o data.html

# All sheets → LaTeX (each sheet = \subsection + longtable)
pandoc -f xlsx -t latex data.xlsx -o data.tex

# All sheets → plain text
pandoc -f xlsx -t plain data.xlsx

# JSON AST (for programmatic sheet access)
pandoc -f xlsx -t json data.xlsx | python3 -m json.tool
```

**Selecting specific sheets**: Use a Lua filter since pandoc has no built-in sheet selection:

```bash
# Keep only non-empty sheets (those with tables)
pandoc -f xlsx --lua-filter=filter-empty-sheets.lua data.xlsx -t markdown

# Select a named sheet via metadata: -M sheet-name="Sheet1"
pandoc -f xlsx --lua-filter=select-sheet.lua -M sheet-name="Sales" data.xlsx -t markdown
```

### CSV/TSV — Input Only

CSV and TSV are input-only formats. Each file produces a single pipe table.

```bash
# CSV → Markdown (simple table)
pandoc -f csv -t markdown data.csv

# TSV → HTML
pandoc -f tsv -t html data.tsv
```

### PowerPoint (pptx) — Bi-directional

```bash
# Markdown → PowerPoint
pandoc -f markdown -t pptx slides.md -o presentation.pptx

# PowerPoint → Markdown (each slide = ## heading with {#slide-N})
pandoc -f pptx -t markdown presentation.pptx -o slides.md

# PowerPoint → HTML
pandoc -f pptx -t html presentation.pptx -o slides.html

# PowerPoint → LaTeX
pandoc -f pptx -t latex presentation.pptx -o slides.tex

# PowerPoint → plain text
pandoc -f pptx -t plain presentation.pptx
```

Round-trip `markdown → pptx → markdown`: tables preserved, but lists lose bullet markers (become paragraphs), YAML front matter becomes heading + paragraph.

### OpenDocument/LibreOffice (odt)

```bash
# Markdown to ODT
pandoc -o document.odt document.md

# ODT to Markdown (bi-directional)
pandoc -f odt -t markdown document.odt -o document.md

# Use custom reference ODT for styling
pandoc -o styled.odt document.md --reference-doc=template.odt

# ODT to HTML
pandoc -f odt -t html document.odt -o document.html
```

Extract default reference: `pandoc -o custom-reference.odt --print-default-data-file reference.odt`.

### Markdown Flavor Conversions

Pandoc supports multiple Markdown variants. Convert between them explicitly:

```bash
# Pandoc Markdown → GitHub-Flavored Markdown (GFM)
pandoc -f markdown -t gfm README.md -o README.gfm.md

# GFM → CommonMark
pandoc -f gfm -t commonmark README.gfm.md -o README.cm.md

# CommonMark with extensions → Pandoc Markdown
pandoc -f commonmark_x -t markdown notes.md

# PHP Markdown Extra → Pandoc Markdown (bi-directional)
pandoc -f markdown_phpextra -t markdown blog.md
pandoc -f markdown -t markdown_phpextra blog.md -o blog.phpextra.md

# MultiMarkdown → Pandoc Markdown
pandoc -f markdown_mmd -t markdown notes.md

# Strict Markdown.pl → Pandoc Markdown
pandoc -f markdown_strict -t markdown original.md
```

### LaTeX Conversions

```bash
# LaTeX to HTML (bi-directional)
pandoc -f latex -t html paper.tex -o paper.html

# HTML to LaTeX (bi-directional)
pandoc -f html -t latex paper.html -o paper.tex

# Markdown to LaTeX (standalone, with document class)
pandoc -s -t latex notes.md -o notes.tex

# LaTeX to Markdown (extract text and structure)
pandoc -f latex -t markdown paper.tex -o paper.md

# LaTeX to PDF (via pandoc's built-in PDF pipeline)
pandoc -f latex -o paper.pdf paper.tex

# Beamer slides from Markdown
pandoc -t beamer slides.md -o slides.tex
```

### Format Inspection (AST Debugging)

Inspect the intermediate representation to understand how pandoc parses a document:

```bash
# JSON AST (human-readable)
pandoc -t json input.md | python3 -m json.tool

# xlsx → JSON AST (for programmatic sheet access)
pandoc -f xlsx -t json data.xlsx | python3 -m json.tool

# Native Haskell AST (compact)
pandoc -t native input.md

# XML AST
pandoc -t xml input.md
```

## Gotchas

- **xlsx, csv, tsv are input-only** — you can read them but cannot write to these formats. Use markdown tables or HTML tables as intermediate output instead.
- **xlsx converts all sheets** — no built-in option to select individual sheets. Each sheet becomes `## <sheet-name>` + table. Use a Lua filter (`--lua-filter`) to extract specific sheets by name or filter empty ones.
- **xlsx sheet path bug** — the xlsx reader may fail with `Entry not found: xl//xl/worksheets/sheet1.xml` on files created by some tools (e.g., openpyxl) that use absolute paths in workbook relationships. Files from Excel/LibreOffice work correctly.
- **pptx round-trip loses list markers** — bullet points become plain paragraphs when converting `pptx → markdown`. Tables and headings are preserved.
- **docx YAML front matter is lost** — metadata becomes heading + paragraph text on `docx → markdown` round-trip.
- **Binary formats (docx, odt, epub, pdf) cannot output to stdout** unless forced with `-o -`. They always write to a file.
- **PDF requires an external engine**: `pdflatex` needs TeX Live installed. For no-LaTeX PDF, use `--pdf-engine=weasyprint` (requires weasyprint) or `--pdf-engine=typst`.
- **Conversions are not perfectly lossless**. Complex LaTeX tables, advanced docx formatting, and custom styles may degrade through the AST. Pandoc preserves structure, not presentation details like margin sizes.
- **File extension auto-detection can mislead**. Always specify `-f` and `-t` explicitly when the extension doesn't match the actual format (e.g., `.txt` containing LaTeX).
- **Math rendering differs by output format**. LaTeX math passes through verbatim to LaTeX output, renders as OMML in docx, MathML in ODT, and requires `--mathjax`, `--katex`, or `--webtex` for HTML.
- **Reference docs must be pandoc-compatible**. Custom `reference.docx`/`reference.odt` should start from pandoc's default template (extracted via `--print-default-data-file`), not arbitrary Word/LibreOffice files.
- **Slide formats need structure**. For `pptx`, `beamer`, and HTML slide decks, headings at the `--slide-level` create slides. Horizontal rules (`---`) manually split slides when `--slide-level=0`.

## References

- [01-markdown-variants](references/01-markdown-variants.md) — GFM, CommonMark, MultiMarkdown, PHP Markdown Extra, and strict Markdown
- [02-pdf-engines](references/02-pdf-engines.md) — PDF creation engines, LaTeX dependencies, HTML-to-PDF pipelines
- [03-docx-odt-pptx](references/03-docx-odt-pptx.md) — Microsoft Word, OpenDocument, and PowerPoint conversion details
- [04-latex-context](references/04-latex-context.md) — LaTeX, ConTeXt, Beamer slides, and typst conversion
- [05-html-formats](references/05-html-formats.md) — HTML output variants, slide frameworks, self-contained files
- [06-filters](references/06-filters.md) — JSON filters, Lua filters, AST transformation
- [07-templates-defaults](references/07-templates-defaults.md) — Template syntax, variables, defaults files
- [08-citations-bibliography](references/08-citations-bibliography.md) — Citation syntax, CSL styles, citeproc, bibliography formats
- [09-extensions](references/09-extensions.md) — Format extensions reference table, per-format capabilities
- [10-metadata-yaml](references/10-metadata-yaml.md) — YAML metadata blocks, variable passing, front matter
- [11-excel-csv-spreadsheets](references/11-excel-csv-spreadsheets.md) — Excel (xlsx), CSV, TSV input handling, sheet selection via Lua filters

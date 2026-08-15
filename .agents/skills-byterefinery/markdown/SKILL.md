---
name: markdown
description: Converts documents to and from Markdown. Accepts local files or URLs (http/https). Use when the user needs to convert PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), or Excel (xlsx) files to Markdown, or convert Markdown to PDF or standalone single-file HTML. Handles formula evaluation in Excel before conversion.
metadata:
  tags:
    - meta
    - markdown
    - pdf
    - office-documents
    - document-conversion
---

# markdown

## Overview

Converts documents to and from Markdown format using `markdown.sh`. Supports conversion from PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), and Excel (xlsx) to Markdown, and from Markdown to PDF or standalone single-file HTML.

Format is auto-detected from file extensions — no subcommands needed. Use `-i INPUT -o OUTPUT`.

For Excel files, formulas are evaluated before conversion so computed values appear in the output rather than raw formula expressions.

PDF extraction uses a fallback chain: **ghostscript → poppler → pypdf**. First successful engine is used.

Non-PDF formats (`.docx`, `.pptx`, `.odt`, `.xlsx`) are converted to Markdown using `pandoc`.

## Usage

### Basic conversion

```bash
# Convert any supported document to Markdown (default: stdout)
markdown.sh -i document.docx
markdown.sh -i presentation.pptx
markdown.sh -i report.pdf
markdown.sh -i data.xlsx

# Write to a file
markdown.sh -i report.pdf -o out.md
```

Markdown output goes to **stdout by default**. All timing and status messages go to stderr, making the output clean for piping or LLM consumption. Use `-o <file>` to write to a file instead.

### URL input

```bash
# Convert a remote file directly (downloaded automatically)
markdown.sh -i https://example.com/report.pdf
markdown.sh -i https://example.com/report.pdf -o out.md
```

Input can be a local file path or an HTTP/HTTPS URL. When a URL is given, the file is downloaded to a temp file (preserving the extension for format detection) and cleaned up after conversion. Download fallback chain: **curl → wget → uvx httpx[cli] → python (urllib)**.

### Convert Markdown to PDF or HTML

```bash
# To PDF
markdown.sh -i notes.md -o result.pdf

# To single-file HTML
markdown.sh -i notes.md -o result.html
```

Format is detected from the output file extension (`.pdf` or `.html`).

### PDF engine selection

```bash
# Default: auto fallback chain (ghostscript → poppler → pypdf)
markdown.sh -i report.pdf

# Force specific engines
markdown.sh -i report.pdf --pypdf
markdown.sh -i report.pdf --poppler
markdown.sh -i report.pdf --gs

# Use pandoc (for non-PDF: .docx, .pptx, .odt, .xlsx, etc.)
markdown.sh -i document.docx --pandoc
# Note: --pandoc cannot convert PDFs (pandoc doesn't support PDF input)
```

### Layout control

```bash
# Default: layout preserved (poppler: -layout flag)
markdown.sh -i report.pdf

# Disable layout (raw text flow)
markdown.sh -i report.pdf --no-layout
```

Layout preservation is on by default and affects the poppler engine (`pdftotext -layout`). It keeps visual column/spacing relationships. Disable with `--no-layout` for plain text flow. The flag has no effect on pypdf or ghostscript engines.

### Page comments

```bash
# Default: page comments inserted (<!-- page N begin --> / <!-- page N end -->)
markdown.sh -i report.pdf

# Suppress page comments
markdown.sh -i report.pdf --no-insert-page-number
```

### Image placeholders

```bash
# Default: <!-- image --> markers on pages with images
markdown.sh -i report.pdf

# Suppress image placeholders
markdown.sh -i report.pdf --no-insert-image-placeholder
```

### Combined options

```bash
# No page comments, no image markers, no layout
markdown.sh -i report.pdf --no-insert-page-number --no-insert-image-placeholder --no-layout
```

Supported input formats: `.pdf`, `.docx`, `.pptx`, `.odt`, `.xlsx`

Output path defaults to the input filename with `.md` extension. Override with `-o`.

### Timing

The script reports per-step and total processing time on stderr:

```
  Trying pypdf...
  → pypdf (12 pages)
  Extraction time (pypdf): 2.04 s
  → report.md

  Total time: 2.05 s
```

## Gotchas

- **Non-PDF conversion** — `.docx`, `.pptx`, `.odt`, `.xlsx` files are converted via `pandoc`. Engine flags (`--pypdf`, `--poppler`, `--gs`, `--pandoc`) only apply to PDF input and are ignored for other formats.
- **PDF fallback chain** — when no engine flag is given: ghostscript → poppler → pypdf. First successful engine is used. Use `--pypdf`, `--poppler`, `--gs`, `--pandoc` to force a specific engine. Flags are mutually exclusive.
- **Engine capabilities**:
  - **pypdf**: ~2s, extracts text layer only (empty for scanned pages)
  - **poppler**: ~1s, preserves visual layout by default (`-layout`), raw text with `--no-layout`
  - **ghostscript**: ~6s, extracts text layer via txtwrite device (empty for scanned pages)
- **Page comments** — `<!-- page N begin -->` and `<!-- page N end -->` inserted by default, wrapping each page's content. Suppress with `--no-insert-page-number`.
- **Image markers** — `<!-- image -->` inserted on pages with embedded images (detected via `pdfimages`). Gives indication of visual content without extracting the image itself. Suppress with `--no-insert-image-placeholder`.
- **Scanned PDFs produce empty output** — all three engines extract from the text layer only. Scanned/image-only PDFs will produce nothing (but will have `<!-- image -->` markers).
- **Excel: all sheets are converted** — xlsx input produces all sheets with no option to select individual ones. Each sheet becomes a `## <sheet-name>` heading followed by a pipe table.
- **Excel: files from some tools may fail** — workbooks created by programs like openpyxl can produce `Entry not found` errors. Files from Excel or LibreOffice work correctly.
- **PDF: requires an external engine** — PDF generation from Markdown needs TeX Live installed. If unavailable, PDF generation will fail.
- **Conversions are not perfectly lossless** — complex formatting, custom styles, and advanced layouts may degrade. Structure is preserved, not presentation details.
- **HTML output can be large** — the standalone single-file HTML embeds all CSS and images as data URIs, increasing file size.
- **Whitespace stripping** — leading and trailing whitespace is stripped from every line after conversion. Empty lines are preserved (kept as blank lines). This cleans up PDF extraction artifacts without affecting content structure, including LTR/RTL text.

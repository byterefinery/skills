---
name: markdown
description: Converts documents to and from Markdown. Use when the user needs to convert PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), or Excel (xlsx) files to Markdown, or convert Markdown to PDF or standalone single-file HTML. Handles formula evaluation in Excel before conversion. Supports image-to-Markdown via docling OCR.
allowed-tools: Bash(pandoc:*) Bash(uvx:*) Bash(pdftotext:*) Bash(pdfinfo:*) Bash(gs:*)
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

Converts documents to and from Markdown format using `markdown.sh`. Supports conversion from PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), and Excel (xlsx) to Markdown, and from Markdown to PDF or standalone single-file HTML. Also supports image-to-Markdown conversion (PNG, JPG, BMP, WebP, TIFF) via docling OCR.

For Excel files, formulas are evaluated before conversion so computed values appear in the output rather than raw formula expressions.

PDF extraction uses a fallback chain: **docling → pypdf → poppler → ghostscript**. Use explicit flags to force a specific engine.

## Usage

### To Markdown

```bash
# Convert any supported document to Markdown (auto engine selection)
markdown.sh to-md document.docx
markdown.sh to-md presentation.pptx
markdown.sh to-md report.pdf
markdown.sh to-md data.xlsx
markdown.sh to-md report.pdf -o out.md
```

**Engine selection** — force a specific PDF extraction engine:

```bash
# Use docling (best quality, OCR for scanned pages, supports images)
markdown.sh to-md report.pdf --docling

# Use pypdf (fast, text-layer only)
markdown.sh to-md report.pdf --pypdf

# Use poppler/pdftotext
markdown.sh to-md report.pdf --poppler

# Use ghostscript
markdown.sh to-md report.pdf --gs
```

**Page and OCR comments** — control `<!-- page N -->` and `<!-- ocr N -->` markers:

```bash
# Default: both page and OCR comments inserted
markdown.sh to-md report.pdf

# Suppress page comments
markdown.sh to-md report.pdf --no-insert-page-number

# Suppress OCR comments
markdown.sh to-md report.pdf --no-ocr-page-number

# Suppress both
markdown.sh to-md report.pdf --no-insert-page-number --no-ocr-page-number
```

**Image conversion** — requires docling:

```bash
markdown.sh to-md scan.png --docling
markdown.sh to-md photo.jpg --docling
```

Supported input formats: `.pdf`, `.docx`, `.pptx`, `.odt`, `.xlsx`
Supported image formats: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.webp`, `.tiff`

Output path defaults to the input filename with `.md` extension. Override with `-o`.

### To PDF

```bash
markdown.sh to-pdf notes.md
markdown.sh to-pdf notes.md -o result.pdf
```

### To HTML

```bash
markdown.sh to-html notes.md
markdown.sh to-html notes.md -o result.html
```

The HTML output is self-contained — all CSS, images, and scripts are embedded inline for portability.

## Gotchas

- **PDF fallback chain** — when no engine flag is given: docling → pypdf → poppler → ghostscript. First successful engine is used. Use `--docling`, `--pypdf`, `--poppler`, `--gs` to force a specific engine. Flags are mutually exclusive.
- **Engine capabilities**:
  - **docling**: best quality, OCR for scanned pages, image support, slowest (downloads models on first run)
  - **pypdf**: fast, extracts text layer only (empty for scanned pages)
  - **poppler**: fast, preserves layout with `-layout` flag (empty for scanned pages)
  - **ghostscript**: extracts text layer via txtwrite device (empty for scanned pages)
- **Page comments** — `<!-- page N -->` inserted by default. Suppress with `--no-insert-page-number`.
- **OCR comments** — `<!-- ocr N -->` inserted on pages where docling used OCR (scanned pages, all images). Suppress with `--no-ocr-page-number`.
- **Image conversion** — requires `--docling`. All image pages get both `<!-- page N -->` and `<!-- ocr N -->` by default.
- **Excel: all sheets are converted** — `to-md` on xlsx produces all sheets with no option to select individual ones. Each sheet becomes a `## <sheet-name>` heading followed by a pipe table.
- **Excel: files from some tools may fail** — workbooks created by programs like openpyxl can produce `Entry not found` errors. Files from Excel or LibreOffice work correctly.
- **PDF: requires an external engine** — the default engine needs TeX Live installed. If unavailable, PDF generation will fail.
- **Conversions are not perfectly lossless** — complex formatting, custom styles, and advanced layouts may degrade. Structure is preserved, not presentation details.
- **HTML output can be large** — the standalone single-file HTML embeds all CSS and images as data URIs, increasing file size.

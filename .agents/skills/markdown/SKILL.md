---
name: markdown
description: Converts documents to and from Markdown. Use when the user needs to convert PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), or Excel (xlsx) files to Markdown, or convert Markdown to PDF or standalone single-file HTML. Handles formula evaluation in Excel before conversion. Supports image-to-Markdown via docling.
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

Converts documents to and from Markdown format using `markdown.sh`. Supports conversion from PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), and Excel (xlsx) to Markdown, and from Markdown to PDF or standalone single-file HTML. Also supports image-to-Markdown conversion (PNG, JPG, BMP, WebP, TIFF) via docling.

Format is auto-detected from file extensions — no subcommands needed. Use `-i INPUT -o OUTPUT`.

For Excel files, formulas are evaluated before conversion so computed values appear in the output rather than raw formula expressions.

PDF extraction uses a fallback chain: **docling → pypdf → poppler → ghostscript**. Docling uses ONNX Runtime for layout detection (Heron model, ~2x faster than Transformers). Use `--ocr` for RapidOCR, `--vlm` for full VLM pipeline.

## Usage

### Basic conversion

```bash
# Convert any supported document to Markdown
markdown.sh -i document.docx
markdown.sh -i presentation.pptx
markdown.sh -i report.pdf
markdown.sh -i data.xlsx
markdown.sh -i report.pdf -o out.md
```

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
# Default: docling standard pipeline (Heron layout via ONNX Runtime, fast)
markdown.sh -i report.pdf

# Explicit layout mode (same as default, ONNX Runtime)
markdown.sh -i report.pdf --layout

# Standard pipeline + RapidOCR for scanned pages
markdown.sh -i report.pdf --ocr

# VLM pipeline (Granite-Docling-258M, full visual understanding)
markdown.sh -i report.pdf --vlm

# Force fallback engines (no AI models, text layer only)
markdown.sh -i report.pdf --pypdf
markdown.sh -i report.pdf --poppler
markdown.sh -i report.pdf --gs
```

`--ocr` and `--vlm` are mutually exclusive. `--layout` is optional (same as default).

### Page and OCR comments

```bash
# Default: both page and OCR comments inserted
markdown.sh -i report.pdf

# Suppress page comments
markdown.sh -i report.pdf --no-insert-page-number

# Suppress OCR comments
markdown.sh -i report.pdf --no-ocr-page-number

# Suppress both
markdown.sh -i report.pdf --no-insert-page-number --no-ocr-page-number
```

### Image conversion

```bash
markdown.sh -i scan.png
markdown.sh -i photo.jpg --ocr
```

Supported input formats: `.pdf`, `.docx`, `.pptx`, `.odt`, `.xlsx`
Supported image formats: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.webp`, `.tiff`

Output path defaults to the input filename with `.md` extension. Override with `-o`.

### Timing

The script reports per-step and total processing time on stderr:

```
  Trying docling (standard pipeline, ONNX layout)...
  → docling (12 pages, 0 OCR)
  Extraction time (docling): 48.64 s
  → report.md

  Total time: 48.65 s
```

## Gotchas

- **PDF fallback chain** — when no engine flag is given: docling → pypdf → poppler → ghostscript. First successful engine is used. Use `--docling`, `--layout`, `--ocr`, `--vlm`, `--pypdf`, `--poppler`, `--gs` to force a specific engine. Flags are mutually exclusive.
- **`--ocr` and `--vlm` are mutually exclusive** — choose one. `--layout` is optional and equivalent to default behavior.
- **Engine capabilities**:
  - **docling (standard, `--docling`, `--layout`)**: Heron layout detection via ONNX Runtime, extracts text/tables from PDF text layer. ~180s for 129-page PDF on CPU. Empty output for fully scanned PDFs.
  - **docling-ocr (`--ocr`)**: Standard pipeline + RapidOCR (ONNX backend), handles scanned pages via OCR. ~210s for 129-page PDF on CPU.
  - **docling-vlm (`--vlm`)**: VLM pipeline with Granite-Docling-258M, full visual understanding. Requires GPU for practical use (>30min on CPU). Best quality for mixed/scanned PDFs.
  - **pypdf**: ~2s, extracts text layer only (empty for scanned pages)
  - **poppler**: ~1s, preserves layout with `-layout` flag (empty for scanned pages)
  - **ghostscript**: ~6s, extracts text layer via txtwrite device (empty for scanned pages)
- **ONNX Runtime for layout** — the default docling mode uses ONNX Runtime (not Transformers) for the Heron layout model, giving ~2x speedup over the CLI default.
- **Page comments** — `<!-- page N -->` inserted by default. Suppress with `--no-insert-page-number`.
- **OCR comments** — `<!-- ocr N -->` inserted on pages where docling used OCR (scanned pages, all images). Suppress with `--no-ocr-page-number`.
- **Image conversion** — uses docling standard pipeline by default. Add `--ocr` for VLM pipeline. All image pages get both `<!-- page N -->` and `<!-- ocr N -->` by default.
- **Excel: all sheets are converted** — xlsx input produces all sheets with no option to select individual ones. Each sheet becomes a `## <sheet-name>` heading followed by a pipe table.
- **Excel: files from some tools may fail** — workbooks created by programs like openpyxl can produce `Entry not found` errors. Files from Excel or LibreOffice work correctly.
- **PDF: requires an external engine** — PDF generation from Markdown needs TeX Live installed. If unavailable, PDF generation will fail.
- **Conversions are not perfectly lossless** — complex formatting, custom styles, and advanced layouts may degrade. Structure is preserved, not presentation details.
- **HTML output can be large** — the standalone single-file HTML embeds all CSS and images as data URIs, increasing file size.
- **Images are skipped** — docling uses `--image-export-mode placeholder` so images produce `<!-- image -->` markers rather than embedded base64 data. This keeps output files small and text-only.

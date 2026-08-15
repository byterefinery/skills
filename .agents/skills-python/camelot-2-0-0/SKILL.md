---
name: camelot-2-0-0
description: >
  Camelot 2.0.0 — PDF table extraction library for Python. Use when extracting
  tabular data from PDF files into pandas DataFrames, CSV, Excel, JSON, HTML,
  Markdown, or SQLite. Supports ruled-grid tables (lattice), borderless/whitespace
  tables (stream, network), combined hybrid parsing, optional neural backend
  (flavor='ml' via Table Transformer), and auto-detection per page. Covers CLI
  (`camelot` / `camelot-py` commands), visual debugging via matplotlib, per-page
  parameter overrides, in-memory bytes input, encrypted PDFs, and multi-page
  table stitching. Triggers on PDF table extraction, camelot-py, read_pdf,
  lattice parser, stream parser, table-to-DataFrame from PDF, PDF-to-CSV table.
license: MIT
compatibility: >
  Python 3.10+. Requires opencv-python-headless, pypdfium2, playa-pdf, pandas,
  numpy, pillow. Avoid installing opencv-python alongside opencv-python-headless
  (they shadow each other). Optional extras include matplotlib (plot), torch+transformers (ml),
  rapidocr-onnxruntime (ocr), ghostscript (ghostscript backend).
metadata:
  tags:
    - python
    - pdf
    - data-extraction
    - tables
    - etl
---

# camelot 2.0.0

## Overview

Camelot extracts tables from PDF files into structured data (pandas DataFrames, CSV, Excel, JSON, HTML, Markdown, SQLite). It offers five parsing flavors plus auto-detection:

- **`lattice`** (default) — line-ruled tables via OpenCV line detection on rasterised pages, plus optional vector-line union. Most accurate for tables with visible grid lines.
- **`stream`** — borderless tables using whitespace-separated text columns and text-edge analysis. Works on tables with no visual rules.
- **`network`** — borderless tables via text bounding-box alignment connectivity. Stronger than stream on complex borderless layouts.
- **`hybrid`** — combines network (text alignment) with lattice (ruled lines). Best for partially-ruled tables.
- **`ml`** — optional neural backend using Microsoft's Table Transformer for structure, with cell text filled from the PDF's own text layer (no hallucination). Requires `camelot-py[ml]`. Best for dense borderless tables where heuristics plateau.
- **`auto`** — probes each page and routes to `lattice` or `network` per page. Handles mixed documents with text-only cover pages and ruled tables deeper in.

### Core Objects

- **`camelot.read_pdf(filepath, ...)`** — main entry point; returns a `TableList`
- **`TableList`** — list of `Table` objects; supports `.export()`, `.filter()`, `.stack_contiguous()`
- **`Table`** — single extracted table with `.df` (pandas DataFrame), `.parsing_report`, `.confidence`, `.to_csv()`, `.to_excel()`, `.to_json()`, `.to_html()`, `.to_markdown()`, `.to_sqlite()`
- **`camelot.plot(table, kind=...)`** — visual debugging plots (requires matplotlib)

### v2.0 Key Changes

- Python 3.10+ minimum (3.9 dropped)
- PDF backend migrated from `pdfminer.six` to `playa-pdf` (faster, better encrypted-PDF support)
- Default lattice `engine` is now `"combined"` (raster + vector lines)
- New `engine="vector"` for render-free lattice on vector-ruled PDFs
- Optional `flavor="ml"` neural backend (Table Transformer)
- `flavor="auto"` per-page flavor detection
- `TableList.filter()` for post-extraction quality filtering
- `Table.confidence` unified quality score in `[0, 1]`
- `per_page=` overrides, `replace_text=`, list-form `strip_text=`, in-memory bytes input, `cpu_count` cap for parallel

### Installation

```bash
pip install camelot-py              # core (note: camelot-py, not camelot)
pip install "camelot-py[plot]"      # + matplotlib for visual debugging
pip install "camelot-py[ml]"        # + Table Transformer (borderless)
pip install "camelot-py[ml,ocr]"    # + OCR for scanned PDFs
pip install "camelot-py[ghostscript]"  # ghostscript backend
```

CLI ad-hoc (no install):

```bash
uvx camelot-py lattice --output tables.csv document.pdf
```

## Usage

```python
import camelot

# Basic extraction (lattice, default)
tables = camelot.read_pdf("report.pdf")
print(tables[0].df)                   # pandas DataFrame
print(tables[0].parsing_report)       # accuracy, whitespace, confidence
tables[0].to_csv("table.csv")         # export single table
tables.export("tables.csv")           # export all (page-*-table-* suffix)

# Specify pages
tables = camelot.read_pdf("report.pdf", pages="1,3,5-10")
tables = camelot.read_pdf("report.pdf", pages="all")

# Different flavors
tables = camelot.read_pdf("doc.pdf", flavor="stream")    # borderless
tables = camelot.read_pdf("doc.pdf", flavor="network")   # alignment-based
tables = camelot.read_pdf("doc.pdf", flavor="hybrid")    # combined
tables = camelot.read_pdf("doc.pdf", flavor="auto")      # auto-detect per page
tables = camelot.read_pdf("doc.pdf", flavor="ml")        # neural (opt-in)

# Parallel processing
tables = camelot.read_pdf("long.pdf", pages="all", parallel=True, cpu_count=4)

# Encrypted PDF
tables = camelot.read_pdf("secure.pdf", password="userpass")

# In-memory bytes
tables = camelot.read_pdf(pdf_bytes)
tables = camelot.read_pdf(io.BytesIO(pdf_bytes))

# Filter low-quality tables
real = tables.filter(min_rows=2, min_columns=2, min_accuracy=90)

# Stack multi-page tables
stitched = tables.stack_contiguous(match="column_count")
stitched = tables.stack_contiguous(match="first_row", keep_first_header=False)
```

### CLI

```bash
# Lattice (ruled tables)
camelot lattice --output tables.csv report.pdf
camelot lattice -p 1,3,5 --output tables.csv report.pdf

# Stream (borderless)
camelot stream --output tables.csv report.pdf

# With visual debugging
camelot lattice -plot grid report.pdf
camelot stream -plot textedge report.pdf

# Auto-detect format from extension
camelot lattice --output tables.xlsx report.pdf
```

## Gotchas

- **Install `camelot-py`, not `camelot`** — PyPI has an unrelated `camelot` package (a config library). `pip install camelot` installs the wrong one. Always use `pip install camelot-py`. Import is still `import camelot`.
- **`opencv-python` vs `opencv-python-headless`** — Camelot depends on the headless variant. If `opencv-python` (full) is already installed, pip lets both coexist and they shadow each other, breaking `import cv2`. Uninstall the full version first.
- **Scanned/image-only PDFs** — Core Camelot reads the PDF text layer. Image-only PDFs (scans, faxes, photos) yield zero tables. Run OCRmyPDF first: `ocrmypdf scan.pdf scan-ocr.pdf`, then pass the OCR'd PDF to Camelot. Alternatively, use `flavor="ml"` with `camelot-py[ocr]` for in-process OCR.
- **PDF coordinate space** — `table_areas` and `columns` use PDF coordinates: origin at bottom-left, y increases upward. When converting from image coordinates (origin top-left), flip y: `pdf_y = page_height_pts - image_y * (72 / dpi)`.
- **`line_scale` default is 15** — docs used to say 40 but implementation always defaulted to 15. If you relied on 40, set it explicitly.
- **`Table.to_excel` drops index/header by default** — matches `to_csv` behavior. Pass `index=True, header=True` to include them.
- **`engine="combined"` is default** — safe (raster always runs, vector lines can only add). Pass `engine="raster"` for exact pre-2.0 behavior.
- **`flavor="ml"` pulls PyTorch** — the neural backend is opt-in because it adds hundreds of MB. Core install is unaffected.
- **`per_page` keys are 1-indexed** — page numbers start at 1, matching the `pages` argument convention.
- **`engine="vector"` yields no tables on pages without vector lines** — use `engine="auto"` or `"combined"` for mixed documents.
- **`stack_contiguous` averages quality metrics** — the stacked table's `accuracy` and `whitespace` are mean-aggregated; `page` and `order` come from the first table.
- **`replace_text` keys are literal substrings** — regex metacharacters are escaped. Longest match wins when keys overlap. Empty keys are ignored.
- **`strip_text` as string vs list** — string strips per-character; list strips whole substrings. `strip_text=" [12]"` strips spaces, brackets, and digits 1/2 individually. `strip_text=["[1]", "[2]"]` strips only the literal markers.

## References

- [01-read-pdf-api](references/01-read-pdf-api.md) — `read_pdf()` full parameter reference, flavors, return types
- [02-table-objects](references/02-table-objects.md) — Table, TableList, Cell classes; parsing_report; export methods
- [03-parser-flavors](references/03-parser-flavors.md) — lattice, stream, network, hybrid, ml, auto — how each works and when to use
- [04-advanced-tuning](references/04-advanced-tuning.md) — per_page overrides, table_areas, columns, strip_text, replace_text, layout_kwargs
- [05-line-detection](references/05-line-detection.md) — engine modes (raster, combined, vector), line_scale, iterations, erode_iterations
- [06-visual-debugging](references/06-visual-debugging.md) — camelot.plot() kinds, coordinate space conversion, bbox overlay
- [07-cli-reference](references/07-cli-reference.md) — full CLI reference for lattice, stream, network, hybrid subcommands
- [08-scanned-pdfs](references/08-scanned-pdfs.md) — OCRmyPDF workflow, flavor='ml' with OCR, mixed PDF handling
- [09-comparison](references/09-comparison.md) — Camelot vs Tabula, pdfplumber, PyMuPDF, gmft, unstructured, tablers
- [10-migration-v2](references/10-migration-v2.md) — breaking changes from 1.x to 2.0, new features checklist

# Comparison with Other Tools

How Camelot compares to other PDF table extraction tools.

## At a Glance

| Capability | Camelot | Tabula | pdfplumber | PyMuPDF | gmft | unstructured | tablers |
|-----------|---------|--------|------------|---------|------|-------------|---------|
| License | MIT | MIT | MIT | AGPL/commercial | MIT | Apache 2.0 | MIT |
| Runtime | pure Python | Java + wrapper | pure Python | C binding | PyTorch model | Python + plugins | Rust + Python |
| Ruled-grid tables | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ✓ |
| Borderless tables | ✓ | ✓ | ◐ | ✓ | ✓ | ✓ | ✗ |
| Per-page kwarg overrides | ✓ | ✗ | ◐ | ◐ | ✗ | ✗ | ✗ |
| Scanned PDFs | ✓ (ml+ocr) | ✗ | ✗ | ◐ | ✓ | ✓ | ✗ |
| Neural/ML structure | ✓ (opt-in) | ✗ | ✗ | ✗ | ✓ | ◐ | ✗ |
| Confidence per table | ✓ | ✗ | ✗ | ◐ | ✓ | ✗ | ✗ |
| In-memory bytes | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Multi-page stitching | ✓ | ◐ | ◐ | ◐ | ✓ | ◐ | ✗ |
| Heavy native deps | opencv-headless, pdfium | JRE | none | mupdf | PyTorch+GPU | varies | none |

## Tabula

Most direct peer. Camelot's `lattice`/`stream` naming is borrowed from Tabula.

**Tabula wins on:** Auto-detection of stream tables; interactive web UI for marking regions.

**Camelot wins on:** Multi-row headers, merged spanning cells, italic/superscript handling; `copy_text`, `shift_text`, `flag_size`, `replace_text`; no JVM dependency.

## pdfplumber

Layout analysis library with table extraction features. Built on pdfminer.six.

**pdfplumber wins on:** Fine-grained access to every layout primitive (characters, rects, curves). Right pick for "find tables AND adjacent paragraph headers".

**Camelot wins on:** Out-of-the-box table detection quality; per-table quality reports; `flavor="hybrid"` combining lattice + network; `playa-pdf` backend (faster than pdfminer.six).

## PyMuPDF (built-in tables)

`Page.find_tables()` API (v1.23+). C-level mupdf library.

**PyMuPDF wins on:** Pure speed on simple ruled tables; no rasterisation; good if already using PyMuPDF for other PDF tasks.

**Camelot wins on:** Stream/network/hybrid flavors for borderless tables; per-page parameter overrides; multi-page stitching; MIT license (PyMuPDF is AGPL).

## gmft

"Give Me The Formatted Tables" — Table Transformer neural network.

**gmft wins on:** Pure model-first workflow on visually-complex tables (bank statements, forms).

**Camelot wins on:** Heuristic-first by default (predictable, CPU-only, no model weights); when using ML, Camelot fills cell text from the PDF's own text layer (no hallucination); per-extraction kwargs; per-table confidence score.

**Resource cost:** gmft always pulls model weights (~hundreds of MB) and benefits from GPU. Camelot's core needs neither.

## unstructured.io

Document preprocessing toolkit for LLM ingestion pipelines.

**unstructured wins on:** Mixed-content documents where tables are one element among many; OCR/image fallback built-in.

**Camelot wins on:** Table-extraction-only workloads; maximum control over parameters; per-table confidence; pandas DataFrame output; CSV/Excel/JSON/SQLite/Markdown exporters.

**Output:** unstructured returns HTML/text snippets; Camelot returns pandas DataFrames.

## tablers

Rust-core extractor with PyO3 bindings. PDF handling via pdfium.

**tablers wins on:** Raw speed on ruled tables (~67x faster than Camelot's combined engine).

**Camelot wins on:** Extraction quality (leads on every quality metric on ICDAR-2013); breadth (borderless tables, neural ML, scanned PDFs, per-table quality, multi-page stitching, pandas output).

**Head-to-head on ruled tables (ICDAR-2013, 67 PDFs):**

| Tool | F1 | TEDS | row | col | time |
|------|------|------|------|------|------|
| camelot lattice (combined) | 0.778 | 0.789 | 0.762 | 0.829 | 101s |
| camelot lattice (vector) | 0.766 | 0.784 | 0.748 | 0.806 | 13s |
| tablers | 0.750 | 0.724 | 0.657 | 0.741 | 1.5s |

Camelot's `engine="vector"` narrows the speed gap to ~9x while keeping most of combined's quality.

## Dormant Tools

No longer compared (repositories archived/dormant):

- **pdftables** — last release 2014
- **pdf-table-extract** — last release 2017

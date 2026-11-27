---
name: camelot-2-2-0
description: >
  Extracts tables from PDF files into pandas DataFrames or CSV/JSON/Excel/HTML/SQLite
  files (camelot-py 2.2.0). Use when parsing ruled (lattice), borderless whitespace-aligned
  (stream), text-alignment (network), hybrid, or neural Table-Transformer (ml) tables from
  PDFs; covers camelot.read_pdf(), flavor selection, table_areas/columns overrides, per-page
  kwargs, parallel processing, encrypted and in-memory PDFs, OCR workflow for scans, the
  camelot CLI, and visual debugging with camelot.plot(). Python 3.11+.
license: Apache-2.0
compatibility: Requires Python 3.11+; pip install camelot-py (extras [plot], [ml], [ocr] optional)
metadata:
  tags:
    - python
    - pdf
    - data-extraction
    - tabular-data
---

# camelot 2.2.0

## Overview

Camelot extracts tables from PDF files. It reads the PDF's text operators (fonts, positions, kerning) via `playa` and, for line-based parsing, renders pages to images for OpenCV line detection. The result is a `TableList` of `Table` objects; each table exposes a pandas DataFrame (`table.df`) plus export methods (`to_csv`, `to_json`, `to_excel`, `to_html`, `to_markdown`, `to_sqlite`).

Five parser flavors exist, selected with the `flavor=` keyword:

- **`lattice`** (default) — deterministic; for tables with demarcated ruled lines. Renders the page and detects line segments/joints/contours with OpenCV.
- **`stream`** — text-based; for borderless tables whose cells are separated by whitespace. Groups words into text rows, computes "textedges" to guess table areas, then guesses column counts.
- **`network`** — text-based; finds tables via coordinate alignments of text bounding boxes (elements must be connected along both axes), grows a table from the most-connected seed element.
- **`hybrid`** — combines network (structure) with lattice (precise row/column boundaries); accepts kwargs from both stream and lattice.
- **`ml`** — optional neural backend (Table Transformer): the model supplies table structure, cell text is filled from the PDF's own text layer so it cannot hallucinate values. Requires `pip install 'camelot-py[ml]'` (PyTorch). Best for dense borderless tables and, with `[ocr]`, scanned/image-only PDFs.
- **`auto`** — probes each page (counts ruled lines) and parses ruled pages via `lattice` with `engine='combined'`, the rest via `network`; a `UserWarning` reports per-page choices. Slower because every page is rendered for the probe.

## Usage

### Install and quickstart

```bash
pip install "camelot-py"        # or: conda install -c conda-forge camelot-py
# ad-hoc CLI without installing:
uvx camelot-py lattice --output tables.csv document.pdf
```

```python
import camelot

tables = camelot.read_pdf('foo.pdf')          # flavor='lattice' by default, page 1 only
print(tables)                                 # <TableList n=1>
table = tables[0]
print(table.parsing_report)                  # accuracy, whitespace, confidence, order, page
df = table.df                                 # pandas DataFrame
table.to_csv('foo.csv')
tables.export('out', f='csv')                # out-page-1-table-1.csv, ... (compress=True -> zip)
```

`parsing_report` fields: `accuracy` and `whitespace` are 0–100; `confidence` is a single [0, 1] score = `(accuracy / 100) * (1 - whitespace / 100)` — convenient for "keep tables above X" filtering.

### Choosing a flavor

- Ruled/ruled-line tables → `lattice` (default).
- Borderless, whitespace-aligned columns → `stream`.
- Borderless with tricky alignment → `network` or `hybrid`.
- Dense borderless where heuristics plateau, or scanned PDFs (with `[ocr]`) → `ml`.
- Mixed document (some ruled pages, some not) → `auto`, or `per_page` overrides.

### Pages, parallelism, encrypted and in-memory input

```python
# Page selection: comma list, ranges, 'end', or 'all'
camelot.read_pdf('doc.pdf', pages='1,2,3')
camelot.read_pdf('doc.pdf', pages='1,4-10,20-end')

# Concurrency — one worker per CPU by default; bound with cpu_count=N
camelot.read_pdf('long.pdf', pages='all', parallel=True, cpu_count=4)

# Encrypted PDFs (playa-supported encryption types; may need PyCryptodome)
camelot.read_pdf('enc.pdf', password='userpass')

# In-memory input: bytes, bytearray, io.BytesIO, or any binary stream with .read()
import io, requests
camelot.read_pdf(io.BytesIO(requests.get(url).content))
```

### Per-page parameter overrides

When different pages need different settings (different `table_areas`, a different `flavor` on one page), use `per_page` — keys are 1-indexed page numbers (int or str), values are dicts of any valid `read_pdf` kwarg, including `flavor`:

```python
tables = camelot.read_pdf(
    'report.pdf',
    pages='1-3',
    flavor='stream',
    split_text=True,
    per_page={2: {'table_areas': ['120, 210, 400, 90']}},
)
```

Unknown kwargs or flavors raise errors naming the offending page.

### Filtering and stacking results

```python
tables = camelot.read_pdf('noisy.pdf')
real = tables.filter(min_rows=2, min_columns=2)          # returns a new TableList
good = tables.filter(min_accuracy=90).filter(max_whitespace=50)
# thresholds default to no-op (min_rows=1, min_columns=1, min_accuracy=0, max_whitespace=100)
```

### Command line

The CLI mirrors the API; `--format` is optional (inferred from `--output` extension), and `--output` is a template — each table is written to `<stem>-page-<P>-table-<T>.<ext>`:

```bash
camelot --format csv --output foo.csv lattice foo.pdf
camelot --pages 1,2,3 lattice your.pdf
camelot --password userpass lattice foo.pdf
camelot stream -T 316,499,566,337 table_areas.pdf          # -T table area
camelot lattice -R 170,370,560,270 table_regions.pdf       # -R table region
camelot stream -C 72,95,209,327,442,529,566,606,683 column_separators.pdf   # -C columns
camelot lattice -plot grid foo.pdf                          # visual debugging
```

Full CLI options are in [01-cli](references/01-cli.md).

### Visual debugging (requires `pip install camelot-py[plot]`)

`camelot.plot(table, kind=...)` renders what the parser detected on the page; kinds: `text`, `grid`, `contour`, `line`, `joint`, `textedge`. `'line'` and `'joint'` are lattice-only; `'textedge'` is stream-only. Use the interactive plot's x-y readout to note coordinates for `table_areas` or `columns`.

```python
camelot.plot(tables[0], kind='grid').show()      # detected table grid
camelot.plot(tables[0], kind='text').show()      # all text (helps pick stream areas/columns)
camelot.plot(tables[0], kind='contour').save('c.png')  # or save to file via filename=
```

## Tuning extraction

Common failure modes and the kwarg that fixes them — full details with examples in [02-advanced-options](references/02-advanced-options.md):

| Symptom | Fix (kwarg) | Flavor |
|---|---|---|
| Table lines in background, not detected | `process_background=True` | lattice |
| Ruled lines don't meet at corners; rows dropped | `iterations=N` + `erode_iterations=N` (morphological closing) | lattice |
| Faintly-rendered vector-ruled table missed | `engine='combined'` or `'vector'` (default is `'combined'`) | lattice, hybrid |
| Table at known coordinates | `table_areas=['x1,y1,x2,y2']` (PDF space, origin bottom-left) | any |
| Table in approximate region only | `table_regions=['x1,y1,x2,y2']` | any |
| Repeated header/footer text frames the table | `header_text=[...]`, `footer_text=[...]` (substring match, case-sensitive) | stream/network |
| Column separators guessed wrong | `columns=['x1,x2,...']` (list length must equal `table_areas` length when both given; use `''` for "no columns") | stream |
| Words merged into one cell across columns | `split_text=True` | stream |
| Superscripts mangle numbers (`24.912`) | `flag_size=True` (wraps in `<s></s>`) | stream |
| Unwanted chars/spaces/dots in cells | `strip_text=' .\n'` (per-char) or `['[1]','[2]']` (per-substring) | any |
| Rewrite cell text (fix soft line breaks, units) | `replace_text={' \n': ' ', 'kw': 'kW'}` (literal substrings, longest key wins) | any |
| Guessed table area too small (text far apart vertically) | increase `edge_tol` (default 50) | stream |
| Rows split that should be grouped | `row_tol=N` (default 2) | stream |
| Short lines not detected | larger `line_scale` (default 15; >150 detects text as lines) | lattice |
| Spanning-cell text placement wrong | `shift_text=['l','t']` default; also `'r'`, `'b'`, `''` (no shift) | lattice |
| Repeat spanning-cell values down/across | `copy_text=['v']` and/or `['h']` | lattice |
| Layout grouping too aggressive/loose | `layout_kwargs={'detect_vertical': False}` (LAParams) | any |

## Gotchas

- **Default flavor is `lattice`, default page is 1 only.** A multi-page PDF returns tables from page 1 unless you pass `pages='all'` or an explicit range — a common source of "missing tables".
- **`table_areas` are in PDF coordinate space** (origin at bottom-left), not image pixels. If your coordinates come from a rendered image, convert with `camelot.image_bbox_to_pdf(bbox, image_size, pdf_size, as_string=True)`.
- **Stream-only kwargs are rejected for lattice and vice versa.** `header_text`, `footer_text`, `columns`, `row_tol`, `column_tol` work only with stream/network; `process_background`, `line_scale`, `shift_text`, `copy_text`, `iterations`, `erode_iterations`, `engine`, `backend` etc. are lattice-only (hybrid accepts both). Passing the wrong set raises an error.
- **`--output` is a template, not a literal filename.** The CLI writes `<stem>-page-P-table-T.ext`; Python's `TableList.export()` does the same and needs `compress=True` to bundle into one ZIP.
- **Scanned/image-only PDFs yield zero tables** — there is no text layer. Run OCR first (`ocrmypdf scan.pdf scan-ocr.pdf`, or use `flavor='ml'` with the `[ocr]` extra). Camelot deliberately does not bundle Tesseract.
- **OpenCV conflict:** camelot depends on `opencv-python-headless`. If full `opencv-python` is installed, the two shadow each other and break `import cv2`; uninstall one. The same applies to the `[ocr]` extra (RapidOCR hard-requires full opencv) — see [03-install-and-backends](references/03-install-and-backends.md).
- **`engine` default is `'combined'`** in 2.x (raster + PDF vector lines unioned), not plain raster. It is safe on any lattice PDF: raster always runs first, so vector lines can only add detections. `engine='vector'` skips rendering entirely but finds nothing on pages without vector rules — prefer `'auto'`-style documents with `flavor='auto'`.
- **Encrypted-PDF behavior changed in 1.0+**: camelot now honours the `/Encrypt` text-extraction permission and raises `playa.exceptions.PDFTextExtractionNotAllowed` if extraction is forbidden (previously a silent no-op). Supplying the owner password via `password=` bypasses it.
- **In-memory inputs are spilled to a temp file internally** (so the lattice image backend keeps working) and cleaned up on close; for file-like inputs the read position is preserved.
- **`parallel=True` emits per-page progress logs from worker processes**, which may not propagate to your logging handlers and finish out of order. Enable with `logging.basicConfig(level=logging.INFO)`; silence with `suppress_stdout=True`.
- **`ml` flavor is opt-in and slow** (~1 s/page with GPU vs tens of ms for network) because it pulls PyTorch — but it is the only parser that works without a text layer at all, and on the borderless FinTabNet.c benchmark it roughly doubles TEDS over network/hybrid.
- **`strip_text` semantics differ by type**: a plain `str` strips *characters* (so `' [12]'` nicks lone brackets/digits); pass a list/tuple to strip whole *substrings*.

## References

- [01-cli](references/01-cli.md) — full CLI command reference: flavors, options, format inference
- [02-advanced-options](references/02-advanced-options.md) — every read_pdf kwarg with defaults and examples (lattice/stream tuning, table areas, regions, header/footer text, columns, split/flag/strip/replace text, backends)
- [03-install-and-backends](references/03-install-and-backends.md) — install extras, OpenCV conflict resolution, image conversion backends, OCR workflow for scanned PDFs

# Parser Flavors Reference

Detailed guide to each parsing flavor: how they work, when to use them, and their parameters.

## Lattice (default)

Line-ruled table detection via OpenCV on rasterised PDF pages.

### How It Works

1. PDF page is rendered to an image (default: pdfium backend, 300 DPI)
2. Horizontal and vertical line segments are detected via morphological transformations
3. Line intersections are found by overlapping horizontal and vertical line masks
4. Table boundaries are computed by OR-ing line segments
5. Coordinates are scaled from image space to PDF coordinate space
6. Spanning cells are detected from line segments and intersections
7. Text is assigned to cells based on x,y coordinates

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `engine` | `"combined"` | Line detection engine (raster/combined/vector) |
| `line_scale` | 15 | Min line detection threshold (larger = detects smaller lines) |
| `process_background` | False | Detect lines in background layer |
| `iterations` | 0 | Dilation passes to close line gaps |
| `erode_iterations` | 0 | Erosion passes after dilation (morphological closing) |
| `line_tol` | 2 | Tolerance for merging close lines |
| `joint_tol` | 2 | Tolerance for joint proximity |
| `threshold_blocksize` | 15 | OpenCV adaptive threshold neighborhood size |
| `threshold_constant` | -2 | Constant subtracted from mean in adaptive threshold |
| `copy_text` | None | `['h']` and/or `['v']` to copy spanning cell text |
| `shift_text` | `['l', 't']` | Text gravity: `''`, `'l'`, `'r'`, `'t'`, `'b'` |
| `backend` | `"pdfium"` | Image conversion backend |
| `resolution` | 300 | PDF-to-PNG DPI |

### When to Use

- Tables with visible ruled grid lines
- Most structured financial reports, government forms, invoices
- Default choice for most PDF table extraction tasks

### engine Modes

- `"combined"` (default) — raster OpenCV detection + PDF vector line union. Safe: raster always runs, vector can only add.
- `"raster"` — OpenCV on rendered page only. Pre-2.0 behavior.
- `"vector"` — pure vector line detection, no rasterisation. Fastest, but yields no tables on pages without vector lines.

## Stream

Borderless table detection via whitespace and text-edge analysis.

### How It Works

1. Words are grouped into text rows by y-axis overlap
2. Textedges are calculated to guess table areas (based on Nurminen's thesis)
3. Column count is guessed from the mode of words per text row
4. Column x-ranges are calculated and extended based on word positions
5. Table is formed from y-ranges and x-ranges; words assigned by coordinates

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `edge_tol` | 50 | Tolerance for extending textedges vertically |
| `row_tol` | 2 | Tolerance for combining text vertically into rows |
| `column_tol` | 0 | Tolerance for combining text horizontally into columns |
| `columns` | None | Explicit column x-coordinates as `['x1,x2,x3,...']` |
| `table_areas` | None | Explicit table areas as `['x1,y1,x2,y2']` |
| `split_text` | False | Split merged text across cells |

### When to Use

- Tables with no visual rules, separated by whitespace
- Consistent column alignment
- Government statistics, census data, academic tables

### Tuning

- Increase `edge_tol` (default 50) when text is far apart vertically and table areas are not detected correctly
- Decrease `row_tol` to group rows more tightly
- Use `columns=['72,95,209,...']` for explicit column separators when auto-detection fails

## Network

Borderless table detection via text bounding-box alignment connectivity.

### How It Works

1. Enumerate bounding boxes of all text elements on the page
2. Identify common horizontal/vertical coordinate alignments across text elements
3. Prune to keep only text elements with connections along both axes (forming a "network")
4. Seed from the text element with most connections
5. Iteratively grow the table by searching for nearby networked text
6. Detect headers from text above the table body
7. Repeat for multiple tables on the same page

### Key Parameters

Same as stream: `edge_tol`, `row_tol`, `column_tol`, `columns`, `table_areas`, `split_text`.

### When to Use

- Complex borderless tables where stream struggles
- Tables with irregular spacing but consistent alignment
- Multi-table pages where stream over-detects

## Hybrid

Combines Network (text alignment) and Lattice (ruled lines).

### How It Works

1. Runs both network and lattice parsers
2. Where both find a table, uses network results enhanced by lattice's precise row/column boundaries
3. Lattice provides more accurate coordinates from solid lines; network handles borderless areas

### Key Parameters

Accepts parameters from both lattice and stream:

| Parameter | From | Description |
|-----------|------|-------------|
| `engine` | lattice | Line detection engine for lattice half |
| `line_scale` | lattice | Min line detection threshold |
| `edge_tol` | stream | Textedge extension tolerance |
| `row_tol` | stream | Vertical text grouping tolerance |
| `columns` | stream | Explicit column separators |
| `table_areas` | both | Explicit table areas |

### When to Use

- Partially-ruled tables (some lines, some whitespace)
- Tables with rules in some areas but not others
- Best default when unsure between lattice and network

### render-free Hybrid

`engine="vector"` with `flavor="hybrid"` skips rasterisation entirely — vector ruled lines merged with network text-edge alignment. ~10x faster than raster path for partial-ruled tables.

## ML (Table Transformer)

Optional neural backend using Microsoft's Table Transformer (TATR).

### How It Works

1. Page is rendered to an image
2. TATR detection model finds table region(s)
3. TATR structure model recognizes rows, columns, spanning cells as bounding boxes
4. Boxes are mapped from image space to PDF coordinates
5. Cell text is filled from the PDF's own text layer (no hallucination)
6. For scanned pages: `ocr='auto'` reads text from the image instead

### Installation

```bash
pip install "camelot-py[ml]"       # borderless tables
pip install "camelot-py[ml,ocr]"   # + scanned PDFs
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `device` | auto | `"cuda"`, `"xpu"`, or auto-detect |

### When to Use

- Dense borderless tables where heuristics plateau
- Financial statements, complex academic tables
- Scanned PDFs (with `[ocr]` extra)

### Performance

~1 second/page with GPU vs tens of milliseconds for network. CPU-only is significantly slower.

### Borderless Benchmark (FinTabNet.c, 545 financial PDFs)

| Flavor | F1 | TEDS | row | col |
|--------|------|------|------|------|
| ml | 0.750 | 0.371 | 0.235 | 0.570 |
| network | 0.725 | 0.200 | 0.109 | 0.220 |
| hybrid | 0.658 | 0.198 | 0.109 | 0.217 |

ML roughly doubles borderless TEDS over network/hybrid.

## Auto

Per-page flavor detection.

### How It Works

1. Each page is rendered and probed for ruled line segments
2. Pages with enough horizontal + vertical lines (≥2 each) are routed to `lattice` with `engine="combined"`
3. Remaining pages go to `network`
4. Results are merged and sorted by page/order

### When to Use

- Mixed documents: text-only cover pages + ruled tables deeper in
- Unknown PDF structure
- When you want the best parser per page without manual selection

### Trade-offs

More accurate (right parser per page) but slower (renders every page for the probe). A `UserWarning` reports the per-page choices.

# camelot.read_pdf() — full kwarg reference (v2.2.0)

Signature: `camelot.read_pdf(filepath, pages="1", password=None, flavor="lattice", suppress_stdout=False, parallel=False, cpu_count=None, layout_kwargs=None, per_page=None, debug=False, **kwargs)`. Flavor-specific kwargs go in `**kwargs`; stream-only ones are annotated `^`, lattice-only `*` (hybrid accepts both).

## Core parameters

| Kwargs | Default | Notes |
|---|---|---|
| `filepath` | — | Path/URL, or `bytes`/`bytearray`/`io.BytesIO`/any binary stream with `.read()`. In-memory inputs are spilled to a temp file internally and cleaned up on close; file-like read position is preserved. |
| `pages` | `"1"` | Comma-separated: `'1,3,4'`, `'1,4-end'`, `'all'`. |
| `password` | `None` | Decryption password (playa-supported encryption types). |
| `flavor` | `"lattice"` | `lattice`, `stream`, `network`, `hybrid`, `ml`, `auto`. |
| `suppress_stdout` | `False` | Suppress logs and warnings. |
| `parallel` | `False` | Process pages concurrently, one worker per CPU. |
| `cpu_count` | `None` | Max workers when `parallel=True`; clamped to `[1, cpu_count()]`. |
| `layout_kwargs` | `{}` | Dict of `pdfminer.layout.LAParams` kwargs (e.g. `{'detect_vertical': False}`). |
| `per_page` | `None` | Map of 1-indexed page number → dict of any valid kwarg override (including `flavor`). |

## Stream / network kwargs (`^`)

| Kwargs | Default | Notes |
|---|---|---|
| `table_areas` | `None` | List of `'x1,y1,x2,y2'` strings; PDF coordinate space, origin bottom-left. |
| `header_text` | `None` | List of substrings; the matched line's **bottom** becomes the table top edge. Substring match, case-sensitive; topmost match used. Stream-only, Python-API-only (no CLI). |
| `footer_text` | `None` | List of substrings; matched line's **top** becomes the table bottom edge; bottommost match used. |
| `columns` | `None` | List of comma-separated x-coordinate strings. If a single string is given with no `table_areas`, it applies to the whole page. When both lists are given, lengths must be equal (use `''` for "no columns" on that area). |
| `split_text` | `False` | Split strings lying in different cells but merged into one. |
| `flag_size` | `False` | Wrap super/subscripts in `<s></s>` based on font size. |
| `strip_text` | `''` | `str` → strip per-character; list/tuple of `str` → strip whole substrings (new in 2.0). |
| `replace_text` | `None` | Dict substring→replacement applied to every cell just before assignment. Literal substrings (regex metachars escaped); longest key wins at a position; empty keys ignored. Works with all flavors; stacks with `strip_text` (strip runs first). |
| `row_tol` | `2` | Vertical tolerance to combine text into rows. |
| `column_tol` | `0` | Horizontal tolerance to combine text into columns. |
| `edge_tol` | `50` | Tolerance for extending textedges vertically; increase when auto-detected table area is too small (text far apart vertically). |

## Lattice kwargs (`*`)

| Kwargs | Default | Notes |
|---|---|---|
| `process_background` | `False` | Process background lines. |
| `line_scale` | `15` | Line size scaling factor; larger → smaller detected lines. >150 starts detecting text as lines. |
| `copy_text` | `None` | List from `{'h','v'}` — copy spanning-cell text horizontally/vertically. Disabled by default. |
| `shift_text` | `['l','t']` | List from `{'l','r','t','b',''}` applied in order — "gravity" for spanning-cell text. `['']` = no shift (text stays in place). |
| `line_tol` | `2` | Tolerance to merge close vertical/horizontal lines. |
| `joint_tol` | `2` | Tolerance for detected lines/points lying close together. |
| `threshold_blocksize` | `15` | OpenCV adaptiveThreshold neighborhood size (3, 5, 7, …). |
| `threshold_constant` | `-2` | OpenCV adaptiveThreshold constant. |
| `iterations` | `0` | Dilation passes to close gaps in the line mask. |
| `erode_iterations` | `0` | Erosion passes **after** dilation. Set equal to `iterations` for a morphological closing — bridges gaps without thickening lines (avoids spurious extra rows). |
| `backend` | `"pdfium"` | Image conversion backend: `"pdfium"`, `"ghostscript"`, or a custom object with `convert(pdf_path, png_path)`. |
| `use_fallback` | `True` | Fallback to another backend if unavailable. |
| `resolution` | `300` | Resolution for PDF→PNG conversion. |
| `engine` | `"combined"` | Line-detection engine: `'combined'` (raster + vector lines unioned; default), `'raster'` (OpenCV only, pre-2.x behavior), `'vector'` (PDF vector rules only — fastest, no render, but finds nothing without vector rules). Also drives the lattice half of `hybrid`. |

## Examples

```python
import camelot

# Lattice: bridge line gaps without thickening
camelot.read_pdf('broken.pdf', flavor='lattice', iterations=1, erode_iterations=1)

# Lattice: recover faintly-ruled vector table
camelot.read_pdf('vector.pdf', flavor='lattice', engine='combined')

# Stream: derive area from repeated header/footer text
camelot.read_pdf(
    'health.pdf', flavor='stream',
    header_text=['Public Health Outlay'],
    footer_text=['Health Sector Financing'],
)

# Stream: explicit areas + per-area columns ('' = no columns for that area)
camelot.read_pdf('doc.pdf', flavor='stream',
                 table_areas=['12,54,43,23', '20,67,55,33'],
                 columns=['10,120,200,400', ''])

# Fix soft line breaks + normalize units in every cell
camelot.read_pdf('doc.pdf', replace_text={' \n': ' ', 'kw': 'kW', 'kva': 'kVA'})

# Per-page override: page 2 gets its own table area
camelot.read_pdf('report.pdf', pages='1-3', flavor='stream', split_text=True,
                 per_page={2: {'table_areas': ['120, 210, 400, 90']}})

# Convert image-pixel bbox to PDF-space table area string
area = camelot.image_bbox_to_pdf((300, 600, 1800, 1500), (2550, 3300), (612, 792), as_string=True)
camelot.read_pdf('doc.pdf', flavor='stream', table_areas=[area])
```

## TableList / Table API

- `tables` is a `TableList`: `len(tables)`, `tables[i]`, iteration, `tables.n`.
- `tables.filter(min_rows=1, min_columns=1, min_accuracy=0, max_whitespace=100)` → new `TableList` (all thresholds default to no-op).
- `tables.stack_contiguous(...)` → vertically stack tables that look like continuations across pages.
- `tables.export(path, f='csv', compress=False)` → writes `<path>-page-P-table-T.<ext>` per table; `compress=True` bundles into a ZIP at `path`.
- `table.df` → pandas DataFrame; `table.data`, `table.parsing_report`, `table.confidence`, `table.shape`.
- Per-table export: `table.to_csv()`, `to_json()`, `to_excel()`, `to_html()`, `to_markdown()`, `to_sqlite()`.

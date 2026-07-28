# read_pdf() API Reference

Full parameter reference for `camelot.read_pdf()`, the main entry point.

## Signature

```python
camelot.read_pdf(
    filepath,              # str | Path | bytes | binary file-like | URL
    pages="1",             # str — comma-separated page numbers
    password=None,         # str — encryption password
    flavor="lattice",      # str — parser flavor
    suppress_stdout=False, # bool — silence logs
    parallel=False,        # bool — multi-process
    cpu_count=None,        # int — worker cap (None = all cores)
    layout_kwargs=None,    # dict — playa LAParams overrides
    per_page=None,         # dict — per-page kwarg overrides
    debug=False,           # bool — debug mode
    # Flavor-specific kwargs below
    table_areas=None,      # list[str] — "x1,y1,x2,y2" in PDF coords
    columns=None,          # list[str] — column x-coords (stream/network/hybrid)
    split_text=False,      # bool — split merged text across cells
    flag_size=False,       # bool — flag superscripts/subscripts with <s></s>
    strip_text='',         # str | list[str] — chars/substrings to strip
    replace_text=None,     # dict — substring -> replacement mapping
    row_tol=2,             # int — vertical text grouping tolerance
    column_tol=0,          # int — horizontal text grouping tolerance
    process_background=False,  # bool — detect background lines (lattice)
    line_scale=15,         # int — min line detection threshold (lattice)
    copy_text=None,        # list — ['h'] and/or ['v'] (lattice)
    shift_text=['l','t'],  # list — text gravity direction (lattice)
    line_tol=2,            # int — line merge tolerance (lattice)
    joint_tol=2,           # int — joint proximity tolerance (lattice)
    threshold_blocksize=15,# int — OpenCV adaptive threshold block size
    threshold_constant=-2, # int — OpenCV adaptive threshold constant
    iterations=0,          # int — dilation passes (lattice)
    erode_iterations=0,    # int — erosion passes after dilation (lattice)
    backend="pdfium",      # str — image conversion backend
    use_fallback=True,     # bool — fallback to alternate backend
    resolution=300,        # int — PDF-to-PNG DPI
    engine="combined",     # str — line detection engine (lattice)
) -> TableList
```

## filepath

Accepts multiple input types:

```python
# Filesystem path
camelot.read_pdf("report.pdf")
camelot.read_pdf(Path("report.pdf"))

# URL (auto-downloaded)
camelot.read_pdf("https://example.org/report.pdf")

# Raw bytes
camelot.read_pdf(pdf_bytes)
camelot.read_pdf(bytearray(pdf_bytes))

# Binary file-like
import io, requests
camelot.read_pdf(io.BytesIO(pdf_bytes))
camelot.read_pdf(open("report.pdf", "rb"))
resp = requests.get("https://example.org/report.pdf")
camelot.read_pdf(resp.raw)  # or io.BytesIO(resp.content)
```

For in-memory inputs, Camelot spills to a temporary file once and cleans up on context-manager exit. The read position of file-like inputs is preserved after the call.

## pages

Comma-separated page numbers (1-indexed). Supports ranges and `end` keyword:

```python
pages="1"           # first page only (default)
pages="1,3,5"       # specific pages
pages="1,4-10,20-end"  # mixed: specific + range + to end
pages="all"         # every page
```

## flavor

| Flavor | Description | Best For |
|--------|-------------|----------|
| `lattice` | Line detection via OpenCV on rasterised page + optional vector lines | Tables with visible ruled grid lines |
| `stream` | Whitespace-separated text columns via text-edge analysis | Borderless tables with consistent column alignment |
| `network` | Text bounding-box alignment connectivity graph | Complex borderless tables; stronger than stream |
| `hybrid` | Network (text) + Lattice (lines) combined | Partially-ruled tables; best of both |
| `ml` | Table Transformer neural model for structure | Dense borderless tables; scanned PDFs with OCR |
| `auto` | Per-page probe: lattice or network | Mixed documents (cover pages + ruled tables) |

## per_page

Override kwargs for specific pages. Keys are 1-indexed page numbers (int or str):

```python
tables = camelot.read_pdf(
    "report.pdf",
    pages="1-3",
    flavor="stream",
    split_text=True,
    per_page={
        2: {"table_areas": ["120,210,400,90"]},
        "3": {"flavor": "lattice", "split_text": False},
    },
)
```

Page 1: global `stream` + `split_text=True`. Page 2: same + `table_areas`. Page 3: overrides to `lattice` + `split_text=False`.

## parallel and cpu_count

```python
# Use all cores
tables = camelot.read_pdf("long.pdf", pages="all", parallel=True)

# Cap at 4 workers
tables = camelot.read_pdf("long.pdf", pages="all", parallel=True, cpu_count=4)
```

`cpu_count` is clamped to `[1, multiprocessing.cpu_count()]`. Ignored when `parallel=False`.

## layout_kwargs

Dict of `playa.miner.LAParams` kwargs for fine-tuning text layout analysis. Mirrors PDFMiner.six's `LAParams`:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    layout_kwargs={
        "char_margin": 10.0,   # character grouping margin
        "line_margin": 0.5,    # line grouping margin
        "word_margin": 0.1,    # word grouping margin
        "detect_vertical": False,
    },
)
```

## strip_text

Two modes:

```python
# Per-character: strips any of ' ', '.', '\n' wherever they appear
camelot.read_pdf("doc.pdf", strip_text=" .\n")

# Per-substring: strips only the literal markers '[1]', '[2]'
camelot.read_pdf("doc.pdf", strip_text=["[1]", "[2]"])
```

## replace_text

Dict mapping substrings to replacements. Applied to every cell before assignment. Keys are literal (regex metacharacters escaped). Longest match wins. Empty keys ignored.

```python
camelot.read_pdf("doc.pdf", replace_text={
    " \n": " ",       # fix soft line breaks
    "kw": "kW",       # normalise units
    "kva": "kVA",
})
```

Stripping runs first, then replacement.

## suppress_stdout

When `True`, all logs and warnings are silenced. Useful in production pipelines where verbose output is unwanted.

## debug

When `True`, enables debug logging for troubleshooting extraction issues.

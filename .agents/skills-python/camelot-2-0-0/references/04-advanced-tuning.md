# Advanced Tuning Reference

Per-page overrides, table area specification, column separators, text processing, and layout tuning.

## per_page Overrides

Override any `read_pdf()` kwarg for specific pages:

```python
tables = camelot.read_pdf(
    "report.pdf",
    pages="1-5",
    flavor="stream",
    split_text=True,
    per_page={
        2: {"table_areas": ["120,210,400,90"]},
        3: {"flavor": "lattice"},
        "4": {"split_text": False, "columns": ["100,200,300"]},
    },
)
```

- Keys are 1-indexed page numbers (int or str)
- Values are dicts of any kwarg valid for `read_pdf()`
- Unknown kwargs/flavors raise errors naming the offending page
- `flavor="auto"` is only valid as the global flavor, not per-page

## table_areas

Specify exact table boundaries in PDF coordinate space:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    table_areas=["316,499,566,337"],  # x1,y1,x2,y2
)
```

Format: `"x1,y1,x2,y2"` where (x1, y1) is top-left and (x2, y2) is bottom-right. PDF coordinates have origin at bottom-left, y increasing upward.

Use `camelot.plot(table, kind="text")` to find coordinates by hovering over the rendered image.

## table_regions

Approximate regions where tables may exist (different from exact `table_areas`):

```python
tables = camelot.read_pdf(
    "doc.pdf",
    table_regions=["170,370,560,270"],
)
```

Camelot analyzes only within these regions for table detection. Useful when tables are in approximate but not exact locations.

## columns (Stream/Network/Hybrid)

Explicit column separator x-coordinates:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    flavor="stream",
    columns=["72,95,209,327,442,529,566,606,683"],
)
```

When multiple `table_areas` are specified, the `columns` list must have the same length. Use an empty string `""` for areas where auto-detection is sufficient:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    flavor="stream",
    table_areas=["12,54,43,23", "20,67,55,33"],
    columns=["10,120,200,400", ""],  # explicit for first, auto for second
)
```

## split_text

Split text that was merged across cells by the PDF layout engine:

```python
tables = camelot.read_pdf("doc.pdf", flavor="stream", split_text=True)
```

Useful when PDF text extraction merges adjacent words into a single cell.

## flag_size

Flag superscripts and subscripts with `<s></s>` tags based on font size:

```python
tables = camelot.read_pdf("doc.pdf", flavor="stream", flag_size=True)
# "24.91" becomes "24.91<s>2</s>" for superscript 2
```

## strip_text

Remove unwanted characters or substrings from cell text:

```python
# Per-character mode: strips any of ' ', '.', '\n'
tables = camelot.read_pdf("doc.pdf", strip_text=" .\n")

# Per-substring mode: strips only '[1]' and '[2]' literally
tables = camelot.read_pdf("doc.pdf", strip_text=["[1]", "[2]"])
```

Per-character mode (string): every character in the string is removed wherever it appears. Per-substring mode (list): whole substrings are removed as units.

## replace_text

Rewrite substrings in cell text. Applied after `strip_text`:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    replace_text={
        " \n": " ",       # fix soft line breaks
        "kw": "kW",       # normalise units
        "kva": "kVA",
    },
)
```

- Keys are matched as literal substrings (regex metacharacters escaped)
- Longest match wins when keys overlap
- Empty keys are ignored
- Works with every flavor

## layout_kwargs

Fine-tune the playa PDFMiner-compatible layout engine:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    layout_kwargs={
        "detect_vertical": False,
        "char_margin": 10.0,
        "line_margin": 0.5,
        "word_margin": 0.1,
    },
)
```

`playa.miner` mirrors `pdfminer.six`'s `LAParams`. See the [PDFMiner.six docs](https://pdfminersix.rtfd.io/en/latest/reference/composable.html) for parameter descriptions.

## Memory Management for Long PDFs

Process in chunks to avoid holding all pages in memory:

```python
import camelot

def extract_in_chunks(filepath, total_pages, chunk_size=50, **kwargs):
    for start in range(1, total_pages + 1, chunk_size):
        end = min(start + chunk_size - 1, total_pages)
        tables = camelot.read_pdf(
            filepath, pages=f"{start}-{end}", **kwargs
        )
        tables.export(f"tables_{start}-{end}.csv")
        # Each TableList becomes unreachable after export,
        # so intermediate state is freed between chunks
```

Combine with `flavor="stream"` or `flavor="network"` (cheaper than lattice's image conversion) where the table layouts allow it.

## edge_tol (Stream)

Tolerance for extending textedges vertically. Increase when text is far apart and automatic table detection fails:

```python
# Default (50) may miss tables with wide vertical gaps
tables = camelot.read_pdf("doc.pdf", flavor="stream", edge_tol=500)
```

Use `camelot.plot(table, kind="contour")` to visualize detected table areas and tune `edge_tol`.

## row_tol (Stream)

Tolerance for combining text vertically into rows. Decrease to group rows more tightly:

```python
tables = camelot.read_pdf("doc.pdf", flavor="stream", row_tol=10)
```

## shift_text (Lattice)

Control text flow direction in spanning cells:

```python
# Default: left then top
tables = camelot.read_pdf("doc.pdf", shift_text=['l', 't'])

# No shifting (text stays in place)
tables = camelot.read_pdf("doc.pdf", shift_text=[''])

# Right then bottom
tables = camelot.read_pdf("doc.pdf", shift_text=['r', 'b'])
```

Options: `''` (no shift), `'l'` (left), `'r'` (right), `'t'` (top), `'b'` (bottom). Applied in order.

## copy_text (Lattice)

Copy text into empty spanning cells:

```python
# Copy vertically (fill empty cells below a spanning cell)
tables = camelot.read_pdf("doc.pdf", copy_text=['v'])

# Copy horizontally (fill empty cells to the right)
tables = camelot.read_pdf("doc.pdf", copy_text=['h'])

# Both directions
tables = camelot.read_pdf("doc.pdf", copy_text=['v', 'h'])
```

Iterates until stable (handles 2D spans where cells span both directions).

# Table Objects Reference

`Table`, `TableList`, and `Cell` — the core data structures.

## Table

Represents a single extracted table with coordinates in PDF coordinate space (origin bottom-left, y increasing upward).

### Construction

Tables are created by parsers, not directly. Access via `TableList` indexing:

```python
tables = camelot.read_pdf("doc.pdf")
table = tables[0]
```

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `table.df` | `pd.DataFrame` | Extracted data as pandas DataFrame |
| `table.shape` | `tuple` | `(nrows, ncols)` |
| `table.accuracy` | `float` | Cell-to-structure alignment accuracy (0-100) |
| `table.whitespace` | `float` | Percentage of empty cells (0-100) |
| `table.confidence` | `float` | Unified quality score: `(accuracy/100) * (1 - whitespace/100)`, range [0, 1] |
| `table.filename` | `str` | Source PDF path |
| `table.page` | `int` | 1-based page number |
| `table.order` | `int` | 1-based table index on page |
| `table.rotation` | `str` | Page rotation info |
| `table.flavor` | `str` | Parser flavor used |
| `table.pdf_size` | `tuple` | `(width, height)` in PDF points |
| `table._bbox` | `tuple` | Bounding box `(x0, y0, x1, y1)` in PDF coords |
| `table.cells` | `list[list[Cell]]` | 2D grid of Cell objects |
| `table.cols` | `list[tuple]` | Column x-coordinate tuples |
| `table.rows` | `list[tuple]` | Row y-coordinate tuples |

### parsing_report

```python
print(table.parsing_report)
# {
#     'accuracy': 99.02,
#     'whitespace': 12.24,
#     'order': 1,
#     'page': 1,
#     'confidence': 0.87
# }
```

### Export Methods

```python
# Single table export
table.to_csv("output.csv")
table.to_json("output.json")
table.to_excel("output.xlsx")
table.to_html("output.html")
table.to_markdown("output.md")
table.to_sqlite("output.sqlite")
```

Each method forwards kwargs to the corresponding pandas method (e.g., `to_csv` kwargs go to `DataFrame.to_csv`).

### Export Defaults

- `to_csv`: `encoding="utf-8"`, `index=False`, `header=False`, `quoting=1`
- `to_excel`: `index=False`, `header=False` (v2.0 change — matches CSV behavior)
- `to_json`: `orient="records"`
- `to_sqlite`: `if_exists="replace"`, `index=False`

### Spanning Cell Methods

```python
# Copy text in spanning cells
table.copy_spanning_text(copy_text=['v'])   # vertical copy
table.copy_spanning_text(copy_text=['h'])   # horizontal copy
table.copy_spanning_text(copy_text=['v', 'h'])  # both
```

### Image Access

```python
# Get the rendered page image (requires lattice flavor)
img = table.get_pdf_image()  # returns numpy array (BGR)
```

## TableList

List of `Table` objects with convenience methods.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tables.n` | `int` | Number of tables |
| `tables[0]` | `Table` | Index access |

### Iteration

```python
for table in tables:
    print(table.parsing_report)
```

### filter()

Post-extraction quality filtering. Returns a new `TableList` (original unchanged). Composable:

```python
# Keep tables with at least 2 rows and 2 columns
real = tables.filter(min_rows=2, min_columns=2)

# Quality-based filtering
good = tables.filter(min_accuracy=90, max_whitespace=50)

# Chained filtering
result = tables.filter(min_rows=2).filter(min_accuracy=85)
```

Parameters:
- `min_rows` (default: 1) — drop tables with fewer rows
- `min_columns` (default: 1) — drop tables with fewer columns
- `min_accuracy` (default: 0.0) — drop tables below this accuracy (0-100)
- `max_whitespace` (default: 100.0) — drop tables above this whitespace (0-100)

### stack_contiguous()

Stitch tables that span multiple pages into single logical tables:

```python
# By column count (default)
stitched = tables.stack_contiguous(match="column_count")

# By matching first row (header)
stitched = tables.stack_contiguous(match="first_row", keep_first_header=False)
```

- `match="column_count"` — same column count = continuation
- `match="first_row"` — same column count AND identical first row text
- `keep_first_header` — when `match="first_row"`, drop repeated headers (default: drop them)

The stacked table's geometry is preserved via y-shift; `page` and `order` come from the first table; quality metrics are mean-aggregated.

### export()

Export all tables at once:

```python
# Export as CSV (creates file-page-P-table-T.csv)
tables.export("output.csv")

# Export as Excel
tables.export("output.xlsx", f="excel")

# Compress into ZIP
tables.export("output.csv", compress=True)  # creates output.zip
```

Format shorthand: `f="csv"`, `f="excel"`, `f="html"`, `f="json"`, `f="markdown"`, `f="sqlite"`.

Output filename template: `<stem>-page-<P>-table-<T>.<ext>`.

## Cell

Individual cell in a table.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `cell.text` | `str` | Cell text content |
| `cell.x1, cell.y1` | `float` | Left-bottom corner (PDF coords) |
| `cell.x2, cell.y2` | `float` | Right-top corner (PDF coords) |
| `cell.left, cell.right, cell.top, cell.bottom` | `bool` | Whether cell is bounded on each side |
| `cell.hspan` | `bool` | Whether cell spans horizontally |
| `cell.vspan` | `bool` | Whether cell spans vertically |
| `cell.bound` | `int` | Number of bounded sides (0-4) |

### Spanning Detection

```python
# Check if a cell spans
if cell.hspan:
    print("Cell spans horizontally")
if cell.vspan:
    print("Cell spans vertically")
```

A cell spans horizontally when it lacks a left or right boundary; vertically when it lacks a top or bottom boundary.

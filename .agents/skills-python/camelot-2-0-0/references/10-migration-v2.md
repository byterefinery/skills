# Migration to v2.0 Reference

Breaking changes and new features when upgrading from Camelot 1.x to 2.0.

## Breaking Changes

### Python 3.10+ Required

Python 3.9 (EOL October 2025) is no longer supported. Minimum is now **Python 3.10**.

### line_scale Default is 15

The CLI and docstring used to say the default was 40, but the Lattice parser always defaulted to 15. Docs now match implementation. If you relied on 40, set it explicitly:

```python
camelot.read_pdf("file.pdf", flavor="lattice", line_scale=40)
```

### Table.to_excel Drops Index/Header by Default

`Table.to_excel` now defaults to `index=False, header=False` to match `Table.to_csv`. Opt back in:

```python
table.to_excel("out.xlsx", index=True, header=True)
```

### TableList Materialises Input

`TableList(...)` now consumes an iterable into a list at construction. A generator passed in is exhausted immediately rather than at first access.

### PDFHandler.pages is a Property

`PDFHandler.pages` is now a lazily-resolved property (was an attribute). Only code that *set* it after subclassing is affected.

### PDF Backend: playa-pdf

Backend moved from `pypdf` + `pdfminer.six` to `playa-pdf`: smaller install, more accurate encrypted-PDF handling, faster hot paths. `pdfminer.six` is no longer a direct dependency — `playa.miner` exposes a PDFMiner-compatible layout API.

### Default Lattice Engine: "combined"

`flavor="lattice"` now defaults to `engine="combined"` (raster + vector lines). Safe by construction — never worse than old `"raster"` default. Pass `engine="raster"` for exact pre-2.0 behavior.

## New Features

### flavor="ml" — Neural Backend

Optional Table Transformer backend for borderless and scanned tables:

```bash
pip install "camelot-py[ml]"        # borderless
pip install "camelot-py[ml,ocr]"    # + scanned PDFs
```

```python
tables = camelot.read_pdf("report.pdf", flavor="ml")
```

### flavor="auto" — Per-Page Detection

Auto-detects `lattice` or `network` per page:

```python
tables = camelot.read_pdf("report.pdf", flavor="auto")
# UserWarning reports per-page choices
```

### TableList.filter()

Post-extraction quality filtering:

```python
real = tables.filter(min_rows=2, min_columns=2)
good = tables.filter(min_accuracy=90, max_whitespace=50)
```

### Table.confidence

Unified `[0, 1]` quality score in `parsing_report`:

```python
print(table.confidence)  # 0.87
```

### per_page Overrides

Per-page parameter overrides:

```python
tables = camelot.read_pdf(
    "report.pdf",
    pages="1-3",
    flavor="stream",
    per_page={2: {"table_areas": ["120,210,400,90"]}},
)
```

### replace_text

Substring replacement in cell text:

```python
tables = camelot.read_pdf("doc.pdf", replace_text={" \n": " "})
```

### List-form strip_text

Strip whole substrings (not just individual characters):

```python
tables = camelot.read_pdf("doc.pdf", strip_text=["[1]", "[2]"])
```

### In-Memory Bytes Input

```python
camelot.read_pdf(pdf_bytes)
camelot.read_pdf(io.BytesIO(pdf_bytes))
```

### cpu_count Cap

Bound parallel worker count:

```python
tables = camelot.read_pdf("long.pdf", pages="all", parallel=True, cpu_count=4)
```

### engine="vector"

Render-free line detection from PDF vector graphics:

```python
tables = camelot.read_pdf("doc.pdf", flavor="lattice", engine="vector")
```

### TableList.stack_contiguous()

Multi-page table stitching:

```python
stitched = tables.stack_contiguous(match="column_count")
stitched = tables.stack_contiguous(match="first_row", keep_first_header=False)
```

### erode_iterations

Morphological closing for lattice:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    flavor="lattice",
    iterations=1,
    erode_iterations=1,
)
```

## Migration Checklist

- [ ] Upgrade to Python 3.10+
- [ ] Check `line_scale` — if relying on documented-but-unimplemented 40, set explicitly
- [ ] Check `to_excel` — add `index=True, header=True` if you need them
- [ ] Check `engine` — if relying on exact pre-2.0 raster behavior, pass `engine="raster"`
- [ ] Review `parsing_report` — now includes `confidence` field
- [ ] Test encrypted PDFs — `playa-pdf` may enforce extraction permissions differently
- [ ] Consider `flavor="auto"` for mixed documents
- [ ] Consider `TableList.filter()` for quality-based table selection

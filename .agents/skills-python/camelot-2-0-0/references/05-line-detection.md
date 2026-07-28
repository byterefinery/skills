# Line Detection Reference

Lattice flavor line detection engines, parameters, and tuning.

## Engine Modes

The `engine` parameter controls how ruled lines are detected:

### "combined" (default)

Raster OpenCV detection **plus** PDF native vector line union.

```python
tables = camelot.read_pdf("doc.pdf", flavor="lattice", engine="combined")
```

- Raster detection always runs first (same as `"raster"`)
- Vector lines from the PDF's native graphics are read and unioned into the line mask
- Tables whose rules render faintly (anti-aliased vector strokes) are still found
- Safe: vector lines can only add to the result, never remove
- Same output as `"raster"` on PDFs where raster already detects all lines cleanly

### "raster"

OpenCV line detection on the rendered page image only.

```python
tables = camelot.read_pdf("doc.pdf", flavor="lattice", engine="raster")
```

- Pre-2.0 behavior
- Works well for scanned or image-based tables
- May miss faintly-rendered vector lines

### "vector"

Pure vector line detection from the PDF's native graphics, skipping rasterisation entirely.

```python
tables = camelot.read_pdf("doc.pdf", flavor="lattice", engine="vector")
```

- Fastest engine (no page render, no OpenCV)
- Only works on PDFs with real vector ruled lines
- Pages without vector lines yield no tables
- Good for known vector-ruled documents where speed matters

## line_scale

Controls the minimum line size that gets detected:

```python
# Default (15) — detects most reasonable lines
tables = camelot.read_pdf("doc.pdf", line_scale=15)

# Larger value detects smaller lines
tables = camelot.read_pdf("doc.pdf", line_scale=40)
```

- Default: 15 (v2.0 corrected docs to match implementation)
- Larger = detects smaller lines
- Warning: values >150 may detect text as lines

## iterations and erode_iterations

Morphological operations to close gaps in ruled lines:

```python
# Dilation only (legacy behavior)
tables = camelot.read_pdf("doc.pdf", iterations=1)

# Morphological closing (dilate then erode)
tables = camelot.read_pdf(
    "doc.pdf",
    iterations=1,
    erode_iterations=1,
)
```

- `iterations` — number of dilation passes to bridge gaps in line mask
- `erode_iterations` — erosion passes after dilation (default: 0)
- Setting `erode_iterations` equal to `iterations` performs a morphological closing: gaps are bridged without thickening the overall line mask, avoiding spurious extra rows

## process_background

Detect lines in the background layer:

```python
tables = camelot.read_pdf("doc.pdf", process_background=True)
```

Some PDFs draw table lines in the background (behind text). By default, only foreground lines are detected. Enable this when tables have background lines.

## threshold_blocksize and threshold_constant

OpenCV adaptive thresholding parameters:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    threshold_blocksize=15,   # neighborhood size (3, 5, 7, ...)
    threshold_constant=-2,    # constant subtracted from mean
)
```

- `threshold_blocksize` — pixel neighborhood used to calculate threshold value
- `threshold_constant` — subtracted from the mean; normally positive but can be zero or negative

## line_tol and joint_tol

Tolerance parameters for line merging and joint detection:

```python
tables = camelot.read_pdf(
    "doc.pdf",
    line_tol=2,    # tolerance for merging close vertical/horizontal lines
    joint_tol=2,   # tolerance for joint proximity detection
)
```

- `line_tol` — how close two lines must be to be considered the same line
- `joint_tol` — how close a line endpoint must be to a cell corner to be considered a joint

## backend

Image conversion backend for PDF-to-image rendering:

```python
# Default: pdfium
tables = camelot.read_pdf("doc.pdf", backend="pdfium")

# Ghostscript (requires ghostscript system package + camelot-py[ghostscript])
tables = camelot.read_pdf("doc.pdf", backend="ghostscript")

# Poppler (requires poppler system package)
tables = camelot.read_pdf("doc.pdf", backend="poppler")

# Custom backend
class MyBackend:
    def convert(pdf_path, png_path):
        # custom conversion logic
        pass

tables = camelot.read_pdf("doc.pdf", backend=MyBackend())
```

- `pdfium` (default since v1.0.0) — fast, pure Python install
- `ghostscript` — alternative, may handle some edge cases differently
- `poppler` — another alternative
- Custom class with `convert(pdf_path, png_path)` method

## resolution

PDF-to-PNG rendering DPI:

```python
tables = camelot.read_pdf("doc.pdf", resolution=300)  # default
tables = camelot.read_pdf("doc.pdf", resolution=150)  # faster, lower quality
tables = camelot.read_pdf("doc.pdf", resolution=600)  # higher quality, slower
```

Default: 300 DPI. Higher resolution improves line detection quality but increases processing time.

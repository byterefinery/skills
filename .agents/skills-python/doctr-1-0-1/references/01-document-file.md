# DocumentFile — Reading Documents

`DocumentFile` is the entry point for loading documents into docTR. It converts PDFs, images, and web pages into lists of numpy arrays (H×W×3 RGB uint8) that can be passed to predictors.

## Methods

### `DocumentFile.from_pdf(file, scale=2, rgb_mode=True, password=None, **kwargs)`

Rasterize a PDF to numpy arrays using `pypdfium2`.

- **`file`** — path string, Path, or binary stream
- **`scale`** — rendering multiplier (1 = 72 DPI, default 2 = 144 DPI). Increase for small text.
- **`rgb_mode`** — if True (default), output is RGB; if False, BGR
- **`password`** — password for encrypted PDFs
- **`**kwargs`** — passed to `pypdfium2.PdfPage.render()`

```python
from doctr.io import DocumentFile

# Basic PDF
pages = DocumentFile.from_pdf("doc.pdf")

# Higher DPI for small text
pages = DocumentFile.from_pdf("fine_print.pdf", scale=3)

# Encrypted PDF
pages = DocumentFile.from_pdf("secure.pdf", password="secret")

# BGR mode (for OpenCV compatibility)
pages = DocumentFile.from_pdf("doc.pdf", rgb_mode=False)
```

### `DocumentFile.from_images(files, **kwargs)`

Read image files as numpy arrays.

- **`files`** — single path string/Path/bytes, or a sequence of those
- **`**kwargs`** — passed to the image reader (Pillow-based)

```python
# Single image
pages = DocumentFile.from_images("page.jpg")

# Multiple images (multi-page document)
pages = DocumentFile.from_images(["page1.png", "page2.png", "page3.jpg"])

# From bytes
pages = DocumentFile.from_images(image_bytes)
```

Supported image formats: JPEG, PNG, BMP, TIFF, WebP (whatever Pillow supports).

### `DocumentFile.from_url(url, **kwargs)`

Convert a web page to PDF via `weasyprint`, then rasterize.

- **`url`** — URL of the web page
- **`**kwargs`** — passed to `pypdfium2.PdfPage.render()`

Requires `weasyprint` (`pip install weasyprint`) and its system dependencies (Pango, etc.).

```python
pages = DocumentFile.from_url("https://example.com/article")
```

## Return Format

All methods return `list[np.ndarray]` — a list of numpy arrays, one per page. Each array has shape `(H, W, 3)` with dtype `uint8` and values in `[0, 255]`. Pass this list directly to a predictor.

## Reading Module

The `doctr.io` module also exposes lower-level functions:

- `read_pdf(file, ...)` — same as `DocumentFile.from_pdf()`, returns list of arrays
- `read_html(url)` — convert URL to PDF bytes (needs weasyprint)

## Gotchas

- **PDF scale matters** — default `scale=2` (144 DPI) works for most documents. For fine print, forms, or receipts, use `scale=3` or `scale=4`. Higher scale increases memory and processing time.
- **`from_images()` accepts single or list** — passing a single string still returns a list with one element.
- **Binary streams work** — all methods accept `bytes` or file-like objects, not just paths.
- **`from_url()` is slow** — weasyprint renders the full page to PDF, then pypdfium2 rasterizes. For dynamic content (JS-rendered), consider using a headless browser instead.
- **Password-protected PDFs** — pass `password` to `from_pdf()`. If the password is wrong, pypdfium2 raises an error.

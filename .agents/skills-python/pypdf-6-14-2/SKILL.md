---
name: pypdf-6-14-2
description: >
  pypdf 6.14.2 — pure-Python PDF library for reading, writing, splitting, merging,
  cropping, and transforming PDF files. Use when extracting text or images from
  PDFs, creating new PDFs, merging/splitting documents, adding passwords (encryption),
  adding attachments, form fields, annotations, outlines (bookmarks), JavaScript,
  or manipulating page layouts. Supports PdfReader (read), PdfWriter (write),
  PageObject (page manipulation), Transformation (affine transforms), PageRange
  (page slicing), PaperSize (standard dimensions), and annotation types
  (Highlight, FreeText, Rectangle, Ellipse, Polygon, PolyLine, Line, Text, Link).
  Optional Pillow dependency for image extraction. Trigger on: pypdf, PdfReader,
  PdfWriter, PDF text extraction, PDF merge, PDF split, PDF encryption,
  PDF annotations, PDF form fields, PDF outlines, PDF images extraction,
  PDF page transformation, PDF metadata.
license: BSD-3-Clause
compatibility: >
  Python 3.9+. Pure Python — no system dependencies. Pillow required for
  image extraction (page.images). For AES encryption/decryption, install
  pypdf[crypto] extra. Optional cryptography package improves encryption.
metadata:
  tags:
    - python
    - pdf
    - document-processing
    - text-extraction
---

# pypdf 6.14.2

## Overview

pypdf is a pure-Python PDF library with no C dependencies. Version 6.14.2 supports Python 3.9+ and provides comprehensive read/write capabilities.

**Core classes:**
- **PdfReader** — read PDFs; access pages, metadata, outlines, attachments, encryption
- **PdfWriter** — create/modify PDFs; add pages, encrypt, attach files, add outlines, JavaScript
- **PageObject** — individual page; extract text/images, merge pages, apply transformations
- **Transformation** — affine transforms (scale, rotate, translate, skew) for page content
- **DocumentInformation** — PDF metadata (title, author, subject, keywords, creator, producer)
- **PageRange** — slice-like page range parsing (e.g., `"0:3"`, `"::2"`, `"-1"`)
- **PaperSize** — standard paper dimensions (A0–A8, C4) in pixels at 72 ppi

**Key capabilities:**
- **Text extraction** — `page.extract_text()` with plain and layout modes
- **Image extraction** — `page.images` virtual list (requires Pillow)
- **Page manipulation** — merge, rotate, transform, scale, crop
- **Document composition** — clone, append pages, add blank pages
- **Encryption** — read encrypted PDFs, write with passwords (RC4, AES)
- **Annotations** — Highlight, FreeText, Rectangle, Ellipse, Polygon, PolyLine, Line, Text, Link
- **Form fields** — read/update form field values, reattach fields
- **Attachments** — embed arbitrary files into PDFs
- **Outlines** — add bookmarks/outline items
- **Metadata** — read/write document info dictionary and XMP

## Usage

```python
from pypdf import PdfReader, PdfWriter, Transformation, PageRange, PaperSize

# --- Read PDF ---
reader = PdfReader("input.pdf")
print(f"Pages: {len(reader.pages)}")
text = reader.pages[0].extract_text()

# --- Extract text with layout mode ---
text = reader.pages[0].extract_text(extraction_mode="layout")

# --- Extract images (requires Pillow) ---
for img in reader.pages[0].images:
    with open(f"{img.name}", "wb") as f:
        f.write(img.data)

# --- Merge PDFs ---
writer = PdfWriter()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    reader = PdfReader(path)
    writer.append_pages_from_reader(reader)
writer.write("merged.pdf")

# --- Clone a document (preserves outlines, annotations, etc.) ---
writer = PdfWriter(clone_from="input.pdf")
# or:
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))
writer.write("cloned.pdf")

# --- Select pages with PageRange ---
reader = PdfReader("input.pdf")
range = PageRange("0:5")  # first 5 pages
for i in range(*range.indices(len(reader.pages))):
    print(reader.pages[i].extract_text())

# --- Split PDF ---
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    writer.write(f"page_{i}.pdf")

# --- Rotate and transform pages ---
page = reader.pages[0]
page.rotate(90)  # rotate in place
page.add_transformation(Transformation().scale(2, 2))
page.add_transformation(Transformation().translate(100, 100))

# --- Encrypt PDF ---
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))
writer.encrypt("user_password", "owner_password", algorithm="AES-256")
writer.write("encrypted.pdf")

# --- Decrypt PDF ---
reader = PdfReader("encrypted.pdf")
reader.decrypt("password")
text = reader.pages[0].extract_text()

# --- Add attachment ---
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))
writer.add_attachment("data.txt", "file content here")
writer.write("with_attachment.pdf")

# --- Add outline (bookmark) ---
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))
writer.add_outline_item("Chapter 1", 0)  # (title, page_number)
writer.add_outline_item("Section 1.1", 1, parent="Chapter 1")
writer.write("with_outlines.pdf")

# --- Add metadata ---
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))
writer.add_metadata({
    "/Title": "My Document",
    "/Author": "Jane Doe",
    "/Subject": "Report",
})
writer.write("with_metadata.pdf")

# --- Remove images or text from pages ---
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))
writer.remove_images()
# writer.remove_text()  # removes all text content streams
writer.write("no_images.pdf")

# --- Remove links or annotations ---
writer.remove_links()
writer.remove_annotations()

# --- Read metadata ---
reader = PdfReader("input.pdf")
meta = reader.metadata
if meta:
    print(meta.title, meta.author, meta.subject)

# --- Paper sizes ---
from pypdf import PaperSize
width, height = PaperSize.A4  # (595, 842) at 72 ppi
writer.add_blank_page(width, height)

# --- Reader as context manager ---
with PdfReader("input.pdf") as reader:
    for page in reader.pages:
        print(page.extract_text())
```

## Gotchas

- **`extract_text()` quality varies by PDF** — text extraction depends on how the PDF was generated. Scanned PDFs require OCR (not built into pypdf). Layout mode (`extraction_mode="layout"`) handles complex layouts better but ignores `orientations`, `space_width`, and `visitor_*` parameters.
- **`page.images` requires Pillow** — accessing `page.images` without Pillow raises `ImportError`. Install with `pip install Pillow` or `pip install pypdf[crypto]` (which includes Pillow).
- **`PdfWriter(clone_from=...)` vs `clone_document_from_reader()`** — `clone_from` is a constructor convenience; `clone_document_from_reader()` clones into an existing writer. Both preserve outlines, annotations, and named destinations.
- **`append_pages_from_reader()` vs `clone_document_from_reader()`** — `append_pages_from_reader()` copies pages only; `clone_document_from_reader()` clones the full document structure (outlines, annotations, etc.). Use `clone_document_from_reader()` for faithful copies.
- **`PdfWriter()` starts empty** — a new PdfWriter has no pages. Add pages with `add_page()`, `add_blank_page()`, or `clone_document_from_reader()`.
- **`encrypt()` on writer, `decrypt()` on reader** — encryption is applied when writing; decryption is applied when reading. Use `writer.encrypt(user_pw, owner_pw)` and `reader.decrypt(password)`.
- **`encrypt()` algorithms** — supported: `"RC4-40"`, `"RC4-128"`, `"AES-128"`, `"AES-256"`, `"AES-256-R5"`. AES requires `cryptography` package (`pip install pypdf[crypto]`). Default is RC4-128.
- **`PageRange` is zero-based** — `PageRange("0")` is the first page, `PageRange("0:3")` is pages 0, 1, 2. Use `range.indices(len(reader.pages))` to get safe Python range.
- **`page.rotate()` is in-place** — it modifies the page directly and returns the page for chaining. Angle must be a multiple of 90.
- **`page.add_transformation()` composes** — each call multiplies the transformation onto the existing CTM. Order matters: `scale().translate()` ≠ `translate().scale()`.
- **`merge_page()` overlays** — `page1.merge_page(page2)` draws page2 on top of page1. Use `merge_transformed_page()` to apply a transformation during merge.
- **`writer.write()` returns `(bool, IO)`** — the return is a tuple of (incremental_update, file_handle). For most uses, ignore the return value.
- **`reader.pages` is a list** — unlike some libraries, `reader.pages` is a full list, not a lazy iterator. `len(reader.pages)` works directly.
- **`metadata` can be None** — `reader.metadata` returns `None` if the PDF has no Info dictionary. Always check before accessing properties.
- **`add_outline_item()` parent is string-based** — parent references use the title string, not an object reference. Duplicate titles can cause ambiguity.
- **`add_metadata()` merges** — calling `add_metadata()` merges into existing metadata; it does not replace. To clear metadata, set fields to empty strings.
- **`remove_images()` / `remove_text()` are destructive** — they modify all pages in the writer. There is no per-page variant.
- **`PdfReader` is not thread-safe** — do not share a single PdfReader across threads. Create one per thread.
- **`strict=True` raises on recoverable errors** — default `strict=False` allows reading malformed PDFs. Use `strict=True` only when you need to detect issues.
- **`decrypt()` returns `PasswordType`** — returns `PasswordType.NONE`, `.USER`, or `.OWNER` indicating which password succeeded. Use this to know if decryption worked.
- **`add_blank_page()` takes width then height** — `add_blank_page(width, height)`, not `(height, width)`. Use `PaperSize.A4` for standard sizes.
- **`writer.append()` is not available** — pypdf uses `append_pages_from_reader()` (plural), not `append()`. The old `PdfMerger` class is deprecated.
- **Form fields: `update_page_form_field_values()` needs dict** — pass `{"field_name": "value"}` mapping. Use `reattach_fields()` after if fields disappear.
- **`xmp_metadata` is separate from `metadata`** — `metadata` is the PDF Info dictionary; `xmp_metadata` is XMP (XML-based). They are independent and may disagree.
- **`open_destination` controls initial page view** — set via `writer.open_destination(page_number_or_destination)` to control which page opens first.
- **`page_layout` controls page arrangement** — use `writer.page_layout = "TwoPageLeft"` or `writer.set_page_layout("SinglePage")`. Valid values: `None`, `"NoLayout"`, `"SinglePage"`, `"OneColumn"`, `"TwoColumnLeft"`, `"TwoColumnRight"`, `"TwoPageLeft"`, `"TwoPageRight"`.

## References

- [01-pdf-reader](references/01-pdf-reader.md) — PdfReader: opening files, pages, metadata, outlines, attachments, decryption, context manager
- [02-pdf-writer](references/02-pdf-writer.md) — PdfWriter: creating documents, adding pages, cloning, encryption, attachments, outlines, writing
- [03-page-object](references/03-page-object.md) — PageObject: text extraction, image extraction, merging, rotation, transformations, rectangles
- [04-transformation](references/04-transformation.md) — Transformation: scale, rotate, translate, skew, compose, apply
- [05-annotations](references/05-annotations.md) — Annotations: Highlight, FreeText, Rectangle, Ellipse, Polygon, PolyLine, Line, Text, Link, Popup
- [06-form-fields](references/06-form-fields.md) — Form fields: reading, updating, reattaching, field types
- [07-metadata-xmp](references/07-metadata-xmp.md) — DocumentInformation, XMP metadata, add_metadata
- [08-page-range-sizes](references/08-page-range-sizes.md) — PageRange parsing, PaperSize constants, parse_filename_page_ranges
- [09-encryption](references/09-encryption.md) — Encryption: algorithms, permissions, PasswordType, decrypt flow
- [10-generic-types](references/10-generic-types.md) — PDF object model: DictionaryObject, ArrayObject, NameObject, StreamObject, RectangleObject
- [11-errors](references/11-errors.md) — Exception hierarchy: PyPdfError, PdfReadError, WrongPasswordError, EmptyFileError, etc.

---
name: pypdf-7-1-1
description: >
  pypdf 7.1.1 — pure-Python PDF library for reading, writing, splitting, merging,
  cropping, and transforming PDF files. Use when extracting text or images from
  PDFs, creating new PDFs, merging/splitting documents with append and merge,
  adding passwords (encryption), attachments, form fields, annotations, outlines
  (bookmarks), JavaScript open actions, or manipulating page layouts. Supports
  PdfReader (read), PdfWriter (write), PageObject (page manipulation),
  Transformation (affine transforms), PageRange (page slicing), PaperSize
  (standard dimensions), and annotation types (FreeText, Text, Line, PolyLine,
  Polygon, Rectangle, Ellipse, Highlight, Link, Popup). Python 3.10+. Optional
  Pillow dependency for image extraction. Triggers on pypdf, PdfReader,
  PdfWriter, PDF text extraction, PDF merge, PDF split, PDF encryption,
  PDF annotations, PDF form fields, PDF outlines, PDF images extraction,
  PDF page transformation, PDF metadata.
license: BSD-3-Clause
compatibility: >
  Python 3.10+. Pure Python — no system dependencies. Pillow required for
  image extraction (page.images), install pypdf[image]. For AES
  encryption/decryption install pypdf[crypto] (cryptography >= 43) or
  pypdf[cryptodome] (pycryptodome). RC4 encryption works with the base install.
metadata:
  tags:
    - python
    - pdf
    - document-processing
    - text-extraction
---

# pypdf 7.1.1

## Overview

pypdf is a pure-Python PDF library with no C dependencies. Version 7.1.1 requires Python 3.10+ (3.9 was dropped in 7.0) and supports PDF 1.0 through PDF 2.0 (AES encryption, CMaps, cross-reference/object streams).

**Core classes:**
- **PdfReader** — read PDFs; pages, metadata, XMP, outlines, attachments, decryption, viewer preferences, form fields
- **PdfWriter** — create/modify PDFs; `append`/`merge` composition, clone, encrypt, attachments, outlines, annotations, open actions
- **PageObject** — individual page; extract text/images, merge pages, rotate, scale, transform
- **Transformation** — affine transforms (scale, rotate, translate) composed via `transform()`
- **DocumentInformation** — PDF Info metadata (title, author, subject, keywords, creator, producer)
- **XmpInformation** — XMP metadata with property-based fields
- **PageRange** — slice-like page range parsing (e.g., `"0:3"`, `"::2"`, `"-1"`)
- **PaperSize** — standard paper dimensions A0–A8 (A4 = 595×842) at 72 ppi
- **Configuration** — global security limits via `apply_configuration` / `overwrite_configuration`

**Key capabilities:**
- **Text extraction** — `page.extract_text()` with plain and layout modes; visitor functions
- **Image extraction** — `page.images` virtual list (requires Pillow)
- **Page composition** — `append()` (concatenate) and `merge()` (insert at position); `add_page()`/`insert_page()` for advanced use
- **Encryption** — read encrypted PDFs; write with RC4-40/RC4-128/AES-128/AES-256-R5/AES-256
- **Annotations** — FreeText, Text, Line, PolyLine, Polygon, Rectangle, Ellipse, Highlight, Link, Popup
- **Form fields** — read/update fields, flatten, reattach fields, group with `add_form_topname`
- **Attachments** — add (returns `EmbeddedFile` with setters), read, delete, PDF/A-3B relationships
- **Outlines** — keyword-only `add_outline_item()` returning the item used as `parent`; Fit view modes
- **Metadata** — Info dictionary (merge/replace/clear) and XMP (create, property fields, raw DOM)
- **Viewer preferences** — `create_viewer_preferences()` + property setters
- **JavaScript** — `add_open_action(JavaScript(...))` from `pypdf.actions`

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
for i, img in enumerate(reader.pages[0].images):
    img.image.save(f"out-image-{i}.png")  # img.name can contain arbitrary chars — sanitize

# --- Merge PDFs (append) ---
writer = PdfWriter()
writer.append("a.pdf")
writer.append(PdfReader("b.pdf"), (0, 3))  # first 3 pages of b
writer.append("c.pdf", pages=PageRange("::2"))  # every second page
writer.write("merged.pdf")

# --- Insert pages at a position (merge) ---
writer = PdfWriter()
writer.merge(position=2, fileobj="insert.pdf", pages=(0, 1))

# --- Clone a document (preserves outlines, annotations, named destinations) ---
writer = PdfWriter(clone_from="input.pdf")
writer.write("cloned.pdf")

# --- Split PDF ---
for i, page in enumerate(PdfReader("input.pdf").pages):
    w = PdfWriter()
    w.add_page(page)
    w.write(f"page_{i}.pdf")

# --- Rotate and transform pages ---
page = reader.pages[0]
page.rotate(90)  # in place, multiple of 90
page.add_transformation(Transformation().scale(sx=2, sy=2))
page.scale_by(0.5)  # scale content + page boxes together

# --- Encrypt PDF ---
writer = PdfWriter(clone_from="input.pdf")
writer.encrypt("user-password", algorithm="AES-256-R5")  # algorithm is keyword-only
writer.write("encrypted.pdf")

# --- Decrypt PDF ---
reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")  # returns PasswordType.NONE/.USER/.OWNER

# --- Add attachment (returns EmbeddedFile with setters) ---
writer = PdfWriter(clone_from="input.pdf")
writer.add_attachment(filename="data.txt", data=b"file content")
writer.write("with_attachment.pdf")

# --- Add outline (keyword-only args; parent is the returned item) ---
writer = PdfWriter(clone_from="input.pdf")
chapter = writer.add_outline_item(title="Chapter 1", page_number=0)
writer.add_outline_item(title="Section 1.1", page_number=1, parent=chapter)
writer.write("with_outlines.pdf")

# --- Metadata: merge into Info dict ---
writer.add_metadata({"/Title": "My Document", "/Author": "Jane Doe"})
# replace everything: writer.metadata = {"...": "..."}
# clear but keep entry: writer.metadata = {}
# remove Info entry: writer.metadata = None

# --- XMP metadata ---
from pypdf.xmp import XmpInformation
xmp = XmpInformation.create()
xmp.dc_title = {"x-default": "My Document Title"}
xmp.pdf_producer = "pypdf"
writer.xmp_metadata = xmp

# --- Fill form fields (use writer's pages) ---
writer = PdfWriter(clone_from="form.pdf")
writer.update_page_form_field_values(
    writer.pages[0], {"fieldname": "value"}, auto_regenerate=False
)
writer.write("filled.pdf")

# --- JavaScript open action ---
from pypdf.actions import JavaScript
writer.add_open_action(JavaScript("this.print({bUI:true});"))

# --- Viewer preferences (create dict first) ---
writer.create_viewer_preferences()
writer.viewer_preferences.fit_window = True
writer.viewer_preferences.direction = "/L2R"

# --- Remove images / text / annotations / links ---
writer.remove_images()  # default ImageType.ALL; booleans deprecated
writer.remove_text()  # optional font_names filter
writer.remove_annotations(subtypes="/Widget")  # None removes all
writer.remove_links()

# --- Paper sizes ---
writer.add_blank_page(width=PaperSize.A4.width, height=PaperSize.A4.height)

# --- Reader as context manager ---
with PdfReader("input.pdf") as reader:
    for page in reader.pages:
        print(page.extract_text())
```

## Gotchas

- **`append()`/`merge()` are the recommended composition API** — `add_page()`/`insert_page()` are for advanced use with `excluded_keys`; `append_pages_from_reader()` is legacy ("`append` should be preferred"). `append(fileobj, outline_item=None, pages=None, ...)` accepts a path, file-like, or PdfReader; `merge(position, fileobj, ...)` inserts *after* page `position`.
- **`add_outline_item()` is keyword-only in 7.x** — positional args are deprecated (removed in 8.0). It returns the outline item (IndirectObject); pass that object as `parent=` for nesting — not the title string as in older versions. Styling: `color` (RGB tuple or hex string), `bold`, `italic`, `fit` (`pypdf.generic.Fit`), `is_open`.
- **`remove_images()` booleans are deprecated** — pass `ImageType.ALL` (default) or a combination of `ImageType.XOBJECT_IMAGES | ImageType.INLINE_IMAGES | ImageType.DRAWING_IMAGES` (from `pypdf.constants`).
- **`encrypt()` takes `algorithm` as keyword-only** — `writer.encrypt(user_pw, owner_pw, use_128bit, permissions_flag, *, algorithm)`. Default is RC4-128 (insecure); docs recommend `AES-256-R5`. AES needs `pypdf[crypto]` (cryptography >= 43) or `pypdf[cryptodome]`; RC4 works with the base install.
- **`extract_text(extraction_mode="layout")` ignores** `orientations`, `space_width`, and all `visitor_*` parameters (warns). Layout-mode kwargs: `layout_mode_space_vertically` (default True), `layout_mode_scale_weight` (default 1.25), `layout_mode_strip_rotated` (default True).
- **Text extraction memory** — parsing a content stream can be very large (10 GB RAM observed for ~300 MB uncompressed streams). Check `len(page.get_contents().get_data())` beforehand if needed.
- **pypdf is not OCR** — scanned PDFs (image-only) yield little or no text. Distinguish digitally-born, scanned, and OCRed PDFs; for scanned files use real OCR (e.g., Tesseract).
- **`page.images` requires Pillow** and returns a `VirtualListImages` — index by int, by name string, or by name-tuple for images inside XObject forms. Iterate for all. Image `.name` values can contain arbitrary characters — sanitize before writing to disk. Iteration raises on the first bad image; for broken PDFs fetch by key inside a try/except loop.
- **`update_page_form_field_values()`** — pass the **writer's** page (or list of pages, or None for all). `auto_regenerate` defaults to True (legacy) which flags viewers to re-render fields and can trigger a "save changes" dialog; use `False`. `flatten=True` converts field contents to page content but does not remove the widgets — follow up with `remove_annotations(subtypes="/Widget")`. Raises `PyPdfError` if the PDF has no `/AcroForm`/`/Fields`.
- **Fields are not copied by `add_page()`** — form field structure lives in the root `/AcroForm`, not in pages. Use `append()` to bring fields along. If field objects are missing, `writer.reattach_fields()` reattaches them from page `/Widget` annotations (cannot recover same-named or intermediate fields).
- **Merging multiple forms with same field names** — call `reader.add_form_topname("form1")` before appending so fields become `form1.field1`.
- **Adding the same page twice shares cloned objects** — second modification affects both copies. Call `writer.reset_translation(reader)` to reset the translation cache.
- **`writer.add_js()` is deprecated** (returns NoReturn) — use `writer.add_open_action(JavaScript(...))` from `pypdf.actions` instead.
- **Viewer preferences dict does not exist by default** — call `writer.create_viewer_preferences()` before setting `writer.viewer_preferences.*` properties. Reading side: `reader.viewer_preferences` is None if absent.
- **`reader.metadata` can be None** — and every property of it can be None. `writer.add_metadata(dict)` merges; assign `writer.metadata = {...}` to replace, `= {}` to clear, `= None` to remove the Info entry.
- **`writer.write()` returns `(bool, IO)`** — (incremental_update, file_handle). Usually ignored.
- **`add_blank_page(width, height)`** — width first, then height; `None` uses the last page's size, but with no pages it raises `PageSizeNotDefinedError`.
- **`PageRange("3")` is one page (the 4th)** — a bare int means a single page, unlike `slice(3)` (first three). Zero step (`::0`) raises `ParseError` (7.1.1). Use `range(*pr.indices(len(reader.pages)))` to materialize.
- **`merge(position=...)` inserts after** the given page number, and `position` is adjusted as pages are inserted.
- **`page.rotate()` is in-place** — returns the page for chaining; angle must be a multiple of 90. Prefer `rotate()` over `add_transformation(Transformation().rotate())` — rotation keeps the page inside the mediabox/cropbox, raw transformations do not.
- **`merge_page()` overlays** — `page.merge_page(other, over=True)` draws `other` on top (use `over=False` for watermarks); `expand=True` grows the page to fit. Combine with `merge_transformed_page(page, Transformation().rotate(45).translate(tx=50))` for transformed stamps. Cropped-looking results usually need `expand=True`.
- **Cropping does not delete content** — box adjustments (mediabox/cropbox) only change the viewbox; cropped content is still in the file and restorable.
- **Rotated pages when merging** — call `page.transfer_rotation_to_content()` before `merge_page` to avoid wrongly rotated results.
- **`PdfWriter(fileobj)` and `clone_from`** — the first positional arg (`fileobj`) or `clone_from` both clone a document; `PdfWriter("input.pdf")` is a full clone. `incremental=True` writes only changes (cannot be combined with `encrypt()`).
- **`strict=False` is the default** — malformed PDFs are read best-effort with warnings; `strict=True` raises. Reader also takes `password=` at open and keyword-only security limits `root_object_recovery_limit` (default 10 000) and `xref_stream_maximum_entries` (default 2 000 000).
- **`decrypt()` returns `PasswordType`** — `.NONE`, `.USER`, or `.OWNER` indicating which password succeeded; passing a `password` to a non-encrypted file raises `PdfReadError`.
- **Attachment names are not unique** — `reader.attachments[name]` is a list of byte strings; sanitize names before writing to disk. `writer.add_attachment()` returns an `EmbeddedFile` with setters (`size`, `alternative_name`, `description`, `subtype`, `checksum`, `modification_date`) and `.delete()`.
- **Global security configuration** — `apply_configuration(...)` is a context manager (resets on exit); `overwrite_configuration(...)` changes it globally. Examples: `maximum_declared_stream_length`.
- **`PdfReader` is not thread-safe** — create one per thread.

## References

- [01-pdf-reader](references/01-pdf-reader.md) — PdfReader: construction, pages, metadata, XMP, outlines, named destinations, page labels, attachments, decryption, viewer preferences
- [02-pdf-writer](references/02-pdf-writer.md) — PdfWriter: construction, clone_from, append/merge, add_page, encryption, attachments, outlines, annotations, open actions, viewer preferences, writing
- [03-page-object](references/03-page-object.md) — PageObject: text extraction (plain/layout, visitors), images, merge_page, rotation, scaling, boxes, page actions
- [04-transformation](references/04-transformation.md) — Transformation: affine matrix, translate/scale/rotate, transform composition, apply_on
- [05-annotations](references/05-annotations.md) — Annotations: FreeText, Text, Line, PolyLine, Polygon, Rectangle, Ellipse, Highlight, Link, Popup; reading annotations
- [06-form-fields](references/06-form-fields.md) — Form fields: get_fields, get_form_text_fields, update_page_form_field_values, flatten, reattach_fields, form top names
- [07-metadata-xmp](references/07-metadata-xmp.md) — DocumentInformation and XmpInformation: read, merge, replace, clear, property fields, raw DOM editing
- [08-page-range-sizes](references/08-page-range-sizes.md) — PageRange syntax and methods, parse_filename_page_ranges, PaperSize constants
- [09-encryption](references/09-encryption.md) — encrypt/decrypt: algorithms, permissions, PasswordType, crypto dependencies
- [10-generic-types](references/10-generic-types.md) — pypdf.generic object model: DictionaryObject, ArrayObject, NameObject, Destination, Fit, RectangleObject, links
- [11-errors](references/11-errors.md) — Exception hierarchy: PyPdfError, PdfReadError, WrongPasswordError, LimitReachedError, PdfReadWarning
- [12-configuration-security](references/12-configuration-security.md) — Configuration, apply_configuration, overwrite_configuration, reader/writer security limits

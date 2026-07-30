# PdfWriter

## Construction

```python
from pypdf import PdfWriter, PdfReader

# Empty writer
writer = PdfWriter()

# Clone from existing PDF (preserves outlines, annotations, named destinations)
writer = PdfWriter(clone_from="existing.pdf")

# Clone from a reader
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("existing.pdf"))

# Context manager
with PdfWriter() as writer:
    writer.add_blank_page(595, 842)
    writer.write("output.pdf")
```

## Adding Pages

```python
writer = PdfWriter()

# Add a blank page
page = writer.add_blank_page(width=595, height=842)
# Returns PageObject

# Insert a blank page at specific position
writer.insert_blank_page(width=595, height=842, index=0)

# Add a page from a reader
reader = PdfReader("input.pdf")
writer.add_page(reader.pages[0])

# Insert a page at specific position
writer.insert_page(reader.pages[0], index=0)

# Append all pages from a reader
writer.append_pages_from_reader(reader)

# Append with callback (e.g., transform each page)
def my_callback(page):
    page.rotate(90)

writer.append_pages_from_reader(reader, after_page_append=my_callback)
```

### Paper sizes

```python
from pypdf import PaperSize

# Standard sizes (width, height in pixels at 72 ppi)
writer.add_blank_page(*PaperSize.A4)   # 595 x 842
writer.add_blank_page(*PaperSize.A3)   # 842 x 1191
writer.add_blank_page(*PaperSize.A5)   # 420 x 595
writer.add_blank_page(*PaperSize.A0)   # 2384 x 3370
```

## Cloning Documents

```python
# Method 1: constructor
writer = PdfWriter(clone_from="input.pdf")

# Method 2: clone method
writer = PdfWriter()
reader = PdfReader("input.pdf")
writer.clone_document_from_reader(reader)

# With callback
writer.clone_document_from_reader(reader, after_page_append=lambda page: page.rotate(90))
```

`clone_document_from_reader()` copies the full document structure including `/Root`, `/Info`, `/ID`, outlines, and annotations.

## Encryption

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Basic encryption (RC4-128 by default)
writer.encrypt("user_password", "owner_password")

# AES-128
writer.encrypt("user_pw", "owner_pw", algorithm="AES-128")

# AES-256
writer.encrypt("user_pw", "owner_pw", algorithm="AES-256")

# AES-256 with revision 5
writer.encrypt("user_pw", "owner_pw", algorithm="AES-256-R5")

# With permissions
from pypdf.constants import UserAccessPermissions as UAP
writer.encrypt(
    "user_pw",
    "owner_pw",
    algorithm="AES-256",
    permissions_flag=~(UAP.MODIFY_DOCUMENT | UAP.PRINT),
)

writer.write("encrypted.pdf")
```

### Supported algorithms

| Algorithm | Description | Extra dependency |
|---|---|---|
| `RC4-40` | 40-bit RC4 (legacy) | None |
| `RC4-128` | 128-bit RC4 (default) | None |
| `AES-128` | AES 128-bit | `cryptography` |
| `AES-256` | AES 256-bit | `cryptography` |
| `AES-256-R5` | AES 256-bit, revision 5 | `cryptography` |

Install with `pip install pypdf[crypto]` for AES support.

### Permission flags

```python
from pypdf.constants import UserAccessPermissions as UAP

# Individual permissions
UAP.PRINT                    # Bit 3
UAP.MODIFY_DOCUMENT          # Bit 4
UAP.MODIFY_ANNOTATIONS       # Bit 5
UAP.FILL_INTERACTIVE_FORMS   # Bit 9
UAP.EXTRACT_TEXT_GRAPHICS    # Bit 10
UAP.MODIFY_ASSEMBY           # Bit 11
UAP.PRINT_HIGH_QUALITY       # Bit 12

# Deny printing and modification
permissions = ~(UAP.PRINT | UAP.MODIFY_DOCUMENT)

# Allow everything
permissions = -1  # all bits set
```

## Attachments

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Add file attachment
embedded = writer.add_attachment("data.txt", "text content here")
# Returns EmbeddedFile

# Add binary attachment
with open("image.png", "rb") as f:
    writer.add_attachment("image.png", f.read())

writer.write("with_attachment.pdf")
```

## Outlines (Bookmarks)

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Add outline item
writer.add_outline_item("Chapter 1", page_number=0)

# Add with parent (string-based reference)
writer.add_outline_item("Chapter 1", page_number=0)
writer.add_outline_item("Section 1.1", page_number=1, parent="Chapter 1")
writer.add_outline_item("Section 1.2", page_number=2, parent="Chapter 1")

# Add from destination object
from pypdf.generic import Destination, Fit
dest = Destination("dest_name", writer.pages[0], Fit.fit())
writer.add_outline_item_destination(dest)

# Build outline from named destinations
writer.add_outline()

# Get outline root
outline_root = writer.get_outline_root()
```

### add_outline_item parameters

| Parameter | Type | Description |
|---|---|---|
| `title` | `str` | Bookmark text |
| `page_number` | `int \| Destination \| PageObject` | Target page (zero-based index) |
| `parent` | `str \| None` | Parent bookmark title (for nesting) |
| `color` | `tuple` | RGB color as `(r, g, b)` floats 0-1 |
| `bold` | `bool` | Bold text |
| `italic` | `bool` | Italic text |
| `closed` | `bool` | Start collapsed |

## JavaScript

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Add JavaScript action (executed on open)
writer.add_js("this.print();")
writer.add_js("this.pageNum = 5;")

writer.write("with_js.pdf")
```

## Metadata

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Add metadata (merges with existing)
writer.add_metadata({
    "/Title": "My Document",
    "/Author": "Jane Doe",
    "/Subject": "Annual Report",
    "/Keywords": "report, annual, 2024",
    "/Creator": "My Application",
    "/Producer": "pypdf 6.14.2",
})

# Read metadata
meta = writer.metadata
print(meta.title)

# Set XMP metadata
writer.xmp_metadata = xmp_bytes  # bytes
writer.xmp_metadata = None  # clear
```

## Page Layout

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Set page layout
writer.set_page_layout("TwoPageLeft")
# or
writer.page_layout = "SinglePage"

# Get current layout
layout = writer.page_layout

# Valid values
# None, "NoLayout", "SinglePage", "OneColumn",
# "TwoColumnLeft", "TwoColumnRight", "TwoPageLeft", "TwoPageRight"
```

## Open Destination (Initial View)

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Open to specific page
writer.open_destination(0)  # page number
writer.open_destination(writer.pages[5])  # PageObject

# Open to destination
from pypdf.generic import Destination, Fit
dest = Destination("", writer.pages[0], Fit.fit())
writer.open_destination(dest)

# Clear open destination
writer.open_destination(None)
```

## Removing Content

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Remove all images from all pages
writer.remove_images()

# Remove all text from all pages
writer.remove_text()

# Remove text from specific fonts
writer.remove_text(font_names=["/Arial"])

# Remove all link annotations
writer.remove_links()

# Remove all annotations
writer.remove_annotations()

# Remove annotations from specific pages
writer.remove_annotations(page_numbers=[0, 1, 2])
```

## Compression

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("input.pdf"))

# Compress identical objects (reduces file size)
deleted = writer.compress_identical_objects()
# Returns list of deleted object references
```

## Writing Output

```python
writer = PdfWriter()
writer.add_blank_page(595, 842)

# Write to file
writer.write("output.pdf")

# Write to path object
from pathlib import Path
writer.write(Path("output.pdf"))

# Write to stream
from io import BytesIO
buffer = BytesIO()
writer.write_stream(buffer)
pdf_bytes = buffer.getvalue()
```

`write()` returns `(bool, IO)` — `(incremental_update, file_handle)`.

## Form Fields

```python
writer = PdfWriter()
writer.clone_document_from_reader(PdfReader("form.pdf"))

# Update form field values
writer.update_page_form_field_values(
    writer.pages[0],
    {"field_name": "new value", "another_field": "value2"},
    flags=1,  # 1 = need appearances
)

# Reattach fields (fix fields that disappear)
writer.reattach_fields()

# Set NeedAppearances
writer.set_need_appearances_writer(True)

# Add form topname
writer.add_form_topname("Form1")

# Rename form topname
writer.rename_form_topname("NewFormName")
```

## Viewer Preferences

```python
from pypdf.generic import ViewerPreferences

prefs = writer.create_viewer_preferences()
prefs.RotatePages = True
prefs.HideToolbar = True
prefs.HideMenubar = True
prefs.HideWindowUI = True
prefs.FitWindow = True
prefs.CenterWindow = True
```

## ObjectDeletionFlag

```python
from pypdf import ObjectDeletionFlag

# Control what gets deleted when removing content
ObjectDeletionFlag.FONT_FILE        # Delete font files
ObjectDeletionFlag.XOBJECT_IMAGE    # Delete XObject images
ObjectDeletionFlag.XOBJECT_FORM     # Delete XObject forms
```

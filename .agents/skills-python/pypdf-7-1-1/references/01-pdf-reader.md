# PdfReader

## Construction

```python
from pypdf import PdfReader

# From file path or Path object
reader = PdfReader("document.pdf")

# From binary stream
from io import BytesIO
reader = PdfReader(BytesIO(pdf_bytes))

# With strict mode (raises on spec violations instead of warning)
reader = PdfReader("document.pdf", strict=True)

# With password (decrypts at open; must match an encrypted file)
reader = PdfReader("encrypted.pdf", password="secret")

# Keyword-only security limits
reader = PdfReader(
    "document.pdf",
    root_object_recovery_limit=10_000,   # default; None disables
    xref_stream_maximum_entries=2_000_000,
)

# Context manager (auto-closes the stream)
with PdfReader("document.pdf") as reader:
    for page in reader.pages:
        print(page.extract_text())

reader.close()  # or use the context manager
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `stream` | `str \| Path \| BinaryIO` | — | File path or binary stream |
| `strict` | `bool` | `False` | Raise on recoverable errors instead of best-effort |
| `password` | `str \| bytes \| None` | `None` | Decrypt at initialization; raises `PdfReadError` if the file is not encrypted |
| `root_object_recovery_limit` | `int \| None` | `10_000` | Max objects read during root recovery in non-strict mode; `None` disables |
| `xref_stream_maximum_entries` | `int` | `2_000_000` | Max cross-reference stream entries |

## Pages

```python
reader = PdfReader("document.pdf")

count = len(reader.pages)           # total page count
page = reader.pages[0]              # zero-based indexing
last = reader.pages[-1]

for i, page in enumerate(reader.pages):
    text = page.extract_text()

reader.get_num_pages()              # same as len(reader.pages)
```

## Metadata (Info dictionary)

```python
reader = PdfReader("example.pdf")
meta = reader.metadata  # DocumentInformation or None

if meta:
    # All of these can be None
    print(meta.title, meta.author, meta.subject)
    print(meta.creator, meta.producer)
    print(meta.creation_date, meta.modification_date)
```

## XMP metadata

```python
meta = reader.xmp_metadata  # XmpInformation or None
if meta:
    print(meta.dc_title)            # e.g. {'x-default': 'PDF Example Document'}
    print(meta.dc_description)
    print(meta.xmp_create_date)
```

## Outlines (bookmarks)

`reader.outline` is a list of `Destination` objects; nested children appear as
lists directly following their parent.

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")

# Top-level items only (skip nested lists)
for outline in reader.outline:
    if isinstance(outline, list):
        continue
    page_number = reader.get_destination_page_number(outline)  # zero-based or None
    print(f"{outline.title} -> page {page_number + 1 if page_number is not None else 'n/a'}")
```

For hierarchical outlines, recurse: an item is a `Destination`, its children
are the `list` entry immediately after it in `reader.outline`.

## Named destinations

```python
reader = PdfReader("document.pdf")
dests = reader.named_destinations  # dict[str, Destination]
for name, dest in dests.items():
    print(name, reader.get_destination_page_number(dest))
```

## Page labels

```python
labels = reader.page_labels  # list[str], e.g. ["1", "2", "i"]
```

## Attachments

`reader.attachments` maps attachment name to a **list** of byte contents
(names may repeat). `reader.attachment_list` yields `EmbeddedFile` objects
(`name`, `alternative_name`, `content`, and other properties).

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for name, content_list in reader.attachments.items():
    for i, content in enumerate(content_list):
        with open(f"out-{i}-{name}", "wb") as fp:  # sanitize name first!
            fp.write(content)

# Object-oriented access
for attachment in reader.attachment_list:
    print(attachment.name, attachment.alternative_name, len(attachment.content))
```

## Encryption / decryption

```python
reader = PdfReader("encrypted-file.pdf")

print(reader.is_encrypted)  # bool
result = reader.decrypt("secret")  # PasswordType.NONE | .USER | .OWNER
text = reader.pages[0].extract_text()
```

## Viewer preferences

```python
vp = reader.viewer_preferences  # ViewerPreferences or None
if vp:
    print(vp.hide_toolbar, vp.direction, vp.non_fullscreen_pagemode)
```

## Form fields

```python
reader = PdfReader("form.pdf")
fields = reader.get_form_text_fields()                    # {name: value}
fields_full = reader.get_form_text_fields(True)           # fully qualified names
all_fields = reader.get_fields()                          # all field types
```

## Context manager / lifecycle

```python
with PdfReader("document.pdf") as reader:
    ...
# __exit__ closes the underlying stream
reader.close()
```

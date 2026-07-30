# PdfReader

## Construction

```python
from pypdf import PdfReader

# From file path
reader = PdfReader("document.pdf")

# From path object
from pathlib import Path
reader = PdfReader(Path("document.pdf"))

# From binary stream
from io import BytesIO
reader = PdfReader(BytesIO(pdf_bytes))

# With strict mode (raises on recoverable errors)
reader = PdfReader("document.pdf", strict=True)

# With password (decrypts at open)
reader = PdfReader("encrypted.pdf", password="secret")

# Context manager (auto-closes file handle)
with PdfReader("document.pdf") as reader:
    for page in reader.pages:
        print(page.extract_text())
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `stream` | `str \| Path \| BinaryIO` | — | File path or stream |
| `strict` | `bool` | `False` | Raise on recoverable errors |
| `password` | `str \| bytes \| None` | `None` | Decrypt at initialization |
| `root_object_recovery_limit` | `int \| None` | — | Max objects to query for root recovery in non-strict mode |

## Pages

```python
reader = PdfReader("document.pdf")

# Total page count
count = len(reader.pages)

# Access by index (zero-based)
page = reader.pages[0]
last_page = reader.pages[-1]

# Iterate
for page in reader.pages:
    text = page.extract_text()

# Iterate with index
for i, page in enumerate(reader.pages):
    print(f"Page {i}: {len(text)} chars")

# Slice
first_three = reader.pages[:3]
```

`reader.pages` returns a `list[PageObject]` — fully materialized, not lazy.

## Metadata

```python
reader = PdfReader("document.pdf")
meta = reader.metadata

if meta:
    # Text properties (decoded, always str or None)
    print(meta.title)
    print(meta.author)
    print(meta.subject)
    print(meta.creator)
    print(meta.producer)
    print(meta.creation_date)   # datetime or None
    print(meta.modification_date)

    # Raw properties (may return ByteStringObject if decoding fails)
    print(meta.author_raw)
    print(meta.title_raw)

    # Access arbitrary keys
    print(meta.get("/CustomKey"))
```

`metadata` returns `DocumentInformation` or `None`.

### DocumentInformation properties

| Property | Raw property | Description |
|---|---|---|
| `title` | `title_raw` | Document title |
| `author` | `author_raw` | Author name |
| `subject` | `subject_raw` | Subject description |
| `keywords` | `keywords_raw` | Comma-separated keywords |
| `creator` | `creator_raw` | Tool that created the document |
| `producer` | `producer_raw` | Tool that produced the PDF |
| `creation_date` | — | Creation timestamp (datetime) |
| `modification_date` | — | Modification timestamp (datetime)

## XMP Metadata

```python
xmp = reader.xmp_metadata

if xmp:
    print(xmp.title)        # list of str (may have multiple language versions)
    print(xmp.creator)
    print(xmp.description)
    print(xmp.modified)
    print(xmp.keywords)     # list of str
    print(xmp.properties)   # dict of all XMP properties
```

XMP metadata is XML-based and separate from the PDF Info dictionary.

## Encryption

```python
reader = PdfReader("encrypted.pdf")

# Check if encrypted
if reader.is_encrypted:
    # Decrypt
    result = reader.decrypt("password")
    # result: PasswordType.NONE | .USER | .OWNER

    # Try with user password
    result = reader.decrypt("user_pw")

    # Try with owner password
    result = reader.decrypt("owner_pw")

from pypdf import PasswordType
if result == PasswordType.NONE:
    print("No password was needed")
elif result == PasswordType.USER:
    print("User password accepted")
elif result == PasswordType.OWNER:
    print("Owner password accepted")
```

`PasswordType` is an `IntEnum`: `NONE=0`, `USER=1`, `OWNER=2`.

## Outlines (Bookmarks)

```python
# Get outline items (list of dicts)
outlines = reader.outlines

for outline in outlines:
    print(outline.title)
    print(outline.page_index)  # page number (zero-based)
    print(outline.children)    # nested outlines
```

## Named Destinations

```python
# Get named destinations
destinations = reader.get_named_destinations()
# Returns dict: {name: Destination}

for name, dest in destinations.items():
    print(name, dest.page_index)
```

## Attachments

```python
# List embedded files
from pypdf.generic import EmbeddedFile

# Access via root
root = reader.root_object
if "/Names" in root and "/EmbeddedFiles" in root["/Names"]:
    # Iterate embedded files
    pass

# Or check reader for attachments
```

## Properties

```python
reader = PdfReader("document.pdf")

# PDF version header
print(reader.pdf_header)  # e.g., "%PDF-1.7"

# Root catalog
root = reader.root_object  # DictionaryObject

# Check encryption
print(reader.is_encrypted)  # bool

# Close file handle
reader.close()
```

## Form Fields (Reader)

```python
# Get form fields
fields = reader.get_form_text_fields()
# Returns dict: {field_name: field_value}

# Check if form exists
form = reader.root_object.get("/AcroForm")
```

## Page Labels

```python
# Get page label for a page index
from pypdf._page_labels import page_index2page_label

label = page_index2page_label(reader, 0)
```

## Errors

```python
from pypdf.errors import (
    PdfReadError,       # General read errors
    PdfStreamError,     # Stream data errors
    EmptyFileError,     # Empty or no-content file
    WrongPasswordError, # Wrong decryption password
    FileNotDecryptedError,  # Encrypted file not decrypted
    ParseError,         # Parsing errors
    LimitReachedError,  # Security limit reached
)

try:
    reader = PdfReader("file.pdf")
except EmptyFileError:
    print("File is empty")
except WrongPasswordError:
    print("Wrong password")
except PdfReadError as e:
    print(f"Read error: {e}")
```

# Errors

## Exception Hierarchy

```
Exception
└── PyPdfError                    # Base class for all pypdf exceptions
    ├── DeprecationError          # Deprecated feature used
    ├── DependencyError           # Required dependency missing
    ├── PdfReadError              # Issue reading a PDF file
    │   ├── PdfStreamError        # Stream data error
    │   ├── FileNotDecryptedError # Encrypted file not decrypted
    │   │   └── WrongPasswordError # Wrong decryption password
    │   └── EmptyFileError        # Empty or no-content file
    ├── PageSizeNotDefinedError   # Page size not defined
    ├── ParseError                # Parsing error
    ├── EmptyImageDataError       # Image has no data
    ├── LimitReachedError         # Security limit reached
    └── XmpDocumentError          # Invalid XMP XML
```

## UserWarning

```
UserWarning
└── PdfReadWarning                # Potential issue, but file readable
```

## Common Errors

### PdfReadError

```python
from pypdf.errors import PdfReadError

try:
    reader = PdfReader("corrupted.pdf")
except PdfReadError as e:
    print(f"Cannot read PDF: {e}")
```

Raised for general read errors. Use `strict=False` (default) to attempt recovery.

### EmptyFileError

```python
from pypdf.errors import EmptyFileError

try:
    reader = PdfReader("empty.pdf")
except EmptyFileError:
    print("File is empty or has no PDF content")
```

### WrongPasswordError

```python
from pypdf.errors import WrongPasswordError

try:
    reader = PdfReader("encrypted.pdf", password="wrong")
except WrongPasswordError:
    print("Incorrect password")
```

### FileNotDecryptedError

```python
from pypdf.errors import FileNotDecryptedError

try:
    text = reader.pages[0].extract_text()
except FileNotDecryptedError:
    print("PDF is encrypted — call reader.decrypt() first")
```

Raised when accessing content of an encrypted PDF that hasn't been decrypted.

### PdfStreamError

```python
from pypdf.errors import PdfStreamError

try:
    reader = PdfReader("truncated.pdf")
except PdfStreamError as e:
    print(f"Stream error: {e}")
```

Raised for stream data issues (truncated streams, invalid compression).

### ParseError

```python
from pypdf.errors import ParseError
from pypdf import PageRange

try:
    range = PageRange("invalid-range")
except ParseError:
    print("Invalid page range syntax")
```

### PageSizeNotDefinedError

```python
from pypdf.errors import PageSizeNotDefinedError

try:
    width = page.mediabox.width
except PageSizeNotDefinedError:
    print("Page has no defined size")
```

### LimitReachedError

```python
from pypdf.errors import LimitReachedError

try:
    reader = PdfReader("massive.pdf")
except LimitReachedError:
    print("Security limit reached — file too large or too many objects")
```

### DependencyError

```python
from pypdf.errors import DependencyError

try:
    images = page.images  # Requires Pillow
except DependencyError:
    print("Pillow not installed — pip install Pillow")
```

### XmpDocumentError

```python
from pypdf.errors import XmpDocumentError

try:
    xmp = reader.xmp_metadata
except XmpDocumentError:
    print("Invalid XMP metadata")
```

## Error Handling Patterns

```python
from pypdf import PdfReader
from pypdf.errors import (
    PdfReadError,
    EmptyFileError,
    WrongPasswordError,
    FileNotDecryptedError,
)

def safe_read_pdf(path, password=None):
    try:
        reader = PdfReader(path, password=password)
    except EmptyFileError:
        return None, "File is empty"
    except WrongPasswordError:
        return None, "Wrong password"
    except PdfReadError as e:
        return None, f"Read error: {e}"

    if reader.is_encrypted:
        try:
            reader.decrypt(password or "")
        except WrongPasswordError:
            return None, "Wrong password"

    return reader, None
```

## Warnings

```python
import warnings
from pypdf.errors import PdfReadWarning

# Suppress pypdf warnings
warnings.filterwarnings("ignore", category=PdfReadWarning)

# Or handle them
warnings.simplefilter("always", PdfReadWarning)
```

`PdfReadWarning` indicates recoverable issues — the PDF was read but may have anomalies.

## Stream Truncation Constant

```python
from pypdf.errors import STREAM_TRUNCATED_PREMATURELY

# Error message for truncated streams
print(STREAM_TRUNCATED_PREMATURELY)  # "Stream has ended unexpectedly"
```

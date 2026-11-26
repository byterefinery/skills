# Errors

All from `pypdf.errors`.

## Exception hierarchy

```
Exception
└── PyPdfError                      # base class for all pypdf exceptions
    ├── DeprecationError            # deprecated feature used
    ├── DependencyError             # required dependency missing
    ├── PdfReadError                # issue reading a PDF file
    │   ├── PdfStreamError          # stream data error
    │   ├── FileNotDecryptedError   # encrypted file not decrypted
    │   │   └── WrongPasswordError  # wrong decryption password
    │   └── EmptyFileError          # empty or no-content file
    ├── PageSizeNotDefinedError     # page size not defined
    ├── ParseError                  # parsing error (e.g. bad PageRange string)
    ├── EmptyImageDataError         # image has no data
    ├── LimitReachedError           # security limit reached
    └── XmpDocumentError            # invalid XMP XML (also a RuntimeError)
```

Warnings:

```
UserWarning
└── PdfReadWarning                  # potential issue, file still readable
```

Note `PdfStreamError` extends `PdfReadError` (not `PyPdfError` directly in
the tree sense — it subclasses `PdfReadError`), and `XmpDocumentError`
multi-inherits from both `PyPdfError` and `RuntimeError`.

## Common patterns

### Reading a possibly broken file

```python
from pypdf.errors import PdfReadError, PdfReadWarning

try:
    reader = PdfReader("corrupted.pdf")
except PdfReadError as e:
    print(f"Cannot read PDF: {e}")
```

### Wrong password

```python
from pypdf.errors import WrongPasswordError

try:
    reader.decrypt("password")
except WrongPasswordError:
    ...
```

`reader.decrypt()` returns `PasswordType.NONE` when the file is not
encrypted at all.

### Empty file

```python
from pypdf.errors import EmptyFileError

try:
    reader = PdfReader("empty.pdf")
except EmptyFileError:
    ...
```

### Page size

```python
from pypdf.errors import PageSizeNotDefinedError

try:
    writer.add_blank_page()   # no width/height and no previous page
except PageSizeNotDefinedError:
    ...
```

### Parsing PageRange

```python
from pypdf.errors import ParseError

try:
    PageRange("::0")          # zero step rejected in 7.1.1
except ParseError:
    ...
```

## Best practices

- pypdf only raises known exception types; catch `PyPdfError` broadly or
  the specific subclass narrowly.
- `PdfReadWarning` is a `UserWarning` — non-fatal issues during parsing;
  silence or filter it per project policy (see docs on suppressing warnings).
- Security limits (stream sizes, object counts, xref entries) raise
  `LimitReachedError` rather than consuming unbounded memory.

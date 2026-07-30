# Metadata and XMP

## DocumentInformation (PDF Info Dictionary)

```python
from pypdf import PdfReader, PdfWriter

# Reading
reader = PdfReader("document.pdf")
meta = reader.metadata

if meta:
    # Text properties (decoded)
    print(meta.title)           # str or None
    print(meta.author)
    print(meta.subject)
    print(meta.keywords)
    print(meta.creator)
    print(meta.producer)

    # Date properties (parsed as datetime)
    print(meta.creation_date)    # datetime or None
    print(meta.modification_date)

    # Raw properties (may be ByteStringObject)
    print(meta.title_raw)
    print(meta.author_raw)

    # Arbitrary access
    print(meta.get("/CustomKey"))
    print(meta.keys())
```

### Properties

| Property | Raw property | Type | Description |
|---|---|---|---|
| `title` | `title_raw` | `str` | Document title |
| `author` | `author_raw` | `str` | Author name |
| `subject` | `subject_raw` | `str` | Subject description |
| `keywords` | `keywords_raw` | `str` | Comma-separated keywords |
| `creator` | `creator_raw` | `str` | Creating application |
| `producer` | `producer_raw` | `str` | PDF producer |
| `creation_date` | — | `datetime` | Creation timestamp |
| `modification_date` | — | `datetime` | Modification timestamp |

## Writing Metadata

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="input.pdf")

# Add metadata (merges with existing)
writer.add_metadata({
    "/Title": "My Document",
    "/Author": "Jane Doe",
    "/Subject": "Annual Report",
    "/Keywords": "report, annual, 2024",
    "/Creator": "My Application",
    "/Producer": "pypdf 6.14.2",
})

# Clear a field (set to empty string)
writer.add_metadata({"/Title": ""})

# Access metadata object
meta = writer.metadata
print(meta.title)

writer.write("output.pdf")
```

`add_metadata()` merges into existing metadata — it does not replace the entire dictionary.

## XMP Metadata

```python
from pypdf import PdfReader, PdfWriter
from pypdf.xmp import XmpInformation

# Reading XMP
reader = PdfReader("document.pdf")
xmp = reader.xmp_metadata

if xmp:
    # XMP properties (lists — may have multiple language versions)
    print(xmp.title)        # list of str
    print(xmp.creator)      # list of str
    print(xmp.description)  # list of str
    print(xmp.modified)     # datetime or None
    print(xmp.keywords)     # list of str
    print(xmp.subject)      # list of str
    print(xmp.create_date)  # datetime or None

    # All properties
    for key, value in xmp.properties.items():
        print(f"{key}: {value}")

# Writing XMP (raw bytes)
writer = PdfWriter(clone_from="input.pdf")
writer.xmp_metadata = xmp_bytes  # bytes — raw XMP packet
writer.xmp_metadata = None        # clear XMP

writer.write("output.pdf")
```

### XmpInformation properties

| Property | Type | Description |
|---|---|---|
| `title` | `list[str]` | Title (may have language variants) |
| `description` | `list[str]` | Description |
| `identifier` | `str` | Document identifier |
| `subject` | `list[str]` | Subject |
| `creator` | `list[str]` | Creator |
| `keywords` | `list[str]` | Keywords |
| `create_date` | `datetime` | Creation date |
| `modified` | `datetime` | Modification date |
| `languages` | `list[str]` | Document languages |
| `properties` | `dict` | All XMP properties |

## Differences: Info vs XMP

| Aspect | Info Dictionary | XMP |
|---|---|---|
| Format | PDF name/value pairs | XML packet |
| Access | `reader.metadata` | `reader.xmp_metadata` |
| Values | Single string | Lists (multi-language) |
| Dates | `datetime` objects | `datetime` objects |
| Writing | `writer.add_metadata()` | `writer.xmp_metadata = bytes` |
| Standard | PDF spec | Adobe XMP spec |
| Rich metadata | No | Yes (namespaces, arrays) |

## Date Format

```python
# PDF date format: D:YYYYMMDDHHmmSSOHH'mm
# pypdf parses this automatically to datetime

# When writing, pypdf converts datetime back to PDF format
from datetime import datetime

writer.add_metadata({
    "/CreationDate": datetime.now(),
})
```

## Custom Metadata Keys

```python
# Add custom keys via raw DictionaryObject access
from pypdf.generic import NameObject, TextStringObject

meta = writer.metadata
meta[NameObject("/CustomKey")] = TextStringObject("Custom value")
```

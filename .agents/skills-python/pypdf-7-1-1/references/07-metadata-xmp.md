# Metadata (Info + XMP)

A PDF can carry both "regular" (Info dictionary) and XMP metadata at the
same time; they are independent and may disagree.

## Info dictionary — reading

```python
reader = PdfReader("example.pdf")
meta = reader.metadata  # DocumentInformation or None

if meta:
    print(meta.title)            # all of these can be None
    print(meta.author)
    print(meta.subject)
    print(meta.creator)
    print(meta.producer)
    print(meta.creation_date)    # PDF date string, e.g. D:20251030092955-05'00'
    print(meta.modification_date)
```

## Info dictionary — writing

```python
from datetime import datetime

writer = PdfWriter(clone_from="example.pdf")

# Merge into existing metadata
writer.add_metadata({
    "/Title": "Title",
    "/Author": "Martin",
    "/Subject": "Subject",
    "/Keywords": "Keywords",
    "/Creator": "Creator",
    "/Producer": "Libre Writer",
    "/CreationDate": "D:20251030092955",
    "/ModDate": "D:20251030092955",
    "/CustomField": "CustomField",
})

# Replace all entries
writer.metadata = {"/Author": "Martin", "/Producer": "Libre Writer"}

# Clear all values but keep the entry
writer.metadata = {}

# Remove the Info entry entirely
writer.metadata = None

writer.write("out.pdf")
```

`add_metadata(dict)` merges; assignment to `writer.metadata` replaces
(dict), clears ({}), or removes (None). To carry over the source metadata
when building a writer from scratch, call
`writer.add_metadata(reader.metadata)` before adding new fields.

PDF date format for `/CreationDate`/`/ModDate`:
`D:YYYYMMDDHHMMSS` plus optional timezone like `-05'00'`.

## XMP — reading

```python
meta = reader.xmp_metadata  # XmpInformation or None
if meta:
    print(meta.dc_title)         # language map, e.g. {'x-default': '...'}
    print(meta.dc_description)
    print(meta.xmp_create_date)  # datetime
```

## XMP — creating and setting

```python
from pypdf.xmp import XmpInformation

xmp = XmpInformation.create()

# Dublin Core
xmp.dc_title = {"x-default": "My Document Title", "en": "English Title"}
xmp.dc_creator = ["Author One", "Author Two"]
xmp.dc_description = {"x-default": "Document description"}
xmp.dc_subject = ["keyword1", "keyword2"]
xmp.dc_date = [datetime.now()]

# XMP / PDF / PDF-A / XMP Media Management
xmp.xmp_create_date = datetime.now()
xmp.xmp_creator_tool = "pypdf"
xmp.pdf_producer = "pypdf"
xmp.pdf_keywords = "keyword1, keyword2"
xmp.pdfaid_part = "1"
xmp.pdfaid_conformance = "B"
xmp.xmpmm_document_id = "uuid:..."

# Clear any field by assigning None
xmp.dc_title = None

writer = PdfWriter()
writer.add_blank_page(612, 792)
writer.xmp_metadata = xmp
writer.write("out-xmp.pdf")
```

Field families: `dc_*` (Dublin Core — bags as lists, sequences as lists,
language maps as dicts), `xmp_*` (dates, `xmp_creator_tool`), `pdf_*`,
`pdfaid_*`, `xmpmm_*`. Date fields accept `datetime` objects or strings.

Incremental update pattern: read the property (returns a list/dict), mutate,
assign back:

```python
subjects = xmp.dc_subject or []
subjects.append("new_keyword")
xmp.dc_subject = subjects
```

## XMP — raw DOM editing

`writer.xmp_metadata` exposes `rdf_root` (an `xml.dom.minidom` node). To add
custom elements:

```python
writer = PdfWriter(clone_from="commented-xmp.pdf")
metadata = writer.xmp_metadata
assert metadata is not None

rdf_root = metadata.rdf_root
xmp_meta = rdf_root.parentNode
xmp_document = xmp_meta.parentNode

desc = xmp_document.createElement("rdf:Description")
desc.setAttribute("rdf:about", "")
desc.setAttribute("xmlns:pdfuaid", "http://www.aiim.org/pdfua/ns/id/")
part = xmp_document.createElement("pdfuaid:part")
part.appendChild(xmp_document.createTextNode("1"))
desc.appendChild(part)
rdf_root.appendChild(desc)

metadata.stream.set_data(xmp_document.toxml().encode("utf-8"))
writer.write("out.pdf")
```

Invalid XMP XML raises `XmpDocumentError`.

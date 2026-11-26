# Generic Types

`pypdf.generic` exposes the PDF object model. Everything is a `PdfObject`;
indirect references are `IndirectObject`s that resolve via `.get_object()`.

Common exports: `ArrayObject`, `BooleanObject`, `ByteStringObject`,
`ContentStream`, `DecodedStreamObject`, `Destination`, `DictionaryObject`,
`EmbeddedFile`, `EncodedStreamObject`, `Field`, `Fit`, `FloatObject`,
`IndirectObject`, `NameObject`, `NullObject`, `NumberObject`,
`OutlineItem`, `PdfObject`, `RectangleObject`, `StreamObject`,
`TextStringObject`, `TreeObject`, `ViewerPreferences`,
`create_string_object`, `extract_links`, `hex_to_rgb`.

## Basics

```python
from pypdf.generic import (
    ArrayObject, DictionaryObject, NameObject, NumberObject, FloatObject,
    ByteStringObject, TextStringObject, create_string_object,
)

d = DictionaryObject({
    NameObject("/Title"): create_string_object("Hello"),
    NameObject("/Count"): NumberObject(3),
})
arr = ArrayObject([NumberObject(1), NumberObject(2)])
name = NameObject("/Subtype")
```

`create_string_object(str)` picks ByteString vs TextString encoding
automatically.

## DictionaryObject

Behaves like a dict keyed by `NameObject` (plain strings work too):

```python
obj = annotation.get_object()
obj["/Subtype"]              # key lookup
obj.get("/Rect")
if "/Annots" in page:
    annots = page["/Annots"].get_object()
obj[NameObject("/C")] = ArrayObject([FloatObject(0.9), FloatObject(0.1), FloatObject(0)])
```

## Indirect objects

```python
ref = page.indirect_reference        # None if the page is not in a document
obj = ref.get_object()
ref.idnum                           # object number
```

## RectangleObject

```python
from pypdf.generic import RectangleObject

r = RectangleObject((left, bottom, right, top))
r.left, r.bottom, r.right, r.top, r.width, r.height
r.upper_right, r.lower_left        # (x, y) tuples
r.scale(sx=0.7, sy=0.7)
RectangleObject([l, b, r_, t])     # from numeric list
```

Used for page boxes (`page.mediabox = ...`) and annotation rects.

## StreamObject / ContentStream

```python
data = stream.get_data()      # decoded bytes
stream.set_data(data)
stream.get_length()
```

`ContentStream` is a page's parsed content stream (used by
`page.get_contents()`).

## Destination / Fit / links

```python
from pypdf.generic import Destination, Fit, extract_links
from pypdf.annotations import Link

# Fit view modes for bookmarks and internal links
Fit.fit()                                   # /Fit
Fit.fit_horizontally(top=800)              # /FitH
Fit.fit_rectangle(rect=(0, 0, 100, 100))    # /FitR
Fit.fit_vertically(left=0)                  # /FitV
Fit.fit_box()                               # /FitB
Fit.xyz(left=0, top=800, zoom=1.25)        # /Xyz
Fit(fit_type="/FitH", fit_args=(123,))     # raw construction

dest = Destination(NameObject("/MyDest"), page_ref, Fit.fit())
dest.title, dest.page
reader.get_destination_page_number(dest)   # zero-based int or None

# Links inside a page content stream
links = extract_links(page)                # list[ReferenceLink]
```

`Link` annotations accept `target_page_index` + `fit=` internally;
`extract_links` classifies page links as `DirectReferenceLink` or
`NamedReferenceLink`.

## TreeObject

Base for tree structures such as the outline root
(`writer.get_outline_root()`) and named threads
(`writer.get_threads_root()`).

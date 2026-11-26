# PdfWriter

## Construction

```python
from pypdf import PdfWriter

writer = PdfWriter()                       # empty document
writer = PdfWriter("input.pdf")            # fileobj as first arg: clones the document
writer = PdfWriter(clone_from="input.pdf") # explicit clone
writer = PdfWriter(clone_from=reader)      # clone from a PdfReader
writer = PdfWriter(clone_from=BytesIO(data))
```

`PdfWriter(fileobj="", clone_from=None, incremental=False, full=False,
strict=False, *, keep_initial_header=False,
incremental_clone_object_count_limit=500_000,
incremental_clone_object_id_limit=1_000_000)`.

- `incremental=True` (alias `full=True`) writes only the changed parts; the
  writer becomes read-only toward the original. `encrypt()` is not supported
  on incremental writers.
- `strict` behaves as in PdfReader.
- The two `incremental_clone_*` limits cap object reading during incremental
  cloning (`None` disables).
- A new writer has no pages; `/Producer: pypdf` is set by default.
- Context manager: `with PdfWriter() as writer:` closes the output stream.

## Composition — append / merge (recommended)

```python
from pypdf import PdfWriter, PageRange

writer = PdfWriter()

# fileobj may be a path, file-like, or PdfReader
writer.append("a.pdf")
writer.append(reader, pages=(0, 10))                    # first 10 pages
writer.append(reader, pages=PageRange("::2"))           # every second page
writer.append("b.pdf", pages=[0, 9])                    # explicit page list
writer.append("c.pdf", outline_item="Chapter C")        # adds an outline bookmark
writer.append("d.pdf", pages=(0, 5), import_outline=False)
writer.append("e.pdf", pages=(0, 3), excluded_fields=["/B", "/Annots"])
```

`append(fileobj, outline_item=None, pages=None, import_outline=True,
excluded_fields=None)` concatenates to the end. `outline_item` as a string
creates a bookmark naming the included file; `pages` accepts a `PageRange`,
a `(start, stop[, step])` tuple, or a list of page indices/`PageObject`s.
`excluded_fields` omits dictionary keys from cloned objects (`"/Annots"`
drops annotations, `"/B"` drops articles).

`merge(position, fileobj, ...)` is identical but inserts at a page number:
the file is inserted *after* page `position`.

```python
writer = PdfWriter()
with open("input1.pdf", "rb") as f1, open("input2.pdf", "rb") as f2:
    writer.append(f1, pages=(0, 3))      # first 3 pages of input1
    writer.merge(position=2, fileobj=f2, pages=(0, 1))
    writer.write("out.pdf")
```

Notes:

- Named destinations from the source are imported during merging.
- Cloned objects are cached: adding the same page twice shares objects; call
  `writer.reset_translation(reader)` to reset before re-adding.
- Merging forms: run `reader.add_form_topname("form1")` first so fields get
  the group prefix (`form1.field1`).
- Large files may hit Python's recursion limit; `sys.setrecursionlimit(...)`
  can help.

Legacy: `append_pages_from_reader(reader, after_page_append=None)` copies
pages only ("`append` should be preferred"); `clone_document_from_reader(reader)`
clones the full document structure into the writer.

## Adding pages directly (advanced)

```python
writer = PdfWriter()
page = writer.add_page(reader.pages[0])          # returns the writer's PageObject
writer.insert_page(reader.pages[0], index=0)    # insert at position
blank = writer.add_blank_page(width=595, height=842)   # None => last page size
writer.insert_blank_page(width=None, height=None, index=1)
```

`add_page(page, excluded_keys=())` and `insert_page(page, index,
excluded_keys=())` exist for fine-grained cloning control. A new writer with
no pages and `add_blank_page()` without dimensions raises
`PageSizeNotDefinedError`.

`writer.pages` behaves like a list; `writer.get_num_pages()` returns the count.

## Rotation, scaling, transforms

See [03-page-object](03-page-object.md) and [04-transformation](04-transformation.md).

## Encryption

See [09-encryption](09-encryption.md).

```python
writer = PdfWriter(clone_from="input.pdf")
writer.encrypt("user-password", "owner-password", algorithm="AES-256-R5")
writer.write("encrypted.pdf")
```

## Attachments

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")
embedded = writer.add_attachment(filename="test.txt", data=b"Hello World!")

# EmbeddedFile setters
import datetime, hashlib
from pypdf.generic import create_string_object, ByteStringObject, NameObject, NumberObject
embedded.size = NumberObject(len(b"Hello World!"))
embedded.alternative_name = create_string_object("test1.txt")
embedded.description = create_string_object("My test file")
embedded.subtype = NameObject("/text/plain")
embedded.checksum = ByteStringObject(hashlib.md5(b"Hello World!").digest())
embedded.modification_date = datetime.datetime.now(tz=datetime.timezone.utc)
embedded.delete()  # remove again (does not remove AF relationships)

for attachment in writer.attachment_list:
    print(attachment.name, attachment.content)

writer.write("out.pdf")
```

PDF/A-3B note: set `subtype`,
`associated_file_relationship = NameObject(AFRelationship.SUPPLEMENT)`
(`pypdf.constants.AFRelationship`), and append
`attachment.pdf_object.indirect_reference` to the root `"/AF"` array.

## Outlines (bookmarks)

Keyword-only in 7.x; returns the added `IndirectObject` for nesting.

```python
from pypdf import PdfWriter
from pypdf.generic import Fit

writer = PdfWriter(clone_from="crazyones.pdf")

chapter = writer.add_outline_item(title="Chapter 1", page_number=0)
writer.add_outline_item(title="Section 1.1", page_number=0, parent=chapter)

# Advanced styling
writer.add_outline_item(
    title="Chapter 2",
    page_number=2,
    color=(0, 0, 1),        # RGB tuple 0.0-1.0 or hex string "#RRGGBB"
    bold=True,
    italic=False,
    is_open=True,
    fit=Fit.fit(),          # or Fit.fit_horizontally(top=800), Fit.xyz(...)
)
writer.write("out.pdf")
```

`add_outline_item(*, title, page_number, parent=None, before=None,
color=None, bold=False, italic=False, fit=PAGE_FIT, is_open=True)`.
`page_number` accepts an int, PageObject, IndirectObject, or None (no
destination). Positional arguments are deprecated (removed in 8.0).

Related: `add_outline_item_destination(outline_item, parent, before,
is_open)`, `add_named_destination(name, page)`, `threads` (named threads /
article views).

## Annotations

`writer.add_annotation(page_number, annotation)` — `page_number` may be an
int index or a PageObject; returns the inserted annotation object (usable as
`Popup`'s `parent`). See [05-annotations](05-annotations.md).

Removal helpers:

```python
writer.remove_links()
writer.remove_annotations(subtypes="/Widget")  # None => remove all
writer.remove_images()              # ImageType.ALL by default
writer.remove_text(font_names=None) # optional list of font names
```

## JavaScript / open actions

```python
from pypdf.actions import JavaScript

writer = PdfWriter(clone_from="example.pdf")
writer.add_open_action(
    JavaScript("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
)
writer.write("out.pdf")
```

`add_js()` is deprecated (NoReturn) — use `add_open_action()`. Per-page
actions: `page.add_action(trigger, action)` with `pypdf.actions.PageTrigger`
(e.g. `PageTrigger("open")`).

## Viewer preferences

```python
writer = PdfWriter()
writer.create_viewer_preferences()   # required: dict does not exist by default

writer.viewer_preferences.hide_toolbar = True
writer.viewer_preferences.fit_window = True
writer.viewer_preferences.direction = "/L2R"          # or "/R2L"
writer.viewer_preferences.non_fullscreen_pagemode = "/UseOutlines"
writer.viewer_preferences.print_scaling = "/AppDefault"
writer.viewer_preferences.duplex = "/Simplex"
writer.viewer_preferences.num_copies = 2
```

## Metadata

See [07-metadata-xmp](07-metadata-xmp.md).

## Form fields

`writer.update_page_form_field_values(page, fields, flags=FFBITS_NUL,
auto_regenerate=True, flatten=False)` — page may be a writer PageObject, a
list of them, or None (all pages). See [06-form-fields](06-form-fields.md).

Other field methods: `writer.reattach_fields()`,
`writer.get_fields()`, `writer.get_form_text_fields()`,
`writer.get_pages_showing_field(field)`,
`writer.set_need_appearances_writer(state=True)`.

## Writing output

```python
result = writer.write("out.pdf")        # returns (bool, IO): (incremental, handle)
writer.write(stream)                    # any file-like object
```

`writer.root_object` exposes the catalog dictionary for direct manipulation.

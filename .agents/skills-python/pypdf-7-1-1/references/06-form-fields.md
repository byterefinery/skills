# Form Fields

## Reading

```python
reader = PdfReader("form.pdf")

fields = reader.get_form_text_fields()      # {"key": "value", ...}
fields = reader.get_form_text_fields(True)  # fully qualified names
all_fields = reader.get_fields()            # every field type
```

Hierarchical fields use dotted fully-qualified names (`sender.city`). Radio
button groups appear as one parent field in `get_fields()` but as multiple
child widgets in `page.annotations`.

## Filling

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter(clone_from=reader)

writer.update_page_form_field_values(
    writer.pages[0],                      # writer's page, list of pages, or None
    {"fieldname": "some filled in text"},
    auto_regenerate=False,                # default True is legacy — avoid
)
writer.write("filled.pdf")
```

`update_page_form_field_values(page, fields, flags=FFBITS_NUL,
auto_regenerate=True, flatten=False)`:

- `page` — the **writer's** `PageObject` (or list, or None for all pages).
  Fields without a widget on the page are still updated from `/Fields`.
- `fields` — dict of field name to value; values may be a list (choice
  field) or a `(text, font_id, font_size)` tuple (size 0 = autosize).
- `auto_regenerate` — sets the `/NeedAppearances` flag. `True` (the default,
  kept for legacy) makes viewers re-render fields and can trigger a "save
  changes" dialog; `False` is recommended; `None` leaves the flag unchanged.
- `flatten` — bakes field appearances into the page content; the widgets
  themselves remain (remove them with `remove_annotations(subtypes="/Widget")`).
- Raises `PyPdfError` if the document has no `/AcroForm`/`/Fields`.

`flags` come from
`pypdf.constants.FieldDictionaryAttributes.FfBits` (default `FFBITS_NUL`).

## Locating fields

```python
field_obj = ...  # a Field/PdfObject from /AcroForm /Fields
pages = writer.get_pages_showing_field(field_obj)  # list[PageObject]
```

## Repairing and grouping

```python
writer.reattach_fields()          # rebuild missing /Fields from page /Widget annots
reader.add_form_topname("form1")  # group fields: field1 -> form1.field1
reader.rename_form_topname("newname")
```

`reattach_fields()` cannot recover intermediate parent fields or
distinguish fields sharing a name.

## Structural notes

- Fields live in the root `/AcroForm` (`/Fields` array), not in pages —
  `writer.add_page()` does **not** copy field structure; use
  `writer.append(reader)` to bring fields along.
- `/Widget` annotations in `page.annotations` render fields visually; Field
  objects carry `/FT` (type), `/T` (partial name), `/V` (value), `/DV`
  (default value), `/Parent`/`/Kids` (hierarchy).
- XFA forms (`/AcroForm`/`XFA`) override page content in some viewers.
- `writer.set_need_appearances_writer(state=True)` toggles `/NeedAppearances`.
- Merging multiple forms: add a top name per source reader before appending
  to avoid field name collisions.

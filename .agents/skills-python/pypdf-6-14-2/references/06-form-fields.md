# Form Fields

## Reading Form Fields

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")

# Get all form field values as a dict
fields = reader.get_form_text_fields()
# Returns: {"field_name": "field_value", ...}

for name, value in fields.items():
    print(f"{name}: {value}")
```

## Updating Form Fields

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter(clone_from="form.pdf")

# Update field values on a specific page
writer.update_page_form_field_values(
    writer.pages[0],
    {
        "Name": "John Doe",
        "Email": "john@example.com",
        "Checkbox": "/Yes",      # Checkbox: "/Yes" or "/Off"
        "Radio": "/Option1",     # Radio button
        "Dropdown": "Option A",  # Dropdown/Listbox
        "Textarea": "Long text...",
    },
    flags=1,  # NeedAppearances flag
)

writer.write("filled_form.pdf")
```

### Field value formats

| Field type | Value format |
|---|---|
| Text field | `str` — any text |
| Checkbox | `"/Yes"` or `"/Off"` |
| Radio button | Option name (e.g., `"/Option1"`) |
| Dropdown | Option text |
| Listbox | Option text (or list for multi-select) |
| Signature | `"/Signed"` |

### Flags parameter

```python
# flags=1 — set NeedAppearances (renderer generates appearance)
# flags=0 — do not set NeedAppearances

writer.update_page_form_field_values(
    writer.pages[0],
    {"field": "value"},
    flags=1,
)
```

## Reattaching Fields

```python
# After updating form fields, fields may disappear from the document
# Reattach them to ensure they persist
writer.reattach_fields()
```

Use `reattach_fields()` after `update_page_form_field_values()` if fields don't appear in the output PDF.

## NeedAppearances

```python
# Set NeedAppearances in AcroForm
writer.set_need_appearances_writer(True)
```

This tells PDF readers to generate appearance streams for form fields, ensuring they display correctly.

## Form Topname

```python
# Add a form topname (root field name)
writer.add_form_topname("Form1")

# Rename existing form topname
writer.rename_form_topname("NewFormName")
```

## Checking for Forms

```python
reader = PdfReader("document.pdf")

# Check if document has an AcroForm
form = reader.root_object.get("/AcroForm")
if form:
    print("Document has form fields")
    fields = reader.get_form_text_fields()
else:
    print("No form fields")
```

## Field Types

```python
from pypdf.generic import Field

# Common field types (as /FT values)
# /Tx — Text field
# /Btn — Button (checkbox, radio, pushbutton)
# /Ch — Choice (dropdown, listbox)
# /Sig — Signature

# Check field type
for field in form_fields:
    field_type = field.get("/FT")
    print(field_type)
```

## Writing Forms

```python
from pypdf import PdfWriter

# Create a new PDF with a form
writer = PdfWriter()
page = writer.add_blank_page(595, 842)

# Add form fields via AcroForm manipulation
# (pypdf focuses on reading/updating existing forms;
#  creating new forms requires low-level dictionary manipulation)

writer.write("form.pdf")
```

For creating new form fields from scratch, use low-level `DictionaryObject` manipulation or start from a template PDF with existing fields.

## Common Issues

- **Fields disappear after update** — call `writer.reattach_fields()` after `update_page_form_field_values()`
- **Fields not rendering** — set `flags=1` (NeedAppearances) or call `writer.set_need_appearances_writer(True)`
- **Checkbox values** — use `"/Yes"` for checked, `"/Off"` for unchecked (not `True`/`False`)
- **Radio button groups** — each option in a group has a different export value; use the correct option name

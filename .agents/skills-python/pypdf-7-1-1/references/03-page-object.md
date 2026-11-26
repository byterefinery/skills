# PageObject

## Text extraction

```python
page = reader.pages[0]

# Plain mode (default)
text = page.extract_text()

# Only certain orientations (0 up, 90 turned left, 180, 270)
text = page.extract_text(0)
text = page.extract_text((0, 90))

# Layout mode — fixed-width text following the rendered layout
text = page.extract_text(extraction_mode="layout")
text = page.extract_text(
    extraction_mode="layout",
    layout_mode_space_vertically=False,   # default True; drops blank/whitespace-only lines
    layout_mode_scale_weight=1.0,         # default 1.25
    layout_mode_strip_rotated=False,      # default True; False includes rotated text (degrades layout, warns)
)
```

`extract_text(*args, orientations=(0,90,180,270), space_width=200.0,
visitor_operand_before=None, visitor_operand_after=None, visitor_text=None,
extraction_mode="plain", **kwargs)`.

- Layout mode **ignores** `orientations`, `space_width`, and all
  `visitor_*` parameters (warns).
- Arabic and Hebrew are extracted in the correct order; custom RTL ranges can
  be defined (see `set_custom_rtl`, private module `pypdf._text_extraction`).
- Extraction parses the whole content stream; very large streams can need
  gigabytes of RAM. Check `len(page.get_contents().get_data())` first if
  needed.
- Output order is not guaranteed stable across pypdf versions.

### Visitor functions

`visitor_text(text, user_matrix, tm_matrix, font_dictionary, font_size)` is
called for each text fragment; `font_dictionary` may be None for unknown
fonts. `visitor_operand_before`/`visitor_operand_after`(operator,
operands, ctm, tm) fire per content-stream operator.

```python
from pypdf import PdfReader, mult

reader = PdfReader("doc.pdf")
page = reader.pages[3]
parts = []

def visitor_body(text, cm, tm, font_dict, font_size):
    txt2user = mult(tm, cm)   # full text->user space matrix
    y = txt2user[5]
    if 50 < y < 720 or y == 0:  # skip header/footer bands
        parts.append(text)

page.extract_text(visitor_text=visitor_body)
body = "".join(parts)
```

`mult` (exported from `pypdf`) multiplies PDF matrices; `txt2user[4]`/`[5]`
are x/y.

## Images

```python
for i, img in enumerate(page.images):
    print(img.name)            # may contain arbitrary characters — sanitize
    img.image.save(f"out-{i}.png")   # Pillow Image; requires Pillow

# Direct access
first = page.images[0]
by_name = page.images["/I0"]
nested = page.images["/TP1", "/Image1"]  # image inside an XObject form
```

`page.images` is a read-only `VirtualListImages` (int, name-string, or
name-tuple indexing). Iteration raises on the first broken image — for
tolerant extraction, iterate `page.images.keys()` and fetch each key inside
try/except.

Images inside annotations: walk the annotation tree and call
`decode_as_image()`:

```python
im = (
    reader.pages[0]["/Annots"][4]["/Parent"]
    .get_object()["/AP"]["/N"]["/Resources"]["/XObject"]["/Im4"]
    .decode_as_image()
)
im.save("out-annotation-image.png")
```

## Merging pages

```python
# Overlay page_box on top (default over=True); expand=True grows page boxes
page.merge_page(page_box, over=False, expand=True)

# Merged with a transformation (stamp/watermark)
from pypdf import Transformation
page.merge_transformed_page(page_box, Transformation().rotate(45).translate(tx=50))
```

`merge_page(page2, expand=False, over=True)` draws `page2`'s content on top
of `page1` by default (`over=False` for watermarks); the page's own boxes are
not altered unless `expand=True`. If a merged result looks cropped, use
`expand=True`.

## Rotation and scaling

```python
page.rotate(90)               # in place, multiple of 90; returns page
page.add_transformation(Transformation().scale(sx=0.7, sy=0.7))
page.scale_by(0.5)            # content AND boxes together
page.scale_to(width, height)  # scale to exact size
page.scale(sx, sy)            # content only (around origin)

# Before merging rotated pages, bake rotation into content:
page.transfer_rotation_to_content()
```

`rotate()` is preferred over a rotate transformation because it keeps content
inside the mediabox/cropbox. `page.rotation` returns the current angle.

## Page boxes

```python
mb = page.mediabox             # RectangleObject; also cropbox, trimbox, bleedbox, artbox
page.mediabox = RectangleObject((0, 0, mb.width / 2, mb.height / 2))  # crop to half
page.mediabox = page.mediabox.scale(sx=0.7, sy=0.7)
```

Cropping only adjusts the viewbox — removed content is still in the file.
The page merge box changed from trimbox to cropbox in pypdf > 3.4.0; restore
old behavior with `overwrite_configuration(page_merge_box="trimbox")`.

## Annotations on a page

```python
annots = page.annotations  # ArrayObject of IndirectObjects or None
page.annotations = None     # delete the /Annots entry
```

## Page actions

```python
from pypdf.actions import JavaScript, PageTrigger
page.add_action(PageTrigger("open"), JavaScript("app.alert('hi');"))
```

## Misc

- `page.page_number` — index of the page in its parent document
- `page.get_contents()` — the page's ContentStream (`.get_data()` for bytes)
- `page.original_page` — the source page set during `append`/`merge`
- `reader.pages[i].original_page` is the reader-side counterpart

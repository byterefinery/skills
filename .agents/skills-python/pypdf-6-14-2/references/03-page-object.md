# PageObject

## Accessing Pages

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")

# By index
page = reader.pages[0]

# Iterate
for page in reader.pages:
    text = page.extract_text()

# Slice
first_three = reader.pages[:3]

# Last page
last = reader.pages[-1]
```

## Text Extraction

### Plain mode (default)

```python
text = page.extract_text()

# With specific orientations
text = page.extract_text(orientations=(0, 90))

# With custom space width
text = page.extract_text(space_width=200.0)

# With visitor callbacks
def before(op, operand, cm, tm):
    pass

def after(op, operand, cm, tm):
    pass

def on_text(text, cm, tm, font, fontsize):
    print(f"Text: {text!r}, Font: {font}, Size: {fontsize}")

text = page.extract_text(
    visitor_operand_before=before,
    visitor_operand_after=after,
    visitor_text=on_text,
)
```

### Layout mode

```python
# Experimental layout-preserving extraction
text = page.extract_text(extraction_mode="layout")

# Layout mode kwargs
text = page.extract_text(
    extraction_mode="layout",
    layout_mode_space_vertically=True,       # include blank lines
    layout_mode_scale_weight=1.25,           # string length multiplier
    layout_mode_strip_rotated=True,          # exclude rotated text
    layout_mode_debug_path=None,             # Path for debug output
    layout_mode_font_height_weight=1.0,      # font height multiplier
)
```

Layout mode ignores `orientations`, `space_width`, and `visitor_*` parameters.

## Image Extraction

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
page = reader.pages[0]

# Access images as a virtual list
images = page.images

# Iterate
for img in images:
    print(img.name)      # filename
    print(img.data)      # bytes (image data)
    print(img.image)     # PIL.Image (if Pillow installed)
    print(img.format)    # image format info

# Index by position
first_img = images[0]

# Index by name
img = images["/Im1"]

# Index by [name, index] for duplicates
img = images[["/Im1", 0]]

# Slice
imgs = images[:2]

# Save images
for i, img in enumerate(images):
    with open(f"page_{i}_{img.name}", "wb") as f:
        f.write(img.data)
```

Requires Pillow: `pip install Pillow`.

### ImageFile attributes

| Attribute | Type | Description |
|---|---|---|
| `name` | `str` | Image name (e.g., `/Im1`) |
| `data` | `bytes` | Raw image data |
| `image` | `PIL.Image` | PIL Image object |
| `format` | `str` | Format info string |
| `indirect_link` | `IndirectObject` | Reference in PDF |

## Inline Images

```python
# Parse inline images from content stream
inline = page.inline_images
# Returns dict[str, ImageFile] or None
```

## Page Merging

```python
reader = PdfReader("document.pdf")
page1 = reader.pages[0]
page2 = reader.pages[1]

# Merge page2 onto page1 (page2 on top)
page1.merge_page(page2)

# Merge with transformation
from pypdf import Transformation
page1.merge_transformed_page(
    page2,
    Transformation().scale(0.5, 0.5).translate(100, 100),
)

# Convenience methods
page1.merge_scaled_page(page2, scale=0.5)
page1.merge_rotated_page(page2, rotation=90)
page1.merge_translated_page(page2, tx=100, ty=100)
```

### Merge parameters

| Method | Description |
|---|---|
| `merge_page(page2)` | Overlay page2 on page1 |
| `merge_transformed_page(page2, transform)` | Overlay with transformation |
| `merge_scaled_page(page2, scale)` | Overlay scaled |
| `merge_rotated_page(page2, rotation)` | Overlay rotated |
| `merge_translated_page(page2, tx, ty)` | Overlay translated |

## Rotation

```python
# Rotate in place (multiple of 90)
page.rotate(90)    # clockwise
page.rotate(-90)   # counter-clockwise
page.rotate(180)

# Get current rotation
rotation = page.rotation  # int: 0, 90, 180, 270

# Transfer rotation to content (bakes rotation into content stream)
page.transfer_rotation_to_content()
```

## Transformations

```python
from pypdf import Transformation

# Scale
page.add_transformation(Transformation().scale(2, 2))
page.add_transformation(Transformation().scale(sx=0.5, sy=0.5))

# Translate
page.add_transformation(Transformation().translate(100, 100))

# Rotate (any angle, not just multiples of 90)
page.add_transformation(Transformation().rotate(45))

# Compose transformations
op = Transformation().scale(2, 2).translate(100, 100).rotate(45)
page.add_transformation(op)

# Matrix multiplication
t1 = Transformation().scale(2, 2)
t2 = Transformation().translate(100, 100)
composed = t1.transform(t2)
```

## Page Dimensions

```python
# MediaBox (full page size)
mediabox = page.mediabox  # RectangleObject: [x1, y1, x2, y2]
print(float(mediabox.lower_left[0]))
print(float(mediabox.upper_right[0]))

# CropBox (visible area)
cropbox = page.cropbox

# BleedBox, TrimBox, ArtBox
bleedbox = page.bleedbox
trimbox = page.trimbox
artbox = page.artbox

# Set dimensions
page.mediabox = [0, 0, 612, 792]
page.cropbox = [0, 0, 612, 792]

# User unit (scaling factor)
unit = page.user_unit  # float
```

## Content Stream

```python
# Get content stream
content = page.get_contents()  # ContentStream or None

# Get as bytes
bytes_data = page._get_contents_as_bytes()

# Replace content stream
from io import BytesIO
page.replace_contents(BytesIO(b"BT /F1 12 Tf 100 700 Td (Hello) Tj ET"))
```

## Annotations

```python
# Get annotations
annots = page.annotations
# Returns list of annotation dictionaries or None

# Iterate annotations
if page.annotations:
    for annot in page.annotations:
        print(annot)
```

## Create Blank Page

```python
from pypdf import PageObject, PaperSize

# Create blank page
page = PageObject.create_blank_page(width=595, height=842)

# From paper size
page = PageObject.create_blank_page(*PaperSize.A4)

# With user unit
page = PageObject.create_blank_page(*PaperSize.A4, user_unit=1.0)
```

## Hash/Identity

```python
# Unique hash for deduplication
hash_val = page.hash_bin()

# Hash of page data (for comparison)
data_hash = page.hash_value_data()
```

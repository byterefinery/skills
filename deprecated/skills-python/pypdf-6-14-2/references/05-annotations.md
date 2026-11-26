# Annotations

## Overview

pypdf provides annotation classes for creating and manipulating PDF annotations. All annotations are `DictionaryObject` subclasses, so you can extend functionality by setting raw PDF keys.

```python
from pypdf.annotations import (
    Highlight,
    FreeText,
    Rectangle,
    Ellipse,
    Polygon,
    PolyLine,
    Line,
    Text,
    Link,
    Popup,
    MarkupAnnotation,
    AnnotationDictionary,
    NO_FLAGS,
)
```

## Markup Annotations

Markup annotations (Highlight, Underline, Squiggly, StrikeOut, FreeText, Line, Square/Rectangle, Circle/Ellipse, Polygon, PolyLine, Text, Caret, Ink, Popup) share common attributes.

### Highlight

```python
from pypdf.annotations import Highlight
from pypdf import PdfWriter, PdfReader
from pypdf.constants import Color

writer = PdfWriter(clone_from="input.pdf")
page = writer.pages[0]

# Create highlight annotation
highlight = Highlight(
    rect=[100, 700, 300, 720],  # [x1, y1, x2, y2]
    page=page,
    colors=[Color.red],         # annotation color
)

# Add to page
page.annotations = page.annotations or []
page.annotations.append(highlight)

writer.write("output.pdf")
```

### FreeText

```python
from pypdf.annotations import FreeText

free_text = FreeText(
    rect=[100, 400, 300, 450],
    page=page,
    text="Hello World",
    font_size=12,
    colors=[Color.black],
)
page.annotations.append(free_text)
```

### Rectangle

```python
from pypdf.annotations import Rectangle

rect = Rectangle(
    rect=[100, 500, 300, 600],
    page=page,
    colors=[Color.blue],
    interior_colors=None,
)
page.annotations.append(rect)
```

### Ellipse

```python
from pypdf.annotations import Ellipse

ellipse = Ellipse(
    rect=[100, 500, 300, 600],
    page=page,
    colors=[Color.green],
)
page.annotations.append(ellipse)
```

### Polygon

```python
from pypdf.annotations import Polygon

polygon = Polygon(
    vertices=[[100, 500], [300, 500], [300, 600], [100, 600]],
    page=page,
    colors=[Color.red],
)
page.annotations.append(polygon)
```

### PolyLine

```python
from pypdf.annotations import PolyLine

polyline = PolyLine(
    vertices=[[100, 500], [200, 550], [300, 500]],
    page=page,
    colors=[Color.blue],
)
page.annotations.append(polyline)
```

### Line

```python
from pypdf.annotations import Line

line = Line(
    coords=[100, 500, 300, 600],  # [x1, y1, x2, y2]
    page=page,
    colors=[Color.black],
)
page.annotations.append(line)
```

### Text (Note/Comment)

```python
from pypdf.annotations import Text

text = Text(
    point=[200, 500],
    page=page,
    contents="This is a note",
    open=False,
)
page.annotations.append(text)
```

## Non-Markup Annotations

### Link

```python
from pypdf.annotations import Link

# Internal link (to another page)
link = Link(
    rect=[100, 700, 200, 720],
    page=page,
    border=[0, 0, 1],
    url=None,
    dest_page_number=5,
)
page.annotations.append(link)

# External URL link
link = Link(
    rect=[100, 680, 300, 700],
    page=page,
    border=[0, 0, 0],
    url="https://example.com",
)
page.annotations.append(link)
```

### Popup

```python
from pypdf.annotations import Popup

popup = Popup(
    point=[200, 500],
    page=page,
    contents="Popup note",
)
page.annotations.append(popup)
```

## Common Attributes

### Rectangle

```python
rect = [x1, y1, x2, y2]  # Bottom-left to top-right
# Coordinates are in default user space (points from bottom-left)
```

### Colors

```python
from pypdf.constants import Color

# Predefined colors
Color.red     # (1.0, 0.0, 0.0)
Color.green   # (0.0, 1.0, 0.0)
Color.blue    # (0.0, 0.0, 1.0)
Color.black   # (0.0, 0.0, 0.0)
Color.white   # (1.0, 1.0, 1.0)
Color.yellow  # (1.0, 1.0, 0.0)
Color.cyan    # (0.0, 1.0, 1.0)
Color.magenta # (1.0, 0.0, 1.0)

# Custom RGB (0-1 floats)
custom = (0.5, 0.3, 0.8)
```

### Border

```python
# [horizontal_width, vertical_width, border_width]
border = [0, 0, 2]  # 2pt border
border = [0, 0, 0]  # No border
```

### Flags

```python
from pypdf.annotations import NO_FLAGS

# Annotation flags
NO_FLAGS = 0
INVISIBLE = 1        # 2^0
HIDDEN = 2           # 2^1
PRINT = 4            # 2^2
NO_ZOOM = 8          # 2^3
NO_ROTATE = 16       # 2^4
NO_VIEW = 32         # 2^5
```

## Working with Annotations on Pages

```python
# Read annotations
page = reader.pages[0]
annots = page.annotations

if annots:
    for annot in annots:
        print(annot.get("/Subtype"))
        print(annot.get("/Rect"))
        print(annot.get("/Contents"))

# Clear annotations
page.annotations = []

# Set annotations
page.annotations = [highlight, free_text, link]
```

## Removing Annotations

```python
# Remove all annotations from all pages
writer.remove_annotations()

# Remove from specific pages
writer.remove_annotations(page_numbers=[0, 1, 2])

# Remove links only
writer.remove_links()
```

## Low-Level Access

All annotations are `DictionaryObject` — set raw PDF keys for unsupported features:

```python
from pypdf.generic import NameObject, TextStringObject

annot = Highlight(rect=[100, 700, 300, 720], page=page)
annot[NameObject("/Title")] = TextStringObject("Author")
annot[NameObject("/CreationDate")] = TextStringObject("D:20240101000000")
```

# Annotations

All pypdf annotation classes live in `pypdf.annotations` and wrap
`DictionaryObject`s — unset attributes can be set directly on the object.

PDF 2.0 defines many subtypes (Text, Link, FreeText, Line, Square, Circle,
Polygon, PolyLine, Highlight, Underline, Squiggly, StrikeOut, Caret, Stamp,
Ink, Popup, FileAttachment, Sound, Movie, Screen, Widget, PrinterMark,
TrapNet, Watermark, 3D, Redact, Projection, RichMedia). pypdf provides
convenience classes for the common ones.

Note: some annotations are invisible by default (e.g. polylines — transparent
default color). Add a `/C` color array (1 = grayscale, 3 = RGB, 4 = CMYK;
values 0.0–1.0) to make them visible:

```python
from pypdf.generic import ArrayObject, FloatObject, NameObject
annotation[NameObject("/C")] = ArrayObject([FloatObject(0.9), FloatObject(0.1), FloatObject(0)])
```

## Adding annotations

`writer.add_annotation(page_number, annotation)` — int page index or
PageObject; returns the inserted object.

## FreeText

```python
from pypdf.annotations import FreeText
from pypdf.constants import AnnotationFlag

annotation = FreeText(
    text="Hello World\nThis is the second line!",
    rect=(50, 550, 200, 650),
    font="Arial",
    bold=True,
    italic=True,
    font_size="20pt",
    font_color="00ff00",
    border_color="0000ff",
    background_color="cdcdcd",
)
annotation.flags = AnnotationFlag.PRINT
writer.add_annotation(page_number=0, annotation=annotation)
```

## Text (sticky note)

```python
from pypdf.annotations import Text
annotation = Text(
    text="Hello World\nThis is the second line!",
    rect=(50, 550, 200, 650),
    open=True,
)
```

## Line

```python
from pypdf.annotations import Line
annotation = Line(
    text="Hello World\nLine2",
    rect=(50, 550, 200, 650),
    p1=(50, 550),
    p2=(200, 650),
)
```

## PolyLine / Polygon

```python
from pypdf.annotations import PolyLine, Polygon
annotation = PolyLine(vertices=[(50, 550), (200, 650), (70, 750), (50, 700)])
annotation = Polygon(vertices=[(50, 550), (200, 650), (70, 750), (50, 700)])
```

Both default to a transparent color — set `/C` explicitly to see them.

## Rectangle / Ellipse

```python
from pypdf.annotations import Rectangle, Ellipse

rect = Rectangle(rect=(50, 550, 200, 650))
rect = Rectangle(rect=(50, 550, 200, 650), border_color="ff0000")  # visible border
rect = Rectangle(rect=(50, 550, 200, 650), interior_color="ff0000")  # fill

ellipse = Ellipse(rect=(50, 550, 200, 650))
```

The PDF "Square" subtype does not have to be square — pypdf calls it
`Rectangle`.

## Popup

Use the object returned by `add_annotation()` as the popup's parent:

```python
from pypdf.annotations import Popup, Text

text_annotation = writer.add_annotation(
    0, Text(text="note", rect=(50, 550, 200, 650), open=True)
)
popup = Popup(rect=(50, 550, 200, 650), open=True, parent=text_annotation)
```

## Link

External URL or internal page target:

```python
from pypdf.annotations import Link
from pypdf.generic import Fit

# External
annotation = Link(rect=(50, 550, 200, 650), url="https://example.com/")

# Internal — target page index plus a Fit view
annotation = Link(
    rect=(50, 550, 200, 650),
    target_page_index=1,
    fit=Fit(fit_type="/FitH", fit_args=(123,)),
    border=[0, 0, 2],
)
```

## Highlight

Text-markup annotations need "quad points" — the exact coordinates of the
highlighted text:

```python
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject

rect = (50, 550, 200, 650)
quad_points = [rect[0], rect[1], rect[2], rect[1], rect[0], rect[3], rect[2], rect[3]]
annotation = Highlight(
    rect=rect,
    quad_points=ArrayObject([FloatObject(q) for q in quad_points]),
)
```

## Reading annotations

```python
for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            obj = annotation.get_object()
            print({"subtype": obj["/Subtype"], "location": obj["/Rect"]})
```

Common subtypes: `/Text` (contents in `"/Contents"`), `/Highlight`
(`/QuadPoints`), `/FileAttachment` (`/FS` file spec, `"/EF"/"F"` data),
`/Widget` (form field widgets), `/Popup`, `/Stamp`.

## Removing

```python
writer.remove_links()
writer.remove_annotations(subtypes="/Widget")  # list or single subtype; None = all
```

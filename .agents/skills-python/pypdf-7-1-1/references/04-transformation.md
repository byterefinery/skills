# Transformation

Affine transformation matrices for page content. The matrix is a compressed
`(a, b, c, d, e, f)` tuple; `Transformation()` starts as the identity.

## Methods

```python
from pypdf import Transformation

t = Transformation()
t.translate(tx=50, ty=0)     # shift
t.scale(sx=0.5, sy=0.5)      # scale (sx, sy keyword args)
t.rotate(45)                 # degrees
t = Transformation().rotate(45).translate(tx=50)   # fluent — each returns Transformation
t2 = t.transform(other)      # compose: t followed by other
```

Each call multiplies onto the existing matrix — order matters:
`scale().translate() != translate().scale()`. There is no `skew()` method in
7.1.1; build a custom matrix via the `ctm` constructor argument
(`Transformation((1, 0, 0.5, 1, 0, 0))` for a horizontal shear) if needed.

## Applying to points

```python
result = t.apply_on([x, y])                 # list[float] in user space
result = t.apply_on([x, y], as_object=True) # NumberObject pair
```

## Using transformations

```python
# On a page
page.add_transformation(Transformation().scale(sx=2, sy=2))

# During page merge (stamps, watermarks, n-up layouts)
page.merge_transformed_page(stamp_page, Transformation().scale(0.5))
```

`page.add_transformation(ctm)` multiplies `ctm` onto the page's content
transform; the mediabox/cropbox are not changed (unlike `page.rotate()`).

## Example: 4x4 n-up layout

```python
from pypdf import PaperSize, PdfReader, PdfWriter, Transformation

reader = PdfReader("card.pdf")
source = reader.pages[0]

writer = PdfWriter()
dest = writer.add_blank_page(
    width=PaperSize.A4.height, height=PaperSize.A4.width  # rotated A4
)
for x in range(4):
    for y in range(4):
        t = Transformation().translate(
            x * PaperSize.A8.height, y * PaperSize.A8.width
        )
        dest.merge_transformed_page(source, t)
writer.write("nup.pdf")
```

## Gotchas

- Transformations act on content coordinates, not page boxes — combining
  `merge_page` with transformations can yield cropped output; use
  `expand=True` or pre-translate.
- `rotate()` on Transformation takes a plain number (any float), while
  `PageObject.rotate()` expects multiples of 90.

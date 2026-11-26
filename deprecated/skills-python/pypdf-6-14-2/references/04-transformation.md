# Transformation

## Overview

`Transformation` applies affine transformations to page content. Transformations are composable and operate on a 6-element compressed matrix `(a, b, c, d, e, f)` representing:

```
| a  c  e |
| b  d  f |
| 0  0  1 |
```

## Construction

```python
from pypdf import Transformation

# Identity (no change)
t = Transformation()

# From compressed matrix
t = Transformation(ctm=(2, 0, 0, 2, 100, 100))

# From full matrix
t = Transformation.compress((
    (2, 0, 0),
    (0, 2, 0),
    (100, 100, 1),
))
```

## Scale

```python
# Uniform scale
t = Transformation().scale(2)       # 2x both axes
t = Transformation().scale(sx=2, sy=2)

# Non-uniform scale
t = Transformation().scale(sx=2, sy=0.5)

# Shrink
t = Transformation().scale(0.5)
```

## Translate

```python
# Translate by (x, y)
t = Transformation().translate(100, 100)
t = Transformation().translate(tx=100, ty=100)

# Negative translation (move left/up)
t = Transformation().translate(-50, -50)
```

## Rotate

```python
# Rotate by angle (degrees)
t = Transformation().rotate(45)
t = Transformation().rotate(90)
t = Transformation().rotate(-30)

# Note: page.rotate() only accepts multiples of 90
# Transformation.rotate() accepts any angle
```

## Compose

```python
# Chain operations (applied left to right)
t = Transformation().scale(2, 2).translate(100, 100).rotate(45)

# Compose two transformations
t1 = Transformation().scale(2, 2)
t2 = Transformation().translate(100, 100)
composed = t1.transform(t2)
```

Order matters: `scale().translate()` ≠ `translate().scale()`.

## Matrix Access

```python
t = Transformation().scale(2, 2).translate(100, 100)

# Full matrix as tuple of tuples
matrix = t.matrix
# ((2.0, 0.0, 0), (0.0, 2.0, 0), (100.0, 100.0, 1))

# Compressed matrix (a, b, c, d, e, f)
ctm = t.ctm
# (2.0, 0.0, 0.0, 2.0, 100.0, 100.0)
```

## Apply to Points

```python
t = Transformation().scale(2, 2).translate(100, 100)

# Apply to a point [x, y]
result = t.apply_on([0, 0])
# [100.0, 100.0]

# Apply and return as PDF objects
result = t.apply_on([0, 0], as_object=True)
```

## Apply to Pages

```python
from pypdf import PdfReader, Transformation

reader = PdfReader("input.pdf")
page = reader.pages[0]

# Apply transformation to page content
page.add_transformation(Transformation().scale(0.5, 0.5))
page.add_transformation(Transformation().translate(50, 50))

# Merge with transformation
page2 = reader.pages[1]
page.merge_transformed_page(page2, Transformation().scale(0.5))
```

## Common Patterns

```python
# Fit page to half size in corner
t = Transformation().scale(0.5, 0.5)
page.add_transformation(t)

# Center a scaled page
page_width = float(page.mediabox.upper_right[0])
page_height = float(page.mediabox.upper_right[1])
scale = 0.5
offset_x = (page_width * (1 - scale)) / 2
offset_y = (page_height * (1 - scale)) / 2
t = Transformation().scale(scale, scale).translate(offset_x, offset_y)
page.add_transformation(t)

# Create a 2-up layout
t_left = Transformation().scale(0.5, 0.5).translate(0, 0)
t_right = Transformation().scale(0.5, 0.5).translate(new_width * 0.5, 0)
```

## Internal Representation

```python
# Compressed matrix format: (a, b, c, d, e, f)
# Corresponds to:
# | a  c  e |
# | b  d  f |
# | 0  0  1 |

# Identity: (1, 0, 0, 1, 0, 0)
# Scale(2): (2, 0, 0, 2, 0, 0)
# Translate(100, 50): (1, 0, 0, 1, 100, 50)
```

## String Representation

```python
t = Transformation().scale(2, 2).translate(100, 100)
print(str(t))    # Human-readable
print(repr(t))   # Full representation
```

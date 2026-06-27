# Patches and Shapes

All patches inherit from `matplotlib.patches.Patch` and share common properties:

| Property | Setter | Description |
|----------|--------|-------------|
| `facecolor` / `fc` | `set_facecolor('blue')` | Fill color |
| `edgecolor` / `ec` | `set_edgecolor('black')` | Border color |
| `linewidth` / `lw` | `set_linewidth(2)` | Border width |
| `linestyle` / `ls` | `set_linestyle('--')` | Border style |
| `alpha` | `set_alpha(0.5)` | Transparency |
| `zorder` | `set_zorder(3)` | Draw order |
| `hatch` | `set_hatch('//')` | Hatch pattern |

## Rectangle

```python
from matplotlib.patches import Rectangle

rect = Rectangle((x0, y0), width, height,
                 facecolor='blue', edgecolor='black',
                 linewidth=2, alpha=0.5)
ax.add_patch(rect)
```

## Circle and Ellipse

```python
from matplotlib.patches import Circle, Ellipse

# Circle: center (x, y), radius
circle = Circle((cx, cy), radius, facecolor='red', alpha=0.3)
ax.add_patch(circle)

# Ellipse: center, width, height, angle in degrees
ellipse = Ellipse((cx, cy), width=4, height=2, angle=30,
                  facecolor='green', edgecolor='black')
ax.add_patch(ellipse)
```

## Polygon

```python
from matplotlib.patches import Polygon

# Define vertices as list of (x, y) tuples
vertices = [(0, 0), (1, 0.5), (2, 0), (1.5, -1), (0.5, -1)]
poly = Polygon(vertices, closed=True, facecolor='orange', alpha=0.6)
ax.add_patch(poly)

# Regular polygon
from matplotlib.patches import RegularPolygon
rp = RegularPolygon((cx, cy), numVertices=6, radius=1,
                    orientation=np.pi/6, facecolor='purple')
ax.add_patch(rp)
```

## Wedge (Pie Slice / Arc Sector)

```python
from matplotlib.patches import Wedge

wedge = Wedge((cx, cy), r, theta1=0, theta2=90,
              facecolor='yellow', edgecolor='black')
ax.add_patch(wedge)
```

## FancyBboxPatch (Rounded Rectangle)

```python
from matplotlib.patches import FancyBboxPatch

# Simple rounded box
fancy = FancyBboxPatch((x0, y0), width, height,
                       boxstyle="round,pad=0.1",
                       facecolor='lightblue', edgecolor='navy')
ax.add_patch(fancy)
```

### Box styles

| Style | Parameters |
|-------|------------|
| `'square'` | None (sharp corners) |
| `'round'` | `pad=0.1`, `rounding_size=0.1` |
| `'circle'` | `pad=0.1` |
| `'dcircle'` | Double-circle; `pad=0.1` |
| `'larrow'` / `'rarrow'` | Arrow-shaped; `pad=0.3` |
| `'darrow'` | Double arrow; `pad=0.3` |
| `'sawtooth'` | `pad=0.3`, `numteeth=15` |
| `'round4'` | Independent corner radii |
| `'round_tooth'` | `pad=0.3` |
| `'assel'` | `pad=0.3` |

## Arrows

```python
from matplotlib.patches import FancyArrow, FancyArrowPatch
from matplotlib.path import Path

# Simple arrow (position-based)
arrow = FancyArrow(x, y, dx, dy, width=0.2,
                   facecolor='red', edgecolor='black')
ax.add_patch(arrow)

# FancyArrowPatch (point-to-point, with curved paths)
arrow = FancyArrowPatch(
    posA=(x1, y1), posB=(x2, y2),
    arrowstyle='->,head_width=0.3,head_length=0.2',
    connectionstyle='arc3,rad=0.3',
    color='blue', linewidth=2
)
ax.add_patch(arrow)
```

### Arrow styles

| Style | Description |
|-------|-------------|
| `'-'` | No arrowhead |
| `'->'` | Simple arrow |
| `'-|>'` | Arrow with tail bar |
| `'<-|'` | Reversed tail bar |
| `'<->'` | Double-headed |
| `'<|-|>'` | Double with bars |
| `'fancy'` | Fancy curved head |
| `'wedge'` | Wedge shape |
| `'simple,head_length=0.6'` | Simple with params |

## Annotation Arrows (via annotate)

```python
# Arrow between two points
ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle='->',
                connectionstyle='arc3,rad=0.2',
                color='red',
                linewidth=2
            ))
```

## ConnectionPatch (between axes)

```python
from matplotlib.patches import ConnectionPatch

# Connect points between two subplots
con = ConnectionPatch(xyA=(x1, y1), xyB=(x2, y2),
                      coordsA='data', coordsB='data',
                      axesA=ax1, axesB=ax2,
                      arrowstyle='->', color='red')
ax1.add_artist(con)
```

## PathPatch (arbitrary paths)

```python
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np

# Create a custom path
verts = [
    (0., 0.),   # P0
    (0.2, 1.),  # P1
    (1., 0.8),  # P2
    (0.8, 0.),  # P3
]
codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
path = Path(verts, codes)

patch = PathPatch(path, facecolor='none', edgecolor='blue', linewidth=2)
ax.add_patch(patch)
```

## Annulus (Ring)

```python
from matplotlib.patches import Annulus

ring = Annulus((cx, cy), r=1.0, width=0.3,
               facecolor='gold', edgecolor='black')
ax.add_patch(ring)
```

## Arc (Partial Circle)

```python
from matplotlib.patches import Arc

arc = Arc((cx, cy), width=2, height=1, angle=0,
          theta1=0, theta2=180, color='red', linewidth=2)
ax.add_patch(arc)
```

## Shadow Effect

```python
from matplotlib.patches import Rectangle, Shadow

rect = Rectangle((0.1, 0.1), 0.5, 0.5, facecolor='blue')
shadow = Shadow(rect, dx=0.02, dy=-0.02)
ax.add_patch(shadow)
ax.add_patch(rect)
```

## Hatch Patterns

Apply to any patch's `hatch` parameter:

| Pattern | Symbol |
|---------|--------|
| Vertical lines | `'\\'` |
| Horizontal lines | `'/'` |
| Cross-hatch | `'x'` |
| Dots | `'.'` |
| Plus | `'+'` |
| Star | `'*'` |
| Vertical bars | `\|` |
| Horizontal bars | `'-'` |
| Grid | `'\|/'` or `'\\|'` |

```python
rect = Rectangle((0, 0), 1, 1, facecolor='none',
                 edgecolor='black', hatch='///', linewidth=2)
ax.add_patch(rect)
```

## Collections (Batch Drawing)

For many similar patches, use collections for performance:

```python
from matplotlib.collections import PatchCollection

patches = [Circle((x, y), 0.1) for x, y in zip(xs, ys)]
collection = PatchCollection(patches, facecolors='blue', alpha=0.5)
ax.add_collection(collection)
```

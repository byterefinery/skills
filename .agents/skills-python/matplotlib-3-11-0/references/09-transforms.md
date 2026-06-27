# Transforms and Coordinate Systems

## Coordinate Systems Overview

Matplotlib has multiple coordinate systems, each useful in different contexts:

| System | Transform | Range | Use Case |
|--------|-----------|-------|----------|
| Data | `ax.transData` | Data units | Plotting data points |
| Axes fraction | `ax.transAxes` | (0,0)–(1,1) | Elements relative to axes |
| Figure fraction | `fig.transFigure` | (0,0)–(1,1) | Elements relative to figure |
| Display (pixels) | `IdentityTransform()` | Pixel coordinates | Low-level positioning |
| X-data, Y-axes | `ax.get_xaxis_transform()` | x=data, y=0–1 | Horizontal spans |
| X-axes, Y-data | `ax.get_yaxis_transform()` | x=0–1, y=data | Vertical spans |

## Common Transform Usage

```python
import matplotlib.transforms as mtransforms
```

### Axes-relative positioning

Place elements that stay fixed relative to the axes regardless of data limits:

```python
# Text at 50% x, 90% y of axes area
ax.text(0.5, 0.9, 'Label', transform=ax.transAxes,
        ha='center', va='top')

# Rectangle covering right half of axes
from matplotlib.patches import Rectangle
rect = Rectangle((0.5, 0), 0.5, 1, transform=ax.transAxes,
                 facecolor='yellow', alpha=0.2)
ax.add_patch(rect)
```

### Mixed coordinate systems

```python
# Vertical line at x=5 (data), spanning full y-range (axes fraction)
ax.axvline(x=5, color='red', linestyle='--')
# Equivalent explicit:
line = mlines.Line2D([5, 5], [0, 1], transform=ax.get_yaxis_transform(),
                     color='red', linestyle='--')
ax.add_line(line)
```

### Figure-relative positioning

```python
# Text at bottom-center of figure
fig.text(0.5, 0.02, 'Source: Data Inc.', ha='center', transform=fig.transFigure)
```

## Affine2D Transformations

`Affine2D` composes linear transformations (translate, scale, rotate, skew):

```python
from matplotlib.transforms import Affine2D

# Create a transformation
t = Affine2D()
t.translate(10, 0)       # Shift right by 10 data units
t.scale(2, 1)            # Double x-axis
t.rotate_degrees(45)     # Rotate 45 degrees

# Compose with data transform
transform = t + ax.transData

# Use in plotting
ax.plot(x, y, transform=transform)
```

### Common affine operations

| Method | Effect |
|--------|--------|
| `translate(dx, dy)` | Shift by (dx, dy) in data units |
| `scale(sx, sy)` | Scale x and y independently |
| `rotate(theta)` | Rotate by theta radians |
| `rotate_degrees(deg)` | Rotate by degrees |
| `skew_x(deg)` | Skew along x-axis |
| `skew_y(deg)` | Skew along y-axis |

### Composition order matters

```python
# Translate then scale (scale affects translation)
t1 = Affine2D().translate(5, 0).scale(2, 1)

# Scale then translate (translation is in scaled space)
t2 = Affine2D().scale(2, 1).translate(5, 0)
# These produce different results!
```

## Transform Composition with + Operator

The `+` operator composes a non-affine transform on the left with an affine on the right:

```python
# Log scale + translation
transform = ax.transData + Affine2D().translate(1, 0)

# Polar to data + scaling
transform = polar_trans + Affine2D().scale(0.5, 0.5)
```

## Bounding Boxes

```python
from matplotlib.transforms import Bbox

# Create a bounding box
bbox = Bbox([[x0, y0], [x1, y1]])

# Transform a bbox
transformed_bbox = bbox.transformed(ax.transData)

# Get tight bounding box of an artist
tight_bbox = ax.get_tightbbox(fig.canvas.get_renderer())
```

## Blitting for Performance

Blitting redraws only changed regions, useful for animations:

```python
fig, ax = plt.subplots()
line, = ax.plot(x, y)
background = fig.canvas.copy_from_bbox(ax.bbox)

def update(new_y):
    fig.canvas.restore_region(background)
    line.set_ydata(new_y)
    ax.draw_artist(line)
    fig.canvas.blit(ax.bbox)
```

## Offset Transforms

Combine data coordinates with display offsets:

```python
# Text offset by 10 pixels from data point
offset = mtransforms.offset_copy(ax.transData, x=10, y=10, units='dots')
ax.text(x, y, 'Label', transform=offset)
```

## Custom Transforms for Annotations

```python
# Arrow from data coords to axes fraction
ax.annotate('Peak',
    xy=(x_peak, y_peak),          # Data coords
    xycoords='data',
    xytext=(0.95, 0.95),          # Axes fraction
    textcoords='axes fraction',
    arrowprops=dict(arrowstyle='->', color='red'))
```

## Transform Tree

Matplotlib's transform system is a tree structure:

```
BboxTransform (figure pixels)
└── BlendedTransform
    ├── xaxis (data → display)
    └── yaxis (data → display)
        └── LogTransform (for log scale)
```

Each node invalidates its parents when changed, enabling efficient recomputation. For most users, the named transforms (`transData`, `transAxes`, etc.) are sufficient.

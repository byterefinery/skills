# Image and Contour Plots

## imshow()

Display 2D arrays as images:

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.random.randn(10, 10)
im = ax.imshow(data, cmap='viridis')
fig.colorbar(im, ax=ax)
```

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `cmap` | Colormap name or Colormap object |
| `norm` | Normalization (e.g., `LogNorm`, `BoundaryNorm`) |
| `vmin`, `vmax` | Data value range for colormap |
| `aspect` | `'auto'`, `'equal'`, or numeric ratio |
| `origin` | `'upper'` (default) or `'lower'` |
| `interpolation` | `'nearest'`, `'bilinear'`, `'bicubic'`, etc. |
| `extent` | `[left, right, bottom, top]` in data coordinates |

### extent for labeled axes

```python
# Map array indices to actual coordinate values
im = ax.imshow(data, extent=[x_min, x_max, y_min, y_max],
               origin='lower', cmap='viridis')
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
```

### Displaying images

```python
# From file
from matplotlib.image import imread
img = imread('photo.png')
ax.imshow(img)

# Grayscale
gray = np.dot(img[..., :3], [0.2989, 0.5870, 0.1140])
ax.imshow(gray, cmap='gray', vmin=0, vmax=255)
```

## pcolormesh()

Pseudo-color plot of 2D arrays — preferred over `imshow` for data with labeled axes:

```python
# Regular grid
X, Y = np.meshgrid(x, y)
Z = np.sin(X) * np.cos(Y)
mesh = ax.pcolormesh(X, Y, Z, shading='auto', cmap='viridis')
fig.colorbar(mesh, ax=ax)
```

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `shading` | `'auto'` (recommended), `'flat'`, `'nearest'`, `'gouraud'` |
| `cmap` | Colormap |
| `norm` | Normalization |
| `vmin`, `vmax` | Color range |
| `edgecolors` | Grid line color (`'face'` hides edges) |
| `linewidth` | Grid line width |

### shading modes

- `'auto'`: Chooses appropriate mode based on input shapes (recommended)
- `'flat'`: Z has one fewer element than X and Y; colors cells
- `'nearest'`: Z same shape as X, Y; each cell takes nearest value
- `'gouraud'`: Smooth interpolation between vertices

### pcolormesh vs imshow

| Feature | `imshow` | `pcolormesh` |
|---------|----------|--------------|
| Coordinate mapping | Array indices → pixels | Explicit X, Y coordinates |
| Irregular grids | No | Yes (with meshgrid) |
| Performance | Faster for large arrays | Slower but more flexible |
| Origin control | `origin='upper'/'lower'` | Natural coordinate order |
| Best for | Images, matrices | Heatmaps with labeled axes |

## contour() and contourf()

Line and filled contour plots:

```python
X, Y = np.meshgrid(np.linspace(-3, 3, 100),
                    np.linspace(-3, 3, 100))
Z = np.sin(X) * np.cos(Y)

# Filled contours
CS = ax.contourf(X, Y, Z, levels=15, cmap='RdYlBu_r')
fig.colorbar(CS, ax=ax)

# Line contours overlaid
CS_lines = ax.contour(X, Y, Z, levels=10, colors='black', linewidths=0.5)
ax.clabel(CS_lines, inline=True, fontsize=8, fmt='%.2f')
```

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `levels` | Number of levels or list of level values |
| `cmap` | Colormap (contourf only) |
| `colors` | Line colors (contour only) |
| `linewidths` | Line widths |
| `alpha` | Transparency |
| `extend` | `'neither'`, `'min'`, `'max'`, `'both'` |

### Specifying contour levels

```python
# Specific level values
levels = [-1, -0.5, 0, 0.5, 1]
CS = ax.contourf(X, Y, Z, levels=levels, cmap='viridis')

# Logarithmic levels
import numpy as np
levels = np.logspace(-2, 2, 20)
CS = ax.contourf(X, Y, Z, levels=levels, norm=LogNorm())
```

## quiver()

Vector field plots:

```python
X, Y = np.meshgrid(np.linspace(-2, 2, 20),
                    np.linspace(-2, 2, 20))
U = -X  # x-component of vectors
V = Y   # y-component of vectors

q = ax.quiver(X, Y, U, V, cmap='viridis')
fig.colorbar(q, ax=ax)
```

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `units` | `'width'`, `'height'`, `'dots'`, `'inches'` |
| `scale` | Auto-scaling factor (larger = shorter arrows) |
| `scale_units` | Units for scale |
| `color` / `c` | Arrow color or array for colormap |
| `cmap` | Colormap when c is an array |
| `width` | Arrow shaft width |
| `headwidth`, `headlength` | Arrow head dimensions |
| `pivot` | `'tail'`, `'middle'`, `'tip'` |

## streamplot()

Streamlines of vector fields:

```python
ax.streamplot(X, Y, U, V,
              color=U, cmap='viridis',
              density=1.5,      # Line density
              linewidth=2,
              arrowsize=1.5)
```

## spy()

Sparse matrix visualization:

```python
import scipy.sparse as sp
matrix = sp.random(100, 100, density=0.01)
ax.spy(matrix, markersize=2, precision=0)
ax.set_aspect('equal')
```

## matshow()

Matrix display (convenience wrapper around imshow):

```python
ax.matshow(data, fignum=1, cmap='viridis')
```

## hexbin()

Hexagonal binning for scatter data:

```python
x = np.random.randn(10000)
y = x + np.random.randn(10000) * 0.5

hb = ax.hexbin(x, y, gridsize=30, cmap='Blues', mincnt=1)
fig.colorbar(hb, ax=ax, label='Count')
```

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `gridsize` | Number of hexagons in x direction (default 100) |
| `cmap` | Colormap |
| `mincnt` | Minimum count to display a hexagon |
| `C` | Values to aggregate (default: count) |
| `reduce_C_function` | Aggregation function (`np.mean`, `np.max`, etc.) |
| `extent` | `[xmin, xmax, ymin, ymax]` |

## hist2d()

2D histogram:

```python
H, xedges, yedges, im = ax.hist2d(x, y, bins=30, cmap='viridis')
fig.colorbar(im, ax=ax, label='Count')
```

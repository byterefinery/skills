# Colors and Colormaps

## Color Specification

Matplotlib accepts many color formats:

| Format | Example | Description |
|--------|---------|-------------|
| Single letter | `'r'`, `'g'`, `'b'`, `'c'`, `'m'`, `'y'`, `'k'`, `'w'` | Basic colors |
| RGB tuple | `(0.1, 0.2, 0.5)` | Values in [0, 1] |
| RGBA tuple | `(0.1, 0.2, 0.5, 0.8)` | With alpha |
| Hex string | `'#FF5733'` | CSS hex color |
| Named color | `'steelblue'`, `'coral'` | CSS4 + Tableau + XKCD names |
| Grayscale | `'0.5'` | String float in [0, 1] |
| Cycle color | `'C0'`–`'C9'` | Default property cycle colors |

### Named colors

Matplotlib recognizes:
- **Single-letter**: `r`, `g`, `b`, `c`, `m`, `y`, `k`, `w`
- **CSS4 colors**: ~140 names (e.g., `'darkorange'`, `'mediumseagreen'`)
- **Tableau colors**: 10 base + variants (`'tab:blue'`, `'tab:orange'`, etc.)
- **XKCD colors**: ~900 crowd-sourced names (`'xkcd:baby poop green'`)

```python
from matplotlib import colors
colors.is_color_like('steelblue')   # True
colors.to_rgba('C0')                 # (0.12..., 0.47..., 0.71..., 1.0)
colors.to_hex('#FF5733')             # '#ff5733'
```

## Default Color Cycle

The default cycle uses `C0` through `C9` (tab10 palette):

| Index | Color | Hex |
|-------|-------|-----|
| C0 | Blue | #1f77b4 |
| C1 | Orange | #ff7f0e |
| C2 | Green | #2ca02c |
| C3 | Red | #d62728 |
| C4 | Purple | #9467bd |
| C5 | Brown | #8c564b |
| C6 | Pink | #e377c2 |
| C7 | Gray | #7f7f7f |
| C8 | Olive | #bcbd22 |
| C9 | Cyan | #17becf |

Customize via rcParams:
```python
import matplotlib as mpl
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#e41a1c', '#377eb8', '#4daf4a'])
```

## Colormaps

Access via `matplotlib.colormaps` (dict-like registry):

```python
from matplotlib import colormaps
cmap = colormaps['viridis']
colors_list = list(colormaps)  # All available colormap names
```

### Perceptually Uniform (recommended for data)

| Name | Type | Use Case |
|------|------|----------|
| `viridis` | Sequential | Default; colorblind-safe, print-friendly |
| `plasma` | Sequential | Vibrant alternative to viridis |
| `inferno` | Sequential | Dark-to-bright, good for dark backgrounds |
| `magma` | Sequential | Similar to inferno, slightly different tone |
| `cividis` | Sequential | Colorblind-safe, high contrast |

### Diverging (for data with meaningful zero/middle)

| Name | Use Case |
|------|----------|
| `coolwarm` | General diverging; colorblind-safe |
| `RdBu_r` | Red-blue; reversed for intuitive warm=red |
| `Seismic` | Earthquake-style; white center |
| `PiYG` | Purple-orange-green; colorblind-safe |
| `PuOr` | Purple-orange; perceptually uniform |

### Cyclic (for periodic data)

| Name | Use Case |
|------|----------|
| `twilight` | Phase angles, wind direction |
| `hsv` | Rainbow cycle (avoid for data magnitude) |
| `terrain` | Topographic feel |

### Other built-in colormaps

`gray`, `binary`, `gist_earth`, `ocean`, `rainbow`, `jet` (legacy, avoid), `nipy_spectral`, `cubehelix`, `turbo`.

### Reversing colormaps

```python
cmap = colormaps['viridis_r']  # Append '_r' to any name
# Or: cmap = colormaps['viridis'].reversed()
```

## Using Colormaps

```python
# In scatter
sc = ax.scatter(x, y, c=values, cmap='viridis', vmin=0, vmax=100)
fig.colorbar(sc, label='Value')

# In imshow / pcolormesh
im = ax.imshow(data, cmap='plasma', norm=norm)
fig.colorbar(im, ax=ax)

# Manual mapping
cmap = colormaps['viridis']
colors = cmap(normalized_values)  # Returns (N, 4) RGBA array
single_color = cmap(0.5)          # Single RGBA tuple
```

## Normalization

Maps data values to [0, 1] for colormap lookup:

```python
from matplotlib.colors import Normalize, LogNorm, SymLogNorm, BoundaryNorm, TwoSlopeNorm

# Linear (default)
norm = Normalize(vmin=0, vmax=100)

# Logarithmic
norm = LogNorm(vmin=1, vmax=1e6)

# Symmetric log (handles zero and negative values)
norm = SymLogNorm(linthresh=1e-3, vmin=-1e6, vmax=1e6)

# Discrete boundaries
norm = BoundaryNorm(boundaries=[0, 25, 50, 75, 100], ncolors=256)

# Two-slope (different scaling above/below center)
norm = TwoSlopeNorm(vcenter=0, vmin=-10, vmax=100)

# Power
from matplotlib.colors import PowerNorm
norm = PowerNorm(gamma=0.5, vmin=0, vmax=1)
```

Use with any mappable:
```python
im = ax.imshow(data, cmap='viridis', norm=LogNorm(vmin=1))
```

## Creating Custom Colormaps

```python
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import numpy as np

# From a list of colors
colors = ['#67001d', '#b2182b', '#d6604d', '#f4a582', '#fddbc7',
          '#f7f7f7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac', '#053061']
cmap = ListedColormap(colors, name='my_cmap')

# From RGB tuples
cmap = LinearSegmentedColormap.from_list('custom', [(0, 0, 1), (1, 0, 0)])

# Register globally
import matplotlib as mpl
mpl.colormaps.register(cmap)
```

## Color Sequences

Named sequences for discrete data:

```python
from matplotlib import color_sequences

# Access by name
colors = color_sequences['tab10']    # 10 colors
colors = color_sequences['Set2']     # From ColorBrewer
colors = color_sequences['pastel1']
colors = color_sequences['dark']
colors = color_sequences['colorblind']
```

Available sequences: `tab10`, `tab20`, `tab20b`, `tab20c`, `Set1`–`Set3`, `Pastel1`, `Pastel2`, `Dark2`, `accent`, `base`, `bright`, `colorblind`, `css`, `tableau`, `xkcd`.

## Alpha (Transparency)

```python
ax.plot(x, y, alpha=0.5)           # Line transparency
ax.scatter(x, y, alpha=0.3)        # Point transparency
ax.bar(x, h, alpha=0.7)            # Bar transparency
ax.imshow(data, alpha=0.8)         # Image transparency
```

Alpha applies to the entire artist. For per-point alpha in scatter, use the `c` parameter with RGBA tuples.

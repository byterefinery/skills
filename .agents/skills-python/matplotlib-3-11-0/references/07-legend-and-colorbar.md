# Legends and Colorbars

## Legends

### Basic legend

```python
ax.plot(x, y1, label='Series A')
ax.plot(x, y2, label='Series B')
ax.legend()  # Auto-uses labels from plot calls
```

### Legend location

```python
ax.legend(loc='upper right')    # Default
ax.legend(loc='best')           # Auto-picks least overlapping
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5))  # Outside axes
```

| Location string | Numeric code |
|-----------------|-------------|
| `'best'` | 0 |
| `'upper right'` | 1 |
| `'upper left'` | 2 |
| `'lower left'` | 3 |
| `'lower right'` | 4 |
| `'right'` | 5 |
| `'center left'` | 6 |
| `'center right'` | 7 |
| `'lower center'` | 8 |
| `'upper center'` | 9 |
| `'center'` | 10 |

### Legend outside axes

```python
# Outside to the right
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5))
fig.tight_layout()  # May need to adjust: rect=[0, 0, 0.85, 1]

# Outside above
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, frameon=False)
```

### Legend styling

```python
ax.legend(
    loc='best',
    fontsize=10,
    frameon=True,            # Show border
    framealpha=0.9,          # Border transparency
    edgecolor='gray',
    facecolor='white',
    shadow=False,
    ncol=2,                  # Number of columns
    title='Groups',
    title_fontsize=11,
    markerscale=1.0,         # Marker size relative to plot
    handletextpad=0.5,       # Space between handle and text
    labelspacing=0.3         # Vertical spacing between entries
)
```

### Custom legend handles

```python
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# Manual legend
handles = [
    Line2D([0], [0], color='blue', linewidth=2, label='Line'),
    Line2D([0], [0], color='red', marker='o', lw=0, label='Points'),
    Patch(facecolor='yellow', edgecolor='black', label='Shaded'),
]
ax.legend(handles=handles, loc='upper right')
```

### Selective legend entries

Use `_nolegend_` as label to exclude specific elements:

```python
ax.plot(x, y1, label='Show this')
ax.plot(x, y2, label='_nolegend_')  # Hidden from legend
ax.plot(x, y3, label='And this')
ax.legend()
```

### Multiple legends on one axes

```python
leg1 = ax.legend(handles=[line1, line2], loc='upper right', title='Group 1')
ax.add_artist(leg1)  # Keep first legend
leg2 = ax.legend(handles=[line3, line4], loc='lower right', title='Group 2')
```

## Colorbars

### Basic colorbar

```python
# From a mappable (scatter, imshow, pcolormesh, contourf)
im = ax.imshow(data, cmap='viridis', vmin=0, vmax=100)
cbar = fig.colorbar(im, ax=ax, label='Temperature (°C)')

# Or pyplot style
plt.colorbar(im, ax=ax)
```

### Colorbar orientation and sizing

```python
# Vertical (default)
fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.8)

# Horizontal
fig.colorbar(im, ax=ax, orientation='horizontal', fraction=0.05, pad=0.1)

# Custom size
cbar = fig.colorbar(im, ax=ax, aspect=20, shrink=0.7)
```

### Colorbar parameters

| Parameter | Description |
|-----------|-------------|
| `orientation` | `'vertical'` or `'horizontal'` |
| `label` | Label text for the colorbar |
| `ticks` | List of tick locations or a Locator |
| `format` | Format string or Formatter |
| `shrink` | Scale factor (0–1) for colorbar size |
| `aspect` | Ratio of long to short dimension |
| `pad` | Spacing between colorbar and axes |
| `fraction` | Fraction of original axes used by colorbar |
| `extend` | `'neither'`, `'both'`, `'min'`, `'max'` (triangular ends) |
| `extendfrac` | Size of triangular extensions |
| `drawedges` | Draw lines at color boundaries |
| `spacing` | `'uniform'` or `'proportional'` |

### Custom colorbar ticks and labels

```python
cbar = fig.colorbar(im, ax=ax)
cbar.set_ticks([0, 25, 50, 75, 100])
cbar.set_ticklabels(['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])

# Or using a formatter
from matplotlib.ticker import FuncFormatter
cbar.ax.yaxis.set_major_formatter(
    FuncFormatter(lambda v, p: f'{v:.0f}°C')
)
```

### Discrete colorbar

```python
from matplotlib.colors import BoundaryNorm, ListedColormap

colors = ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
cmap = ListedColormap(colors)
norm = BoundaryNorm([0, 20, 40, 60, 80, 100], ncolors=256)

im = ax.imshow(data, cmap=cmap, norm=norm)
cbar = fig.colorbar(im, ax=ax, ticks=[10, 30, 50, 70, 90])
cbar.set_ticklabels(['0–20', '20–40', '40–60', '60–80', '80–100'])
```

### Colorbar for contour plots

```python
CS = ax.contourf(X, Y, Z, levels=15, cmap='RdYlBu_r')
cbar = fig.colorbar(CS, ax=ax)
cbar.set_label('Elevation (m)')
```

### Multiple colorbars in one figure

```python
# Create dedicated axes for each colorbar
from matplotlib import colors
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2)
norm = colors.Normalize(vmin=0, vmax=100)

im1 = ax1.imshow(data1, cmap='viridis', norm=norm)
im2 = ax2.imshow(data2, cmap='plasma', norm=norm)

# Shared colorbar
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
fig.colorbar(im1, cax=cbar_ax, label='Value')
```

### Diverging colorbar with center at zero

```python
from matplotlib.colors import TwoSlopeNorm

norm = TwoSlopeNorm(vcenter=0, vmin=-100, vmax=100)
im = ax.imshow(data, cmap='RdBu_r', norm=norm)
fig.colorbar(im, ax=ax, label='Anomaly')
```

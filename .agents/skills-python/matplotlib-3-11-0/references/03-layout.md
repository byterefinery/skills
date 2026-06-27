# Layout: Subplots, GridSpec, and Constrained Layout

## plt.subplots()

The most common way to create multiple axes:

```python
fig, ax = plt.subplots()                    # Single axes
fig, axes = plt.subplots(2, 3)              # 2×3 grid, axes is (2,3) array
fig, axes = plt.subplots(1, 1)              # axes is scalar (not array)
fig, axes = plt.subplots(2, 1, squeeze=False)  # Always returns array
```

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `nrows`, `ncols` | Grid dimensions |
| `figsize=(w, h)` | Figure size in inches |
| `dpi` | Dots per inch |
| `sharex`, `sharey` | Share axis limits and ticks (`True`, `'all'`, `'row'`, `'col'`) |
| `gridspec_kw` | Dict passed to `GridSpec` (e.g., `{'width_ratios': [1, 2]}`) |
| `subplot_kw` | Dict passed to each subplot creation |
| `constrained_layout=True` | Auto-adjust spacing (preferred over `tight_layout`) |
| `layout='tight'` | Legacy tight layout |
| `squeeze` | If False, always returns 2D array even for single axes |

### Shared axes behavior

```python
fig, axes = plt.subplots(2, 3, sharex=True)
# All rows share x-axis limits; setting xlim on one affects all
# Bottom row x-tick labels are shown; top row are hidden
```

## subplot_mosaic()

Named layout specification — preferred for irregular grids:

```python
fig, axd = plt.subplot_mosaic([
    ['header',  'header'],
    ['left',    'right'],
    ['left',    'bottom'],
], figsize=(10, 8), constrained_layout=True)

axd['header'].set_title('Header spans both columns')
axd['left'].plot(x, y1)
axd['right'].plot(x, y2)
axd['bottom'].hist(data, bins=30)
```

### Mosaic features

- Empty cells: use `None` or `'empty'` for gaps
- Spanning: repeat a name in adjacent cells
- Custom gridspec per subplot: pass dict to `subplot_kw`
- Zero-height/width spines for shared edges: `axd['A'].share_x(axd['B'])`

```python
# With gaps and spanning
fig, axd = plt.subplot_mosaic([
    ['title',   'title',  None],
    ['main',    'side',   'side'],
    ['main',    'bottom', None],
])
axd['title'].axis('off')
```

## GridSpec

Fine-grained control over subplot geometry:

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(3, 3, figure=fig,
                       hspace=0.3, wspace=0.3,
                       height_ratios=[1, 2, 1],
                       width_ratios=[1, 2, 1])

ax1 = fig.add_subplot(gs[0, :])       # Top row, all columns
ax2 = fig.add_subplot(gs[1, 0])       # Middle-left
ax3 = fig.add_subplot(gs[1, 1:3])     # Middle-right (spans 2 cols)
ax4 = fig.add_subplot(gs[2, 0])       # Bottom-left
ax5 = fig.add_subplot(gs[2, 1:])      # Bottom-right
```

### GridSpec slicing

```python
gs[0, :]        # First row, all columns
gs[:, -1]       # All rows, last column
gs[1:3, 1:3]    # Rows 1-2, cols 1-2
gs[0, 0]         # Single cell
```

### SubplotSpec composition

```python
# Combine grid specs with + (overlapping) or & (intersection)
spec = gs[0, 0] + gs[1, 0]  # Union: spans both cells
ax = fig.add_subplot(spec)
```

## add_subfigure() and SubFigures

For grouping related subplots:

```python
fig = plt.figure(constrained_layout=True, figsize=(12, 8))
subfigs = fig.subfigures(2, 1)  # Two vertical subfigures

# Left subfigure
ax_left = subfigs[0].subplots(2, 1)
ax_left[0].set_title('Group A')

# Right subfigure
ax_right = subfigs[1].subplots(2, 2)
ax_right[0, 0].set_title('Group B')
```

## Layout Engines

| Engine | How to enable | Behavior |
|--------|---------------|----------|
| `constrained_layout` | `constrained_layout=True` or `layout='constrained'` | Reactive; adjusts as elements added. Best for complex figures. |
| `tight_layout` | `fig.tight_layout()` or `layout='tight'` | Runs once at call time. Simpler but less adaptive. |
| Manual | `fig.subplots_adjust(left, right, top, bottom, wspace, hspace)` | Full manual control over margins and spacing. |

### constrained_layout tips

- Set it when creating the figure: `plt.subplots(constrained_layout=True)`
- It reacts to element changes — no need to call it again
- Works with `subplot_mosaic`, `subfigures`, and `GridSpec`
- Use `fig.set_constrained_layout_pads(wspace=0.05, hspace=0.05)` for fine-tuning

### tight_layout tips

- Call after all elements are added (titles, colorbars, etc.)
- May not account for all elements (e.g., some annotations)
- Use `pad` and `h_pad`/`w_pad` parameters for spacing control
- `fig.tight_layout(rect=[0, 0, 1, 0.95])` to reserve space for suptitle

## Manual Spacing

```python
# Adjust margins
fig.subplots_adjust(left=0.12, right=0.95, top=0.92, bottom=0.1)
fig.subplots_adjust(wspace=0.3, hspace=0.4)  # Space between subplots

# Per-axes margin control
ax.margins(x=0.05, y=0.1)  # 5% x-margin, 10% y-margin
ax.autoscale(tight=True)    # Remove all margins
```

## Inset Axes

Zoomed-in region within a subplot:

```python
fig, ax = plt.subplots()
ax.plot(x, y)

# Create inset axes (position in axes coordinates)
inset_ax = ax.inset_axes([0.55, 0.15, 0.35, 0.35])  # [x, y, w, h]
inset_ax.plot(x, y)
inset_ax.set_xlim(4, 6)
inset_ax.set_ylim(-1, 1)

# Draw indicator rectangle on parent axes
ax.indicate_inset(inset_ax, edgecolor='gray', alpha=0.5)
```

## Twin Axes

Overlay two axes with different scales:

```python
fig, ax1 = plt.subplots()
ax1.plot(x, y1, 'b-', label='Temperature')
ax1.set_ylabel('Temperature (°C)', color='blue')

ax2 = ax1.twinx()
ax2.plot(x, y2, 'r-', label='Humidity')
ax2.set_ylabel('Humidity (%)', color='red')
```

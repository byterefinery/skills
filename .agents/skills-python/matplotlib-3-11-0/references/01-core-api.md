# Core API: Figure, Axes, Artist Hierarchy

## Object Model

Matplotlib's rendering is a tree of `Artist` objects:

```
Figure
├── Axes (one or more)
│   ├── Line2D
│   ├── Patch (Rectangle, Circle, etc.)
│   ├── Text
│   ├── Image
│   ├── Collection (scatter, contour, etc.)
│   └── Axis (xaxis, yaxis)
│       └── Tick
├── Legend
├── Colorbar
└── Text (suptitle, figtext)
```

Every drawable object inherits from `Artist`. Key properties shared across all artists:

| Property | Setter | Description |
|----------|--------|-------------|
| visible | `set_visible(True/False)` | Toggle visibility |
| alpha | `set_alpha(0.0–1.0)` | Transparency |
| zorder | `set_zorder(N)` | Draw order (higher = on top) |
| transform | `set_transform(t)` | Coordinate transform |
| clip_on | `set_clip_on(True/False)` | Clip to axes bounds |
| animated | `set_animated(True)` | Exclude from static draw |

## pyplot vs Object-Oriented API

### pyplot (state-based)

```python
import matplotlib.pyplot as plt

plt.figure()           # Creates a new figure
plt.plot(x, y)         # Plots on "current" axes
plt.xlabel('X axis')   # Modifies current axes
plt.title('My Plot')
plt.legend()
plt.savefig('fig.png')
plt.show()
```

**When to use**: Quick exploratory plots, interactive notebooks, simple scripts.

**Risks**: Implicit state can target wrong figure/axes in multi-plot code. `plt.plot()` silently uses whatever axes is currently active.

### Object-Oriented (preferred)

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x, y, label='data')
ax.set_xlabel('X axis')
ax.set_title('My Plot')
ax.legend()
fig.savefig('fig.png', bbox_inches='tight')
plt.show()
```

**When to use**: Production code, complex layouts, multiple subplots, any situation where explicit control matters.

### Hybrid (common pattern)

Use pyplot for figure creation, OO for everything else:

```python
fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
for ax in axes.flat:
    ax.plot(x, np.random.randn(100))
    ax.set_title(f'Run {ax.get_subplotspec().get_position(fig)}')
```

## Figure Methods

| Method | Description |
|--------|-------------|
| `fig.add_axes([left, bottom, width, height])` | Add axes at absolute position (0–1 figure coords) |
| `fig.add_subplot(nrows, ncols, index)` | Add subplot in grid |
| `fig.subplots(nrows, ncols, **kwargs)` | Create grid of subplots (returns fig + axes array) |
| `fig.subplot_mosaic(spec)` | Create named subplot layout |
| `fig.subplot2grid(shape, loc, rowspan, colspan)` | Add subplot spanning grid cells |
| `fig.suptitle('Title', fontsize=16)` | Figure-level title |
| `fig.text(x, y, 'text')` | Text in figure coordinates (0–1) |
| `fig.tight_layout()` | Auto-adjust subplot params |
| `fig.savefig(path, dpi, bbox_inches)` | Save to file |
| `fig.canvas.draw()` | Force redraw |
| `fig.canvas.mpl_connect(event, callback)` | Connect event handler |

## Axes Creation Methods

```python
# Single axes
fig, ax = plt.subplots()

# Grid of subplots
fig, axes = plt.subplots(2, 3, figsize=(12, 8), sharex=True, sharey=False)

# Named mosaic layout
fig, axd = plt.subplot_mosaic([
    ['A', 'B'],
    ['C', 'C'],
], figsize=(10, 8), constrained_layout=True)
# Access: axd['A'], axd['B'], axd['C']

# Manual axes placement
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # [left, bottom, width, height]

# Polar axes
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
```

## Backends

A backend is the rendering engine. Choose before creating any figures:

```python
import matplotlib
matplotlib.use('Agg')  # Non-interactive, for saving files (no display needed)
# or set env: MPLBACKEND=Agg
```

| Backend | Use Case |
|---------|----------|
| `Agg` | Headless rendering, save to PNG (default in scripts) |
| `TkAgg` | Desktop interactive with Tkinter |
| `Qt5Agg` / `QtAgg` | Desktop interactive with PyQt/PySide |
| `WebAgg` | Interactive plots in web browser |
| `nbAgg` | Jupyter notebook inline (interactive) |
| `macosx` | Native macOS window |
| `PDF` / `SVG` / `PS` | Vector output only |

**Important**: `matplotlib.use()` must be called before `import matplotlib.pyplot`. In Jupyter, use `%matplotlib inline`, `%matplotlib widget`, or `%matplotlib notebook` magic instead.

## Event Handling

```python
fig, ax = plt.subplots()
line, = ax.plot(x, y)

def on_click(event):
    if event.inaxes == ax:
        print(f'Clicked at data coords: ({event.xdata:.2f}, {event.ydata:.2f})')

cid = fig.canvas.mpl_connect('button_press_event', on_click)
# Later: fig.canvas.mpl_disconnect(cid)
```

Event types: `button_press_event`, `button_release_event`, `motion_notify_event`, `key_press_event`, `key_release_event`, `draw_event`, `resize_event`, `close_event`.

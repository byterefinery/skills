# Styling and Themes

## rcParams

`matplotlib.rcParams` is a dictionary-like object controlling all default appearance settings:

```python
import matplotlib as mpl

# Read current value
print(mpl.rcParams['figure.figsize'])   # [6.4, 4.8]
print(mpl.rcParams['lines.linewidth'])   # 1.5

# Set individual params
mpl.rcParams['font.size'] = 12
mpl.rcParams['axes.titlesize'] = 14
mpl.rcParams['lines.linewidth'] = 2

# Set multiple at once
mpl.rc('font', family='sans-serif', size=12)
mpl.rc('axes', titlesize=14, labelsize=12)
mpl.rc('lines', linewidth=2, marker_size=6)

# Reset to defaults
mpl.rcParams.update(mpl.rcParamsDefault)
```

### rcParams by group

| Group | Key params |
|-------|-----------|
| `figure` | `figsize`, `dpi`, `facecolor`, `edgecolor`, `max_open_warning` |
| `axes` | `titlesize`, `labelsize`, `linewidth`, `grid`, `facecolor`, `edgecolor` |
| `lines` | `linewidth`, `color`, `linestyle`, `marker`, `markersize` |
| `xtick` / `ytick` | `labelsize`, `direction`, `length`, `width` |
| `font` | `family`, `size`, `weight`, `style` |
| `savefig` | `dpi`, `facecolor`, `edgecolor`, `format`, `bbox_inches` |
| `legend` | `fontsize`, `frameon`, `framealpha`, `numpoints` |
| `grid` | `linestyle`, `linewidth`, `alpha`, `color` |
| `image` | `cmap`, `interpolation`, `aspect`, `lut` |
| `patch` | `edgecolor`, `facecolor`, `linewidth` |
| `axes.prop_cycle` | Color/line cycle for multiple lines |

### Property cycle

```python
from cycler import cycler

# Custom color and linestyle cycle
mpl.rcParams['axes.prop_cycle'] = cycler(
    color=['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
) * cycler(linestyle=['-', '--', '-.', ':'])

# Or using tab colors
mpl.rcParams['axes.prop_cycle'] = cycler(color=['tab:blue', 'tab:orange', 'tab:green'])
```

## Built-in Styles

```python
import matplotlib.style as style

# List available styles
print(style.available)

# Apply a style
style.use('seaborn-v0_8-darkgrid')
style.use('ggplot')
style.use('dark_background')
style.use('fivethirtyeight')
style.use('bmh')
style.use('grayscale')
style.use('classic')       # MATLAB-like defaults
style.use('fast')          # Optimized for speed
```

### Available built-in styles

| Style | Description |
|-------|-------------|
| `default` | Matplotlib defaults |
| `classic` | Pre-2.0 style (MATLAB-like) |
| `bmh` | Bayes Methods for Hackers |
| `ggplot` | R ggplot2 theme |
| `grayscale` | Grayscale-only |
| `dark_background` | Dark theme |
| `fivethirtyeight` | FiveThirtyEight.com style |
| `seaborn-v0_8` | Seaborn v0.8 defaults |
| `seaborn-v0_8-darkgrid` | Seaborn with dark grid |
| `seaborn-v0_8-whitegrid` | Seaborn with white grid |
| `seaborn-v0_8-ticks` | Seaborn with tick marks |
| `Solarize_Light2` | Solarized light theme |
| `petroff6` / `petroff8` / `petroff10` | Petroff color palettes |

### Style context (temporary)

```python
# Temporarily apply style within a block
with style.context('seaborn-v0_8-darkgrid'):
    fig, ax = plt.subplots()
    ax.plot(x, y)
# Style reverts after the block

# Stack contexts
with style.context('dark_background'):
    with style.context('fivethirtyeight'):
        fig, ax = plt.subplots()
```

## Custom Styles

### Via dictionary

```python
custom_style = {
    'figure.figsize': (10, 6),
    'axes.facecolor': '#f0f0f0',
    'axes.edgecolor': '#333333',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'lines.linewidth': 2,
    'font.size': 12,
}
mpl.rc(**custom_style)
```

### Via .mplstyle file

Create a file `my_style.mplstyle`:
```
figure.figsize: 10, 6
axes.facecolor: #f0f0f0
axes.grid: True
grid.alpha: 0.3
lines.linewidth: 2
font.size: 12
```

Load it:
```python
style.use('/path/to/my_style.mplstyle')
# Or place in ~/.config/matplotlib/stylelib/
style.use('my_style')
```

### Via package

Styles can be distributed as Python packages. Place `.mplstyle` files alongside `__init__.py`:
```
mypackage/
├── __init__.py
└── mytheme.mplstyle
```
Then: `style.use('mypackage.mytheme')`

## Common Style Patterns

### Publication-ready

```python
import matplotlib as mpl
mpl.rcParams.update({
    'figure.figsize': (6.4, 4.8),
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.5,
    'pdf.fonttype': 42,       # Embed fonts in PDF
    'ps.fonttype': 42,
})
```

### Clean minimal

```python
mpl.rcParams.update({
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.2,
    'figure.facecolor': 'white',
    'savefig.facecolor': 'white',
})
```

### Dark theme

```python
style.use('dark_background')
mpl.rcParams.update({
    'axes.edgecolor': 'gray',
    'grid.color': 'gray',
    'grid.alpha': 0.2,
})
```

## rc_context (temporary settings)

```python
import matplotlib.pyplot as plt

with plt.rc_context({'figure.figsize': (12, 8), 'font.size': 14}):
    fig, ax = plt.subplots()
    ax.plot(x, y)
# Settings revert after the block
```

## getp / setp (inspect and modify artists)

```python
import matplotlib.pyplot as plt

line, = plt.plot(x, y)
plt.getp(line)              # List all properties
plt.getp(line, 'color')     # Get specific property
plt.setp(line, color='red', linewidth=3)  # Set multiple properties
```

# Ticks, Axes, and Scales

## Tick Location and Labels

### Basic tick control

```python
# Set specific tick locations
ax.set_xticks([0, 5, 10, 15, 20])
ax.set_yticks([-1, -0.5, 0, 0.5, 1])

# Custom labels
ax.set_xticklabels(['Zero', 'Five', 'Ten', 'Fifteen', 'Twenty'])

# Rotate labels
ax.set_xticklabels(labels, rotation=45, ha='right')

# Tick label font size
ax.tick_params(axis='both', labelsize=10)
```

### Using `xticks()` / `yticks()` (pyplot style)

```python
import matplotlib.pyplot as plt
plt.xticks([0, 5, 10], labels=['A', 'B', 'C'], rotation=30)
plt.yticks(range(-5, 6))
```

## Tick Locators

Control where ticks appear. Set via `ax.xaxis.set_major_locator()` or `ax.xaxis.set_minor_locator()`:

```python
from matplotlib.ticker import (
    AutoLocator, MaxNLocator, MultipleLocator, FixedLocator,
    LinearLocator, LogLocator, NullLocator, IndexLocator,
    AutoMinorLocator
)
```

| Locator | Use Case | Example |
|---------|----------|---------|
| `AutoLocator` | Default; auto-picks nice locations | `ax.xaxis.set_major_locator(AutoLocator())` |
| `MaxNLocator(nbins=10)` | Up to N ticks at nice values | `ax.yaxis.set_major_locator(MaxNLocator(nbins=8))` |
| `MultipleLocator(base=5.0)` | Every multiple of base | `ax.xaxis.set_major_locator(MultipleLocator(5))` |
| `FixedLocator(locs=[0, 10, 20])` | Exact positions | `ax.yaxis.set_major_locator(FixedLocator([0, 50, 100]))` |
| `LinearLocator(numticks=15)` | Evenly spaced from min to max | `ax.xaxis.set_major_locator(LinearLocator(15))` |
| `LogLocator(base=10, numticks=15)` | Log-spaced ticks | `ax.xaxis.set_major_locator(LogLocator())` |
| `NullLocator()` | No ticks | `ax.xaxis.set_minor_locator(NullLocator())` |
| `AutoMinorLocator(n=4)` | Minor ticks between major | `ax.xaxis.set_minor_locator(AutoMinorLocator(5))` |

```python
# Combined: major every 10, minor every 2
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.xaxis.set_minor_locator(MultipleLocator(2))
```

## Tick Formatters

Control how tick values are displayed as strings:

```python
from matplotlib.ticker import (
    ScalarFormatter, LogFormatter, FormatStrFormatter,
    FuncFormatter, FixedFormatter, NullFormatter,
    StrMethodFormatter, PercentFormatter, EngFormatter
)
```

| Formatter | Use Case | Example |
|-----------|----------|---------|
| `ScalarFormatter` | Default for numeric axes | Auto-scales format |
| `FormatStrFormatter('%.2f')` | sprintf-style format | 2 decimal places |
| `FuncFormatter(func)` | Custom Python function | Any formatting logic |
| `FixedFormatter(labels)` | Hard-coded labels | Must match locator count |
| `NullFormatter()` | No labels | Hide tick text |
| `StrMethodFormatter('{x:.1f}')` | str.format style | Flexible templates |
| `PercentFormatter(xmax=1)` | Percentage display | 0% to 100% |
| `EngFormatter(unit='V')` | Engineering notation | 1.5 kV, 2.3 MV |

### Custom formatter with FuncFormatter

```python
from matplotlib.ticker import FuncFormatter

def currency_formatter(val, pos):
    return f'${val:,.0f}'

ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# Or using a lambda
ax.xaxis.set_major_formatter(
    FuncFormatter(lambda val, pos: f'{val * 100:.1f}%')
)
```

### Common formatting patterns

```python
# Scientific notation
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))

# With units
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:.0f} nm'))

# Power of 10
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'${v/1000:.0f}\\times10^3$'))

# Date formatting (see dates reference)
from matplotlib.dates import DateFormatter
ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
```

## Axis Scales

```python
ax.set_xscale('linear')    # Default
ax.set_xscale('log')       # Logarithmic
ax.set_xscale('symlog')    # Symmetric log (handles zero/negative)
ax.set_xscale('logit')     # Logit scale (for probabilities)
ax.set_xscale('asinh')     # Inverse hyperbolic sine
```

### Built-in scales

| Scale | Description |
|-------|-------------|
| `'linear'` | Default linear scaling |
| `'log'` | Logarithmic; data must be positive |
| `'symlog'` | Linear near zero, log far from zero |
| `'logit'` | For probability data (0 < x < 1) |
| `'asinh'` | Handles all values including zero |

```python
# symlog with linear threshold
ax.set_yscale('symlog', linthresh=1e-3)

# log with base
ax.set_xscale('log', base=2)
```

## Spines

Spines are the lines connecting axis tick marks:

```python
# Hide top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Move spine position
ax.spines['left'].set_position(('data', 0))   # At x=0
ax.spines['bottom'].set_position(('data', 0))  # At y=0

# Change spine style
ax.spines['left'].set_color('red')
ax.spines['left'].set_linewidth(2)
ax.spines['left'].set_linestyle('--')

# Remove all spines (for heatmaps, etc.)
for spine in ax.spines.values():
    spine.set_visible(False)
```

### Centered axes (crosshair style)

```python
ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
```

## Tick Appearance

```python
ax.tick_params(
    axis='both',          # 'x', 'y', or 'both'
    direction='out',      # 'in', 'out', or 'inout'
    length=6,             # Tick length in points
    width=1,              # Tick line width
    pad=5,                # Space between tick and label
    labelsize=10,         # Label font size
    labelrotation=45,     # Label rotation
    bottom=True,          # Show bottom ticks
    top=False,            # Hide top ticks
    left=True,            # Show left ticks
    right=False           # Hide right ticks
)
```

## Axis Limits and Margins

```python
# Fixed limits
ax.set_xlim(0, 10)
ax.set_ylim(-1, 1)
ax.set(xlim=(0, 10), ylim=(-1, 1))

# Auto with margins
ax.margins(x=0.05, y=0.1)   # 5% x-margin, 10% y-margin

# Tight fit (no margins)
ax.autoscale(tight=True)

# Invert axis
ax.invert_xaxis()
ax.invert_yaxis()
```

## Twin Axes

Overlay axes with different scales:

```python
fig, ax1 = plt.subplots()
line1 = ax1.plot(x, y1, 'b-', label='Temperature')
ax1.set_ylabel('Temperature (°C)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

ax2 = ax1.twinx()
line2 = ax2.plot(x, y2, 'r-', label='Pressure')
ax2.set_ylabel('Pressure (hPa)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Combined legend
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left')
```

## Polar Axes

```python
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.plot(theta, r)
ax.set_theta_zero_location('N')    # 0° at top
ax.set_theta_direction(-1)         # Clockwise
ax.set_rlabel_position(30)         # Angle for radial labels
```

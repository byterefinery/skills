# Text and Annotations

## Basic Text

```python
# On axes (data coordinates)
ax.text(x, y, 'Label', fontsize=12, ha='center', va='bottom')

# Figure-level text (figure coordinates 0–1)
fig.text(0.5, 0.95, 'Figure Title', ha='center', fontsize=16)

# Axes title
ax.set_title('My Plot', fontsize=14, fontweight='bold', pad=10)

# Axis labels
ax.set_xlabel('X Axis (units)', fontsize=12, labelpad=8)
ax.set_ylabel('Y Axis (units)', fontsize=12, labelpad=8)
```

### Text alignment

| `ha` (horizontal) | `va` (vertical) |
|--------------------|-----------------|
| `'left'` | `'top'` |
| `'center'` | `'center'` |
| `'right'` | `'bottom'` |
| `'center'` is default for ha | `'baseline'` is default for va |

### Common text properties

```python
ax.text(x, y, 'Label',
    fontsize=12,           # Size in points
    fontweight='bold',     # 'normal', 'bold', 'heavy', or 100–900
    fontstyle='italic',    # 'normal' or 'italic'
    family='serif',        # 'serif', 'sans-serif', 'monospace', or font name
    color='red',
    alpha=0.8,
    rotation=45,           # Degrees
    ha='center', va='top',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3)
)
```

## Annotations with Arrows

```python
ax.annotate('Peak value',
    xy=(x_peak, y_peak),           # Point to annotate (data coords)
    xytext=(x_text, y_text),       # Text position
    textcoords='offset points',    # Relative to xy
    arrowprops=dict(
        arrowstyle='->',
        connectionstyle='arc3,rad=0.3',
        color='red',
        linewidth=1.5
    ),
    fontsize=10,
    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
)
```

### Coordinate systems for annotations

| `xycoords` | Meaning |
|------------|---------|
| `'data'` (default) | Data coordinates |
| `'axes fraction'` | Axes: (0,0)=bottom-left, (1,1)=top-right |
| `'axes pixels'` | Pixels from axes origin |
| `'figure fraction'` | Figure: (0,0)=bottom-left, (1,1)=top-right |
| `'figure pixels'` | Pixels from figure origin |
| `'offset points'` | Offset from xy in display points |

Same options for `textcoords`. Mix different systems:
```python
ax.annotate('Note',
    xy=(0.5, 0.8),
    xycoords='axes fraction',
    xytext=(10, -20),
    textcoords='offset points',
    arrowprops=dict(arrowstyle='->'))
```

### Arrow styles

| Style | Description |
|-------|-------------|
| `'->'` | Simple arrow |
| `'-|>'` | Arrow with bar at tail |
| `'fancy'` | Fancy arrowhead |
| `'wedge'` | Wedge shape |
| `'-'` | No arrowhead (just line) |
| `'<->'` | Double-headed |
| `'fancy,<->'` | Fancy double-headed |

### Connection styles

```python
arrowprops=dict(connectionstyle='arc3,rad=0.3')      # Curved
arrowprops=dict(connectionstyle='angle3,angleA=30')  # Angled
arrowprops=dict(connectionstyle='bar,fraction=0.15') # Barbell
```

## Math Text (LaTeX)

Wrap expressions in `$...$` for inline or `$$...$$` for display math:

```python
ax.set_title(r'$\alpha > 0.5 \implies f(x) = \sum_{i=0}^{n} \frac{x^i}{i!}$')
ax.text(0.5, 0.5, r'$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$')
```

### Common math symbols

| Symbol | LaTeX | Symbol | LaTeX |
|--------|-------|--------|-------|
| α β γ | `\alpha` `\beta` `\gamma` | ∑ ∏ | `\sum` `\prod` |
| ≤ ≥ ≠ | `\leq` `\geq` `\neq` | → ← | `\rightarrow` `\leftarrow` |
| ∂ ∇ | `\partial` `\nabla` | ± × ÷ | `\pm` `\times` `\div` |
| ∞ μ σ | `\infty` `\mu` `\sigma` | θ φ ω | `\theta` `\phi` `\omega` |
| sin cos tan | `\sin` `\cos` `\tan` | ln log exp | `\ln` `\log` `\exp` |
| ½ ⅓ | `\frac{1}{2}` | x̂ n̂ | `\hat{x}` `\hat{n}` |
| x⃗ | `\vec{x}` | x̄ | `\bar{x}` |

### Math text formatting

```python
# Superscript/subscript
r'$x_{i}^{2}$'           # x_i^2
r'$\frac{a}{b}$'         # a/b fraction
r'$\sqrt{x}$'            # sqrt(x)
r'$\lim_{x \to 0}$'      # limit
r'$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$'  # matrix

# Bold and styled math
r'$\mathbf{x}$'          # Bold vector
r'$\boldsymbol{\Sigma}$' # Bold Greek
r'$\mathrm{units}$'      # Roman text in math mode
```

### Math rendering modes

```python
import matplotlib as mpl
mpl.rcParams['text.usetex'] = True    # Use system LaTeX (requires tex installed)
mpl.rcParams['mathtext.fontset'] = 'cm'  # Computer Modern (default)
mpl.rcParams['mathtext.fontset'] = 'stix'  # STIX fonts
mpl.rcParams['mathtext.fontset'] = 'dejavusans'  # DejaVu
```

## Titles and Labels

```python
# Axes title with positioning
ax.set_title('Title', loc='left', fontsize=14, fontweight='bold')
ax.set_title('Title', loc='right', pad=10)
ax.set_title('Title', loc='center')  # Default

# Figure-level title
fig.suptitle('Overall Figure Title', fontsize=16, y=0.98)

# Axis labels with padding
ax.set_xlabel('Time (seconds)', labelpad=10)
ax.set_ylabel('Amplitude', labelpad=10)
```

## Font Management

```python
from matplotlib.font_manager import fontManager, FontProperties

# List available fonts
available = [f.name for f in fontManager.ttflist]

# Set specific font
fp = FontProperties(family='DejaVu Sans', size=12, weight='bold')
ax.text(x, y, 'Label', fontproperties=fp)

# Or via rcParams
import matplotlib as mpl
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
```

## Bounding Boxes (Background Boxes)

```python
ax.text(x, y, 'Label', bbox={
    'boxstyle': 'round,pad=0.5',   # 'square' or 'round'
    'facecolor': 'yellow',
    'edgecolor': 'black',
    'alpha': 0.3,
    'linewidth': 1
})
```

## Anchored Text

Text that stays in a fixed position relative to the axes:

```python
from matplotlib.offsetbox import AnchoredText

at = AnchoredText('Important note', loc='upper right', prop=dict(size=8),
                  frameon=True, framealpha=0.5)
ax.add_artist(at)
```

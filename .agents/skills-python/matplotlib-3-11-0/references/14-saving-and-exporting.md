# Saving and Exporting

## savefig()

```python
fig.savefig('plot.png')
fig.savefig('plot.pdf', bbox_inches='tight')
fig.savefig('plot.svg', dpi=300)
```

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `dpi` | Dots per inch (default: rcParams['savefig.dpi']) |
| `format` | `'png'`, `'pdf'`, `'svg'`, `'eps'`, `'ps'`, `'jpg'`, `'tif'` |
| `bbox_inches` | `'tight'` trims whitespace; or tuple of inches |
| `pad_inches` | Padding around tight bbox (default: 0.1) |
| `facecolor` | Background color (default: rcParams['savefig.facecolor']) |
| `edgecolor` | Edge color (default: rcParams['savefig.edgecolor']) |
| `transparent` | Transparent background (`True`) |
| `metadata` | Dict of metadata (title, author, etc.) |

## Format Selection

### Raster formats (pixel-based)

| Format | Extension | Best For | Notes |
|--------|-----------|----------|-------|
| PNG | `.png` | General use, web, transparency | Lossless, supports alpha |
| JPEG | `.jpg` | Photos, large images | Lossy, no transparency |
| TIFF | `.tif` | Print, archival | Large file, lossless |
| BMP | `.bmp` | Legacy systems | Uncompressed, large files |

### Vector formats (scalable)

| Format | Extension | Best For | Notes |
|--------|-----------|----------|-------|
| PDF | `.pdf` | Publications, reports | Embeds fonts, scalable |
| SVG | `.svg` | Web, further editing | XML-based, editable |
| EPS | `.eps` | LaTeX (legacy) | PostScript format |
| PS | `.ps` | Print (legacy) | PostScript format |

### Choosing a format

- **Publication papers**: PDF or PNG at 300+ dpi
- **Web display**: PNG (smaller) or SVG (scalable)
- **Further editing in Inkscape/Illustrator**: SVG
- **LaTeX documents**: PDF (with `graphicx` package)
- **Photos/images**: JPEG

## DPI and Resolution

```python
# Figure size in inches × DPI = pixel dimensions
fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
# → 600 × 400 pixels at save time

# Override DPI on save
fig.savefig('plot.png', dpi=300)
# → 1800 × 1200 pixels

# Set default
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 150
mpl.rcParams['savefig.dpi'] = 300
```

### Resolution guidelines

| Use case | DPI |
|----------|-----|
| Screen display | 72–100 |
| Presentation slides | 150 |
| Publication (print) | 300 |
| High-quality print | 600 |

## bbox_inches='tight'

Trims whitespace around the plot:

```python
fig.savefig('plot.png', bbox_inches='tight')
fig.savefig('plot.pdf', bbox_inches='tight', pad_inches=0.05)
```

**When to use**: When labels, legends, or colorbars extend beyond the default figure area. Without it, elements may be clipped.

**Watch out**: `tight` recalculates the bounding box which can sometimes shift element positions slightly. For consistent multi-figure layouts, consider using `constrained_layout` instead.

## Transparent Background

```python
# On save
fig.savefig('plot.png', transparent=True)

# Or set facecolor
fig.savefig('plot.png', facecolor='none')

# Set globally
mpl.rcParams['savefig.transparent'] = True
```

## PDF-Specific Options

```python
fig.savefig('plot.pdf',
    bbox_inches='tight',
    metadata={'Creator': 'My Script', 'Title': 'Results'},
    pdf_compression=4,          # 0–9 compression level
)
```

For embedding fonts in PDF (required by many journals):
```python
mpl.rcParams['pdf.fonttype'] = 42     # TrueType fonts
mpl.rcParams['ps.fonttype'] = 42
```

## SVG-Specific Options

```python
fig.savefig('plot.svg',
    bbox_inches='tight',
    metadata={'Creator': 'My Script'},
)
```

SVG output is clean and editable. Use `optimize=True` for smaller files (requires `lxml`).

## Saving Multiple Pages (PDF)

```python
from matplotlib.backends.backend_pdf import PdfPages

with PdfPages('multipage.pdf') as pdf:
    fig1, ax1 = plt.subplots()
    ax1.plot(x, y1)
    pdf.savefig(fig1, bbox_inches='tight')
    plt.close(fig1)

    fig2, ax2 = plt.subplots()
    ax2.plot(x, y2)
    pdf.savefig(fig2, bbox_inches='tight')
    plt.close(fig2)
```

## Headless Rendering (No Display)

For servers or CI environments without a display:

```python
import matplotlib
matplotlib.use('Agg')  # Must be before pyplot import
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(x, y)
fig.savefig('plot.png')
plt.close(fig)
```

Or set environment variable:
```bash
export MPLBACKEND=Agg
```

## Memory Management

Close figures to free memory in loops:

```python
for i in range(1000):
    fig, ax = plt.subplots()
    ax.plot(data[i])
    fig.savefig(f'plot_{i}.png')
    plt.close(fig)  # Critical: prevents memory leak
    # Or: plt.close('all')
```

## Saving to BytesIO (in-memory)

```python
import io

buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=150)
buf.seek(0)
# buf now contains PNG bytes for sending over network, storing in DB, etc.
```

## Common savefig Patterns

### Publication-ready figure

```python
fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=300)
ax.plot(x, y, linewidth=1.5)
ax.set_xlabel('X (units)', fontsize=10)
ax.set_ylabel('Y (units)', fontsize=10)
fig.savefig('figure.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
```

### Multi-panel figure

```python
fig, axes = plt.subplots(2, 3, figsize=(15, 9),
                         constrained_layout=True)
for i, ax in enumerate(axes.flat):
    ax.plot(x, data[i])
    ax.set_title(f'Panel {i+1}')

fig.savefig('multipanel.pdf', bbox_inches='tight')
```

---
name: matplotlib-3-11-0
description: >
  Matplotlib plotting library (v3.11). Use this skill whenever the user mentions
  plots, charts, graphs, figures, data visualization, matplotlib, pyplot, or
  needs to create any kind of visual output from Python data — line plots, scatter
  plots, bar charts, histograms, heatmaps, contour plots, subplots, legends,
  colormaps, saving figures, styling, animations, or interactive widgets. Covers
  both the pyplot (state-based) and object-oriented APIs.
---

# matplotlib 3.11.0

## Overview

Matplotlib is Python's foundational plotting library. It provides two interfaces:

- **pyplot (state-based)** — `plt.plot()`, `plt.show()`. MATLAB-like, convenient for interactive work and quick scripts.
- **Object-oriented (OO)** — `fig, ax = plt.subplots(); ax.plot()`. Explicit control over every element. Preferred for complex plots and production code.

The core hierarchy is: `Figure` → `Axes` → `Artist` (lines, patches, text, images). Most pyplot functions are thin wrappers around `Axes` methods.

## Usage

### Quick start (pyplot)

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x), label='sin')
plt.xlabel('x'); plt.ylabel('y')
plt.legend(); plt.tight_layout()
plt.savefig('plot.png', dpi=150)
plt.show()
```

### Object-oriented (preferred for complex plots)

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, np.sin(x), label='sin')
ax.plot(x, np.cos(x), label='cos')
ax.set_xlabel('x'); ax.set_ylabel('y')
ax.legend(); fig.tight_layout()
fig.savefig('plot.png', dpi=150, bbox_inches='tight')
```

### Multiple subplots

```python
# Regular grid
fig, axes = plt.subplots(2, 3, figsize=(12, 8), sharex=True)

# Named layout (preferred for irregular grids)
fig, axd = plt.subplot_mosaic([
    ['top_left', 'top_right'],
    ['bottom',    'bottom'],
], figsize=(10, 6))

# Constrained layout (auto-adjusts spacing)
fig, axes = plt.subplots(2, 2, constrained_layout=True)
```

### Key OO methods on `Axes`

| Task | Method |
|------|--------|
| Line plot | `ax.plot(x, y, label='...', color='C0', linewidth=2)` |
| Scatter | `ax.scatter(x, y, c=colors, s=sizes, cmap='viridis')` |
| Bar chart | `ax.bar(x, height, width=0.8, color='steelblue')` |
| Horizontal bar | `ax.barh(y, width, left=None)` |
| Histogram | `ax.hist(data, bins=30, density=False, alpha=0.7)` |
| Fill between | `ax.fill_between(x, y1, y2, alpha=0.3)` |
| Error bars | `ax.errorbar(x, y, yerr=err, capsize=4)` |
| Box plot | `ax.boxplot(data, patch_artist=True)` |
| Violin plot | `ax.violinplot(data)` |
| Pie chart | `ax.pie(sizes, labels=labels, autopct='%.1f%%')` |
| Heatmap | `ax.imshow(Z, cmap='viridis', aspect='auto')` |
| Contour | `ax.contour(X, Y, Z, levels=10)` / `ax.contourf(...)` |
| Pcolormesh | `ax.pcolormesh(X, Y, Z, shading='auto', cmap='viridis')` |
| Stem plot | `ax.stem(x, y, linefmt='C0-', markerfmt='o')` |
| Quiver (vector) | `ax.quiver(x, y, u, v)` |
| Streamplot | `ax.streamplot(X, Y, U, V)` |
| Hexbin | `ax.hexbin(x, y, C, gridsize=20, cmap='Blues')` |
| Text | `ax.text(x, y, 'label', fontsize=12)` |
| Annotate | `ax.annotate('text', xy=(x,y), xytext=(tx,ty), arrowprops=dict(...))` |
| Title | `ax.set_title('Title', fontsize=14, fontweight='bold')` |
| Labels | `ax.set_xlabel('X'); ax.set_ylabel('Y')` |
| Limits | `ax.set_xlim(0, 10); ax.set_ylim(-1, 1)` |
| Scale | `ax.set_xscale('log'); ax.set_yscale('symlog')` |
| Ticks | `ax.set_xticks([0, 5, 10]); ax.set_xticklabels(['a','b','c'])` |
| Grid | `ax.grid(True, alpha=0.3)` |
| Legend | `ax.legend(loc='upper right', framealpha=0.9)` |
| Twin axis | `ax2 = ax.twinx()` |

## Gotchas

- **`plt.plot()` without explicit axes** draws on the "current" axes, which can silently target the wrong subplot in multi-figure scripts. Always use `fig, ax = plt.subplots()` for reliability.
- **`imshow` vs `pcolormesh`**: `imshow` maps array indices to pixel centers (default origin='upper'), while `pcolormesh` maps to grid corners. For heatmaps with labeled axes, `pcolormesh` is usually more intuitive. Use `shading='auto'` on `pcolormesh` for correct alignment.
- **Colormap normalization**: If colors look wrong, check that `vmin`/`vmax` are set explicitly. Without them, matplotlib auto-scales to data min/max which can be misleading when comparing multiple plots.
- **`tight_layout()` vs `constrained_layout`**: `tight_layout()` runs once at call time; `constrained_layout=True` (or `layout='constrained'`) is reactive and adjusts as elements are added. Prefer `constrained_layout` for complex figures.
- **Backend selection must happen before any figure creation**. Call `matplotlib.use('Agg')` or set `MPLBACKEND=Agg` before importing pyplot if running headless (no display).
- **DPI confusion**: `figsize` is in inches, `savefig(dpi)` controls output resolution. A 6×4 inch figure at 100 dpi = 600×400 pixels. For publication, use `dpi=300` or `bbox_inches='tight'`.
- **Legend overlaps data**: Use `loc='best'` for auto-placement, or `bbox_to_anchor=(x, y)` with `loc` to position outside the axes area.
- **Shared axes**: `sharex=True` / `sharey=True` in `subplots()` links axis limits and removes redundant tick labels. But calling `ax.set_xlim()` on one shared axis affects all of them.
- **Markers are not clipped by default** — large markers can extend beyond axis boundaries. Use `clip_on=True` or adjust margins with `ax.margins(x=0.05, y=0.05)`.

## References

Detailed topic guides loaded on demand:

- [01-core-api](references/01-core-api.md) — Figure/Axes/Artist hierarchy, pyplot vs OO, backends
- [02-plot-types](references/02-plot-types.md) — Line, scatter, bar, histogram, area, errorbar, stem, pie
- [03-layout](references/03-layout.md) — subplots, gridspec, subplot_mosaic, constrained_layout
- [04-colors-and-colormaps](references/04-colors-and-colormaps.md) — Color specs, colormaps, normalization, color sequences
- [05-text-and-annotations](references/05-text-and-annotations.md) — Text, titles, labels, annotations, math text, fonts
- [06-ticks-and-axes](references/06-ticks-and-axes.md) — Locators, formatters, scales, spines, twin axes
- [07-legend-and-colorbar](references/07-legend-and-colorbar.md) — Legends, colorbars, custom handles
- [08-patches-and-shapes](references/08-patches-and-shapes.md) — Rectangle, Circle, Polygon, Arrow, FancyBboxPatch
- [09-transforms](references/09-transforms.md) — Coordinate systems, Affine2D, blitting
- [10-styling-and-themes](references/10-styling-and-themes.md) — rcParams, style.use(), contexts, custom styles
- [11-dates-and-times](references/11-dates-and-times.md) — Date plotting, locators, formatters, timezones
- [12-image-and-contour](references/12-image-and-contour.md) — imshow, pcolormesh, contour, quiver, streamplot
- [13-animation-and-widgets](references/13-animation-and-widgets.md) — FuncAnimation, widgets (Slider, Button, Cursor)
- [14-saving-and-exporting](references/14-saving-and-exporting.md) — savefig formats, DPI, vector vs raster, PDF/SVG

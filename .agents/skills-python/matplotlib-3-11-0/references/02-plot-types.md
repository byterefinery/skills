# Plot Types

## Line Plots

```python
ax.plot(x, y)                              # Basic line
ax.plot(x, y, 'r--', linewidth=2)          # Shorthand: red dashed
ax.plot(x, y, color='C0', ls='-', lw=1.5)  # Explicit style
ax.plot(x, y, marker='o', markersize=4)    # With markers
ax.plot(x, y, marker='s', markevery=10)    # Markers every 10th point
```

### Line style shorthand

| Char | Color | Char | Style | Char | Marker |
|------|-------|------|-------|------|--------|
| `b` blue | `-` solid | `.` point | `o` circle |
| `g` green | `--` dashed | `,` pixel | `s` square |
| `r` red | `-.` dash-dot | `x` x-mark | `D` diamond |
| `c` cyan | `:` dotted | `+` plus | `^` triangle-up |
| `m` magenta | ` ` none | `*` star | `v` triangle-down |
| `y` yellow | | `p` pentagon | `<` triangle-left |
| `k` black | | `h` hexagon1 | `>` triangle-right |
| `w` white | | `1` tri_down | `\|` vline |
| `C0`–`C9` | cycle colors | | `2` tri_up | `/` hline |

### Step plots

```python
ax.step(x, y, where='pre')    # Default: step at x[i]
ax.step(x, y, where='post')   # Step after x[i]
ax.step(x, y, where='mid')    # Step between x[i] and x[i+1]
```

### Log-scale line plots

```python
ax.loglog(x, y)           # Both axes log
ax.semilogx(x, y)         # X axis log
ax.semilogy(x, y)         # Y axis log
# Equivalent: ax.plot(x, y); ax.set_xscale('log')
```

## Scatter Plots

```python
# Basic scatter
ax.scatter(x, y, s=50, c='blue', alpha=0.6, edgecolors='none')

# Colored by a third variable
scatter = ax.scatter(x, y, c=values, cmap='viridis', s=sizes, alpha=0.7)
fig.colorbar(scatter, ax=ax, label='Value')

# With error bars
ax.errorbar(x, y, xerr=dx, yerr=dy, fmt='o', capsize=3, capthick=1)
```

Key parameters: `s` (size, scalar or array), `c` (color), `cmap`, `norm`, `vmin`, `vmax`, `marker`, `linewidths`, `edgecolors`.

## Bar Charts

```python
# Vertical bar
ax.bar(x, height, width=0.8, color='steelblue', edgecolor='white')

# Horizontal bar
ax.barh(y, width, height=0.8, left=None, color='coral')

# Stacked bars
ax.bar(x, h1, label='A')
ax.bar(x, h2, bottom=h1, label='B')

# Grouped bars
width = 0.35
ax.bar(x - width/2, h1, width, label='A')
ax.bar(x + width/2, h2, width, label='B')

# With error bars
ax.bar(x, height, yerr=errors, capsize=4)

# Bar labels
container = ax.bar(x, height)
ax.bar_label(container, fmt='%.1f', padding=3)
```

## Histograms

```python
# Basic histogram
ax.hist(data, bins=30, color='steelblue', edgecolor='white', alpha=0.8)

# Multiple datasets
ax.hist([data1, data2], bins=30, label=['A', 'B'],
        color=['steelblue', 'coral'], alpha=0.7)

# Density (probability density, not counts)
ax.hist(data, bins=30, density=True, alpha=0.5)

# Cumulative
ax.hist(data, bins=30, cumulative=True)

# Horizontal
ax.hist(data, orientation='horizontal', bins=20)

# Stacked
ax.hist([data1, data2], bins=20, stacked=True)
```

### ECDF (Empirical CDF)

```python
# Step-style ECDF
ax.ecdf(data, complementary=False)  # cumulative
ax.ecdf(data, complementary=True)   # survival function
```

## Area / Fill Plots

```python
# Fill between two curves
ax.fill_between(x, y1, y2, alpha=0.3, color='gray')

# Fill with condition
ax.fill_between(x, y1, y2, where=(y1 > y2), alpha=0.3)

# Stacked area
ax.stackplot(x, y1, y2, y3, labels=['A', 'B', 'C'], alpha=0.7)

# Fill between x (horizontal)
ax.fill_betweenx(y, x1, x2, alpha=0.3)
```

## Error Bars

```python
ax.errorbar(x, y, yerr=dy, fmt='o', capsize=4)
ax.errorbar(x, y, xerr=dx, yerr=dy, fmt='s', capsize=3)
ax.errorbar(x, y, yerr=[lower, upper], fmt='-o')  # Asymmetric
```

Parameters: `yerr`, `xerr` (scalar, array, or (N,2) for asymmetric), `fmt` (line format), `capsize`, `elinewidth`, `errorevery`.

## Box Plots and Violin Plots

```python
# Box plot
bp = ax.boxplot([data1, data2], patch_artist=True,
                boxprops=dict(facecolor='lightblue'))
ax.set_xticklabels(['Group A', 'Group B'])

# Horizontal
ax.boxplot(data, vert=False)

# Violin plot
vp = ax.violinplot(data, showmeans=True, showmedians=True)
for pc in vp['bodies']:
    pc.set_facecolor('steelblue')
    pc.set_alpha(0.7)
```

## Pie Charts

```python
labels = ['A', 'B', 'C', 'D']
sizes = [30, 25, 25, 20]
explode = (0.05, 0, 0, 0)  # Offset first slice

wedges, texts, autotexts = ax.pie(
    sizes, labels=labels, explode=explode,
    autopct='%1.1f%%', startangle=90,
    colors=['C0', 'C1', 'C2', 'C3']
)
ax.axis('equal')  # Equal aspect for circular pie
```

## Stem Plots

```python
ax.stem(x, y, linefmt='C0-', markerfmt='o', basefmt='k-')
# Or: (markerline, stemlines, baseline) = ax.stem(x, y)
```

## Horizontal/Vertical Lines and Spans

```python
ax.axhline(y=0, color='red', linestyle='--', linewidth=1)
ax.axvline(x=5, color='blue', linestyle=':', linewidth=1)
ax.axhspan(ymin=0, ymax=5, alpha=0.2, color='yellow')
ax.axvspan(xmin=0, xmax=3, alpha=0.2, color='green')
```

## Correlation Plots

```python
# Autocorrelation
ax.acorr(data, maxlags=50)

# Cross-correlation
ax.xcorr(x, y, maxlags=50, usevlines=True)
```

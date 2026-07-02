# Themes and Styling

Seaborn manages matplotlib rcParams for consistent visual styling.

## set_theme

Set the overall visual theme (recommended entry point).

```python
sns.set_theme(style="darkgrid", context="talk", palette="deep", font="sans-serif", font_scale=1.2)
```

**Parameters:**
- `context` — `"paper"` (smallest), `"notebook"` (default), `"talk"`, `"poster"` (largest). Controls font sizes and line widths.
- `style` — `"darkgrid"` (default), `"whitegrid"`, `"dark"`, `"white"`, `"ticks"`. Controls background, grid, and spine visibility.
- `palette` — default color palette name or list (default `"deep"`)
- `font` — `"sans-serif"` (default), `"serif"`, `"monospace"`, or font name
- `font_scale` — multiplier for font sizes (default 1)
- `color_codes` — `True` (default, enable C0-C9 color shortcuts), `False`
- `rc` — dict of additional rcParams to set

**Note:** `set_theme()` calls both `set_context()` and `set_style()` internally. It also resets any previously customized rcParams.

## set_style

Set only the axes style (background, grid, spines).

```python
sns.set_style("whitegrid")
```

**Styles:**
| Style | Background | Grid | Spines |
|-------|-----------|------|--------|
| `"darkgrid"` | Light gray | Horizontal + vertical | Hidden |
| `"whitegrid"` | White | Horizontal + vertical | Visible |
| `"dark"` | Dark gray | None | Hidden |
| `"white"` | White | None | Visible |
| `"ticks"` | White | None | Visible with ticks |

**Custom rcParams:**
```python
sns.set_style("whitegrid", {"axes.linewidth": 1.5, "grid.alpha": 0.3})
```

## set_context

Set element scaling (font sizes, line widths, tick sizes).

```python
sns.set_context("talk", font_scale=1.2)
```

**Contexts:**
| Context | Axes label | Tick label | Grid linewidth |
|---------|-----------|------------|----------------|
| `"paper"` | 1.0pt | 8.0pt | 0.40 |
| `"notebook"` | 1.0pt | 8.0pt | 0.50 |
| `"talk"` | 1.5pt | 10.0pt | 0.80 |
| `"poster"` | 2.0pt | 14.0pt | 1.20 |

## axes_style

Get or temporarily apply style settings.

```python
# Get style dict
style_dict = sns.axes_style("whitegrid")

# Use as context manager
with sns.axes_style("whitegrid"):
    sns.histplot(data=df, x="value")
# Style reverts after the block
```

## reset_defaults / reset_orig

```python
sns.reset_defaults()  # restore matplotlib defaults
sns.reset_orig()      # restore original rcParams (before seaborn was imported)
```

## move_legend

Move legend to a different position.

```python
ax = sns.scatterplot(data=df, x="x", y="y", hue="group")
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
```

**Positions:** `"best"`, `"upper right"`, `"upper left"`, `"lower left"`, `"lower right"`, `"right"`, `"center"`, `"lower center"`, `"upper center"`, `"center left"`, `"center right"`.

**Outside plot:** Use `bbox_to_anchor=(x, y)` to position outside the axes.

## Style Recommendations

- **Exploratory analysis**: `set_theme(style="darkgrid")` — grid helps read values
- **Publication**: `set_theme(style="white", context="paper")` — clean, no grid
- **Presentation**: `set_theme(style="darkgrid", context="talk")` — larger fonts, grid for readability
- **Poster**: `set_theme(style="whitegrid", context="poster")` — very large fonts

## Color Shortcuts

When `color_codes=True` (default), matplotlib's C0–C9 shortcuts map to the current palette:

```python
ax.plot(x, y1, color="C0")  # first palette color
ax.plot(x, y2, color="C1")  # second palette color
```

# Palettes and Colors

Seaborn provides comprehensive color palette utilities.

## color_palette

General palette accessor.

```python
# Named palette
colors = sns.color_palette("deep")           # default 6 colors
colors = sns.color_palette("deep", 10)        # 10 colors

# Matplotlib colormap
colors = sns.color_palette("viridis", 20)     # 20 samples from viridis

# As continuous colormap
cmap = sns.color_palette("mako", as_cmap=True)
```

**Named palettes:**
| Palette | Description |
|---------|-------------|
| `"deep"` | Default, 6 saturated colors |
| `"muted"` | Saturated but softer |
| `"pastel"` | Light, pastel versions |
| `"bright"` | High saturation, bright |
| `"dark"` | Darker versions |
| `"colorblind"` | Colorblind-safe (6 colors) |
| `"husl"` | Evenly spaced in HUSL |
| `"hls"` | Evenly spaced in HLS |

**Matplotlib colormaps:** `"viridis"`, `"plasma"`, `"inferno"`, `"magma"`, `"cividis"`, `"coolwarm"`, `"seismic"`, `"RdBu"`, `"BrBG"`, `"PiYG"`, `"PuOr"`, `"RdYlGn"`, `"RdYlBu"`, `"YlGnBu"`, `"YlOrRd"`, `"YlGn"`, `"Blues"`, `"Greens"`, `"Oranges"`, `"Reds"`, `"Purples"`, `"Greys"`.

**Seaborn colormaps:** `"mako"`, `"crest"`, `"flare"`, `"rocket"`, `"icefire"`, `"light"`, `"dark"`.

## Sequential Palettes

Single hue, varying lightness/saturation.

```python
# Matplotlib sequential
sns.color_palette("Blues", 7)
sns.color_palette("YlOrRd", 9)

# Dark-to-color
sns.dark_palette("red", 7)
sns.dark_palette("#e69f00", 7)

# Light-to-color
sns.light_palette("blue", 7)
sns.light_palette("#009e73", 7)

# Reverse
sns.dark_palette("red", 7, reverse=True)
```

## Diverging Palettes

Two hues meeting at a neutral center.

```python
# HUSL-based diverging
sns.diverging_palette(250, 15, s=75, l=50, n=9, center="light")
# h_neg=250 (blue), h_pos=15 (red), s=saturation, l=lightness, n=number of colors

# Matplotlib diverging
sns.color_palette("coolwarm", 9)
sns.color_palette("RdBu", 9)
sns.color_palette("seismic", 9)
sns.color_palette("BrBG", 9)
```

## cubehelix_palette

Perceptually uniform sequential palette.

```python
sns.cubehelix_palette(
    n_colors=7,
    start=2,       # starting hue (0–3)
    rot=0.4,       # rotation through color wheel (-3 to 3)
    gamma=1.0,     # brightness pre-correction
    hue=0.8,       # hue range (0–1)
    light=0.85,    # lightness at start (0–1)
    dark=0.15,     # lightness at end (0–1)
    reverse=False,
    as_cmap=False
)
```

## blend_palette

Create a palette by blending between colors.

```python
# Blend between two colors
sns.blend_palette(["red", "blue"], 7)

# Blend through multiple colors
sns.blend_palette(["red", "yellow", "green", "blue"], 10)

# As colormap
cmap = sns.blend_palette(["#e69f00", "#56b4e9", "#009e73"], as_cmap=True)
```

## hls_palette / husl_palette

Evenly spaced hues.

```python
# HLS (standard)
sns.hls_palette(8, h=0.01, l=0.6, s=0.65)

# HUSL (perceptually uniform)
sns.husl_palette(8, h=0.01, s=0.9, l=0.65)
```

## mpl_palette

Access matplotlib registered palettes.

```python
sns.mpl_palette("tab10", 10)
sns.mpl_palette("Set2", 8)
```

## set_palette

Set the default palette for all subsequent plots.

```python
sns.set_palette("colorblind")
sns.set_palette(["#e69f00", "#56b4e9", "#009e73", "#f0e442"])
sns.set_palette("viridis", as_cmap=True)  # continuous
```

## choose_cmap

Choose a colormap based on data characteristics.

```python
# Returns a Colormap object
cmap = sns.choose_cmap(data)       # auto-detect
cmap = sns.choose_cmap(data, "sequential")
cmap = sns.choose_cmap(data, "diverging")
cmap = sns.choose_cmap(data,="cyclic")
```

## Color Names

Seaborn exposes named color dictionaries:

```python
# XKCD color names
sns.colors.xkcd_rgb["cranberry"]    # '#8c5653'
sns.colors.xkcd_rgb["baby blue"]    # '#8dcbef'

# Crayola crayon names
sns.colors.crayons["cerulean"]      # '#007fa7'
sns.colors.crayons["raspberry"]     # '#e25641'
```

## Colormap Module

```python
import seaborn.cm as scm

# Seaborn colormaps
scm.mako    # sequential, dark
scm.crest   # sequential, light
scm.flare   # sequential, bright
scm.rocket  # sequential, high contrast
scm.icefire # diverging
scm.light   # sequential, light
scm.dark    # sequential, dark
```

## Palette Selection Guide

| Use case | Recommendation |
|----------|---------------|
| Categorical data (nominal) | `"deep"`, `"muted"`, `"colorblind"` |
| Categorical (accessible) | `"colorblind"` |
| Sequential data | `"Blues"`, `"viridis"`, `"mako"`, `"rocket"` |
| Diverging data | `"coolwarm"`, `"RdBu"`, `diverging_palette()` |
| High contrast | `"bright"`, `"dark"` |
| Publication (grayscale-safe) | `"crest"`, `"mako"`, `"rocket"` |
| Many categories (>10) | `"husl"`, `"hls"`, `cubehelix_palette()` |

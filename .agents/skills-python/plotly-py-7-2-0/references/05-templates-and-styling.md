# Templates and Styling

## Built-in templates (v7.2.0)

Available via `pio.templates` (names verified from `plotly/io/_templates.py`):

`ggplot2`, `seaborn`, `simple_white`, `plotly`, `plotly_white`, `plotly_dark`, `presentation`, `xgridoff`, `ygridoff`, `gridon`, `none`

## Global default

```python
import plotly.io as pio

pio.templates.default = "plotly_white"     # affects all new figures
pio.templates.default = None               # reset
```

The default template is `plotly` (set in `plotly.io` on import).

## Per-figure template

```python
fig.update_layout(template="ggplot2")
```

A template provides figure-wide defaults (colors, fonts, axes, paper/plot background). Explicit per-trace/per-layout attributes override the template.

## Custom templates

Templates are full `go.Layout` objects; build one from an existing template:

```python
import plotly.graph_objects as go
import plotly.io as pio

custom = pio.templates["plotly_white"].clone()
custom.layout.font.family = "Inter"
custom.layout.paper_bgcolor = "white"
custom.layout.plot_bgcolor = "rgba(0,0,0,0)"
custom.layout.colorway = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]
pio.templates["my-template"] = custom
```

## px styling entry points

- `px.defaults.template`, `px.defaults.color`, `px.defaults.font`, `px.defaults.height`, `px.defaults.width` — defaults applied by all px functions
- Per-call: `template=`, `color_continuous_scale=`, `color_discrete_sequence=`, `labels=`, `category_orders=`, `color_discrete_map=`
- `NO_COLOR` sentinel disables a color mapping

## Color scales

`px.colors` re-exports built-in color scales (e.g., `px.colors.sequential.Viridis`, `px.colors.diverging.RdBu`) plus discrete sequences (`px.colors.qualitative.Plotly`, etc.). Sequential scales need `color_continuous_scale`; discrete categorical colors use `color_discrete_sequence` (a list) or `color_discrete_map` (dict).

## v7 color-string rules (CSS Color 4)

Color *strings* are parsed per CSS Color 4. No longer working: `hsv(...)`; `rgb(0.5, 0.5, 0.5)` (0–1 fractions); `hsl(0, 100, 40)` (commas without percent units); hex without `#`. Newly supported: `#ff0000aa`, `#f00a`, `rgb(255 0 0)`, `rgba(255 0 0 / 0.5)`, `hsl(0 100% 50% / 0.5)`, `hwb(...)`, `lab()`, `lch()`, `oklab()`, `oklch()`. An unparseable color falls back to the attribute default — it does not error.

Separately, `plotly.colors.hex_to_rgb` now parses 3-digit shorthand (`#FFF`) correctly (7.0.0) and raises on invalid-length hex codes, warning on hex codes containing alpha (7.1.0).

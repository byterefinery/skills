# Templates and Styling

## Built-in templates

```python
import plotly.io as pio

# Available templates
print(pio.templates)
# plotly, plotly_white, plotly_dark, plotly_netlify,
# ggplot, seaborn, xgridon, presentation

# Set global default
pio.templates.default = "plotly_white"

# Per-figure
fig.update_layout(template="ggplot")
```

## Custom templates

```python
import plotly.graph_objects as go
import plotly.io as pio

# Clone and modify
custom = pio.templates["plotly_white"].clone()
custom.layout.font = dict(family="Inter", size=12, color="#333")
custom.layout.plot_bgcolor = "rgba(0,0,0,0)"
custom.layout.paper_bgcolor = "rgba(0,0,0,0)"
custom.layout.xaxis.gridcolor = "#eee"
custom.layout.yaxis.gridcolor = "#eee"

# Register
pio.templates["my_theme"] = custom

# Use
fig = px.scatter(df, x="x", y="y", template="my_theme")
```

## Color sequences

```python
# Discrete (categorical colors)
fig.update_traces(marker_color=px.colors.qualitative.Plotly)
# Other palettes: Pastel, Safe, Alpha, Dark2, Colorblind, Tableau

# Continuous (colormaps)
fig = px.scatter(df, x="x", y="y", color="z",
    color_continuous_scale="Viridis")
# Options: Viridis, Plots, Hot, Cool, Balance, Earth, Electric, Matter,
# YlGnBu, RdBu, Portland, Turbo, Cividis, etc.

# Reversed
color_continuous_scale="Viridis_r"

# Custom scale
color_continuous_scale=[[0, "blue"], [0.5, "white"], [1, "red"]]
```

## Color scale reference

| Category | Palettes |
|----------|----------|
| Sequential | Viridis, Cividis, Turbo, Blues, YlGnBu, RdYlBu |
| Diverging | RdBu, PiYG, BrBG, coolwarm, Balance, Earth |
| Qualitative | Plotly, Pastel, Safe, Dark2, Colorblind, Tableau |
| Perceptual | Hot, Electric, Matter, Plot3, Deephot |

Access via `px.colors.sequential.Viridis`, `px.colors.qualitative.Plotly`, `px.colors.diverging.RdBu`.

## Font styling

```python
fig.update_layout(
    font=dict(family="Inter", size=14, color="#333"),
    title_font=dict(size=24, weight="bold"),
    xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
    legend=dict(font=dict(size=12, family="Helvetica")),
)
```

## Background and grid

```python
fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(gridcolor="#e0e0e0", gridwidth=1),
    yaxis=dict(gridcolor="#e0e0e0", gridwidth=1),
)
```

## Bar styling

```python
fig.update_traces(
    marker=dict(
        line=dict(width=1, color="white"),
        cornerradius=4,        # rounded corners (v6.2+)
    ),
    textposition="outside",    # "outside", "inside", "auto", None
    texttemplate="%{y:,.0f}",
    hovertemplate="%{x}<br>%{y:,.0f}",
)
```

## Legend

```python
fig.update_layout(
    legend=dict(
        x=1.02, y=1,           # position outside plot
        xanchor="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1,
        itemsizing="constant",  # trace, constant
        traceorder="normal",    # normal, reversed, grouped, grouped+reversed
        font=dict(size=12),
    )
)
```

## Margins

```python
fig.update_layout(
    margin=dict(l=60, r=30, t=50, b=50, pad=5),
    height=500,
    width=700,
)
```

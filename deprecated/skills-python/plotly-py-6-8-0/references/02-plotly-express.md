# Plotly Express

## Common parameters

All `px` functions share these parameters:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `data_frame` | DataFrame | Input data (pandas, polars, narwhals-compatible) |
| `x`, `y` | str | Column names for axes |
| `color` | str | Column for color grouping |
| `symbol` | str | Column for marker symbol |
| `size` | str | Column for marker size |
| `facet_row`, `facet_col` | str | Columns for faceting |
| `animation_frame`, `animation_group` | str | Columns for animation |
| `hover_name`, `hover_data` | str/list | Columns shown in hover |
| `text` | str | Column for text labels on markers/bars |
| `title` | str | Figure title |
| `template` | str | Template name (`"plotly_white"`, `"ggplot"`, etc.) |
| `color_discrete_sequence` | list | Override color palette |
| `color_continuous_scale` | str/list | Colormap for continuous colors |
| `render_mode` | str | `"webgl"` or `"svg"` for scatter/line |

## Cartesian chart functions

| Function | Description |
|----------|-------------|
| `px.scatter()` | Scatter plot |
| `px.line()` | Line chart |
| `px.area()` | Stacked area chart |
| `px.bar()` | Bar chart (vertical) |
| `px.histogram()` | Histogram with optional marginal |
| `px.box()` | Box plot |
| `px.violin()` | Violin plot |
| `px.strip()` | Strip/jitter plot |
| `px.ecdf()` | Empirical CDF |
| `px.density_contour()` | Density contour plot |
| `px.density_heatmap()` | Density heatmap |
| `px.imshow()` | Image/array heatmap (supports `facet_row` since v6.7) |

## Polar and ternary

| Function | Description |
|----------|-------------|
| `px.scatter_polar()` | Polar scatter |
| `px.line_polar()` | Polar line |
| `px.bar_polar()` | Polar bar (rose chart) |
| `px.scatter_ternary()` | Ternary scatter |
| `px.line_ternary()` | Ternary line |

## 3D charts

| Function | Description |
|----------|-------------|
| `px.scatter_3d()` | 3D scatter |
| `px.line_3d()` | 3D line |

## Map charts

| Function | Description |
|----------|-------------|
| `px.scatter_map()` | MapLibre scatter map |
| `px.line_map()` | MapLibre line map |
| `px.choropleth_map()` | MapLibre choropleth |
| `px.density_map()` | MapLibre density map |
| `px.scatter_mapbox()` | Mapbox scatter (deprecated) |
| `px.line_mapbox()` | Mapbox line (deprecated) |
| `px.choropleth_mapbox()` | Mapbox choropleth (deprecated) |
| `px.scatter_geo()` | SVG geo scatter |
| `px.line_geo()` | SVG geo line |
| `px.choropleth()` | SVG choropleth |

## Hierarchical and special

| Function | Description |
|----------|-------------|
| `px.pie()` | Pie chart |
| `px.sunburst()` | Sunburst chart |
| `px.treemap()` | Treemap |
| `px.icicle()` | Icicle chart |
| `px.funnel()` | Funnel chart |
| `px.funnel_area()` | Funnel area chart |
| `px.timeline()` | Timeline/Gantt |
| `px.parallel_coordinates()` | Parallel coordinates |
| `px.parallel_categories()` | Parallel categories |
| `px.scatter_matrix()` | Scatter matrix (SPLOM) |

## Trendline

```python
fig = px.scatter(df, x="x", y="y", trendline="ols")
# Options: "ols", "lowess", "exponential", "polynomial"
# Requires statsmodels (ols, lowess) or numpy (polynomial, exponential)

# Access trendline results
results = px.get_trendline_results(fig)
```

## Faceting

```python
# Row and column facets
fig = px.scatter(df, x="x", y="y", facet_row="category", facet_col="region")

# Control facet layout
fig.update_layout(margin=dict(t=100, b=50), height=600)
fig.update_xaxes(matches=None)  # independent x scales per facet
```

## Animation

```python
fig = px.scatter(
    df, x="x", y="y",
    animation_frame="year",      # frames ordered by this column
    animation_group="country",   # unique trace per group
)
fig.update_traces(mode="lines+markers")
```

## Hover customization

```python
# Custom hover template
fig = px.scatter(df, x="x", y="y",
    hover_data=["extra_col"],
    hover_name="label",
    hover_template="%{x}<br>%{y}<br>Extra: %{extra_col}"
)

# Use NO_COLOR to skip a column from color encoding
from plotly.express import NO_COLOR
fig = px.bar(df, x="x", y="y", color=NO_COLOR)
```

## Category ordering

```python
fig = px.bar(df, x="category", y="value",
    category_orders={"category": ["C", "B", "A"]})
```

## IdentityMap and Constant

```python
from plotly.express import IdentityMap, Constant, Range

# Map column values directly (no aggregation)
fig = px.scatter(df, x=IdentityMap("x"), y=IdentityMap("y"))

# Constant values
fig = px.scatter(df, x="x", y=Constant(0))

# Range for histogram bins
fig = px.histogram(df, x="value", nbins=Range(0, 100))
```

# Figure Factories

`plotly.figure_factory` (`ff`) provides convenience functions for complex chart types. Requires numpy.

## Annotated heatmap

```python
import plotly.figure_factory as ff

data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
fig = ff.create_annotated_heatmap(
    z=data,
    x=["A", "B", "C"],
    y=["X", "Y", "Z"],
    annotation_text=None,       # or 2D list of strings
    colorscale="Viridis",
    showscale=True,
)
```

## Gantt chart

```python
fig = ff.create_gantt(
    df,                      # DataFrame with columns: Task, Start, Finish, Resource, Complete
    colors={"A": "blue", "B": "green"},
    index=2,                 # zoom level: 0=year, 1=month, 2=day, 3=hour, 4=min, 5=s
    bar_width=0.3,
    show_colorbar=True,
    show_grid=False,
    title="Project Timeline",
)
```

## Dendrogram

```python
fig = ff.create_dendrogram(
    df.values,
    orientation="bottom",     # bottom, top, right, left
    labels=["A", "B", "C"],
    colorscale="Viridis",
    link_color="rgba(255,255,255,0)",
)
```

## Distplot (distribution)

```python
import numpy as np

data = [np.random.normal(0, 1, 1000), np.random.normal(2, 0.5, 1000)]
fig = ff.create_distplot(
    data, ["Group A", "Group B"],
    bin_size=0.1,
    colors=["blue", "red"],
    show_hist=True,
    show_rug=True,
)
```

## Candlestick / OHLC

```python
fig = ff.create_candlestick(df,                  # OHLCV DataFrame
                            open="Open",
                            high="High",
                            low="Low",
                            close="Close",
                            volume="Volume",
                            increasing_line_color="green",
                            decreasing_line_color="red",
)

fig = ff.create_ohlc(df, open="Open", high="High", low="Low", close="Close")
```

## Quiver plot

```python
fig = ff.create_quiver(x, y, u, v,               # coordinates + vectors
                       scale=1,
                       arrow_scale=0.3,
                       scale_units="axes",
)
```

## Streamline

```python
fig = ff.create_streamline(x, y, u, v,           # grid + vector field
                           density=1,
                           arrow_scale=0.3,
                           normalize=False,
)
```

## Table

```python
cells = dict(values=df.values.tolist(),
             titles=df.columns.tolist())
fig = ff.create_table(cells,
                      height=30,
                      font=dict(family="Arial", size=12),
)
```

## Triangular surface

```python
fig = ff.create_trisurf(x, y, z,                 # point clouds
                        colormap="Viridis",
                        title="Triangular Surface",
)
```

## 2D density

```python
fig = ff.create_2d_density(x, y,                 # point coordinates
                           x_edge_count=50,
                           y_edge_count=50,
                           title="2D Density",
)
```

## Facet grid

```python
fig = ff.create_facet_grid(df,                   # DataFrame
                           x="x_col",
                           y="y_col",
                           col="facet_col",
                           col_wrap=3,
                           size=3,
)
```

## Bullet chart

```python
fig = ff.create_bullet(
    actual=75,
    compare=80,
    ranges=[0, 50, 75, 100],
    ranges_colors=["#d66", "#faa", "#aef"],
    title="Performance",
)
```

## Choropleth (US counties)

```python
# Requires pandas and plotly-geo
fig = ff.create_choropleth(
    fips="state_fips_codes",
    values="data_values",
    scope=["USA"],
    state_colorscale=px.colors.sequential.Viridis,
)
```

## Violin

```python
fig = ff.create_violin(data,                     # list of arrays or DataFrame columns
                       title="Violin Plot",
                       show_box=True,             # show box inside violin
                       point_width=0.5,
                       scale="area",              # area, count, width
)
```

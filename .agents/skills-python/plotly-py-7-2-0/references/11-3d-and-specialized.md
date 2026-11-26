# 3D and Specialized Plots

## 3D traces

- `go.Scatter3d` — 3D point/line scatter (`mode="markers"`, `line`, `surface`)
- `go.Surface` — height-map surface from a 2D `z` matrix (`cmin`/`cmax`/`colorscale`)
- `go.Mesh3d` — surface from triangles
- `go.Volume` — 3D volumetric rendering
- `go.Cone` — cone trace for vector fields (3D quiver-like)
- `go.Streamtube` — streamtubes from a vector field (also `ff.create_streamline` for 2D-style streamlines)
- `go.Isosurface` — isosurfaces from 3D scalar data
- `px.scatter_3d`, `px.line_3d` — Express wrappers

```python
import plotly.graph_objects as go

fig = go.Figure(go.Surface(z=[[1, 2, 3], [4, 5, 6]], colorscale="Viridis"))
fig.update_layout(scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"))
```

3D subplot type in `make_subplots`: `specs=[[{"type": "scatter3d"}]]`.

## Quiver plots (new in v7)

`go.Quiver` is the native 2D vector-field trace added in v7 (plotly.js 4.0). It supersedes `ff.create_quiver` as the recommended approach (`create_quiver` remains for its `angle` and `scaleratio` options).

```python
import plotly.graph_objects as go

fig = go.Figure(go.Quiver(
    x=[0, 1, 2, 0, 1, 2],
    y=[0, 0, 0, 1, 1, 1],
    u=[1, 0.5, 0, 0.5, 0, -0.5],
    v=[0, 0.5, 1, 0.5, 1, 0.5],
))
```

## Sankey (changed in v7)

- Layout algorithm updated (`@plotly/d3-sankey` 0.7.2 → 0.12.3): node positions and link paths shift slightly for the same data, with links tending to cross less.
- New `node.sort` and `link.sort`: default `"auto"` reorders nodes within a column and links within a node to reduce crossings; `"input"` keeps the order given in `node.label` and `link.source`/`link.target` (stable renders, or when order carries meaning).
- New `direction` attribute: `"forward"` (default) or `"reversed"` — flow along the `orientation` axis.

```python
fig = go.Figure(go.Sankey(
    node=dict(label=["A", "B"], pad=15, thickness=20, sort="input"),
    link=dict(source=[0], target=[1], value=[4], sort="input"),
))
```

## Specialized chart types

- **Splom** — `go.Splom` (scatter plot matrix). In v7, `axis.matches` defaults to `True`: axes in the same row/column are linked and pan/zoom together. Set `matches=False` for the previous behavior. px equivalent: `px.scatter_matrix`.
- **Parallel coordinates/categories** — `go.Parcoords` / `px.parallel_coordinates`, `px.parallel_categories`
- **Polar** — `go.Scatterpolar`, `go.Barpolar`; px: `scatter_polar`, `line_polar`, `bar_polar` (wind rose)
- **Ternary** — `go.Scatterternary`; px: `scatter_ternary`, `line_ternary`; factory: `ff.create_ternary_contour`
- **Carpet** — `go.Carpet` (carpet plots, contour on carpet)
- **Contour / density** — `go.Contour`, `px.density_contour`, `px.density_heatmap`
- **Gauge / indicator** — `go.Indicator` (replaces removed `create_bullet`)
- **Waterfall, funnel, icicle, treemap, sunburst** — `go.Waterfall`, `go.Funnel`/`go.Funnelarea`, `go.Icicle`, `go.Treemap`, `go.Sunburst` (+ px equivalents)
- **Table** — `ff.create_table`
- **Dendrogram** — `ff.create_dendrogram` (scipy required)

## MathJax / LaTeX annotations

MathJax v3 and v4 are supported in v7 (v2 removed). If your environment loads MathJax itself (notebook, custom HTML page), ensure it is v3+.

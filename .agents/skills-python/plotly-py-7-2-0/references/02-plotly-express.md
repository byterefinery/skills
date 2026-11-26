# Plotly Express

## All px functions (v7.2.0)

From `plotly/express/__init__.py`:

- **Basics** — `scatter`, `line`, `area`, `bar`, `timeline`, `funnel`, `bar_polar`, `scatter_polar`, `line_polar`
- **Part-of-whole** — `pie`, `sunburst`, `treemap`, `icicle`, `funnel_area`
- **1D distributions** — `histogram`, `box`, `violin`, `strip`, `ecdf`
- **2D distributions** — `density_heatmap`, `density_contour`
- **Matrix / image input** — `imshow`
- **3D** — `scatter_3d`, `line_3d`
- **Multidimensional** — `scatter_matrix`, `parallel_coordinates`, `parallel_categories`
- **Tile maps (MapLibre)** — `scatter_map`, `line_map`, `choropleth_map`, `density_map`
- **Outline maps** — `scatter_geo`, `line_geo`, `choropleth`
- **Ternary** — `scatter_ternary`, `line_ternary`

Note: `scatter_mapbox`, `line_mapbox`, `choropleth_mapbox`, `density_mapbox` were removed in v7 (use the `*map` versions above).

Also exported: `defaults`, `get_trendline_results`, `NO_COLOR`, plus special input helpers `IdentityMap`, `Constant`, `Range`.

## Common parameters

Most 2D cartesian functions share a consistent parameter set:

| Parameter | Purpose |
|---|---|
| `x`, `y` | Columns/arrays for axes (lists, dicts, or DataFrame columns) |
| `color`, `size`, `symbol`, `text` | Discrete or continuous encoding |
| `labels` | Override axis/legend/colorbar labels |
| `category_orders` | Fix category order and palette assignment |
| `color_discrete_map`, `color_discrete_sequence` | Categorical color control |
| `color_continuous_scale`, `color_continuous_midpoint` | Sequential color scale control |
| `facet_row`, `facet_col`, `facet_col_wrap`, `facet_titles` | Faceting |
| `marginal`, `marginal_x`, `marginal_y` | Marginal distributions ("box", "violin", "histogram", "ecdf"; 7.1+ adds `marginal_x`/`marginal_y="heatmap"` for density functions) |
| `animation_frame`, `animation_group` | Simple frame animation |
| `log_x`, `log_y` | Log scale |
| `template`, `color_continuous_scale`, etc. | Any layout attribute |

Every px function returns a `go.Figure` — use `update_layout`, `add_trace`, `add_hline`, etc. afterward.

## Demo datasets (`px.data`)

`gapminder()`, `tips()`, `iris()`, `wind()`, `election()`, `election_geojson()`, `carshare()`, `stocks()`, `experiment()`, `medals_wide()`, `medals_long()`.

## Styling

- `px.defaults` — set defaults for all subsequent px calls (`px.defaults.template = "plotly_white"`, `px.defaults.color = "..."`, ...)
- `NO_COLOR` — sentinel to disable color encoding
- `labels={"col": "Label"}` overrides automatic labels
- Automatic hover labels come from labels; control with `hover_name` / `hover_data`
- `category_orders` fixes both ordering and, combined with `color_discrete_map`, the color per category

## Trendlines

`px.scatter` supports `trendline="ols"` (ordinary least squares) and `trendline="lowess"` (locally weighted scatterplot smoothing). Both require `statsmodels` to be installed. The trendline is fitted per trace; hover shows the equation and R-squared. `trendline_scope="overall"` fits a single line on the entire dataset (overlaid on all facets/frames); `trendline_color_override` changes its color. `px.get_trendline_results(fig)` returns the underlying model parameters.

## v7/v7.x Express fixes worth knowing

- `trendline_scope="overall"` no longer draws the overall trendline on `marginal_x`/`marginal_y` subplots (7.2.0)
- `px.sunburst`, `px.treemap`, `px.icicle` with `path` on a Polars DataFrame now list sectors in order of first appearance across all backends (7.2.0)
- `px.imshow` / faceted figures now honor `facet_row_spacing=0` and `facet_col_spacing=0` (7.2.0)
- px no longer mutates lists passed to `x`/`y` in wide mode (7.2.0)
- unsigned integer columns (`uint8`–`uint64`) are no longer treated as categorical, so orientation is inferred correctly (7.1.0)

# Figure Factories (v7)

## What remains in v7.2.0

`plotly.figure_factory` (alias `ff`) in v7 provides:

- `create_dendrogram` — hierarchical clustering tree (with scipy linkage)
- `create_table` — styled data table with optional column grouping
- `create_trisurf` — 3D triangular surface from a set of points
- `create_streamline` — streamlines from a vector field (scatter or path mode)
- `create_quiver` — 2D quiver plot (superseded by the native `go.Quiver` trace in v7; prefer that)
- `create_ternary_contour` — ternary contour
- `create_hexbin_map` — hexbin tile map (MapLibre-based; the Mapbox version is gone)

Access via `import plotly.figure_factory as ff` then `ff.create_table(...)`.

## Removed in v7 (and recommended alternatives, per the Figure Factories doc)

| Removed factory | Use instead |
|---|---|
| `create_2d_density` | `px.density_heatmap` |
| `create_annotated_heatmap` | `px.imshow` |
| `create_bullet` | `go.Indicator` |
| `create_candlestick` | `go.Candlestick` |
| `create_choropleth` | `px.choropleth` with custom GeoJSON |
| `create_distplot` | Plotly Express functions like `px.histogram` |
| `create_facet_grid` | px functions with `facet_row` and `facet_col` |
| `create_gantt` | `px.timeline` |
| `create_hexbin_mapbox` | `create_hexbin_map` |
| `create_ohlc` | `go.Ohlc` |
| `create_scatterplotmatrix` | `go.Splom` |
| `create_violin` | `go.Violin` |

Note: `create_quiver` remains in v7 but quiver plots are better made with the native `go.Quiver` trace type since v7.0; `create_quiver` is kept for its `angle` and `scaleratio` options.

`plotly.tools.FigureFactory` is a deprecated shim — it warns and forwards to `plotly.figure_factory` (only for the still-existing factories).

## mpl_to_plotly (plotly.tools)

`plotly.tools.mpl_to_plotly(fig, resize=False, strip_style=False, verbose=False)` converts a matplotlib `Figure` into a `go.Figure`. v7.x improvements (from the 7.0.0–7.2.0 changelogs):

- twinned/overlaid subplots (`twinx`/`twiny`): tick mirroring, axis positioning, trace visibility fixed (7.2.0)
- spine and tick label colors exported to Plotly axis `linecolor`/`tickfont` (7.2.0)
- step plots: `steps-pre`/`steps-post`/`steps-mid` mapped to Plotly step line shapes (7.2.0)
- stairs plots rendered as step lines or filled step areas (7.2.0)
- transparent/`"none"`/alpha colors handled through a single helper (7.2.0)
- touching bars (`plt.hist`): `bargap` clamped to [0, 1] (7.2.0)
- placeholder legend entries (`_nolegend_`, `_childN`) suppressed; `showlegend=False` unless the source figure defines a legend (7.2.0)
- contour lines/line collections: closed rings, dash styles, date axes, `None` separators between subpaths, grouped same-style lines (7.2.0)
- reference lines (`axhline`/`axvline`/axes-coordinate lines) exported as layout shapes, incl. date axes (7.2.0)
- custom tick values when ticks aren't arithmetic (7.1.0)
- `paper_bgcolor`/`plot_bgcolor` from matplotlib backgrounds (7.1.0)
- path collections in data coordinates (violin, pcolor, fill_between, stem) rendered as filled polygons/lines (7.0.0)

## Dash conversion

`plotly.tools.convert_dash` converts Dash chart specs to Plotly. 7.2.0 fixed dotted-line (`linestyle=':'`) mapping (was invalid `'circle'`, now `'dot'`) and preserves custom dash patterns as pixel lists.

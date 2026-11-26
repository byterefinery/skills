# v7 Migration (v6 → v7)

Grounded in the official "Changes in Version 7" guide (`doc/python/v7-changes.md`) and the 7.0.0–7.2.0 CHANGELOG entries. Version 7 upgrades the bundled plotly.js from v3 to v4 (4.1.1 in 7.2.0), so it includes both plotly.js and plotly.py changes. Most figures render without any changes; the cases below need code updates.

## Python version

- v7.2.0 removed Python 3.8 and 3.9 support — plotly.py now requires Python 3.10+.

## Removed traces (Mapbox)

| Removed | Use instead |
|---|---|
| `go.Scattermapbox` | `go.Scattermap` |
| `go.Choroplethmapbox` | `go.Choroplethmap` |
| `go.Densitymapbox` | `go.Densitymap` |
| `px.scatter_mapbox` | `px.scatter_map` |
| `px.line_mapbox` | `px.line_map` |
| `px.choropleth_mapbox` | `px.choropleth_map` |
| `px.density_mapbox` | `px.density_map` |

The MapLibre-based traces have the same attributes.

## Removed attributes

- **`layout.mapbox`** — removed; use `layout.map` (same attributes). In Express, `mapbox_style` becomes `map_style`.
- **`stream`** — removed from all traces (configured the retired Chart Studio streaming service).
- **`*src` attributes** — `xsrc`, `ysrc`, `textsrc`, `marker.colorsrc`, etc., plus `layout.hidesources` (Chart Studio data sources).
- **Chart Studio config options** — `showLink`, `link_text`, `sendData`, `showSources`, `showEditInChartStudio` removed. Use `showSendToCloud` (enabled by default in v7; adds a "Share chart…" modebar button).

## Removed figure factories

`create_2d_density`, `create_annotated_heatmap`, `create_bullet`, `create_candlestick`, `create_choropleth`, `create_distplot`, `create_facet_grid`, `create_gantt`, `create_hexbin_mapbox`, `create_ohlc`, `create_scatterplotmatrix`, `create_violin`. See [08-figure-factories](08-figure-factories.md) for the recommended alternative for each.

## Static image export

- Kaleido < 1.0.0 support removed; Orca support removed.
- The `engine` argument removed from `fig.write_image()`, `fig.to_image()`, `pio.write_image()`, `pio.write_images()`, `pio.to_image()`, `pio.full_figure_for_development()`, and renderer constructors.

## Changed defaults

- **Maps fit your data** — `layout.geo.fitbounds` defaults to `"locations"` (was `False`); new `layout.map.fitbounds` defaults to `"locations"` for tile maps. Set `fitbounds=False` for the previous world view. Setting view attributes (`center`, `zoom`, `projection.scale`, ranges, rotation) also disables auto-fitting.
- **Overlaying axes share tick positions** — `yaxis2.overlaying="y"` now defaults `tickmode="sync"`. Use `tickmode="auto"` for the previous independent grid.
- **Splom axes linked** — `go.Splom` defaults `axis.matches` to `True`. Use `matches=False` for the previous behavior.

## Color parsing (CSS Color 4)

No longer produces the same color (unparseable colors fall back to the attribute default):

| No longer works | Example | Use instead |
|---|---|---|
| `hsv()` color function | `"hsv(200, 80%, 80%)"` | `"hsl(200, 67%, 47%)"`, `"hwb()"`, hex, or `"rgb()"` |
| Comma-separated hsl without percent units | `"hsl(0, 100, 40)"` | `"hsl(0, 100%, 40%)"` or space-separated `"hsl(0 100 40)"` |
| Channel values as fractions of 1 | `"rgb(0.5, 0.5, 0.5)"` (now near black) | `"rgb(128, 128, 128)"` |
| Hex without leading `#` | `"fff"` | `"#fff"` |

These rules apply to color strings only — numeric arrays used with a colorscale are unaffected. Automatically computed contrast colors (e.g., text on heatmap cells) can shift slightly around mid-luminance backgrounds. Separately, `plotly.colors.hex_to_rgb` parses 3-digit shorthand (`#FFF`) correctly (7.0.0 fix).

## Country names

`locationmode="country names"` is now resolved by `country-iso-search` (more forms accepted — ISO-3166 codes, UN M49 numeric codes, flag emoji, historical/native names; case/accents/punctuation ignored; partial phrases rejected). Unrecognized names are logged and their locations skipped. Use `locationmode="ISO-3"` for certainty.

## Tile map rendering (go.Scattermap)

- Marker icons are tinted with `marker.color` (were always black).
- Maki icon set updated 2.1 → 8.2; a few icon names removed.
- Legend swatches always draw a circle, regardless of `marker.symbol`.

## Sankey

Layout algorithm updated (0.7.2 → 0.12.3): positions shift slightly, links cross less. New `node.sort`/`link.sort` (`"auto"` default, `"input"` to preserve input order) and `direction` (`"forward"`/`"reversed"`) attributes.

## New in v7

- **`go.Quiver`** — native 2D vector-field trace (supersedes `ff.create_quiver`).
- **Geo zoom limits** — `layout.geo.projection.minscale` / `maxscale` clamp user zoom (multipliers of `projection.scale`).
- **plotly.js 4.0/4.1 features** — "Share Chart" modebar button, opt-in JSON-download modebar button (4.1), `legend.groupdoubleclick` (4.1), 500 ms double-click delay (4.1), MathJax v3/v4 (v2 removed), culori color processing, `<!doctype html>` in `to_html()` output (7.0.0).

## Notable 7.1.0 / 7.2.0 fixes

- `marginal_x`/`marginal_y="heatmap"` added for `density_heatmap` (7.1.0)
- `hex_to_rgb` raises on invalid-length hex, warns on alpha hex (7.1.0)
- `Figure.show()` div size fixed in Google Colab (7.1.0)
- px unsigned-integer columns no longer treated as categorical (7.1.0)
- JupyterLab figures redraw on `update_display_data` / `DisplayHandle.update`; animations no longer stuck on first frame (7.2.0)
- `mpl_to_plotly`: twinned subplots, spine/tick colors, reference lines, step/stairs plots, path collections, contour lines, bargap clamping, placeholder legends (7.0.0–7.2.0)
- `write_images` honors `layout.width`/`layout.height` (7.2.0)
- `px.sunburst`/`treemap`/`icicle` sector order stable across DataFrame backends (7.2.0)
- `facet_row_spacing=0` / `facet_col_spacing=0` honored (7.2.0)
- Color utilities no longer mutate passed color lists (7.2.0)
- Concurrent first access to lazily initialized graph object properties no longer raises `ValueError("Invalid value")` (7.2.0)

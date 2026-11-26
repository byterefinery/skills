# plotly.js 4.3.0 — trace types

47 trace types from the `src/traces/` directory of plotly.js v4.3.0. The `type` field of a trace object selects one of these (e.g. `{type: 'scatter', x: [...], y: [...]}`). Partial-bundle membership from `dist/README.md`.

## 2D cartesian (18)

bar, box, candlestick, contour, funnel, funnelarea, heatmap, histogram, histogram2d, histogram2dcontour, indicator, ohlc, pie, scatter, splom, table, violin, waterfall

## 2D WebGL (4)

scattergl (large point clouds), parcoords, parcats, quiver (vector fields; new in 4.0.0)

## Polar (3)

barpolar, scatterpolar, scatterpolargl

## 3D (7)

cone, isosurface, mesh3d, scatter3d, streamtube, surface, volume

## Geo and maps (10)

carpet, choropleth, choroplethmap, contourcarpet, densitymap, image, scattercarpet, scattergeo, scattermap, scattersmith

## Hierarchical and flow (4)

icicle, sankey, sunburst, treemap

## Ternary (1)

scatterternary

## Bundle coverage

- basic: bar, pie, scatter
- cartesian: bar, box, contour, heatmap, histogram, histogram2d, histogram2dcontour, image, pie, scatter, scatterternary, violin
- geo: choropleth, scatter, scattergeo
- gl3d: all 7 3D traces plus scatter
- gl2d: parcoords, scatter, scattergl, splom (not parcats)
- map: choroplethmap, densitymap, scatter, scattermap
- finance: bar, candlestick, funnel, funnelarea, histogram, indicator, ohlc, pie, scatter, waterfall
- strict: 46 traces listed in the v4.3.0 dist README — every trace except quiver

The full CDN/npm bundle always contains every trace.

---
name: plotly-js-3-6-0
description: >
  Plotly.js is a standalone JavaScript data visualization library built on d3.js and stack.gl, shipping
  with 40+ chart types including 3D graphs, statistical charts, SVG maps, and financial charts. Use
  this skill whenever the user mentions Plotly.js, plotly charts, interactive web charts, scatter plots,
  line charts, bar charts, pie charts, box plots, violin plots, heatmaps, contour plots, 3D scatter,
  surface plots, mesh3d, candlestick, OHLC, choropleth, geo maps, mapbox maps, sankey diagrams, treemaps,
  sunburst charts, parcoords, splom, waterfall, funnel, indicator gauges, or any interactive data
  visualization in JavaScript using the Plotly.js API (v3.6.0). Also use when the user asks about
  Plotly.newPlot, Plotly.update, Plotly.restyle, Plotly.relayout, Plotly.animate, Plotly.downloadImage,
  plotly.js bundles, CDN loading, or embedding plotly charts in web apps.
metadata:
  tags:
    - visualization
    - charts
    - data-graphics
    - javascript
---

# plotly-js 3.6.0

## Overview

Plotly.js is a high-level, declarative JavaScript charting library. Charts are described as JSON objects with `data` (trace array), `layout` (axes, title, margins, etc.), and optional `config` (interactions, locale, display modes). The library renders interactive SVG and WebGL visualizations into a DOM element.

Plotly.js powers the `plotly` Python and R modules and is maintained by Plotly, Inc. under the MIT license. It requires Node >= 18.0.0.

### Core API

All operations go through the global `Plotly` object:

| Method | Purpose |
|---|---|
| `Plotly.newPlot(gd, data, layout, config)` | Create a new plot in element `gd` |
| `Plotly.addTraces(gd, data, layout)` | Append traces to an existing plot |
| `Plotly.deleteTraces(gd, indices)` | Remove traces by index |
| `Plotly.restyle(gd, data, traces)` | Update trace properties (partial data OK) |
| `Plotly.relayout(gd, layout)` | Update layout properties |
| `Plotly.update(gd, data, layout)` | Combined restyle + relayout |
| `Plotly.extendTraces(gd, data, indices, maxPoints)` | Append data points efficiently |
| `Plotly.purge(gd)` | Destroy plot, free memory |
| `Plotly.delete(gd)` | Alias for purge |
| `Plotly.downloadImage(gd, opts)` | Export as PNG, SVG, JPEG, PDF |
| `Plotly.animate(gd, frames, opts)` | Play animation frames |
| `Plotly.addFrames(gd, frames, traceIndex)` | Add animation frames |

### Data Model

A figure is three parts:

```javascript
var data = [
  { type: 'scatter', x: [1, 2, 3], y: [2, 3, 1], mode: 'lines+markers' }
];
var layout = {
  title: { text: 'My Chart' },
  xaxis: { title: { text: 'X' } },
  yaxis: { title: { text: 'Y' } },
  width: 600,
  height: 400
};
var config = { responsive: true, displayModeBar: true };

Plotly.newPlot('myDiv', data, layout, config);
```

- **`data`** — array of trace objects. Each trace has a `type` and type-specific attributes
- **`layout`** — axes, title, legend, margin, grid (subplots), annotations, shapes, colorscale defaults
- **`config`** — display options: `responsive`, `displayModeBar`, `modeBarButtonsToAdd`, `locale`, `scrollZoom`, `toImageButtonOptions`

### Trace Types

Plotly.js v3.6.0 supports these trace types:

| Category | Trace Types |
|---|---|
| Cartesian | `scatter`, `scattergl`, `bar`, `box`, `violin`, `histogram`, `histogram2d`, `histogram2dcontour`, `heatmap`, `contour`, `image`, `pie`, `scatterpolar`, `scatterpolargl`, `barpolar`, `scatterternary`, `scattersmith`, `scattercarpet`, `contourcarpet`, `table` |
| 3D / GL | `scatter3d`, `surface`, `mesh3d`, `cone`, `streamtube`, `volume`, `isosurface` |
| Geo / Maps | `scattergeo`, `choropleth`, `scattermapbox`, `choroplethmapbox`, `densitymapbox` |
| Financial | `candlestick`, `ohlc`, `waterfall`, `funnel`, `funnelarea`, `indicator` |
| Network / Hierarchical | `sankey`, `parcoords`, `parcats`, `splom`, `treemap`, `icicle`, `sunburst` |

### Bundles

Plotly.js ships partial bundles to reduce payload size. Pick the smallest bundle that covers the trace types you need:

| Bundle | Traces | Minified + gzip |
|---|---|---|
| `basic` | bar, pie, scatter | 365 kB |
| `cartesian` | bar, box, contour, heatmap, histogram, pie, scatter, violin, scatterternary | 464 kB |
| `geo` | choropleth, scatter, scattergeo | 416 kB |
| `gl3d` | cone, isosurface, mesh3d, scatter, scatter3d, streamtube, surface, volume | 528 kB |
| `gl2d` | parcoords, scatter, scattergl, splom | 522 kB |
| `mapbox` | choroplethmapbox, densitymapbox, scatter, scattermapbox | 581 kB |
| `finance` | bar, candlestick, funnel, funnelarea, histogram, indicator, ohlc, pie, scatter, waterfall | 399 kB |
| `strict` | all traces (CSP-safe, no function constructors) | 1.5 MB |
| full | all traces | 1.4 MB |

## Usage

### Loading

**CDN (script tag):**

```html
<script src="https://cdn.plot.ly/plotly-3.6.0.min.js" charset="utf-8"></script>
```

Partial bundles use the same pattern:

```html
<script src="https://cdn.plot.ly/plotly-basic-3.6.0.min.js"></script>
<script src="https://cdn.plot.ly/plotly-cartesian-3.6.0.min.js"></script>
```

**ES6 module (script tag):**

```html
<script type="module">
  import "https://cdn.plot.ly/plotly-3.6.0.min.js"
  Plotly.newPlot("gd", [{ y: [1, 2, 3] }])
</script>
```

**npm:**

```bash
npm i --save plotly.js-dist-min
```

```javascript
// ES6
import Plotly from 'plotly.js-dist-min'

// CommonJS
const Plotly = require('plotly.js-dist-min')
```

Use `plotly.js-dist` for unminified, or partial bundle packages like `plotly.js-cartesian-dist-min`.

### Basic Plot

```javascript
Plotly.newPlot('myDiv', [
  {
    type: 'scatter',
    x: [1, 2, 3, 4],
    y: [2, 3, 5, 7],
    mode: 'lines+markers',
    name: 'Series A'
  }
], {
  title: { text: 'Sample Chart' },
  xaxis: { title: { text: 'X Axis' } },
  yaxis: { title: { text: 'Y Axis' } },
  width: 600,
  height: 400
}, {
  responsive: true
});
```

### Updating an Existing Plot

```javascript
// Change data only
Plotly.restyle('myDiv', { y: [[10, 20, 30, 40]] });

// Change layout only
Plotly.relayout('myDiv', { title: { text: 'Updated Title' } });

// Both at once
Plotly.update('myDiv', { y: [[10, 20]] }, { width: 800 });

// Append points efficiently (for streaming)
Plotly.extendTraces('myDiv', { x: [[5, 6]], y: [[11, 13]] }, [0]);
```

### Exporting

```javascript
Plotly.downloadImage('myDiv', { format: 'png', width: 1200, height: 800, filename: 'chart' });
```

### Localization

```html
<script src="https://cdn.plot.ly/plotly-3.6.0.min.js"></script>
<script src="https://cdn.plot.ly/plotly-locale-de-ch-3.6.0.min.js"></script>
<script>
  Plotly.setPlotConfig({ locale: 'de-CH' });
</script>
```

Or per-plot:

```javascript
Plotly.newPlot('myDiv', data, layout, { locale: 'de-CH' });
```

### MathJax Support

Load MathJax before or alongside Plotly.js:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_SVG.js"></script>
<!-- or MathJax 3 -->
<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js"></script>
```

### Multiple WebGL Graphs

For WebGL 1 traces with multiple graphs on one page, load virtual-webgl first:

```html
<script src="https://unpkg.com/virtual-webgl@1.0.6/src/virtual-webgl.js"></script>
```

## Gotchas

- **`plotly-latest` is frozen at v1.58.5** — the CDN `plotly-latest.min.js` will not be updated past v1. Always specify an exact version: `plotly-3.6.0.min.js`.
- **`newPlot` replaces everything** — calling `Plotly.newPlot()` on an existing div destroys the previous plot. Use `restyle`, `relayout`, or `update` to modify an existing plot instead.
- **`scattergl` needs the right bundle** — `scattergl` (WebGL-accelerated scatter) is available in the full, `gl2d`, `strict`, and `basic` bundles. It is NOT in `cartesian`, `geo`, `gl3d`, `mapbox`, or `finance` bundles.
- **`purge` before reusing a div** — if you need to destroy a plot and reuse the DOM element, call `Plotly.purge(gd)` or `Plotly.delete(gd)` first. Otherwise, event listeners and WebGL contexts leak.
- **`extendTraces` is for streaming** — use `extendTraces` instead of `restyle` when appending data points to live charts. It avoids full re-render and is much faster for streaming data.
- **`maxPoints` in `extendTraces`** — the optional `maxPoints` parameter caps the data array length. Use it to prevent unbounded memory growth in streaming scenarios.
- **Layout `grid` for subplots** — subplot domains (`xaxis.domain`, `yaxis.domain`) are calculated automatically when you set `layout.grid: { rows, columns, pattern }`. Manual domain calculation is error-prone.
- **`scattermapbox` needs Mapbox access token** — set `config: { mapboxAccessToken: 'your-token' }` or `Plotly.registerSanitizer()` for Mapbox-based traces.
- **`choropleth` needs a `locations` or `lon/lat` strategy** — for country choropleths, use `locations` (ISO-3 codes) and `locationmode: 'country names'` or `'ISO-3'`. For custom GeoJSON, use `features` and `projection: { type: 'natural earth' }`.
- **3D plots use WebGL** — `scatter3d`, `surface`, `mesh3d`, `volume`, `cone`, `streamtube`, `isosurface` all require WebGL support. They fall back silently in unsupported environments.
- **`strict` bundle is CSP-safe** — if your environment blocks `eval` or `new Function`, use the `strict` or `strict-min` bundle. It is ~10% larger but works under strict CSP.
- **`config` is optional in `newPlot`** — `Plotly.newPlot(gd, data, layout)` works without config, but defaults show the "Link to Plotly" button. Pass `{ displayModeBar: false }` or `{ toImageButtonOptions: { formats: ['png', 'svg', 'jpeg'] } }` for production.
- **`mode` on scatter controls rendering** — `'markers'`, `'lines'`, `'lines+markers'`, `'text'`, or `'lines+markers+text'`. Default is `'markers'`.
- **`autosize: true` vs fixed `width/height`** — when `autosize: true`, the plot fills the parent div. Set explicit `width`/`height` on the layout for fixed-size charts.
- **`Plotly.addTraces` returns a promise** — all Plotly methods that modify plots return promises. Chain with `.then()` or use `await`.
- **`downloadImage` needs a canvas** — `Plotly.downloadImage` renders through an offscreen canvas. It may fail in headless environments without a canvas backend (e.g., Node.js without `node-canvas`).

## References

- [01-scatter-charts.md](references/01-scatter-charts.md) — Scatter, scattergl, scatterpolar, scatterternary, scattercarpet, splom
- [02-line-charts.md](references/02-line-charts.md) — Line charts, area fills, step lines, error bars, secondary axis
- [03-bar-charts.md](references/03-bar-charts.md) — Bar, barpolar, waterfall, funnel, funnelarea, grouped, stacked
- [04-statistical-charts.md](references/04-statistical-charts.md) — Box, violin, histogram, histogram2d, heatmap, densitymapbox, indicator
- [05-contour-plots.md](references/05-contour-plots.md) — Contour, contourcarpet, filled contours, custom colorscales
- [06-pie-charts.md](references/06-pie-charts.md) — Pie, donut, nested pie, pull effects, hover labels
- [07-financial-charts.md](references/07-financial-charts.md) — Candlestick, OHLC, financial subplots, volume overlay
- [08-geo-maps.md](references/08-geo-maps.md) — Scattergeo, choropleth, geo projections, location modes
- [09-mapbox-maps.md](references/09-mapbox-maps.md) — Scattermapbox, choroplethmapbox, densitymapbox, mapbox styling
- [10-3d-charts.md](references/10-3d-charts.md) — Scatter3d, surface, mesh3d, cone, streamtube, volume, isosurface
- [11-hierarchical-charts.md](references/11-hierarchical-charts.md) — Treemap, icicle, sunburst, hierarchical layouts
- [12-network-charts.md](references/12-network-charts.md) — Sankey, parcoords, parcats, network diagrams
- [13-subplots.md](references/13-subplots.md) — Grid layouts, shared axes, secondary axes, subplot patterns
- [14-events.md](references/14-events.md) — Plotly events: click, hover, relayout, legendclick, zoom, animation events
- [15-animations.md](references/15-animations.md) — Animation frames, slider, button controls, streaming updates
- [16-layout-config.md](references/16-layout-config.md) — Layout attributes, config options, modebar, responsive, localization
- [17-colorscales.md](references/17-colorscales.md) — Built-in colorscales, custom colorscales, reversescale, cmin/cmax
- [18-tables-images.md](references/18-tables-images.md) — Table traces, image traces, probe-image-size, base64 images

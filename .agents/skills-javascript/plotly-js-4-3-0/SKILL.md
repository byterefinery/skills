---
name: plotly-js-4-3-0
description: >
  Plotly.js 4.3.0 is a standalone JavaScript data visualization library that renders
  interactive SVG and WebGL charts from declarative figure objects, and it powers the
  plotly Python and R modules. Use this skill when the user asks about Plotly.newPlot,
  Plotly.react, Plotly.restyle, Plotly.relayout, plotly.js CDN or npm bundles, partial
  bundles, custom bundles, locales, image export, or building any interactive chart
  (scatter, bar, line, pie, box, violin, heatmap, contour, 3D surface, map, choropleth,
  sankey, treemap, sunburst, parcoords, splom, candlestick, ohlc, waterfall, funnel)
  with plotly.js version 4.3.0.
metadata:
  tags:
    - visualization
    - charts
    - javascript
---

# plotly-js 4.3.0

## Overview

Plotly.js is a standalone JavaScript data visualization library that produces dozens of chart types — statistical charts, 3D graphs, scientific charts, SVG and tile maps, financial charts — rendered as interactive SVG and WebGL inside a DOM element. It powers the `plotly` Python and R modules (Plotly.py, Plotly.R) and is released under the MIT license.

A figure is a plain JSON-like object with `data` (array of trace objects), `layout` (axes, title, margins, colors), `config` (display options, locale), and optional `frames` (animation). Methods that act on a plot take the graph div (`gd`) — an element id or DOM element — as the first argument and return a Promise.

Version 4.3.0 (2026-11-10) added `domainpad` to cartesian axes to reserve pixel space inside the axis `domain` edges, and fixed `Plotly.react`/`Plotly.relayout` ignoring a new range on axes with `constrain: 'domain'`.

## Usage

### Load it

CDN — the script tag exposes a global `Plotly`. Always pin an exact version for v2 and higher:

```html
<script src="https://cdn.plot.ly/plotly-4.3.0.min.js" charset="utf-8"></script>
```

npm — install a ready-made dist bundle (minified or unminified):

```sh
npm i --save plotly.js-dist-min
```

```js
import Plotly from 'plotly.js-dist-min'    // ES6
var Plotly = require('plotly.js-dist-min') // CommonJS
```

### Create a plot

`Plotly.newPlot(gd, data, layout, config)`. The second argument can also be a whole figure object `{data, layout, config, frames}`:

```js
Plotly.newPlot("gd", {
    data: [{ y: [1, 2, 3] }],
    layout: { width: 600, height: 400 }
})
```

To update an existing plot, use `Plotly.react(gd, data, layout, config)`, which diffs old and new data/layout; `newPlot` purges the div and plots from scratch. Attribute-level edits go through `restyle` (traces) and `relayout` (layout).

### MathJax and multiple WebGL graphs

MathJax v3/v4 support is built in but not bundled — load a MathJax script separately, then any text wrapped in `$...$` in plot titles, axis labels, tick labels, and annotations is typeset. For several WebGL graphs on one page, load the `virtual-webgl` script (WebGL 1 only) before other scripts.

### Locales

The default locale is `en-US` (`en` is included in the standard bundle). To add e.g. Swiss German:

```html
<script src="plotly-locale-de-ch.js"></script>
<script>Plotly.setPlotConfig({locale: 'de-CH'})</script>
```

Locale file names are lowercase even when the locale string uses uppercase regions. A locale can also be passed per plot as a `config` parameter, `Plotly.newPlot(gd, data, layout, {locale: 'de-CH'})`.

## Gotchas

- **Pin an exact CDN version** — `plotly-latest` CDN URLs stopped updating at v1.58.5, so v2+ must use exact-version URLs like `plotly-4.3.0.min.js`.
- **Unminified bundles need `charset="utf-8"`** — non-minified source files may contain characters outside UTF-8.
- **`newPlot` is not an update** — it purges the graph div and re-plots. Use `Plotly.react` for in-place figure updates, `restyle`/`relayout` for attribute edits.
- **`scatter` is in every bundle** — it cannot be removed from a custom bundle; include it explicitly anyway because that behavior may change upstream.
- **MathJax is not bundled** — without a separate MathJax script tag, `$...$` text renders literally.
- **Custom bundles need Node 22** — plotly.js 4.0+ requires Node 22 / npm 10 to build a custom bundle from source.
- **The strict bundle is ~10% larger** — regl-based traces are built without function constructors for strict CSP; it now contains all traces.
- **Attribute docs live outside the repo** — the official reference (https://plotly.com/javascript) is generated from the separate `graphing-library-docs` repo, not from the plotly.js repository itself.

## References

- [01-api](references/01-api.md) — full public API (methods, signatures) and emitted events
- [02-bundles](references/02-bundles.md) — full and partial bundle sizes, CDN URLs, npm packages, custom bundle workflow
- [03-trace-types](references/03-trace-types.md) — all 47 trace types and which partial bundles contain them

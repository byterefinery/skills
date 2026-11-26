---
name: chart-js-4-6-2
description: >
  Chart.js 4.6.2 is a JavaScript charting library that renders responsive, animated charts on HTML5
  canvas. Use this skill whenever the user mentions Chart.js, chartjs, canvas charts, line charts, bar
  charts, scatter charts, bubble charts, pie charts, doughnut charts, radar charts, polar area charts,
  mixed charts, chart.js configuration, chart.js plugins, chart.js scales, chart.js axes, chart.js
  tooltips, chart.js legends, or any chart visualization built with the Chart.js API (v4.6.2). Also use
  when the user asks about Chart.js installation, CDN loading, npm integration, bundlers (Webpack, Vite,
  Rollup), or embedding Chart.js charts in web apps.
license: MIT
metadata:
  tags:
    - visualization
    - charts
    - data-graphics
    - javascript
---

# chart-js 4.6.2

## Overview

Chart.js 4.6.2 is a JavaScript library that renders interactive charts on HTML5 <canvas>. Charts are instantiated with `new Chart(ctx, config)` where `ctx` is a canvas element or its 2D context, and `config` specifies `type`, `data`, `options`, and `plugins`. The library supports 8 chart types (line, bar, scatter, bubble, pie, doughnut, radar, polarArea), multiple scale types, built-in plugins (legend, title, subtitle, tooltip, filler, decimation), and a plugin API for extensions.

Chart.js 4.6.2 is an ESM-only npm package (`"type": "module"`), MIT licensed, and tree-shakeable. UMD builds (`dist/chart.umd.min.js`) remain available for script tags and CDNs.

### Core API

| Method | Purpose |
|---|---|
| `new Chart(ctx, config)` | Create a chart instance (throws if canvas is already in use) |
| `chart.destroy()` | Destroy chart, free resources; required before reusing the canvas |
| `chart.update(mode?)` | Update data/options; `mode` selects a transition (`'none'` skips animation) |
| `chart.reset()` | Reset to state before initial animation |
| `chart.render()` | Redraw all elements (does not recompute for new data) |
| `chart.stop()` | Stop the running animation loop |
| `chart.resize(width?, height?)` | Manually resize (no args = fit container) |
| `chart.clear()` | Clear the canvas |
| `chart.toBase64Image(type?, quality?)` | Export current canvas as data URL (png by default) |
| `chart.getElementsAtEventForMode(e, mode, options, useFinalPosition)` | Elements hit by an event under a given mode |
| `chart.getDatasetMeta(index)` | Dataset metadata (positions of points/bars/arcs) |
| `chart.isDatasetVisible(i)` / `chart.setDatasetVisibility(i, v)` | Query/set dataset visibility |
| `chart.hide(datasetIndex, dataIndex?)` / `chart.show(datasetIndex, dataIndex?)` | Hide/show a dataset or one data item, animated |
| `chart.toggleDataVisibility(index)` | Toggle one index in all datasets (doughnut/pie, polar area, bar) |
| `chart.setActiveElements(elements)` | Programmatically set hovered elements |
| `chart.isPluginEnabled(pluginId)` | Check plugin registration |
| `Chart.getChart(key)` | Static: look up instance by canvas id, context, or DOM element |
| `Chart.register(...components)` | Static: register controllers, elements, scales, plugins |

## Usage

Install (npm) or load the UMD build from a CDN / script tag:

```sh
npm install chart.js
```

Minimal chart (pattern from the official step-by-step guide):

```html
<div style="width: 800px;"><canvas id="acquisitions"></canvas></div>
```

```js
import Chart from 'chart.js/auto';

new Chart(document.getElementById('acquisitions'), {
  type: 'bar',
  data: {
    labels: ['2010', '2011', '2012', '2013'],
    datasets: [{
      label: 'Acquisitions by year',
      data: [10, 20, 15, 25]
    }]
  }
});
```

With bundlers, `chart.js/auto` registers everything (convenient, no tree-shaking). For production, import only the components you use from `chart.js` and `Chart.register(...)` them — the per-chart-type minimums are listed in [01-getting-started](references/01-getting-started.md).

Updating data:

```js
chart.data.datasets[0].data[0] = 42;
chart.update();          // animates to the new value
chart.update('none');    // same, without animation
```

## Gotchas

- **Wrap each canvas in a dedicated, relatively-positioned container** — Chart.js sizes the canvas from its parent element. Setting `width`/`height` attributes or CSS sizes on the canvas itself does not work (invalid or blurry, or the canvas keeps shrinking). Use `<div style="position: relative; ...">` containing only the canvas.
- **`chart.js/auto` disables tree-shaking** — it registers every controller, element, scale, and plugin. A single `import ... from 'chart.js/auto'` in production kills bundler dead-code elimination.
- **ESM-only package** — CommonJS code must use dynamic `const { Chart } = await import('chart.js')`; RequireJS can only load the UMD builds.
- **One chart per canvas** — the constructor throws if the canvas/context is already in use. Call `chart.destroy()` before reusing a canvas.
- **There is no `horizontalBar` type** — horizontal bars are `type: 'bar'` with `indexAxis: 'y'` (works for line charts too).
- **Time scales require a date adapter** — moment is no longer an npm dependency of chart.js; install an adapter (e.g. from the chartjs/awesome list) and load it after Chart.js.
- **Mixed charts** — set `type` per dataset. Default options are only considered at the dataset level, not merged at the chart level. `order` is a weight: higher values are drawn sooner, i.e. *behind* lower ones.
- **Angles are degrees, 0 at top** — doughnut `rotation` (default 0) and `circumference` (default 360); polar area `startAngle` default 0.
- **`cutout`, not `cutoutPercentage`** — accepts pixels (number) or percent (string ending `%`); pie default `'0'`, doughnut default `'50%'`.
- **Indexable options loop** — `backgroundColor: ['red', 'green']` alternates red/green across all points forever; it does not stop at the array end.
- **Radar charts with object data still need a `labels` array** for the chart to display correctly.
- **Doughnut/pie/polarArea override legend defaults** — change type-specific legend defaults via `Chart.overrides[type].plugins.legend`, not `Chart.defaults.plugins.legend`.
- **Disable animation** with `options.animation = false` (all), `options.animations.<name> = false` (one collection), `duration: 0` (one transition), or `update('none')` (one update).
- **The `destroy` plugin hook is gone in v4** — use `afterDestroy`.
- **v4 scale border renames** — `scales[id].grid.drawBorder/borderWidth/borderColor/borderDash/borderDashOffset` are now `scales[id].border.display/width/color/dash/dashOffset`.
- **Legacy `xAxes`/`yAxes` keys do not override the default axis** in v4 — they create a second scale. Configure axes under `options.scales` keyed by scale id (`x`, `y`, custom ids).

## References

- [01-getting-started](references/01-getting-started.md) — installation (npm, CDN, GitHub), bundler integration, tree-shaking component minimums, CommonJS/RequireJS, Node.js
- [02-data-structures](references/02-data-structures.md) — data formats, parsing options, dataset properties, TypeScript
- [03-chart-types](references/03-chart-types.md) — all 8 chart types, mixed charts, area fill modes
- [04-configuration](references/04-configuration.md) — config structure, option resolution, scriptable/indexable options, responsive sizing, canvas background, decimation
- [05-axes-scales](references/05-axes-scales.md) — scale types (category, linear, logarithmic, time, radial), common options, ticks, range settings
- [06-plugins](references/06-plugins.md) — plugin API and hooks, built-in plugins (legend, title, subtitle, tooltip)
- [07-interactions](references/07-interactions.md) — interaction modes, events, converting events to data values
- [08-animations](references/08-animations.md) — animation configuration, transitions, easing functions, disabling
- [09-updating-api](references/09-updating-api.md) — full instance and static API, updating data/options/scales
- [10-migration](references/10-migration.md) — v3 to v4 breaking changes (option renames, ESM-only, dist file names)

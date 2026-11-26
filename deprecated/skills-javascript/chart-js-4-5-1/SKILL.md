---
name: chart-js-4-5-1
description: >
  Chart.js is a JavaScript charting library for designers and developers, providing responsive, animated charts
  rendered on HTML5 canvas. Use this skill whenever the user mentions Chart.js, chartjs, canvas charts, bar charts,
  line charts, scatter charts, bubble charts, pie charts, doughnut charts, radar charts, polar area charts, mixed
  charts, chart.js configuration, chart.js plugins, chart.js scales, chart.js axes, chart.js tooltips, chart.js
  legends, or any chart visualization built with the Chart.js API (v4.5.1). Also use when the user asks about
  Chart.js installation, CDN loading, npm integration, bundlers (Webpack, Vite, Rollup), or embedding chart.js
  charts in web apps.
metadata:
  tags:
    - visualization
    - charts
    - data-graphics
    - javascript
---

# chart-js 4.5.1

## Overview

Chart.js is a JavaScript library that renders interactive charts on HTML5 `<canvas>`. Charts are instantiated with `new Chart(ctx, config)` where `ctx` is a canvas element or its 2D context, and `config` specifies type, data, options, and plugins. The library supports 8 chart types, multiple scale types, built-in plugins (legend, tooltip, title), and a plugin API for extensions.

Chart.js v4.5.1 is an ES module by default (`"type": "module"` in package.json), with a CommonJS fallback. It requires a modern browser or Node.js with canvas support. It is licensed under MIT and maintained by the Chart.js community.

### Core API

| Method / Property | Purpose |
|---|---|
| `new Chart(ctx, config)` | Create a chart instance |
| `chart.destroy()` | Destroy chart, free resources |
| `chart.update()` | Re-render chart with updated data/options |
| `chart.resize(width, height)` | Manually resize chart |
| `chart.toBase64Image(type, quality)` | Export chart as base64 data URL |
| `chart.stop()` | Stop running animations |
| `chart.render()` | Force re-render |
| `chart.ensureScalesHaveIDs()` | Ensure all scales have IDs |
| `chart.buildUpdateModes()` | Build update mode handlers |
| `chart.isPointInArea(point)` | Check if point is in chart area |
| `chart.getDatasetMeta(index)` | Get metadata for a dataset |
| `chart.getSortedVisibleDatasetMetas()` | Get sorted visible dataset metas |
| `chart.getElementsAtEventForMode(event, mode, options, useFinal)` | Get elements at event |
| `Chart.register(...items)` | Register plugins, scales, controllers globally |
| `Chart.unregister(...items)` | Unregister items globally |
| `Chart.helpers` | Access helper utilities (`helpers.color`, `helpers.each`, etc.) |
| `Chart.defaults` | Global default configuration object |
| `Chart.overrides` | Per-type default overrides |
| `Chart.instances` | Map of all chart instances by canvas ID |

### Configuration Object

```javascript
const config = {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Sales',
      data: [10, 20, 30],
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'top' },
      tooltip: { enabled: true, mode: 'index' }
    },
    scales: {
      x: { type: 'category' },
      y: { beginAtZero: true }
    }
  },
  plugins: [/* inline plugin objects */]
};

const chart = new Chart(ctx, config);
```

### Chart Types

| Type | Description | Data Format |
|---|---|---|
| `line` | Line chart with optional fill, tension, stepped lines | `number[]`, `[{x, y}]`, `[x, y]` |
| `bar` | Vertical or horizontal bars, grouped or stacked | `number[]`, `[{x, y}]` |
| `scatter` | Scatter plot (line variant with linear x-axis, `showLine: false`) | `[{x, y}]` only |
| `bubble` | Bubble chart with radius as third dimension | `[{x, y, r}]` |
| `pie` | Pie chart (`cutout: 0`) | `number[]` |
| `doughnut` | Doughnut chart (`cutout: '50%'` default) | `number[]` |
| `radar` | Radar/spider chart with radial axis | `number[]` |
| `polarArea` | Polar area chart (radial bars) | `number[]` |

### Scale Types

| Cartesian | Radial |
|---|---|
| `category` — discrete labels from `data.labels` | `radialLinear` — used by radar and polarArea |
| `linear` — continuous numeric axis | |
| `time` — dates/timestamps (requires date adapter) | |
| `logarithmic` — log-scale numeric axis | |

### Built-in Plugins

| Plugin ID | Namespace | Purpose |
|---|---|---|
| `legend` | `options.plugins.legend` | Dataset legend with labels, position, click/hover callbacks |
| `tooltip` | `options.plugins.tooltip` | Hover tooltips with title, body, footer, custom callbacks |
| `title` | `options.plugins.title` | Chart title text |
| `decimation` | `options.plugins.decimation` | Reduce data points for performance (min-max, lttb, etc.) |
| `faker` | — | Dev-only: generates random data |

## Usage

### Installation

**npm:**

```bash
npm install chart.js
```

```javascript
import { Chart } from 'chart.js';
```

**CDN (script tag):**

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>
<script>
  const { Chart } = window;
  new Chart(ctx, config);
</script>
```

**ES module (script tag):**

```html
<script type="module">
  import { Chart } from 'https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.esm.js';
  new Chart(ctx, config);
</script>
```

### Basic Bar Chart

```html
<div style="position: relative; height: 400px; width: 100%">
  <canvas id="myChart"></canvas>
</div>
```

```javascript
import { Chart } from 'chart.js';

new Chart(document.getElementById('myChart'), {
  type: 'bar',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
    datasets: [{
      label: '# of Votes',
      data: [12, 19, 3, 5, 2, 3],
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgb(54, 162, 235)',
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: { beginAtZero: true }
    }
  }
});
```

### Line Chart with Multiple Datasets

```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [
      {
        label: 'Revenue',
        data: [100, 150, 200, 180, 220],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      },
      {
        label: 'Cost',
        data: [80, 120, 140, 160, 130],
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1
      }
    ]
  },
  options: {
    interaction: { mode: 'index', intersect: false },
    plugins: {
      tooltip: { mode: 'index', intersect: false }
    }
  }
});
```

### Mixed Chart (bar + line)

Specify `type` per dataset to mix chart types:

```javascript
new Chart(ctx, {
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr'],
    datasets: [
      {
        type: 'bar',
        label: 'Sales',
        data: [10, 20, 30, 40]
      },
      {
        type: 'line',
        label: 'Target',
        data: [50, 50, 50, 50],
        borderColor: 'rgb(54, 162, 235)',
        fill: false
      }
    ]
  }
});
```

### Scatter Chart

```javascript
new Chart(ctx, {
  type: 'scatter',
  data: {
    datasets: [{
      label: 'Scatter Dataset',
      data: [{ x: -10, y: 0 }, { x: 0, y: 10 }, { x: 10, y: 5 }]
    }]
  },
  options: {
    scales: {
      x: { type: 'linear', position: 'bottom' }
    }
  }
});
```

### Doughnut Chart

```javascript
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Red', 'Blue', 'Yellow'],
    datasets: [{
      data: [300, 50, 100],
      backgroundColor: ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)']
    }]
  }
});
```

### Updating Data

```javascript
// Update a single dataset
chart.data.datasets[0].data = [1, 2, 3, 4, 5];
chart.update();

// Update with animation mode
chart.update('default');  // 'default', 'active', 'hide', 'show', 'resize', 'none'

// Add a dataset
chart.data.datasets.push({ label: 'New', data: [5, 6, 7] });
chart.update();

// Remove a dataset
chart.data.datasets.splice(0, 1);
chart.update();
```

### Global Defaults

```javascript
import { Chart } from 'chart.js';

// Set defaults for all charts
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.color = '#666';
Chart.defaults.plugins.legend.position = 'bottom';

// Set defaults for a specific chart type
Chart.overrides.line.tension = 0.3;
Chart.overrides.line.showLine = true;
```

### Time Scale

The time scale requires a date adapter. Register one before creating charts:

```javascript
import { Chart, registerables } from 'chart.js';
import { DateAdapter } from 'chartjs-adapter-date-fns';

Chart.register(DateAdapter, ...registerables);

new Chart(ctx, {
  type: 'line',
  data: {
    datasets: [{
      data: [
        { x: '2024/01/01', y: 10 },
        { x: '2024/02/01', y: 20 },
        { x: '2024/03/01', y: 15 }
      ]
    }]
  },
  options: {
    scales: {
      x: {
        type: 'time',
        time: { unit: 'month' }
      }
    }
  }
});
```

Popular date adapters: `chartjs-adapter-date-fns`, `chartjs-adapter-luxon`, `chartjs-adapter-moment`.

### Custom Plugin

```javascript
const watermarkPlugin = {
  id: 'watermark',
  afterDraw(chart) {
    const { ctx, chartArea } = chart;
    ctx.save();
    ctx.font = '20px sans-serif';
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.textAlign = 'center';
    ctx.fillText('CONFIDENTIAL', chartArea.width / 2 + chartArea.left, chartArea.height / 2 + chartArea.top);
    ctx.restore();
  }
};

new Chart(ctx, {
  type: 'bar',
  data: { /* ... */ },
  plugins: [watermarkPlugin]
});
```

### Registering Globally

```javascript
import { Chart, BarController, BarElement, CategoryScale, LinearScale } from 'chart.js';

// Register only what you need (tree-shakeable)
Chart.register(BarController, BarElement, CategoryScale, LinearScale);

// Or register all built-in components
import { registerables } from 'chart.js';
Chart.register(...registerables);
```

## Gotchas

- **Canvas needs a positioned parent container for responsiveness** — Chart.js detects resize from the parent element. The container must have `position: relative` and explicit dimensions. Without it, `responsive: true` silently fails or produces blurry charts.

```html
<div style="position: relative; height: 400px; width: 100%">
  <canvas id="myChart"></canvas>
</div>
```

- **`<canvas width="80vw" height="40vh">` does not work** — canvas `width`/`height` attributes accept only integers. Use CSS `style` on the parent container instead.

- **`chart.update()` is required after changing data** — modifying `chart.data.datasets[0].data` does not trigger a re-render. Always call `chart.update()` after data changes.

- **`new Chart()` on the same canvas twice leaks memory** — destroy the old chart first with `chart.destroy()` or check `Chart.instances[canvasId]` before creating a new one.

- **`responsive: true` + `maintainAspectRatio: true` ignores explicit height** — if the canvas has an explicit `height` attribute or inline `style.height`, aspect ratio is maintained based on that. Set `maintainAspectRatio: false` for full control.

- **Time scale needs a date adapter** — Chart.js v4 does not ship with a date adapter. Install `chartjs-adapter-date-fns` (or luxon/moment) and register it before creating time-scale charts.

- **`tension` controls line smoothness** — `0` = straight lines, `0.4` = smooth curves. This is a dataset-level option, not a global option. Default is `0`.

- **`fill` on line datasets** — `true` fills to the x-axis, `false` fills nothing, `'origin'` fills to origin, `'end'` fills to the last data point, or use a dataset index like `'-1'` to fill to another dataset.

- **Scatter chart requires `{x, y}` objects** — unlike line charts that accept `number[]`, scatter charts only accept `[{x, y}]` data format. The x-axis is automatically `linear`.

- **`indexAxis: 'y'` flips bar charts horizontal** — set on the dataset to make horizontal bar charts. The default is `'x'` (vertical bars).

- **Legend defaults differ for pie/doughnut/polarArea** — these chart types override legend defaults. To change them, use `Chart.overrides.doughnut.plugins.legend` rather than `Chart.defaults.plugins.legend`.

- **`beginAtZero` forces scale to include 0** — without it, the scale auto-ranges to the data. Set `scales.y.beginAtZero = true` to prevent misleading visual comparisons.

- **Plugin `id` must be unique** — each plugin needs a unique `id` string. Reusing an ID causes conflicts. Follow npm package naming conventions (lowercase, no dots/underscores at start).

- **`Chart.register()` is required for individual imports** — when importing specific components (e.g., `BarController`, `LinearScale`), register them explicitly. Using `registerables` imports everything but loses tree-shaking benefits.

- **`stacked: true` on scales, not datasets** — to stack bars, set `scales.y.stacked = true`. The `stack` property on datasets groups them into separate stacks.

- **`onResize` callback receives chart instance and new size** — use it for custom resize logic. The signature is `onResize(chart, size)` where `size` is `{width, height}`.

- **`decimation` plugin activates automatically** — when a dataset has more than 1000 points and the chart width exceeds a threshold, the decimation plugin kicks in. Configure via `options.plugins.decimation` or disable with `options.plugins.decimation: false`.

- **`parsing: false` for performance** — when data is already in the correct format, disable parsing to speed up rendering: `options.parsing = false`. Data must be sorted and in the scale's internal format.

- **`spanGaps` connects lines across null values** — set `spanGaps: true` on a line dataset to draw lines through `null` data points. Default is `false` (gaps shown).

- **`borderRadius` on bars** — set `borderRadius` on bar datasets for rounded corners. Accepts a number (all corners) or an object `{topLeft, topRight, bottomLeft, bottomRight}`.

- **`Chart.helpers` utilities** — access helpers like `helpers.color()`, `helpers.each()`, `helpers.clone()`, `helpers.merge()`, `helpers.isArray()`, `helpers.isObject()`, `helpers.callback()`. Useful in plugins and custom logic.

## References

- [01-chart-types.md](references/01-chart-types.md) — Line, bar, scatter, bubble, pie, doughnut, radar, polarArea — dataset properties and options
- [02-scales.md](references/02-scales.md) — Category, linear, time, logarithmic, radialLinear — axis configuration, ticks, grid, labels
- [03-plugins.md](references/03-plugins.md) — Legend, tooltip, title, decimation — built-in plugin options and custom plugin lifecycle
- [04-interactions.md](references/04-interactions.md) — Interaction modes, events, hover, click callbacks, onHover, onClick
- [05-data-structures.md](references/05-data-structures.md) — Primitive[], Array[], Object[], custom parsing, null handling, spanGaps
- [06-responsive.md](references/06-responsive.md) — Responsive layout, container requirements, maintainAspectRatio, aspectRatio, onResize, resizeDelay
- [07-animations.md](references/07-animations.md) — Animation config, transitions, property animations, duration, easing, loop
- [08-styling.md](references/08-styling.md) — Colors, fonts, borders, point styles, segment options, scriptable/indexable options
- [09-mixed-charts.md](references/09-mixed-charts.md) — Mixed chart types, drawing order, dataset-level type override
- [10-exporting.md](references/10-exporting.md) — toBase64Image, canvas export, printing, PDF generation
- [11-developers.md](references/11-developers.md) — Custom controllers, custom scales, custom elements, plugin hooks, extending built-in types

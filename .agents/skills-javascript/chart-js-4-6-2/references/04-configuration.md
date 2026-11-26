# Configuration

Top-level configuration object:

```js
const config = {
  type: 'line',     // main chart type; a dataset can override it (mixed charts)
  data: {},         // see data structures
  options: {},      // all customization
  plugins: []       // inline plugins for this chart only
};
```

## Global Configuration

Global defaults: `Chart.defaults` (all chart types) and `Chart.overrides.<type>` (per chart type). Chart.js merges instance options over the global configuration using chart type defaults and scale defaults.

```js
Chart.defaults.interaction.mode = 'nearest';
```

Type-specific defaults, e.g. disable line showLine globally:

```js
Chart.defaults.datasets.line.showLine = false;
```

## Option Resolution

Options are resolved top to bottom.

- Chart level: options → overrides[type] → defaults
- Dataset level: dataset → options.datasets[dataset.type] → options → overrides[type].datasets[type] → defaults.datasets[type] → defaults
- Dataset element level (prefix lookup, e.g. `pointRadius` then `radius`): dataset → options.datasets[type] → options.datasets[type].elements[elementType] → options.elements[elementType] → options → overrides chain → defaults chain
- Scale options: options.scales → overrides[type].scales → defaults.scales → defaults.scale
- Plugin options: options.plugins[plugin.id] → (additionalOptionScopes) → overrides[type].plugins[id] → defaults.plugins[id]

## Scriptable Options

Scriptable options accept a function called per data value with a context argument (and an option resolver as second parameter):

```js
color: function(context) {
  const index = context.dataIndex;
  const value = context.dataset.data[index];
  return value < 0 ? 'red' : index % 2 ? 'blue' : 'green';
}
```

Validate `context.type` inside scriptable functions — they are invoked in different contexts.

Context levels and properties: `chart` (chart, type), `dataset` (active, dataset, datasetIndex, index, mode), `data` (dataIndex, parsed, raw, element, index), `scale` (scale), `tick` (tick, index), `pointLabel` (label, index), `tooltip` (tooltip, tooltipItems). Child levels inherit parent context.

## Indexable Options

Indexable options accept an array mapped to elements by index; if there are fewer items than data, the items are **looped** (they cycle over).

## Responsive Charts

Namespace `options`:

| Name | Default | Description |
|---|---|---|
| `responsive` | true | Resize the canvas when its container does |
| `maintainAspectRatio` | true | Keep the canvas width/height ratio when resizing |
| `aspectRatio` | 1 (radial: doughnut, pie, polarArea, radar) or 2 (others) | width / height; ignored if height is explicitly defined |
| `onResize` | null | Called on resize with (chart, newSize) |
| `resizeDelay` | 0 | Debounce resize updates by N ms |

Canvas render size cannot use relative values, and display size does not drive render size automatically — Chart.js works around this using the parent container. Requirements: the container must be **relatively positioned and dedicated to this canvas only**.

```html
<div class="chart-container" style="position: relative; height:40vh; width:80vw">
  <canvas id="chart"></canvas>
</div>
```

Programmatic resize: change the container's style (canvas.parentNode.style.width/height). To change height programmatically, `maintainAspectRatio` must be false. In flexbox/grid layouts set the flex/grid child to `min-width: 0` to avoid overflow issues.

## Canvas Background

There is no built-in whole-canvas background; use CSS for normal use, or a custom plugin when the background must be exported with the chart (color or image, drawn in `beforeDraw` with `ctx.globalCompositeOperation = 'destination-over'`).

```js
const plugin = {
  id: 'customCanvasBackgroundColor',
  beforeDraw: (chart, args, options) => {
    const { ctx } = chart;
    ctx.save();
    ctx.globalCompositeOperation = 'destination-over';
    ctx.fillStyle = options.color || '#99ffff';
    ctx.fillRect(0, 0, chart.width, chart.height);
    ctx.restore();
  }
};
// config: plugins: [plugin], options.plugins.customCanvasBackgroundColor: { color: 'lightGreen' }
```

## Data Decimation

The Decimation plugin (line charts only) automatically reduces data at the start of the chart lifecycle. Namespace `options.plugins.decimation`:

| Name | Default | Description |
|---|---|---|
| `enabled` | false | Enable the plugin |
| `algorithm` | 'min-max' | 'lttb' or 'min-max' |
| `samples` | canvas width (1 sample/px) | Output sample count for 'lttb' |
| `threshold` | 4x canvas width | Min point count before decimation triggers |

Algorithms: `'lttb'` (Largest-Triangle-Three-Buckets — strong reduction, trend-preserving) and `'min-max'` (peak-preserving, up to 4 points per pixel).

Requirements: dataset indexAxis must be `'x'`; dataset must be a line; x scale must be linear or time; parsing must be `false`; the dataset object must be mutable (original data stored as `dataset._data`); more points than the threshold must exist.

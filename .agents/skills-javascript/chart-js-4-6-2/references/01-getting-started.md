# Getting Started (installation, integration, Node.js)

## Installation

npm:

```sh
npm install chart.js
```

CDN — built files are on CDNJS (https://cdnjs.com/libraries/Chart.js) and jsDelivr (https://www.jsdelivr.com/package/npm/chart.js?path=dist), path `/dist`.

GitHub — you can download or clone the repository, but you must build Chart.js to generate the dist files. Chart.js no longer ships prebuilt release versions with the repo, so downloading the repo is not recommended for end users.

## Integration

### Script tag

```html
<script src="path/to/chartjs/dist/chart.umd.min.js"></script>
<script>
    const myChart = new Chart(ctx, {...});
</script>
```

### Bundlers (Webpack, Rollup, Vite, Parcel, ...)

Chart.js is tree-shakeable: import and register only the components you use. If bundle size does not matter, use the `auto` path:

```js
import Chart from 'chart.js/auto';
```

To optimize the bundle, register components explicitly:

```js
import { Chart, Colors, BarController, CategoryScale, LinearScale, BarElement, Legend } from 'chart.js';

Chart.register(Colors, BarController, BarElement, CategoryScale, LinearScale, Legend);
```

Minimum components per chart type:

| Chart | Controllers / elements | Default scales |
|---|---|---|
| bar | BarController, BarElement | CategoryScale (x), LinearScale (y) |
| bubble | BubbleController, PointElement | LinearScale (x/y) |
| doughnut | DoughnutController, ArcElement | none |
| line | LineController, LineElement, PointElement | CategoryScale (x), LinearScale (y) |
| pie | PieController, ArcElement | none |
| polarArea | PolarAreaController, ArcElement | RadialLinearScale (r) |
| radar | RadarController, LineElement, PointElement | RadialLinearScale (r) |
| scatter | ScatterController, PointElement | LinearScale (x/y) |

Available plugins (import from `chart.js` and register): Decimation, Filler (fills areas described by LineElement), Legend, SubTitle, Title, Tooltip.

Available scales: Cartesian — CategoryScale, LinearScale, LogarithmicScale, TimeScale, TimeSeriesScale. Radial — RadialLinearScale.

If a controller is missing the browser console reports e.g. `"bar" is not a registered controller.`

Helper functions come from a separate entry point:

```js
import { getRelativePosition } from 'chart.js/helpers';
const canvasPosition = getRelativePosition(event, chart);
```

### CommonJS

Chart.js is an ESM library; in CommonJS modules use a dynamic import:

```js
const { Chart } = await import('chart.js');
```

### RequireJS

RequireJS loads AMD modules only, so require one of the UMD builds (`dist/chart.umd.min.js`):

```js
require(['path/to/chartjs/dist/chart.umd.min.js'], function(Chart){
    const myChart = new Chart(ctx, {...});
});
```

The time scale additionally needs a date adapter and its date library fully loaded **after** Chart.js (nested `require` calls).

## Using from Node.js

Server-side rendering works with a canvas implementation such as node-canvas or skia-canvas (doc example, abbreviated):

```js
import { CategoryScale, Chart, LinearScale, LineController, LineElement, PointElement } from 'chart.js';
import { Canvas } from 'skia-canvas';

Chart.register(CategoryScale, LineController, LineElement, LinearScale, PointElement);

const canvas = new Canvas(400, 300);
const chart = new Chart(canvas, {
  type: 'line',
  data: {
    labels: ['Red', 'Blue', 'Yellow'],
    datasets: [{ label: '# of Votes', data: [12, 19, 3], borderColor: 'red' }]
  }
});
const pngBuffer = await canvas.toBuffer('png', { matte: 'white' });
// await fsp.writeFile('output.png', pngBuffer);
chart.destroy();
```

## Live samples

The documentation ships runnable samples (the repo path `docs/samples/<category>/<name>.md` maps to https://www.chartjs.org/samples/<category>/<name>.html). Categories: advanced, animations, area, bar, legend, line, other-charts, plugins, scale-options, scales, scriptable, subtitle, title, tooltip.

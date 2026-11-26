# Data Structures

The `data` property of a dataset can be passed in several formats. By default it is parsed using the associated chart type and scales. If `data.labels` is used it must contain the same number of elements as the dataset with the most values; labels label the index axis (default `x`). Label values must be string or number; a label can be an array of strings for multiline rendering.

## Formats

### Primitive[] (numbers with labels)

```js
const cfg = {
  type: 'bar',
  data: {
    datasets: [{ data: [20, 10] }],
    labels: ['a', 'b']
  }
}
```

Values from `labels` at the same index are used for the index axis (`x` for vertical, `y` for horizontal charts).

### Array[] (tuples)

```js
data: [[10, 20], [15, null], [20, 10]]
```

First tuple element = index, second = value.

### Object[] ({x, y} — the internal format)

```js
data: [{x: 10, y: 20}, {x: 15, y: null}, {x: 20, y: 10}]
// string dates work for time scales
data: [{x: '2016-12-25', y: 20}, {x: '2016-12-26', y: 10}]
```

This is the internal format used for parsed data. With `parsing: false` (chart options or dataset) parsing is disabled and the data must already be sorted and in the internal format of the chart type and scales. `null` is a skipped value.

### Object[] using custom properties

Map arbitrary object fields with `parsing` keys:

```js
data: [{id: 'Sales', nested: {value: 1500}}],
options: {
  parsing: { xAxisKey: 'id', yAxisKey: 'nested.value' }
}
```

For pie/doughnut, radar and polarArea the `parsing` object uses a single `key` pointing at the value field. Keys containing dots must be escaped with a double backslash: `xAxisKey: 'data\\.key'`.

Radar charts with object data still need a `labels` array to display correctly.

### Object (single map)

```js
data: { January: 10, February: 20 }
```

Property name → index scale, value → value scale.

## Dataset Configuration

| Name | Type | Description |
|---|---|---|
| `label` | `string` | Label shown in legend and tooltips |
| `clip` | `number` or object | Clip relative to chartArea; positive allows overflow, negative clips inside; `0` = clip at chartArea; per side via `{left, top, right, bottom}` |
| `order` | `number` | Drawing order; also affects stacking, tooltip and legend order |
| `stack` | `string` | Stack group id (defaults to dataset `type`) |
| `parsing` | `boolean` or object | How to parse the dataset; `false` disables parsing |
| `hidden` | `boolean` | Initial visibility of the dataset |

TypeScript: pass the custom data shape to `ChartData` when instantiating:

```ts
import { ChartData } from 'chart.js';

const datasets: ChartData<'bar', {key: string, value: number}[]> = {
  datasets: [{
    data: [{key: 'Sales', value: 20}, {key: 'Revenue', value: 10}],
    parsing: { xAxisKey: 'key', yAxisKey: 'value' }
  }]
};
```

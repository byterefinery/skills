# Chart Types

Type strings: `line`, `bar`, `scatter`, `bubble`, `pie`, `doughnut`, `radar`, `polarArea`. A dataset can override the chart `type` (mixed charts, see below). Global per-type defaults live in `Chart.overrides.<type>`; changing them only affects charts created afterwards.

Contents: line, bar, scatter, bubble, pie/doughnut, radar, polarArea, mixed, area (fill).

## Line

Trend data; internal data format `{x, y}`. All data structures supported. Key dataset properties (defaults in parentheses where noted):

- `borderColor`, `backgroundColor`, `borderWidth` (3), `borderCapStyle`, `borderJoinStyle`, `borderDash`, `borderDashOffset`
- `tension` (0) — Bezier curve tension; 0 draws straight lines; ignored with monotone interpolation
- `cubicInterpolationMode` — `'default'` (weighted cubic) or `'monotone'` (preserves monotonicity, extrema stay at input points)
- `showLine` (true) — `false` plots points only
- `spanGaps` — boolean or number (max gap length, scale units); connects across null/missing data
- `stepped` — `false` (default), `true`/`'before'`, `'after'`, `'middle'`; non-false values ignore `tension`
- `fill` — see area (fill) below
- `pointRadius` (3), `pointHoverRadius` (4), `pointHitRadius` (1), `pointStyle`, `pointBackgroundColor`, `pointBorderColor`, `pointBorderWidth` (1), `pointRotation` (0), hover variants `pointHover*`
- `segment` — scriptable per-segment styles for all `border*` and `backgroundColor` options (context has `type: 'segment'`, `p0`, `p1`, `p0DataIndex`, `p1DataIndex`, `datasetIndex`); styling gaps requires `spanGaps`
- `indexAxis` — `'x'` (default, horizontal line) or `'y'` (vertical line chart; x-axis options then apply to y)
- `drawActiveElementsOnTop` (true), `clip`, `order`, `stack`, `xAxisID`, `yAxisID`

Stacked area chart: set `scales.y.stacked: true`.

## Bar

Internal data format numeric with labels; internal format `{x, y}`. Key dataset properties:

- `barPercentage` (0.9), `categoryPercentage` (0.8), `barThickness`, `maxBarThickness`, `minBarLength`
- `borderWidth` (0; number or per-side object), `borderRadius` (0; number or per-corner object), `borderSkipped` (`'start'`; values: start, end, middle, bottom, left, top, right, true, false)
- `grouped` (true) — false places each bar on its actual index value
- `base` — base value in data units along the value axis
- `inflateAmount` (`'auto'`), `skipNull` (null/undefined excluded from spacing calculations)
- `indexAxis` — `'x'` (default, vertical bars) or `'y'` (horizontal bars)
- `stack` — stack group id; stacked bar charts via `scales.y.stacked: true`

## Scatter

Line-based with a linear x-axis. Data must be point objects — scatter accepts only the `{x, y}` object format (no labels arrays). Supports all line chart properties but overrides `showLine` to `false` by default. Index scale type is `linear`, so labels (if used) must be numbers or parsable to numbers.

## Bubble

Three dimensions: `{x, y, r}` (r = radius). Key dataset properties: `radius` (3), `hitRadius` (1), `hoverRadius` (4), `borderWidth` (3), `rotation` (0), `pointStyle`, `backgroundColor`, `borderColor`, hover variants.

## Pie and Doughnut

Same class, two aliases; only defaults differ: `cutout` is `'0'` for pie, `'50%` for doughnut. Data: array of numbers plus a `labels` array (needed for legend/tooltips). Key dataset properties:

- `rotation` — degrees, 0 at top (default 0)
- `circumference` — degrees (default 360)
- `cutout` — pixels (number) or percent (string ending `%`)
- `hoverOffset` (0) — arc offset when hovered
- `offset` — number or per-arc number[], pushes arcs out from center
- `spacing` (0), `spacingMode` — doughnut default `'angular'` (also `'proportional'`, `'parallel'`)
- `weight` (1) — relative thickness of the dataset ring (multi-ring doughnuts)
- `borderWidth` (2), `borderColor` ('#fff'), `borderAlign` — `'center'` (default) or `'inner'` (no overlapping borders)
- `backgroundColor`, `borderDash`, `borderDashOffset`, `borderJoinStyle`, `borderRadius`, hover variants

## Radar

Multiple datasets over a single radial scale; data: array of numbers with a `labels` array (also required for object data). Scale options live under `scales.r`. Dataset properties mirror line (line + point styling, `fill`, `tension`, `spanGaps`). Example scale config:

```js
options: {
  scales: {
    r: {
      angleLines: { display: false },
      suggestedMin: 50,
      suggestedMax: 100
    }
  }
}
```

## Polar Area

Radial scale (`r`); data: array of numbers plus a `labels` array; Chart.js totals the numbers and shows each slice's relative proportion. Animation options: `animation.animateRotate` (true), `animation.animateScale` (true). Arc dataset properties include `circular` (true; false draws flat), `spacingMode` (default `'proportional'`).

## Mixed Charts

Set `type` on each dataset; the config-level type is otherwise used as fallback.

```js
const mixedChart = new Chart(ctx, {
  data: {
    datasets: [{
      type: 'bar',
      label: 'Bar Dataset',
      data: [10, 20, 30, 40]
    }, {
      type: 'line',
      label: 'Line Dataset',
      data: [50, 50, 50, 50]
    }],
    labels: ['January', 'February', 'March', 'April']
  },
  options: options
});
```

Default options are only considered at the dataset level and are not merged at the chart level for mixed charts.

Drawing order: by default the first dataset is top-most. `order` (default 0) behaves like a weight — the higher the number, the sooner the dataset is drawn, i.e. lower-order datasets are drawn over it. This also affects stacking, legend, and tooltip order.

## Area (fill)

Line and radar datasets support `fill` (implemented by the Filler plugin). Filling modes:

| Mode | Type | Values |
|---|---|---|
| Absolute dataset index | number | `1`, `2`, ... |
| Relative dataset index | string | `'-1'`, `'-2'`, `' +1'`, ... |
| Boundary | string | `'start'`, `'end'`, `'origin'` |
| Disabled | boolean | `false` |
| Stacked value below | string | `'stack'` |
| Axis value | object | `{value: number}` |
| Shape (fill inside line) | string | `'shape'` |

`fill: true` is equivalent to `fill: 'origin'`. For multiple fill colors use an object:

```js
{
  fill: {
    target: 'origin',
    above: 'rgb(255, 0, 0)',
    below: 'rgb(0, 0, 255)'
  }
}
```

Filler plugin options (namespace `options.plugins.filler`): `drawTime` (`'beforeDatasetDraw'`; also `'beforeDraw'`, `'beforeDatasetsDraw'`) and `propagate` (true — fill recursively extends to the visible target when the direct target dataset is hidden).

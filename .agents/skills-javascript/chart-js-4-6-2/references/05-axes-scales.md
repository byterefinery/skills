# Axes and Scales

Cartesian charts have x/y axes; radial charts (radar, polarArea) have a single `r` axis. Multiple axes per direction are supported; built-in label auto-skip prevents overlapping ticks; scale titles are supported; new scale types can be registered.

## Scale IDs and Dataset Mapping

Default scale ids: `'x'` and `'y'` (cartesian), `'r'` (radial). Each dataset maps to scales via `xAxisID`, `yAxisID`, `rAxisID`; if not specified, the first scale of that axis is used; if none exists, a new one is created. The `axis` of a scale is inferred from the first character of the id (must be `x`/`y`) — specify `position` and/or `axis` explicitly when using custom ids.

## Common Axis Options

Namespace `options.scales[scaleId]`:

| Name | Default | Description |
|---|---|---|
| `type` | | Scale type; custom scales can be registered under a string key |
| `alignToPixels` | false | Align pixel values to device pixels |
| `backgroundColor` | | Background color of the scale area |
| `border` | | Border configuration (v4: `border.display/width/color/dash/dashOffset`) |
| `display` | true | true/false, or `'auto'` (visible only if an associated dataset is visible) |
| `grid` | | Grid line configuration |
| `min` / `max` | | Explicit bounds, override data range |
| `reverse` | false | Reverse the scale |
| `stacked` | false | Stack data |
| `suggestedMin` / `suggestedMax` | | Extend range while keeping auto-fit (ignored if data goes beyond) |
| `ticks` | | Tick configuration (below) |
| `weight` | 0 | Sort weight; higher weights sit further from the chart area |

Cartesian-specific: `bounds` (`'ticks'`), `clip` (true), `position` (top/left/bottom/right), `stack`, `stackWeight` (1), `axis` (`'x'`/`'y'`), `offset` (false; true by default for bar charts — extra space at edges), `title` (scale title object; v3 renamed from `scaleLabel`).

## Common Tick Options

Namespace `options.scales[scaleId].ticks`:

| Name | Default | Description |
|---|---|---|
| `backdropColor` | 'rgba(255, 255, 255, 0.75)' | Label backdrop color |
| `backdropPadding` | 2 | Label backdrop padding |
| `callback` | | Returns the display string for a tick value |
| `display` | true | Show tick labels |
| `color` | Chart.defaults.color | Tick color |
| `font` | Chart.defaults.font | Tick font |
| `major` | {} | Major tick configuration |
| `padding` | 3 | Offset of tick labels from the axis |
| `showLabelBackdrop` | false (true for radial) | Draw backdrop behind tick labels |
| `textStrokeColor` / `textStrokeWidth` | / 0 | Stroke around tick text |
| `z` | 0 | Layer: <= 0 under datasets, > 0 on top |

## Scale Types

- **linear** — numeric data, on x or y; scatter auto-configures linear x. Specifics: `beginAtZero`, `grace` (number or `'%'` string — added room above max / below min; explicit `min`/`max` are not extended, data/suggested bounds are), ticks: `count`, `format` (Intl.NumberFormat options), `precision`, `stepSize` (fixed step; if unset, nice-numbers auto algorithm).
- **category** — labels from `data.labels` (or `data.xLabels`/`data.yLabels` for horizontal/vertical); can also be defined on the axis itself: `scales.x.labels`. `min`/`max` accept a label string or a numeric index into the labels array.
- **logarithmic** — logarithmic spacing; register `LogarithmicScale`; type string `'logarithmic'` (used in docs examples, e.g. `position: 'right'`).
- **time / timeseries** — time scales; **require a date adapter** (e.g. from the chartjs/awesome list) loaded after Chart.js; step size is configured via `ticks.stepSize` (v4 removed `time.stepSize`); the ticks callback receives a **timestamp**, not a formatted label (v4 change).
- **radial linear** — radial scale for radar/polarArea; options: `animate` (true), `angleLines` (object), `beginAtZero` (false), `pointLabels` (object), `startAngle` (0; degrees, 0 at top); ticks: `count`, `format`, `maxTicksLimit` (11), `precision`, `stepSize`.

## Axis Range Settings

`suggestedMin`/`suggestedMax` only change the data values used to scale the axis (auto-fit preserved):

```js
let minDataValue = Math.min(mostNegativeValue, options.suggestedMin);
let maxDataValue = Math.max(mostPositiveValue, options.suggestedMax);
```

`min`/`max` hard-override the range.

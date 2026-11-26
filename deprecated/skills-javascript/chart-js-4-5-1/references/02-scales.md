# Scales Reference

## Scale Types Overview

| Type | Axis | Use Case |
|---|---|---|
| `category` | Cartesian (x, y) | Discrete labels from `data.labels` |
| `linear` | Cartesian (x, y) | Continuous numeric data |
| `time` | Cartesian (x, y) | Dates and timestamps |
| `logarithmic` | Cartesian (x, y) | Log-scale numeric data |
| `radialLinear` | Radial (r) | Radar and polar area charts |

## Common Cartesian Scale Options

| Property | Type | Default | Description |
|---|---|---|---|
| `type` | `string` | | Scale type: `category`, `linear`, `time`, `logarithmic` |
| `position` | `string` | `'left'` \| `'bottom'` | Position: `'left'`, `'right'`, `'top'`, `'bottom'` |
| `axis` | `string` | | Explicit axis: `'x'` or `'y'` |
| `min` | `number` \| `string` | | Minimum value/label |
| `max` | `number` \| `string` | | Maximum value/label |
| `suggestedMin` | `number` \| `string` | | Suggested min (respects data) |
| `suggestedMax` | `number` \| `string` | | Suggested max (respects data) |
| `reverse` | `boolean` | `false` | Reverse scale direction |
| `stacked` | `boolean` | `false` | Stack datasets on this axis |
| `display` | `boolean` | `true` | Show the axis |
| `grid` | `object` | | Grid line options |
| `border` | `object` | | Border options |
| `ticks` | `object` | | Tick options |
| `title` | `object` | | Axis title options |

### Grid Options

| Property | Type | Default | Description |
|---|---|---|---|
| `display` | `boolean` | `true` | Show grid lines |
| `color` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Grid line color |
| `borderDash` | `number[]` | `[]` | Dash pattern |
| `borderDashOffset` | `number` | `0` | Dash offset |
| `lineWidth` | `number` | `1` | Line width |
| `drawOnChartArea` | `boolean` | `true` | Draw in chart area |
| `drawTicks` | `boolean` | `true` | Draw tick marks |
| `tickColor` | `Color` | | Color of tick marks |
| `tickWidth` | `number` | | Width of tick marks |
| `tickLength` | `number` | | Length of tick marks |
| `z` | `number` | `0` | Drawing order |

### Tick Options

| Property | Type | Default | Description |
|---|---|---|---|
| `display` | `boolean` | `true` | Show ticks |
| `color` | `Color` | | Tick label color |
| `font` | `Font` | | Tick label font |
| `padding` | `number` | `3` | Padding between tick and axis |
| `maxRotation` | `number` | `90` | Maximum rotation degrees |
| `minRotation` | `number` | `0` | Minimum rotation degrees |
| `mirror` | `boolean` | `false` | Place labels outside chart area |
| `autoSkip` | `boolean` | `true` | Auto-skip overlapping labels |
| `autoSkipPadding` | `number` | `3` | Padding between skipped ticks |
| `maxTicksLimit` | `number` | | Maximum number of ticks |
| `maxTicksLimit` | `number` | | Cap on tick count |
| `callback` | `function` | | Custom tick formatter |
| `format` | `object` | | `Intl.NumberFormat` options |
| `stepSize` | `number` | | Fixed step between ticks |
| `count` | `number` | | Target number of ticks |
| `precision` | `number` | | Decimal precision |
| `callback` | `function` | | `(value, index, ticks) => string` |

### Title Options

| Property | Type | Default | Description |
|---|---|---|---|
| `display` | `boolean` | `false` | Show axis title |
| `text` | `string` \| `string[]` | | Title text (array = multiline) |
| `color` | `Color` | | Title color |
| `font` | `Font` | | Title font |
| `padding` | `number` \| `Padding` | | Padding around title |

## Category Scale

For discrete labels. Auto-detected when `data.labels` is used.

```javascript
options: {
  scales: {
    x: {
      type: 'category',
      labels: ['Jan', 'Feb', 'Mar']  // override data.labels
    }
  }
}
```

### Category-specific Options

| Property | Type | Description |
|---|---|---|
| `labels` | `string[]` \| `string[][]` | Labels array (nested = multiline) |

## Linear Scale

For continuous numeric data.

### Linear-specific Options

| Property | Type | Description |
|---|---|---|
| `beginAtZero` | `boolean` | Include 0 in range |
| `grace` | `number` \| `string` | Extra padding (`'10%'` or `5`) |

### Linear Tick Options

| Property | Type | Default | Description |
|---|---|---|---|
| `stepSize` | `number` | | Fixed step between ticks |
| `count` | `number` | | Target tick count |
| `precision` | `number` | | Decimal precision |
| `format` | `object` | | `Intl.NumberFormat` options |

## Time Scale

For dates and timestamps. Requires a date adapter.

### Installation

```bash
npm install chartjs-adapter-date-fns
# or
npm install chartjs-adapter-luxon
# or
npm install chartjs-adapter-moment
```

```javascript
import { Chart } from 'chart.js';
import { DateAdapter } from 'chartjs-adapter-date-fns';

Chart.register(DateAdapter);
```

### Time-specific Options

| Property | Type | Default | Description |
|---|---|---|---|
| `time.unit` | `string` | | Force unit: `millisecond`, `second`, `minute`, `hour`, `day`, `week`, `month`, `quarter`, `year` |
| `time.minUnit` | `string` | `'millisecond'` | Minimum display unit |
| `time.round` | `string` | `false` | Round dates to unit start |
| `time.parser` | `string` \| `function` | | Custom date parser |
| `time.format` | `string` | | Input date format |
| `time.displayFormats` | `object` | | Per-unit display format map |
| `time.tooltipFormat` | `string` | | Tooltip date format |
| `time.isoWeekday` | `boolean` \| `number` | `false` | First day of week |
| `ticks.source` | `string` | `'auto'` | `'auto'`, `'data'`, `'labels'` |
| `adapters.date` | `object` | `{}` | Date adapter options |

### Data Formats

```javascript
// Timestamps (milliseconds since epoch)
data: [{ x: 1704067200000, y: 10 }]

// ISO strings
data: [{ x: '2024-01-01', y: 10 }]

// Custom format (with time.format)
data: [{ x: '01/01/2024', y: 10 }]
// time: { format: 'MM/DD/YYYY' }
```

### Display Formats

```javascript
time: {
  displayFormats: {
    millisecond: 'HH:mm:ss.SSS',
    second: 'HH:mm:ss',
    minute: 'HH:mm',
    hour: 'HH:mm',
    day: 'MMM DD',
    week: 'MMM DD',
    month: 'YYYY MMM',
    quarter: 'YYYY QQ',
    year: 'YYYY'
  }
}
```

## Logarithmic Scale

For data spanning multiple orders of magnitude.

### Log-specific Options

No scale-specific options beyond common options.

### Log Tick Options

| Property | Type | Default | Description |
|---|---|---|---|
| `format` | `object` | | `Intl.NumberFormat` options |

### Internal Format

Uses numeric data internally. Values must be positive.

## Radial Linear Scale

Used by radar and polar area charts. Single scale with ID `'r'`.

### Radial-specific Options

| Property | Type | Default | Description |
|---|---|---|---|
| `beginAtZero` | `boolean` | | Include 0 |
| `angleLines.color` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Angle line color |
| `angleLines.lineWidth` | `number` | `1` | Angle line width |
| `angleLines.display` | `boolean` | `true` | Show angle lines |
| `angleLines.circular` | `boolean` | `false` | Circular angle lines |
| `pointLabels` | `object` | | Point label options |
| `pointLabels.font` | `Font` | | Point label font |
| `pointLabels.color` | `Color` | | Point label color |
| `pointLabels.callback` | `function` | | Custom label formatter |
| `grid.circular` | `boolean` | `false` | Circular grid lines |
| `grid.color` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Grid color |
| `grid.lineWidth` | `number` | `1` | Grid line width |

## Multiple Axes

```javascript
options: {
  scales: {
    x: { position: 'bottom' },
    y: {
      position: 'left',
      grid: { color: 'rgba(0,0,0,0.1)' }
    },
    y1: {
      position: 'right',
      grid: { drawOnChartArea: false },
      ticks: { color: 'red' }
    }
  }
}
```

Map datasets to axes:

```javascript
datasets: [
  { data: [1, 2, 3], yAxisID: 'y' },
  { data: [10, 20, 30], yAxisID: 'y1' }
]
```

## Axis ID Detection

- Axis ID starting with `'x'` → x-axis (horizontal)
- Axis ID starting with `'y'` → y-axis (vertical)
- Explicit `axis` property overrides detection
- Explicit `position` also determines axis when `axis` is not set

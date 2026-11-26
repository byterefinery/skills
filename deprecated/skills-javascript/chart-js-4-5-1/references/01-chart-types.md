# Chart Types Reference

## Line Chart

Line charts plot data points connected by straight or curved lines. Used for trends, time series, and comparisons.

### Dataset Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `data` | `number[]` \| `[{x, y}]` \| `[x, y][]` | required | Data points |
| `label` | `string` | `''` | Legend/tooltip label |
| `borderColor` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Line color |
| `borderWidth` | `number` | `3` | Line thickness in px |
| `borderDash` | `number[]` | `[]` | Dash pattern (e.g., `[5, 5]`) |
| `borderCapStyle` | `string` | `'butt'` | Line cap style |
| `borderJoinStyle` | `string` | `'miter'` | Line join style |
| `backgroundColor` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Fill color under line |
| `fill` | `boolean` \| `string` | `false | Fill mode: `true` (to x-axis), `'origin'`, `'end'`, `'-1'` (to dataset -1) |
| `tension` | `number` | `0` | Bezier curve tension (0 = straight, 0.4 = smooth) |
| `stepped` | `boolean` \| `string` | `false` | Stepped line: `true`/`'before'`/`'after'`/`'middle'` |
| `showLine` | `boolean` | `true` | Show connecting line |
| `spanGaps` | `boolean` \| `number` | `undefined` | Connect across null values |
| `pointRadius` | `number` | `3` | Point marker radius |
| `pointStyle` | `string` | `'circle'` | Point style: `circle`, `cross`, `dash`, `line`, `rect`, `rectRounded`, `rectRot`, `star`, `triangle` |
| `pointBackgroundColor` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Point fill color |
| `pointBorderColor` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Point border color |
| `pointBorderWidth` | `number` | `1` | Point border width |
| `pointHitRadius` | `number` | `1` | Invisible hit area radius |
| `pointHoverRadius` | `number` | `4` | Point radius on hover |
| `indexAxis` | `string` | `'x'` | `'x'` (horizontal) or `'y'` (vertical) |
| `order` | `number` | `0` | Drawing order (higher = drawn first) |
| `clip` | `number` \| `object` \| `false` | `undefined` | Clipping relative to chartArea |
| `segment` | `object` | `undefined` | Segment-level styling via callback functions |

### Fill Modes

```javascript
// Fill to x-axis
fill: true

// Fill to origin (y=0)
fill: 'origin'

// Fill to last data point
fill: 'end'

// Fill to first data point
fill: 'start'

// Fill to another dataset (by index, negative = relative)
fill: 1      // fill to dataset at index 1
fill: '-1'   // fill to previous dataset
```

### Segment Styling

Apply different styles to segments based on conditions:

```javascript
{
  segment: {
    borderColor(ctx) {
      return ctx.p0.parsed.y > ctx.p1.parsed.y ? 'red' : 'green';
    },
    borderWidth(ctx) {
      return ctx.p0.parsed.y > ctx.p1.parsed.y ? 3 : 1;
    }
  }
}
```

## Bar Chart

Bar charts display data as vertical or horizontal bars. Supports grouping, stacking, and variable widths.

### Dataset Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `data` | `number[]` \| `[{x, y}]` | required | Data values |
| `backgroundColor` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Bar fill color |
| `borderColor` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Bar border color |
| `borderWidth` | `number` \| `object` | `0` | Border width |
| `borderRadius` | `number` \| `object` | `0` | Corner radius |
| `borderSkipped` | `string` \| `boolean` | `'start'` | Skip border on side: `'start'`, `'end'`, `'left'`, `'right'`, `'top'`, `'bottom'`, `false` |
| `barPercentage` | `number` | `0.9` | Width relative to available space (0-1) |
| `categoryPercentage` | `number` | `0.8` | Category width relative to full category (0-1) |
| `barThickness` | `number` \| `string` | | Fixed bar thickness or `'flex'` |
| `maxBarThickness` | `number` | | Maximum bar thickness |
| `minBarLength` | `number` | | Minimum bar length |
| `base` | `number` | | Base value along value axis |
| `indexAxis` | `string` | `'x'` | `'x'` (vertical) or `'y'` (horizontal) |
| `grouped` | `boolean` | `true` | Grouped vs overlaid bars |
| `stack` | `string` | `'bar'` | Stack group ID |
| `inflateAmount` | `number` \| `'auto'` | `'auto'` | How much bars inflate to fill available space |
| `skipNull` | `boolean` | | Skip rendering bars for null values |

### Stacked Bar Chart

```javascript
options: {
  scales: {
    x: { stacked: true },
    y: { stacked: true }
  }
}
```

Use `stack` property on datasets to create separate stack groups:

```javascript
datasets: [
  { data: [10, 20], stack: 'groupA' },
  { data: [30, 40], stack: 'groupA' },
  { data: [50, 60], stack: 'groupB' }
]
```

### Horizontal Bar Chart

```javascript
datasets: [{
  data: [10, 20, 30],
  indexAxis: 'y'
}]
```

## Scatter Chart

Scatter charts show relationships between two numeric variables. Based on line chart with `showLine: false` and linear x-axis.

### Data Format

Only accepts point objects:

```javascript
data: [
  { x: 10, y: 20 },
  { x: 15, y: 10 },
  { x: 20, y: 5 }
]
```

### Configuration

```javascript
{
  type: 'scatter',
  options: {
    scales: {
      x: { type: 'linear', position: 'bottom' },
      y: { type: 'linear' }
    }
  }
}
```

Supports all line chart dataset properties. `showLine` defaults to `false`.

## Bubble Chart

Bubble charts display three dimensions: x position, y position, and bubble radius.

### Data Format

```javascript
data: [
  { x: 20, y: 30, r: 15 },
  { x: 40, y: 10, r: 10 }
]
```

### Dataset Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `data` | `[{x, y, r}]` | required | Points with x, y, and radius |
| `radius` | `number` | `3` | Default bubble radius (when r not in data) |
| `backgroundColor` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Bubble fill color |
| `borderColor` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Bubble border color |
| `borderWidth` | `number` | `3` | Border width |
| `hoverRadius` | `number` | `4` | Extra radius on hover |
| `hitRadius` | `number` | `1` | Extra hit detection radius |
| `pointStyle` | `string` | `'circle'` | Point style |
| `rotation` | `number` | `0` | Rotation in degrees |

## Pie Chart

Pie charts show proportional data as slices of a circle. Same class as doughnut with `cutout: 0`.

### Dataset Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `data` | `number[]` | required | Slice values |
| `backgroundColor` | `Color[]` | | Per-slice fill colors |
| `borderColor` | `Color` \| `Color[]` | `'#fff'` | Slice border color(s) |
| `borderWidth` | `number` | `2` | Border width |
| `borderAlign` | `string` | `'center'` | `'center'` or `'inner'` |
| `hoverOffset` | `number` | `0` | Distance slice moves on hover |
| `hoverBorderColor` | `Color` | | Border color on hover |
| `hoverBackgroundColor` | `Color` | | Background color on hover |
| `hoverBorderWidth` | `number` | | Border width on hover |
| `angle` | `number` | | Start angle (radians) |
| `circumference` | `number` | `360` | Total arc degrees |
| `rotation` | `number` | `0` | Rotation offset (degrees) |

### Legend Defaults

Pie charts override legend defaults. To customize:

```javascript
Chart.overrides.pie.plugins.legend = {
  position: 'right',
  labels: { usePointStyle: true }
};
```

## Doughnut Chart

Doughnut charts are pie charts with a cutout center. Default `cutout: '50%'`.

### Dataset Properties

Same as pie chart, plus:

| Property | Type | Default | Description |
|---|---|---|---|
| `cutout` | `number` \| `string` | `'50%'` | Inner radius as percentage or pixels |
| `cutoutPercentage` | `number` | | Legacy (use `cutout`) |

### Partial Doughnut

```javascript
datasets: [{
  data: [300, 50, 100],
  circumference: 180,  // half circle
  rotation: -90        // start from top
}]
```

## Radar Chart

Radar charts display multiple data points on axes radiating from center. Uses `radialLinear` scale.

### Dataset Properties

Same as line chart. Uses `options.datasets.line` namespace for defaults.

### Configuration

```javascript
{
  type: 'radar',
  data: {
    labels: ['Eating', 'Sleeping', 'Designing', 'Coding'],
    datasets: [{
      label: 'Dataset 1',
      data: [65, 59, 90, 81],
      fill: true,
      backgroundColor: 'rgba(255, 99, 132, 0.2)',
      borderColor: 'rgb(255, 99, 132)',
      pointBackgroundColor: 'rgb(255, 99, 132)'
    }]
  },
  options: {
    scales: {
      r: {
        beginAtZero: true,
        ticks: { stepSize: 20 }
      }
    }
  }
}
```

### Radial Scale Options

| Property | Type | Default | Description |
|---|---|---|---|
| `beginAtZero` | `boolean` | | Include 0 in scale |
| `angleLines.color` | `Color` | `'rgba(0, 0, 0, 0.1)'` | Color of radial angle lines |
| `angleLines.lineWidth` | `number` | `1` | Width of angle lines |
| `angleLines.circular` | `boolean` | `false` | Draw circular grid lines |
| `pointLabels` | `object` | | Point label styling |
| `pointLabels.font` | `Font` | | Font for point labels |
| `pointLabels.color` | `Color` | | Color of point labels |
| `pointLabels.callback` | `function` | | Custom label formatter |
| `grid.circular` | `boolean` | `false` | Draw circular grid |

## Polar Area Chart

Polar area charts are radial bar charts where each bar has the same angle.

### Dataset Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `data` | `number[]` | required | Bar values |
| `backgroundColor` | `Color[]` | | Per-bar fill colors |
| `borderColor` | `Color` \| `Color[]` | `'#fff'` | Border color(s) |
| `borderWidth` | `number` | `2` | Border width |
| `borderAlign` | `string` | `'center'` | `'center'` or `'inner'` |
| `hoverOffset` | `number` | `4` | Offset on hover |

### Configuration

```javascript
{
  type: 'polarArea',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green'],
    datasets: [{
      data: [11, 16, 7, 14],
      backgroundColor: [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)'
      ]
    }]
  },
  options: {
    scales: {
      r: {
        ticks: { backdropColor: 'transparent' }
      }
    }
  }
}
```

# Styling Reference

## Colors

Chart.js accepts any valid CSS color value:

```javascript
// Hex
borderColor: '#ff6384'

// RGB/RGBA
borderColor: 'rgb(255, 99, 132)'
borderColor: 'rgba(255, 99, 132, 0.5)'

// HSL/HSLA
borderColor: 'hsl(348, 100%, 68%)'

// Named
borderColor: 'red'

// Gradient
const gradient = ctx.createLinearGradient(0, 0, 0, 400);
gradient.addColorStop(0, 'rgba(255, 99, 132, 0.8)');
gradient.addColorStop(1, 'rgba(255, 99, 132, 0.1)');
backgroundColor: gradient

// Pattern
const pattern = ctx.createPattern(image, 'repeat');
backgroundColor: pattern
```

### Per-Data Point Colors

```javascript
backgroundColor: [
  'rgba(255, 99, 132, 0.5)',
  'rgba(54, 162, 235, 0.5)',
  'rgba(255, 205, 86, 0.5)'
]
```

## Fonts

### Global Font Settings

```javascript
Chart.defaults.font = {
  family: "'Inter', sans-serif",
  size: 13,
  style: 'normal',
  weight: 'normal',
  lineHeight: 1.2
};
```

### Per-Element Fonts

```javascript
options: {
  plugins: {
    legend: {
      labels: {
        font: {
          family: 'Georgia',
          size: 14,
          weight: 'bold'
        }
      }
    },
    tooltip: {
      titleFont: { weight: 'bold', size: 14 },
      bodyFont: { size: 12 }
    }
  },
  scales: {
    x: {
      ticks: {
        font: { size: 11, weight: '600' }
      },
      title: {
        font: { size: 13, weight: 'bold' }
      }
    }
  }
}
```

### Font Object

| Property | Type | Default | Description |
|---|---|---|---|
| `family` | `string` | `'Helvetica Neue', 'Helvetica', 'Arial', sans-serif` | Font family |
| `size` | `number` | `12` | Font size in px |
| `style` | `string` | `'normal'` | `normal`, `italic`, `oblique` |
| `weight` | `string` \| `number` | `undefined` | `normal`, `bold`, `lighter`, `bolder`, or 100-900 |
| `lineHeight` | `number` \| `string` | `1.2` | Line height |

## Scriptable Options

Many options can be set as functions for dynamic values:

```javascript
backgroundColor(ctx) {
  const value = ctx.parsed.y;
  return value > 50 ? 'green' : 'red';
},
borderWidth(ctx) {
  return ctx.active ? 3 : 1;
}
```

### Context Object

The context passed to scriptable options includes:

| Property | Description |
|---|---|
| `active` | Whether element is active |
| `dataIndex` | Index in dataset |
| `datasetIndex` | Dataset index |
| `dataset` | Dataset object |
| `parsed` | Parsed data values |
| `raw` | Raw data value |
| `chart` | Chart instance |
| `chartArea` | Chart area rectangle |
| `index` | Same as dataIndex |

## Indexable Options

Some options accept arrays indexed by data point:

```javascript
pointRadius: [5, 3, 8, 2],
pointBackgroundColor: ['red', 'green', 'blue', 'yellow']
```

## Point Styles

| Style | Shape |
|---|---|
| `'circle'` | Circle (default) |
| `'cross'` | Cross (+) |
| `'crossRot'` | Rotated cross (x) |
| `'dash'` | Dash (-) |
| `'line'` | Line |
| `'rect'` | Square |
| `'rectRounded'` | Rounded square |
| `'rectRot'` | Rotated square |
| `'star'` | Star |
| `'triangle'` | Triangle |

Custom point style (Image):

```javascript
pointStyle(ctx) {
  return new Image();  // or canvas pattern
}
```

## Segment Options (Line Charts)

Style individual line segments:

```javascript
segment: {
  borderColor(ctx) {
    return ctx.p0.parsed.y > ctx.p1.parsed.y ? '#ff6384' : '#36a2eb';
  },
  borderWidth(ctx) {
    return Math.abs(ctx.p0.parsed.y - ctx.p1.parsed.y) > 10 ? 3 : 1;
  },
  borderDash(ctx) {
    return ctx.p0.parsed.y === ctx.p1.parsed.y ? [5, 5] : [];
  }
}
```

## Border Radius (Bar Charts)

```javascript
// All corners
borderRadius: 4

// Per corner
borderRadius: {
  topLeft: 4,
  topRight: 4,
  bottomLeft: 0,
  bottomRight: 0
}

// Scriptable
borderRadius(ctx) {
  return ctx.parsed.y > 50 ? 8 : 0;
}
```

## Global Defaults

```javascript
Chart.defaults.color = '#666';
Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.1)';
Chart.defaults.backgroundColor = 'rgba(0, 0, 0, 0.1)';
Chart.defaults.font = { family: 'Inter', size: 13 };
```

## Type-Specific Overrides

```javascript
Chart.overrides.line = {
  tension: 0.3,
  showLine: true
};

Chart.overrides.bar = {
  borderRadius: 4,
  borderSkipped: false
};
```

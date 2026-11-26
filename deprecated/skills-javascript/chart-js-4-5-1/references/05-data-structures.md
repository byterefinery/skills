# Data Structures Reference

## Data Formats

### Primitive Array

Simple numeric values paired with `data.labels`:

```javascript
data: {
  labels: ['a', 'b', 'c'],
  datasets: [{
    data: [20, 10, 30]
  }]
}
```

Values at same index map to labels. Used by bar, line, pie, doughnut, radar, polarArea.

### Tuple Array

Arrays of `[x, y]` pairs:

```javascript
data: {
  datasets: [{
    data: [[10, 20], [15, null], [20, 10]]
  }]
}
```

First element = index axis value, second = value axis. `null` creates gaps.

### Object Array

Objects with `x` and `y` properties:

```javascript
data: {
  datasets: [{
    data: [
      { x: 10, y: 20 },
      { x: 15, y: null },
      { x: 20, y: 10 }
    ]
  }]
}
```

This is the internal format used by Chart.js. Supports string x values for category scales:

```javascript
data: [{ x: 'Sales', y: 20 }, { x: 'Revenue', y: 10 }]
```

Or date strings for time scales:

```javascript
data: [{ x: '2024-01-01', y: 20 }, { x: '2024-01-02', y: 15 }]
```

### Custom Properties

Map nested or renamed properties:

```javascript
data: {
  datasets: [{
    data: [
      { id: 'Sales', nested: { value: 1500 } },
      { id: 'Purchases', nested: { value: 500 } }
    ]
  }]
},
options: {
  parsing: {
    xAxisKey: 'id',
    yAxisKey: 'nested.value'
  }
}
```

For pie/doughnut/radar/polarArea, use `key` for the value:

```javascript
options: {
  parsing: {
    key: 'nested.value'
  }
}
```

## Parsing

### Disable Parsing

When data is already in the correct internal format, disable parsing for performance:

```javascript
options: {
  parsing: false
}
```

Data must be sorted and in the scale's internal format.

### Custom Parser

```javascript
options: {
  parsing: (ctx, data) => {
    // ctx: { dataIndex, datasetIndex }
    // data: the raw data point
    return { x: data.customX, y: data.customY };
  }
}
```

## Null Values

`null` creates gaps in the data:

```javascript
data: [10, 20, null, 30, 40]
```

- **Line charts**: gap in the line (unless `spanGaps: true`)
- **Bar charts**: no bar rendered
- **Scatter/bubble**: no point rendered

### spanGaps

Connect lines across null values:

```javascript
datasets: [{
  data: [10, 20, null, 30],
  spanGaps: true        // connect across null
  // spanGaps: 1        // connect if gap <= 1 data point
}]
```

## Data Labels

### Global Labels

```javascript
data: {
  labels: ['Jan', 'Feb', 'Mar'],
  datasets: [{ data: [10, 20, 30] }]
}
```

### Per-Axis Labels

```javascript
options: {
  scales: {
    x: {
      type: 'category',
      labels: ['A', 'B', 'C']  // override data.labels for x-axis
    }
  }
}
```

### Multiline Labels

```javascript
labels: [
  ['Line 1', 'Line 2'],
  ['Single line'],
  ['Short', 'Medium', 'Long']
]
```

## Dataset Configuration

### Per-Dataset Options

Options can be set directly on the dataset object:

```javascript
datasets: [{
  label: 'Dataset 1',
  data: [10, 20, 30],
  borderColor: 'red',     // dataset-level option
  backgroundColor: 'blue',
  borderWidth: 2,
  tension: 0.1
}]
```

### Option Resolution Order

Options are resolved in this order (most specific first):

1. Dataset object properties (e.g., `datasets[0].borderColor`)
2. `options.datasets.<type>` (e.g., `options.datasets.line.borderColor`)
3. `options.elements.<element>` (e.g., `options.elements.line.borderColor`)
4. `Chart.overrides.<type>` (chart type defaults)
5. `Chart.defaults` (global defaults)

## Updating Data

```javascript
// Replace all data
chart.data.datasets[0].data = [1, 2, 3, 4, 5];
chart.update();

// Push new data point
chart.data.datasets[0].data.push(6);
chart.data.labels.push('New Label');
chart.update();

// Remove data point
chart.data.datasets[0].data.pop();
chart.data.labels.pop();
chart.update();

// Animate update
chart.update('default');  // 'default', 'none', 'reset', 'active'
```

## Internal Data Format

Each chart type stores data in a specific internal format:

| Chart Type | Internal Format |
|---|---|
| line, bar, scatter | `{x, y}` |
| bubble | `{x, y, r}` |
| pie, doughnut | `{parsed: number}` (the value) |
| radar, polarArea | `{parsed: number}` (the value) |

When `parsing: false`, data must match the internal format.

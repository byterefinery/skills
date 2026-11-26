# Mixed Charts Reference

## Creating Mixed Charts

Specify `type` on each dataset to combine chart types:

```javascript
new Chart(ctx, {
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr'],
    datasets: [
      {
        type: 'bar',
        label: 'Sales',
        data: [10, 20, 30, 40],
        backgroundColor: 'rgba(255, 99, 132, 0.5)'
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

## Drawing Order

Datasets are drawn in reverse order by default (first dataset = top-most). Control with `order`:

```javascript
datasets: [
  { type: 'bar', data: [1, 2, 3], order: 1 },  // drawn second (lower)
  { type: 'line', data: [4, 5, 6], order: 0 }   // drawn first (higher, on top)
]
```

Higher `order` value = drawn earlier = lower in z-order.

## Mixed Chart with Multiple Axes

```javascript
new Chart(ctx, {
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [
      {
        type: 'bar',
        label: 'Revenue ($)',
        data: [1000, 1500, 1200],
        yAxisID: 'y'
      },
      {
        type: 'line',
        label: 'Growth (%)',
        data: [5, 8, 6],
        borderColor: 'rgb(75, 192, 192)',
        yAxisID: 'y1'
      }
    ]
  },
  options: {
    scales: {
      y: {
        position: 'left',
        title: { display: true, text: 'Revenue ($)' }
      },
      y1: {
        position: 'right',
        grid: { drawOnChartArea: false },
        title: { display: true, text: 'Growth (%)' }
      }
    }
  }
});
```

## Common Mixed Chart Patterns

### Bar + Line (Benchmark)

```javascript
datasets: [
  { type: 'bar', label: 'Actual', data: [80, 90, 70, 85] },
  { type: 'line', label: 'Target', data: [85, 85, 85, 85], borderColor: 'red', borderDash: [5, 5] }
]
```

### Scatter + Line (Trend)

```javascript
datasets: [
  { type: 'scatter', label: 'Data Points', data: [{x: 1, y: 2}, {x: 2, y: 3}] },
  { type: 'line', label: 'Trend', data: [{x: 1, y: 2}, {x: 2, y: 3}], borderColor: 'blue', pointRadius: 0 }
]
```

### Bar + Bar (Comparison)

```javascript
datasets: [
  { type: 'bar', label: '2023', data: [10, 15, 20] },
  { type: 'bar', label: '2024', data: [12, 18, 22] }
]
```

### Stacked Bar + Line

```javascript
options: {
  scales: {
    x: { stacked: true },
    y: { stacked: true }
  }
}
datasets: [
  { type: 'bar', label: 'A', data: [10, 20], stack: 'sales' },
  { type: 'bar', label: 'B', data: [5, 15], stack: 'sales' },
  { type: 'line', label: 'Total', data: [15, 35], yAxisID: 'y1' }
]
```

## Default Type

The chart-level `type` is used as the default when a dataset doesn't specify its own `type`:

```javascript
{
  type: 'bar',  // default type
  data: {
    datasets: [
      { data: [1, 2, 3] },              // uses 'bar' (default)
      { type: 'line', data: [4, 5, 6] }  // overrides to 'line'
    ]
  }
}
```

# Responsive Layout Reference

## Configuration Options

Namespace: `options`

| Property | Type | Default | Description |
|---|---|---|---|
| `responsive` | `boolean` | `true` | Auto-resize when container changes |
| `maintainAspectRatio` | `boolean` | `true` | Keep original aspect ratio |
| `aspectRatio` | `number` | `1` (radial) / `2` (others) | Width/height ratio |
| `onResize` | `function` | `null` | Callback on resize: `(chart, size)` |
| `resizeDelay` | `number` | `0` | Debounce delay in ms |

## Container Requirements

For `responsive: true` to work, the canvas needs a **dedicated parent container** with:

1. `position: relative`
2. Explicit dimensions (via CSS or style)
3. Contains only the canvas element

```html
<div style="position: relative; height: 400px; width: 100%">
  <canvas id="myChart"></canvas>
</div>
```

### What Does NOT Work

```html
<!-- INVALID: canvas width/height attributes only accept integers -->
<canvas width="80vw" height="40vh"></canvas>

<!-- INVALID: style on canvas causes blurriness -->
<canvas style="width: 80vw; height: 40vh"></canvas>

<!-- INVALID: no dedicated container -->
<canvas style="margin: 0 auto;"></canvas>
```

## Aspect Ratio

```javascript
// Square chart
aspectRatio: 1

// Wide chart (default for most types)
aspectRatio: 2

// Custom ratio
aspectRatio: 16 / 9
```

When `maintainAspectRatio: false`, the chart fills the container regardless of aspect ratio:

```javascript
options: {
  responsive: true,
  maintainAspectRatio: false
}
```

## Programmatic Resize

```javascript
// Resize via container
chart.canvas.parentNode.style.height = '600px';
chart.canvas.parentNode.style.width = '800px';

// Direct resize
chart.resize(800, 600);

// Resize without arguments (use container size)
chart.resize();
```

## onResize Callback

```javascript
options: {
  onResize(chart, size) {
    console.log('New size:', size.width, size.height);
    // Adjust options based on size
    if (size.width < 500) {
      chart.options.plugins.legend.display = false;
    } else {
      chart.options.plugins.legend.display = true;
    }
    chart.update();
  }
}
```

## resizeDelay

Debounce resize events to improve performance during rapid resizing:

```javascript
options: {
  resizeDelay: 200  // wait 200ms after resize stops
}
```

## Printing

Charts do not auto-resize for print. Hook the `beforeprint` event:

```javascript
window.addEventListener('beforeprint', () => {
  for (const id in Chart.instances) {
    Chart.instances[id].resize();
  }
});

// Or with explicit size
window.addEventListener('beforeprint', () => {
  myChart.resize(1200, 800);
});

window.addEventListener('afterprint', () => {
  myChart.resize();  // restore auto size
});
```

## High DPI / Retina

Chart.js handles device pixel ratio automatically. The canvas render size is scaled to match the display size, ensuring crisp rendering on high-DPI screens.

No manual configuration needed — this is handled by the responsive system.

## Common Layout Patterns

### Full Width, Fixed Height

```html
<div style="position: relative; width: 100%; height: 400px">
  <canvas id="chart"></canvas>
</div>
```

```javascript
options: {
  responsive: true,
  maintainAspectRatio: false
}
```

### Square Chart

```html
<div style="position: relative; width: 100%; max-width: 500px; padding-bottom: 100%">
  <canvas id="chart" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%"></canvas>
</div>
```

### Side by Side Charts

```html
<div style="display: flex; gap: 20px">
  <div style="position: relative; flex: 1; height: 400px">
    <canvas id="chart1"></canvas>
  </div>
  <div style="position: relative; flex: 1; height: 400px">
    <canvas id="chart2"></canvas>
  </div>
</div>
```

### Responsive with CSS Grid

```html
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px">
  <div style="position: relative; height: 300px">
    <canvas id="chart1"></canvas>
  </div>
  <div style="position: relative; height: 300px">
    <canvas id="chart2"></canvas>
  </div>
</div>
```

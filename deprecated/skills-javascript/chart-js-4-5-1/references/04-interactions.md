# Interactions Reference

## Interaction Configuration

Namespace: `options.interaction` (global), `options.hover` (hover-only), `options.plugins.tooltip` (tooltip-only)

| Property | Type | Default | Description |
|---|---|---|---|
| `mode` | `string` | `'nearest'` | Interaction mode |
| `intersect` | `boolean` | `true` | Require mouse intersection |
| `axis` | `string` | `'x'` \| `'xy'` | Axis for distance calculation |
| `includeInvisible` | `boolean` | `false` | Include elements outside chart area |

## Interaction Modes

| Mode | Description |
|---|---|
| `'nearest'` | Nearest single element (default) |
| `'nearest'` + `intersect: false` | Nearest element even without direct hover |
| `'index'` | All elements at same x index |
| `'index'` + `intersect: false` | All elements at nearest x index |
| `'dataset'` | All elements in same dataset |
| `'point'` | Nearest point (same as nearest for point elements) |
| `'x'` | All elements with same x value |
| `'y'` | All elements with same y value |
| `'xy'` | All elements within a radius |

### Typical Configurations

```javascript
// Show tooltip for all datasets at same x position
interaction: { mode: 'index', intersect: false },
plugins: {
  tooltip: { mode: 'index', intersect: false }
}

// Only highlight nearest element
interaction: { mode: 'nearest', intersect: true }

// Highlight entire dataset on hover
interaction: { mode: 'dataset' }
```

## Events

Namespace: `options`

| Property | Type | Default | Description |
|---|---|---|---|
| `events` | `string[]` | `['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove']` | Events to listen for |
| `onHover` | `function` | `null` | Called on hover events |
| `onClick` | `function` | `null` | Called on click events |

### Event Handlers

```javascript
options: {
  onHover(event, activeElements, chart) {
    if (activeElements.length) {
      const idx = activeElements[0].index;
      console.log('Hovered index:', idx);
    }
  },
  onClick(event, activeElements, chart) {
    if (activeElements.length) {
      const idx = activeElements[0].index;
      const datasetIdx = activeElements[0].datasetIndex;
      console.log('Clicked:', chart.data.datasets[datasetIdx].data[idx]);
    }
  }
}
```

### Limiting Events Per Plugin

```javascript
options: {
  events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'],
  plugins: {
    tooltip: {
      events: ['click']  // tooltip only on click
    }
  }
}
```

### Capturing Non-ChartArea Events

```javascript
plugins: [{
  id: 'event-catcher',
  beforeEvent(chart, args) {
    if (args.event.type === 'mouseout') {
      // handle mouseout
    }
  }
}]
```

## Getting Elements

### Programmatic Element Access

```javascript
// Get elements at a specific mode
const elements = chart.getElementsAtEventForMode(
  event,
  'index',
  { intersect: true },
  false  // useFinal
);

// Get all active elements
const active = chart.tooltip?._active || [];

// Get dataset metadata
const meta = chart.getDatasetMeta(0);
const visible = meta.hidden === false;
const elements = meta.data;  // array of element instances

// Get sorted visible datasets
const datasets = chart.getSortedVisibleDatasetMetas();
```

### Element Properties

Each element has:

| Property | Description |
|---|---|
| `element.x` | X position |
| `element.y` | Y position |
| `element.options` | Element options (colors, sizes, etc.) |
| `element.getCenterPoint()` | Center point |
| `element.inRange(x, y)` | Check if point is in element |
| `element.inXRange(x)` | Check X range |
| `element.inYRange(y)` | Check Y range |
| `element.getPointPoint()` | Point position (for point elements) |

## Hover Configuration

Namespace: `options.hover`

Same properties as `options.interaction` but only affects hover behavior:

```javascript
options: {
  interaction: { mode: 'nearest' },  // default interaction
  hover: { mode: 'dataset' },         // hover highlights entire dataset
  plugins: {
    tooltip: { mode: 'index' }        // tooltip shows all at same index
  }
}
```

## Active Elements

```javascript
// Set active elements programmatically
chart.setActiveElements(
  [{ datasetIndex: 0, index: 2 }],
  { x: 100, y: 150 }
);
chart.update();

// Clear active elements
chart.setActiveElements([], { x: 0, y: 0 });
chart.update();
```

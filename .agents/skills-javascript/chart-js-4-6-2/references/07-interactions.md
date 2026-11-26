# Interactions

## Interaction Options

Namespace `options.interaction` (global: `Chart.defaults.interaction`). `options.hover` and `options.plugins.tooltip` extend from it — settings made only in `interaction` apply to both hover and tooltip.

| Name | Default | Description |
|---|---|---|
| `mode` | 'nearest' | Which elements appear in the interaction |
| `intersect` | true | Mode applies only when the pointer intersects an element |
| `axis` | 'x' (index mode) / 'xy' (dataset, nearest) | 'x', 'y', 'xy', or 'r' — directions used for distance |
| `includeInvisible` | false | Include points outside the chart area |

## Events

Namespace `options`:

| Name | Default | Description |
|---|---|---|
| `events` | ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'] | Browser events the chart listens to; each triggers hover and is passed to plugins |
| `onHover` | null | `(event, activeElements, chart)` — any event over chartArea |
| `onClick` | null | Fires for 'mouseup', 'click', 'contextmenu' over chartArea; same args |

Plugin events can be further restricted per plugin, e.g. `options.plugins.tooltip.events = ['click']`. Events that do not fire over chartArea (like `mouseout`) can be caught in a plugin's `beforeEvent` hook.

## Interaction Modes

- **point** — all items intersecting the point
- **nearest** — items at the nearest distance (distance to the item center, per `axis`); with `intersect: true` only on intersection — useful for combo charts where points hide behind bars
- **index** — item(s) at the same index; with intersect, the first intersecting item determines the index, otherwise the nearest in x. Use `axis: 'y'` for horizontal bar charts.
- **dataset** — items in the same dataset (same index-resolution rules)
- **x** — all items intersecting on the X coordinate only (vertical cursor; cartesian charts)
- **y** — all items intersecting on the Y coordinate only (horizontal cursor; cartesian charts)

## Converting Events to Data Values

```js
options: {
  onClick: (e) => {
    const canvasPosition = Chart.helpers.getRelativePosition(e, chart);
    const dataX = chart.scales.x.getValueForPixel(canvasPosition.x);
    const dataY = chart.scales.y.getValueForPixel(canvasPosition.y);
  }
}
```

With bundlers, import helpers separately: `import { getRelativePosition } from 'chart.js/helpers'`.

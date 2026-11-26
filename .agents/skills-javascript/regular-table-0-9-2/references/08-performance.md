# Performance

## Why It Stays Fast

Only the visible rectangular region is in the DOM. The element sizes a virtual panel to the full data set (capped, see below) and renders roughly the viewport's worth of rows and columns, recycling cells as the viewport moves. Scrolling triggers a DataListener fetch for the new slice and a redraw. The `two_billion_rows` example renders a 2,000,000,000-row table this way.

## Virtual Mode Tradeoffs

`"both"` is the default and the only mode that virtualizes both axes. `"vertical"`, `"horizontal"`, and `"none"` render the entire table along the non-virtual axis — e.g., with 1000 columns, `"vertical"` still puts all 1000 columns of every visible row in the DOM. Match the mode to your data shape; keep `"both"` unless one axis is genuinely small.

## Keeping Renders Fast

- **Style listeners run every frame while scrolling** — keep them O(visible cells) and allocation-light.
- **Throttling** — `draw()` is throttled by default (one in flight per element). Pass `{ throttle: false }` when you need an immediate forced draw (e.g., after mutating data mid-scroll); `{ cache: true }` reuses the previous DataResponse for dimensions to skip a listener call.
- **Batch with `predraw()`** — prepare the render, commit it inside a `requestAnimationFrame` alongside other DOM writes.
- **Await fonts before the first draw** — autosizing measures rendered text; the `2d_array` example awaits `document.fonts.load('12px "Open Sans"')` and `document.fonts.ready` before `draw()`.
- **Constant row heights** — supply `row_height` in the DataResponse when you can; scroll calculations then do not depend on the auto-detection probe.

## getDrawFPS()

Returns `{ avg, real_fps, virtual_fps, num_frames, elapsed }` — average ms per draw (`avg`), `real_fps` = frames/elapsed, `virtual_fps` = 1000/avg, frames rendered, and milliseconds since the last call. Two caveats:

1. The counters reset on every call — sample it on an interval.
2. The counters are module-level globals — one shared set of statistics for every `<regular-table>` instance on the page, not per element.

```javascript
setInterval(() => {
  const fps = table.getDrawFPS();
  console.log(`${fps.real_fps.toFixed(1)} fps, ${fps.avg.toFixed(2)} ms/frame`);
}, 1000);
```

## Size Limits

The virtual panel height is capped at `BROWSER_MAX_HEIGHT` — the largest virtual div the browser can handle without glitching: 10,000,000px generally, 5,000,000px on Firefox. A data set whose `num_rows × row_height` exceeds the cap will have a clamped scroll area, so very tall sets need a small enough `row_height` (or a pre-aggregated data model) to stay under the limit.

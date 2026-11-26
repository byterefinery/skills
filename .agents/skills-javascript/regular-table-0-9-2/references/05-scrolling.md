# Scrolling

## Virtual Modes

`setDataListener(listener, { virtual_mode })` selects which axes are virtualized:

| Mode | Behavior |
|---|---|
| `"both"` (default) | Both axes virtualized — only the visible region is in the DOM |
| `"vertical"` | Only y virtualized; the full table is rendered horizontally |
| `"horizontal"` | Only x virtualized; the full table is rendered vertically |
| `"none"` | No virtualization — full render |

A mode other than `"both"` renders the entire table along the non-virtual axis(es) and may cause rendering performance degradation — use it for data shapes where one axis is small (e.g., many rows, few columns → `"vertical"`). Changing `virtual_mode` requires `preserve_state: false`.

## Sub-Cell Scrolling

Because `<td>` elements must stay aligned with their row/column, a regular `<table>` can only scroll in increments of a cell, which looks irregular when cell content lengths differ. regular-table implements sub-cell (pixel-level) scrolling in CSS via slotted custom properties (`--regular-table--clip-x/y`, `--regular-table--transform-x/y`): the first row/column is clipped with `clip-path` and the body translated by the sub-cell offset.

- The `material.css` theme already includes sub-cell scrolling (it imports `sub-cell-scrolling.less`).
- For a custom theme, import `dist/css/sub-cell-scrolling.css` explicitly.
- As of 0.9.x the offsets are written as inline styles on the slotted `<table>` — a fix for WebKit not reliably reflecting CSSOM-written rules in computed style (finos/regular-table#292, fixed in v0.9.2).

## Row Height

The element auto-detects the default row height by probing a hidden `<table><td>` against your CSS. Override per render with `DataResponse.row_height`; clear a cached row height with `resetAutoSize({ row_height: true })`. Row height drives every virtual scroll calculation (scroll area height, row ranges) — a wrong value produces glitchy scrolling.

## draw() Options

```javascript
table.draw({
  invalid_viewport: true,  // assume viewport contents changed (default true)
  preserve_width: false,   // skip column auto-sizing
  throttle: true,          // default true — coalesces rapid successive draws
  cache: false,            // reuse the previous DataResponse for dimensions
});
```

`draw()` returns a `Promise` that resolves when rendering completes.

## predraw() — Prepared Commits (added in v0.8.6)

`predraw(width, height, options)` performs the asynchronous portion of a draw — DataListener invocation and viewport calculation — against the provided viewport dimensions, and returns a closure that applies the prepared render to the DOM synchronously. Use it to schedule the visible mutation inside a larger async workflow (e.g., batched with other component updates in a single animation frame):

```javascript
const commit = await table.predraw(table.clientWidth, table.clientHeight);
requestAnimationFrame(() => commit());
```

- `width`/`height` — the scrollable clip region (the element's `clientWidth`/`clientHeight` less any classic scrollbar gutter).
- Options: `invalid_viewport`, `preserve_width`, `cache`, `scroll_left`, `scroll_top` (default the element's current values), `container_height`, `throttle`.
- `commit()` returns `false` if the pre-fetched data did not fill the viewport and a corrective async `draw()` was scheduled, `true` otherwise.
- `commit.inline === true` means column widths were not yet known, so `predraw()` fell back to drawing inline (equivalent to `draw()`) and the closure is a no-op.
- Async style callbacks cannot be awaited by the synchronous commit.

## flush()

`await table.flush()` awaits pending rendering operations, including a scroll-driven draw still waiting on its animation frame. Use it before reading the DOM after a programmatic change.

## scrollToCell(x, y)

Sets `scrollLeft`/`scrollTop` to bring the given cell into view. The column position is computed from accumulated column widths (unmeasured columns default to 60px). Warns "data listener not configured" if called before `setDataListener()`. Await it — it waits for the next animation frame and a flush.

## Scroll Event

The element dispatches a `regular-table-scroll` CustomEvent after each processed scroll. Scroll-driven renders are throttled internally (one in flight per element), so a burst of scroll events does not mean a burst of renders.

# Column Sizing

## How Autosizing Works

On each render, regular-table measures the maximum content width of each visible column and caches it in internal size maps (`auto` for measured widths, `override` for user-resized widths, `indices` for the final per-column widths). Generated width rules give each column a `min-width` floor from its header cells, and body cells narrower than auto are clamped with `max-width` (the `rt-cell-clip` class plus `rt-col-{size_key}` tag make the clamp reach clipped cells).

## User Resize

- Drag the `<span class="rt-column-resize">` handle inside a column header to set an explicit override width (clamped to a 1px minimum).
- Overrides persist in the internal override map and are what `saveColumnSizes()` returns.
- Double-click the handle to reset one column to auto; Shift+double-click to reset all (double-click is emulated: two `mousedown` events within 500ms).

## API

```javascript
// { [columnIndex]: pixelWidth } — user overrides only (a structuredClone)
const sizes = table.saveColumnSizes();

table.restoreColumnSizes(sizes); // restores a prior snapshot

// clear size caches so the next draw() recalculates
table.resetAutoSize(); // everything
table.resetAutoSize({ auto: false, override: true, indices: true, row_height: false });
```

`resetAutoSize()` options (all default to `true`): `auto` (measured content widths), `override` (user-resized widths), `indices` (final per-column widths), `row_height` (cached row height).

## Fixed-Width Recipe

From the `fixed_column_widths` demo: because column widths are implemented via `max-width` CSS, a style listener that toggles a `fixed-column-width` class (carrying a `max-width`) on cells whose `getMeta(cell)` matches a predicate produces fixed-width columns. The demo's predicate checks whether the cell value contains `"Fixed"`, but any logic over `CellMetadata` works.

Note: the demo also calls `table.invalidate()` inside its style listener — that method does not exist in 0.9.2, so remove it when porting the demo.

## Persisting Layouts

`saveColumnSizes()` returns a clone of the override map, so you can persist it (e.g., `localStorage`) and restore it later on the same or a new element. Indices are logical column indices including row header columns — the `size_key` you see from `getMeta()`.

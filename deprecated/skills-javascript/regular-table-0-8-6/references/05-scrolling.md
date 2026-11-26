# Scrolling

regular-table uses virtual scrolling to render only visible cells. The viewport determines which data slice is requested from the `DataListener`.

## Virtual Modes

Configured via `setDataListener()` options:

```javascript
table.setDataListener(listener, { virtual_mode: "both" });
```

| Mode | Description |
|---|---|
| `"both"` | (Default) Virtualizes both axes. Only visible cells in DOM. Best for large datasets. |
| `"vertical"` | Virtualizes rows only. All columns rendered. Use when column count is small. |
| `"horizontal"` | Virtualizes columns only. All rows rendered. Use when row count is small. |
| `"none"` | No virtualization. Full table rendered. Only for small datasets. |

## scrollToCell

Scroll to bring a specific cell into view:

```javascript
await table.scrollToCell(x, y);
```

The method calculates pixel offsets from column widths and row heights, then sets `scrollLeft` and `scrollTop`. It is approximate — actual position depends on rendered dimensions.

### Scroll With Buffer

```javascript
const SCROLL_AHEAD = 4;

async function scrollToCellWithBuffer(x, y) {
  await table.scrollToCell(x - SCROLL_AHEAD, y - SCROLL_AHEAD);
}
```

## Sub-Cell Scrolling

By default, scrolling snaps to cell boundaries. For smooth pixel-level scrolling, use the sub-cell scrolling CSS:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table/dist/css/sub-cell-scrolling.css" />
```

Or include `material.css` which bundles sub-cell scrolling.

Without sub-cell scrolling CSS, `scrollLeft`/`scrollTop` changes snap to the nearest cell boundary, causing a "jumpy" scroll experience when content varies in length.

## row_height

The `row_height` property in `DataResponse` overrides the auto-detected row pixel height:

```javascript
return {
  num_rows: 1000000,
  num_columns: 10,
  data: /* ... */,
  row_height: 30,  // fixed 30px rows
};
```

### When to Override

- Auto-detection fails with dynamic content (images, multi-line text)
- Virtual scrolling calculations are off (overscroll/underscroll)
- Rows have consistent known height for performance

### Auto-Detection

Without `row_height`, regular-table measures the first rendered row's height from the DOM. This works well for uniform rows but can be inaccurate with:

- Variable row heights
- Lazy-loaded images
- Font loading delays
- CSS transitions affecting height

## Viewport Coordinates

The `DataListener` receives viewport coordinates that define the visible region:

```javascript
function dataListener(x0, y0, x1, y1) {
  // x0, y0: top-left corner (inclusive)
  // x1, y1: bottom-right corner (exclusive)
  // Return data for this rectangular region
}
```

These coordinates are in data-space (virtual indices), not DOM indices. The same cell `(x=5, y=10)` always has the same coordinates regardless of scroll position.

## Scroll Performance

Virtual scrolling performance depends on:

1. **DataListener speed** — the callback should return quickly. Async listeners block rendering until resolved.
2. **Style listener overhead** — heavy DOM queries in `addStyleListener()` slow down scroll events.
3. **Cell content complexity** — cells with many child elements or complex HTML render slower.

### Optimizing Scroll Performance

```javascript
// Use a lighter style listener
table.addStyleListener(() => {
  // Only query what you need
  const tds = table.querySelectorAll("td.highlight");
  // ...
});

// Set row_height to avoid measurement
return {
  row_height: 25,
  // ...
};

// Use virtual_mode: "both" for large datasets
table.setDataListener(listener, { virtual_mode: "both" });
```

## Scroll Events

```javascript
table.addEventListener("scroll", (event) => {
  // Fires on every scroll event
  // Use for saving edit state, lazy loading, etc.
  // Avoid heavy work here
});
```

## Programmatic Scrolling

```javascript
// Direct scroll (bypasses scrollToCell calculation)
table.scrollTop = 500;
table.scrollLeft = 200;

// Then trigger re-render
table.draw();
```

Direct scroll properties work but may not align with cell boundaries unless sub-cell scrolling CSS is active.

## Gotchas

- **`scrollToCell()` before first `draw()`** — column widths are unknown before the initial render. Call `scrollToCell()` after `table.draw()` has completed.
- **`virtual_mode: "none"` with large data** — renders the entire table in the DOM. This can cause memory issues with large datasets. Only use for small tables.
- **Variable row heights break virtual scrolling** — when rows have different heights, the virtual scroll position calculation is wrong. Either use `row_height` override or avoid virtualization.
- **`material.css` includes sub-cell scrolling** — if you use `material.css`, you don't need to also include `sub-cell-scrolling.css`.
- **Scroll event fires frequently** — avoid expensive operations in scroll handlers. Use throttling or debouncing if needed.
- **`preserve_state` keeps scroll position** — when re-setting the data listener with `preserve_state: true`, the current scroll position is maintained.

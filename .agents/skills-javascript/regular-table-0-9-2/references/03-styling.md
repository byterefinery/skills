# Styling

The element renders a plain `<table>` (slotted into its shadow DOM), so regular CSS for `<table>` applies directly. Bundled themes cover the common cases; data-dependent styling uses `addStyleListener()` + `getMeta()`.

## Bundled Stylesheets

| File | Purpose |
|---|---|
| `dist/css/material.css` | Material-style theme — Open Sans (Google Fonts), compact rows, padding, hover scrollbar styling — and it imports sub-cell scrolling |
| `dist/css/sub-cell-scrolling.css` | Standalone sub-cell (pixel-level) scrolling micro-offsets |
| `dist/css/container.css` | Internal container layout — injected into the shadow root by the library itself, not meant for direct import |

From a CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table/dist/css/material.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table/dist/css/sub-cell-scrolling.css" />
```

Without any CSS the table renders with browser defaults.

## addStyleListener()

The callback is invoked whenever the `<table>` is re-rendered — API invocations of `draw()` and user-initiated events such as scrolling. It receives `{ detail: tableElement }`, may be async, and returns an unsubscribe function:

```javascript
const unsubscribe = table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    td.setAttribute("contenteditable", true);
  }
});
// later
unsubscribe();
```

Because cells are recycled across scrolls, any per-cell DOM change (classes, attributes, inline styles) must be re-applied from a style listener on every render. `removeStyleListener(callback)` also exists; it asserts if the callback was not registered.

A synchronous `predraw()` commit cannot await async style callbacks — deferred DOM effects land after the commit.

## getMeta()

Returns the `CellMetadata` record for a rendered `<td>`/`<th>`, mapping DOM back to virtual coordinates:

| Property | Meaning |
|---|---|
| `type` | `"body"` \| `"row_header"` \| `"column_header"` \| `"corner"` |
| `x`, `y` | Virtual column/row index (absent on some header variants) |
| `x0`, `y0`, `x1`, `y1` | Current viewport bounds in data space |
| `dx`, `dy` | Index within the returned `data` slice (body cells) |
| `column_header_y` | Level index within `column_headers[x]` (column header cells) |
| `row_header_x` | Level index within `row_headers[y]` (row header cells) |
| `size_key` | Unique column index including row header columns |
| `virtual_x` | Virtual x position |
| `value` | The value displayed in the cell or header |
| `column_header`, `row_header` | The full header arrays for this cell |
| `user` | The value from `DataResponse.metadata` at this cell |

`getMeta()` also accepts a coordinates-like object — `{row_header_x, y}`, `{column_header_y, x}`, or `{dx, dy}` — and resolves it to the rendered cell's metadata. It returns `undefined` for elements with no metadata (text nodes, `<tr>`, the element itself); always guard the return value.

## Data-Aware Styling Recipes

Plain CSS cannot select on properties of your data — e.g., `tr:nth-child(even)` strips by DOM position, so scrolling shifts the data under fixed stripes. Recipes from the examples and features:

- **Value-based styling** — in a style listener, iterate `td`, read `getMeta(td).value`, toggle a class (negatives red, heatmaps by magnitude, categories).
- **Virtual-aware row stripes** (`row_stripes` demo) — on each render, read `meta.y0` from the first cell of the first row and toggle `stripes`/`reverse-stripes` classes on the `regular-table` element itself, so CSS `tr:nth-child` alternation stays attached to data rows as the table scrolls. The demo returns a cleanup function that unsubscribes and removes the classes.
- **Column-specific styling** — a `<td>` may represent a different column depending on horizontal scroll position, so positional column selectors are wrong. Use `meta.x` per cell, or enable `column_classes: true` in `setDataListener()` and target the stable `rt-col-{size_key}` classes from your own stylesheet (adopted on the same root).
- **Canvas as a data source** (`canvas_data_model` example) — the DataListener reads pixels via `context.getImageData(x, y, 1, 1)`, a style listener sets `td.style.backgroundColor` to the cell value and blanks the text: the table renders an image.

## Fixed Column Widths (CSS recipe)

Column widths are calculated by the library using `max-width` CSS rules, so setting `max-width` from your own CSS yields fixed-width behavior for that column (the `fixed_column_widths` demo toggles a `fixed-column-width` class from a style listener based on a predicate over `getMeta(cell).value`). Column width never auto-grows past the max content width; manual shrinking is bounded (the demo quotes a 10px minimum; the resize drag itself clamps at 1px).

---
name: regular-table-0-8-6
description: >
  regular-table is a zero-dependency JavaScript library that exports a custom element (Web Component)
  rendering a virtualized HTML table for enormous or remote data sets. Use this skill whenever the user
  mentions regular-table, regular table, virtualized table, virtual data grid, async data model tables,
  FINOS regular-table, or building high-performance data grids, spreadsheets, pivot tables, or file trees
  with a native HTML table output. Also use when the user asks about virtual scrolling, column/row headers
  with colspan/rowspan merging, or integrating regular-table with Perspective, React, Web Workers, or async
  backends (v0.8.6).
license: Apache-2.0
compatibility: Modern browsers supporting Custom Elements v1 and ES modules. Requires Node.js 16+ for build.
metadata:
  tags:
    - web-component
    - data-grid
    - virtualization
    - tables
    - javascript
---

# regular-table 0.8.6

## Overview

regular-table exports a `<regular-table>` custom element that renders a standard HTML `<table>` inside a scrollable viewport. Only visible cells are rendered via a virtual data model, making it suitable for data sets with billions of rows. The library has zero runtime dependencies and outputs a plain `<table>` that works with regular CSS.

Importing the module is a side-effect that registers the custom element — no symbols are exported. The core pattern is: set a `DataListener` callback that returns rectangular slices of data for the current viewport, then call `draw()`.

### Key Concepts

- **Virtual Data Model** — the library calls your `DataListener` with `(x0, y0, x1, y1)` viewport coordinates and expects a `DataResponse` with `num_rows`, `num_columns`, and a columnar `data` array. Only the visible region is fetched.
- **Columnar data** — `data[x][y]` returns the y-th row of the x-th column within the slice. This orientation differs from the more common row-major format.
- **Async support** — `DataListener` can return a `Promise`, enabling Web Workers, fetch calls, or any async backend.
- **`getMeta()`** — maps any rendered `<td>` or `<th>` back to its virtual data coordinates, enabling data-aware styling and interaction.
- **`addStyleListener()`** — callback invoked after each render, for applying data-dependent CSS classes or attributes.

### Core API

| Method | Purpose |
|---|---|
| `table.setDataListener(listener, options?)` | Register the virtual data model callback |
| `table.draw(options?)` | Trigger a re-render |
| `table.addStyleListener(callback)` | Register post-render styling callback; returns unsubscribe function |
| `table.removeStyleListener(callback)` | Remove a previously registered style listener |
| `table.getMeta(element)` | Get `CellMetadata` for a `<td>`/`<th>` element |
| `table.scrollToCell(x, y)` | Scroll to bring cell `(x, y)` into view |
| `table.clear()` | Clear the table and reset internal state |
| `table.getDrawFPS()` | Get performance stats (`avg`, `real_fps`, `virtual_fps`, `num_frames`, `elapsed`) |
| `table.resetAutoSize(options?)` | Reset column sizing so next `draw()` recalculates |
| `table.saveColumnSizes()` | Save column width overrides as `{index: pixelWidth}` record |
| `table.restoreColumnSizes(sizes)` | Restore previously saved column width overrides |

### DataResponse Object

```javascript
{
  num_rows: 1000,           // total rows in the dataset
  num_columns: 10,          // total columns in the dataset
  data: [[0, 1], ["A", "B"]], // columnar: data[col][row] for the viewport slice
  column_headers?: [["Col 1"], ["Col 2"]], // per-column header arrays
  row_headers?: [["Row 1"], ["Row 2"]],     // per-row header arrays
  metadata?: [["tag1"], ["tag2"]],          // optional per-cell metadata for getMeta()
  row_height?: 25,                          // pixel height override
  merge_headers?: "both" | "row" | "column" | "none",
  column_header_merge_depth?: number,
}
```

### CellMetadata (from `getMeta()`)

| Property | Meaning |
|---|---|
| `type` | `"body"`, `"row_header"`, `"column_header"`, or `"corner"` |
| `x` | Virtual column index (body + row_header cells) |
| `y` | Virtual row index (body + row_header cells) |
| `x0`, `y0`, `x1`, `y1` | Current viewport boundaries |
| `dx`, `dy` | Index within the `data` slice (body cells only) |
| `column_header_y` | Index within `column_headers[x]` (header cells) |
| `row_header_x` | Index within `row_headers[y]` (row header cells) |
| `value` | The displayed cell value |
| `column_header` | Full column header array for this cell |
| `row_header` | Full row header array for this cell |
| `size_key` | Unique column index including row header offset |
| `user` | Custom metadata from `DataResponse.metadata` |

### Virtual Modes

```javascript
table.setDataListener(listener, { virtual_mode: "both" });   // default: both axes virtualized
table.setDataListener(listener, { virtual_mode: "vertical" }); // only vertical virtualization
table.setDataListener(listener, { virtual_mode: "horizontal" }); // only horizontal virtualization
table.setDataListener(listener, { virtual_mode: "none" });   // full render, no virtualization
```

## Usage

### Installation

**npm:**

```bash
npm install regular-table
```

```javascript
import "regular-table";
import "regular-table/dist/css/material.css";
```

**CDN:**

```html
<script type="module" src="https://cdn.jsdelivr.net/npm/regular-table@0.8.6/dist/esm/regular-table.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table@0.8.6/dist/css/material.css" />
```

### Basic Example

```html
<regular-table></regular-table>
```

```javascript
const DATA = [
  [0, 1, 2, 3, 4],
  ["A", "B", "C", "D", "E"],
  [true, false, true, false, true],
];

const table = document.querySelector("regular-table");

table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: DATA[0].length,
  num_columns: DATA.length,
  data: DATA.slice(x0, x1).map((col) => col.slice(y0, y1)),
}));

table.draw();
```

### With Column and Row Headers

```javascript
const COLUMN_NAMES = ["Numbers", "Letters", "Booleans"];

table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: DATA[0].length,
  num_columns: DATA.length,
  data: DATA.slice(x0, x1).map((col) => col.slice(y0, y1)),
  column_headers: COLUMN_NAMES.slice(x0, x1).map((name) => [name]),
  row_headers: Array.from({ length: y1 - y0 }, (_, i) => [`Row ${y0 + i}`]),
}));

table.draw();
```

### Hierarchical Group Headers

```javascript
table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: 100,
  num_columns: 6,
  data: /* ... */,
  column_headers: [
    ["Group A", "Col 1"],
    ["Group A", "Col 2"],
    ["Group B", "Col 3"],
    ["Group B", "Col 4"],
  ],
  row_headers: [
    ["Section 1", "Row 0"],
    ["Section 1", "Row 1"],
  ],
}));
```

Consecutive repeated values in header arrays are automatically merged via `colspan`/`rowspan`. Disable with `merge_headers: "none"`.

### Async Data Model (Web Worker)

```javascript
// Browser
const worker = new Worker("data-worker.js");

worker.addEventListener("message", (event) => {
  resolve(event.data);
});

table.setDataListener(async (x0, y0, x1, y1) => {
  return new Promise((resolve) => {
    worker.once("message", (event) => resolve(event.data));
    worker.postMessage([x0, y0, x1, y1]);
  });
});

table.draw();
```

```javascript
// data-worker.js
self.addEventListener("message", (event) => {
  const [x0, y0, x1, y1] = event.data;
  const response = fetchDataSlice(x0, y0, x1, y1);
  self.postMessage(response);
});
```

### Data-Aware Styling

```javascript
// Highlight negative values in red
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    if (meta && meta.value != null && Number(meta.value) < 0) {
      td.classList.add("negative");
    }
  }
});

table.draw();
```

```css
.negative { color: red; font-weight: bold; }
```

### Zebra Striping (Virtual-Aware)

Regular CSS `:nth-child` strips by DOM position, not data position. Use `getMeta()` for data-aware striping:

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    td.classList.toggle("zebra", meta.y % 2 === 0);
  }
});
```

### Row Selection

```javascript
const selectedRows = new Set();

table.addEventListener("click", (event) => {
  const meta = table.getMeta(event.target);
  if (meta && meta.y >= 0) {
    if (selectedRows.has(meta.y)) {
      selectedRows.delete(meta.y);
    } else {
      selectedRows.add(meta.y);
    }
    table.draw();
  }
});

table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    td.classList.toggle("selected", selectedRows.has(meta.y));
  }
});
```

### Scrolling to a Cell

```javascript
// Scroll to column 50, row 1000
await table.scrollToCell(50, 1000);
```

### React Integration

```javascript
import "regular-table";

function App() {
  const ref = useCallback((el) => {
    if (el) {
      el.setDataListener(dataListener);
      el.draw();
    }
  }, []);

  return <regular-table ref={ref} />;
}
```

### Sub-Cell Scrolling

For smooth pixel-level scrolling (rather than cell-by-cell), include the sub-cell scrolling CSS:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table/dist/css/sub-cell-scrolling.css" />
```

The bundled `material.css` theme already includes sub-cell scrolling.

### Column Width Management

```javascript
// Save current column widths
const widths = table.saveColumnSizes();

// Later restore them
table.restoreColumnSizes(widths);

// Force recalculation on next draw
table.resetAutoSize();
```

### Performance Monitoring

```javascript
setInterval(() => {
  const { real_fps, avg, num_frames } = table.getDrawFPS();
  console.log(`${real_fps} fps, avg ${avg}ms/frame, ${num_frames} frames`);
}, 1000);
```

## Gotchas

- **Data is columnar, not row-major** — `data[x][y]` means column x, row y. The `DataResponse.data` array is indexed by column first, then row. This is the opposite of most table libraries. A common mistake is transposing the data.

- **`setDataListener()` does not auto-draw** — after setting the listener, you must call `table.draw()` to trigger rendering. The listener is only invoked during `draw()`.

- **`draw()` is async** — `draw()` returns a Promise that resolves when rendering completes. Use `await table.draw()` if subsequent code depends on the rendered DOM.

- **`getMeta()` returns `undefined` for non-cell elements** — calling `getMeta()` on `<tr>`, `<tbody>`, or the `<table>` itself returns `undefined`. Always check the return value before accessing properties.

- **`addStyleListener()` fires on every render** — including scroll events. Keep style callbacks fast; heavy DOM queries or synchronous work here will tank scrolling performance.

- **Header arrays must match the viewport width** — `column_headers` must have exactly `x1 - x0` entries (one per column in the current data slice). Same for `row_headers` with `y1 - y0` entries.

- **`merge_headers` auto-merges consecutive duplicates** — if you want every header cell rendered separately (no colspan/rowspan), set `merge_headers: "none"`. Default is `"both"`.

- **`virtual_mode: "none"` renders everything** — disabling virtualization renders the entire table in the DOM. Only use this for small datasets; it defeats the purpose of regular-table for large data.

- **No symbols exported** — the module only registers the custom element as a side effect. There is no `import { RegularTable } from "regular-table"`. Access the element via DOM APIs or template literals.

- **`material.css` is optional but recommended** — without any CSS, the table renders with browser defaults. The `material.css` theme provides sub-cell scrolling, sticky headers, and clean styling.

- **`row_height` auto-detection can be off** — if rows have variable heights or dynamic content, virtual scrolling may miscalculate. Override with `row_height` in the `DataResponse` if needed.

- **`preserve_state` option** — when calling `setDataListener()` a second time, use `{ preserve_state: true }` to keep existing scroll position and column sizing. Without it, state is reset.

- **Custom element registration is immediate** — importing the module registers `<regular-table>` globally. Using multiple versions on the same page will cause a `DuplicateCustomElement` error.

- **`clear()` resets everything** — calling `table.clear()` destroys the internal view model. You must re-register the `DataListener` and call `draw()` again.

- **`scrollToCell()` is approximate** — column widths may not be known yet when `scrollToCell()` is called (e.g., before the first `draw()`). Call it after the table has rendered at least once.

- **Metadata from `DataResponse.metadata` lands in `meta.user`** — the optional `metadata` field in `DataResponse` is the same shape as `data` and its values appear as `meta.user` in `getMeta()` results.

- **`getDrawFPS()` resets its counter** — each call to `getDrawFPS()` clears the internal frame counter. Call it at regular intervals for accurate FPS measurement.

- **Contenteditable cells need `addStyleListener`** — to make cells editable, use `addStyleListener()` to set `contenteditable="true"` on `<td>` elements after each render, since cells are recreated during scrolling.

## References

- [01-data-model.md](references/01-data-model.md) — DataListener, DataResponse, columnar data orientation, async patterns, Web Worker integration
- [02-styling.md](references/02-styling.md) — addStyleListener, getMeta, CSS theming, material.css, sub-cell scrolling, data-aware styles
- [03-headers.md](references/03-headers.md) — Column headers, row headers, hierarchical/group headers, merge_headers, colspan/rowspan behavior
- [04-interaction.md](references/04-interaction.md) — Event handling, row/column selection, keyboard navigation, contenteditable cells, click handlers
- [05-scrolling.md](references/05-scrolling.md) — Virtual modes, scrollToCell, sub-cell scrolling, row_height, viewport management
- [06-column-sizing.md](references/06-column-sizing.md) — Auto-sizing, saveColumnSizes, restoreColumnSizes, resetAutoSize, override widths
- [07-integration.md](references/07-integration.md) — React, Vue, Svelte, Perspective, CDN vs npm, bundlers, TypeScript usage
- [08-performance.md](references/08-performance.md) — getDrawFPS, virtualization modes, rendering optimization, large dataset patterns

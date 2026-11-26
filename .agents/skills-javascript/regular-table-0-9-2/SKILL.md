---
name: regular-table-0-9-2
description: >
  regular-table is a zero-dependency JavaScript library that exports a custom element
  rendering a virtualized HTML table for enormous or remote data sets. Only visible
  cells are rendered, queried from a natively async virtual data model. Use this skill
  whenever the user mentions regular-table, virtualized table, virtual data grid, async
  data model tables, FINOS regular-table, or building data grids, spreadsheets, pivot
  tables, or file trees that output a native HTML table. Also use when the user asks
  about virtual scrolling, column or row headers with colspan and rowspan merging,
  column resize, or integrating regular-table with React, Web Workers, or async
  backends (v0.9.2).
license: Apache-2.0
compatibility: >
  Modern browsers with Custom Elements v1, ES modules, and constructable stylesheets.
  Node.js 16+ for development builds.
metadata:
  tags:
    - web-component
    - data-grid
    - virtualization
    - tables
    - javascript
---

# regular-table 0.9.2

## Overview

regular-table exports a `<regular-table>` custom element that renders a standard HTML `<table>` inside a scrollable viewport. Only cells in the visible region are in the DOM; the rest of the (possibly enormous or remote) data set is queried on demand through a user-supplied *virtual data model* — a `DataListener` callback that receives viewport coordinates `(x0, y0, x1, y1)` and returns a `DataResponse` for that rectangular slice. Importing the module is a side effect: no symbols are exported, only the custom element registration.

### Key Concepts

- **Virtual data model** — `DataListener(x0, y0, x1, y1)` returns (or a `Promise` of) a `DataResponse` with the slice plus the overall dimensions (`num_rows`, `num_columns`). Nothing renders until `draw()` is called.
- **Columnar data** — `data[x][y]` is the y-th row of the x-th column of the slice. The opposite of the row-major layout most table libraries use.
- **`getMeta()`** — maps any rendered `<td>`/`<th>` back to its virtual coordinates (`x`, `y`, viewport bounds, header arrays, `value`, user `metadata`), enabling data-aware styling and interaction.
- **`addStyleListener()`** — post-render callback (fires on every draw, including scroll) for applying data-dependent classes and attributes; returns an unsubscribe function.
- **Regular CSS** — the output is a plain `<table>`, styled with normal CSS plus the bundled `material.css` / `sub-cell-scrolling.css` themes.

### Core API

| Method | Purpose |
|---|---|
| `table.setDataListener(listener, options?)` | Register the virtual data model. Options `virtual_mode` (default `"both"`), `preserve_state`, `column_classes` |
| `table.draw(options?)` | Render. Options `invalid_viewport`, `preserve_width`, `throttle`, `cache`. Returns `Promise<void>` |
| `table.predraw(width, height, options?)` | Prepare a render without applying it; returns `Promise<commit>` to apply synchronously in a chosen frame |
| `table.flush()` | Await pending render operations |
| `table.addStyleListener(callback)` | Post-render style callback; returns unsubscribe function |
| `table.removeStyleListener(callback)` | Remove a previously registered style listener |
| `table.getMeta(element?)` | `CellMetadata` for a `<td>`/`<th>` element (or a coordinates-like object), else `undefined` |
| `table.scrollToCell(x, y)` | Scroll to bring the cell at `(x, y)` into view |
| `table.clear()` | Discard the current table model and rendered table (the DataListener is kept) |
| `table.saveColumnSizes()` | User column-width overrides as `{index: pixelWidth}` |
| `table.restoreColumnSizes(sizes)` | Restore previously saved width overrides |
| `table.resetAutoSize(options?)` | Recalculate column sizes on next draw. Options `auto`, `override`, `indices`, `row_height` |
| `table.getDrawFPS()` | `{avg, real_fps, virtual_fps, num_frames, elapsed}` — counters reset on each call; global across instances |

### DataResponse Object

```javascript
{
  num_rows: 1000,        // total rows in the data set
  num_columns: 10,       // total columns in the data set
  data: [[0, 1], ["A", "B"]],  // columnar slice, data[col][row]
  column_headers?: [["Col 1"], ["Col 2"]], // per-column header arrays, specificity order
  row_headers?: [["Row 1"], ["Row 2"]],    // per-row header arrays
  metadata?: [["tag1"], ["tag2"]],         // same shape as data; surfaces as meta.user
  row_height?: 25,                       // pixel height override
  num_row_headers?: 2,                   // row header column count
  num_column_headers?: 2,                // column header row count
  column_header_merge_depth?: 2,         // colspan merge depth (default header_length - 1)
  merge_headers?: "both" | "row" | "column", // default "both"
}
```

## Usage

### Installation

**npm** (per the README):

```bash
npm add regular-table
```

```javascript
import "regular-table";
import "regular-table/dist/css/material.css";
```

**CDN:**

```html
<script type="module" src="https://cdn.jsdelivr.net/npm/regular-table"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/regular-table/dist/css/material.css" />
```

### Minimal Example

```html
<regular-table></regular-table>
```

```javascript
const DATA = [
  [0, 1, 2, 3, 4, 5],
  ["A", "B", "C", "D", "E", "F"],
  [true, false, true, false, true, false],
];

const table = document.querySelector("regular-table");

table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: DATA[0].length,
  num_columns: DATA.length,
  data: DATA.slice(x0, x1).map((col) => col.slice(y0, y1)),
}));

// await web fonts before the first draw or autosized widths will be wrong
await document.fonts.ready;
table.draw();
```

### Column and Row Headers

```javascript
const COLUMN_NAMES = ["Numbers", "Letters", "Booleans"];

table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: DATA[0].length,
  num_columns: DATA.length,
  data: DATA.slice(x0, x1).map((col) => col.slice(y0, y1)),
  column_headers: COLUMN_NAMES.slice(x0, x1).map((name) => [name]),
  row_headers: Array.from({ length: y1 - y0 }, (_, i) => [`Row ${y0 + i}`]),
}));
```

Each entry is an array in *specificity order* — `["Group A", "Column 1"]` renders two stacked header levels. Consecutive equal values merge via `rowspan`/`colspan` (see `merge_headers`, [02-headers](references/02-headers.md)).

### Async Data Model

`DataListener` may be async. regular-table does not render until the Promise settles, and does not call the listener again until the current call resolves or rejects:

```javascript
// Web worker as data source
const worker = new Worker("data-worker.js");

table.setDataListener((...viewport) => {
  return new Promise((resolve) => {
    const onMessage = (event) => {
      worker.removeEventListener("message", onMessage);
      resolve(event.data);
    };
    worker.addEventListener("message", onMessage);
    worker.postMessage(viewport);
  });
});
```

The protocol is language-agnostic: send `(x0, y0, x1, y1)`, receive a `DataResponse` as JSON — any HTTP backend works with `fetch()`.

### Data-Aware Styling

Plain CSS cannot select on your data. Use `addStyleListener()` + `getMeta()`:

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("tbody td")) {
    const meta = table.getMeta(td);
    td.classList.toggle("zebra", meta.y % 2 === 0);
  }
});
```

`meta.y0` is the viewport origin row — the row_stripes demo toggles a class on the element itself based on `meta.y0 % 2` so stripes stay attached to data rows while scrolling (see [03-styling](references/03-styling.md)).

### Row Selection

```javascript
const selected = new Set();

table.addEventListener("click", (event) => {
  const meta = table.getMeta(event.target);
  if (meta && meta.type === "body") {
    if (event.ctrlKey || event.metaKey) {
      if (selected.has(meta.y)) selected.delete(meta.y);
      else selected.add(meta.y);
    } else {
      selected.clear();
      selected.add(meta.y);
    }
    table.draw();
  }
});

table.addStyleListener(() => {
  for (const td of table.querySelectorAll("tbody td")) {
    const meta = table.getMeta(td);
    td.classList.toggle("selected", selected.has(meta.y));
  }
});
```

### Scrolling to a Cell

```javascript
await table.scrollToCell(50, 1000); // column, row
```

### Column Sizing

Column widths are auto-sized from content. Users drag the `.rt-column-resize` handle inside column headers; double-clicking a handle resets that column (Shift+double-click resets all):

```javascript
const sizes = table.saveColumnSizes(); // {index: pixelWidth}
table.restoreColumnSizes(sizes);
table.resetAutoSize(); // recalculate on next draw
```

### Batching Renders with predraw()

For frameworks that batch DOM mutations, `predraw()` runs the async part (DataListener + viewport calculation) and returns a commit closure that applies the render synchronously:

```javascript
const commit = await table.predraw(table.clientWidth, table.clientHeight);
requestAnimationFrame(() => commit());
```

## Gotchas

- **Data is columnar, not row-major** — `data[x][y]` means column x, row y. Transposing your data is the classic integration mistake.
- **`setDataListener()` does not auto-draw** — nothing renders until `draw()` is called; the listener is invoked from `draw()`/`predraw()`, not at registration.
- **The module exports nothing** — no `import { RegularTable }`. The import registers the custom element as a side effect; access instances via DOM APIs.
- **A DataListener that never settles blocks rendering forever** — always resolve or reject the Promise you return.
- **Header slices must match the data slice** — `column_headers` has exactly `x1 - x0` entries (one per visible column); `row_headers` has `y1 - y0`.
- **`merge_headers` has no `"none"` in 0.9.2** — the type is `"both" | "row" | "column"` (default `"both"`); the README's `"none"` is not implemented.
- **`virtual_mode` other than `"both"` renders the entire table on the non-virtual axis** — expect full-DOM cost along that axis.
- **`preserve_state: true` only swaps the listener** — it must not be combined with a `virtual_mode` change (console assert).
- **Style listeners run on every render, including scroll frames** — keep them fast; a synchronous `predraw()` commit cannot await async style callbacks.
- **`getMeta()` returns `undefined` for non-cell elements** — `event.target` can be a text node, `<tr>`, or the resize handle span; guard before property access.
- **`getDrawFPS()` is global and resets on each call** — one shared counter set for all instances on the page, not per element; sample it on an interval.
- **`clear()` keeps the DataListener** — it discards the table model and rendered table only; a subsequent `draw()` re-renders with the same listener.
- **`draw()` is throttled by default** — pass `{ throttle: false }` to force an immediate render (e.g., after mutating data mid-scroll).
- **Await web fonts before the first `draw()`** — autosizing measures rendered text; drawing before `document.fonts.ready` bakes in fallback-font widths.
- **The `fixed_column_widths` demo's `table.invalidate()` call is legacy** — no such method exists in 0.9.2; remove it when porting the demo.
- **Column resize drags clamp to a 1px minimum** — the handler uses `Math.max(1, width + diff)`.
- **Double-click is emulated** — two `mousedown` events within 500ms; native `dblclick` is not used for column reset.
- **`regular-table-scroll` CustomEvent** fires on the element after each processed scroll — listen for it rather than assuming a synchronous redraw.

## References

- [01-data-model.md](references/01-data-model.md) — DataListener contract, DataResponse fields, columnar orientation, async/Web Worker patterns, setDataListener options, two-billion-rows pattern
- [02-headers.md](references/02-headers.md) — Column and row headers, specificity order, colspan/rowspan merging, merge_headers, column_header_merge_depth, tree-like row headers
- [03-styling.md](references/03-styling.md) — Plain CSS, material.css, sub-cell-scrolling.css, addStyleListener, getMeta, rt-col classes, data-aware styling recipes
- [04-interaction.md](references/04-interaction.md) — DOM events, row/column/area selection demos, clipboard, contenteditable spreadsheet, keyboard navigation, column resize and reset
- [05-scrolling.md](references/05-scrolling.md) — Virtual modes, sub-cell scrolling, draw/predraw/flush options, scrollToCell, row height detection
- [06-column-sizing.md](references/06-column-sizing.md) — Autosizing mechanics, resize handle, save/restore/reset column sizes, fixed-width CSS recipe
- [07-integration.md](references/07-integration.md) — React, CDN vs npm, Web Workers, perspective compatibility, upstream development workflow
- [08-performance.md](references/08-performance.md) — Two-billion-rows pattern, draw throttling and cache, predraw batching, getDrawFPS, virtual mode tradeoffs, size limits

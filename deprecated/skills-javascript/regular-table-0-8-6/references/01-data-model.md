# Data Model

The virtual data model is the core abstraction of regular-table. Instead of passing the entire dataset, you provide a `DataListener` callback that fetches only the data needed for the current viewport.

## DataListener Signature

```javascript
table.setDataListener((x0, y0, x1, y1) => {
  return {
    num_rows: 1000,
    num_columns: 10,
    data: /* columnar slice */,
  };
});
```

The callback receives four arguments defining the viewport rectangle:

| Parameter | Meaning |
|---|---|
| `x0` | Starting column index (inclusive) |
| `y0` | Starting row index (inclusive) |
| `x1` | Ending column index (exclusive) |
| `y1` | Ending row index (exclusive) |

The callback must return a `DataResponse` object (synchronously or as a `Promise`).

## DataResponse

```typescript
interface DataResponse {
  data: CellScalar[][];       // required: columnar data slice
  num_columns: number;        // required: total columns
  num_rows: number;           // required: total rows
  column_headers?: CellScalar[][];  // optional: per-column headers
  row_headers?: CellScalar[][];    // optional: per-row headers
  metadata?: unknown[][];              // optional: per-cell user metadata
  row_height?: number;                 // optional: pixel height override
  merge_headers?: "both" | "row" | "column" | "none";
  column_header_merge_depth?: number;
}
```

### Columnar Data Orientation

The `data` field is a 2D array indexed as `data[column][row]` — column-major order. This is different from the more common row-major format.

```javascript
// For viewport (0, 0) to (3, 5):
// data[0] = [col0_row0, col0_row1, col0_row2, col0_row3, col0_row4]
// data[1] = [col1_row0, col1_row1, col1_row2, col1_row3, col1_row4]
// data[2] = [col2_row0, col2_row1, col2_row2, col2_row3, col2_row4]
```

To convert from a row-major source:

```javascript
// Row-major source
const ROWS = [
  [1, "A", true],
  [2, "B", false],
  [3, "C", true],
];

// Transpose to columnar
function getDataSlice(x0, y0, x1, y1) {
  return {
    num_rows: ROWS.length,
    num_columns: ROWS[0].length,
    data: Array.from({ length: x1 - x0 }, (_, dx) =>
      ROWS.map((row) => row[x0 + dx])
    ).map((col) => col.slice(y0, y1)),
  };
}
```

### CellScalar Types

Cell values can be: `string`, `number`, `boolean`, `null`, or `HTMLElement`. When an `HTMLElement` is used, it is rendered directly into the cell.

```javascript
data: [
  [{ textContent: "Bold" }, { textContent: "Normal" }],
],
```

## Async Data Models

The `DataListener` can return a `Promise`, enabling async data sources:

```javascript
table.setDataListener(async (x0, y0, x1, y1) => {
  const response = await fetch(`/api/data?x0=${x0}&y0=${y0}&x1=${x1}&y1=${y1}`);
  return response.json();
});
```

The table blocks rendering until the Promise resolves. It will not issue another request until the current one completes.

### Web Worker Pattern

```javascript
// Main thread
const worker = new Worker("worker.js");

table.setDataListener((x0, y0, x1, y1) => {
  return new Promise((resolve) => {
    worker.once("message", (event) => resolve(event.data));
    worker.postMessage([x0, y0, x1, y1]);
  });
});

table.draw();
```

```javascript
// worker.js
self.addEventListener("message", (event) => {
  const [x0, y0, x1, y1] = event.data;
  // Process data in background thread
  const response = computeSlice(x0, y0, x1, y1);
  self.postMessage(response);
});
```

### Perspective Integration

regular-table is designed to work with [Perspective](https://github.comfinos/perspective/), a WebAssembly data engine:

```javascript
import "perspective";
import "regular-table";

const table = perspective.worker().new({
  columns: ["a", "b", "c"],
  data: /* large dataset */,
});

regularTable.setDataListener((x0, y0, x1, y1) => {
  return table.table.then((t) => t.to_arrow());
});
```

## SetDataListener Options

```javascript
table.setDataListener(listener, {
  virtual_mode: "both",      // "both" | "horizontal" | "vertical" | "none"
  preserve_state: false,     // keep scroll position and column sizes
});
```

- **`virtual_mode: "both"`** (default) — virtualizes both axes. Only visible cells are in the DOM.
- **`virtual_mode: "vertical"`** — virtualizes rows only. All columns are rendered.
- **`virtual_mode: "horizontal"`** — virtualizes columns only. All rows are rendered.
- **`virtual_mode: "none"`** — no virtualization. Entire table is rendered. Use only for small datasets.
- **`preserve_state: true`** — when re-setting the listener, keeps scroll position and column sizing. Without it, the table resets to origin.

## Metadata Field

The optional `metadata` field in `DataResponse` mirrors the shape of `data` and provides per-cell custom data accessible via `getMeta(cell).user`:

```javascript
return {
  num_rows: 100,
  num_columns: 5,
  data: [[1, 2], [3, 4]],
  metadata: [["positive", "negative"], ["neutral", "positive"]],
};
```

```javascript
table.addStyleListener(() => {
  for (const td of table.querySelectorAll("td")) {
    const meta = table.getMeta(td);
    if (meta.user === "negative") {
      td.classList.add("negative");
    }
  }
});
```

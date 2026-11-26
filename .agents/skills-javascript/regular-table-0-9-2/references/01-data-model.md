# Data Model

The virtual data model is the contract between your data and the `<regular-table>` element: a `DataListener` function that serves rectangular slices of an arbitrarily large (or remote) data set.

- [DataListener](#datalistener)
- [DataResponse Fields](#dataresponse-fields)
- [Columnar Orientation](#columnar-orientation)
- [Async Data Models](#async-data-models)
- [setDataListener Options](#setdatalistener-options)
- [The Two-Billion-Rows Pattern](#the-two-billion-rows-pattern)

## DataListener

```javascript
type DataListener = (x0, y0, x1, y1) => DataResponse | Promise<DataResponse>
```

- `x0, y0` — origin (top-left) of the viewport in data coordinates
- `x1, y1` — corner (bottom-right) of the viewport
- Return — a `DataResponse` object, or a `Promise` resolving to one

The listener is called only during `draw()`/`predraw()`, never when `setDataListener()` registers it. The element will not call the listener again until the current call has resolved or rejected, and will not render until the Promise settles — a listener that never settles blocks rendering forever.

The listener must report the *full* dimensions of the underlying set (`num_rows`, `num_columns`) even though it returns only a slice; the element sizes its scroll area from them.

## DataResponse Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `data` | `(string\|number\|boolean\|null)[][]` | yes | Columnar slice; `data[x][y]` = y-th row of x-th column of the slice |
| `num_rows` | number | yes | Total rows in the data set |
| `num_columns` | number | yes | Total columns in the data set |
| `column_headers` | `(string\|HTMLElement)[][]` | no | One array per column of the slice (length `x1 - x0`), specificity order |
| `row_headers` | `(string\|HTMLElement)[][]` | no | One array per row of the slice (length `y1 - y0`), specificity order |
| `metadata` | unknown[][] | no | Same shape as `data`; each value surfaces as `meta.user` from `getMeta()` |
| `row_height` | number | no | Pixel height override for virtual scrolling calculations |
| `num_row_headers` | number | no | Row header column count, when headers are not in the slice |
| `num_column_headers` | number | no | Column header row count |
| `column_header_merge_depth` | number | no | How many header rows participate in `colspan` merging (default `header_length - 1`) |
| `merge_headers` | `"both"` \| `"row"` \| `"column"` | no | Header-merging axes; default `"both"` |

Cell values are scalars (`string | number | boolean | null`); header entries may also be `HTMLElement` instances, which are rendered directly.

## Columnar Orientation

`data` is **column-major**. For a viewport from `(0, 0)` to `(2, 2)` of this data set:

```javascript
const DATA = [
  [0, 1, 2],           // column 0, 3 rows
  ["A", "B", "C"],     // column 1
  [true, false, true], // column 2
];
```

the listener returns:

```javascript
{
  num_rows: 3,
  num_columns: 3,
  data: DATA.slice(x0, x1).map((col) => col.slice(y0, y1)),
}
```

`data[0]` is the first column's slice; `data[0][1]` is that column's second row. If you keep row-major data, transpose before slicing.

## Async Data Models

Any Promise-returning source works — Web Worker, `fetch()`, Web Sockets, `readFile()`. The element blocks rendering until the Promise settles.

Web Worker pattern (from the README):

```javascript
// Browser
let callback;
worker.addEventListener("message", (event) => callback(event.data));

table.setDataListener((...viewport) => {
  return new Promise(function (resolve) {
    callback = resolve;
    worker.postMessage(viewport);
  });
});

// Web Worker
self.addEventListener("message", async (event) => {
  const response = await getDataSlice.apply(null, event.data);
  self.postMessage(response);
});
```

For a remote backend, the protocol is just `(x0, y0, x1, y1)` in, `DataResponse` JSON out — re-implementable in any language.

## setDataListener Options

```javascript
table.setDataListener(listener, {
  virtual_mode: "both",   // "both" | "vertical" | "horizontal" | "none"
  preserve_state: false,  // swap only the listener, keep scroll/sizing state
  column_classes: false,  // tag every leaf header and body cell rt-col-{size_key}
});
```

- `virtual_mode` — which axes to virtualize. Any mode other than `"both"` renders the entire table along the non-virtual axis (see [05-scrolling](05-scrolling.md)).
- `preserve_state` — when `setDataListener()` has already been called, this flag prevents internal state from being reset (other than the callback itself). Must not be combined with a `virtual_mode` change (console assert).
- `column_classes` — every rendered leaf header and body cell carries a stable `rt-col-{size_key}` class identifying its logical column, so your own stylesheet can apply column-scoped declarations (`text-align`, `color`, …) that follow the column as the table scrolls. Off by default; without it, only cells regular-table's own column sizing requires carry the class.

## The Two-Billion-Rows Pattern

The canonical way to serve an enormous set without materializing it — generate the slice on the fly (adapted from `examples/two_billion_rows`, which renders `NUM_ROWS = 2000000000`, `NUM_COLUMNS = 1000`):

```javascript
function dataListener(num_rows, num_columns) {
  return (x0, y0, x1, y1) => ({
    num_rows,
    num_columns,
    row_headers: range(y0, y1, (y) => [`Group ${clamp(y, 10)}`, `Row ${y}`]),
    column_headers: range(x0, x1, (x) => [`Group ${clamp(x, 10)}`, `Column ${x}`]),
    data: range(x0, x1, (x) => range(y0, y1, (y) => x + y)),
  });
}

function range(x0, x1, f) {
  return Array.from({ length: x1 - x0 }, (_, i) => f(x0 + i));
}

const clamp = (x, y) => Math.floor(x / y) * y;
```

It works because the listener returns static dimensions and computes cells lazily — the data set never exists in memory as a whole.

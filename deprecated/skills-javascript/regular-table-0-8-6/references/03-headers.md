# Headers

regular-table supports column headers (`<thead>`), row headers (`<th>` in `<tbody>`), and hierarchical group headers with automatic `colspan`/`rowspan` merging.

## Column Headers

Column headers appear in the `<thead>` and are provided via the `column_headers` field in `DataResponse`. The array must have exactly `x1 - x0` entries (one per column in the viewport).

```javascript
table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: 100,
  num_columns: 5,
  data: /* ... */,
  column_headers: [
    ["Name"],
    ["Age"],
    ["City"],
    ["Score"],
    ["Status"],
  ].slice(x0, x1),
}));
```

Each entry is an array representing the header hierarchy levels. A single-element array produces one `<th>` per column.

## Row Headers

Row headers appear as the first `<th>` in each `<tr>` within `<tbody>`. Provided via `row_headers`:

```javascript
table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: 100,
  num_columns: 5,
  data: /* ... */,
  row_headers: Array.from({ length: y1 - y0 }, (_, i) => [`Row ${y0 + i}`]),
}));
```

## Hierarchical Group Headers

Multi-level headers use arrays with multiple elements. Consecutive duplicate values are automatically merged via `colspan`/`rowspan`.

```javascript
column_headers: [
  ["Group A", "Col 1"],
  ["Group A", "Col 2"],
  ["Group B", "Col 3"],
  ["Group B", "Col 4"],
  ["Group C", "Col 5"],
].slice(x0, x1),
```

This renders as:

```html
<thead>
  <tr>
    <th colspan="2">Group A</th>
    <th colspan="2">Group B</th>
    <th>Group C</th>
  </tr>
  <tr>
    <th>Col 1</th>
    <th>Col 2</th>
    <th>Col 3</th>
    <th>Col 4</th>
    <th>Col 5</th>
  </tr>
</thead>
```

### Row Group Headers

```javascript
row_headers: [
  ["Section 1", "Item A"],
  ["Section 1", "Item B"],
  ["Section 2", "Item C"],
  ["Section 2", "Item D"],
].slice(y0, y1),
```

 Renders with `rowspan` for the group level:

```html
<tbody>
  <tr>
    <th rowspan="2">Section 1</th>
    <th>Item A</th>
    <td>...</td>
  </tr>
  <tr>
    <th>Item B</th>
    <td>...</td>
  </tr>
  <!-- ... -->
</tbody>
```

## merge_headers Option

Control automatic merging of consecutive duplicate headers:

```javascript
{
  merge_headers: "both",    // default: merge both column and row headers
  merge_headers: "column",  // only merge column headers
  merge_headers: "row",     // only merge row headers
  merge_headers: "none",    // no merging, every header gets its own <th>
}
```

When `merge_headers: "none"`, each header level gets its own `<th>` without `colspan`/`rowspan`:

```html
<thead>
  <tr>
    <th>Group A</th>
    <th>Group A</th>
    <th>Group B</th>
    <th>Group B</th>
  </tr>
  <tr>
    <th>Col 1</th>
    <th>Col 2</th>
    <th>Col 3</th>
    <th>Col 4</th>
  </tr>
</thead>
```

## column_header_merge_depth

Limit how many rows participate in `colspan` merging:

```javascript
{
  column_header_merge_depth: 1,  // only merge the top row
}
```

Default is `header_length - 1` (merge all levels).

## Corner Headers

When both column and row headers are present, the intersection area (top-left corner) is rendered with corner cells. These show the row header group labels in the fixed corner area.

## Header with HTMLElement Values

Headers can contain `HTMLElement` instances for rich content:

```javascript
column_headers: [
  [document.createElement("strong")],  // renders <th><strong>...</strong></th>
  ["Plain Text"],
],
```

## Dynamic Headers

Headers are fetched per-viewport, so they can be computed dynamically:

```javascript
table.setDataListener((x0, y0, x1, y1) => {
  const columnNames = getColumnNames(x0, x1);
  const groupNames = getGroupNames(x0, x1);

  return {
    num_rows: 1000,
    num_columns: 100,
    data: /* ... */,
    column_headers: columnNames.map((name, i) => [groupNames[i], name]),
  };
});
```

## Styling Headers

Use `addStyleListener()` with `querySelectorAll("th")` for data-aware header styling:

```javascript
table.addStyleListener(() => {
  for (const th of table.querySelectorAll("thead th")) {
    const meta = table.getMeta(th);
    if (meta) {
      th.style.cursor = "pointer";
      th.title = `Click to sort by ${meta.value}`;
    }
  }
});
```

Target row headers specifically:

```javascript
table.addStyleListener(() => {
  for (const th of table.querySelectorAll("tbody th")) {
    const meta = table.getMeta(th);
    if (meta) {
      th.style.fontWeight = "bold";
      th.style.background = "#f5f5f5";
    }
  }
});
```

## Gotchas

- **Header array length must match viewport** — `column_headers` must have exactly `x1 - x0` entries. `row_headers` must have exactly `y1 - y0` entries. Mismatched lengths cause rendering errors.
- **Headers are fetched per viewport** — unlike static tables, headers are requested for each visible region. Ensure your header generation is consistent across viewport boundaries.
- **Auto-merge only applies to consecutive duplicates** — non-adjacent identical values are not merged. The merge algorithm checks each pair of adjacent cells.
- **Corner cells have `type: "corner"` in `getMeta()`** — when querying metadata for corner header cells, check `meta.type === "corner"` to distinguish them from regular headers.

# Headers

regular-table renders column headers in a `<thead>` and row headers as `<th>` elements at the start of each `<tbody><tr>`. Both accept multi-level (hierarchical) arrays and merge consecutive equal values automatically.

## Single-Level Headers

```javascript
table.setDataListener((x0, y0, x1, y1) => ({
  num_rows: 26,
  num_columns: 3,
  data: /* slice */,
  column_headers: [["Column 1 (number)"], ["Column 2 (string)"]],
  row_headers: [["Row 1"], ["Row 2"]],
}));
```

- Omitting `column_headers` means no `<thead>` is generated at all.
- Omitting `row_headers` means no `<th>` inside `<tbody>` rows.
- `column_headers` must contain exactly `x1 - x0` entries (one per column of the current data window) and `row_headers` exactly `y1 - y0`.

## Hierarchical (Group) Headers

Each entry is an array in **specificity order** (outermost group first). Multiple `<tr>` of `<th>` are emitted, and repeated elements in a sequence are merged via `rowspan`/`colspan`, so a group name renders to a single `<th>`:

```javascript
column_headers: [
  ["Colgroup 1", "Column 1"],
  ["Colgroup 1", "Column 2"],
  ["Colgroup 2", "Column 3"],
],
row_headers: [
  ["Rowgroup 1", "Row 1"],
  ["Rowgroup 1", "Row 2"],
],
```

renders `Colgroup 1` once with `colspan="2"` above `Column 1`/`Column 2`, and `Rowgroup 1` once with `rowspan="2"` beside `Row 1`/`Row 2`.

## merge_headers

Controls which axes merge equivalent contiguous `<th>` elements (DataResponse field, default `"both"`):

| Value | Row headers | Column headers |
|---|---|---|
| `"both"` (default) | merged via `rowspan` | merged via `colspan` |
| `"row"` | merged | not merged |
| `"column"` | not merged | merged |

There is no `"none"` in the 0.9.2 type (`"both" | "row" | "column"`), even though the README lists one — there is no single option to disable merging on both axes at once.

## column_header_merge_depth

`column_header_merge_depth: number` configures how many rows are included from `colspan` merging; it defaults to `header_length - 1`. Use it to control which header level participates in the merge.

## Group Corner

Where merged column and row header regions intersect, the element produces a corner cell tagged with the `rt-group-corner` class (the sub-cell scrolling CSS excludes these from the horizontal transform).

## Tree-like Row Headers (file browser pattern)

Group-like row headers repeat the parent name in every child row; merging keeps the full path in view, but each directory level claims its own minimum-width column, so deeply asymmetric trees yield wide row headers. For a conventional file-tree look, replace consecutive duplicates with `""`:

```javascript
// group-like — full path always visible
[["Dir_1"], ["Dir_1", "Dir_2"], ["Dir_1", "Dir_2", "File_1"], ["Dir_1", "File_2"]]

// tree-like — one long th per row; empty cells collapse into it
[["Dir_1"], ["", "Dir_2"], ["", "", "File_1"], ["", "File_2"]]
```

regular-table merges consecutive equal `<th>` content, preferring `rowspan` to `colspan` (inserting empty `<th>` when necessary to fill gaps, since table cells cannot overlap). When a `<th>` lacks a `rowspan`, trailing `undefined`/empty values are merged via `colspan` into one long `<th>` per row header group. In the tree-like layout no content exclusively occupies any but the last `row_headers` column, so size the empty columns via CSS to shape trees of any geometry.

The `file_browser` example builds on this: `DATA` is a row-oriented array of `{path, row, is_open}` records where `path` is built with `Array(n).fill("").concat([name])`; opening/closing a directory splices `DATA` and re-draws.

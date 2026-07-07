# Utility Functions

## Data Input — Creating Worksheets

### `aoa_to_sheet(data, opts?)`

Convert array-of-arrays to a worksheet:

```js
const ws = XLSX.utils.aoa_to_sheet([
  ["Name", "Age", "City"],
  ["Alice", 30, "NYC"],
  ["Bob", 25, "LA"]
]);
```

Options: `dateNF`, `cellDates`, `sheetStubs`, `nullError`, `UTC`, `dense`.

Values are auto-typed: numbers → `"n"`, booleans → `"b"`, strings → `"s"`, Date objects → `"d"` or `"n"`. Array holes and `undefined` are skipped. `null` can be stubbed or become `#NULL!` errors.

Cell objects can be passed directly:

```js
const ws = XLSX.utils.aoa_to_sheet([
  ["Name", "Value"],
  ["Total", { t: "n", v: 42, f: "SUM(B1:B10)" }]
]);
```

### `json_to_sheet(data, opts?)`

Convert array-of-objects to a worksheet:

```js
const ws = XLSX.utils.json_to_sheet([
  { name: "Alice", age: 30, city: "NYC" },
  { name: "Bob", age: 25, city: "LA" }
]);
```

Options: `header` (column order array), `dateNF`, `cellDates`, `skipHeader`, `nullError`, `UTC`, `dense`.

First row is auto-generated from keys. Use `header` array to control column order.

### `table_to_sheet(table, opts?)` / `table_to_book(table, opts?)`

Convert HTML TABLE DOM element to worksheet/workbook (browser only):

```js
const table = document.getElementById("myTable");
const ws = XLSX.utils.table_to_sheet(table);
const wb = XLSX.utils.table_to_book(table);
```

Options: `raw`, `dateNF`, `cellDates`, `sheetRows`, `display`, `UTC`.

### `sheet_add_aoa(ws, data, opts?)`

Append array-of-arrays to existing worksheet:

```js
XLSX.utils.sheet_add_aoa(ws, [["Total", 100]], { origin: -1 });
```

`origin` options: `"A1"` (string), `{r: 0, c: 0}` (cell address), `0` (row index), `-1` (append at end).

### `sheet_add_json(ws, data, opts?)`

Append array-of-objects to existing worksheet:

```js
XLSX.utils.sheet_add_json(ws, [{ name: "Charlie", age: 35 }], {
  origin: -1,
  skipHeader: true
});
```

### `sheet_add_dom(ws, table, opts?)`

Append HTML TABLE data to existing worksheet:

```js
const table = document.getElementById("table2");
XLSX.utils.sheet_add_dom(ws, table, { origin: -1 });
```

## Data Output — Extracting from Worksheets

### `sheet_to_json(ws, opts?)`

Convert worksheet to array of objects:

```js
const data = XLSX.utils.sheet_to_json(ws);
// [{ Name: "Alice", Age: 30, City: "NYC" }, ...]
```

Options:
- `header: 1` — array-of-arrays instead of objects
- `header: "A"` — column labels as keys
- `header: ["A", "B", "C"]` — custom key names
- `range: "A1:D10"` — limit to range
- `range: 1` — skip first row (start from row 2)
- `raw: true` — raw values (default)
- `blankrows: true` — include blank rows
- `defval: ""` — default for empty cells
- `skipHidden: true` — skip hidden rows/columns
- `UTC: true` — UTC date interpretation

### `sheet_to_csv(ws, opts?)`

Convert worksheet to CSV string:

```js
const csv = XLSX.utils.sheet_to_csv(ws);
```

Options: `FS` (field separator), `RS` (record separator), `strip`, `blankrows`, `skipHidden`, `forceQuotes`, `dateNF`.

### `sheet_to_txt(ws, opts?)`

Convert worksheet to UTF-16 TSV string (tab-separated):

```js
const txt = XLSX.utils.sheet_to_txt(ws);
```

### `sheet_to_html(ws, opts?)`

Convert worksheet to HTML TABLE string:

```js
const html = XLSX.utils.sheet_to_html(ws);
```

Options: `id`, `editable`, `header`, `footer`.

Generated TD elements include `data-t`, `data-v`, `data-z` attributes.

### `sheet_to_formulae(ws, opts?)`

Extract all formulae from a worksheet:

```js
const formulae = XLSX.utils.sheet_to_formulae(ws);
// ["A1=1", "B1=2", "C1=A1+B1", ...]
```

## Cell Manipulation

### `cell_set_number_format(cell, fmt)`

```js
XLSX.utils.cell_set_number_format(ws["B2"], "#,##0.00");
```

### `cell_set_hyperlink(cell, target, tooltip?)`

```js
XLSX.utils.cell_set_hyperlink(ws["A1"], "https://example.com", "Click here");
```

### `cell_set_internal_link(cell, target, tooltip?)`

```js
XLSX.utils.cell_set_internal_link(ws["A1"], "#Sheet2!A1", "Go to Sheet2");
```

### `cell_add_comment(cell, text, author?)`

```js
XLSX.utils.cell_add_comment(ws["A1"], "This is a comment", "Author");
```

### `sheet_set_array_formula(ws, range, formula, dynamic?)`

```js
// Single-cell array formula
XLSX.utils.sheet_set_array_formula(ws, "C1", "SUM(A1:A3*B1:B3)");

// Multi-cell array formula
XLSX.utils.sheet_set_array_formula(ws, "D1:D3", "A1:A3*B1:B3");

// Dynamic array formula
XLSX.utils.sheet_set_array_formula(ws, "C1", "_xlfn.UNIQUE(A1:A10)", true);
```

## Address Utilities

### Cell Addresses

```js
XLSX.utils.encode_cell({ r: 0, c: 0 });   // "A1"
XLSX.utils.decode_cell("A1");              // { r: 0, c: 0 }
XLSX.utils.encode_col(0);                  // "A"
XLSX.utils.decode_col("A");                // 0
XLSX.utils.encode_row(0);                  // "1"
XLSX.utils.decode_row("1");                // 0
```

### Ranges

```js
XLSX.utils.encode_range({ s: { r: 0, c: 0 }, e: { r: 9, c: 3 } }); // "A1:D10"
XLSX.utils.decode_range("A1:D10");                                     // { s: { r: 0, c: 0 }, e: { r: 9, c: 3 } }
```

### Iterating Over Cells

```js
const range = XLSX.utils.decode_range(ws["!ref"]);
const dense = ws["!data"] != null;

for (let R = range.s.r; R <= range.e.r; R++) {
  for (let C = range.s.c; C <= range.e.c; C++) {
    const addr = XLSX.utils.encode_cell({ r: R, c: C });
    const cell = dense ? ws["!data"]?.[R]?.[C] : ws[addr];
    if (cell) {
      console.log(addr, cell.v);
    }
  }
}
```

## Workbook Helpers

### `book_new(ws?, name?)`

```js
const wb = XLSX.utils.book_new();                        // empty workbook
const wb = XLSX.utils.book_new(ws);                      // with one sheet ("Sheet1")
const wb = XLSX.utils.book_new(ws, "Data");              // with named sheet
```

### `book_append_sheet(wb, ws, name, roll?)`

```js
XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
XLSX.utils.book_append_sheet(wb, ws2, "Sheet1", true);  // auto-increment if name exists
```

### `book_set_sheet_visibility(wb, sheet, visibility)`

```js
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 0);  // visible
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 1);  // hidden
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 2);  // very hidden
```

### `format_cell(cell, v?, opts?)`

```js
const text = XLSX.utils.format_cell(ws["B2"]);
```

### `sheet_new(opts?)`

```js
const ws = XLSX.utils.sheet_new();           // empty sparse sheet
const ws = XLSX.utils.sheet_new({ dense: true }); // empty dense sheet
```

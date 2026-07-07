# Utility Functions (`XLSX.utils`)

## Import Functions

### `aoa_to_sheet(data, opts)`

Convert an array of arrays to a worksheet. Each inner array is a row.

```js
const ws = XLSX.utils.aoa_to_sheet([
  ["Name", "Age", "City"],
  ["Alice", 30, "NYC"],
  ["Bob", 25, "LA"]
]);
// A1="Name", B1="Age", C1="City", A2="Alice", etc.
```

Options:
- `origin` — starting cell (default: `"A1"`, or `"{r, c}"` object)
- `sheetStubs` — create stub cells for empty positions (default: `false`)
- `dateNF` — date format string

### `json_to_sheet(data, opts)`

Convert an array of objects to a worksheet. Keys become headers.

```js
const ws = XLSX.utils.json_to_sheet([
  { name: "Alice", age: 30, city: "NYC" },
  { name: "Bob", age: 25, city: "LA" }
]);
// Auto-generates header row: A1="name", B1="age", C1="city"
```

Options:
- `header` — custom column order: `["name", "age", "city"]`
- `skipHeader` — omit the header row (default: `false`)
- `origin` — starting cell
- `dateNF` — date format string

### `table_to_sheet(table, opts)`

Convert an HTML TABLE element to a worksheet. Browser only.

```js
const table = document.getElementById("my-table");
const ws = XLSX.utils.table_to_sheet(table);
```

Options:
- `raw` — don't parse values (default: `false`)
- `sheetRows` — max rows to parse (0 = unlimited)
- `display` — skip hidden rows/cells (default: `false`)
- `origin` — starting cell

### `table_to_book(table, opts)`

Convert an HTML TABLE to a full workbook (single sheet). Browser only.

```js
const wb = XLSX.utils.table_to_book(table, { sheet: "Data" });
```

Options: same as `table_to_sheet` plus `sheet` (worksheet name).

## Export Functions

### `sheet_to_json(ws, opts)`

Convert a worksheet to an array of JS objects or arrays.

```js
// Default: array of objects (first row = keys)
const data = XLSX.utils.sheet_to_json(ws);
// [{ name: "Alice", age: 30 }, { name: "Bob", age: 25 }]

// Array of arrays (includes header row)
const rows = XLSX.utils.sheet_to_json(ws, { header: 1 });
// [["name", "age"], ["Alice", 30], ["Bob", 25]]

// Custom header row (use row A as keys, skip row 1)
const data = XLSX.utils.sheet_to_json(ws, { header: "A" });
```

Options:
- `header` — `"A"` (use row A), `1` (array-of-arrays), or `string[]` (custom keys)
- `range` — limit to a specific range (e.g., `"A1:D10"`)
- `blankrows` — include blank rows (default: `false`)
- `defval` — default value for empty cells
- `raw` — return raw values instead of formatted text (default: `false`)
- `skipHidden` — skip hidden rows/columns
- `dateNF` — date format for output
- `rawNumbers` — return raw numbers vs formatted (default: `true`)

### `sheet_to_csv(ws, opts)`

Generate CSV string from a worksheet.

```js
const csv = XLSX.utils.sheet_to_csv(ws);
```

Options: `FS`, `RS`, `strip`, `blankrows`, `skipHidden`, `forceQuotes`, `dateNF`, `rawNumbers`.

### `sheet_to_html(ws, opts)`

Generate HTML string from a worksheet.

```js
const html = XLSX.utils.sheet_to_html(ws, { id: "data-table", editable: true });
```

Options:
- `id` — TABLE element id attribute
- `editable` — add `contenteditable` to cells
- `header` — header HTML string
- `footer` — footer HTML string

### `sheet_to_formulae(ws)`

Extract all formulae from a worksheet as strings.

```js
const formulae = XLSX.utils.sheet_to_formulae(ws);
// ["A1=SUM(B1:B10)", "C1=A1+B1"]
```

### `sheet_to_txt(ws, opts)`

Generate tab-separated values (UTF-16 formatted text).

### `sheet_to_dif(ws)`, `sheet_to_slk(ws)`, `sheet_to_eth(ws)`

Generate DIF, SYLK, and ETH format strings respectively.

## Append Functions

### `sheet_add_aoa(ws, data, opts)`

Append array-of-arrays to an existing worksheet.

```js
// Append at next empty row
XLSX.utils.sheet_add_aoa(ws, [["Total", 100]], { origin: -1 });

// Append at specific cell
XLSX.utils.sheet_add_aoa(ws, [["New", "Data"]], { origin: "D1" });

// Append at row index
XLSX.utils.sheet_add_aoa(ws, [["New", "Data"]], { origin: { r: 5, c: 0 } });
```

### `sheet_add_json(ws, data, opts)`

Append array-of-objects to an existing worksheet.

```js
XLSX.utils.sheet_add_json(ws, [{ name: "Charlie", age: 35 }], { origin: -1 });
```

Options: `origin`, `header` (column order), `skipHeader`.

## Workbook Functions

### `book_new()`

Create an empty workbook.

```js
const wb = XLSX.utils.book_new();
// { SheetNames: [], Sheets: {} }
```

### `book_append_sheet(wb, ws, name, roll)`

Append a worksheet to a workbook.

```js
XLSX.utils.book_append_sheet(wb, ws, "Data");

// Auto-increment if name exists
const actualName = XLSX.utils.book_append_sheet(wb, ws, "Sheet", true);
// Returns "Sheet1", "Sheet2", etc.
```

### `book_set_sheet_visibility(wb, sheet, visibility)`

Set sheet visibility.

```js
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 0); // visible
XLSX.utils.book_set_sheet_visibility(wb, "Sheet2", 1); // hidden
XLSX.utils.book_set_sheet_visibility(wb, "Sheet3", 2); // very hidden
```

## Cell Manipulation Functions

### `cell_set_number_format(cell, fmt)`

Set a cell's number format.

```js
XLSX.utils.cell_set_number_format(ws["B2"], "#,##0.00");
XLSX.utils.cell_set_number_format(ws["C2"], "yyyy-mm-dd");
XLSX.utils.cell_set_number_format(ws["D2"], "0.00%");
```

### `cell_set_hyperlink(cell, target, tooltip)`

Set a hyperlink on a cell.

```js
XLSX.utils.cell_set_hyperlink(ws["A1"], "https://example.com", "Visit Example");
```

### `cell_set_internal_link(cell, target, tooltip)`

Set an internal (sheet) link.

```js
XLSX.utils.cell_set_internal_link(ws["A1"], "'Sheet2'!A1", "Go to Sheet2");
```

### `cell_add_comment(cell, text, author)`

Add a comment to a cell.

```js
XLSX.utils.cell_add_comment(ws["A1"], "Important note", "Author");
```

### `format_cell(cell, value, opts)`

Get the formatted text for a cell.

```js
const formatted = XLSX.utils.format_cell(ws["B2"]);
```

### `sheet_set_array_formula(ws, range, formula, dynamic)`

Assign an array formula to a range.

```js
XLSX.utils.sheet_set_array_formula(ws, "D1:D10", "SUMPRODUCT(A1:A10,B1:B10)");
```

## Cell Address Utilities

### Encode Functions (0-indexed → A1)

```js
XLSX.utils.encode_cell({ r: 0, c: 0 });  // "A1"
XLSX.utils.encode_cell({ r: 2, c: 1 });  // "B3"
XLSX.utils.encode_row(0);                 // "1"
XLSX.utils.encode_col(0);                 // "A"
XLSX.utils.encode_col(26);                // "AA"
XLSX.utils.encode_range({ r: 0, c: 0 }, { r: 9, c: 3 }); // "A1:D10"
XLSX.utils.encode_range({ s: { r: 0, c: 0 }, e: { r: 9, c: 3 } }); // "A1:D10"
```

### Decode Functions (A1 → 0-indexed)

```js
XLSX.utils.decode_cell("A1");   // { r: 0, c: 0 }
XLSX.utils.decode_cell("B3");   // { r: 2, c: 1 }
XLSX.utils.decode_row("1");     // 0
XLSX.utils.decode_col("A");     // 0
XLSX.utils.decode_col("AA");    // 26
XLSX.utils.decode_range("A1:D10"); // { s: { r: 0, c: 0 }, e: { r: 9, c: 3 } }
```

## Constants

```js
XLSX.utils.consts.SHEET_VISIBLE;     // 0
XLSX.utils.consts.SHEET_HIDDEN;      // 1
XLSX.utils.consts.SHEET_VERYHIDDEN;  // 2
```

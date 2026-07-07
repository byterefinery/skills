---
name: xlsx-js-0-18-5
description: Parse, create, and manipulate Excel/spreadsheet files (XLSX, XLS, CSV, ODS, and more) in JavaScript/Node.js. Use when the user mentions xlsx, sheetjs, excel parsing, spreadsheet manipulation, csv export, xls read, ods conversion, or any task involving reading or writing spreadsheet data with the xlsx npm package (v0.18.5).
metadata:
  tags:
    - spreadsheet
    - excel
    - data-processing
    - javascript
    - file-io
---

# xlsx-js 0.18.5

## Overview

SheetJS (xlsx v0.18.5) is a JavaScript/Node.js library for parsing, creating, and manipulating spreadsheet files. It supports a wide range of formats including XLSX, XLS, XLSB, XLSM, ODS, CSV, TSV, DBF, SYLK, DIF, HTML, RTF, and more. The library works in Node.js, browsers, Deno, Electron, React Native, and Adobe ExtendScript.

The core data model is the **Common Spreadsheet Format (CSF)** — plain JS objects representing workbooks, worksheets, and cells. All operations work on this in-memory representation, making the library framework-agnostic and suitable for Web Workers.

### Core API

| Function | Purpose |
|---|---|
| `XLSX.read(data, opts)` | Parse bytes (Buffer, ArrayBuffer, binary string, base64) into a workbook |
| `XLSX.readFile(filename, opts)` | Read and parse a local file (Node.js/Deno only) |
| `XLSX.write(workbook, opts)` | Serialize workbook to bytes (string, buffer, base64, array) |
| `XLSX.writeFile(workbook, filename, opts)` | Write workbook to a local file (Node.js/Deno only) |
| `XLSX.writeFileAsync(filename, workbook, opts, cb)` | Async file write (Node.js only) |
| `XLSX.writeXLSX(workbook, opts)` | Convenience: write as XLSX format |
| `XLSX.writeFileXLSX(workbook, filename, opts)` | Convenience: write XLSX to file |

### Utility Functions (`XLSX.utils`)

| Function | Purpose |
|---|---|
| `book_new()` | Create an empty workbook |
| `book_append_sheet(wb, ws, name)` | Append a worksheet to a workbook |
| `book_set_sheet_visibility(wb, sheet, visibility)` | Set sheet visibility (0=visible, 1=hidden, 2=very hidden) |
| `aoa_to_sheet(data, opts)` | Convert array-of-arrays to a worksheet |
| `json_to_sheet(data, opts)` | Convert array-of-objects to a worksheet |
| `table_to_sheet(table, opts)` | Convert HTML TABLE element to a worksheet (browser only) |
| `table_to_book(table, opts)` | Convert HTML TABLE to a full workbook (browser only) |
| `sheet_to_json(ws, opts)` | Convert worksheet to array of JS objects |
| `sheet_to_csv(ws, opts)` | Convert worksheet to CSV string |
| `sheet_to_html(ws, opts)` | Convert worksheet to HTML string |
| `sheet_to_formulae(ws)` | Extract all formulae from a worksheet |
| `sheet_add_aoa(ws, data, opts)` | Append array-of-arrays to existing worksheet |
| `sheet_add_json(ws, data, opts)` | Append array-of-objects to existing worksheet |
| `encode_cell({r, c})` / `decode_cell("A1")` | Convert between 0-indexed and A1 addresses |
| `encode_range(s, e)` / `decode_range("A1:B2")` | Convert ranges |
| `format_cell(cell)` | Get formatted text for a cell |
| `cell_set_number_format(cell, fmt)` | Set cell number format |
| `cell_set_hyperlink(cell, target, tooltip)` | Set hyperlink on a cell |
| `cell_add_comment(cell, text, author)` | Add comment to a cell |
| `sheet_set_array_formula(ws, range, formula)` | Assign an array formula to a range |

### Stream Utilities (`XLSX.stream`) — Node.js only

| Function | Purpose |
|---|---|
| `to_csv(sheet, opts)` | Readable stream, one CSV line at a time |
| `to_json(sheet, opts)` | Readable stream, one JSON object at a time |
| `to_html(sheet, opts)` | Readable stream, one HTML line at a time |

### Constants (`XLSX.utils.consts`)

| Constant | Value | Meaning |
|---|---|---|
| `SHEET_VISIBLE` | 0 | Sheet is visible |
| `SHEET_HIDDEN` | 1 | Sheet is hidden (user can unhide) |
| `SHEET_VERYHIDDEN` | 2 | Sheet is very hidden (requires code to unhide) |

### Supported Output Formats (`bookType`)

`xlsx`, `xlsm`, `xlsb`, `xls`, `xla`, `biff8`, `biff5`, `biff2`, `xlml`, `ods`, `fods`, `csv`, `txt`, `sylk`, `slk`, `html`, `dif`, `rtf`, `prn`, `eth`, `dbf`

### Data Model

**Workbook** — `{ Sheets: { [name]: WorkSheet }, SheetNames: string[] }`

**Worksheet** — object keyed by cell addresses (`"A1"`, `"B2"`) with special keys prefixed by `!`:
- `!ref` — range string (e.g., `"A1:D10"`)
- `!cols` — column info array (`[{ wch, wpx, hidden, level }]`)
- `!rows` — row info array (`[{ hpx, hpt, hidden, level }]`)
- `!merges` — merge ranges (`[{ s: {r, c}, e: {r, c} }]`)
- `!protect` — sheet protection info
- `!autofilter` — autofilter range
- `!margins` — page margins

**Cell** (`CellObject`) — `{ v, w, t, f, F, r, h, c, z, l, s }`:
- `v` — raw value (string, number, boolean, Date)
- `w` — formatted text
- `t` — data type: `"b"` (boolean), `"n"` (number), `"e"` (error), `"s"` (string), `"d"` (date), `"z"` (stub)
- `f` — cell formula
- `F` — array formula range
- `h` — HTML rendering of rich text
- `c` — comments array
- `z` — number format string
- `l` — hyperlink (`{ Target, Tooltip }`)
- `s` — style/theme info

## Usage

### Installation

```bash
npm install xlsx@0.18.5
```

### CommonJS (default)

```js
const XLSX = require("xlsx");
```

### ESM (Node.js)

```js
import { read, writeFile, utils } from "xlsx/xlsx.mjs";
import * as fs from "fs";
readFile(fs.readFileSync("file.xlsx"));
// Enable readFile/writeFile helpers:
import { set_fs } from "xlsx/xlsx.mjs";
set_fs(fs);
```

### Browser (standalone script)

```html
<script src="https://unpkg.com/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
<!-- XLSX is available as a global -->
```

### Browser (ESM)

```html
<script type="module">
  import { read, utils } from "https://unpkg.com/xlsx@0.18.5/xlsx.mjs";
</script>
```

### CDN Options

- unpkg: `https://unpkg.com/xlsx@0.18.5/dist/xlsx.full.min.js`
- jsDelivr: `https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js`
- CDNjs: `https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js`

### Reading Files

```js
// Node.js — direct file read
const workbook = XLSX.readFile("data.xlsx");

// Node.js — ESM
import { read } from "xlsx/xlsx.mjs";
import { readFileSync } from "fs";
const workbook = read(readFileSync("data.xlsx"));

// Browser — file input
const reader = new FileReader();
reader.onload = (e) => {
  const workbook = XLSX.read(e.target.result);
};
reader.readAsArrayBuffer(file);

// Browser — fetch
const data = await (await fetch(url)).arrayBuffer();
const workbook = XLSX.read(data);

// Base64 string
const workbook = XLSX.read(base64String, { type: "base64" });
```

### Writing Files

```js
// Write to file (Node.js)
XLSX.writeFile(workbook, "output.xlsx");
XLSX.writeFile(workbook, "output.csv", { bookType: "csv" });

// Write to buffer/string
const buffer = XLSX.write(workbook, { type: "buffer", bookType: "xlsx" });
const base64 = XLSX.write(workbook, { type: "base64", bookType: "xlsx" });

// Browser — download
const buffer = XLSX.write(workbook, { type: "array", bookType: "xlsx" });
const blob = new Blob([buffer], { type: "application/octet-stream" });
URL.createObjectURL(blob);
```

### Creating Workbooks from JS Data

```js
// Array of arrays
const ws = XLSX.utils.aoa_to_sheet([
  ["Name", "Age", "City"],
  ["Alice", 30, "NYC"],
  ["Bob", 25, "LA"]
]);

// Array of objects (auto-headers from keys)
const ws = XLSX.utils.json_to_sheet([
  { name: "Alice", age: 30, city: "NYC" },
  { name: "Bob", age: 25, city: "LA" }
]);

// Build workbook
const wb = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(wb, ws, "Data");
XLSX.writeFile(wb, "output.xlsx");
```

### Reading Data from Workbooks

```js
const wb = XLSX.readFile("data.xlsx");

// Get first sheet
const ws = wb.Sheets[wb.SheetNames[0]];

// Convert to array of objects
const data = XLSX.utils.sheet_to_json(ws);

// Convert to array of arrays
const rows = XLSX.utils.sheet_to_json(ws, { header: 1 });

// To CSV string
const csv = XLSX.utils.sheet_to_csv(ws);

// Access individual cells
const cell = ws["A1"]; // { v: "Name", t: "s", ... }
```

### Modifying Worksheets

```js
const wb = XLSX.readFile("data.xlsx");
const ws = wb.Sheets["Sheet1"];

// Set column widths
ws["!cols"] = [{ wch: 20 }, { wch: 10 }, { wch: 15 }];

// Add rows
XLSX.utils.sheet_add_aoa(ws, [["Total", 100, "Summary"]], { origin: -1 });

// Merge cells
ws["!merges"] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: 2 } }];

// Set cell hyperlink
XLSX.utils.cell_set_hyperlink(ws["A1"], "https://example.com", "Click here");

// Set number format
XLSX.utils.cell_set_number_format(ws["B2"], "#,##0.00");

// Add comment
XLSX.utils.cell_add_comment(ws["A1"], "This is a comment", "Author");

// Set autofilter
ws["!autofilter"] = { ref: "A1:C10" };

// Set sheet protection
ws["!protect"] = { password: "secret", selectLockedCells: true };

// Set sheet visibility
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 1); // hidden

// Rename sheet
wb.Sheets["New Name"] = ws;
delete wb.Sheets["Old Name"];
wb.SheetNames = wb.SheetNames.map(n => n === "Old Name" ? "New Name" : n);

XLSX.writeFile(wb, "modified.xlsx");
```

### Parsing Options

```js
const wb = XLSX.readFile("data.xlsx", {
  cellDates: true,      // store dates as Date objects (type "d") instead of numbers
  cellFormula: true,    // keep formulae in .f field (default: true)
  cellHTML: true,       // parse rich text to .h field (default: true)
  cellNF: true,         // save number format to .z field (default: false)
  cellStyles: true,     // save style info to .s field (default: false)
  cellText: true,       // generate formatted text in .w field (default: true)
  dateNF: "yyyy-mm-dd", // override default date format
  bookDeps: true,       // parse calculation chains (default: false)
  bookProps: true,      // only parse workbook metadata (default: false)
  bookSheets: true,     // only parse sheet names (default: false)
  sheets: [0, 2],       // only parse specific sheets by index or name
  sheetStubs: true,     // create cell objects for stub cells (default: false)
  WTF: true,            // throw on unsupported features (default: false)
  password: "pass",     // password for encrypted files
  codepage: 1252,       // default codepage for legacy formats
});
```

### Writing Options

```js
XLSX.writeFile(wb, "output.xlsx", {
  bookType: "xlsx",     // output format (default: "xlsx")
  bookSST: false,       // use Shared String Table (default: false)
  compression: true,    // enable ZIP compression (default: false)
  ignoreEC: true,       // suppress "number stored as text" warnings (default: true)
  cellDates: true,      // write native dates instead of date codes
  cellStyles: true,     // export style info
  Props: { Title: "Report", Author: "Me" }, // override workbook properties
  sheet: "Sheet1",      // specify sheet for single-sheet formats
});
```

### `sheet_to_json` Options

```js
XLSX.utils.sheet_to_json(ws, {
  header: "A",     // use row A as header (or 1 for array-of-arrays, or string[] for custom)
  range: "A1:D10", // limit to specific range
  blankrows: true,  // include blank rows (default: false)
  defval: null,     // default value for empty cells
  raw: true,        // return raw values instead of formatted text (default: false)
  skipHidden: true, // skip hidden rows and columns
  dateNF: "yyyy-mm-dd", // date format for output
});
```

### `sheet_to_csv` Options

```js
XLSX.utils.sheet_to_csv(ws, {
  FS: ",",       // field separator (default: ",")
  RS: "\r\n",    // record separator (default: "\r\n")
  strip: true,   // remove trailing field separators
  blankrows: true, // include blank lines
  skipHidden: true, // skip hidden rows/columns
  forceQuotes: true, // force quotes around all fields
  dateNF: "yyyy-mm-dd",
});
```

## Gotchas

- **`readFile` / `writeFile` are Node.js-only** — they rely on `fs`. In ESM mode, `readFile` is not available by default; use `fs.readFileSync` + `XLSX.read()` instead, or call `set_fs(fs)` to enable it. In the browser, always use `XLSX.read()` with ArrayBuffer/binary data.
- **Dates are numbers by default** — Excel stores dates as serial numbers. Use `cellDates: true` in read options to get actual `Date` objects. Without it, dates appear as numbers (e.g., `44927`).
- **`sheet_to_json` with `header: 1` returns array-of-arrays** — the default behavior (no header option) returns array-of-objects using the first row as keys. Use `header: 1` for raw row data including headers.
- **`!ref` is required for writing** — if you create a worksheet manually without using `aoa_to_sheet` or `json_to_sheet`, you must set `ws["!ref"]` (e.g., `"A1:D10"`) or the writer won't know the sheet bounds.
- **Sheet names must be unique and ≤31 chars** — Excel enforces this. `book_append_sheet` throws if the name already exists. Use the 4th argument (`true`) to auto-increment: `book_append_sheet(wb, ws, "Sheet", true)`.
- **Rich text and styling are limited in CE** — the Community Edition has read support for some styling but write support is minimal. For full style/theme/image support, SheetJS Pro is required.
- **Formulae are stored but not evaluated** — the CE preserves formula strings in `.f` but does not calculate results. The computed value is stored in `.v`.
- **`set_cptable` is needed for legacy formats** — to read old XLS files with non-UTF encodings, load the codepage library: `import * as cptable from 'xlsx/dist/cpexcel.full.mjs'; XLSX.set_cptable(cptable);`
- **`set_fs` is needed for ESM file I/O** — in ESM, `readFile`/`writeFile` are stubs until you call `set_fs(fs)`. The `read`/`write` functions work without it.
- **`stream.set_readable(Readable)` for streaming** — to use `XLSX.stream` utilities in Node.js ESM, import `Readable` from `stream` and register it.
- **Cell type `"z"` means stub/empty** — stub cells are placeholder cells in merged ranges. They have `t: "z"` and no value. Use `sheetStubs: false` (default) to skip them during parsing.
- **`origin: -1` appends at the end** — when using `sheet_add_aoa` or `sheet_add_json`, `{ origin: -1 }` automatically finds the next empty row. `{ origin: "A1" }` starts at a specific cell.
- **Browser builds differ** — `xlsx.full.min.js` includes everything; `xlsx.core.min.js` omits the codepage library (no XLS encoding support); `xlsx.mini.min.js` is the smallest (no XLSB/XLS/Numbers/SpreadsheetML).
- **`bookType: "xlsb"` is the most compact binary format** — for large files, XLSB is significantly smaller than XLSX and faster to parse.
- **Merged cells only store value in top-left cell** — the other cells in a merge range are stubs. To get the value, check the top-left cell of the merge range.

## References

- [01-parsing-reading](references/01-parsing-reading.md) — Detailed guide to reading/parsing workbooks from various input sources
- [02-writing-exporting](references/02-writing-exporting.md) — Writing workbooks, output formats, and browser download patterns
- [03-data-model](references/03-data-model.md) — Common Spreadsheet Format: workbook, worksheet, and cell objects in detail
- [04-utility-functions](references/04-utility-functions.md) — Complete reference for `XLSX.utils` conversion and manipulation functions
- [05-parsing-writing-options](references/05-parsing-writing-options.md) — Full reference for read/write option objects
- [06-cell-addresses](references/06-cell-addresses.md) — Cell address encoding/decoding, ranges, and coordinate utilities
- [07-browser-integration](references/07-browser-integration.md) — File input, drag-and-drop, fetch, and download patterns for web apps
- [08-advanced-topics](references/08-advanced-topics.md) — Merged cells, hyperlinks, comments, protection, autofilter, column/row properties

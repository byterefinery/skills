---
name: sheetjs-0-20-3
description: Parse, create, and manipulate spreadsheet files (XLSX, XLS, XLSB, ODS, CSV, DBF, SYLK, HTML, and more) in JavaScript/Node.js/Deno/Bun. Use when the user mentions xlsx, sheetjs, excel parsing, spreadsheet manipulation, csv export, xls read, ods conversion, or any task involving reading or writing spreadsheet data with the xlsx npm package (v0.20.3).
metadata:
  tags:
    - spreadsheet
    - excel
    - data-processing
    - javascript
    - file-io
---

# sheetjs 0.20.3

## Overview

SheetJS (xlsx v0.20.3) is a JavaScript library for parsing, creating, and manipulating spreadsheet files. It supports XLSX, XLS, XLSB, XLSM, ODS, CSV, TSV, DBF, SYLK, DIF, HTML, RTF, NUMBERS, and more. Works in Node.js, browsers, Deno, Bun, Electron, React Native, and Adobe ExtendScript.

The core data model is the **Common Spreadsheet Format (CSF)** — plain JS objects representing workbooks, worksheets, and cells. All operations work on this in-memory representation, making the library framework-agnostic and suitable for Web Workers.

### Core API

| Function | Purpose |
|---|---|
| `XLSX.read(data, opts)` | Parse bytes (Buffer, ArrayBuffer, binary string, base64) into a workbook |
| `XLSX.readFile(filename, opts)` | Read and parse a local file (Node.js/Deno/Bun only) |
| `XLSX.write(workbook, opts)` | Serialize workbook to bytes (string, buffer, base64, array) |
| `XLSX.writeFile(workbook, filename, opts)` | Write workbook to a local file (Node.js/Deno/Bun only) |
| `XLSX.writeFileAsync(filename, workbook, opts, cb)` | Async file write (Node.js only, callback) |
| `XLSX.writeXLSX(workbook, opts)` | Convenience: write as XLSX format only |
| `XLSX.writeFileXLSX(workbook, filename, opts)` | Convenience: write XLSX to file |

### Utility Functions (`XLSX.utils`)

| Function | Purpose |
|---|---|
| `book_new(ws?, name?)` | Create a new workbook (optionally with one sheet) |
| `book_append_sheet(wb, ws, name, roll?)` | Append a worksheet to a workbook |
| `book_set_sheet_visibility(wb, sheet, visibility)` | Set sheet visibility (0=visible, 1=hidden, 2=very hidden) |
| `aoa_to_sheet(data, opts)` | Convert array-of-arrays to a worksheet |
| `json_to_sheet(data, opts)` | Convert array-of-objects to a worksheet |
| `table_to_sheet(table, opts)` | Convert HTML TABLE element to a worksheet (browser only) |
| `table_to_book(table, opts)` | Convert HTML TABLE to a full workbook (browser only) |
| `sheet_add_aoa(ws, data, opts)` | Append array-of-arrays to existing worksheet |
| `sheet_add_json(ws, data, opts)` | Append array-of-objects to existing worksheet |
| `sheet_add_dom(ws, table, opts)` | Append HTML TABLE data to existing worksheet |
| `sheet_to_json(ws, opts)` | Convert worksheet to array of JS objects |
| `sheet_to_csv(ws, opts)` | Convert worksheet to CSV string |
| `sheet_to_txt(ws, opts)` | Convert worksheet to UTF-16 TSV string |
| `sheet_to_html(ws, opts)` | Convert worksheet to HTML string |
| `sheet_to_formulae(ws, opts)` | Extract all formulae from a worksheet |
| `sheet_set_array_formula(ws, range, formula, dynamic?)` | Assign an array formula to a range |
| `encode_cell({r, c})` / `decode_cell("A1")` | Convert between 0-indexed and A1 addresses |
| `encode_col(n)` / `decode_col("A")` | Convert between 0-indexed and A1 column labels |
| `encode_row(n)` / `decode_row("1")` | Convert between 0-indexed and A1 row labels |
| `encode_range(r)` / `decode_range("A1:B2")` | Convert ranges |
| `format_cell(cell)` | Get formatted text for a cell |
| `cell_set_number_format(cell, fmt)` | Set cell number format |
| `cell_set_hyperlink(cell, target, tooltip)` | Set hyperlink on a cell |
| `cell_set_internal_link(cell, target, tooltip)` | Set internal (same-workbook) link |
| `cell_add_comment(cell, text, author)` | Add comment to a cell |

### Stream Utilities (`XLSX.stream`) — Node.js only

| Function | Purpose |
|---|---|
| `to_csv(sheet, opts)` | Node.js Readable stream, one CSV line at a time |
| `to_json(sheet, opts)` | Node.js Readable stream, one JSON object at a time |
| `to_html(sheet, opts)` | Node.js Readable stream, one HTML line at a time |
| `to_xlml(workbook, opts)` | Node.js Readable stream for XLML (new in 0.20.3) |
| `set_readable(Readable)` | Register Readable class (required in ESM) |

### Constants (`XLSX.utils.consts`)

| Constant | Value | Meaning |
|---|---|---|
| `SHEET_VISIBLE` | 0 | Sheet is visible |
| `SHEET_HIDDEN` | 1 | Sheet is hidden (user can unhide) |
| `SHEET_VERYHIDDEN` | 2 | Sheet is very hidden (requires code to unhide) |

### Supported Output Formats (`bookType`)

`xlsx`, `xlsm`, `xlsb`, `xls`, `xla`, `biff8`, `biff5`, `biff4`, `biff3`, `biff2`, `xlml`, `ods`, `fods`, `csv`, `txt`, `sylk`, `slk`, `html`, `dif`, `rtf`, `prn`, `eth`, `dbf`, `numbers`, `wk1`, `wk3`

### Data Model

**Workbook** — `{ Sheets: { [name]: WorkSheet }, SheetNames: string[], Props?, Custprops?, Workbook?, vbaraw?, bookType? }`

**Worksheet** — object keyed by cell addresses (`"A1"`, `"B2"`) with special keys prefixed by `!`:
- `!ref` — range string (e.g., `"A1:D10"`)
- `!data` — dense-mode: `CellObject[][]` array of arrays
- `!cols` — column info array (`[{ wch, wpx, width, hidden, level, MDW }]`)
- `!rows` — row info array (`[{ hpx, hpt, hidden, level }]`)
- `!merges` — merge ranges (`[{ s: {r, c}, e: {r, c} }]`)
- `!protect` — sheet protection info
- `!autofilter` — autofilter range (`{ ref: "A1:C10" }`)
- `!margins` — page margins
- `!outline` — outline behavior (`{ above, left }`)
- `!type` — sheet type (`"sheet"`, `"chart"`, `"macro"`, `"dialog"`)

**Cell** (`CellObject`) — `{ v, w, t, f, F, D, r, h, c, z, l, s }`:
- `v` — raw value (string, number, boolean, Date)
- `w` — formatted text
- `t` — data type: `"b"` (boolean), `"n"` (number), `"e"` (error), `"s"` (string), `"d"` (date), `"z"` (stub)
- `f` — cell formula (A1-style, no leading `=`)
- `F` — array formula range
- `D` — if true, dynamic array formula
- `r` — rich text encoding
- `h` — HTML rendering of rich text
- `c` — comments array (`[{ a, t, T? }]`) with optional `hidden` property
- `z` — number format string
- `l` — hyperlink (`{ Target, Tooltip? }`)
- `s` — style/theme info

## Usage

### Installation

```bash
npm install xlsx@0.20.3
```

### CommonJS (default)

```js
const XLSX = require("xlsx");
```

### ESM (Node.js)

```js
import * as XLSX from "xlsx";
// Or named imports:
import { read, writeFile, utils, stream } from "xlsx";
```

### Browser (standalone script)

```html
<script src="https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js"></script>
<!-- XLSX is available as a global -->
```

### Browser (ESM)

```html
<script type="module">
  import * as XLSX from "https://cdn.sheetjs.com/xlsx-0.20.3/package/xlsx.mjs";
</script>
```

### Deno

```ts
import * as XLSX from "https://cdn.sheetjs.com/xlsx-0.20.3/package/xlsx.mjs";
```

### Bun

```js
import * as XLSX from "xlsx";
import * as fs from "fs";
XLSX.set_fs(fs);
```

### CDN URLs

- Full build: `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js`
- ESM module: `https://cdn.sheetjs.com/xlsx-0.20.3/package/xlsx.mjs`
- Core (no codepage): `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.core.min.js`
- Mini (smallest): `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.mini.min.js`

### Reading Files

```js
// Node.js — direct file read
const workbook = XLSX.readFile("data.xlsx");

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

// Node.js — Buffer
import { readFileSync } from "fs";
const workbook = XLSX.read(readFileSync("data.xlsx"));
```

### Writing Files

```js
// Write to file (Node.js/Deno/Bun)
XLSX.writeFile(workbook, "output.xlsx");
XLSX.writeFile(workbook, "output.csv", { bookType: "csv" });

// Write to buffer/string
const buffer = XLSX.write(workbook, { type: "buffer", bookType: "xlsx" });
const base64 = XLSX.write(workbook, { type: "base64", bookType: "xlsx" });

// Browser — download via Blob
const buffer = XLSX.write(workbook, { type: "array", bookType: "xlsx" });
const blob = new Blob([buffer], { type: "application/octet-stream" });
const url = URL.createObjectURL(blob);
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

// Access individual cells (sparse mode)
const cell = ws["A1"]; // { v: "Name", t: "s", ... }

// Access individual cells (dense mode)
const cell = ws["!data"][0][0];
```

### Modifying Worksheets

```js
const wb = XLSX.readFile("data.xlsx");
const ws = wb.Sheets["Sheet1"];

// Set column widths
ws["!cols"] = [{ wch: 20 }, { wch: 10 }, { wch: 15 }];

// Set row heights
ws["!rows"] = [];
ws["!rows"][0] = { hpx: 30 }; // first row, 30px

// Add rows at the end
XLSX.utils.sheet_add_aoa(ws, [["Total", 100, "Summary"]], { origin: -1 });

// Merge cells
ws["!merges"] = [XLSX.utils.decode_range("A1:C1")];

// Set cell hyperlink
ws["A1"].l = { Target: "https://example.com", Tooltip: "Click here" };

// Set number format
ws["B2"].z = "#,##0.00";

// Add comment
if(!ws["A1"].c) ws["A1"].c = [];
ws["A1"].c.push({ a: "Author", t: "This is a comment" });

// Set autofilter
ws["!autofilter"] = { ref: "A1:C10" };

// Set sheet protection
ws["!protect"] = { password: "secret", selectLockedCells: true };

// Set sheet margins
ws["!margins"] = { left: 0.7, right: 0.7, top: 0.75, bottom: 0.75, header: 0.3, footer: 0.3 };

// Set sheet visibility
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 1); // hidden

// Rename sheet
wb.Sheets["New Name"] = ws;
delete wb.Sheets["Old Name"];
wb.SheetNames = wb.SheetNames.map(n => n === "Old Name" ? "New Name" : n);

// Add defined names
if(!wb.Workbook) wb.Workbook = {};
if(!wb.Workbook.Names) wb.Workbook.Names = [];
wb.Workbook.Names.push({ Name: "MyData", Ref: "Sheet1!$A$1:$D$10" });

XLSX.writeFile(wb, "modified.xlsx");
```

### Parsing Options

```js
const wb = XLSX.readFile("data.xlsx", {
  type: "buffer",        // input type: base64, binary, string, buffer, array, file
  cellDates: true,       // store dates as Date objects (type "d") instead of numbers
  cellFormula: true,     // keep formulae in .f field (default: true)
  cellHTML: true,        // parse rich text to .h field (default: true)
  cellNF: true,          // save number format to .z field (default: false)
  cellStyles: true,      // save style info to .s field + row/col props (default: false)
  cellText: true,        // generate formatted text in .w field (default: true)
  dense: true,           // generate dense-mode worksheets (default: false)
  dateNF: "yyyy-mm-dd",  // override default date format (code 14)
  bookDeps: true,        // parse calculation chains (default: false)
  bookProps: true,       // only parse workbook metadata (default: false)
  bookSheets: true,      // only parse sheet names (default: false)
  bookVBA: true,         // extract VBA blob to vbaraw (default: false)
  bookFiles: true,       // preserve raw sub-files (default: false)
  sheets: [0, 2],        // only parse specific sheets by index or name
  sheet: "Sheet1",       // override worksheet name for single-sheet formats
  sheetStubs: true,      // create cell objects for stub cells (default: false)
  sheetRows: 100,        // only read first N rows (default: 0 = all)
  raw: true,             // disable value parsing in plaintext formats
  nodim: true,           // ignore self-reported dimensions, compute from cells
  xlfn: true,            // preserve _xlfn. prefixes in formula names
  password: "pass",      // password for XOR-encrypted XLS files
  codepage: 1252,        // default codepage for legacy formats
  UTC: true,             // parse text dates/times using UTC (default: true)
  FS: ",",               // DSV field separator override
  PRN: true,             // allow parsing of Lotus PRN files
  WTF: true,             // throw on unsupported features (default: false)
});
```

### Writing Options

```js
XLSX.writeFile(wb, "output.xlsx", {
  type: "buffer",        // output type: base64, binary, string, buffer, array, file
  bookType: "xlsx",      // output format (default: "xlsx", inferred from extension)
  bookSST: false,        // use Shared String Table (default: false)
  compression: true,     // enable ZIP compression (default: false, larger but faster)
  ignoreEC: true,        // suppress "number stored as text" warnings (default: true)
  cellDates: true,       // write native dates instead of date codes
  cellStyles: true,      // export style info + row/col props
  codepage: 1252,        // codepage for legacy formats
  Props: { Title: "Report", Author: "Me" }, // override workbook properties
  sheet: "Sheet1",       // specify sheet for single-sheet formats
  bookVBA: true,         // export VBA blob
  themeXLSX: "...",      // override theme XML for XLSX/XLSB/XLSM
  FS: ",",               // field separator for CSV/Text output
  RS: "\n",              // record separator for CSV/Text output
  numbers: "...",        // base64 NUMBERS payload (required for .numbers export)
  WTF: true,             // show warnings for unsafe features
});
```

### `sheet_to_json` Options

```js
XLSX.utils.sheet_to_json(ws, {
  header: 1,             // 1 = array-of-arrays, "A" = column labels, string[] = custom keys
  range: "A1:D10",       // limit to specific range (number = starting row, string = A1 range)
  blankrows: false,      // include blank rows (default: false when header not 1)
  defval: null,          // default value for empty cells
  raw: true,             // return raw values instead of formatted text (default: true)
  skipHidden: true,      // skip hidden rows and columns
  dateNF: "yyyy-mm-dd",  // date format for output
  UTC: true,             // return dates with correct UTC interpretation (default: false)
});
```

### `sheet_to_csv` Options

```js
XLSX.utils.sheet_to_csv(ws, {
  FS: ",",               // field separator (default: ",")
  RS: "\n",              // record separator (default: "\n")
  strip: true,           // remove trailing field separators
  blankrows: true,       // include blank lines (default: true)
  skipHidden: true,      // skip hidden rows/columns
  forceQuotes: true,     // force quotes around all fields
  dateNF: "yyyy-mm-dd",  // date format
});
```

## Gotchas

- **`readFile` / `writeFile` are Node.js/Deno/Bun only** — they rely on `fs`. In the browser, always use `XLSX.read()` with ArrayBuffer/binary data. In ESM, `readFile`/`writeFile` are stubs until `set_fs(fs)` is called.
- **Dates are numbers by default** — Excel stores dates as serial numbers. Use `cellDates: true` in read options to get actual `Date` objects. Without it, dates appear as numbers (e.g., `44927`). v0.20.0+ uses UTC interpretation for Date objects.
- **`sheet_to_json` with `header: 1` returns array-of-arrays** — the default behavior (no header option) returns array-of-objects using the first row as keys. Use `header: 1` for raw row data including headers.
- **`!ref` is required for writing** — if you create a worksheet manually without using `aoa_to_sheet` or `json_to_sheet`, you must set `ws["!ref"]` (e.g., `"A1:D10"`) or the writer won't know the sheet bounds.
- **Sheet names must be unique and ≤31 chars** — Excel enforces this. `book_append_sheet` throws if the name already exists. Use the 4th argument (`true`) to auto-increment.
- **Rich text and styling are limited in CE** — the Community Edition reads some styling but write support is minimal. Full style/theme/image support requires SheetJS Pro.
- **Formulae are stored but not evaluated** — the CE preserves formula strings in `.f` but does not calculate results. SheetJS Pro offers a formula calculator.
- **`cellStyles: true` is needed for row/col properties** — without it, `!rows`, `!cols`, and cell styles are not parsed or exported.
- **`set_cptable` is needed for legacy formats** — to read old XLS/DBF files with non-UTF encodings, load the codepage library separately.
- **`set_fs` is needed for ESM file I/O** — in ESM, call `XLSX.set_fs(fs)` before using `readFile`/`writeFile`.
- **`stream.set_readable(Readable)` for streaming** — in ESM, import `Readable` from `stream` and register it before using `XLSX.stream`.
- **Cell type `"z"` means stub/empty** — stub cells are placeholders in merged ranges. Use `sheetStubs: false` (default) to skip them.
- **`origin: -1` appends at the end** — when using `sheet_add_aoa` or `sheet_add_json`, `{ origin: -1 }` automatically finds the next empty row.
- **Dense mode changes cell access** — with `dense: true`, cells are at `ws["!data"][row][col]` (0-indexed), not `ws["A1"]`. Utility functions auto-detect dense sheets.
- **Merged cells only store value in top-left cell** — other cells in a merge range are stubs. Check the top-left cell for the value.
- **Excel tooltip limit is 255 characters** — longer tooltips in hyperlinks will cause files to fail in Excel.
- **`NaN` → `#NUM!`, `Infinity` → `#DIV/0!`** — v0.20.0+ exports these JS values as Excel errors.
- **`_xlfn.` prefix required for newer Excel functions** — functions like `UNIQUE`, `FILTER`, `XLOOKUP` need the `_xlfn.` prefix for compatibility.
- **1904 date system** — check `wb.Workbook?.WBProps?.date1904` to determine the epoch. Most files use 1900 system.
- **`bookType` inferred from extension** — `writeFile` guesses format from file extension if `bookType` is omitted.
- **CSV output includes UTF-8 BOM** — `XLSX.write` with `bookType: "csv"` always adds a BOM for Excel compatibility. `sheet_to_csv` does not.
- **NUMBERS export requires payload** — the `xlsx.zahl` script provides the base file. Import it and pass `numbers: XLSX_ZAHL_PAYLOAD`.
- **`defined names` need `wb.Workbook` structure** — parsers don't always create it. Initialize with `if(!wb.Workbook) wb.Workbook = {}; if(!wb.Workbook.Names) wb.Workbook.Names = [];`.
- **Overlapping merges are not auto-detected** — validate manually before adding merges to an existing sheet.
- **Column widths vary by font/scaling** — `wch` (character width) is more portable than `wpx` (pixel width) across machines.

## References

- [01-parsing-reading](references/01-parsing-reading.md) — Detailed guide to reading/parsing workbooks from various input sources
- [02-writing-exporting](references/02-writing-exporting.md) — Writing workbooks, output formats, browser download patterns, and NUMBERS export
- [03-data-model](references/03-data-model.md) — Common Spreadsheet Format: workbook, worksheet, cell objects, and dense mode in detail
- [04-utility-functions](references/04-utility-functions.md) — Complete reference for `XLSX.utils` conversion and manipulation functions
- [05-parsing-writing-options](references/05-parsing-writing-options.md) — Full reference for all read/write option objects
- [06-cell-addresses](references/06-cell-addresses.md) — Cell address encoding/decoding, ranges, and coordinate utilities
- [07-browser-integration](references/07-browser-integration.md) — File input, drag-and-drop, fetch, download patterns, and HTML table integration
- [08-advanced-topics](references/08-advanced-topics.md) — Merged cells, hyperlinks, comments, protection, autofilter, column/row properties, defined names, sheet visibility
- [09-dates-and-formats](references/09-dates-and-formats.md) — Date handling, number formats, SSF library, 1900/1904 date systems, and UTC vs local time
- [10-formulae](references/10-formulae.md) — Cell formulae, array formulae, dynamic array formulae, localization, and _xlfn. prefixes
- [11-streaming](references/11-streaming.md) — Streaming export with `XLSX.stream` for CSV, JSON, HTML, and XLML
- [12-installation](references/12-installation.md) — Installation methods, ESM setup, bundler configs, and platform-specific notes

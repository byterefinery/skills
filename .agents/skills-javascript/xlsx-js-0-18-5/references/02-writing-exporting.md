# Writing and Exporting Workbooks

## Write Functions

| Function | Environment | Description |
|---|---|---|
| `XLSX.writeFile(wb, filename, opts)` | Node.js, Deno | Write workbook to a local file |
| `XLSX.writeFileAsync(filename, wb, opts, cb)` | Node.js | Async file write |
| `XLSX.write(wb, opts)` | Universal | Serialize workbook to bytes |
| `XLSX.writeXLSX(wb, opts)` | Universal | Convenience: write as XLSX format |
| `XLSX.writeFileXLSX(wb, filename, opts)` | Node.js, Deno | Convenience: write XLSX to file |

## Output Types

`XLSX.write(wb, opts)` returns data in the specified format:

| `type` | Return Type | Description |
|---|---|---|
| `"buffer"` | `Buffer` | Node.js Buffer |
| `"array"` | `number[]` | Array of bytes |
| `"binary"` | `string` | Binary string |
| `"base64"` | `string` | Base64-encoded string |
| `"string"` | `string` | UTF-8 string (for text formats) |
| `"file"` | `void` | Write to file (used by `writeFile`) |

## Supported Output Formats

```js
XLSX.writeFile(wb, "output.xlsx", { bookType: "xlsx" });
```

| `bookType` | Format | Description |
|---|---|---|
| `"xlsx"` | .xlsx | Office Open XML (default) |
| `"xlsm"` | .xlsm | XLSX with macros |
| `"xlsb"` | .xlsb | Excel Binary (compact, fast) |
| `"xls"` | .xls | BIFF8 Excel 97-2003 |
| `"xla"` | .xla | Excel Add-in (BIFF8) |
| `"biff8"` | .xls | Raw BIFF8 |
| `"biff5"` | .xls | BIFF5 Excel 5.0 |
| `"biff2"` | .xls | BIFF2 Excel 2.0 |
| `"xlml"` | .xml | SpreadsheetML 2003 |
| `"ods"` | .ods | OpenDocument Spreadsheet |
| `"fods"` | .fods | Flat ODS (XML) |
| `"csv"` | .csv | Comma-separated values |
| `"txt"` | .txt | Tab-separated values |
| `"sylk"` / `"slk"` | .slk | Symbolic Link |
| `"html"` | .html | HTML table |
| `"dif"` | .dif | Data Interchange Format |
| `"rtf"` | .rtf | Rich Text Format |
| `"prn"` | .prn | Fixed-width text |
| `"eth"` | .eth | ETH format |
| `"dbf"` | .dbf | dBase file |

## Writing Options

```js
XLSX.writeFile(wb, "output.xlsx", {
  bookType: "xlsx",     // output format (default: "xlsx")
  bookSST: false,       // generate Shared String Table (default: false)
  compression: true,    // ZIP compression for ZIP-based formats (default: false)
  ignoreEC: true,       // suppress "number stored as text" warnings (default: true)
  cellDates: false,     // write native dates vs date codes
  cellStyles: false,    // export style/theme info
  bookVBA: false,       // include VBA macros
  password: "",         // password for encrypted files
  sheet: "Sheet1",      // specify sheet for single-sheet formats (CSV, etc.)
  Props: {              // override workbook properties
    Title: "Report",
    Subject: "Q4 Data",
    Author: "Analytics Team",
    Company: "Acme Corp",
    Keywords: "report, data",
    Comments: "Auto-generated",
  },
});
```

## Browser Download Patterns

### Method 1: Using `writeFile` (built-in, modern browsers)

```js
// XLSX.writeFile attempts to trigger a download in browsers
XLSX.writeFile(wb, "report.xlsx");
```

### Method 2: Manual Blob Download

```js
function downloadWorkbook(wb, filename = "report.xlsx") {
  const buf = XLSX.write(wb, { type: "array", bookType: "xlsx" });
  const blob = new Blob([buf], { type: "application/octet-stream" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
```

### Method 3: Base64 Download Link

```js
function createDownloadLink(wb, filename = "report.xlsx") {
  const b64 = XLSX.write(wb, { type: "base64", bookType: "xlsx" });
  const link = document.createElement("a");
  link.href = "data:application/octet-stream;base64," + b64;
  link.download = filename;
  return link;
}
```

### Method 4: Fetch API (for server upload)

```js
async function uploadWorkbook(wb, url) {
  const buf = XLSX.write(wb, { type: "array", bookType: "xlsx" });
  const blob = new Blob([buf], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
  const formData = new FormData();
  formData.append("file", blob, "report.xlsx");
  await fetch(url, { method: "POST", body: formData });
}
```

## Node.js Write Patterns

```js
const XLSX = require("xlsx");
const fs = require("fs");

// Direct write
XLSX.writeFile(wb, "output.xlsx");

// Write to buffer, then save
const buf = XLSX.write(wb, { type: "buffer", bookType: "xlsx" });
fs.writeFileSync("output.xlsx", buf);

// Write to stream
const stream = fs.createWriteStream("output.xlsx");
const buf = XLSX.write(wb, { type: "buffer" });
stream.write(buf);
stream.end();

// Async write
XLSX.writeFileAsync("output.xlsx", wb, (err) => {
  if (err) console.error(err);
});
```

## Streaming Output (Node.js)

```js
import { Readable } from "stream";
XLSX.stream.set_readable(Readable);

// CSV stream
const csvStream = XLSX.stream.to_csv(ws);
csvStream.pipe(process.stdout);

// JSON stream
const jsonStream = XLSX.stream.to_json(ws);
jsonStream.on("data", (obj) => console.log(obj));
```

## Multi-Sheet Workbooks

```js
const wb = XLSX.utils.book_new();

// Add multiple sheets
XLSX.utils.book_append_sheet(wb, sheet1, "Sales");
XLSX.utils.book_append_sheet(wb, sheet2, "Inventory");
XLSX.utils.book_append_sheet(wb, sheet3, "Summary");

// For single-sheet formats (CSV, etc.), use sheet option
XLSX.writeFile(wb, "sales.csv", { sheet: "Sales" });
```

## Format-Specific Notes

- **XLSB** is the most compact binary format and fastest to parse. Use it for large files.
- **XLSX** is the default and most compatible format.
- **CSV** only exports one sheet at a time. Use the `sheet` option to select which sheet.
- **XLSM** requires `bookVBA: true` and a `vbaraw` property on the workbook.
- **Compression** (`compression: true`) reduces file size for ZIP-based formats (XLSX, XLSB, ODS) but increases CPU usage.
- **`bookSST: true`** generates a Shared String Table, which can reduce file size for workbooks with repeated string values.

# Parsing and Reading

## Input Types

`XLSX.read(data, opts)` accepts data in several formats. The `type` option controls interpretation:

| `type` | Expected Input |
|---|---|
| `base64` | Base64-encoded string |
| `binary` | Binary string (byte `n` = `data.charCodeAt(n)`) |
| `string` | UTF-8 text string (for text formats only) |
| `buffer` | Node.js Buffer |
| `array` | Array of 8-bit unsigned integers |

Some types are auto-detected: `Buffer`, `Uint8Array`, `Int8Array`, `ArrayBuffer`. When a plain string is passed with no `type`, the library assumes Base64.

## Reading Patterns

### Node.js — File System

```js
const XLSX = require("xlsx");
const wb = XLSX.readFile("data.xlsx");
```

### Node.js — ESM

```js
import * as XLSX from "xlsx";
import { readFileSync } from "fs";
const wb = XLSX.read(readFileSync("data.xlsx"));
```

### Node.js — ESM with readFile

```js
import * as XLSX from "xlsx";
import * as fs from "fs";
XLSX.set_fs(fs);
const wb = XLSX.readFile("data.xlsx");
```

### Browser — File Input

```js
const reader = new FileReader();
reader.onload = (e) => {
  const wb = XLSX.read(e.target.result);
};
reader.readAsArrayBuffer(file);
```

### Browser — Fetch

```js
const data = await (await fetch(url)).arrayBuffer();
const wb = XLSX.read(data);
```

### Deno

```ts
import * as XLSX from "https://cdn.sheetjs.com/xlsx-0.20.3/package/xlsx.mjs";
const file = await Deno.open("data.xlsx");
const buffer = new Uint8Array(await Deno.readFile("data.xlsx"));
const wb = XLSX.read(buffer);
```

### Bun

```js
import * as XLSX from "xlsx";
import * as fs from "fs";
XLSX.set_fs(fs);
const wb = XLSX.readFile("data.xlsx");
```

## Auto-Detection

SheetJS auto-detects file format from the first bytes:

| Byte 0 | File Type | Spreadsheet Formats |
|---|---|---|
| `0xD0` | CFB Container | BIFF 5/8, protected XLSX/XLSB, WQ3/QPW, XLR |
| `0x09` | BIFF Stream | BIFF 2/3/4/5 |
| `0x3C` | XML/HTML | SpreadsheetML, Flat ODS, UOS1, HTML, plain text |
| `0x50` | ZIP Archive | XLSB, XLSX/XLSM, ODS, UOS2, NUMBERS |
| `0x49` | Plain Text | SYLK, plain text |
| `0x54` | Plain Text | DIF, plain text |
| `0xEF` | UTF-8 Text | SpreadsheetML, Flat ODS, HTML |
| `0x00` | Record Stream | Lotus WK*, Quattro Pro |
| `0x7B` | Plain text | RTF, plain text |

Plain text formats are guessed in priority order: XML → HTML → RTF → DSV (PSV → SSV → TSV → CSV) → PRN → CSV (fallback).

## Partial Parsing

For large files, parse only what you need:

```js
// Only get sheet names (fast)
const wb = XLSX.read(data, { bookSheets: true });
console.log(wb.SheetNames); // ["Sheet1", "Sheet2"]

// Only get workbook properties
const wb = XLSX.read(data, { bookProps: true });
console.log(wb.Props); // { Title, Author, ... }

// Only parse specific sheets
const wb = XLSX.read(data, { sheets: [0, 2] }); // first and third sheets
const wb = XLSX.read(data, { sheets: "Sheet1" }); // by name
const wb = XLSX.read(data, { sheets: [0, "Data"] }); // mixed

// Limit rows
const wb = XLSX.read(data, { sheetRows: 100 }); // first 100 rows
```

## VBA Extraction

```js
const wb = XLSX.read(data, { bookVBA: true });
if (wb.vbaraw) {
  // Raw VBA CFB object available
}
```

## Encrypted Files

SheetJS CE supports XOR encryption in XLS files only:

```js
const wb = XLSX.read(data, { password: "secret" });
```

AES-encrypted XLSX/XLSB/XLSM requires SheetJS Pro.

## Legacy Codepage Support

For old XLS/DBF files with non-UTF encodings:

```js
// CommonJS
const XLSX = require("xlsx");
const cptable = require("xlsx/dist/cpexcel.full");
XLSX.set_cptable(cptable);

// ESM
import * as XLSX from "xlsx";
import * as cptable from "xlsx/dist/cpexcel.full.mjs";
XLSX.set_cptable(cptable);

const wb = XLSX.read(data, { codepage: 1252 });
```

## Error Handling

By default, worksheet parsing errors are suppressed (valid sheets from multi-sheet workbooks are still parsed). Use `WTF: true` to throw on errors:

```js
try {
  const wb = XLSX.read(data, { WTF: true });
} catch (e) {
  console.error("Parse error:", e.message);
}
```

## Raw Internal Files

Preserve raw sub-files from ZIP/CFB containers:

```js
const wb = XLSX.read(data, { bookFiles: true });
// wb will have:
// - keys: array of paths in the ZIP
// - files: hash mapping paths to file objects
// - cfb: CFB container object (for CFB-based formats)
```

# Parsing and Reading Workbooks

## Input Types

`XLSX.read(data, opts)` accepts multiple input formats controlled by the `type` option:

| `type` | Input | Description |
|---|---|---|
| `"buffer"` | `Buffer` | Node.js Buffer (default for Buffer input) |
| `"array"` | `Uint8Array` / `ArrayBuffer` / `number[]` | Typed array or plain array of bytes |
| `"binary"` | `string` | Binary string (each char = 1 byte) |
| `"base64"` | `string` | Base64-encoded string |
| `"string"` | `string` | UTF-8 string (for HTML/CSV text input) |
| `"file"` | `string` | File path (used internally by `readFile`) |

If `type` is omitted, the library auto-detects based on the input type.

## Reading from Files

### Node.js CommonJS

```js
const XLSX = require("xlsx");

// Direct file read (uses fs.readFileSync internally)
const wb = XLSX.readFile("data.xlsx");
const wb = XLSX.readFile("data.xlsx", { cellDates: true, cellNF: true });
```

### Node.js ESM

```js
import { read } from "xlsx/xlsx.mjs";
import { readFileSync } from "fs";

// Manual approach — read file then parse
const buf = readFileSync("data.xlsx");
const wb = read(buf);

// Or enable readFile helper
import { set_fs } from "xlsx/xlsx.mjs";
import * as fs from "fs";
set_fs(fs);
// Now readFile is available via the XLSX namespace if using full import
```

### Browser — File Input Element

```js
// Modern approach (Chrome 76+)
async function handleFile(e) {
  const file = e.target.files[0];
  const data = await file.arrayBuffer();
  const wb = XLSX.read(data);
}

// Broad compatibility (IE10+)
function handleFile(e) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const wb = XLSX.read(e.target.result); // ArrayBuffer
  };
  reader.readAsArrayBuffer(e.target.files[0]);
}
```

### Browser — Drag and Drop

```js
async function handleDrop(e) {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  const data = await file.arrayBuffer();
  const wb = XLSX.read(data);
}

dropZone.addEventListener("drop", handleDrop);
dropZone.addEventListener("dragover", (e) => e.preventDefault());
```

### Browser — Fetch (Remote Files)

```js
// Using fetch
async function loadRemote(url) {
  const data = await (await fetch(url)).arrayBuffer();
  return XLSX.read(data);
}

// Using XMLHttpRequest
function loadRemoteXHR(url, callback) {
  const req = new XMLHttpRequest();
  req.open("GET", url, true);
  req.responseType = "arraybuffer";
  req.onload = () => callback(XLSX.read(req.response));
  req.send();
}
```

### Deno

```js
import * as XLSX from 'https://unpkg.com/xlsx@0.18.5/xlsx.mjs';

// readFile works in Deno (requires --allow-read)
const wb = XLSX.readFile("data.xlsx");

// Or manual
const buf = await Deno.readFile("data.xlsx");
const wb = XLSX.read(buf);
```

### React Native

```js
import XLSX from "xlsx";
import { readFile } from "react-native-fs";

// Using react-native-fs (returns binary string)
const bstr = await readFile(path, "ascii");
const wb = XLSX.read(bstr, { type: "binary" });

// Using react-native-file-access (returns base64)
const b64 = await FileSystem.readFile(path, "base64");
const wb = XLSX.read(b64, { type: "base64" });
```

### Node.js — HTTP Uploads

```js
const XLSX = require("xlsx");
const formidable = require("formidable");

const form = new formidable.IncomingForm();
form.parse(req, (err, fields, files) => {
  const file = Object.values(files)[0];
  const wb = XLSX.readFile(file.filepath);
});
```

### Node.js — Streams

```js
const XLSX = require("xlsx");
const fs = require("fs");

function readFromStream(stream) {
  return new Promise((resolve, reject) => {
    const buffers = [];
    stream.on("data", (chunk) => buffers.push(chunk));
    stream.on("end", () => {
      const buffer = Buffer.concat(buffers);
      resolve(XLSX.read(buffer));
    });
    stream.on("error", reject);
  });
}
```

### Node.js — Axios

```js
const XLSX = require("xlsx");
const axios = require("axios");

const res = await axios.get(url, { responseType: "arraybuffer" });
const wb = XLSX.read(res.data);
```

## Parsing Options Reference

```js
const wb = XLSX.read(data, {
  // Input type
  type: "buffer",        // "base64" | "binary" | "buffer" | "file" | "array" | "string"
  codepage: 1252,        // default codepage for legacy formats

  // Cell content options
  cellDates: false,      // store dates as Date objects (type "d") vs numbers (type "n")
  cellFormula: true,     // keep formulae in .f field
  cellHTML: true,        // parse rich text to .h field
  cellNF: false,         // save number format to .z field
  cellStyles: false,     // save style info to .s field
  cellText: true,        // generate formatted text in .w field

  // Date handling
  dateNF: "yyyy-mm-dd",  // override default date format (code 14)

  // Structural options
  sheetStubs: false,     // create cell objects for stub cells
  bookDeps: false,       // parse calculation chains
  bookProps: false,      // only parse workbook metadata
  bookSheets: false,     // only parse sheet names
  bookFiles: false,      // add raw files to workbook object

  // Sheet selection
  sheets: [0],           // only parse specific sheets (index or name)

  // Delimiter-separated formats
  FS: ",",               // field separator override
  raw: false,            // don't parse values in plaintext formats

  // Other
  WTF: false,            // throw on unsupported features
  password: "",          // password for encrypted files
  xlfn: false,           // preserve _xlfn. prefixes in formula names
  dense: false,          // use dense array format (not supported in 0.18.5)
});
```

## Accessing Parsed Data

```js
const wb = XLSX.read(data);

// List sheet names
console.log(wb.SheetNames); // ["Sheet1", "Sheet2"]

// Access a worksheet
const ws = wb.Sheets["Sheet1"];

// Get used range
console.log(ws["!ref"]); // "A1:D10"

// Access a cell
const cell = ws["A1"];
console.log(cell.v);  // raw value
console.log(cell.w);  // formatted text
console.log(cell.t);  // type: "s" | "n" | "b" | "d" | "e" | "z"
console.log(cell.f);  // formula (if any)
console.log(cell.z);  // number format (if cellNF: true)

// Iterate cells in range
const range = XLSX.utils.decode_range(ws["!ref"]);
for (let R = range.s.r; R <= range.e.r; ++R) {
  for (let C = range.s.c; C <= range.e.c; ++C) {
    const addr = XLSX.utils.encode_cell({ r: R, c: C });
    const cell = ws[addr];
    if (cell) {
      console.log(addr, cell.v);
    }
  }
}

// Workbook properties
console.log(wb.Props); // { Title, Author, Subject, ... }
```

## Legacy Format Support

For reading old XLS files with non-UTF encodings, load the codepage library:

```js
// ESM
import { set_cptable } from "xlsx/xlsx.mjs";
import * as cptable from "xlsx/dist/cpexcel.full.mjs";
set_cptable(cptable);

// CommonJS (built-in, no extra step needed)
const XLSX = require("xlsx"); // cptable is bundled
```

Supported codepages: 874, 932, 936, 949, 950, 1250-1258, 65001 (UTF-8), 6969 (MAC), 10000 (MAC).

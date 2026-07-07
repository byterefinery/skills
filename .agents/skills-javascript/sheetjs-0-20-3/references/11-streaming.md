# Streaming Export

SheetJS streams use the Node.js push stream API. They enable incremental output for large workbooks.

## Setup

### CommonJS

Streams work out of the box:

```js
const XLSX = require("xlsx");
// XLSX.stream is ready to use
```

### ESM

Register `Readable` before use:

```js
import { stream } from "xlsx";
import { Readable } from "stream";
stream.set_readable(Readable);
```

## Worksheet Streams

### CSV Stream

```js
const wb = XLSX.read(data);
const ws = wb.Sheets[wb.SheetNames[0]];
XLSX.stream.to_csv(ws).pipe(process.stdout);
```

Options mirror `sheet_to_csv`: `FS`, `RS`, `strip`, `blankrows`, `skipHidden`, `forceQuotes`, `dateNF`.

### JSON Stream

```js
const { Transform } = require("stream");

const conv = new Transform({ writableObjectMode: true });
conv._transform = (obj, enc, cb) => cb(null, JSON.stringify(obj) + "\n");

XLSX.stream.to_json(ws, { raw: true }).pipe(conv).pipe(process.stdout);
```

Options mirror `sheet_to_json`: `header`, `range`, `blankrows`, `defval`, `raw`, `skipHidden`, `UTC`.

### HTML Stream

```js
XLSX.stream.to_html(ws).pipe(process.stdout);
```

Options mirror `sheet_to_html`: `id`, `editable`, `header`, `footer`.

## Workbook Streams

### XLML Stream (v0.20.3)

```js
const fs = require("fs");
XLSX.stream.to_xlml(wb).pipe(fs.createWriteStream("output.xls"));
```

Options mirror `write` with `bookType: "xlml"`.

## Streaming Patterns

### Pipe to File

```js
const fs = require("fs");
const wb = XLSX.read(data);
const ws = wb.Sheets[wb.SheetNames[0]];
XLSX.stream.to_csv(ws).pipe(fs.createWriteStream("output.csv"));
```

### Pipe to HTTP Response

```js
app.get("/download", (req, res) => {
  res.setHeader("Content-Type", "text/csv");
  res.setHeader("Content-Disposition", "attachment; filename=data.csv");
  const wb = XLSX.read(data);
  const ws = wb.Sheets[wb.SheetNames[0]];
  XLSX.stream.to_csv(ws).pipe(res);
});
```

### Collect Stream Output

```js
const chunks = [];
XLSX.stream.to_csv(ws)
  .on("data", (chunk) => chunks.push(chunk))
  .on("end", () => {
    const csv = chunks.join("");
    console.log(csv);
  });
```

## Limitations

- Streams use Node.js push API — not directly compatible with browser Web Streams
- `to_xlml` is the only workbook-level stream (XLSX/XLSB streaming not supported)
- Worksheet streams process the entire worksheet in memory before streaming output
- For truly streaming large files, consider processing in chunks or using SheetJS Pro

# Installation and Setup

## npm / yarn / pnpm

```bash
npm install xlsx@0.20.3
# or
yarn add xlsx@0.20.3
# or
pnpm add xlsx@0.20.3
```

## CommonJS

```js
const XLSX = require("xlsx");
```

## ESM (Node.js)

```js
import * as XLSX from "xlsx";
// Or named imports:
import { read, writeFile, utils, stream } from "xlsx";
```

### ESM File I/O

In ESM, `readFile` and `writeFile` are stubs until `fs` is registered:

```js
import * as XLSX from "xlsx";
import * as fs from "fs";
XLSX.set_fs(fs);

// Now readFile/writeFile work
const wb = XLSX.readFile("data.xlsx");
XLSX.writeFile(wb, "output.xlsx");
```

Alternatively, use `read`/`write` directly:

```js
import { read, write } from "xlsx";
import { readFileSync, writeFileSync } from "fs";

const wb = read(readFileSync("data.xlsx"));
writeFileSync("output.xlsx", write(wb, { type: "buffer", bookType: "xlsx" }));
```

## Browser — Standalone Script

```html
<script src="https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js"></script>
<script>
  // XLSX is available as a global
  const wb = XLSX.read(data);
</script>
```

## Browser — ESM Module

```html
<script type="module">
  import * as XLSX from "https://cdn.sheetjs.com/xlsx-0.20.3/package/xlsx.mjs";
</script>
```

## Deno

```ts
import * as XLSX from "https://cdn.sheetjs.com/xlsx-0.20.3/package/xlsx.mjs";
```

## Bun

```js
import * as XLSX from "xlsx";
import * as fs from "fs";
XLSX.set_fs(fs);
```

## CDN URLs

| Build | URL |
|---|---|
| Full | `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js` |
| ESM | `https://cdn.sheetjs.com/xlsx-0.20.3/package/xlsx.mjs` |
| Core (no codepage) | `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.core.min.js` |
| Mini (smallest) | `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.mini.min.js` |
| NUMBERS payload | `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.zahl.js` |

### Build Differences

| Build | Size | Features |
|---|---|---|
| `xlsx.full.min.js` | ~1MB | Everything: all formats, codepage support |
| `xlsx.core.min.js` | ~700KB | All formats except codepage (no legacy XLS encoding) |
| `xlsx.mini.min.js` | ~300KB | XLSX, ODS, CSV only (no XLSB, XLS, NUMBERS, SpreadsheetML) |

## Codepage Support

For reading old XLS/DBF files with non-UTF encodings:

```js
// CommonJS — included in xlsx.full.min.js
const XLSX = require("xlsx");

// ESM — load separately
import * as XLSX from "xlsx";
import * as cptable from "xlsx/dist/cpexcel.full.mjs";
XLSX.set_cptable(cptable);
```

## NUMBERS Export Payload

```js
// CommonJS
const XLSX_ZAHL_PAYLOAD = require("xlsx/dist/xlsx.zahl");

// ESM
import XLSX_ZAHL_PAYLOAD from "xlsx/dist/xlsx.zahl.mjs";

// CDN
// <script src="https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.zahl.js"></script>
// Global: XLSX_ZAHL_PAYLOAD
```

## Bundler Configuration

### Vite

```js
// vite.config.js
export default {
  optimizeDeps: {
    include: ["xlsx"]
  }
};
```

### Webpack

No special config needed. Use standard imports.

### esbuild

```bash
esbuild entry.js --bundle --outfile=dist/bundle.js
```

### Rollup

```js
// rollup.config.js
export default {
  input: "src/index.js",
  output: { file: "dist/bundle.js", format: "iife" }
};
```

## TypeScript

SheetJS ships with type definitions:

```ts
import * as XLSX from "xlsx";

const wb: XLSX.WorkBook = XLSX.read(data);
const ws: XLSX.WorkSheet = wb.Sheets[wb.SheetNames[0]];
const cell: XLSX.CellObject | undefined = ws["A1"];
```

Key types: `WorkBook`, `WorkSheet`, `CellObject`, `CellAddress`, `Range`, `ParsingOptions`, `WritingOptions`, `Sheet2JSONOpts`, `Sheet2CSVOpts`.

## Package Exports

```json
{
  "main": "xlsx.js",
  "module": "xlsx.mjs",
  "types": "types/index.d.ts",
  "exports": {
    ".": {
      "import": "./xlsx.mjs",
      "require": "./xlsx.js"
    },
    "./dist/*": "./dist/*",
    "./types/*": "./types/*"
  }
}
```

## CLI

SheetJS includes a CLI tool (bin/xlsx.njs):

```bash
npx xlsx file.xlsx
```

For a standalone CLI, use the `xlsx-cli` package:

```bash
npm install -g xlsx-cli
xlsx file.xlsx
```

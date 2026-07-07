# Browser Integration

## Loading the Library

### Standalone Script (Global `XLSX`)

```html
<script src="https://unpkg.com/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
<script>
  // XLSX is available as a global
  const wb = XLSX.read(data);
</script>
```

Build variants:
- `xlsx.full.min.js` — complete build with codepage support
- `xlsx.core.min.js` — without codepage library (no XLS encoding support)
- `xlsx.mini.min.js` — smallest (no XLSB/XLS/Numbers/SpreadsheetML)

### ES Module

```html
<script type="module">
  import { read, utils, writeFile } from "https://unpkg.com/xlsx@0.18.5/xlsx.mjs";
</script>
```

### CDN Sources

| CDN | URL |
|---|---|
| unpkg | `https://unpkg.com/xlsx@0.18.5/dist/xlsx.full.min.js` |
| jsDelivr | `https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js` |
| CDNjs | `https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js` |

## Reading Files in the Browser

### File Input Element

```html
<input type="file" id="fileInput" accept=".xlsx,.xls,.csv,.ods">
```

```js
// Modern (Chrome 76+)
const input = document.getElementById("fileInput");
input.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  const data = await file.arrayBuffer();
  const wb = XLSX.read(data);
  processWorkbook(wb);
});

// Broad compatibility (IE10+)
input.addEventListener("change", (e) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    const wb = XLSX.read(e.target.result);
    processWorkbook(wb);
  };
  reader.readAsArrayBuffer(e.target.files[0]);
});
```

### Drag and Drop

```html
<div id="dropZone">Drop file here</div>
```

```js
const dropZone = document.getElementById("dropZone");

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.style.background = "#e0e0e0";
});

dropZone.addEventListener("dragleave", () => {
  dropZone.style.background = "";
});

dropZone.addEventListener("drop", async (e) => {
  e.preventDefault();
  dropZone.style.background = "";
  const file = e.dataTransfer.files[0];
  const data = await file.arrayBuffer();
  const wb = XLSX.read(data);
  processWorkbook(wb);
});
```

### Fetch (Remote Files)

```js
// fetch API
async function loadRemote(url) {
  const data = await (await fetch(url)).arrayBuffer();
  return XLSX.read(data);
}

// XMLHttpRequest
function loadRemoteXHR(url, callback) {
  const req = new XMLHttpRequest();
  req.open("GET", url, true);
  req.responseType = "arraybuffer";
  req.onload = () => callback(XLSX.read(req.response));
  req.onerror = () => callback(null);
  req.send();
}
```

### HTML Table to Workbook

```js
// From a TABLE element on the page
const table = document.getElementById("my-table");
const wb = XLSX.utils.table_to_book(table);

// From HTML string
const htmlString = "<table><tr><td>A</td><td>B</td></tr></table>";
const wb = XLSX.read(htmlString, { type: "string" });
```

## Downloading Workbooks

### Using `writeFile` (built-in)

```js
// XLSX.writeFile triggers a download in modern browsers
XLSX.writeFile(wb, "report.xlsx");
```

### Manual Blob Download

```js
function download(wb, filename = "report.xlsx") {
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

### Base64 Data URL

```js
function downloadBase64(wb, filename = "report.xlsx") {
  const b64 = XLSX.write(wb, { type: "base64", bookType: "xlsx" });
  const url = "data:application/octet-stream;base64," + b64;
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
}
```

### Upload to Server

```js
async function upload(wb, url) {
  const buf = XLSX.write(wb, { type: "array", bookType: "xlsx" });
  const blob = new Blob([buf], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  });
  const formData = new FormData();
  formData.append("file", blob, "report.xlsx");
  const response = await fetch(url, { method: "POST", body: formData });
  return response.json();
}
```

## Displaying Data

### Render as HTML Table

```js
function renderSheetToTable(ws, container) {
  const html = XLSX.utils.sheet_to_html(ws);
  container.innerHTML = html;
}
```

### Convert to JSON for Data Grids

```js
const data = XLSX.utils.sheet_to_json(ws);
// Pass to DataTables, AG-Grid, Handsontable, etc.
```

### CSV Download

```js
function downloadCSV(ws, filename = "data.csv") {
  const csv = XLSX.utils.sheet_to_csv(ws);
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
```

## Web Workers

```js
// main.js
const worker = new Worker("xlsx-worker.js");
worker.postMessage({ action: "read", data: arrayBuffer });
worker.onmessage = (e) => {
  const json = e.data; // sheet_to_json result
};
```

```js
// xlsx-worker.js
importScripts("https://unpkg.com/xlsx@0.18.5/dist/xlsx.full.min.js");

self.onmessage = (e) => {
  if (e.data.action === "read") {
    const wb = XLSX.read(e.data.data);
    const ws = wb.Sheets[wb.SheetNames[0]];
    const json = XLSX.utils.sheet_to_json(ws);
    self.postMessage(json);
  }
};
```

## Framework Integration

### React

```jsx
function ExcelUploader() {
  const [data, setData] = useState([]);

  const handleFile = async (e) => {
    const file = e.target.files[0];
    const buf = await file.arrayBuffer();
    const wb = XLSX.read(buf);
    const ws = wb.Sheets[wb.SheetNames[0]];
    setData(XLSX.utils.sheet_to_json(ws));
  };

  return <input type="file" onChange={handleFile} accept=".xlsx,.csv" />;
}
```

### Vue

```js
export default {
  data() { return { rows: [] } },
  methods: {
    async handleFile(e) {
      const file = e.target.files[0];
      const buf = await file.arrayBuffer();
      const wb = XLSX.read(buf);
      this.rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]);
    }
  }
}
```

## IE Compatibility

For IE 6-9, add the shim before the library:

```html
<script src="https://unpkg.com/xlsx@0.18.5/dist/shim.min.js"></script>
<script src="https://unpkg.com/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
```

The shim provides `IE_LoadFile` and `IE_SaveFile` helpers for IE 6-9.

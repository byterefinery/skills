# Browser Integration

## File Input

### Basic File Input

```html
<input type="file" id="fileInput" />
<script>
  document.getElementById("fileInput").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    const arrayBuffer = await file.arrayBuffer();
    const wb = XLSX.read(arrayBuffer);
    const ws = wb.Sheets[wb.SheetNames[0]];
    const data = XLSX.utils.sheet_to_json(ws);
    console.log(data);
  });
</script>
```

### FileReader API

```js
const reader = new FileReader();
reader.onload = (e) => {
  const wb = XLSX.read(e.target.result);
  // process workbook
};
reader.readAsArrayBuffer(file);
```

### Drag and Drop

```html
<div id="dropZone">Drop file here</div>
<script>
  const dropZone = document.getElementById("dropZone");
  dropZone.addEventListener("dragover", (e) => { e.preventDefault(); });
  dropZone.addEventListener("drop", async (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    const arrayBuffer = await file.arrayBuffer();
    const wb = XLSX.read(arrayBuffer);
    // process workbook
  });
</script>
```

## Fetching Remote Files

```js
const response = await fetch("https://example.com/data.xlsx");
const arrayBuffer = await response.arrayBuffer();
const wb = XLSX.read(arrayBuffer);
```

## Downloading Files

### Using `writeFile` (simplest)

```js
XLSX.writeFile(wb, "output.xlsx");
```

`writeFile` triggers a browser download. Works in most modern browsers.

### Manual Blob Download

```js
const buffer = XLSX.write(wb, { type: "array", bookType: "xlsx" });
const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "output.xlsx";
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
URL.revokeObjectURL(url);
```

### MIME Types

| Format | MIME Type |
|---|---|
| XLSX | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| XLSM | `application/vnd.ms-excel` |
| XLSB | `application/vnd.ms-excel` |
| XLS | `application/vnd.ms-excel` |
| ODS | `application/vnd.oasis.opendocument.spreadsheet` |
| CSV | `text/csv` |
| HTML | `text/html` |

## HTML Table Integration

### Export HTML Table to Spreadsheet

```html
<table id="myTable">
  <tr><th>Name</th><th>Age</th></tr>
  <tr><td>Alice</td><td>30</td></tr>
  <tr><td>Bob</td><td>25</td></tr>
</table>
<button onclick="exportTable()">Export</button>

<script>
  function exportTable() {
    const table = document.getElementById("myTable");
    const wb = XLSX.utils.table_to_book(table);
    XLSX.writeFile(wb, "export.xlsx");
  }
</script>
```

### Display Spreadsheet as HTML Table

```js
const wb = XLSX.read(data);
const ws = wb.Sheets[wb.SheetNames[0]];
const html = XLSX.utils.sheet_to_html(ws);
document.getElementById("output").innerHTML = html;
```

### HTML Table with Value Attributes

Generated HTML includes `data-t`, `data-v`, `data-z` attributes:

```html
<td data-t="n" data-v="42" data-z="0">42</td>
```

These can be used to override values when re-importing:

```html
<td data-t="s">2012-12-03</td>  <!-- Force text type -->
<td data-t="n" data-v="41246" data-z="yyyy-mm-dd">2012-12-03</td>  <!-- Force date -->
```

## React Integration

```jsx
import { useState } from "react";
import * as XLSX from "xlsx";

function ExcelUploader() {
  const [data, setData] = useState([]);

  const handleFile = async (e) => {
    const file = e.target.files[0];
    const buffer = await file.arrayBuffer();
    const wb = XLSX.read(buffer);
    const ws = wb.Sheets[wb.SheetNames[0]];
    setData(XLSX.utils.sheet_to_json(ws));
  };

  const handleExport = () => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Data");
    XLSX.writeFile(wb, "export.xlsx");
  };

  return (
    <div>
      <input type="file" onChange={handleFile} />
      <button onClick={handleExport}>Export</button>
      <table>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {Object.values(row).map((val, j) => (
                <td key={j}>{val}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## Vue Integration

```vue
<template>
  <div>
    <input type="file" @change="handleFile" />
    <button @click="handleExport">Export</button>
  </div>
</template>

<script>
import * as XLSX from "xlsx";

export default {
  data() {
    return { data: [] };
  },
  methods: {
    async handleFile(e) {
      const file = e.target.files[0];
      const buffer = await file.arrayBuffer();
      const wb = XLSX.read(buffer);
      const ws = wb.Sheets[wb.SheetNames[0]];
      this.data = XLSX.utils.sheet_to_json(ws);
    },
    handleExport() {
      const ws = XLSX.utils.json_to_sheet(this.data);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Data");
      XLSX.writeFile(wb, "export.xlsx");
    }
  }
};
</script>
```

## Web Workers

SheetJS is suitable for Web Workers since it uses plain JS objects:

```js
// worker.js
self.onmessage = (e) => {
  const wb = XLSX.read(e.data);
  const ws = wb.Sheets[wb.SheetNames[0]];
  const json = XLSX.utils.sheet_to_json(ws);
  self.postMessage(json);
};
```

```js
// main.js
const worker = new Worker("worker.js");
worker.onmessage = (e) => {
  console.log("Parsed data:", e.data);
};
worker.postMessage(arrayBuffer);
```

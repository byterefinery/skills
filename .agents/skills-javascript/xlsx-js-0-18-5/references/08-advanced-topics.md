# Advanced Topics

## Merged Cells

Merged cells are stored as a range in `!merges`. Only the top-left cell holds the value; other cells are stubs (`t: "z"`).

```js
// Define merges
ws["!merges"] = [
  { s: { r: 0, c: 0 }, e: { r: 0, c: 2 } }  // A1:C1 merged
];

// Read merges
for (const merge of ws["!merges"] || []) {
  const start = XLSX.utils.encode_cell(merge.s);
  const end = XLSX.utils.encode_cell(merge.e);
  const value = ws[XLSX.utils.encode_cell(merge.s)]?.v;
  console.log(`${start}:${end} = ${value}`);
}

// Get value for any cell in a merge range
function getMergedValue(ws, addr) {
  const cell = ws[addr];
  if (cell && cell.t !== "z") return cell.v;
  // Check if this cell is part of a merge
  const rc = XLSX.utils.decode_cell(addr);
  for (const merge of ws["!merges"] || []) {
    if (rc.r >= merge.s.r && rc.r <= merge.e.r &&
        rc.c >= merge.s.c && rc.c <= merge.e.c) {
      return ws[XLSX.utils.encode_cell(merge.s)]?.v;
    }
  }
  return undefined;
}
```

## Hyperlinks

```js
// External hyperlink
XLSX.utils.cell_set_hyperlink(ws["A1"], "https://example.com", "Visit Example");

// Internal hyperlink (to another sheet/cell)
XLSX.utils.cell_set_internal_link(ws["A2"], "'Sheet2'!B5", "Go to Sheet2");

// Read hyperlinks
const cell = ws["A1"];
if (cell.l) {
  console.log("Target:", cell.l.Target);
  console.log("Tooltip:", cell.l.Tooltip);
}
```

## Cell Comments

```js
// Add comment
XLSX.utils.cell_add_comment(ws["A1"], "This is important", "Author");

// Read comments
const cell = ws["A1"];
if (cell.c) {
  for (const comment of cell.c) {
    console.log(`[${comment.a}]: ${comment.t}`);
  }
}
```

## Sheet Protection

```js
// Set protection
ws["!protect"] = {
  password: "secret",
  selectLockedCells: true,
  selectUnlockedCells: true,
  formatCells: false,
  formatColumns: false,
  formatRows: false,
  insertColumns: false,
  insertRows: false,
  insertHyperlinks: false,
  deleteColumns: false,
  deleteRows: false,
  sort: false,
  autoFilter: false,
  pivotTables: false,
  objects: true,
  scenarios: true
};
```

## AutoFilter

```js
// Set autofilter range
ws["!autofilter"] = { ref: "A1:D10" };

// Read autofilter
if (ws["!autofilter"]) {
  console.log("Filter range:", ws["!autofilter"].ref);
}
```

## Column Properties

```js
// Set column widths and visibility
ws["!cols"] = [
  { wch: 20, hidden: false },   // Column A: 20 chars wide
  { wch: 10, hidden: true },    // Column B: 10 chars, hidden
  { wch: 15, level: 1 },        // Column C: grouped (outline level 1)
  { wpx: 100 },                  // Column D: 100 pixels wide
];

// Calculate column widths from data
function autoColumnWidths(ws) {
  const range = XLSX.utils.decode_range(ws["!ref"]);
  const widths = [];
  for (let C = range.s.c; C <= range.e.c; ++C) {
    let maxWidth = 0;
    for (let R = range.s.r; R <= range.e.r; ++R) {
      const addr = XLSX.utils.encode_cell({ r: R, c: C });
      const cell = ws[addr];
      if (cell && cell.w) {
        maxWidth = Math.max(maxWidth, cell.w.length);
      } else if (cell && cell.v != null) {
        maxWidth = Math.max(maxWidth, String(cell.v).length);
      }
    }
    widths.push({ wch: maxWidth + 2 }); // +2 for padding
  }
  ws["!cols"] = widths;
}
```

## Row Properties

```js
// Set row heights and visibility
ws["!rows"] = [
  { hpt: 30, hidden: false },   // Row 1: 30 points tall
  { hpx: 50, hidden: true },    // Row 2: 50 pixels, hidden
  { level: 1 },                  // Row 3: grouped
];
```

## Page Margins

```js
ws["!margins"] = {
  left: 0.7,      // inches
  right: 0.7,
  top: 0.75,
  bottom: 0.75,
  header: 0.3,
  footer: 0.3
};
```

## Number Formats

```js
// Common Excel number format codes
const formats = {
  general: "General",
  integer: "0",
  decimal2: "0.00",
  comma: "#,##0",
  comma2: "#,##0.00",
  percentage: "0%",
  percentage2: "0.00%",
  scientific: "0.00E+00",
  fraction: "# ?/?",
  date: "yyyy-mm-dd",
  datetime: "yyyy-mm-dd hh:mm:ss",
  time: "hh:mm:ss",
  currency: "$#,##0.00",
  euro: "€#,##0.00",
};

// Set format on a cell
XLSX.utils.cell_set_number_format(ws["B2"], formats.comma2);

// Read format (requires cellNF: true in read options)
const wb = XLSX.readFile("data.xlsx", { cellNF: true });
console.log(ws["B2"].z); // "#,##0.00"
```

## Date Handling

```js
// Read dates as Date objects
const wb = XLSX.readFile("data.xlsx", { cellDates: true });
const cell = ws["A1"];
if (cell.t === "d") {
  console.log(cell.v instanceof Date); // true
  console.log(cell.v.toISOString());
}

// Read dates as serial numbers (default)
const wb = XLSX.readFile("data.xlsx");
// cell.t === "n", cell.v is a number like 44927

// Convert Excel serial number to Date
function excelSerialToDate(serial) {
  // Excel's epoch is Jan 0, 1900 (not Jan 1)
  // Excel incorrectly treats 1900 as a leap year
  const utc_days = Math.floor(serial - 25569);
  return new Date(utc_days * 86400 * 1000);
}

// Custom date format on read
const wb = XLSX.readFile("data.xlsx", {
  cellDates: true,
  dateNF: "mm/dd/yyyy"
});
```

## 1904 Date System

Some Excel files use the 1904 date system (Mac Excel legacy).

```js
const wb = XLSX.readFile("data.xlsx");
if (wb.Workbook?.WBProps?.date1904) {
  console.log("This file uses the 1904 date system");
  // Dates are offset by 1462 days
}
```

## Defined Names

```js
// Read defined names
const names = wb.Workbook?.Names || [];
for (const name of names) {
  console.log(`${name.Name} = ${name.Ref}`);
}

// Add defined name
if (!wb.Workbook) wb.Workbook = {};
if (!wb.Workbook.Names) wb.Workbook.Names = [];
wb.Workbook.Names.push({
  Name: "DataRange",
  Ref: "Sheet1!A1:D100",
  Comment: "Main data range"
});
```

## Workbook Properties

```js
// Read properties
console.log(wb.Props?.Title);
console.log(wb.Props?.Author);
console.log(wb.Props?.CreatedDate);

// Override on write
XLSX.writeFile(wb, "output.xlsx", {
  Props: {
    Title: "Quarterly Report",
    Author: "Analytics Team",
    Subject: "Q4 2024",
    Company: "Acme Corp",
    Keywords: "report, quarterly, data",
    Comments: "Auto-generated by system"
  }
});
```

## Sheet Visibility

```js
// Set visibility
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 0); // visible
XLSX.utils.book_set_sheet_visibility(wb, "Sheet2", 1); // hidden
XLSX.utils.book_set_sheet_visibility(wb, "Sheet3", 2); // very hidden

// Read visibility
const sheetProps = wb.Workbook?.Sheets || [];
for (const sp of sheetProps) {
  const vis = sp.Hidden === 0 ? "visible" : sp.Hidden === 1 ? "hidden" : "very hidden";
  console.log(`${sp.name}: ${vis}`);
}
```

## Renaming and Reordering Sheets

```js
// Rename a sheet
const oldName = "Sheet1";
const newName = "Data";
wb.Sheets[newName] = wb.Sheets[oldName];
delete wb.Sheets[oldName];
wb.SheetNames = wb.SheetNames.map(n => n === oldName ? newName : n);

// Reorder sheets
const names = [...wb.SheetNames];
[names[0], names[1]] = [names[1], names[0]]; // swap first two
wb.SheetNames = names;
// Update Workbook.Sheets order if present
if (wb.Workbook?.Sheets) {
  wb.Workbook.Sheets = names.map(name =>
    wb.Workbook.Sheets.find(s => s.name === name)
  );
}
```

## Array Formulas

```js
// Set array formula
XLSX.utils.sheet_set_array_formula(
  ws,
  "D1:D10",
  "SUMPRODUCT(A1:A10,B1:B10)"
);

// Dynamic array formula
XLSX.utils.sheet_set_array_formula(ws, "E1", "SORT(A1:A10)", true);
```

## Formulae

```js
// Cell with formula
ws["A1"] = { t: "n", f: "SUM(B1:B10)", v: 55 };

// Read all formulae
const formulae = XLSX.utils.sheet_to_formulae(ws);
// ["A1=SUM(B1:B10)"]

// Read individual formula
if (ws["A1"]?.f) {
  console.log("Formula:", ws["A1"].f);
  console.log("Result:", ws["A1"].v);
}
```

## VBA Macros

```js
// Read workbook with macros
const wb = XLSX.readFile("macro.xlsm", { bookVBA: true });

// The VBA project is available as wb.vbaraw (CFB blob)

// Write with macros
XLSX.writeFile(wb, "output.xlsm", {
  bookType: "xlsm",
  bookVBA: true
});
```

## Performance Tips

- Use `bookSheets: true` to get sheet names without parsing data
- Use `bookProps: true` to get metadata without parsing cells
- Use `sheets: [0]` to parse only specific sheets
- Use `sheetRows: N` to limit rows parsed
- For large files, consider `bookType: "xlsb"` (smaller, faster)
- Use `compression: true` when writing large XLSX files
- For streaming large CSV output, use `XLSX.stream.to_csv()`

# Advanced Topics

## Merged Cells

### Creating Merges

```js
ws["!merges"] = [
  XLSX.utils.decode_range("A1:B2"),
  XLSX.utils.decode_range("C1:C3")
];
```

Or manually:

```js
ws["!merges"] = [
  { s: { c: 0, r: 0 }, e: { c: 1, r: 1 } },  // A1:B2
  { s: { c: 2, r: 0 }, e: { c: 2, r: 2 } }   // C1:C3
];
```

### Adding Merges Safely

```js
function sheet_add_merge(ws, range) {
  const merge = typeof range == "string"
    ? XLSX.utils.decode_range(range)
    : range;

  if (!ws["!merges"]) ws["!merges"] = [];

  // Check for overlap
  for (const existing of ws["!merges"]) {
    if (
      merge.e.r >= existing.s.r && existing.e.r >= merge.s.r &&
      merge.e.c >= existing.s.c && existing.e.c >= merge.s.c
    ) {
      throw new Error(
        XLSX.utils.encode_range(merge) + " overlaps " +
        XLSX.utils.encode_range(existing)
      );
    }
  }

  ws["!merges"].push(merge);
}
```

### Merged Cell Behavior

- Only the top-left cell stores the value
- Covered cells are stubs (type `"z"`) or absent
- `sheet_to_json` and `sheet_to_csv` include all cells in merge range
- Merges are not supported in CSV, TXT, and other text formats on export

## Hyperlinks

### External Links

```js
ws["A1"].l = { Target: "https://sheetjs.com", Tooltip: "SheetJS" };
ws["A2"].l = { Target: "mailto:user@example.com" };
ws["A3"].l = { Target: "file:///path/to/file.xlsx" };
```

### Internal Links

```js
ws["A1"].l = { Target: "#E2" };                      // same sheet
ws["A2"].l = { Target: "#Sheet2!A1" };               // cross-sheet
ws["A3"].l = { Target: "#MyDefinedName" };            // defined name
```

### Helper Functions

```js
XLSX.utils.cell_set_hyperlink(ws["A1"], "https://example.com", "Click");
XLSX.utils.cell_set_internal_link(ws["A1"], "#Sheet2!A1", "Go");
```

## Cell Comments

### Adding Comments

```js
if (!ws["A1"].c) ws["A1"].c = [];
ws["A1"].c.push({ a: "Author", t: "This is a comment" });
```

### Threaded Comments

```js
if (!ws["A1"].c) ws["A1"].c = [];
ws["A1"].c.push({ a: "Alice", t: "First comment", T: true });
ws["A1"].c.push({ a: "Bob", t: "Reply to Alice", T: true });
```

### Hidden Comments

```js
if (!ws["A1"].c) ws["A1"].c = [];
ws["A1"].c.hidden = true;
ws["A1"].c.push({ a: "Author", t: "Hidden comment" });
```

### Helper Function

```js
XLSX.utils.cell_add_comment(ws["A1"], "Comment text", "Author");
```

## Sheet Protection

```js
ws["!protect"] = {
  password: "secret",
  selectLockedCells: true,
  selectUnlockedCells: true,
  formatCells: false,
  formatColumns: false,
  formatRows: false,
  insertColumns: false,
  insertRows: false,
  deleteColumns: false,
  deleteRows: false,
  sort: false,
  autoFilter: false,
  pivotTables: false,
  objects: true,
  scenarios: true
};
```

Password uses XOR obfuscation — not real encryption.

## AutoFilter

```js
ws["!autofilter"] = { ref: "A1:D10" };
```

The range should include the header row.

## Column Properties

### Setting Widths

```js
ws["!cols"] = [
  { wch: 20 },     // column A: 20 characters
  { wpx: 100 },    // column B: 100 pixels
  { width: 15 }    // column C: 15 MDW units
];
```

Width priority: `width` → `wpx` → `wch`.

### Hiding Columns

```js
if (!ws["!cols"]) ws["!cols"] = [];
ws["!cols"][2] = { wch: 8, hidden: true };  // hide column C
```

### Column Grouping

```js
// Group columns B-D (indices 1-3)
for (let i = 1; i <= 3; i++) {
  if (!ws["!cols"]) ws["!cols"] = [];
  if (!ws["!cols"][i]) ws["!cols"][i] = { wch: 8 };
  ws["!cols"][i].level = 1;
}
```

## Row Properties

### Setting Heights

```js
ws["!rows"] = [];
ws["!rows"][0] = { hpx: 30 };   // first row: 30 pixels
ws["!rows"][1] = { hpt: 20 };   // second row: 20 points
```

Height priority: `hpx` → `hpt`.

### Hiding Rows

```js
if (!ws["!rows"]) ws["!rows"] = [];
ws["!rows"][2] = { hpx: 20, hidden: true };  // hide row 3
```

### Row Grouping

```js
// Group rows 2-5 (indices 1-4)
for (let i = 1; i <= 4; i++) {
  if (!ws["!rows"]) ws["!rows"] = [];
  if (!ws["!rows"][i]) ws["!rows"][i] = { hpx: 20 };
  ws["!rows"][i].level = 1;
}
```

## Defined Names

### Creating Defined Names

```js
if (!wb.Workbook) wb.Workbook = {};
if (!wb.Workbook.Names) wb.Workbook.Names = [];

// Workbook-level name
wb.Workbook.Names.push({
  Name: "MyData",
  Ref: "Sheet1!$A$1:$D$10"
});

// Sheet-scoped name
wb.Workbook.Names.push({
  Name: "Total",
  Ref: "Sheet1!$E$1",
  Sheet: 0  // scoped to first sheet
});
```

### Reading Defined Names

```js
const wb = XLSX.read(data);
if (wb.Workbook?.Names) {
  wb.Workbook.Names.forEach(name => {
    console.log(name.Name, "→", name.Ref);
  });
}
```

## Sheet Visibility

### Setting Visibility

```js
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 0);  // visible
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 1);  // hidden
XLSX.utils.book_set_sheet_visibility(wb, "Sheet1", 2);  // very hidden
```

### Manual Setting

```js
const idx = wb.SheetNames.indexOf("Sheet1");
if (!wb.Workbook) wb.Workbook = {};
if (!wb.Workbook.Sheets) wb.Workbook.Sheets = [];
if (!wb.Workbook.Sheets[idx]) wb.Workbook.Sheets[idx] = {};
wb.Workbook.Sheets[idx].Hidden = 1;  // hidden
```

### Checking Visibility

```js
function getSheetVisibility(wb, sheetName) {
  const idx = wb.SheetNames.indexOf(sheetName);
  if (idx === -1) throw new Error(`Sheet ${sheetName} not found`);
  return wb?.Workbook?.Sheets?.[idx]?.Hidden || 0;
}
```

## Outline Behavior

```js
ws["!outline"] = {
  above: true,   // show summary rows above detail
  left: true     // show summary columns to left of detail
};
```

## Page Margins

```js
ws["!margins"] = {
  left: 0.7,
  right: 0.7,
  top: 0.75,
  bottom: 0.75,
  header: 0.3,
  footer: 0.3
};
```

## Renaming Sheets

```js
const ws = wb.Sheets["Old Name"];
wb.Sheets["New Name"] = ws;
delete wb.Sheets["Old Name"];
wb.SheetNames = wb.SheetNames.map(n =>
  n === "Old Name" ? "New Name" : n
);
```

Sheet names must be unique and ≤31 characters.

# Data Model — Common Spreadsheet Format

## Workbook Object

```js
{
  SheetNames: ["Sheet1", "Sheet2"],
  Sheets: {
    "Sheet1": { /* worksheet object */ },
    "Sheet2": { /* worksheet object */ }
  },
  Props: {
    Title: "Report",
    Subject: "Q4",
    Author: "John",
    Company: "Acme",
    Keywords: "data",
    Comments: "Auto-generated",
    CreatedDate: new Date(),
    ModifiedDate: new Date(),
    LastAuthor: "Jane",
    Category: "Reports",
    Manager: "Boss",
  },
  Custprops: { /* custom document properties */ },
  Workbook: {
    Sheets: [
      { name: "Sheet1", Hidden: 0, CodeName: "Sheet1" },
      { name: "Sheet2", Hidden: 1 },
    ],
    Names: [
      { Name: "MyRange", Ref: "Sheet1!A1:D10", Sheet: 0, Comment: "My range" }
    ],
    Views: [{ RTL: false }],
    WBProps: { date1904: false, filterPrivacy: false, CodeName: "" }
  },
  vbaraw: /* CFB blob for VBA macros (when bookVBA: true) */
}
```

## Worksheet Object

```js
{
  // Cell data — keyed by A1-style addresses
  "A1": { v: "Name", t: "s" },
  "A2": { v: "Alice", t: "s" },
  "B1": { v: "Age", t: "s" },
  "B2": { v: 30, t: "n" },

  // Special keys (prefixed with !)
  "!ref": "A1:B10",        // used range
  "!type": "sheet",        // sheet type: "sheet" | "chart"
  "!cols": [               // column properties
    { wch: 15, wpx: 100, hidden: false, level: 0, MDW: 9 },
    { wch: 10, hidden: false }
  ],
  "!rows": [               // row properties
    { hpx: 20, hpt: 15, hidden: false, level: 0 }
  ],
  "!merges": [             // merged cell ranges
    { s: { r: 0, c: 0 }, e: { r: 0, c: 2 } }
  ],
  "!protect": {            // sheet protection
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
  },
  "!autofilter": { ref: "A1:D10" },
  "!margins": {            // page margins in inches
    left: 0.7, right: 0.7, top: 0.75, bottom: 0.75, header: 0.3, footer: 0.3
  }
}
```

## Cell Object (`CellObject`)

```js
{
  v: "Hello",        // raw value: string | number | boolean | Date
  w: "Hello",        // formatted text (display string)
  t: "s",            // type: "b" | "n" | "e" | "s" | "d" | "z"
  f: "SUM(B2:B10)",  // formula string
  F: "A1:A10",       // array formula range
  r: /* any */,      // rich text encoding
  h: "<b>Hello</b>", // HTML rendering of rich text
  c: [               // comments
    { t: "Note", a: "Author", T: false }
  ],
  z: "#,##0.00",     // number format string
  l: {               // hyperlink
    Target: "https://example.com",
    Tooltip: "Click here"
  },
  s: /* any */       // style/theme info (when cellStyles: true)
}
```

### Cell Data Types

| Type | Name | Description |
|---|---|---|
| `"b"` | Boolean | `true` / `false` |
| `"n"` | Number | Numeric value (includes dates as serial numbers when `cellDates: false`) |
| `"e"` | Error | Error code (number) |
| `"s"` | String | Text value |
| `"d"` | Date | JavaScript Date object (when `cellDates: true`) |
| `"z"` | Stub | Stub cell in merged range (no value) |

## Column Info (`ColInfo`)

```js
{
  hidden: false,    // column is hidden
  width: 10,        // Excel's "Max Digit Width" (width * 256 is integral)
  wpx: 100,         // width in screen pixels
  wch: 15,          // width in characters
  level: 0,         // outline/group level
  MDW: 9,           // Excel's Max Digit Width unit (always integral)
  DBF: {            // DBF field header (for DBF format)
    name: "Field1",
    type: "C",
    len: 20,
    dec: 0
  }
}
```

## Row Info (`RowInfo`)

```js
{
  hidden: false,    // row is hidden
  hpx: 20,          // height in screen pixels
  hpt: 15,          // height in points
  level: 0          // outline/group level
}
```

## Range Object

```js
{
  s: { r: 0, c: 0 },  // start: { row, col } (0-indexed)
  e: { r: 9, c: 3 }   // end: { row, col } (0-indexed)
}
// Represents "A1:D10"
```

## Cell Address Object

```js
{ r: 0, c: 0 }  // row 0, column 0 = "A1"
```

## Hyperlink Object

```js
{
  Target: "https://example.com",  // URL
  Tooltip: "Visit Example"        // tooltip text
}
```

## Comment Object

```js
{
  t: "Comment text",   // comment content
  a: "Author Name",    // author
  T: false             // true if part of a thread
}
```

## Defined Name Object

```js
{
  Name: "MyRange",      // name
  Ref: "Sheet1!A1:D10", // reference
  Sheet: 0,             // scope (undefined = workbook scope)
  Comment: "My range"   // comment
}
```

## Sheet Props

```js
{
  name: "Sheet1",       // sheet name
  Hidden: 0,            // 0 = visible, 1 = hidden, 2 = very hidden
  CodeName: "Sheet1"    // VBA code name
}
```

## Workbook Properties (`WBProps`)

```js
{
  date1904: false,      // true = 1904 date system, false = 1900
  filterPrivacy: false, // warn about personal info on save
  CodeName: ""          // VBA project code name
}
```

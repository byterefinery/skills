# Data Model — Common Spreadsheet Format (CSF)

## Workbook Object

```js
{
  Sheets: {
    "Sheet1": WorkSheet,
    "Sheet2": WorkSheet
  },
  SheetNames: ["Sheet1", "Sheet2"],
  Props?: FullProperties,
  Custprops?: object,
  Workbook?: WBProps,
  vbaraw?: any,
  bookType?: BookType
}
```

- `Sheets` — dictionary keyed by sheet name
- `SheetNames` — ordered list of sheet names
- `Props` — standard file properties (Title, Author, Subject, etc.)
- `Custprops` — custom properties
- `Workbook` — workbook-level attributes (defined names, views, sheet metadata)
- `vbaraw` — raw VBA CFB object (when `bookVBA: true`)
- `bookType` — detected file type when parsed from file (e.g., `"xlsx"`, `"xlsb"`)

## Worksheet Object

### Sparse Mode (default)

Cells stored as properties keyed by A1-style address:

```js
{
  "!ref": "A1:D10",
  "!cols": [{ wch: 20 }, { wch: 10 }],
  "!rows": [{ hpx: 30 }],
  "!merges": [{ s: { c: 0, r: 0 }, e: { c: 2, r: 0 } }],
  "!protect": { password: "secret" },
  "!autofilter": { ref: "A1:D10" },
  "!margins": { left: 0.7, right: 0.7, top: 0.75, bottom: 0.75 },
  "!outline": { above: false, left: false },
  "!type": "sheet",
  "A1": { t: "s", v: "Name" },
  "A2": { t: "n", v: 42 },
  // ... cells keyed by address
}
```

### Dense Mode (`dense: true`)

Cells stored in `!data` array of arrays:

```js
{
  "!ref": "A1:D10",
  "!data": [
    [{ t: "s", v: "Name" }, { t: "n", v: 42 }],  // row 0
    [{ t: "s", v: "Age" }, { t: "n", v: 25 }],   // row 1
    // ...
  ]
}
```

Access cells with `ws["!data"][row][col]` (0-indexed). Utility functions auto-detect dense sheets.

### Sheet Properties

| Property | Description |
|---|---|
| `!ref` | A1-style range string (e.g., `"A1:D10"`) |
| `!data` | Dense-mode cell array (`CellObject[][]`) |
| `!cols` | Column properties array (`ColInfo[]`) |
| `!rows` | Row properties array (`RowInfo[]`) |
| `!merges` | Merge ranges (`Range[]`) |
| `!protect` | Sheet protection (`ProtectInfo`) |
| `!autofilter` | AutoFilter range (`{ ref: string }`) |
| `!margins` | Page margins (`MarginInfo`) |
| `!outline` | Outline behavior (`{ above?: boolean, left?: boolean }`) |
| `!type` | Sheet type: `"sheet"`, `"chart"`, `"macro"`, `"dialog"` |

### Page Margins

```js
ws["!margins"] = {
  left: 0.7,    // inches
  right: 0.7,
  top: 0.75,
  bottom: 0.75,
  header: 0.3,
  footer: 0.3
};
```

Presets: `"normal"` (above), `"wide"` (all 1.0, header/footer 0.5), `"narrow"` (left/right 0.25, others same as normal).

## Cell Object (`CellObject`)

```js
{
  t: "n",           // cell type
  v: 42,            // raw value
  w: "42",          // formatted text
  z: "0",           // number format string
  f: "A1+B1",       // formula (A1-style, no leading =)
  F: "C1:C1",       // array formula range
  D: false,         // dynamic array formula
  l: { Target: "https://example.com", Tooltip: "Link" },  // hyperlink
  c: [{ a: "Author", t: "Comment text" }],  // comments
  r: undefined,     // rich text encoding
  h: undefined,     // HTML rendering of rich text
  s: undefined      // style/theme info
}
```

### Cell Types

| Type | Description |
|---|---|
| `"b"` | Boolean — value is JS `boolean` |
| `"n"` | Number — value is JS `number` (includes dates as serial numbers) |
| `"e"` | Error — value is numeric error code, `w` holds error string |
| `"s"` | String — value is JS `string` |
| `"d"` | Date — value is JS `Date` object or ISO 8601 string |
| `"z"` | Stub — blank placeholder (e.g., cells under merge range) |

### Error Codes

| Error | Code |
|---|---|
| `#NULL!` | `0x00` |
| `#DIV/0!` | `0x07` |
| `#VALUE!` | `0x0F` |
| `#REF!` | `0x17` |
| `#NAME?` | `0x1D` |
| `#NUM!` | `0x24` |
| `#N/A` | `0x2A` |
| `#GETTING_DATA` | `0x2B` |

## Column Properties (`ColInfo`)

```js
{
  hidden: false,    // if true, column is hidden
  wch: 8,           // inner width in characters (MDW units)
  wpx: 64,          // width in screen pixels
  width: 10,        // outer width in MDW units
  level: 0,         // outline/group level (0-7)
  MDW: 7,           // Max Digit Width unit
  DBF: {...}        // DBF field header (for DBF format)
}
```

Width priority: `width` → `wpx` → `wch`.

## Row Properties (`RowInfo`)

```js
{
  hidden: false,    // if true, row is hidden
  hpx: 20,          // height in screen pixels
  hpt: 15,          // height in points
  level: 0          // outline/group level (0-7)
}
```

Height priority: `hpx` → `hpt`.

## Sheet Protection (`ProtectInfo`)

```js
{
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
}
```

Password uses XOR obfuscation (not real encryption).

## Workbook-Level Attributes (`WBProps`)

```js
{
  Sheets?: SheetProps[],    // sheet metadata (visibility, CodeName)
  Names?: DefinedName[],    // defined names
  Views?: WBView[],         // workbook views
  WBProps?: WorkbookProperties  // date1904, filterPrivacy, CodeName
}
```

### Defined Names

```js
{
  Name: "MyData",           // case-sensitive name
  Ref: "Sheet1!$A$1:$D$10", // A1-style reference (use $ for absolute)
  Sheet: 0,                 // scope: sheet index or undefined (workbook)
  Comment: "Data range"     // comment
}
```

Initialize before use: `if(!wb.Workbook) wb.Workbook = {}; if(!wb.Workbook.Names) wb.Workbook.Names = [];`

## Cell Comments

```js
cell.c = [];
cell.c.push({
  a: "Author",              // author (optional for notes, shown for threads)
  t: "Comment text",        // text (required)
  T: true                   // if true, threaded comment part
});
cell.c.hidden = true;       // hide comment by default
```

## Hyperlinks

```js
cell.l = {
  Target: "https://example.com",   // required: link target
  Tooltip: "Click here"            // optional: tooltip (max 255 chars for Excel)
};
```

Internal links use `#` prefix: `#E2`, `#Sheet2!E2`, `#DefinedName`.

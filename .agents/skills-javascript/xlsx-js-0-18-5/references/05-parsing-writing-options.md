# Parsing and Writing Options

## Parsing Options (`read` / `readFile`)

### Input Type

```js
{ type: "buffer" }
```

| Value | Input Type | Notes |
|---|---|---|
| `"buffer"` | Node.js `Buffer` | Default for Buffer input |
| `"array"` | `Uint8Array`, `ArrayBuffer`, `number[]` | Default for typed arrays |
| `"binary"` | Binary string | Each char = 1 byte |
| `"base64"` | Base64 string | For base64-encoded data |
| `"string"` | UTF-8 string | For HTML/CSV text input |
| `"file"` | File path string | Used by `readFile` internally |

### Cell Content Options

```js
{
  cellDates: false,      // Dates as Date objects ("d") vs serial numbers ("n")
  cellFormula: true,     // Preserve formulae in .f field
  cellHTML: true,        // Parse rich text to .h field
  cellNF: false,         // Save number format string to .z field
  cellStyles: false,     // Save style/theme to .s field
  cellText: true,        // Generate formatted text in .w field
}
```

- **`cellDates: true`** — critical for date handling. Without it, dates appear as Excel serial numbers (e.g., `44927` = Jan 1, 2023).
- **`cellNF: true`** — needed to read number format strings (e.g., `"#,##0.00"`, `"yyyy-mm-dd"`).
- **`cellStyles: true`** — reads style information but write support is limited in CE.

### Date Options

```js
{
  dateNF: "yyyy-mm-dd",  // Override default date format (Excel code 14)
}
```

Common format codes: `yyyy-mm-dd`, `mm/dd/yyyy`, `dd/mm/yyyy`, `yyyy-mm-dd hh:mm:ss`, `m/d/yy h:mm`.

### Structural Options

```js
{
  sheetStubs: false,     // Create cell objects for stub cells (default: false)
  bookDeps: false,       // Parse calculation chains (default: false)
  bookProps: false,      // Only parse workbook metadata (default: false)
  bookSheets: false,     // Only parse sheet names (default: false)
  bookFiles: false,      // Add raw file data to workbook object (default: false)
}
```

- **`bookProps: true`** — fast metadata extraction without parsing cells.
- **`bookSheets: true`** — fastest option, only gets sheet names.

### Sheet Selection

```js
{
  sheets: [0],           // Parse only sheet at index 0
  sheets: ["Sheet1"],    // Parse only the named sheet
  sheets: [0, 2],        // Parse multiple sheets
}
```

### Delimiter-Separated Format Options

```js
{
  FS: ",",               // Field separator (delimiter) override
  raw: false,            // Don't parse values in plaintext formats
}
```

### Other Options

```js
{
  codepage: 1252,        // Default codepage for legacy XLS formats
  password: "",          // Password for encrypted files
  WTF: false,            // Throw errors on unsupported features
  xlfn: false,           // Preserve _xlfn. prefixes in formula function names
  sheetRows: 0,          // Limit: read only first N rows (0 = unlimited)
}
```

## Writing Options (`write` / `writeFile`)

### Output Type

```js
{ type: "buffer" }
```

| Value | Return Type | Notes |
|---|---|---|
| `"buffer"` | Node.js `Buffer` | Default for Node.js |
| `"array"` | `number[]` | Array of bytes |
| `"binary"` | Binary string | Each char = 1 byte |
| `"base64"` | Base64 string | For data URLs |
| `"string"` | UTF-8 string | For text formats (CSV, HTML) |
| `"file"` | void | Write to file (used by `writeFile`) |

### Format Options

```js
{
  bookType: "xlsx",      // Output format
  bookSST: false,        // Generate Shared String Table
  compression: true,     // ZIP compression for ZIP-based formats
}
```

- **`bookSST: true`** — can reduce file size for workbooks with many repeated strings.
- **`compression: true`** — reduces file size but increases CPU time.

### Cell Options

```js
{
  cellDates: false,      // Write native dates vs Excel date codes
  cellStyles: false,     // Export style/theme info
  bookVBA: false,        // Include VBA macros
}
```

### Warning Suppression

```js
{
  ignoreEC: true,        // Suppress "number stored as text" warnings (default: true)
}
```

### Sheet Selection (for single-sheet formats)

```js
{
  sheet: "Sheet1",       // Which sheet to export (for CSV, TXT, etc.)
}
```

### Workbook Properties Override

```js
{
  Props: {
    Title: "Report",
    Subject: "Q4 Sales",
    Author: "Analytics Team",
    Manager: "Director",
    Company: "Acme Corp",
    Category: "Reports",
    Keywords: "sales, q4",
    Comments: "Auto-generated report",
  }
}
```

### Password Protection

```js
{
  password: "secret",    // Password for encrypted output files
}
```

## `sheet_to_json` Options

```js
{
  header: "A",           // "A" = use row A as keys, 1 = array-of-arrays, string[] = custom
  range: "A1:D10",       // Limit to specific range
  blankrows: false,      // Include blank rows
  defval: null,          // Default value for empty cells
  raw: false,            // Return raw values vs formatted text
  skipHidden: false,     // Skip hidden rows/columns
  dateNF: "yyyy-mm-dd",  // Date format for output
  rawNumbers: true,      // Return raw numbers vs formatted
}
```

## `sheet_to_csv` Options

```js
{
  FS: ",",               // Field separator
  RS: "\r\n",            // Record separator
  strip: false,          // Remove trailing field separators
  blankrows: false,      // Include blank lines
  skipHidden: false,     // Skip hidden rows/columns
  forceQuotes: false,    // Force quotes around all fields
  dateNF: "yyyy-mm-dd",  // Date format
  rawNumbers: true,      // Raw numbers vs formatted
}
```

## `aoa_to_sheet` / `json_to_sheet` Options

```js
{
  origin: "A1",          // Starting cell (string, {r, c}, or row number)
  sheetStubs: false,     // Create stub cells for empty positions
  dateNF: "yyyy-mm-dd",  // Date format
}
```

For `json_to_sheet` only:
```js
{
  header: ["col1", "col2"],  // Custom column order
  skipHeader: false,         // Omit header row
}
```

## `table_to_sheet` / `table_to_book` Options

```js
{
  raw: false,            // Don't parse cell values
  sheetRows: 0,          // Max rows to parse (0 = unlimited)
  display: false,        // Skip hidden rows/cells
  origin: "A1",          // Starting cell
  sheet: "Sheet1",       // Worksheet name (table_to_book only)
}
```

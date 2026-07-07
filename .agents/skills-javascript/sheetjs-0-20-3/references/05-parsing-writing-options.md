# Parsing and Writing Options

## Parsing Options (`read`, `readFile`)

### Cell-Level Options

| Option | Default | Description |
|---|---|---|
| `cellDates` | `false` | Store dates as Date objects (type `"d"`) instead of numbers |
| `cellFormula` | `true` | Save formulae to `.f` field |
| `cellHTML` | `true` | Parse rich text and save HTML to `.h` field |
| `cellNF` | `false` | Save number format string to `.z` field |
| `cellStyles` | `false` | Save style info to `.s` field + row/col properties |
| `cellText` | `true` | Generate formatted text in `.w` field |
| `dateNF` | — | Override default date format string (code 14) |

### Sheet-Level Options

| Option | Default | Description |
|---|---|---|
| `dense` | `false` | Generate dense-mode worksheets (`!data` array) |
| `sheetStubs` | `false` | Create type `"z"` cells for stub/empty cells |
| `sheetRows` | `0` | If >0, read only the first N rows |
| `nodim` | `false` | Ignore self-reported dimensions, compute from cells |
| `sheets` | — | Parse only specified sheets (index, name, or array) |

### Book-Level Options

| Option | Default | Description |
|---|---|---|
| `bookDeps` | `false` | Parse calculation chains |
| `bookFiles` | `false` | Preserve raw sub-files in workbook object |
| `bookProps` | `false` | Only parse workbook metadata (skip sheet data) |
| `bookSheets` | `false` | Only parse sheet names (skip sheet data) |
| `bookVBA` | `false` | Extract VBA blob to `vbaraw` property |

### File-Level Options

| Option | Default | Description |
|---|---|---|
| `type` | — | Input encoding: `base64`, `binary`, `string`, `buffer`, `array`, `file` |
| `raw` | `false` | Disable value parsing in plaintext formats |
| `codepage` | — | Default codepage for legacy formats (requires `set_cptable`) |
| `password` | `""` | Password for XOR-encrypted XLS files |
| `FS` | — | DSV field separator override |
| `PRN` | `false` | Allow parsing of Lotus PRN files |
| `UTC` | `true` | Parse text dates/times using UTC |
| `xlfn` | `false` | Preserve `_xlfn.` prefixes in formula names |
| `WTF` | `false` | Do not suppress worksheet parsing errors |

## Writing Options (`write`, `writeFile`)

### Output Options

| Option | Default | Description |
|---|---|---|
| `type` | — | Output encoding: `base64`, `binary`, `string`, `buffer`, `array`, `file` |
| `bookType` | `"xlsx"` | Output format (inferred from extension in `writeFile`) |
| `compression` | `false` | Enable ZIP compression (smaller files, slower) |

### Cell-Level Options

| Option | Default | Description |
|---|---|---|
| `cellDates` | `false` | Write native dates instead of date codes |
| `cellStyles` | `false` | Export style info + row/col properties |

### Book-Level Options

| Option | Default | Description |
|---|---|---|
| `bookSST` | `false` | Use Shared String Table (better compatibility) |
| `bookVBA` | — | Add VBA blob from workbook object |
| `Props` | — | Override workbook properties |
| `themeXLSX` | — | Override theme XML for XLSX/XLSB/XLSM |

### File-Level Options

| Option | Default | Description |
|---|---|---|
| `codepage` | — | Codepage for legacy formats |
| `ignoreEC` | `true` | Suppress "number stored as text" warnings |
| `numbers` | — | Base64 NUMBERS payload (required for `.numbers` export) |
| `sheet` | — | Target sheet for single-sheet formats |
| `FS` | `","` | Field separator for CSV/Text output |
| `RS` | `"\n"` | Record separator for CSV/Text output |
| `WTF` | `false` | Show warnings for unsafe features |

## `sheet_to_json` Options

| Option | Default | Description |
|---|---|---|
| `header` | — | `1` = array-of-arrays, `"A"` = column labels, `string[]` = custom keys |
| `range` | — | `number` = starting row, `string` = A1 range |
| `blankrows` | — | `true` = include blank rows (default depends on `header`) |
| `defval` | — | Default value for empty cells |
| `raw` | `true` | `true` = raw values, `false` = formatted text |
| `skipHidden` | `false` | Skip hidden rows/columns |
| `dateNF` | FMT 14 | Date format for output |
| `UTC` | `false` | UTC date interpretation |

## `sheet_to_csv` / `sheet_to_txt` Options

| Option | Default | Description |
|---|---|---|
| `FS` | `","` | Field separator |
| `RS` | `"\n"` | Record separator |
| `strip` | `false` | Remove trailing field separators |
| `blankrows` | `true` | Include blank lines |
| `skipHidden` | `false` | Skip hidden rows/columns |
| `forceQuotes` | `false` | Force quotes around all fields |
| `dateNF` | FMT 14 | Date format |

## `aoa_to_sheet` / `sheet_add_aoa` Options

| Option | Default | Description |
|---|---|---|
| `dateNF` | FMT 14 | Date format |
| `cellDates` | `false` | Store dates as type `"d"` |
| `sheetStubs` | `false` | Create type `"z"` for `null` values |
| `nullError` | `false` | Emit `#NULL!` errors for `null` values |
| `UTC` | `false` | Interpret dates using UTC |
| `dense` | `false` | Emit dense sheets |
| `origin` | `"A1"` | Starting cell (for `sheet_add_aoa`) |

## `json_to_sheet` / `sheet_add_json` Options

| Option | Default | Description |
|---|---|---|
| `header` | — | Column order array |
| `dateNF` | FMT 14 | Date format |
| `cellDates` | `false` | Store dates as type `"d"` |
| `skipHeader` | `false` | Skip header row |
| `nullError` | `false` | Emit `#NULL!` for `null` |
| `UTC` | `false` | Interpret dates using UTC |
| `dense` | `false` | Emit dense sheets |
| `origin` | `"A1"` | Starting cell (for `sheet_add_json`) |

## `table_to_sheet` / `sheet_add_dom` Options

| Option | Default | Description |
|---|---|---|
| `raw` | — | If true, all cells are text |
| `dateNF` | `"m/d/yy"` | Date format |
| `cellDates` | `false` | Store dates as type `"d"` |
| `sheetRows` | `0` | Read only first N rows |
| `display` | `false` | Skip hidden rows/cells if true |
| `UTC` | `false` | Interpret dates as UTC |
| `origin` | `"A1"` | Starting cell (for `sheet_add_dom`) |
| `sheet` | `"Sheet1"` | Worksheet name (for `table_to_book`) |

# Excel Read — read_xlsx()

The `read_xlsx()` table function reads `.xlsx` files as queryable tables. XLSX files are ZIP archives containing XML parts; DuckDB parses them on-the-fly without extracting.

## Basic Usage

```sql
-- Direct file reference (replacement scan)
SELECT * FROM 'report.xlsx';

-- Explicit function call with options
SELECT * FROM read_xlsx('report.xlsx', header true);
```

Both forms are equivalent when no options are needed. The replacement scan automatically maps `.xlsx` extensions to `read_xlsx()`.

## Named Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `header` | BOOLEAN | auto-inferred | Treat first row as column names. Auto-detection checks if the first row looks like headers (non-numeric, distinct values). |
| `sheet` | VARCHAR | first sheet | Sheet name to read. Defaults to the primary (first) sheet in the workbook. |
| `all_varchar` | BOOLEAN | `false` | Read all cells as VARCHAR, bypassing type inference. Useful for heterogeneous columns. |
| `ignore_errors` | BOOLEAN | `false` | Silently replace uncastable cells with NULL instead of raising errors. |
| `range` | VARCHAR | auto-inferred | Cell range to read, e.g., `'A1:D100'`. Auto-detection finds the rectangular region between first consecutive non-empty row and first empty row. |
| `stop_at_empty` | BOOLEAN | `true` (auto) / `false` (explicit range) | Stop reading when an empty row is encountered. Defaults to `true` unless an explicit `range` is given. |
| `empty_as_varchar` | BOOLEAN | `false` | Treat empty cells as VARCHAR instead of DOUBLE during type inference. Prevents empty-first-row issues. |
| `normalize_names` | BOOLEAN | `false` | Normalize column names: lowercase, ASCII-only, spaces to underscores, prepend `_` for reserved keywords or digit-starting names. |

## Type Inference

### How It Works

Column types are inferred from the first "data" row (first row after header, or first non-empty row if no header):

1. **NUMBER cells** → Check cell style format:
   - Date-style format → `DATE`, `TIME`, or `TIMESTAMP`
   - Boolean-style format → `BOOLEAN`
   - No special format → `DOUBLE`
2. **SHARED_STRING / INLINE_STRING cells** → `VARCHAR`
3. **BOOLEAN cells** → `BOOLEAN`
4. **DATE cells** → `DATE`
5. **FORMULA_STRING cells** → `VARCHAR` (computed result as string)
6. **Empty cells** → `DOUBLE` by default, `VARCHAR` if `empty_as_varchar=true`

### Special Cases

- **TRUE/FALSE text**: String cells containing exactly `true` or `false` (case-insensitive) are inferred as `BOOLEAN`.
- **Mixed types in a column**: Type is determined by the first data row only. Later rows that don't match will fail unless `ignore_errors=true`.
- **All varchar mode**: Setting `all_varchar=true` skips all inference and returns everything as VARCHAR.

### Example: Handling Sparse Sheets

```sql
-- Default: stops at first empty row
SELECT * FROM read_xlsx('sparse.xlsx');

-- Read specific range including gaps
SELECT * FROM read_xlsx('sparse.xlsx', range 'A1:D100', header false);

-- Treat empty cells as VARCHAR to avoid type conflicts
SELECT * FROM read_xlsx('sparse.xlsx', empty_as_varchar true);
```

## Range Syntax

Ranges use Excel-style notation: `ColumnRow:ColumnRow`

```sql
-- Read specific cells
SELECT * FROM read_xlsx('file.xlsx', range 'A1:B10');

-- Read from row 5 onwards
SELECT * FROM read_xlsx('file.xlsx', range 'A5:Z1000');

-- Single cell
SELECT * FROM read_xlsx('file.xlsx', range 'C3:C3');
```

Range constraints:
- Maximum columns: 16,384 (XLSX limit)
- Maximum rows: 1,048,576 (XLSX limit)
- Start column must be ≤ end column
- Start row must be ≤ end row

## Column Name Handling

### Default Behavior
Column names are taken from the header row with whitespace trimmed. Names may contain any characters including spaces and special characters.

### Normalized Names (`normalize_names=true`)
```
Original          →  Normalized
"First Name"      →  first_name
"CAS#01"          →  cas_01
"123count"        →  _123count
"select"          →  _select
"" (empty)        →  _
"Über straße"     →  uber_strasse
```

Normalization rules:
1. UTF-8 NFKD decomposition
2. Keep only ASCII alphanumeric + underscore
3. Spaces become underscores
4. Trim leading/trailing whitespace
5. Collapse consecutive whitespace to single underscore
6. Lowercase everything
7. Prepend `_` if name starts with digit or is a SQL reserved keyword

## Sheet Selection

```sql
-- Read specific sheet by name
SELECT * FROM read_xlsx('file.xlsx', sheet 'Sales Data');

-- Default reads the first (primary) sheet
SELECT * FROM read_xlsx('file.xlsx');
```

Sheet names are case-sensitive. If a sheet name is not found, DuckDB provides suggestions:
```
Binder Error: Sheet "Sh" not found in xlsx file "file.xlsx"
Did you mean: "Sheet1", "My Sheet"
```

This error-message technique can be used for sheet discovery (see metadata reference).

## Performance Considerations

- **Streaming parse**: XLSX files are parsed as streaming XML, so memory usage is proportional to row chunk size, not total file size.
- **Shared strings table**: Extracted once at startup, then referenced by index during parsing.
- **Progress tracking**: `read_xlsx()` reports scan progress percentage via the table function progress callback.
- **Single-file only**: Glob patterns are resolved but only the first file is read. Use `UNION ALL` for multiple files.

## Error Handling

```sql
-- Ignore parse errors, replace with NULL
SELECT * FROM read_xlsx('file.xlsx', ignore_errors true);

-- All varchar to avoid casting issues entirely
SELECT * FROM read_xlsx('file.xlsx', all_varchar true);
```

Common errors:
- `No sheets found in xlsx file (is the file corrupt?)` — Invalid or non-XLSX file
- `Sheet "X" not found` — Wrong sheet name; check spelling and case
- `Failed to parse cell 'A5': Could not convert string 'abc' to DOUBLE` — Type mismatch; use `ignore_errors` or `all_varchar`
- `Invalid range 'Z1:A5' specified` — Range start must be ≤ end

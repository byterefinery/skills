# Excel Write — COPY TO XLSX

Write query results to `.xlsx` files using the `COPY ... TO` statement with `FORMAT 'xlsx'`. Each write creates a fresh single-sheet workbook, overwriting any existing file at the target path.

## Basic Usage

```sql
-- Simple export
COPY (SELECT * FROM my_table) TO 'output.xlsx' (FORMAT 'xlsx');

-- With header row
COPY (SELECT name, age, salary FROM employees)
TO 'report.xlsx' (FORMAT 'xlsx', header true);

-- Named sheet
COPY (SELECT * FROM data)
TO 'output.xlsx' (FORMAT 'xlsx', header true, sheet 'MyData');
```

## Named Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `header` | BOOLEAN | `false` | Write column names as the first row in the sheet. |
| `sheet` | VARCHAR | `'Sheet1'` | Name of the sheet to write. |
| `sheet_row_limit` | INTEGER | `1048576` | Maximum rows per sheet. Exceeding this throws an error. XLSX standard limit is 1,048,576. |

## Type Conversions (DuckDB → Excel)

Excel stores only numbers and strings natively. DuckDB types are converted as follows:

| DuckDB Type | Excel Storage | Notes |
|-------------|---------------|-------|
| `TINYINT`, `SMALLINT`, `INTEGER`, `BIGINT`, `HUGEINT` | Number cell | Exact integer values preserved up to DOUBLE precision |
| `FLOAT`, `DOUBLE`, `DECIMAL` | Number cell | Floating-point representation |
| `BOOLEAN` | Number cell (1/0) | Styled with Excel format to display as `TRUE`/`FALSE` |
| `DATE` | Number cell (serial) | Days since 1900-01-01, styled with date format |
| `TIME` | Number cell (fractional day) | Fraction of a day, styled with time format |
| `TIMESTAMP` | Number cell (serial + fraction) | Combined date-time serial number, styled with datetime format |
| `TIMESTAMP_TZ`, `TIME_TZ` | Converted to UTC first | Timezone information is lost in output |
| `VARCHAR`, `UUID`, etc. | String cell | All other types cast to VARCHAR then written as text |

### Date/Time Serial Numbers

Excel stores dates as "serial numbers" — the number of days since January 1, 1900:
- `DATE '2024-01-01'` → serial `45292.0`
- `TIME '14:30:00'` → fraction `0.604166...` (14.5/24)
- `TIMESTAMP '2024-01-01 14:30:00'` → serial `45292.604166...`

The cell is styled with an Excel number format so it displays as a date/time in spreadsheet applications, even though the underlying value is a number.

### Boolean Conversion

Booleans are stored as numbers (1 = TRUE, 0 = FALSE) with a custom number format:
```
[=1]TRUE;[=0]FALSE;GENERAL
```
This makes them display as `TRUE`/`FALSE` in Excel while being stored as numeric values.

## v1.5.3 Limitations

### No Multi-Sheet Write Modes

The Excel extension bundled with DuckDB 1.5.3 (commit `f4c72b5`) does **not** support `mode 'append'` or `mode 'replace'`. Each `COPY TO` statement creates a completely new single-sheet workbook, overwriting any existing file at the target path.

```sql
-- This overwrites the entire file — no append in v1.5.3
COPY (SELECT 1 AS x) TO 'file.xlsx' (FORMAT 'xlsx', sheet 'A');
COPY (SELECT 2 AS x) TO 'file.xlsx' (FORMAT 'xlsx', sheet 'B');
-- Result: file contains only sheet "B", sheet "A" is gone
```

### Workarounds for Multi-Sheet Files

**Option 1: Python with openpyxl**
```python
import duckdb, openpyxl

wb = openpyxl.Workbook()

# Write first sheet
con = duckdb.connect()
rows = con.execute("SELECT * FROM table1").fetchall()
ws1 = wb.active
ws1.title = "Sheet1"
for row in rows:
    ws1.append(row)

# Write second sheet
rows2 = con.execute("SELECT * FROM table2").fetchall()
ws2 = wb.create_sheet("Sheet2")
for row in rows2:
    ws2.append(row)

wb.save('multi_sheet.xlsx')
```

**Option 2: Python with pandas**
```python
import duckdb, pandas as pd

con = duckdb.connect()
df1 = con.execute("SELECT * FROM table1").fetchdf()
df2 = con.execute("SELECT * FROM table2").fetchdf()

with pd.ExcelWriter('multi.xlsx', engine='openpyxl') as writer:
    df1.to_excel(writer, sheet_name='Table1', index=False)
    df2.to_excel(writer, sheet_name='Table2', index=False)
```

**Option 3: Upgrade DuckDB** — Multi-sheet `mode 'append'` and `mode 'replace'` were added in later Excel extension commits after v1.5.3.

## Row Limit Handling

```sql
-- Default limit (XLSX standard)
COPY (SELECT * FROM huge_table) TO 'output.xlsx' (FORMAT 'xlsx');
-- Error if > 1,048,576 rows

-- Custom limit (at your own risk)
COPY (SELECT * FROM huge_table)
TO 'output.xlsx' (FORMAT 'xlsx', sheet_row_limit 2000000);
```

Exceeding the limit produces:
```
Invalid Input Error: XLSX: Sheet row limit of '1048576' rows exceeded!
 * XLSX files and compatible applications generally have a limit of '1048576' rows
 * You can export larger sheets at your own risk by setting the 'sheet_row_limit' parameter
```

## Remote Filesystems

`COPY TO` with `FORMAT 'xlsx'` works with remote filesystems (S3, GCS, Azure) when the corresponding extension is loaded (e.g., `httpfs`). The entire workbook is written as a single file to the remote location.

```sql
INSTALL httpfs; LOAD httpfs;
COPY (SELECT * FROM data)
TO 's3://my-bucket/report.xlsx' (FORMAT 'xlsx', header true);
```

## COPY FROM XLSX

Read XLSX files into existing tables:

```sql
CREATE TABLE my_table (name VARCHAR, age INTEGER, score DOUBLE);
COPY my_table FROM 'input.xlsx' (FORMAT 'xlsx', header true);
```

The `COPY FROM` syntax uses the same options as `read_xlsx()` but maps columns by position to the target table schema. Column count must match exactly.

```sql
-- With explicit range
COPY my_table FROM 'input.xlsx' (FORMAT 'xlsx', range 'A2:C100');
```

Column mismatch error:
```
Failed to read file(s) "input.xlsx" - column count mismatch: expected 3 columns but found 5
Table schema: name VARCHAR, age INTEGER, score DOUBLE
XLSX schema: A1 VARCHAR, B1 VARCHAR, C1 VARCHAR, D1 VARCHAR, E1 VARCHAR

Possible solutions:
* Manually specify which columns to insert using "INSERT INTO tbl SELECT ... FROM read_xlsx(...)"
* Provide an explicit range option with the same width as the table schema
```

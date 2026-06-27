---
name: duckdb-1-5-3
description: DuckDB 1.5.3 — high-performance analytical OLAP database with embedded SQL engine. Use this skill whenever the user queries about DuckDB, needs to run SQL analytics on local files (CSV, Parquet, Excel/XLSX), wants to install or use extensions (excel, json, icu, parquet, httpfs, delta, iceberg, postgres_scanner, sqlite_scanner, fts, spatial, and others), needs data import/export workflows, or is comparing DuckDB against other analytical databases. Covers CLI usage, Python API, extension management, Excel file handling (read/write/formatting/metadata), and the full extension ecosystem available in v1.5.3.
metadata:
  tags:
    - database
    - sql
    - analytics
    - olap
---

# duckdb 1.5.3

DuckDB is a high-performance analytical database system designed to be fast, reliable, portable, and easy to use. It provides an embedded SQL engine with rich dialect support including correlated subqueries, window functions, complex types (arrays, structs, maps), and seamless file-based data access.

## Overview

- **Version**: 1.5.3 (Variegata)
- **Architecture**: Embedded library — no separate server process needed
- **Primary use**: Analytical queries on local files, in-memory datasets, and connected databases
- **Key differentiator**: Query CSV/Parquet/XLSX files directly via `SELECT * FROM 'file.csv'` without explicit import
- **Extensions**: Modular ecosystem covering filesystems, data formats, database connectors, and specialized functions

### Quick Start

```sql
-- CLI: query a file directly
duckdb -c "SELECT * FROM 'data.csv' LIMIT 5"

-- Install and load an extension
INSTALL excel; LOAD excel;
SELECT * FROM read_xlsx('report.xlsx', header true);

-- Python API
import duckdb
con = duckdb.connect()
result = con.execute("SELECT * FROM 'data.parquet'").fetchall()
```

## Usage

### CLI

```bash
duckdb                        # Interactive shell
duckdb :memory:               # In-memory mode (no persistence)
duckdb mydb.duckdb            # Persistent database file
duckdb -c "SELECT 42"         # One-shot query
duckdb --version              # v1.5.3 (Variegata)
```

### Python API

```python
import duckdb
con = duckdb.connect()                    # In-memory
con = duckdb.connect('mydb.duckdb')       # Persistent
result = con.execute("SELECT * FROM table").fetchall()
df = con.execute("SELECT * FROM table").fetchdf()  # pandas DataFrame
```

### Extension Management

```sql
-- List available extensions
SELECT * FROM duckdb_extensions();

-- Install and load
INSTALL excel; LOAD excel;

-- Autoload (extensions load on first use)
-- Default behavior — no explicit INSTALL/LOAD needed for common extensions
```

## Gotchas

- **`mode 'append'` / `mode 'replace'` not available in v1.5.3** — The Excel extension bundled with DuckDB 1.5.3 (commit `f4c72b5`) does not support multi-sheet write modes. Each `COPY TO ... (FORMAT 'xlsx')` creates a fresh single-sheet file, overwriting any existing file. Multi-sheet append/replace was added in later commits. Workaround: use Python's `openpyxl` or `pandas` for multi-sheet writes, or build DuckDB from a newer Excel extension commit.
- **Excel formula cells read as computed values** — DuckDB reads the result of formulas, not the formula expressions themselves. Formula cells are typed as `VARCHAR`. There is no Excel formula evaluation engine in DuckDB.
- **Sheet discovery requires workarounds** — No built-in `excel_sheets()` function exists. Use Python's `zipfile` + `xml.etree` to parse the xlsx (which is a zip archive), or trigger an error with a wrong sheet name to get suggestions from the error message.
- **Type inference from first data row** — `read_xlsx()` infers column types from the first non-header row. If that row has empty cells, columns may be inferred as the wrong type. Use `all_varchar=true` then cast explicitly, or use `empty_as_varchar=true` to handle sparse sheets.
- **Replacement scans auto-trigger on file extensions** — Referencing `'file.csv'`, `'file.parquet'`, or `'file.xlsx'` in a FROM clause automatically triggers the corresponding scanner. No explicit function call needed.
- **Extension autoloading may mask missing INSTALL** — Common extensions autoload on first use, which can hide the fact that an extension wasn't explicitly installed. Use `SELECT * FROM duckdb_extensions()` to verify loaded state.

## References

- [01-extensions-overview](references/01-extensions-overview.md) — Extension ecosystem, categories, installation patterns
- [02-excel-read](references/02-excel-read.md) — Reading XLSX files with read_xlsx(), options, type inference
- [03-excel-write](references/03-excel-write.md) — Writing XLSX files via COPY TO, type conversions, limitations in v1.5.3
- [04-excel-formatting](references/04-excel-formatting.md) — text() / excel_text() functions for Excel-compatible number formatting
- [05-excel-metadata](references/05-excel-metadata.md) — Sheet discovery, metadata extraction, formula cell handling, cell types
- [06-extensions-filesystem](references/06-extensions-filesystem.md) — httpfs, aws, azure, GCS filesystem extensions
- [07-extensions-data-formats](references/07-extensions-data-formats.md) — json, parquet, delta, iceberg, avro, lance format extensions
- [08-extensions-database-connectors](references/08-extensions-database-connectors.md) — postgres_scanner, mysql_scanner, sqlite_scanner, odbc_scanner

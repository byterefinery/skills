---
name: duckdb-python-1-5-4
description: DuckDB Python client 1.5.4 API reference and usage patterns. Use when working with the `duckdb` Python package — in-process analytical SQL database. Covers connection management, relational API (lazy evaluation), data I/O (CSV/Parquet/JSON), Python UDFs, type system, pandas/PyArrow/Polars integration, fsspec filesystems, ADBC driver, profiling, and extensions. Trigger on: duckdb, DuckDBPyConnection, DuckDBPyRelation, read_parquet, from_df, create_function, fetch_arrow_table, register_filesystem.
metadata:
  tags:
    - database
    - sql
    - analytics
    - olap
---

# duckdb-python 1.5.4

DuckDB Python client providing in-process analytical SQL database with zero-config deployment. Runs entirely in-process (no server), supports pandas, PyArrow, Polars, and NumPy natively.

## Overview

DuckDB is a columnar OLAP engine that runs inside the Python process. Two main API styles:

- **Connection/DB-API 2.0** — `duckdb.connect()`, `conn.execute()`, `fetchall()` — standard cursor interface
- **Relational API** — `duckdb.sql()`, `.filter()`, `.project()`, `.join()` — lazy, chainable, returns `DuckDBPyRelation`

Key strengths:
- Reads CSV/Parquet/JSON directly from paths or buffers without loading into memory first
- Seamless pandas DataFrame and PyArrow Table interop via `from_df()`, `fetchdf()`, `to_arrow_table()`
- Python scalar UDFs registered with `create_function()` (native or arrow-backed)
- fsspec filesystem integration for S3, GCS, Azure, and in-memory storage
- ADBC driver included (`adbc_driver_duckdb`)

## Usage

### Quick start — top-level convenience functions

```python
import duckdb

# Query returns DuckDBPyRelation (lazy)
rel = duckdb.sql("SELECT 42 as x, 'hello' as y")
rel.show()

# Read files directly
rel = duckdb.read_parquet("data/*.parquet")
rel = duckdb.read_csv("data.csv", header=True)
rel = duckdb.read_json("data.json")

# Convert to pandas / PyArrow
df = rel.df()                          # pandas DataFrame
table = rel.to_arrow_table()           # pyarrow.Table
reader = rel.to_arrow_reader()         # streaming RecordBatchReader
```

### Connection-based workflow

```python
import duckdb

conn = duckdb.connect("my_db.duckdb")  # persistent; ":memory:" is default

# Register a pandas DataFrame as a virtual table
conn.register("sales", sales_df)

# Execute SQL, get Relation back
rel = conn.sql("SELECT region, SUM(amount) FROM sales GROUP BY region")
rel.show()

# Standard DB-API 2.0 cursor interface
cursor = conn.cursor()
cursor.execute("SELECT * FROM sales WHERE amount > ?", [1000])
rows = cursor.fetchall()

conn.close()
```

### Relational API chaining (lazy evaluation)

```python
rel = (duckdb.from_df(df)
       .filter("amount > 100")
       .project("region, customer_id, amount * 1.1 as taxed_amount")
       .order("taxed_amount DESC")
       .limit(10))

rel.show()
```

### Python UDFs

```python
import duckdb

def double_it(x):
    return x * 2

duckdb.create_function("double_it", double_it, ["integer"], "integer")
duckdb.sql("SELECT double_it(i) FROM range(5)").show()
```

## Gotchas

- **Default connection is `:memory:`** — data disappears when the process exits. Pass a file path to `connect()` for persistence.
- **`fetch_arrow_table()` and `fetch_record_batch()` are deprecated** — use `to_arrow_table()` and `to_arrow_reader()` instead (same on both Connection and Relation).
- **Relations are lazy** — `.filter()`, `.project()`, `.join()` etc. build a query plan. Results materialize only on `.show()`, `.fetchall()`, `.df()`, `.execute()`, or `.create()`.
- **`conn.register()` creates a virtual table reference** — it holds a Python object alive as long as the view/table exists in DuckDB catalog. Unregister with `conn.unregister("name")` to release.
- **UDF parameter types must match exactly** — `create_function("fn", fn_impl, ["bigint"], "varchar")` requires input columns to be castable to `BIGINT`. Mismatched types raise `InvalidInputException`.
- **Arrow UDFs receive ChunkedArrays** — use `@duckdb.udf.vectorized` decorator or annotate parameters with `pa.ChunkedArray` for arrow-mode UDFs.
- **`conn.pl()` returns Polars DataFrame** — requires `polars` installed. Use `lazy=True` for `LazyFrame`.
- **Free-threaded Python (3.13t, 3.14t) is not supported** — the production client does not work with free-threaded builds.
- **`conn.duplicate()` clones a connection** sharing the same database but with independent transaction state. Useful for concurrent queries on the same DB.

## References

- [01-connection-api](references/01-connection-api.md) — connect, execute, cursor, transactions, config
- [02-relational-api](references/02-relational-api.md) — DuckDBPyRelation: lazy chaining, joins, aggregations, exports
- [03-data-io](references/03-data-io.md) — CSV, Parquet, JSON read/write with options
- [04-udfs](references/04-udfs.md) — Python scalar UDFs (native and arrow), type annotations, null handling
- [05-types-values](references/05-types-values.md) — DuckDBPyType, sqltypes constants, Value classes, DB-API type objects
- [06-integrations](references/06-integrations.md) — pandas, PyArrow, Polars, NumPy, fsspec, ADBC, Spark compat

---
name: duckdb-python-1-5-5
description: DuckDB in-process analytical database for Python — query CSV/Parquet/JSON files, pandas DataFrames, and Arrow tables with SQL. Provides DB-API 2.0 connection, lazy Relation API for method-chained transformations, Python UDFs, and Spark-compatible API. Use for data analysis, ETL pipelines, EDA, and SQL-based data processing in Python.
license: MIT
compatibility: Python 3.10+. Install via `pip install duckdb`. Optional deps include pandas, pyarrow, polars, numpy, fsspec, and ipython. Install all with `pip install 'duckdb[all]'`.
metadata:
  tags:
    - database
    - analytics
    - sql
    - data-processing
---

# duckdb-python 1.5.5

## Overview

DuckDB is an in-process, columnar OLAP database engine with Python bindings. It runs entirely in-process (no server), has zero external runtime dependencies beyond Python, and supports reading/writing CSV, Parquet, JSON, and Python data structures directly via SQL or a fluent `Relation` API.

Two main access patterns:
- **DB-API 2.0** (`connect()` → `execute()` → `fetchall()`/`fetch_df()`) — familiar cursor-style interface, compatible with SQLAlchemy
- **Relation API** (`duckdb.sql()` / `read_csv()` / `from_df()`) — lazy, method-chained transformations (`filter()`, `project()`, `join()`, `aggregate()`) that compile to optimized SQL

## Usage

### Installation

```bash
pip install duckdb
```

### Quick queries

```python
import duckdb

# Query a file directly — no loading into memory first
duckdb.sql("SELECT * FROM 'data.parquet' LIMIT 10").show()

# Query a pandas DataFrame
import pandas as pd
df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
duckdb.sql("SELECT * FROM df WHERE x > 1").df()

# In-memory database
con = duckdb.connect()
con.execute("CREATE TABLE t (id INT, val DOUBLE)")
con.execute("INSERT INTO t VALUES (1, 3.14), (2, 2.71)")
con.execute("SELECT * FROM t").fetchall()
```

### Connection API (DB-API 2.0)

```python
import duckdb

# In-memory (default) or file-backed
con = duckdb.connect()                          # in-memory
con = duckdb.connect("my_database.duckdb")      # persistent

# Execute SQL
con.execute("CREATE TABLE sales (date DATE, amount INT)")
con.execute("INSERT INTO sales VALUES ('2024-01-01', 100)")

# Fetch results
con.execute("SELECT * FROM sales").fetchall()    # list of tuples
con.execute("SELECT * FROM sales").fetch_df()    # pandas DataFrame
con.execute("SELECT * FROM sales").to_arrow_table()  # PyArrow Table
con.execute("SELECT * FROM sales").pl()          # Polars DataFrame

# Context manager
with duckdb.connect() as con:
    con.execute("SELECT 42")

# Parameterized queries
con.execute("SELECT * FROM t WHERE id = ?", (1,))
con.execute("SELECT * FROM t WHERE id IN %s", ((1, 2, 3),))
```

### Relation API (lazy, fluent)

```python
import duckdb

rel = duckdb.read_csv("data.csv")

# Method chaining — all lazy, evaluated on .show() or .df()
rel.filter("amount > 100") \
   .project("date, amount, amount * 1.1 as with_tax") \
   .order("date") \
   .limit(10) \
   .show()

# Aggregations
rel.aggregate("AVG(amount), SUM(amount)", group_expr="date").show()

# Joins
rel1 = duckdb.read_csv("orders.csv")
rel2 = duckdb.read_csv("customers.csv")
rel1.join(rel2, "customer_id = customer_id", how="left").show()

# Set operations
rel1.union(rel2)
rel1.intersect(rel2)
rel1.except_(rel2)

# Write output
rel.to_df()                        # pandas
rel.pl()                           # polars
rel.to_arrow_table()               # pyarrow
rel.to_parquet("output.parquet")   # write to file
rel.to_csv("output.csv")
```

### Reading and writing files

```python
import duckdb

# Read — returns a Relation (lazy)
rel = duckdb.read_csv("data.csv")
rel = duckdb.read_parquet("data.parquet")
rel = duckdb.read_json("data.json")

# Write from a Relation
rel.to_csv("out.csv")
rel.to_parquet("out.parquet")

# Direct I/O (no Relation)
duckdb.sql("COPY (SELECT * FROM data) TO 'out.parquet' (FORMAT PARQUET)")
duckdb.sql("COPY (SELECT * FROM data) TO 'out.csv' (HEADER TRUE, DELIMITER ',')")

# From DuckDB to pandas
df = duckdb.sql("SELECT * FROM 'data.parquet'").df()

# From pandas to DuckDB
rel = duckdb.from_df(df)
rel.create("my_table")
```

### Registering Python objects

```python
import duckdb

con = duckdb.connect()

# Register a pandas DataFrame as a virtual table
con.register("my_data", df)
con.execute("SELECT * FROM my_data").fetchall()

# Register arbitrary Python objects (lists, dicts)
con.register("my_list", [{"x": 1}, {"x": 2}])
con.execute("SELECT * FROM my_list").fetchall()

# Unregister when done
con.unregister("my_data")
```

### Python UDFs

```python
import duckdb

# Native UDF — row-by-row
duckdb.create_function(
    "double_it",
    lambda x: x * 2,
    parameters=[duckdb.Integer],
    return_type=duckdb.Integer,
)
duckdb.sql("SELECT double_it(x) FROM t").show()

# Arrow (vectorized) UDF — operates on whole arrays
duckdb.create_function(
    "arrow_double",
    lambda arr: arr * 2,
    parameters=["integer"],
    return_type="integer",
    type=duckdb.func.ARROW,
)

# Vectorized decorator (auto-annotates with pyarrow.ChunkedArray)
from duckdb.udf import vectorized

@vectorized
def my_func(col1, col2):
    return col1 + col2

duckdb.create_function("my_func", my_func, type=duckdb.func.ARROW)
```

### Custom types

```python
import duckdb

# Struct
duckdb.struct_type({"name": "varchar", "age": "integer"})

# List
duckdb.list_type("integer")

# Map
duckdb.map_type("varchar", "integer")

# Enum
duckdb.enum_type("status", "varchar", ["open", "closed", "pending"])

# Decimal
duckdb.decimal_type(10, 2)

# Array (fixed size)
duckdb.array_type("integer", 3)
```

### fsspec filesystems

```python
import duckdb
from fsspec.implementations.http import HTTPFileSystem

http = HTTPFileSystem()
duckdb.register_filesystem(http)

# Now query remote URLs directly
duckdb.sql("SELECT * FROM 'https://example.com/data.parquet'").show()
```

### Profiling

```python
import duckdb

con = duckdb.connect()
con.enable_profiling()
con.execute("SELECT COUNT(*) FROM large_table")
print(con.get_profiling_information(format="json"))
con.disable_profiling()
```

### Spark compatibility (experimental)

```python
from duckdb.experimental.spark import SparkSession

spark = SparkSession.builder.getOrCreate()
df = spark.read.parquet("data.parquet")
df.filter(df.amount > 100).select("date", "amount").show()
```

## Gotchas

- **`fetch_df()` vs `.df()`** — on `DuckDBPyConnection`, use `con.fetch_df()` (after execute). On `DuckDBPyRelation`, use `rel.df()`. The naming is inconsistent between the two APIs.
- **`fetch_arrow_table()` is deprecated** — use `to_arrow_table()` instead. Same for `fetch_record_batch()` → `to_arrow_reader()`.
- **Parameterized queries use `?` or `%s`** — `paramstyle` is `qmark`. Use `con.execute("SELECT * FROM t WHERE id = ?", (1,))`. For tuples/lists, wrap in an extra tuple: `con.execute("SELECT * FROM t WHERE id IN %s", ((1, 2, 3),))`.
- **Relations are lazy** — `read_csv()`, `sql()`, `filter()`, `project()` all build a query plan. Evaluation happens on `.show()`, `.df()`, `.fetchall()`, or `.to_parquet()`. This is efficient but means errors surface at evaluation time, not at construction time.
- **`duckdb.sql()` uses the default connection** — if you need multiple databases, use explicit `connection` keyword argument or work with `DuckDBPyConnection` directly.
- **`register()` creates a view, not a table** — registered DataFrames and objects are virtual views. They are not persisted in the database file. Use `CREATE TABLE` + `INSERT` for persistence.
- **`con.execute()` returns the connection, not a cursor** — DuckDB's connection is its own cursor (PEP 249 compliant). Use method chaining: `con.execute("...").fetchall()`.
- **`from_df()` vs `df()`** — `duckdb.from_df(df)` converts a pandas DataFrame to a Relation. `rel.df()` or `con.fetch_df()` converts results back to pandas.
- **In-memory is default** — `duckdb.connect()` with no arguments creates an in-memory database. It disappears when the connection closes. Use `duckdb.connect("file.duckdb")` for persistence.
- **Extensions are bundled** — `core_functions`, `json`, `parquet`, and `icu` are built into the wheel. No need to `LOAD` them. Other extensions require `con.load_extension("name")`.
- **`rel.join()` condition uses SQL syntax** — pass a SQL expression string, not a Python lambda: `rel1.join(rel2, "t1.id = t2.id")`.

## References

- [01-connection-api](references/01-connection-api.md) — DuckDBPyConnection: execute, fetch, transactions, configuration
- [02-relation-api](references/02-relation-api.md) — DuckDBPyRelation: lazy method-chained transformations
- [03-file-io](references/03-file-io.md) — Reading and writing CSV, Parquet, JSON files
- [04-udfs](references/04-udfs.md) — Python UDFs: native, Arrow (vectorized), type annotations
- [05-integrations](references/05-integrations.md) — pandas, PyArrow, Polars, NumPy, fsspec, TensorFlow, PyTorch
- [06-types](references/06-types.md) — SQL types, struct, list, map, enum, decimal, custom type construction
- [07-experimental-spark](references/07-experimental-spark.md) — PySpark compatibility layer overview

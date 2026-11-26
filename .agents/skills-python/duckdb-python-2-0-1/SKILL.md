---
name: duckdb-python-2-0-1
description: DuckDB in-process analytical database for Python — query CSV/Parquet/JSON files, pandas DataFrames, and Arrow tables with SQL. Provides DB-API 2.0 connection, lazy Relation API for method-chained transformations, Python UDFs, and a Spark-compatible API. Use for data analysis, ETL pipelines, EDA, and SQL-based data processing in Python.
license: MIT
compatibility: Python 3.11–3.15 (free-threaded builds not supported). Install via `pip install duckdb`. Optional deps include pandas, pyarrow, polars, numpy, fsspec, ipython; install all with `pip install 'duckdb[all]'`.
metadata:
  tags:
    - database
    - analytics
    - sql
    - data-processing
---

# duckdb-python 2.0.1

## Overview

DuckDB is an in-process, columnar OLAP database engine with Python bindings. It runs entirely in-process (no server), has zero external runtime dependencies beyond Python, and supports reading/writing CSV, Parquet, JSON, and Python data structures directly via SQL or a fluent `Relation` API.

Two main access patterns:
- **DB-API 2.0** (`connect()` → `execute()` → `fetchall()`/`fetch_df()`) — familiar cursor-style interface, compatible with SQLAlchemy
- **Relation API** (`duckdb.sql()` / `read_csv()` / `from_df()`) — lazy, method-chained transformations (`filter()`, `project()`, `join()`, `aggregate()`) that compile to optimized SQL

v2.0 specifics (this skill targets the v2.0.1 release):
- Bindings are built on **nanobind 3.x** (the C++ extension module is `_duckdb`; the `duckdb` package wraps it). The user-facing Python API is unchanged from 1.x — nanobind is an implementation detail.
- Wheels for **CPython 3.12+ use the stable ABI** (`cp312-abi3`), so one wheel serves 3.12 through 3.15. CPython 3.11 gets a version-specific wheel. Supported interpreters: 3.11, 3.12, 3.13, 3.14, 3.15.
- **Free-threaded Python is not supported** — no wheels ship for `3.11t`/`3.12t`/etc.; don't target those interpreters.
- Bundled extensions built into the wheel: `core_functions`, `json`, `parquet`, `icu`. No need to `LOAD` them.

## Usage

### Installation

```bash
pip install duckdb            # core only
pip install 'duckdb[all]'     # with optional deps (pandas, pyarrow, polars, numpy, fsspec, ipython)
```

### Quick queries

```python
import duckdb

# Query a file directly — no loading into memory first
duckdb.sql("SELECT * FROM 'data.parquet' LIMIT 10").show()

# Query a pandas DataFrame in scope
import pandas as pd
df = pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]])
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

# Execute SQL — the connection is its own cursor; chain results
con.execute("CREATE TABLE sales (date DATE, amount INT)")
con.execute("INSERT INTO sales VALUES ('2024-01-01', 100)")
con.execute("SELECT * FROM sales").fetchall()   # list of tuples
con.execute("SELECT * FROM sales").fetch_df()   # pandas DataFrame

# Parameterized queries (? or %s placeholders)
con.execute("SELECT * FROM t WHERE id = ?", (1,))
```

### Relation API (lazy, fluent)

```python
import duckdb

rel = duckdb.read_csv("data.csv")

# Method chaining — all lazy, evaluated on .show() / .df() / .fetchall()
rel.filter("amount > 100") \
   .project("date, amount, amount * 1.1 as with_tax") \
   .order("date") \
   .limit(10) \
   .show()

# Aggregations
rel.aggregate("AVG(amount), SUM(amount)", group_expr="date").show()

# Joins — condition is a SQL expression string
rel1 = duckdb.read_csv("orders.csv")
rel2 = duckdb.read_csv("customers.csv")
rel1.join(rel2, "customer_id = customer_id", how="left").show()

# Write output
rel.to_df()                        # pandas
rel.to_arrow_table()               # pyarrow
rel.to_parquet("output.parquet")   # write to file
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
```

### Python UDFs

```python
import duckdb

# Native scalar UDF — row-by-row
duckdb.create_function(
    "double_it",
    lambda x: x * 2,
    parameters=["INTEGER"],
    return_type="INTEGER",
)
duckdb.sql("SELECT double_it(x) FROM t").show()

# Vectorized decorator (auto-annotates with pyarrow types)
from duckdb.udf import vectorized

@vectorized
def add_one(col):
    return col + 1

duckdb.create_function("add_one", add_one, type=duckdb.func.ARROW)
```

See [04-udfs](references/04-udfs.md) for native vs Arrow UDFs and type handling.

## Gotchas

- **`fetch_df()` vs `.df()`** — on `DuckDBPyConnection`, use `con.execute(...).fetch_df()`. On `DuckDBPyRelation`, use `rel.df()`. The naming is inconsistent between the two APIs.
- **Relations are lazy** — `read_csv()`, `sql()`, `filter()`, `project()` all build a query plan. Evaluation happens on `.show()`, `.df()`, `.fetchall()`, or `.to_parquet()`. Errors surface at evaluation time, not construction time.
- **`duckdb.sql()` uses the default connection** — if you need multiple databases, create explicit `DuckDBPyConnection` objects (`duckdb.connect(...)`) and call methods on them.
- **`register()` creates a view, not a table** — registered DataFrames/objects are virtual views, not persisted to the database file. Use `CREATE TABLE` + `INSERT` (or `COPY`) for persistence.
- **`con.execute()` returns the connection, not a cursor** — DuckDB's connection is its own cursor (PEP 249 compliant). Chain methods: `con.execute("...").fetchall()`.
- **In-memory is default** — `duckdb.connect()` with no arguments creates an in-memory database that disappears when the connection closes. Use `duckdb.connect("file.duckdb")` for persistence.
- **Extensions are bundled** — `core_functions`, `json`, `parquet`, and `icu` are built into the wheel; don't `LOAD` them. Other extensions require `con.install_extension(...)` / `con.load_extension(...)`.
- **`rel.join()` condition uses SQL syntax** — pass a SQL expression string, not a Python lambda: `rel1.join(rel2, "t1.id = t2.id")`.
- **Free-threaded Python is unsupported in v2.0** — no wheels for `3.xt` interpreters; the C API-based prototype client targets free-threading separately.
- **v2.0 wheels are nanobind/stable-ABI** — if you pin to 1.x behavior (pybind11 internals, per-version wheels), that's a v1.5-and-earlier concern. The Python-level API is compatible; only the C extension and wheel tags changed.

## References

- [01-connection-api](references/01-connection-api.md) — DuckDBPyConnection: execute, fetch, transactions, configuration
- [02-relation-api](references/02-relation-api.md) — DuckDBPyRelation: lazy method-chained transformations
- [03-file-io](references/03-file-io.md) — Reading and writing CSV, Parquet, JSON files
- [04-udfs](references/04-udfs.md) — Python UDFs: native, Arrow (vectorized), type annotations
- [05-integrations](references/05-integrations.md) — pandas, PyArrow, Polars, NumPy, fsspec integrations
- [06-types](references/06-types.md) — SQL types, struct, list, map, enum, decimal, custom type construction
- [07-experimental-spark](references/07-experimental-spark.md) — PySpark compatibility layer overview

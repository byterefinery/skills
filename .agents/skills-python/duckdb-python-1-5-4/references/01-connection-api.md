# Connection API

## Creating Connections

```python
import duckdb

# In-memory (default) — data lost on process exit
conn = duckdb.connect()
conn = duckdb.connect(":memory:")

# Persistent database file
conn = duckdb.connect("my_db.duckdb")

# Read-only
conn = duckdb.connect("my_db.duckdb", read_only=True)

# With config options
conn = duckdb.connect(
    "my_db.duckdb",
    config={
        "threads": "4",
        "memory_limit": "2GB",
        "preserve_insertion_order": "true",
    }
)
```

## Top-Level vs Connection Methods

Most functions exist at both module level (using default connection) and as connection methods:

| Module-level | Connection method | Returns |
|---|---|---|
| `duckdb.connect(path)` | — | `DuckDBPyConnection` |
| `duckdb.execute(sql, params)` | `conn.execute(sql, params)` | `DuckDBPyConnection` |
| `duckdb.sql(sql)` | `conn.sql(sql)` | `DuckDBPyRelation` |
| `duckdb.query(sql)` | `conn.query(sql)` | `DuckDBPyRelation` |
| `duckdb.fetchall()` | `conn.fetchall()` | `list[tuple]` |
| `duckdb.fetchone()` | `conn.fetchone()` | `tuple \| None` |
| `duckdb.fetchmany(n)` | `conn.fetchmany(n)` | `list[tuple]` |
| `duckdb.fetchdf()` | `conn.df()` | `pandas.DataFrame` |
| `duckdb.to_arrow_table()` | `conn.to_arrow_table()` | `pyarrow.Table` |
| `duckdb.to_arrow_reader()` | `conn.to_arrow_reader()` | `RecordBatchReader` |
| `duckdb.description` | `conn.description` | column metadata |
| `duckdb.rowcount` | `conn.rowcount` | `int` |

Set the default connection with `duckdb.set_default_connection(conn)`. Get it with `duckdb.default_connection()`.

## DB-API 2.0 (PEP 249) Compliance

DuckDB implements the Python Database API Specification:

```python
conn = duckdb.connect()
cursor = conn.cursor()  # returns the connection itself (self-cursor pattern)

# Execute with positional parameters (?)
cursor.execute("SELECT * FROM t WHERE x > ?", [10])
rows = cursor.fetchall()

# Execute with named parameters (:name)
cursor.execute("SELECT * FROM t WHERE x > :threshold", {"threshold": 10})

# executemany for batch inserts
cursor.executemany("INSERT INTO t VALUES (?, ?)", [(1, "a"), (2, "b")])

# Column metadata via description
print(cursor.description)
# [('x', <INTEGER>, None, None, None, None, None), ...]

# Module-level constants
print(duckdb.apilevel)    # "2.0"
print(duckdb.threadsafety)  # 1 (threads may share the module)
print(duckdb.paramstyle)   # "qmark"
```

## Transactions

```python
conn = duckdb.connect()

# Explicit transactions
conn.begin()
conn.execute("INSERT INTO t VALUES (1)")
conn.execute("INSERT INTO t VALUES (2)")
conn.commit()

# Rollback
conn.begin()
conn.execute("INSERT INTO t VALUES (3)")
conn.rollback()

# Context manager (auto-commit on success, rollback on exception)
with conn:
    conn.execute("INSERT INTO t VALUES (4)")
    conn.execute("INSERT INTO t VALUES (5)")
```

## Connection Management

```python
# Duplicate — shares database, independent transaction state
conn2 = conn.duplicate()

# Interrupt a long-running query
conn.interrupt()

# Close connection
conn.close()

# Query progress (0.0 to 1.0)
progress = conn.query_progress()

# Check registered filesystems
conn.list_filesystems()
```

## Statement Preparation

```python
# Extract and inspect statements
stmts = conn.extract_statements("SELECT 1; SELECT 2; INSERT INTO t VALUES (3)")
for stmt in stmts:
    print(stmt.type)           # StatementType
    print(stmt.query)          # SQL text
    print(stmt.named_parameters)  # set of named params
    print(stmt.expected_result_type)  # list of StatementType
```

## Profiling

```python
conn.enable_profiling()
conn.execute("SELECT * FROM large_table GROUP BY category")
info = conn.get_profiling_information(format="json")
# Formats: "json", "query_tree", "query_tree_optimizer", "html", "graphviz"
conn.disable_profiling()
```

## Extensions

```python
# Install and load extensions
conn.install_extension("httpfs")
conn.load_extension("httpfs")

# Or at module level
duckdb.install_extension("spatial")
duckdb.load_extension("spatial")
```

## Register / Unregister Objects

```python
# Register a pandas DataFrame as a virtual table
conn.register("my_data", df)
conn.sql("SELECT * FROM my_data").show()

# Register an fsspec filesystem
conn.register_filesystem(s3_fs)
conn.sql("SELECT * FROM 's3://bucket/data.parquet'").show()

# Unregister
conn.unregister("my_data")
conn.unregister_filesystem("S3FileSystem")
conn.filesystem_is_registered("S3FileSystem")  # bool
```

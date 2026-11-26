# Connection API (DuckDBPyConnection)

## Connecting

```python
import duckdb

# In-memory (default, ephemeral)
con = duckdb.connect()

# Persistent file-backed database
con = duckdb.connect("my_db.duckdb")

# Read-only
con = duckdb.connect("my_db.duckdb", read_only=True)

# With configuration options
con = duckdb.connect(
    "my_db.duckdb",
    config={
        "threads": "4",
        "memory_limit": "2GB",
        "preserve_insertion_order": "true",
    }
)
```

## Execution

```python
# Execute SQL — returns the connection itself (for chaining)
con.execute("CREATE TABLE t (id INT, val DOUBLE)")
con.execute("INSERT INTO t VALUES (1, 3.14)")
con.execute("SELECT * FROM t")

# Parameterized queries (qmark style)
con.execute("SELECT * FROM t WHERE id = ?", (1,))
con.execute("SELECT * FROM t WHERE id = ? AND val > ?", (1, 1.0))

# IN clause — wrap the tuple in another tuple
con.execute("SELECT * FROM t WHERE id IN %s", ((1, 2, 3),))

# executemany for batch inserts
con.executemany("INSERT INTO t VALUES (?, ?)", [(1, 1.0), (2, 2.0), (3, 3.0)])

# Named parameters via Statement object
stmt = con.extract_statements("SELECT * FROM t WHERE id = $id AND val = $val")
con.execute(stmt, {"$id": 1, "$val": 3.14})
```

## Fetching Results

```python
con.execute("SELECT * FROM t")

# As list of tuples (standard DB-API)
rows = con.fetchall()
row = con.fetchone()
rows = con.fetchmany(10)

# As pandas DataFrame
df = con.fetch_df()
df = con.fetch_df(date_as_object=True)

# As chunked pandas DataFrames (for large results)
while True:
    chunk = con.fetch_df_chunk()
    if chunk.empty:
        break
    process(chunk)

# As PyArrow
table = con.to_arrow_table()
reader = con.to_arrow_reader(batch_size=10000)

# As Polars
pl_df = con.pl()
pl_lazy = con.pl(lazy=True)

# As NumPy arrays (dict of column_name → ndarray)
arrays = con.fetchnumpy()

# Description and rowcount (DB-API properties)
con.execute("SELECT * FROM t")
print(con.description)  # list of (name, type, ...) tuples
print(con.rowcount)     # int
```

## Transactions

```python
con.begin()
con.execute("INSERT INTO t VALUES (1, 1.0)")
con.execute("INSERT INTO t VALUES (2, 2.0)")
con.commit()

# Rollback
con.begin()
con.execute("INSERT INTO t VALUES (3, 3.0)")
con.rollback()

# Context manager (auto-commits on success, rolls back on exception)
with duckdb.connect() as con:
    con.execute("INSERT INTO t VALUES (1, 1.0)")
```

## Registering Objects

```python
import pandas as pd

df = pd.DataFrame({"x": [1, 2, 3]})
con.register("my_df", df)
con.execute("SELECT * FROM my_df").fetchall()

# Unregister
con.unregister("my_df")

# Register arbitrary Python objects
con.register("my_dict", {"a": 1, "b": 2})
con.register("my_list", [{"x": 1}, {"x": 2}])
```

## Extensions

```python
# Bundled extensions (core_functions, json, parquet, icu) — auto-loaded

# Load additional extensions
con.load_extension("httpfs")
con.load_extension("spatial")

# Install from repository
con.install_extension("httpfs")
con.install_extension("httpfs", version="1.0.0")
con.install_extension("httpfs", repository="https://my-repo.com")
```

## Profiling

```python
con.enable_profiling()
con.execute("SELECT COUNT(*) FROM large_table")
json_info = con.get_profiling_information(format="json")
text_info = con.get_profiling_information(format="text")
con.disable_profiling()
```

## Filesystems

```python
from fsspec.implementations.http import HTTPFileSystem
from fsspec.implementations.memory import MemoryFileSystem

con.register_filesystem(HTTPFileSystem())
con.register_filesystem(MemoryFileSystem())

print(con.list_filesystems())
print(con.filesystem_is_registered("http"))

con.unregister_filesystem("http")
```

## Connection Management

```python
# Close connection
con.close()

# Duplicate connection (shares the same database)
con2 = con.duplicate()

# Interrupt a long-running query
con.interrupt()

# Check query progress (0.0 to 1.0)
progress = con.query_progress()

# Checkpoint WAL
con.checkpoint()
```

## Default Connection

```python
# Module-level functions use a default connection
duckdb.execute("SELECT 42")
duckdb.sql("SELECT 42").show()

# Change the default connection
con = duckdb.connect("my_db.duckdb")
duckdb.set_default_connection(con)

# Get the default connection
default = duckdb.default_connection()
```

## Configuration Reference

Key config options passed to `connect()`:

| Option | Type | Description |
|--------|------|-------------|
| `threads` | int | Number of threads for parallel execution |
| `memory_limit` | string | Max memory (e.g., "2GB", "500MB") |
| `temp_directory` | string | Directory for spill-to-disk |
| `preserve_insertion_order` | bool | Preserve row order in INSERT |
| `allow_unsigned_extensions` | bool | Allow loading unsigned extensions |
| `custom_user_agent` | string | User-agent for HTTP requests |
| `default_null_order` | string | "nulls_first" / "nulls_last" |

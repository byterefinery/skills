# Integrations

## Pandas

```python
import duckdb
import pandas as pd

# DataFrame → Relation
rel = duckdb.from_df(df)

# Relation → DataFrame
df = rel.df()
df = con.fetch_df()

# Query a DataFrame directly
duckdb.sql("SELECT * FROM df WHERE x > 10").df()

# Register as table
con.register("my_df", df)
con.execute("SELECT * FROM my_df").fetchall()

# Append to table
con.append("my_table", df)
con.append("my_table", df, by_name=True)  # match columns by name, not position

# Chunked reading (for large results)
con.execute("SELECT * FROM large_table")
while True:
    chunk = con.fetch_df_chunk()
    if chunk.empty:
        break
    process(chunk)

# date_as_object — return dates as Python date objects instead of numpy datetime64
df = rel.df(date_as_object=True)
```

### DuckDB-on-Pandas Operations

Module-level functions that operate on DataFrames without explicit connection:

```python
duckdb.from_df(df)                                    # DataFrame → Relation
duckdf.from_df(df).filter("x > 10").project("x, y")   # chain operations
duckdb.filter(df, "x > 10")                           # filter DataFrame
duckdb.project(df, "x", "y * 2 as double_y")          # select columns
duckdb.aggregate(df, "AVG(x)", group_expr="y")        # groupby + agg
duckdb.order(df, "x DESC")                            # sort
duckdb.limit(df, 10)                                  # head
duckdb.distinct(df)                                   # drop duplicates
duckdb.alias(df, "my_alias")                           # set alias
duckdb.query_df(df, "df", "SELECT * FROM df WHERE x > 0")  # SQL on DataFrame
```

## PyArrow

```python
import duckdb
import pyarrow as pa

# Arrow Table → Relation
rel = duckdb.from_arrow(table)

# Relation → Arrow Table
table = rel.to_arrow_table()
table = con.to_arrow_table()

# Relation → Arrow RecordBatchReader (streaming)
reader = rel.to_arrow_reader(batch_size=10000)
reader = con.to_arrow_reader(batch_size=10000)

# Arrow as UDF parameter/result
# (see UDFs reference for details)
```

## Polars

```python
import duckdb

# Relation → Polars DataFrame
pl_df = rel.pl()
pl_df = con.pl()

# Relation → Polars LazyFrame
pl_lazy = rel.pl(lazy=True)
pl_lazy = con.pl(lazy=True)

# Batch size control
pl_df = rel.pl(batch_size=1000000)
```

## NumPy

```python
import duckdb

# Relation → dict of column_name → ndarray
arrays = rel.fetchnumpy()
arrays = con.fetchnumpy()

# Result: {"col1": ndarray, "col2": ndarray, ...}
# Categorical columns returned as pandas.Categorical
```

## fsspec

```python
import duckdb
from fsspec.implementations.http import HTTPFileSystem
from fsspec.implementations.memory import MemoryFileSystem
from fsspec.implementations.s3 import S3FileSystem

# Register filesystems
duckdb.register_filesystem(HTTPFileSystem())
duckdb.register_filesystem(MemoryFileSystem())

# Now query remote files directly
duckdb.sql("SELECT * FROM 'https://example.com/data.parquet'").show()

# Check registered filesystems
duckdb.list_filesystems()
duckdb.filesystem_is_registered("http")

# Unregister
duckdb.unregister_filesystem("http")

# Connection-specific
con.register_filesystem(HTTPFileSystem())
con.unregister_filesystem("http")
```

## TensorFlow

```python
# Access TensorFlow tensors as a dict from connection
con = duckdb.connect()
tf_dict = con.tf()

# Or from a relation
tf_dict = rel.tf()

# Returns dict of column_name → TensorFlow tensor
```

## PyTorch

```python
# Access PyTorch tensors as a dict from connection
con = duckdb.connect()
torch_dict = con.torch()

# Or from a relation
torch_dict = rel.torch()

# Returns dict of column_name → PyTorch tensor
```

## ADBC

DuckDB provides an ADBC (Arrow Database Connectivity) driver:

```python
import adbc_driver_duckdb

# Connect via ADBC
with adbc_driver_duckdb.connect() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM table")
        arrow_table = cur.fetch_arrow_table()
```

## SQLAlchemy

DuckDB works with SQLAlchemy via the `duckdb` dialect:

```python
from sqlalchemy import create_engine

engine = create_engine("duckdb:///:memory:")
# or: create_engine("duckdb:///path/to/database.duckdb")
```

## Query Graph (IPython)

```python
# In IPython/Jupyter, visualize query execution plans
# Requires ipython (install with duckdb[all])
%load_ext duckdb.query_graph
```

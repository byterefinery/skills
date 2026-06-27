# Integrations

## Pandas

```python
import duckdb
import pandas as pd

df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})

# DataFrame to Relation
rel = duckdb.from_df(df)
rel = conn.from_df(df)

# Register as virtual table
conn.register("people", df)
duckdb.sql("SELECT * FROM people WHERE age > 25").show()

# Relation to DataFrame
df = rel.df()
df = rel.fetchdf()

# Chunked fetch for large results
df_chunk = rel.fetch_df_chunk(vectors_per_chunk=1)

# Append to existing table
duckdb.append("existing_table", df)
conn.append("existing_table", df, by_name=False)

# Query a DataFrame directly
rel = duckdb.query_df(df, "df", "SELECT name, age + 1 as older_age")
```

### Date Handling

```python
# Return dates as Python objects (not pandas Timestamp)
df = rel.df(date_as_object=True)
```

## PyArrow

```python
import duckdb
import pyarrow as pa

table = pa.table({"name": ["Alice", "Bob"], "age": [30, 25]})

# Arrow to Relation
rel = duckdb.from_arrow(table)
rel = conn.from_arrow(table)

# Relation to Arrow Table
table = rel.to_arrow_table()
table = conn.to_arrow_table()

# Streaming via RecordBatchReader
reader = rel.to_arrow_reader()
reader = conn.to_arrow_reader(batch_size=10000)

# Deprecated aliases (use to_arrow_* instead):
table = rel.fetch_arrow_table()    # deprecated
reader = rel.fetch_record_batch()  # deprecated
```

## Polars

```python
import duckdb

# Relation to Polars DataFrame
pl_df = rel.pl()
pl_df = conn.pl()

# Relation to Polars LazyFrame
pl_lf = rel.pl(lazy=True)
pl_lf = conn.pl(lazy=True)

# Batch size control
pl_df = rel.pl(batch_size=500000)
```

## NumPy

```python
import duckdb

# Relation to NumPy arrays (dict of column name -> array)
arrays = rel.fetchnumpy()
arrays = conn.fetchnumpy()
# Returns: {"col1": np.ndarray, "col2": np.ndarray, ...}
```

## fsspec Filesystems

Register custom filesystems to read from S3, GCS, Azure, HDFS, etc.:

```python
import duckdb
import fsspec

# Memory filesystem
mem_fs = fsspec.filesystem("memory")
conn.register_filesystem(mem_fs)
conn.sql("SELECT * FROM 'memory://data.csv'").show()

# S3 filesystem (requires s3fs)
s3_fs = fsspec.filesystem("s3", key="...", secret="...")
conn.register_filesystem(s3_fs)
conn.sql("SELECT * FROM 's3://bucket/data.parquet'").show()

# Check if registered
conn.filesystem_is_registered("S3FileSystem")  # bool

# List registered filesystems
conn.list_filesystems()

# Unregister
conn.unregister_filesystem("memory")
```

### HTTP Filesystem

The `httpfs` extension enables reading from HTTP/HTTPS URLs:

```python
conn.load_extension("httpfs")
rel = duckdb.read_csv("https://example.com/data.csv")
rel = duckdb.read_parquet("https://example.com/data.parquet")
```

## ADBC Driver

DuckDB includes an Apache Arrow Database Connectivity (ADBC) driver:

```python
import adbc_driver_duckdb

# Low-level ADBC connection
db = adbc_driver_duckdb.connect()              # in-memory
db = adbc_driver_duckdb.connect("my_db.duckdb")  # persistent

# Use with adbc-driver-manager
import adbc_driver_manager
conn = db.connect()
stmt = conn.create_statement()
stmt.execute()
reader = stmt.read_chunk_stream()
```

## PySpark Compatibility (Experimental)

```python
import duckdb.experimental.spark as spark

# Create a Spark-like session backed by DuckDB
spark_session = spark.SparkSession.builder.getOrCreate()

# Use DataFrame API (limited compatibility)
df = spark_session.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
df.show()
df.filter(df["id"] > 1).collect()
```

Note: This is experimental and covers a subset of PySpark's API. Not all functions and transformations are supported.

## TensorFlow / PyTorch

```python
import duckdb

# Access TensorFlow namespace (requires tensorflow installed)
tf = conn.tf()
# Returns dict with TensorFlow integration functions

# Access PyTorch namespace (requires torch installed)
torch = conn.torch()
# Returns dict with PyTorch integration functions
```

## Version Info

```python
import duckdb

print(duckdb.__version__)           # e.g. "1.5.4"
print(duckdb.__duckdb_version__)    # DuckDB engine version
print(duckdb.__git_revision__)      # Git commit hash
print(duckdb.__formatted_python_version__)  # Python version string
print(duckdb.__standard_vector_size__)      # Internal vector size (2048)
print(duckdb.__interactive__)             # Running in interactive mode?
print(duckdb.__jupyter__)                 # Running in Jupyter?
```

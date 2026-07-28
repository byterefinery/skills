# File I/O

## Reading Files

### CSV

```python
import duckdb

# Simple read (auto-detects schema)
rel = duckdb.read_csv("data.csv")

# With options
rel = duckdb.read_csv(
    "data.csv",
    header=True,
    sep=",",
    quotechar='"',
    escapechar='\\',
    encoding="utf-8",
    compression=None,           # None, "gzip", "zstd", "lz4", etc.
    parallel=True,
    auto_detect=True,           # auto-detect schema (default)
    sample_size=1024 * 1024,    # bytes to sample for detection
    date_format="%Y-%m-%d",
    timestamp_format="%Y-%m-%d %H:%M:%S",
    na_values=["", "NA", "N/A"],
    skiprows=1,
    names=["col1", "col2"],
    all_varchar=False,          # read all columns as varchar
    normalize_names=False,      # normalize column names (lowercase, replace spaces)
)

# Multiple files / glob patterns
rel = duckdb.read_csv("data_*.csv")
rel = duckdb.read_csv("s3://bucket/data/*.parquet")

# Type overrides
rel = duckdb.read_csv("data.csv", dtype={"price": "DOUBLE", "date": "DATE"})

# Column type specification
rel = duckdb.read_csv("data.csv", columns={"col1": "INTEGER", "col2": "VARCHAR"})

# Reject handling
rel = duckdb.read_csv(
    "data.csv",
    ignore_errors=True,
    store_rejects=True,
    rejects_table="csv_rejects",
    rejects_limit=1000,
)

# Hive partitioning
rel = duckdb.read_csv("data/*/*/*.csv", hive_partitioning=True)
```

### Parquet

```python
# Simple read
rel = duckdb.read_parquet("data.parquet")

# With options
rel = duckdb.read_parquet(
    "data.parquet",
    binary_as_string=False,     # read BINARY as BLOB (default) or as VARCHAR
    file_row_number=False,      # add __row_id column
    filename=False,             # add __filename column
    hive_partitioning=False,
    union_by_name=False,        # union by column name across files
)

# Multiple files / globs
rel = duckdb.read_parquet("data_*.parquet")
rel = duckdb.read_parquet(["file1.parquet", "file2.parquet"])
```

### JSON

```python
rel = duckdb.read_json("data.json")

rel = duckdb.read_json(
    "data.json",
    format="auto",              # "auto", "newline_delimited", "json"
    records=False,              # treat top-level array elements as records
    maximum_depth=4,            # max nesting depth for schema inference
    sample_size=1024 * 1024,
    compression=None,
    ignore_errors=True,
    convert_strings_to_integers=True,
    field_appearance_threshold=0.6,  # threshold for inferring fields
    map_inference_threshold=0.6,
    filename=False,
    hive_partitioning=False,
)
```

## Writing Files

### From Relations

```python
rel = duckdb.sql("SELECT * FROM data")

# CSV
rel.to_csv("output.csv")
rel.to_csv("output.csv", sep=";", header=True, na_rep="NULL")
rel.to_csv("output.csv", quoting=True, quotechar='"')
rel.to_csv("output.csv", date_format="%Y-%m-%d", timestamp_format="%Y-%m-%d %H:%M:%S")
rel.to_csv("output.csv", compression="gzip")
rel.to_csv("output.csv", encoding="utf-8")
rel.to_csv("output.csv", overwrite=True)

# Parquet
rel.to_parquet("output.parquet")
rel.to_parquet("output.parquet", compression="zstd")
rel.to_parquet("output.parquet", row_group_size=100000)
rel.to_parquet("output.parquet", row_group_size_bytes="128MB")
rel.to_parquet("output.parquet", overwrite=True)
rel.to_parquet("output.parquet", append=True)

# Partitioned writes
rel.to_parquet("output/", partition_by=["date", "category"])
rel.to_csv("output/", partition_by=["date"])

# File size control
rel.to_parquet("output/", file_size_bytes="1GB")
rel.to_parquet("output/", filename_pattern="part_#.parquet")

# Per-thread output (no merging, faster)
rel.to_parquet("output/", per_thread_output=True)
```

### COPY Statements

```python
con = duckdb.connect()

# Write
con.execute("COPY (SELECT * FROM data) TO 'output.parquet' (FORMAT PARQUET)")
con.execute("COPY (SELECT * FROM data) TO 'output.csv' (HEADER TRUE, DELIMITER ',')")
con.execute("COPY (SELECT * FROM data) TO 'output.json' (FORMAT JSON)")

# Read into table
con.execute("COPY data FROM 'input.parquet'")
con.execute("COPY data FROM 'input.csv' (HEADER TRUE)")
```

## DuckDB File Format

```python
# Create persistent database
con = duckdb.connect("my_database.duckdb")
con.execute("CREATE TABLE t (id INT, val DOUBLE)")
con.execute("INSERT INTO t VALUES (1, 3.14)")
con.close()

# Reopen
con = duckdb.connect("my_database.duckdb")
con.execute("SELECT * FROM t").fetchall()

# Attach external databases
con.execute("ATTACH 'other.duckdb' AS other_db")
con.execute("SELECT * FROM other_db.my_table")
con.execute("DETACH other_db")
```

## Remote Files

```python
# HTTP/HTTPS (requires httpfs extension)
duckdb.load_extension("httpfs")
rel = duckdb.read_parquet("https://example.com/data.parquet")

# S3 (requires httpfs extension + credentials)
duckdb.load_extension("httpfs")
duckdb.config = {"s3_region": "us-east-1", "s3_access_key_id": "...", "s3_secret_access_key": "..."}
rel = duckdb.read_parquet("s3://bucket/data.parquet")

# With fsspec
from fsspec.implementations.http import HTTPFileSystem
duckdb.register_filesystem(HTTPFileSystem())
rel = duckdb.read_parquet("https://example.com/data.parquet")
```

## Performance Tips

- Use Parquet over CSV when possible — columnar format, built-in compression, schema preservation
- Enable `parallel=True` for CSV reading (default) — DuckDB parallelizes file scanning
- Use `sample_size` to speed up schema detection for large files
- For very large files, consider `fetch_df_chunk()` or `to_arrow_reader()` for streaming
- `per_thread_output=True` avoids merging overhead when writing partitioned files
- `union_by_name=True` when reading multiple Parquet files with potentially different schemas

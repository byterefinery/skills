# Data I/O

## Reading CSV

```python
import duckdb

# Basic
rel = duckdb.read_csv("data.csv")
rel = duckdb.from_csv_auto("data.csv")  # alias

# With options
rel = duckdb.read_csv(
    "data.csv",
    header=True,               # auto-detect by default
    sep=",",                   # or delimiter="|"
    compression="gzip",        # "gzip", "zstd", "none", None
    encoding="utf-8",          # "utf-8", "utf-16", "latin-1"
    sample_size=10000,         # rows to sample for type inference
    auto_detect=True,          # enable/disable auto-detection
    parallel=True,             # parallel reading
    date_format="%Y-%m-%d",
    timestamp_format="%Y-%m-%d %H:%M:%S",
    na_values=["NA", "N/A"],   # additional null markers
    skiprows=1,                # skip N rows from start
    comment="#",               # comment character
    quotechar='"',
    escapechar='\\',
)

# Explicit column types
rel = duckdb.read_csv(
    "data.csv",
    columns={"id": "INTEGER", "name": "VARCHAR", "price": "DOUBLE"},
)

# Multiple files / glob patterns
rel = duckdb.read_csv("data/*.csv")
rel = duckdb.read_csv(["file1.csv", "file2.csv"])

# From buffer
import io
rel = duckdb.read_csv(io.BytesIO(b"name,age\nAlice,30\nBob,25"))

# Hive partitioning
rel = duckdb.read_csv("s3://bucket/data/*/*.csv", hive_partitioning=True)
```

### Key CSV Options

| Option | Type | Default | Description |
|---|---|---|---|
| `header` | bool/int/None | None | True=first row, int=row number, None=auto |
| `sep` / `delimiter` | str | auto | Column separator |
| `compression` | str/None | None | "gzip", "zstd", "none" |
| `auto_detect` | bool/int/None | True | Auto-infer schema |
| `sample_size` | int | 0 | Rows for type inference (0=all) |
| `parallel` | bool/None | True | Parallel reading |
| `all_varchar` | bool | False | Read all columns as VARCHAR |
| `normalize_names` | bool | False | Normalize column names |
| `ignore_errors` | bool | False | Skip malformed rows |
| `store_rejects` | bool | False | Store rejected rows |
| `rejects_table` | str/None | None | Table name for rejects |
| `rejects_limit` | int/None | None | Max rejects to store |
| `filename` | bool/str/None | None | Include filename as column |
| `union_by_name` | bool | False | Union by column names (multi-file) |
| `strict_mode` | bool | False | Strict parsing mode |

## Reading Parquet

```python
import duckdb

# Basic
rel = duckdb.read_parquet("data.parquet")
rel = duckdb.from_parquet("data.parquet")  # alias

# Multiple files / glob
rel = duckdb.read_parquet("data/*.parquet")
rel = duckdb.read_parquet(["file1.parquet", "file2.parquet"])

# Options
rel = duckdb.read_parquet(
    "data.parquet",
    binary_as_string=False,       # treat binary as VARCHAR
    file_row_number=False,        # include file row number
    filename=False,               # include source filename
    hive_partitioning=False,      # read Hive partitions
    union_by_name=False,          # union by column names
    compression=None,             # override: "uncompressed", "snappy", etc.
)

# From buffer
import io
rel = duckdb.read_parquet(io.BytesIO(parquet_bytes))
```

## Reading JSON

```python
import duckdb

# Basic
rel = duckdb.read_json("data.json")

# Options
rel = duckdb.read_json(
    "data.json",
    format="auto",                # "auto", "unstructured", "newline_delimited", "array"
    records="auto",               # treat as JSON records array
    compression="auto_detect",    # "auto_detect", "none", "gzip", "zstd"
    maximum_depth=5,              # max nesting depth
    sample_size=0,                # rows to sample (0=all)
    ignore_errors=False,          # skip malformed entries
    convert_strings_to_integers=True,  # auto-convert numeric strings
    field_appearance_threshold=0.8,  # min fraction for column inclusion
    map_inference_threshold=0.8,   # threshold for MAP type inference
    maximum_sample_files=10,      # max files to sample
    filename=False,               # include source filename
    hive_partitioning=False,
    union_by_name=False,
)

# Multiple files
rel = duckdb.read_json("data/*.json")
```

## Writing Parquet

```python
# From Relation
rel.to_parquet("output.parquet")
rel.write_parquet(
    "output.parquet",
    compression="zstd",              # "uncompressed", "brotli", "snappy", "lz4", etc.
    field_ids=None,                  # None or {"col": int} or "auto"
    row_group_size_bytes=None,       # e.g. "64MB"
    row_group_size=None,             # rows per group
    overwrite=False,
    partition_by=["date"],           # partition by column
    write_partition_columns=True,
    append=False,                    # append to existing
    filename_pattern="{DATE}",       # multi-file pattern
    file_size_bytes="1GB",           # target file size
)
```

## Writing CSV

```python
# From Relation
rel.to_csv("output.csv")
rel.write_csv(
    "output.csv",
    sep=",",
    na_rep="",                       # null representation
    header=True,
    quotechar='"',
    escapechar='\\',
    date_format="%Y-%m-%d",
    timestamp_format="%Y-%m-%d %H:%M:%S",
    quoting=None,
    encoding="utf-8",
    compression=None,                # "gzip", "zstd", "none"
    overwrite=False,
    partition_by=["category"],       # partition by column
)
```

## DataFrame I/O

```python
import duckdb
import pandas as pd

# DataFrame to Relation
rel = duckdb.from_df(df)
rel = conn.from_df(df)

# Register DataFrame as virtual table
conn.register("my_table", df)
duckdb.sql("SELECT * FROM my_table").show()

# Append DataFrame to existing table
duckdb.append("existing_table", df, connection=conn)
conn.append("existing_table", df, by_name=False)

# Relation to DataFrame
df = rel.df()
df = rel.fetchdf()
df = conn.df()
df = conn.fetchdf()
df = conn.fetch_df()

# Chunked fetch for large results
df_chunk = rel.fetch_df_chunk(vectors_per_chunk=1)
```

## Arrow I/O

```python
import duckdb
import pyarrow as pa

# Arrow to Relation
rel = duckdb.from_arrow(arrow_table)
rel = conn.from_arrow(arrow_table)

# Relation to Arrow
table = rel.to_arrow_table()
reader = rel.to_arrow_reader()       # streaming
table = conn.to_arrow_table()
reader = conn.to_arrow_reader()

# Deprecated (use to_arrow_* instead):
table = rel.fetch_arrow_table()      # deprecated
reader = rel.fetch_record_batch()    # deprecated
```

# I/O Operations Reference

Reading and writing data from/to files, databases, and other sources.

## CSV Files

### `pd.read_csv()`

```python
# Basic usage
df = pd.read_csv("data.csv")

# Common parameters
df = pd.read_csv(
    "data.csv",
    sep=",",                    # Delimiter (default: comma)
    header=0,                   # Row number for column names
    names=["a", "b", "c"],      # Custom column names
    index_col=0,                # Column to use as index
    dtype={"col": "Int64"},     # Explicit dtypes per column
    usecols=["a", "b"],         # Only read specific columns
    parse_dates=["date"],       # Parse columns as dates
    date_format="%Y-%m-%d",     # Date format hint
    na_values=["?", ""],        # Additional NA values
    skiprows=3,                 # Skip first 3 rows
    nrows=1000,                 # Read only first 1000 rows
    encoding="utf-8",           # File encoding
    engine="c",                 # Parser: "c" (default) or "python" or "pyarrow"
    low_memory=True,            # Process file in chunks (default True)
    thousands=",",              # Thousands separator
    on_bad_lines="warn",        # How to handle bad lines: "error", "warn", "skip"
)

# Large files — chunked reading
chunk_iter = pd.read_csv("large.csv", chunksize=100_000)
for chunk in chunk_iter:
    process(chunk)

# From URL
df = pd.read_csv("https://example.com/data.csv")

# From string
df = pd.read_csv(StringIO("a,b\n1,2\n3,4"))
```

### `df.to_csv()`

```python
df.to_csv(
    "output.csv",
    index=False,                # Don't write row indices
    columns=["a", "b"],         # Write only specific columns
    sep=",",                    # Delimiter
    na_rep="",                  # Representation for NA values
    float_format="{:.6f}",      # v3.0: f-string format (also "% .2f")
    date_format="%Y-%m-%d",     # Date formatting
    encoding="utf-8",           # File encoding
    compression="gzip",         # "infer", "gzip", "bz2", "zip", "xz", None
)
```

## Excel Files

### `pd.read_excel()`

```python
df = pd.read_excel(
    "data.xlsx",
    sheet_name=0,               # Sheet name or index (0 = first)
    header=0,                   # Row with column names
    usecols="A:D",              # Column range
    dtype={"col": str},         # Explicit dtypes
    engine="openpyxl",          # "openpyxl" (.xlsx) or "calamine" or "odf"
    na_values=["N/A"],          # NA value strings
    skiprows=2,                 # Skip rows from top
)

# Read all sheets as dict
all_sheets = pd.read_excel("data.xlsx", sheet_name=None)
# {"Sheet1": DataFrame, "Sheet2": DataFrame}
```

### `df.to_excel()`

```python
df.to_excel(
    "output.xlsx",
    sheet_name="Data",
    index=False,
    merge_cells=True,           # Merge MultiIndex header cells
    # merge_cells="columns",    # v3.0: only merge column headers
    autofilter=True,            # v3.0: add auto-filters to all columns
    engine="openpyxl",
)

# Multiple sheets
with pd.ExcelWriter("output.xlsx") as writer:
    df1.to_excel(writer, sheet_name="Sheet1")
    df2.to_excel(writer, sheet_name="Sheet2")
```

## Parquet Files

Efficient columnar format. Requires `pyarrow` or `fastparquet`.

```python
# Read
df = pd.read_parquet("data.parquet")
df = pd.read_parquet(
    "data.parquet",
    columns=["a", "b"],                  # Only read specific columns
    engine="pyarrow",                    # "pyarrow" (default) or "fastparquet"
    filters=[("date", ">=", "2024-01-01")],  # Predicate pushdown
    to_pandas_kwargs={"maps_as_pydicts": True},  # v3.0: forward kwargs
)

# Write
df.to_parquet(
    "data.parquet",
    engine="pyarrow",
    compression="snappy",     # "snappy", "gzip", "brotli", None
    index=False,
)
```

## SQL Databases

### `pd.read_sql()` / `pd.read_sql_query()` / `pd.read_sql_table()`

```python
import sqlalchemy as sa

engine = sa.create_engine("postgresql://user:pass@host/db")

# From query
df = pd.read_sql(
    "SELECT * FROM table WHERE date > :start",
    engine,
    params={"start": "2024-01-01"},
    parse_dates=["date"],
    chunksize=10000,            # Return iterator for large results
)

# From table name
df = pd.read_sql_table("table_name", engine, index_col="id")

# Large query — chunked
for chunk in pd.read_sql("SELECT * FROM large_table", engine, chunksize=50000):
    process(chunk)
```

### `df.to_sql()`

```python
df.to_sql(
    "table_name",
    engine,
    if_exists="append",       # "fail", "append", "replace", "delete_rows" (v3.0)
    index=False,
    dtype={"col": sa.types.Integer()},  # Explicit column types
    chunksize=1000,           # Insert in batches
    method="multi",           # Use multi-row insert for speed
)
```

## JSON

### `pd.read_json()`

```python
df = pd.read_json("data.json")
df = pd.read_json(
    '{"a": [1,2], "b": [3,4]}',
    orient="columns",         # "columns", "records", "index", "table", "split", "values"
    lines=True,               # JSON Lines format (one JSON object per line)
    dtype={"col": "Int64"},
)

# From API response
import urllib.request
with urllib.request.urlopen("https://api.example.com/data") as resp:
    df = pd.read_json(resp, lines=True)
```

### `df.to_json()`

```python
df.to_json(
    "output.json",
    orient="records",         # List of row dicts
    # orient="columns",      # Dict of column arrays
    # orient="index",        # Dict of row dicts keyed by index
    # orient="table",        # Includes schema metadata
    date_format="iso",        # "iso" or "epoch"
    double_precision=6,       # Decimal precision for floats
    force_ascii=False,
    lines=True,               # JSON Lines format
)
```

### `pd.json_normalize()`

Flatten nested JSON structures.

```python
data = [
    {"name": "Alice", "address": {"city": "NYC", "zip": "10001"}},
    {"name": "Bob", "address": {"city": "LA", "zip": "90001"}}
]
df = pd.json_normalize(data)
#   name  address.city  address.zip

# With record expansion
data = [
    {"name": "Alice", "scores": [{"test": 1, "score": 85}, {"test": 2, "score": 92}]}
]
df = pd.json_normalize(data, record_path="scores", meta=["name"])
#    test  score   name
# 0     1     85  Alice
# 1     2     92  Alice
```

## HTML

```python
# Read tables from HTML page
dfs = pd.read_html("https://example.com/table_page")
# Returns list of DataFrames (one per <table> found)

df = pd.read_html(
    html_string,
    match="Revenue",           # Only tables containing this text
    header=0,
    flavor="lxml",             # Parser: "lxml" or "html5lib"
)
```

## XML

```python
df = pd.read_xml("data.xml")
df = pd.read_xml(
    xml_string,
    xpath=".//row",            # XPath to data rows
    columns=["a", "b"],
)
```

## Pickle (Python Serialization)

```python
# Save
df.to_pickle("data.pkl")
pd.to_pickle(df, "data.pkl")

# Load
df = pd.read_pickle("data.pkl")
```

## Feather / ORC

Arrow-based formats for fast read/write.

```python
# Feather
df.to_feather("data.feather", compression="zstd")
df = pd.read_feather("data.feather")

# ORC
df.to_orc("data.orc")
df = pd.read_orc("data.orc")
```

## Clipboard

```python
# Copy from spreadsheet → paste into pandas
df = pd.read_clipboard()

# Write to clipboard
df.to_clipboard(index=False)
```

## HDF5 (PyTables)

```python
# Store
with pd.HDFStore("data.h5") as store:
    store.put("my_df", df, format="table", data_columns=True)

# Read
df = pd.read_hdf("data.h5", key="my_df")

# Query within store
df = pd.read_hdf("data.h5", "my_df", where="date > '2024-01-01'")
```

## Stata / SAS / SPSS

```python
# Stata
df = pd.read_stata("data.dta", convert_nonutf8=True)
df.to_stata("output.dta", write_index=False)

# SAS
df = pd.read_sas("data.sas7bdat")

# SPSS
df = pd.read_spss("data.sav")
```

## Iceberg (v3.0+)

```python
# Read from Apache Iceberg table
df = pd.read_iceberg("s3://bucket/db/table")

# Write to Iceberg
df.to_iceberg("s3://bucket/db/table")
```

## Arrow PyCapsule Interface (v3.0+)

Zero-copy data exchange with Arrow-compatible libraries.

```python
# Import from any Arrow-compatible object
df = pd.DataFrame.from_arrow(arrow_table)
s = pd.Series.from_arrow(arrow_chunk)

# Export (DataFrame/Series implement __arrow_c_stream__)
arrow_table = df.__arrow_c_stream__()
```

## Common I/O Patterns

```python
# Read multiple CSV files and concatenate
files = ["part1.csv", "part2.csv", "part3.csv"]
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

# Parquet partitioned reads
df = pd.read_parquet("s3://bucket/data/*.parquet")

# Cache expensive reads
import functools
@functools.lru_cache(maxsize=4)
def load_data(path: str):
    return pd.read_parquet(path)
```

# Relational API (DuckDBPyRelation)

## Core Concept

`DuckDBPyRelation` is a lazy, immutable query plan. Methods return new Relations — the original is unchanged. Results materialize only on terminal operations.

```python
import duckdb

rel = duckdb.sql("SELECT * FROM sales")  # lazy — no execution yet
rel.show()                                # triggers execution
```

## Creating Relations

```python
# From SQL
rel = duckdb.sql("SELECT * FROM t")
rel = conn.sql("SELECT * FROM t", alias="my_alias")
rel = conn.query("SELECT * FROM t")       # same as sql()
rel = conn.from_query("SELECT * FROM t")

# From DataFrames
rel = duckdb.from_df(df)
rel = conn.from_df(df)

# From files
rel = duckdb.read_csv("data.csv")
rel = duckdb.read_parquet("data.parquet")
rel = duckdb.read_json("data.json")
rel = duckdb.from_csv_auto("data.csv")    # same as read_csv()
rel = duckdb.from_parquet("data.parquet")  # same as read_parquet()

# From Arrow
rel = duckdb.from_arrow(arrow_table)

# From existing table/view
rel = conn.table("table_name")
rel = conn.view("view_name")

# From values (literal rows)
rel = conn.values([1, "a"], [2, "b"], [3, "c"])

# Table functions
rel = conn.table_function("range", [100])
```

## Chaining Operators

All operators return new `DuckDBPyRelation` instances:

### Filtering and Projection

```python
rel.filter("amount > 100")
rel.filter(duckdb.ColumnExpression("amount") > 100)
rel.filter(rel["amount"] > 100)

rel.project("name, amount * 2 as doubled")
rel.project("name", "SUM(amount)")
rel.select("name, amount")           # alias for project()
rel.select_dtypes(["INTEGER", "VARCHAR"])  # filter by column types
```

### Ordering and Limiting

```python
rel.order("amount DESC, name ASC")
rel.sort("amount DESC")              # alias for order()
rel.limit(10)
rel.limit(10, offset=5)
```

### Aggregation

```python
# Simple aggregation
rel.aggregate("SUM(amount)")
rel.aggregate("COUNT(*)")

# Grouped aggregation
rel.aggregate("region, SUM(amount)", "region")
rel.sum("amount", groups="region")
rel.count("*", groups="category")
rel.avg("price", groups="category")
rel.min("price", groups="category")
rel.max("price", groups="category")
rel.median("price", groups="category")
rel.stddev("price", groups="category")
rel.variance("price", groups="category")
rel.quantile("price", q=0.9, groups="category")
rel.histogram("price", groups="category")
rel.value_counts("status")
rel.string_agg("name", sep=", ", groups="region")
```

### Set Operations

```python
rel1.union(rel2)
rel1.intersect(rel2)
rel1.except_(rel2)
rel.distinct()
```

### Joins

```python
rel1.join(rel2, "t1.id = t2.id", how="inner")
# Join types: "inner", "left", "right", "outer", "semi", "anti"
rel1.cross(rel2)  # cross join
```

### Window Functions

```python
rel.rank("ORDER BY amount DESC")
rel.dense_rank("ORDER BY amount DESC")
rel.row_number("ORDER BY amount DESC")
rel.percent_rank("ORDER BY amount DESC")
rel.cume_dist("ORDER BY amount DESC")
rel.n_tile("ORDER BY amount DESC", num_buckets=10)
rel.lag("amount", "ORDER BY date", offset=1)
rel.lead("amount", "ORDER BY date", offset=1)
rel.first_value("name", "PARTITION BY region ORDER BY date")
rel.last_value("name", "PARTITION BY region ORDER BY date")
```

## Terminal Operations

These trigger execution and materialize results:

```python
# Display
rel.show()
rel.show(max_rows=20, max_width=80)

# Fetch as Python objects
rows = rel.fetchall()        # list[tuple]
row = rel.fetchone()         # tuple | None
chunk = rel.fetchmany(100)   # list[tuple]

# Fetch as DataFrames
df = rel.df()                # pandas DataFrame
df = rel.fetchdf()           # same as df()
df = rel.fetch_df_chunk()    # chunked fetch

# Fetch as Arrow
table = rel.to_arrow_table()          # pyarrow.Table
reader = rel.to_arrow_reader()        # RecordBatchReader (streaming)

# Fetch as NumPy
arrays = rel.fetchnumpy()  # dict[str, np.ndarray]

# Polars
pl_df = rel.pl()              # polars.DataFrame
pl_lf = rel.pl(lazy=True)     # polars.LazyFrame

# Create persistent objects
rel.create("my_table")        # create table from relation
rel.to_table("my_table")      # same as create()
rel.create_view("my_view")    # create view
rel.to_view("my_view")        # same as create_view()

# Write to files
rel.to_parquet("output.parquet")
rel.to_csv("output.csv")
rel.write_parquet("output.parquet", compression="zstd")
rel.write_csv("output.csv", sep=";", header=True)
```

## Relation Properties

```python
rel.columns       # list[str] — column names
rel.dtypes        # list[DuckDBPyType] — column types
rel.types         # same as dtypes
rel.shape         # (rows, cols) tuple
rel.alias         # str — relation alias
rel.description   # DB-API description tuples
rel.type          # str — relation type info
```

## Query Inspection

```python
# Get the underlying SQL
sql = rel.sql_query()

# Explain the query plan
plan = rel.explain()
plan = rel.explain(type=duckdb.ExplainType.STANDARD)
# ExplainType: STANDARD, PHYSICAL, OPTIMIZED_LOGICAL, etc.
```

## Map (Row-wise Python Function)

```python
# Apply a Python function to each row
def process_row(row):
    return (row["name"], row["amount"] * 1.1)

result = rel.map(process_row, schema={"name": "VARCHAR", "taxed": "DOUBLE"})
```

## Update and Insert

```python
# Insert into existing table
rel.insert_into("target_table")

# Insert single row
rel.insert([1, "value"])

# Update (on materialized relations)
rel.update({"amount": rel["amount"] * 2}, condition="id > 100")
```

## Aliasing and Column Access

```python
rel = rel.set_alias("sales_data")
col = rel["amount"]           # column projection
col = rel.amount              # attribute access
"amount" in rel               # __contains__ check
len(rel)                      # row count (triggers execution!)
```

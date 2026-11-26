# Relation API (DuckDBPyRelation)

## Core Concept

Relations are lazy query plans. Every operation returns a new `DuckDBPyRelation` — nothing executes until you call `.show()`, `.df()`, `.fetchall()`, `.to_parquet()`, etc.

```python
import duckdb

rel = duckdb.sql("SELECT * FROM data")           # lazy
rel = rel.filter("amount > 100")                  # still lazy
rel = rel.project("date, amount").order("date")   # still lazy
rel.show()                                         # evaluates here
```

## Creating Relations

```python
# From SQL
rel = duckdb.sql("SELECT * FROM my_table")
rel = duckdb.query("SELECT * FROM my_table")

# From files
rel = duckdb.read_csv("data.csv")
rel = duckdb.read_parquet("data.parquet")
rel = duckdb.read_json("data.json")

# From DataFrames
rel = duckdb.from_df(pandas_df)

# From Arrow
rel = duckdb.from_arrow(arrow_table)

# From a query (subquery as relation)
rel = duckdb.from_query("SELECT * FROM t WHERE x > 0")

# From values
rel = duckdb.values([1, 2, 3], [4, 5, 6]).project("a, b")

# From connection
con = duckdb.connect()
rel = con.query("SELECT * FROM t")
rel = con.table("my_table")
rel = con.view("my_view")
rel = con.from_df(df)
rel = con.from_arrow(table)
```

## Projection and Selection

```python
# project / select — choose columns and expressions
rel.project("name, age * 2 as double_age")
rel.project("name", "age + 10")
rel.select("name", "SUM(age) as total_age", groups="name")

# Filter
rel.filter("age > 21")
rel.filter("name = 'Alice' AND age > 21")

# Distinct
rel.distinct()

# Limit and offset
rel.limit(10)
rel.limit(10, offset=5)

# Order / sort
rel.order("name")
rel.order("name DESC, age ASC")
rel.sort("name", "age DESC")
```

## Aggregations

```python
# aggregate — explicit aggregation expressions
rel.aggregate("AVG(age), COUNT(*)", group_expr="name")
rel.aggregate("SUM(amount), AVG(amount)", group_expr="category")

# Convenience methods (each takes expression, groups, window_spec, projected_columns)
rel.count("id", groups="name")
rel.sum("amount", groups="category")
rel.avg("amount", groups="category")
rel.min("price", groups="product")
rel.max("price", groups="product")
rel.median("price", groups="product")
rel.std("price", groups="product")
rel.stddev("price", groups="product")
rel.var("price", groups="product")
rel.product("quantity", groups="order_id")
rel.list("item", groups="order_id")
rel.string_agg("name", sep=", ", groups="category")

# Quantiles
rel.quantile("price", q=0.5, groups="category")
rel.quantile("price", q=[0.25, 0.5, 0.75], groups="category")
rel.quantile_cont("price", q=0.5)
rel.quantile_disc("price", q=0.5)

# Statistical
rel.geomean("value")
rel.mode("category")
rel.histogram("age")
rel.value_counts("status")

# Window functions
rel.rank("ORDER BY amount DESC")
rel.dense_rank("ORDER BY amount DESC")
rel.row_number("ORDER BY created_at DESC")
rel.percent_rank("ORDER BY score DESC")
rel.cume_dist("ORDER BY score DESC")
rel.n_tile("ORDER BY amount DESC", num_buckets=10)
rel.lag("amount", "ORDER BY date", offset=1)
rel.lead("amount", "ORDER BY date", offset=1)
rel.first_value("price", "PARTITION BY product ORDER BY date")
rel.last_value("price", "PARTITION BY product ORDER BY date")
rel.nth_value("price", "PARTITION BY product ORDER BY date", offset=2)

# Bitwise aggregations
rel.bit_and("flags")
rel.bit_or("flags")
rel.bit_xor("flags")
rel.bool_and("is_valid")
rel.bool_or("is_valid")

# Floating-point sum (higher precision)
rel.fsum("amount")

# Approximate
rel.unique("user_id")  # approximate count distinct
rel.any_value("name", groups="category")
rel.apply("name", "first", groups="category")
rel.arg_max("name", "score", groups="category")
rel.arg_min("name", "score", groups="category")
```

## Joins

```python
rel1.join(rel2, "t1.id = t2.id")                          # inner join (default)
rel1.join(rel2, "t1.id = t2.id", how="inner")
rel1.join(rel2, "t1.id = t2.id", how="left")
rel1.join(rel2, "t1.id = t2.id", how="right")
rel1.join(rel2, "t1.id = t2.id", how="outer")
rel1.join(rel2, "t1.id = t2.id", how="semi")
rel1.join(rel2, "t1.id = t2.id", how="anti")
rel1.join(rel2, "t1.id = t2.id", how="asof")
rel1.cross(rel2)                                           # cross join
```

## Set Operations

```python
rel1.union(rel2)
rel1.intersect(rel2)
rel1.except_(rel2)
```

## Output and Conversion

```python
# Display
rel.show()
rel.show(max_rows=20, max_width=80, null_value="N/A")

# To pandas
df = rel.df()
df = rel.df(date_as_object=True)

# Chunked pandas (for large results)
while True:
    chunk = rel.fetch_df_chunk()
    if chunk.empty:
        break

# To Polars
pl_df = rel.pl()
pl_lazy = rel.pl(lazy=True)

# To PyArrow
table = rel.to_arrow_table()
reader = rel.to_arrow_reader(batch_size=10000)

# To list of tuples
rows = rel.fetchall()
row = rel.fetchone()
rows = rel.fetchmany(10)

# To NumPy
arrays = rel.fetchnumpy()

# Write to files
rel.to_csv("output.csv")
rel.to_csv("output.csv", sep=";", header=True)
rel.to_parquet("output.parquet")
rel.to_parquet("output.parquet", compression="zstd")

# Partitioned writes
rel.to_parquet("output/", partition_by=["date", "category"])
rel.to_csv("output/", partition_by=["date"])
```

## Inspecting Relations

```python
# Metadata
rel.columns        # list of column names
rel.dtypes         # list of DuckDBPyType
rel.types          # alias for dtypes
rel.shape          # (rows, cols) — triggers evaluation
rel.description    # DB-API style description
rel.alias          # relation alias
rel.type           # relation type string

# SQL representation
rel.sql_query()    # the underlying SQL string

# Explain query plan
rel.explain()
rel.explain(duckdb.ExplainType.STANDARD)
rel.explain(duckdb.ExplainType.DETAILED)
rel.explain(duckdb.ExplainType.TIMED)

# Describe (schema info as relation)
rel.describe()

# Check column presence
"amount" in rel

# Access columns by attribute or index
rel["amount"]
rel.amount

# Select by dtype
rel.select_dtypes([duckdb.dtype("INTEGER"), duckdb.dtype("DOUBLE")])
```

## Mutation

```python
# Create a table from a relation
rel.create("my_table")

# Create a view
rel.create_view("my_view")
rel.to_view("my_view", replace=True)

# Insert into existing table
rel.insert_into("target_table")

# Insert single row
rel.insert([1, "Alice", 30])

# Update
rel.update({"amount": "amount * 1.1"}, condition="date > '2024-01-01'")

# Execute (materialize)
rel.execute()
```

## Map (row-wise Python function)

```python
# Apply a Python function to each row
rel.map(
    lambda row: row["amount"] * 1.1,
    schema={"amount": duckdb.dtype("DOUBLE")}
)
```

## Aliases

```python
rel.set_alias("sales")
```

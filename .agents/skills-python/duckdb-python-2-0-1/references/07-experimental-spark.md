# Experimental Spark Compatibility

## Overview

DuckDB provides an experimental PySpark compatibility layer under `duckdb.experimental.spark`. It is **not a full Spark implementation** — it maps a subset of the Spark API to DuckDB's SQL engine for local development and testing.

```python
from duckdb.experimental.spark import SparkSession, SparkContext, SparkConf
```

## SparkSession

```python
from duckdb.experimental.spark import SparkSession

# Create session
spark = SparkSession.builder.getOrCreate()

# Read data
df = spark.read.parquet("data.parquet")
df = spark.read.csv("data.csv")

# DataFrame operations
df.filter(df.amount > 100).select("date", "amount").show()
df.groupBy("category").avg("amount").show()

# SQL
spark.sql("SELECT * FROM data WHERE amount > 100").show()

# Write
df.write.parquet("output.parquet")
df.write.csv("output.csv")
```

## SparkContext

```python
from duckdb.experimental.spark import SparkContext

sc = SparkContext(master="local")

# Access underlying DuckDB connection
con = sc.connection

# Stop
sc.stop()
```

## SparkConf

```python
from duckdb.experimental.spark import SparkConf

conf = SparkConf()
```

## Limitations

- **Not a Spark replacement** — this is a compatibility shim for local testing
- Many Spark methods raise `ContributionsAcceptedError` — the project invites community contributions to fill gaps
- `SparkContext.getOrCreate()`, `setSystemProperty()`, `applicationId`, `defaultMinPartitions`, `defaultParallelism`, `startTime`, `uiWebUrl` all raise `ContributionsAcceptedError`
- The layer sets `default_null_order='nulls_first_on_asc_last_on_desc'` to align null ordering with Spark
- Complex distributed operations, RDD API, and streaming are not supported

## When to Use

- Testing Spark code locally without a cluster
- Migrating from Spark to DuckDB for workloads that fit in memory
- Prototyping Spark DataFrames before deploying to a real cluster

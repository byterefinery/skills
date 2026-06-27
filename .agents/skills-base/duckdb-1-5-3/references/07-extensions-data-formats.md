# Data Format Extensions — json, parquet, delta, iceberg, avro

DuckDB supports multiple data formats through extensions. Some are built-in (parquet), others are out-of-tree extensions.

## Parquet (Built-In)

Parquet support is statically linked into DuckDB — no INSTALL/LOAD needed.

### Reading

```sql
-- Direct file reference
SELECT * FROM 'data.parquet';

-- Multiple files via glob
SELECT * FROM 'data/part-*.parquet';

-- With column selection
SELECT name, age FROM 'data.parquet' WHERE age > 30;
```

### Writing

```sql
COPY (SELECT * FROM my_table) TO 'output.parquet' (FORMAT 'parquet');

-- Compression options
COPY (SELECT * FROM my_table) TO 'output.parquet'
(FORMAT 'parquet', compression 'zstd');

-- Available: uncompressed, snappy, gzip, lz4, zstd
```

### Features
- Column pruning (only reads needed columns)
- Predicate pushdown (filters applied during read)
- Partitioned datasets
- Schema evolution handling
- Remote file support (with httpfs)

## JSON Extension

### Installation

```sql
INSTALL json;
LOAD json;
```

Autoloads when referencing `.json` files.

### Reading JSON Files

```sql
-- Auto-detects JSON format from .json extension
SELECT * FROM 'data.json';

-- Explicit function
SELECT * FROM read_json_auto('data.json');

-- Options
SELECT * FROM read_json('data.json', pretty_print true);
```

### JSON Functions

```sql
-- Parse JSON string
SELECT json('{"name": "Alice", "age": 30}');

-- Extract values
SELECT json_extract('{"name": "Alice"}', '$.name');
-- Result: "Alice"

-- Flatten arrays
SELECT json_array_elements('[1, 2, 3]');
-- Result: 1, 2, 3 (as rows)

-- Parse structured JSON
SELECT * FROM json_each('[{"a": 1}, {"a": 2}]');
```

### JSON File Formats Supported
- Line-delimited JSON (JSONL/NDJSON) — one JSON object per line
- JSON array — `[ {...}, {...} ]`
- Pretty-printed JSON

## Delta Lake Extension

### Installation

```sql
INSTALL delta;
LOAD delta;
```

### Usage

```sql
-- Read a Delta table
SELECT * FROM 's3://bucket/delta-table/';

-- Read specific version
SELECT * FROM delta_scan('s3://bucket/delta-table/', version 5);

-- Read as of timestamp
SELECT * FROM delta_scan('s3://bucket/delta-table/', timestamp '2024-01-01');

-- Write to Delta table
COPY (SELECT * FROM my_table) TO 's3://bucket/delta-table/'
(FORMAT 'parquet');  -- Delta uses Parquet underneath

-- Vacuum (remove old files)
CALL delta_vacuum('s3://bucket/delta-table/');
```

### Features
- Time travel (query historical versions)
- Schema evolution
- ACID transactions
- Merge operations
- Works with local files and S3/GCS/Azure

## Iceberg Extension

### Installation

```sql
INSTALL iceberg;
LOAD iceberg;
```

### Usage

```sql
-- Read an Iceberg table
SELECT * FROM iceberg_scan('s3://bucket/iceberg-table/');

-- Read specific snapshot
SELECT * FROM iceberg_scan('s3://bucket/iceberg-table/', snapshot_id 12345);

-- Register as a view for repeated access
CREATE VIEW my_iceberg_table AS SELECT * FROM iceberg_scan('s3://bucket/table/');
```

### Features
- Snapshot isolation
- Partition evolution
- Hidden partitioning
- Column statistics
- Works with Hive metastore (via configuration)

## Avro Extension

### Installation

```sql
INSTALL avro;
LOAD avro;
```

### Usage

```sql
-- Read Avro files
SELECT * FROM 'data.avro';
SELECT * FROM read_avro('data.avro');

-- Multiple files
SELECT * FROM 'data/part-*.avro';
```

## Lance Extension

### Installation

```sql
INSTALL lance;
LOAD lance;
```

### Usage

```sql
-- Read Lance dataset
SELECT * FROM lance_scan('dataset.lance/');

-- With filtering
SELECT * FROM lance_scan('dataset.lance/', where 'score > 0.8');
```

## DuckLake Extension

### Installation

```sql
INSTALL ducklake;
LOAD ducklake;
```

DuckLake is DuckDB Labs' lakehouse format that stores data with SQL-native metadata. It enables ACID transactions, schema evolution, and time travel on top of Parquet files.

## Format Comparison

| Format | Read | Write | Time Travel | Schema Evolution | Partitioning |
|--------|------|-------|-------------|-----------------|--------------|
| Parquet | ✓ | ✓ | — | Limited | Manual |
| JSON | ✓ | ✓ | — | Flexible | — |
| Delta | ✓ | ✓ | ✓ | ✓ | ✓ |
| Iceberg | ✓ | Limited | ✓ | ✓ | ✓ |
| Avro | ✓ | — | — | ✓ | — |
| Lance | ✓ | — | — | ✓ | ✓ |

## Choosing a Format

- **Parquet**: Best for general analytical workloads, wide compatibility
- **JSON**: Best for semi-structured data, API responses, logs
- **Delta/Iceberg**: Best for lakehouse architectures requiring ACID and time travel
- **Avro**: Best for row-oriented data with schema registry (read-only in DuckDB)
- **Lance**: Best for vector search and ML workflows

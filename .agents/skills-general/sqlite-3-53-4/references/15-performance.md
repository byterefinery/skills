# Performance Tuning

## Table of Contents

- [Transaction Strategy](#transaction-strategy)
- [Indexing](#indexing)
- [PRAGMA Settings](#pragma-settings)
- [Query Optimization](#query-optimization)
- [EXPLAIN](#explain)
- [Schema Design](#schema-design)
- [Bulk Operations](#bulk-operations)
- [Memory Tuning](#memory-tuning)

## Transaction Strategy

The single biggest performance factor. Each statement is its own transaction by default.

```sql
-- SLOW: Each INSERT is a separate transaction (disk sync each time)
INSERT INTO t VALUES(1, 'a');
INSERT INTO t VALUES(2, 'b');
INSERT INTO t VALUES(3, 'c');

-- FAST: All INSERTs in one transaction (single disk sync)
BEGIN TRANSACTION;
INSERT INTO t VALUES(1, 'a');
INSERT INTO t VALUES(2, 'b');
INSERT INTO t VALUES(3, 'c');
COMMIT;
```

For bulk inserts, wrapping in a transaction can improve throughput by 10-100×.

## Indexing

### When to Index

- Columns used in WHERE clauses with selective filters
- Columns used in JOIN conditions
- Columns used in ORDER BY (especially with LIMIT)
- Columns used in GROUP BY

### When Not to Index

- Small tables (full scan may be faster)
- Columns with very low cardinality (e.g., boolean flags)
- Tables with heavy write load (each write updates all indices)
- Columns rarely used in queries

### Index Types

```sql
-- Standard B-tree index
CREATE INDEX idx_name ON users(name);

-- Composite index (order matters — leftmost prefix rule)
CREATE INDEX idx_dept_role ON employees(dept, role);
-- Useful for: WHERE dept = ? AND role = ?
-- Useful for: WHERE dept = ?
-- NOT useful for: WHERE role = ? (alone)

-- Partial index (since 3.8.0)
CREATE INDEX idx_active ON users(email) WHERE status = 'active';

-- Expression index (since 3.9.0)
CREATE INDEX idx_lower ON users(LOWER(name));

-- Covering index (INCLUDE, since 3.8.3)
CREATE INDEX idx_covering ON orders(customer_id) INCLUDE (order_date, total);
```

### Index Analysis

```sql
-- Check index usage
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'x@y.com';

-- Analyze tables for query planner
ANALYZE;
-- Or: PRAGMA optimize;
```

## PRAGMA Settings

### Recommended Defaults

```sql
PRAGMA journal_mode = WAL;        -- Better concurrency
PRAGMA synchronous = NORMAL;      -- Good safety/speed balance
PRAGMA foreign_keys = ON;         -- Enable FK enforcement
PRAGMA cache_size = -65536;       -- 64MB cache
PRAGMA temp_store = MEMORY;       -- Temp tables in memory
PRAGMA busy_timeout = 5000;       -- Wait on busy
```

### For Bulk Writes

```sql
PRAGMA synchronous = OFF;         -- Risk: corruption on crash
PRAGMA journal_mode = MEMORY;     -- In-memory journal
PRAGMA cache_size = -131072;      -- 128MB cache
BEGIN TRANSACTION;
-- ... bulk inserts ...
COMMIT;
PRAGMA synchronous = NORMAL;      -- Restore
PRAGMA journal_mode = WAL;        -- Restore
```

### For Read-Only

```sql
PRAGMA query_only = ON;
PRAGMA cache_size = -131072;
PRAGMA mmap_size = 268435456;     -- 256MB memory-mapped I/O
```

## Query Optimization

### Use Parameterized Queries

```sql
-- Prepare once, execute many times with different parameters
PREPARE stmt FROM "SELECT * FROM users WHERE id = ?";
```

### Avoid SELECT *

Specify only needed columns — enables covering index scans.

### Use LIMIT

Always use LIMIT when you only need a subset of results.

### Prefer INTEGER PRIMARY KEY

Auto-indexed, faster than separate indices.

### Use EXISTS Instead of COUNT

```sql
-- SLOW
SELECT COUNT(*) FROM users WHERE email = 'x@y.com';

-- FAST (stops at first match)
SELECT EXISTS(SELECT 1 FROM users WHERE email = 'x@y.com');
```

### Avoid Functions on Indexed Columns

```sql
-- Does NOT use index on name
SELECT * FROM users WHERE LOWER(name) = 'alice';

-- Uses index
SELECT * FROM users WHERE name = 'alice';

-- Solution: expression index
CREATE INDEX idx_lower_name ON users(LOWER(name));
```

## EXPLAIN

### EXPLAIN QUERY PLAN

Shows the high-level query plan:

```sql
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'x@y.com';
-- SCAN TABLE users USING INDEX idx_users_email  ← good
-- SCAN TABLE users                               ← full table scan
```

Key output terms:
- `SCAN TABLE` — full table scan (slow for large tables)
- `SEARCH TABLE USING INDEX` — index lookup (fast)
- `SEARCH TABLE USING COVERING INDEX` — index-only scan (fastest)
- `TEMP B-TREE FOR ORDER BY` — requires sorting (no suitable index)

### EXPLAIN

Shows VDBE bytecode (detailed, for debugging):

```sql
EXPLAIN SELECT * FROM users WHERE id = 1;
```

## Schema Design

### Normalization

Normalize to avoid data duplication and update anomalies. Denormalize selectively for read performance.

### Column Order

Put frequently queried/filtered columns first. Put large columns (TEXT, BLOB) last.

### Use Appropriate Types

- `INTEGER PRIMARY KEY` for auto-incrementing IDs
- `TEXT` for strings (no length limit enforcement)
- `REAL` for floating point
- `BLOB` for binary data
- `STRICT` tables for type safety

### Generated Columns

For frequently computed values:

```sql
CREATE TABLE orders(
  subtotal REAL,
  tax_rate REAL,
  total REAL GENERATED ALWAYS AS (subtotal * (1 + tax_rate)) STORED
);
```

## Bulk Operations

### Import from CSV

```bash
# Fastest approach
sqlite3 mydb.db <<EOF
.mode csv
.import data.csv users
EOF
```

### Bulk Insert in C

```c
sqlite3_exec(db, "BEGIN TRANSACTION", NULL, NULL, NULL);
for (int i = 0; i < N; i++) {
    sqlite3_bind_text(stmt, 1, names[i], -1, SQLITE_TRANSIENT);
    sqlite3_step(stmt);
    sqlite3_reset(stmt);
}
sqlite3_exec(db, "COMMIT", NULL, NULL, NULL);
```

### VACUUM

Reclaim space after large deletes:

```sql
VACUUM;              -- Full rebuild (uses extra disk space)
PRAGMA incremental_vacuum;  -- Incremental (requires auto_vacuum mode)
```

## Memory Tuning

| Setting | Default | Tuning |
|---|---|---|
| `cache_size` | -2000 (2MB) | Increase for large working sets |
| `mmap_size` | 0 (off) | Enable for read-heavy workloads |
| `soft_heap_limit` | unlimited | Set to cap memory usage |
| `temp_store` | DEFAULT | MEMORY for performance |

```sql
PRAGMA cache_size = -262144;     -- 256MB
PRAGMA mmap_size = 536870912;    -- 512MB
PRAGMA soft_heap_limit = 1073741824;  -- 1GB
```

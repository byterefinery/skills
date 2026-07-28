# SQLite Limits

## Table of Contents

- [Size Limits](#size-limits)
- [Structural Limits](#structural-limits)
- [Runtime Limits](#runtime-limits)
- [Changing Limits](#changing-limits)

## Size Limits

| Limit | Default | Maximum |
|---|---|---|
| Max database size | 281 TB (256 TiB) | 281 TB |
| Max page count | 4,294,967,294 | 4,294,967,294 |
| Max page size | 4,096 bytes | 65,536 bytes |
| Max row size | 1 GB (2^30 - 2) | 1 GB |
| Max string/BLOB length | 1,000,000,000 (1 GB) | 2,147,483,645 |
| Max SQL statement length | 1,000,000,000 | Compile-time |
| Max number of rows | ~2×10^13 (practical) | 2^64 (theoretical) |

## Structural Limits

| Limit | Default | Maximum |
|---|---|---|
| Max columns in table | 2,000 | 32,767 |
| Max columns in index | 2,000 | 32,767 |
| Max columns in result set | 2,000 | 32,767 |
| Max columns in INSERT | 2,000 | 32,767 |
| Max tables in a join | 64 | 64 (fixed) |
| Max expression depth | 1,000 | Compile-time |
| Max function arguments | 1,000 (since 3.48.0) | 32,767 |
| Max compound SELECT terms | 500 | Compile-time |
| Max LIKE/GLOB pattern length | 50,000 | Compile-time |
| Max host parameters | 32,766 (since 3.32.0) | Compile-time |
| Max trigger recursion depth | 1,000 | Compile-time |
| Max attached databases | 10 | 125 |
| Max schema objects | Limited by page count | Limited by page count |

## Runtime Limits

Many limits can be adjusted at runtime per-connection using `sqlite3_limit()`:

```c
int sqlite3_limit(sqlite3 *db, int limitID, int newVal);
```

Limit IDs:
- `SQLITE_LIMIT_LENGTH` — max string/BLOB length
- `SQLITE_LIMIT_SQL_LENGTH` — max SQL statement length
- `SQLITE_LIMIT_COLUMN` — max columns
- `SQLITE_LIMIT_EXPR_DEPTH` — max expression depth
- `SQLITE_LIMIT_COMPOUND_SELECT` — max compound SELECT terms
- `SQLITE_LIMIT_VARIABLE_NUMBER` — max host parameter number
- `SQLITE_LIMIT_FUNCTION_ARG` — max function arguments
- `SQLITE_LIMIT_LIKE_PATTERN_LENGTH` — max LIKE/GLOB pattern length
- `SQLITE_LIMIT_ATTACHED` — max attached databases
- `SQLITE_LIMIT_TRIGGER_DEPTH` — max trigger recursion depth
- `SQLITE_LIMIT_WORKER_THREADS` — max worker threads

Runtime limits can only **lower** the compile-time defaults, not raise them.

## Changing Limits

### Compile-Time

Override defaults by defining preprocessor macros:

```bash
gcc -DSQLITE_MAX_LENGTH=100000000 \
    -DSQLITE_MAX_COLUMN=100 \
    -DSQLITE_MAX_EXPR_DEPTH=500 \
    sqlite3.c -o sqlite3
```

### Runtime

```c
// Lower max string length
sqlite3_limit(db, SQLITE_LIMIT_LENGTH, 10000000);

// Lower max columns
sqlite3_limit(db, SQLITE_LIMIT_COLUMN, 100);

// Lower max expression depth
sqlite3_limit(db, SQLITE_LIMIT_EXPR_DEPTH, 100);
```

### Via PRAGMA

```sql
-- Max page count
PRAGMA max_page_count = 1000000;

-- Journal size limit
PRAGMA journal_size_limit = 67108864;  -- 64MB
```

## Security Considerations

For applications that process untrusted SQL:
- Lower `SQLITE_LIMIT_LENGTH` to prevent memory exhaustion
- Lower `SQLITE_LIMIT_COLUMN` to prevent slow O(N²) code generation
- Lower `SQLITE_LIMIT_EXPR_DEPTH` to prevent stack overflow
- Lower `SQLITE_LIMIT_LIKE_PATTERN_LENGTH` to prevent DoS via pathological patterns
- Lower `SQLITE_LIMIT_VARIABLE_NUMBER` to prevent excessive memory allocation
- Use `SQLITE_MAX_MEMORY` to limit total heap usage

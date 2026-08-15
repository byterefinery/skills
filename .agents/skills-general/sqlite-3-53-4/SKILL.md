---
name: sqlite-3-53-4
description: >
  Comprehensive SQLite 3.53.4 reference — SQL syntax, data types, built-in functions
  (scalar, aggregate, window, math, JSON, date/time), PRAGMAs, C/C++ API, virtual tables
  (FTS5, R-Tree), STRICT tables, WAL journaling, performance tuning, CLI usage, and
  quirks. Use when working with SQLite databases, writing SQL for SQLite, embedding
  SQLite in applications, debugging SQLite behavior, or porting between SQLite and
  other RDBMSes. Covers serverless, zero-config, ACID, single-file database engine.
license: Public Domain
compatibility: SQLite 3.53.4+ (C library); CLI is the sqlite3 command-line tool
metadata:
  tags:
    - database
    - sql
    - sqlite
    - embedded
    - c-api
    - full-text-search
---

# sqlite 3.53.4

## Overview

SQLite is a C-language library implementing a small, fast, self-contained, serverless, zero-configuration, transactional SQL database engine. A complete database lives in a single cross-platform disk file. It uses dynamic typing with five storage classes (NULL, INTEGER, REAL, TEXT, BLOB) and column type affinity rather than rigid type enforcement. Foreign key enforcement is off by default. ACID compliance holds even after crashes or power loss.

Key characteristics:
- **Serverless** — no separate server process; reads/writes directly to disk files
- **Single file** — entire database (tables, indices, triggers, views) in one file
- **Cross-platform** — file format is endian-independent and word-size-independent
- **Dynamic typing** — values carry their type, not columns; flexible by default
- **STRICT tables** — optional rigid type enforcement (since 3.37.0)
- **WAL mode** — write-ahead logging for better concurrency (default since 3.37.0 in many builds)
- **JSON support** — built-in JSON functions and JSONB binary format (since 3.38.0 / 3.45.0)
- **Public domain** — free for any use, commercial or private

## Usage

### Quick Start

```bash
# Create/open a database
sqlite3 mydb.db

# At the sqlite3 prompt, run SQL
CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, email TEXT);
INSERT INTO users VALUES(NULL, 'Alice', 'alice@example.com');
SELECT * FROM users;

# Dot-commands (CLI only)
.schema           -- show CREATE TABLE statements
.tables           -- list tables
.headers on       -- show column names
.mode column      -- formatted output
.dump             -- export full SQL dump
.read file.sql    -- execute SQL from file
```

### In C/C++

```c
#include <sqlite3.h>

sqlite3 *db;
sqlite3_open("mydb.db", &db);

sqlite3_stmt *stmt;
sqlite3_prepare_v2(db, "SELECT name FROM users WHERE id=?", -1, &stmt, 0);
sqlite3_bind_int(stmt, 1, 42);
if (sqlite3_step(stmt) == SQLITE_ROW) {
    const char *name = (const char*)sqlite3_column_text(stmt, 0);
}
sqlite3_finalize(stmt);
sqlite3_close(db);
```

### Performance Tips

- Wrap multiple INSERTs in a single `BEGIN...COMMIT` transaction — each individual INSERT is its own transaction by default, limited by disk rotation speed
- Use `PRAGMA journal_mode=WAL` for better read/write concurrency
- Use `PRAGMA synchronous=NORMAL` (default) for good balance of safety and speed; `OFF` for max speed with corruption risk on crash
- Use `PRAGMA cache_size=-2000` (default: 2MB) or higher for larger working sets
- Use `PRAGMA foreign_keys=ON` to enable FK enforcement (off by default)
- Use `PRAGMA optimize` (since 3.32.0) to run ANALYZE and optimize the query planner
- Use `VACUUM` to reclaim space after large deletes; or enable `PRAGMA auto_vacuum=INCREMENTAL`

### Common Patterns

```sql
-- Auto-incrementing primary key
CREATE TABLE t(id INTEGER PRIMARY KEY, ...);
-- Insert NULL or omit to auto-assign

-- UPSERT (insert or update on conflict)
INSERT INTO t(id, val) VALUES(1, 'x')
  ON CONFLICT(id) DO UPDATE SET val=excluded.val;

-- JSON extraction
SELECT json_extract(data, '$.name') FROM t;
SELECT data->>'$.name' FROM t;  -- shorthand

-- Date/time
SELECT date('now');
SELECT datetime(unixepoch(), 'unixepoch', 'localtime');
SELECT julianday('now') - julianday('2024-01-01');  -- days between

-- Window functions
SELECT name, salary,
  rank() OVER (ORDER BY salary DESC) as rk
FROM employees;

-- CTEs
WITH RECURSIVE cte(n) AS (
  VALUES(1) UNION ALL SELECT n+1 FROM cte WHERE n<10
) SELECT * FROM cte;
```

## Gotchas

- **Foreign keys are OFF by default** — run `PRAGMA foreign_keys=ON` on each connection. There is no compile-time default-ON in most builds.
- **Dynamic typing** — inserting a string into an INTEGER column stores the string (after trying to convert). Use `STRICT` tables for rigid enforcement.
- **No BOOLEAN type** — use INTEGER (0/1). `TRUE`/`FALSE` keywords are aliases for 1/0 since 3.23.0.
- **No DATETIME type** — store dates as TEXT (ISO-8601), INTEGER (Unix epoch), or REAL (Julian day). Use built-in date/time functions for manipulation.
- **`INTEGER PRIMARY KEY` is an alias for ROWID** — it auto-assigns even without AUTOINCREMENT. `AUTOINCREMENT` adds extra overhead preventing reuse of deleted rowids; rarely needed.
- **VARCHAR(N) has no length limit** — SQLite does not enforce the N. A VARCHAR(50) accepts strings of any length.
- **`GROUP BY` without aggregates acts as `DISTINCT ON`** — SQLite allows non-aggregate, non-GROUP-BY columns in result sets (returns arbitrary row values).
- **`1='1'` is FALSE** — SQLite distinguishes integer and text literals. Use `CAST` or rely on affinity for implicit conversion.
- **Double-quoted strings** — SQLite accepts `"text"` as a string literal (MySQL legacy). This is deprecated and disabled by default in CLI since 3.41.0. Use single quotes.
- **`LIKE` is ASCII-only** — full Unicode case folding requires ICU extension.
- **Division by zero returns NULL** — not an error.
- **NUL characters allowed in TEXT** — `length()` stops at first NUL; use `octet_length()` for byte count.
- **`sqlite3_prepare()` vs `sqlite3_prepare_v2()`** — always use `_v2` which auto-recompiles on schema changes.
- **Comma-joins have wrong precedence** — `FROM a, b RIGHT JOIN c, d` parses differently than standard SQL. Use parentheses.
- **`PRAGMA journal_mode=WAL` is persistent** — once set, it stays across connections. Cannot be changed during an active transaction.
- **WAL files left behind** — checkpoint with `PRAGMA wal_checkpoint(TRUNCATE)` to clean up.
- **Not for high-write-concurrency** — only one writer at a time. Writers queue. For heavy concurrent writes, consider a client/server RDBMS.
- **Not for network filesystems** — file locking is unreliable on NFS. Do not put SQLite databases on NFS with multiple writers.

## References

- [01-sql-syntax](references/01-sql-syntax.md) — SQL statement reference (CREATE, SELECT, INSERT, UPDATE, DELETE, ALTER, transactions, CTEs, UPSERT, RETURNING)
- [02-datatypes](references/02-datatypes.md) — Storage classes, type affinity, STRICT tables, collating sequences, comparison rules
- [03-scalar-functions](references/03-scalar-functions.md) — Built-in scalar SQL functions (abs, coalesce, ifnull, substr, typeof, hex, random, quote, printf, and more)
- [04-aggregate-functions](references/04-aggregate-functions.md) — Aggregate functions (count, sum, avg, min, max, group_concat, median, percentile)
- [05-window-functions](references/05-window-functions.md) — Window functions (row_number, rank, dense_rank, lag, lead, first_value, last_value, ntile)
- [06-math-functions](references/06-math-functions.md) — Math functions (sin, cos, sqrt, log, exp, pi, pow, trunc, ceil, floor) — requires SQLITE_ENABLE_MATH_FUNCTIONS
- [07-date-time-functions](references/07-date-time-functions.md) — Date/time functions (date, time, datetime, julianday, unixepoch, strftime, timediff)
- [08-json-functions](references/08-json-functions.md) — JSON functions and operators (json_extract, json_object, json_array, ->, ->>, JSONB, json_tree)
- [09-pragmas](references/09-pragmas.md) — PRAGMA commands (journal_mode, foreign_keys, synchronous, cache_size, integrity_check, and more)
- [10-c-api](references/10-c-api.md) — C/C++ interface (sqlite3_open, sqlite3_prepare_v2, sqlite3_step, sqlite3_column, sqlite3_bind, error handling)
- [11-virtual-tables](references/11-virtual-tables.md) — Virtual tables, FTS5 full-text search, R-Tree spatial index, table-valued functions
- [12-advanced-features](references/12-advanced-features.md) — WAL journaling, savepoints, recursive triggers, generated columns, UPSERT, WITHOUT ROWID, compile options
- [13-cli](references/13-cli.md) — sqlite3 command-line interface, dot-commands, import/export, modes
- [14-limits](references/14-limits.md) — SQLite limits (max DB size, string length, columns, SQL statement length, etc.)
- [15-performance](references/15-performance.md) — Performance tuning, indexing strategies, query planner, EXPLAIN, EXPLAIN QUERY PLAN

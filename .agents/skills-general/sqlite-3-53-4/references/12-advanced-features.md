# Advanced Features

## Table of Contents

- [WAL Journaling](#wal-journaling)
- [Savepoints](#savepoints)
- [Recursive Triggers](#recursive-triggers)
- [Generated Columns](#generated-columns)
- [UPSERT](#upsert)
- [WITHOUT ROWID Tables](#without-rowid-tables)
- [Partial Indexes](#partial-indexes)
- [Expression Indexes](#expression-indexes)
- [Common Table Expressions](#common-table-expressions)
- [RETURNING Clause](#returning-clause)
- [Compile-Time Options](#compile-time-options)
- [URI Filenames](#uri-filenames)
- [Incremental BLOB I/O](#incremental-blob-io)
- [Session Extension](#session-extension)

## WAL Journaling

Write-Ahead Logging (WAL) provides better concurrency than rollback journals:

```sql
PRAGMA journal_mode = WAL;
```

Benefits:
- Readers and writers can operate concurrently
- No reader blocking during writes
- Often faster for mixed read/write workloads

Trade-offs:
- WAL file persists until checkpointed
- Slightly more disk space used
- Not suitable for network filesystems

Checkpoints:
```sql
PRAGMA wal_checkpoint(PASSIVE);   -- Don't block writers
PRAGMA wal_checkpoint(FULL);      -- Wait for all readers to finish
PRAGMA wal_checkpoint(TRUNCATE);  -- Checkpoint and delete WAL file
```

Auto-checkpoint: `PRAGMA wal_autocheckpoint = 1000;` (default: 1000 pages)

## Savepoints

Nested transaction control within a transaction:

```sql
BEGIN TRANSACTION;
INSERT INTO t VALUES(1);

SAVEPOINT sp1;
INSERT INTO t VALUES(2);
ROLLBACK TO sp1;  -- Undoes the INSERT of 2, keeps INSERT of 1

SAVEPOINT sp2;
INSERT INTO t VALUES(3);
RELEASE sp2;      -- Commits the INSERT of 3

COMMIT;           -- Commits everything
```

## Recursive Triggers

Enabled per-connection:

```sql
PRAGMA recursive_triggers = ON;

CREATE TRIGGER cascade_delete AFTER DELETE ON categories
BEGIN
  DELETE FROM categories WHERE parent_id = old.id;
END;
```

Default: OFF. Recursive triggers allow triggers to fire other triggers.

## Generated Columns

Computed automatically from other columns:

```sql
CREATE TABLE t(
  width REAL,
  height REAL,
  area REAL GENERATED ALWAYS AS (width * height) STORED
);

-- VIRTUAL (computed on read, not stored)
CREATE TABLE t2(
  first_name TEXT,
  last_name TEXT,
  full_name TEXT GENERATED ALWAYS AS (first_name || ' ' || last_name) VIRTUAL
);
```

- `STORED` — computed on write, stored on disk
- `VIRTUAL` — computed on read, not stored

## UPSERT

Insert-or-update on conflict (since 3.24.0):

```sql
INSERT INTO users(id, name, email)
VALUES (1, 'Alice', 'alice@new.com')
ON CONFLICT(id) DO UPDATE SET
  name = excluded.name,
  email = excluded.email,
  updated_at = datetime('now');

-- Do nothing on conflict
INSERT INTO users(id, name) VALUES (1, 'Alice')
ON CONFLICT(id) DO NOTHING;

-- Conditional upsert
INSERT INTO users(id, name) VALUES (1, 'Alice')
ON CONFLICT(id) DO UPDATE SET name = excluded.name
WHERE excluded.name IS NOT NULL;
```

`excluded.*` references the values that would have been inserted.

## WITHOUT ROWID Tables

Store data as a b-tree keyed on PRIMARY KEY (no implicit rowid):

```sql
CREATE TABLE t(
  key1 TEXT,
  key2 INTEGER,
  data TEXT,
  PRIMARY KEY(key1, key2)
) WITHOUT ROWID;
```

Benefits:
- Can be more compact for composite primary keys
- Can be faster for lookups by primary key

Trade-offs:
- PRIMARY KEY must be unique and non-NULL
- Cannot use `INTEGER PRIMARY KEY` (it IS the rowid)

## Partial Indexes

Index only a subset of rows (since 3.8.0):

```sql
CREATE INDEX idx_active_users ON users(email)
WHERE status = 'active';

CREATE INDEX idx_recent ON events(timestamp)
WHERE timestamp > datetime('now', '-30 days');
```

Smaller than full indexes, faster for filtered queries.

## Expression Indexes

Index on computed expressions (since 3.9.0):

```sql
CREATE INDEX idx_lower_name ON users(LOWER(name));
CREATE INDEX idx_email_domain ON users(SUBSTR(email, INSTR(email, '@') + 1));
```

Query must use the same expression to use the index:
```sql
SELECT * FROM users WHERE LOWER(name) = 'alice';  -- Uses index
```

## Common Table Expressions

```sql
-- Non-recursive
WITH dept_avg AS (
  SELECT dept, AVG(salary) AS avg_sal
  FROM employees GROUP BY dept
)
SELECT e.name, e.salary, d.avg_sal
FROM employees e JOIN dept_avg d ON e.dept = d.dept
WHERE e.salary > d.avg_sal;

-- Recursive (hierarchical data)
WITH RECURSIVE ancestors(id, parent, depth) AS (
  SELECT id, parent, 0 FROM nodes WHERE id = 5
  UNION ALL
  SELECT n.id, n.parent, a.depth + 1
  FROM nodes n JOIN ancestors a ON n.id = a.parent
)
SELECT * FROM ancestors;
```

## RETURNING Clause

Return data from modified rows (since 3.35.0):

```sql
INSERT INTO users(name, email) VALUES ('Alice', 'a@b.com')
RETURNING id, name;

UPDATE users SET status = 'active' WHERE id = 1
RETURNING id, name, status;

DELETE FROM users WHERE inactive = 1
RETURNING id, name;
```

## Compile-Time Options

Key options that affect behavior:

| Option | Description |
|---|---|
| `SQLITE_ENABLE_MATH_FUNCTIONS` | Enable math functions |
| `SQLITE_ENABLE_FTS5` | Enable FTS5 (built-in by default) |
| `SQLITE_ENABLE_JSON1` | Enable JSON functions (built-in by default since 3.38.0) |
| `SQLITE_ENABLE_RBU` | Enable RBU (ripple-update) extension |
| `SQLITE_ENABLE_COLUMN_METADATA` | Enable column metadata APIs |
| `SQLITE_DEFAULT_JOURNAL_SIZE_LIMIT` | Default journal size limit |
| `SQLITE_DEFAULT_CACHE_SIZE` | Default page cache size |
| `SQLITE_DEFAULT_FOREIGN_KEYS=1` | Enable FK enforcement by default |
| `SQLITE_DQS=0` | Disable double-quoted string literals |
| `SQLITE_THREADSAFE=1` | Enable mutex-based thread safety |
| `SQLITE_OMIT_*` | Omit features to reduce size |

Check at runtime:
```sql
PRAGMA compile_options;
SELECT sqlite_compileoption_used('ENABLE_MATH_FUNCTIONS');
```

## URI Filenames

Enable URI interpretation:

```c
sqlite3_open_v2("file:mydb.db?mode=rw&cache=shared", &db,
    SQLITE_OPEN_URI | SQLITE_OPEN_READWRITE, NULL);
```

Query parameters:
- `mode=ro|rw|rwgc` — read-only, read-write, read-write with create
- `cache=shared|private` — shared cache mode
- `journal_size=N` — journal size limit
- `immutable=1` — database is immutable

## Incremental BLOB I/O

Read/write BLOBs in chunks without loading entire value:

```c
sqlite3_blob *blob;
sqlite3_blob_open(db, "main", "table", "column", rowid, flags, &blob);
int n = sqlite3_blob_bytes(blob);
char buf[1024];
sqlite3_blob_read(blob, buf, sizeof(buf), offset);
sqlite3_blob_write(blob, buf, sizeof(buf), offset);
sqlite3_blob_close(blob);
```

## Session Extension

Track changes to the database:

```c
sqlite3_session *pSession;
sqlite3_session_create(db, "main", &pSession);
sqlite3_session_changeset(pSession, &nSize, &pChangeset);
// Apply changeset to another database
sqlite3_changeset_apply(dbTarget, nSize, pChangeset, ...);
```

Useful for synchronization, undo/redo, and change tracking.

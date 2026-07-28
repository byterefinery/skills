# SQL Syntax Reference

## Table of Contents

- [CREATE TABLE](#create-table)
- [CREATE INDEX](#create-index)
- [CREATE VIEW](#create-view)
- [CREATE TRIGGER](#create-trigger)
- [CREATE VIRTUAL TABLE](#create-virtual-table)
- [SELECT](#select)
- [INSERT](#insert)
- [UPDATE](#update)
- [DELETE](#delete)
- [UPSERT](#upsert)
- [RETURNING Clause](#returning-clause)
- [ALTER TABLE](#alter-table)
- [DROP](#drop)
- [Transactions](#transactions)
- [Savepoints](#savepoints)
- [WITH (CTEs)](#with-ctes)
- [REPLACE](#replace)
- [EXPLAIN](#explain)
- [PRAGMA](#pragma)

## CREATE TABLE

```sql
CREATE [TEMP | TEMPORARY] TABLE [IF NOT EXISTS] [schema.]table-name
  (column-def [, column-def ...] [, table-constraint ...])
  [WITHOUT ROWID] [STRICT];
```

Column definition:
```sql
column-name [type-name] [COLLATE collation]
  [CONSTRAINT name]
  [NOT NULL | NULL]
  [CHECK(expr)]
  [DEFAULT default-value]
  [PRIMARY KEY [ASC | DESC] [UNIQUE]]
  [REFERENCES table [(columns)] [ON DELETE|UPDATE action]]
  [GENERATED ALWAYS AS (expr) [STORED | VIRTUAL]]
```

Key points:
- `INTEGER PRIMARY KEY` is an alias for the ROWID — auto-assigns on NULL insert
- `AUTOINCREMENT` prevents reuse of deleted rowids (extra overhead, rarely needed)
- `STRICT` enforces rigid type checking — only INT, INTEGER, REAL, TEXT, BLOB, ANY allowed
- `WITHOUT ROWID` stores data as a b-tree keyed on PRIMARY KEY (useful for composite keys)
- Generated columns compute values automatically from other columns
- Column types are advisory (affinity) unless table is `STRICT`

```sql
-- Standard table with affinity
CREATE TABLE users(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  age INT CHECK(age >= 0),
  created_at TEXT DEFAULT (datetime('now'))
);

-- STRICT table with rigid types
CREATE TABLE strict_data(
  id INT PRIMARY KEY,
  label TEXT NOT NULL,
  value REAL,
  blob_data BLOB,
  anything ANY
) STRICT;

-- WITHOUT ROWID table (composite primary key)
CREATE TABLE matrix(
  row_id INT,
  col_id INT,
  value REAL,
  PRIMARY KEY(row_id, col_id)
) WITHOUT ROWID;
```

## CREATE INDEX

```sql
CREATE [UNIQUE] [TEMP | TEMPORARY] INDEX [IF NOT EXISTS] [schema.]index-name
  ON [schema.]table-name (key [, key ...])
  [WHERE expr];
```

Key expressions support:
```sql
-- Standard column index
CREATE INDEX idx_users_email ON users(email);

-- Expression index (since 3.9.0)
CREATE INDEX idx_lower_name ON users(LOWER(name));

-- Partial index (since 3.8.0)
CREATE INDEX idx_active ON users(status) WHERE status = 'active';

-- Descending index
CREATE INDEX idx_created ON users(created_at DESC);
```

## CREATE VIEW

```sql
CREATE [TEMP | TEMPORARY] VIEW [IF NOT EXISTS] [schema.]view-name
  [(column-names)] AS select-stmt;
```

Views are read-only unless they have `INSTEAD OF` triggers.

## CREATE TRIGGER

```sql
CREATE [TEMP | TEMPORARY] TRIGGER [IF NOT EXISTS] [schema.]trigger-name
  [BEFORE | AFTER | INSTEAD OF]
  [INSERT | UPDATE | DELETE | UPDATE OF column-list]
  ON [schema.]table-name
  [FOR EACH ROW] [WHEN condition]
  BEGIN
    trigger-stmt;
    ...
  END;
```

- `NEW.column` and `OLD.column` reference column values
- `INSTEAD OF` triggers allow writes to views
- Recursive triggers enabled via `PRAGMA recursive_triggers=ON`

## CREATE VIRTUAL TABLE

```sql
CREATE VIRTUAL TABLE [IF NOT EXISTS] [schema.]table-name
  USING module-name (module-args);
```

Built-in modules: `fts5` (full-text search), `rtree` (spatial index), `dbstat`.

## SELECT

```sql
WITH [RECURSIVE] cte-name AS (select-stmt) [, ...]
SELECT [DISTINCT | ALL] result-columns
  FROM table-references [JOIN table-references ON expr ...]
  [WHERE expr]
  [GROUP BY expr [, expr ...] [HAVING expr]]
  [WINDOW window-name AS (window-def)]
  [ORDER BY expr [ASC | DESC] [NULLS FIRST | NULLS LAST] [, ...]]
  [LIMIT count [OFFSET count]]
  [UNION | INTERSECT | EXCEPT] select-stmt;
```

Key features:
- `LIMIT -1` means no limit
- `OFFSET` can be specified as `LIMIT count, offset` (MySQL-compatible)
- `GROUP BY` without aggregates acts as `DISTINCT ON`
- `FILTER (WHERE expr)` clause on aggregates filters rows before aggregation
- `NULLS FIRST/LAST` control NULL ordering in ORDER BY

```sql
-- Basic query
SELECT name, email FROM users WHERE age > 25 ORDER BY name LIMIT 10;

-- Aggregate with FILTER
SELECT
  COUNT(*) FILTER (WHERE status='active') AS active_count,
  AVG(score) FILTER (WHERE score > 0) AS avg_score
FROM users;

-- Window function
SELECT name, dept, salary,
  RANK() OVER (PARTITION BY dept ORDER BY salary DESC) as dept_rank
FROM employees;

-- CTE
WITH dept_stats AS (
  SELECT dept, AVG(salary) AS avg_sal FROM employees GROUP BY dept
)
SELECT e.name, e.salary, d.avg_sal
FROM employees e JOIN dept_stats d ON e.dept = d.dept;

-- Recursive CTE
WITH RECURSIVE nums(n) AS (
  VALUES(1) UNION ALL SELECT n+1 FROM nums WHERE n < 100
)
SELECT SUM(n) FROM nums;
```

## INSERT

```sql
INSERT [OR conflict-algorithm] INTO [schema.]table-name [(columns)]
  VALUES (values) [, (values) ...]
  [ON CONFLICT(target) DO UPDATE SET assignments | DO NOTHING]
  [RETURNING expr];

INSERT [OR conflict-algorithm] INTO [schema.]table-name [(columns)]
  SELECT ...
  [ON CONFLICT(target) DO UPDATE SET assignments | DO NOTHING]
  [RETURNING expr];
```

Conflict algorithms: `ROLLBACK`, `ABORT` (default), `FAIL`, `IGNORE`, `REPLACE`.

```sql
-- Simple insert
INSERT INTO users(name, email) VALUES('Alice', 'alice@example.com');

-- Multi-row insert
INSERT INTO users(name, email) VALUES
  ('Alice', 'alice@example.com'),
  ('Bob', 'bob@example.com');

-- Insert from query
INSERT INTO archive SELECT * FROM users WHERE inactive = 1;

-- UPSERT
INSERT INTO users(id, name, email) VALUES(1, 'Alice', 'new@email.com')
  ON CONFLICT(id) DO UPDATE SET name=excluded.name, email=excluded.email;

INSERT OR IGNORE INTO users(id, name) VALUES(1, 'Alice');
```

## UPDATE

```sql
UPDATE [OR conflict-algorithm] [schema.]table-name
  SET assignments
  [WHERE expr]
  [RETURNING expr];
```

```sql
UPDATE users SET email='new@example.com' WHERE id=1;
UPDATE users SET age=age+1 WHERE created_at < '2020-01-01';
```

## DELETE

```sql
DELETE [OR conflict-algorithm] FROM [schema.]table-name
  [WHERE expr]
  [RETURNING expr];
```

## UPSERT

SQLite supports UPSERT via `ON CONFLICT` clause (since 3.24.0):

```sql
INSERT INTO t(id, val) VALUES(1, 'x')
  ON CONFLICT(id) DO UPDATE SET val=excluded.val;

INSERT INTO t(id, val) VALUES(1, 'x')
  ON CONFLICT(id) DO NOTHING;

-- With WHERE on conflict
INSERT INTO t(id, val) VALUES(1, 'x')
  ON CONFLICT(id) WHERE val IS NOT NULL DO UPDATE SET val=excluded.val;
```

`excluded.*` references the values that would have been inserted.

## RETURNING Clause

Returns data from modified rows (since 3.35.0):

```sql
INSERT INTO users(name) VALUES('Alice') RETURNING id, name;
UPDATE users SET age=30 WHERE id=1 RETURNING id, name, age;
DELETE FROM users WHERE id=1 RETURNING id, name;
```

## ALTER TABLE

Limited support:

```sql
-- Rename table
ALTER TABLE old_name RENAME TO new_name;

-- Rename column (since 3.25.0)
ALTER TABLE t RENAME COLUMN old_col TO new_col;

-- Add column (since 3.30.0)
ALTER TABLE t ADD COLUMN new_col TEXT DEFAULT 'x';

-- Drop column (since 3.35.0)
ALTER TABLE t DROP COLUMN col_name;
```

For complex schema changes, recreate the table:
1. BEGIN TRANSACTION
2. Create new table with desired schema
3. COPY data from old to new
4. DROP old table
5. RENAME new table
6. Recreate indices/triggers
7. COMMIT

## DROP

```sql
DROP TABLE [IF EXISTS] [schema.]table-name;
DROP INDEX [IF EXISTS] [schema.]index-name;
DROP VIEW [IF EXISTS] [schema.]view-name;
DROP TRIGGER [IF EXISTS] [schema.]trigger-name;
```

## Transactions

```sql
BEGIN [DEFERRED | IMMEDIATE | EXCLUSIVE] [TRANSACTION [name]];
COMMIT [TRANSACTION [name]];
ROLLBACK [TRANSACTION [name] [TO SAVEPOINT name]];
```

- `DEFERRED` (default) — no locks until first operation
- `IMMEDIATE` — acquire RESERVED lock immediately
- `EXCLUSIVE` — acquire EXCLUSIVE lock immediately

## Savepoints

```sql
SAVEPOINT name;
RELEASE SAVEPOINT name;
ROLLBACK TO SAVEPOINT name;
```

Nested within transactions for partial rollback.

## WITH (CTEs)

```sql
-- Non-recursive
WITH dept_avg AS (
  SELECT dept, AVG(salary) AS avg_sal FROM emp GROUP BY dept
)
SELECT e.name, e.salary, d.avg_sal
FROM emp e JOIN dept_avg d ON e.dept = d.dept;

-- Recursive
WITH RECURSIVE hierarchy(id, parent, depth) AS (
  SELECT id, parent, 0 FROM nodes WHERE parent IS NULL
  UNION ALL
  SELECT n.id, n.parent, h.depth+1
  FROM nodes n JOIN hierarchy h ON n.parent = h.id
)
SELECT * FROM hierarchy;
```

## REPLACE

`REPLACE` is equivalent to `INSERT OR REPLACE` — deletes conflicting rows before inserting.

## EXPLAIN

```sql
EXPLAIN SELECT ...;          -- VDBE bytecode
EXPLAIN QUERY PLAN SELECT ...; -- human-readable plan
```

Use `EXPLAIN QUERY PLAN` to verify index usage:
```sql
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email='x@y.com';
-- SCAN TABLE users USING INDEX idx_users_email
```

## PRAGMA

SQLite-specific commands for configuration and introspection. See [09-pragmas](09-pragmas.md) for full reference.

# Datatypes in SQLite

## Table of Contents

- [Storage Classes](#storage-classes)
- [Type Affinity](#type-affinity)
- [STRICT Tables](#strict-tables)
- [Collating Sequences](#collating-sequences)
- [Comparison Rules](#comparison-rules)
- [Boolean Values](#boolean-values)
- [Date/Time Storage](#datetime-storage)

## Storage Classes

Every value in SQLite has one of five storage classes:

| Storage Class | Description |
|---|---|
| `NULL` | The value is a NULL |
| `INTEGER` | Signed integer, 0-8 bytes depending on magnitude |
| `REAL` | 8-byte IEEE floating point number |
| `TEXT` | Text string in database encoding (UTF-8, UTF-16BE, UTF-16LE) |
| `BLOB` | Blob of data, stored exactly as input |

Key points:
- Type belongs to the **value**, not the column (dynamic typing)
- Any column (except `INTEGER PRIMARY KEY`) can store any storage class
- `INTEGER PRIMARY KEY` can only hold 64-bit signed integers
- `typeof(X)` returns the storage class name as text

```sql
SELECT typeof(NULL);          -- 'null'
SELECT typeof(123);           -- 'integer'
SELECT typeof(3.14);          -- 'real'
SELECT typeof('hello');       -- 'text'
SELECT typeof(X'DEAD');       -- 'blob'
```

## Type Affinity

Columns have a recommended type (affinity), not a required type. Affinity determines how SQLite tries to convert values on insert:

| Affinity | Behavior |
|---|---|
| `TEXT` | Stores NULL, TEXT, or BLOB. Converts numbers to text. |
| `NUMERIC` | Tries to convert text to INTEGER, then REAL. Stores as-is if not convertible. |
| `INTEGER` | Same as NUMERIC, except `CAST(x AS INT)` returns integer for exact values. |
| `REAL` | Like NUMERIC but forces integers to floating point. |
| `BLOB` | No conversion. Stores exactly as received. |

### Determining Affinity from Type Name

Rules applied in order (first match wins):

1. Type contains "INT" → INTEGER affinity
2. Type contains "CHAR", "CLOB", or "TEXT" → TEXT affinity
3. Type contains "BLOB" or no type specified → BLOB affinity
4. Type contains "REAL", "FLOA", or "DOUB" → REAL affinity
5. Otherwise → NUMERIC affinity

### Common Type Name Examples

| Declared Type | Affinity | Rule |
|---|---|---|
| INT, INTEGER, TINYINT, SMALLINT, BIGINT, INT2, INT8 | INTEGER | 1 |
| CHARACTER, VARCHAR, NVARCHAR, TEXT, CLOB | TEXT | 2 |
| BLOB, (no type) | BLOB | 3 |
| REAL, DOUBLE, FLOAT | REAL | 4 |
| NUMERIC, DECIMAL, BOOLEAN, DATE, DATETIME | NUMERIC | 5 |

Note: `VARCHAR(255)` — the length is ignored. SQLite does not enforce string length limits.

### Affinity Behavior Example

```sql
CREATE TABLE t(
  t TEXT,      -- text affinity
  nu NUMERIC,  -- numeric affinity
  i INTEGER,   -- integer affinity
  r REAL,      -- real affinity
  b BLOB       -- blob affinity (no conversion)
);

INSERT INTO t VALUES('500', '500', '500', '500', '500');
SELECT typeof(t), typeof(nu), typeof(i), typeof(r), typeof(b) FROM t;
-- text | integer | integer | real | text
```

## STRICT Tables

Since version 3.37.0, SQLite supports rigid type enforcement per table:

```sql
CREATE TABLE strict_t(
  id INT PRIMARY KEY,
  name TEXT NOT NULL,
  price REAL,
  data BLOB,
  mixed ANY
) STRICT;
```

Rules for STRICT tables:
1. Every column must specify a datatype
2. Only these types allowed: `INT`, `INTEGER`, `REAL`, `TEXT`, `BLOB`, `ANY`
3. Values must match the declared type (NULL allowed unless NOT NULL)
4. SQLite tries to coerce; raises `SQLITE_CONSTRAINT_DATATYPE` if it cannot
5. `ANY` accepts any type with no coercion
6. PRIMARY KEY columns are implicitly NOT NULL

The `ANY` type preserves values exactly as inserted (no affinity conversion).

## Collating Sequences

Built-in collations:

| Collation | Description |
|---|---|
| `BINARY` | Byte-by-byte comparison using `memcmp()` (default) |
| `NOCASE` | Case-insensitive for ASCII characters only |
| `RTRIM` | Like BINARY but ignores trailing spaces |

Assign collation to columns or expressions:

```sql
CREATE TABLE t(
  name TEXT COLLATE NOCASE,
  code TEXT COLLATE RTRIM
);

-- Override in queries
SELECT * FROM t WHERE name = 'alice' COLLATE NOCASE;
SELECT * FROM t ORDER BY name COLLATE BINARY;
```

Custom collations registered via `sqlite3_create_collation()` C API.

## Comparison Rules

### Sort Order (cross-type)

1. `NULL` < everything (including other NULLs)
2. `INTEGER` / `REAL` < `TEXT` / `BLOB` (numeric comparison within)
3. `TEXT` < `BLOB` (collation-based comparison)
4. `BLOB` (memcmp comparison)

### Type Conversion in Comparisons

Affinity is applied to operands before comparison:

- If one operand has INTEGER/REAL/NUMERIC affinity and the other has TEXT/BLOB/no affinity → NUMERIC affinity applied to the other
- If one operand has TEXT affinity and the other has no affinity → TEXT affinity applied to the other
- Otherwise, no conversion

```sql
-- '500' (TEXT) compared to 40 (INTEGER)
-- TEXT affinity applied: 40 → '40', then text comparison
-- '500' > '40' → true (lexicographic)

-- 500 (INTEGER) compared to '40' (TEXT)
-- NUMERIC affinity applied: '40' → 40, then numeric comparison
-- 500 > 40 → true
```

## Boolean Values

SQLite has no separate BOOLEAN storage class. Booleans are stored as integers:
- `TRUE` = 1
- `FALSE` = 0

Since 3.23.0, `TRUE` and `FALSE` are recognized as keywords (aliases for 1 and 0). In WHERE clauses, any non-zero, non-NULL value is "true".

## Date/Time Storage

SQLite has no dedicated DATE/DATETIME type. Store dates as:

| Format | Storage Class | Example |
|---|---|---|
| TEXT (ISO-8601) | TEXT | `'2024-01-15 10:30:00'` |
| Julian Day Number | REAL | `2460310.5` |
| Unix Timestamp | INTEGER | `1705312200` |

Use built-in date/time functions for manipulation and conversion. See [07-date-time-functions](07-date-time-functions.md).

Recommended: store as TEXT in ISO-8601 format (`YYYY-MM-DD HH:MM:SS`) for readability and index efficiency.

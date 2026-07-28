# JSON Functions

## Table of Contents

- [Overview](#overview)
- [JSON vs JSONB](#json-vs-jsonb)
- [PATH Syntax](#path-syntax)
- [Core Functions](#core-functions)
- [Construction Functions](#construction-functions)
- [Modification Functions](#modification-functions)
- [Operators](#operators)
- [Aggregate Functions](#aggregate-functions)
- [Table-Valued Functions](#table-valued-functions)
- [Examples](#examples)

## Overview

SQLite includes 28+ JSON scalar functions, 4 aggregate functions, 2 operators, and 4 table-valued functions. Built-in by default since 3.38.0 (opt-out with `-DSQLITE_OMIT_JSON`).

JSON is stored as ordinary TEXT. JSONB (binary format) available since 3.45.0 for faster processing.

## JSON vs JSONB

| Aspect | `json_*` | `jsonb_*` |
|---|---|---|
| Returns | TEXT (RFC 8259) | BLOB (binary JSONB) |
| Speed | Standard | Faster (no parse overhead) |
| Size | Standard | Slightly smaller on disk |

Use `jsonb_*` variants for chained operations (faster). Use `json_*` for final output or aggregates.

## PATH Syntax

JSON paths start with `$` followed by object keys (`.`label`) or array indices (`[N]`):

| Path | Meaning |
|---|---|
| `$` | Root element |
| `$.name` | Object key "name" |
| `$[0]` | First array element |
| `$.items[2].price` | Nested access |
| `$[#-1]` | Last array element |
| `$[#]` | Position after last element (for appending) |

## Core Functions

| Function | Description |
|---|---|
| `json(X)` | Validate and minify JSON |
| `jsonb(X)` | Convert to JSONB binary format |
| `json_valid(X)` / `json_valid(X, flags)` | Check if valid JSON |
| `json_type(X)` / `json_type(X, path)` | Return type: 'null', 'true', 'false', 'integer', 'real', 'text', 'array', 'object' |
| `json_quote(X)` | Convert SQL value to JSON representation |
| `json_error_position(X)` | Position of first syntax error (0 if valid) |
| `json_pretty(X)` | Pretty-print JSON with indentation |
| `json_array_length(X)` / `json_array_length(X, path)` | Number of elements in array |

## Construction Functions

| Function | Description |
|---|---|
| `json_array(v1, v2, ...)` | Build JSON array |
| `jsonb_array(v1, v2, ...)` | Build JSON array as JSONB |
| `json_object(k1, v1, k2, v2, ...)` | Build JSON object |
| `jsonb_object(k1, v1, k2, v2, ...)` | Build JSON object as JSONB |

```sql
SELECT json_array(1, 2, 'three', NULL);
-- '[1,2,"three",null]'

SELECT json_object('name', 'Alice', 'age', 30);
-- '{"name":"Alice","age":30}'
```

Note: TEXT values are quoted as JSON strings. To embed raw JSON, use `json()` or another JSON function as the value.

## Modification Functions

### Extraction

| Function | Description |
|---|---|
| `json_extract(X, path, ...)` | Extract value(s) from JSON |
| `jsonb_extract(X, path, ...)` | Same, returns JSONB for objects/arrays |

Single path: returns unquoted value (SQL type). Multiple paths: returns JSON array.

### Insertion/Replacement

| Function | Create if missing? | Overwrite if exists? |
|---|---|---|
| `json_insert(X, path, val, ...)` | Yes | No |
| `json_replace(X, path, val, ...)` | No | Yes |
| `json_set(X, path, val, ...)` | Yes | Yes |

Each has a `jsonb_*` variant.

### Removal

```sql
json_remove(X, path, ...)    -- Remove elements at paths
jsonb_remove(X, path, ...)
```

### Patching

```sql
json_patch(T, P)    -- RFC-7396 MergePatch
jsonb_patch(T, P)
```

## Operators

Since 3.38.0:

| Operator | Description |
|---|---|
| `json -> path` | Extract as JSON text |
| `json ->> path` | Extract as SQL value (unquoted) |

```sql
SELECT '{"a":2,"b":"x"}' -> '$.a';    -- '2'
SELECT '{"a":2,"b":"x"}' ->> '$.a';   -- 2 (integer)
SELECT '{"a":2}' -> 'a';              -- '2' (PostgreSQL shorthand)
```

## Aggregate Functions

| Function | Description |
|---|---|
| `json_group_array(X)` | Aggregate values into JSON array |
| `jsonb_group_array(X)` | Same, returns JSONB |
| `json_group_object(key, val)` | Aggregate key-value pairs into JSON object |
| `jsonb_group_object(key, val)` | Same, returns JSONB |

```sql
SELECT dept, json_group_array(name) AS members
FROM employees GROUP BY dept;

SELECT json_group_object(name, salary) FROM employees;
```

## Table-Valued Functions

| Function | Description |
|---|---|
| `json_each(X)` / `json_each(X, path)` | Iterate top-level elements |
| `jsonb_each(X)` / `jsonb_each(X, path)` | Same, value column returns JSONB |
| `json_tree(X)` / `json_tree(X, path)` | Recursively iterate all elements |
| `jsonb_tree(X)` / `jsonb_tree(X, path)` | Same, value column returns JSONB |

Columns returned: `key`, `value`, `type`, `atom`, `id`, `parent`, `fullkey`, `path`.

```sql
SELECT key, value, type FROM json_each('[1,2,3]');
-- key=0, value=1, type=integer
-- key=1, value=2, type=integer
-- key=2, value=3, type=integer

SELECT * FROM json_tree('{"a":{"b":1}}');
-- Recursively walks the entire structure
```

## Examples

```sql
-- Extract nested values
SELECT json_extract(data, '$.user.name') FROM t;
SELECT data->>'$.user.name' FROM t;

-- Build JSON from query
SELECT json_object(
  'id', id,
  'name', name,
  'scores', json_group_array(score)
) FROM grades GROUP BY id;

-- Modify JSON
SELECT json_set(config, '$.theme', 'dark', '$.lang', 'en') FROM settings;
SELECT json_remove(config, '$.deprecated') FROM settings;

-- Array operations
SELECT json_insert('[1,2,3]', '$[#]', 4);     -- '[1,2,3,4]' (append)
SELECT json_array_insert('[1,2,3]', '$[1]', 'x'); -- '[1,"x",2,3]' (insert at index)

-- Parse JSON into rows
SELECT t.key, t.value
FROM t, json_each(t.metadata) AS t
WHERE t.key = 'status';
```

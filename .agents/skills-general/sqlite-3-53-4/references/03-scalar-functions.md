# Scalar SQL Functions

## Table of Contents

- [String Functions](#string-functions)
- [Numeric Functions](#numeric-functions)
- [NULL Handling](#null-handling)
- [Type Inspection](#type-inspection)
- [Encoding/Decoding](#encodingdecoding)
- [Formatting](#formatting)
- [Pattern Matching](#pattern-matching)
- [Query Planner Hints](#query-planner-hints)
- [System Functions](#system-functions)

## String Functions

| Function | Description |
|---|---|
| `length(X)` | Number of characters (code points) for TEXT, bytes for BLOB |
| `octet_length(X)` | Number of bytes in the encoding of X |
| `lower(X)` | Convert ASCII characters to lowercase |
| `upper(X)` | Convert ASCII characters to uppercase |
| `ltrim(X)` / `ltrim(X, chars)` | Remove leading spaces or specified characters |
| `rtrim(X)` / `rtrim(X, chars)` | Remove trailing spaces or specified characters |
| `trim(X)` / `trim(X, chars)` | Remove leading and trailing spaces or characters |
| `replace(X, Y, Z)` | Replace all occurrences of Y with Z in X |
| `substr(X, Y)` / `substr(X, Y, Z)` | Substring starting at Y (1-indexed), length Z |
| `substring(X, Y)` / `substring(X, Y, Z)` | Alias for substr() |
| `instr(X, Y)` | Position of first occurrence of Y in X (1-indexed), 0 if not found |
| `like(X, Y)` / `like(X, Y, Z)` | LIKE pattern matching (X is pattern, Y is string) |
| `glob(X, Y)` | GLOB pattern matching (X is pattern, Y is string) |
| `char(X1, X2, ...)` | String from Unicode code points |
| `unicode(X)` | Unicode code point of first character |
| `unistr(X)` | Interpret backslash escapes as Unicode (since 3.50.0) |
| `concat(X, ...)` | Concatenate non-NULL arguments |
| `concat_ws(SEP, X, ...)` | Concatenate with separator |

```sql
SELECT length('hello');              -- 5
SELECT octet_length('café');         -- 5 (UTF-8)
SELECT substr('hello world', 7);     -- 'world'
SELECT substr('hello world', -6);    -- 'world' (count from right)
SELECT instr('hello world', 'world'); -- 7
SELECT replace('a,b,c', ',', ';');   -- 'a;b;c'
SELECT concat_ws('-', 'a', 'b', 'c'); -- 'a-b-c'
```

## Numeric Functions

| Function | Description |
|---|---|
| `abs(X)` | Absolute value |
| `round(X)` / `round(X, D)` | Round to D decimal places (default 0) |
| `sign(X)` | -1, 0, or +1 |
| `random()` | Pseudo-random integer between -2^63 and 2^63-1 |
| `randomblob(N)` | N-byte random BLOB |
| `max(X, Y, ...)` | Maximum of arguments (scalar, not aggregate) |
| `min(X, Y, ...)` | Minimum of arguments (scalar, not aggregate) |
| `changes()` | Rows changed by last INSERT/UPDATE/DELETE |
| `total_changes()` | Total rows changed since connection opened |
| `last_insert_rowid()` | ROWID of last insert |

```sql
SELECT abs(-42);           -- 42
SELECT round(3.14159, 2);  -- 3.14
SELECT sign(-5);           -- -1
SELECT random();           -- random 64-bit integer
SELECT hex(randomblob(16)); -- 32-char hex UUID-like string
```

## NULL Handling

| Function | Description |
|---|---|
| `ifnull(X, Y)` | Return X if not NULL, else Y |
| `coalesce(X, Y, ...)` | Return first non-NULL argument |
| `nullif(X, Y)` | Return X if X≠Y, else NULL |
| `iif(B, V1, V2)` | Inline if: V1 if B is true, else V2 |
| `if(B, V1, V2)` | Alias for iif() |

```sql
SELECT ifnull(NULL, 'default');       -- 'default'
SELECT ifnull('hello', 'default');    -- 'hello'
SELECT coalesce(NULL, NULL, 42);      -- 42
SELECT nullif(5, 5);                  -- NULL
SELECT nullif(5, 3);                  -- 5
SELECT iif(1 > 0, 'yes', 'no');      -- 'yes'
```

## Type Inspection

| Function | Description |
|---|---|
| `typeof(X)` | Returns 'null', 'integer', 'real', 'text', or 'blob' |
| `quote(X)` | SQL literal representation of X |
| `unistr_quote(X)` | Like quote() but escapes control characters |

```sql
SELECT typeof(42);        -- 'integer'
SELECT typeof(3.14);      -- 'real'
SELECT typeof('hello');   -- 'text'
SELECT quote('O''Brien'); -- '''O''Brien'''
```

## Encoding/Decoding

| Function | Description |
|---|---|
| `hex(X)` | Hexadecimal representation of BLOB/text |
| `unhex(X)` / `unhex(X, ignore)` | Decode hex string to BLOB |
| `zeroblob(N)` | N-byte BLOB of zeros (efficient placeholder) |

```sql
SELECT hex('hello');       -- '68656C6C6F'
SELECT unhex('68656C6C6F'); -- 'hello' as BLOB
SELECT zeroblob(1024);      -- 1KB zero BLOB
```

## Formatting

| Function | Description |
|---|---|
| `printf(FORMAT, ...)` | C-style printf formatting |
| `format(FORMAT, ...)` | Alias for printf() |

```sql
SELECT printf('Hello %s, you have %d messages', 'Alice', 5);
-- 'Hello Alice, you have 5 messages'
SELECT printf('Price: %.2f', 19.995);
-- 'Price: 20.00'
```

## Pattern Matching

| Operator/Function | Description |
|---|---|
| `X LIKE Y` | Pattern match: `%` = any chars, `_` = single char (ASCII case-insensitive) |
| `X LIKE Y ESCAPE Z` | Escape character for literal %/_ |
| `X GLOB Y` | Unix glob: `*` = any, `?` = single, `[abc]` = set (case-sensitive) |
| `X REGEXP Y` | No built-in implementation (register custom via C API) |

```sql
SELECT 'hello' LIKE 'H%';        -- true (case-insensitive)
SELECT 'hello' GLOB 'H*';        -- false (case-sensitive)
SELECT 'abc123' GLOB '[a-z]*';   -- true
SELECT 'test' LIKE 'te__';       -- true
```

## Query Planner Hints

| Function | Description |
|---|---|
| `likely(X)` | Hint: X is usually true |
| `unlikely(X)` | Hint: X is usually false |
| `likelihood(X, P)` | Hint: X is true with probability P (0.0-1.0) |

These are no-ops at runtime but guide the query planner.

```sql
SELECT * FROM users
WHERE likely(is_active = 1) AND name = 'Alice';
```

## System Functions

| Function | Description |
|---|---|
| `sqlite_version()` | SQLite version string |
| `sqlite_source_id()` | Source code version identifier |
| `sqlite_compileoption_get(N)` | N-th compile-time option |
| `sqlite_compileoption_used(X)` | 1 if compile option X was used |
| `sqlite_offset(X)` | Byte offset of X in database file |
| `load_extension(X)` | Load shared library extension |

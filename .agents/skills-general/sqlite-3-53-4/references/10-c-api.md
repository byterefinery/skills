# C/C++ Interface

## Table of Contents

- [Core Objects](#core-objects)
- [Opening/Closing](#openingclosing)
- [Executing SQL](#executing-sql)
- [Prepared Statements](#prepared-statements)
- [Binding Parameters](#binding-parameters)
- [Reading Results](#reading-results)
- [Error Handling](#error-handling)
- [Custom Functions](#custom-functions)
- [Utility Functions](#utility-functions)
- [Complete Example](#complete-example)

## Core Objects

| Object | Description |
|---|---|
| `sqlite3` | Database connection. Created by `sqlite3_open()`, destroyed by `sqlite3_close()` |
| `sqlite3_stmt` | Prepared statement. Created by `sqlite3_prepare_v2()`, destroyed by `sqlite3_finalize()` |

## Opening/Closing

```c
#include <sqlite3.h>

int sqlite3_open(const char *filename, sqlite3 **ppDb);
int sqlite3_open_v2(const char *filename, sqlite3 **ppDb, int flags, const char *zVfs);
int sqlite3_close(sqlite3 *db);
int sqlite3_close_v2(sqlite3 *db);
```

Flags for `sqlite3_open_v2()`:
- `SQLITE_OPEN_READONLY` — read-only
- `SQLITE_OPEN_READWRITE` — read/write (create if not exists)
- `SQLITE_OPEN_CREATE` — create if not exists
- `SQLITE_OPEN_URI` — interpret filename as URI
- `SQLITE_OPEN_MEMORY` — in-memory database

Special filenames:
- `":memory:"` — in-memory database
- `""` — temporary file-backed database

```c
sqlite3 *db;
int rc = sqlite3_open("mydb.db", &db);
if (rc != SQLITE_OK) {
    fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 1;
}
// ... use db ...
sqlite3_close(db);
```

## Executing SQL

### Simple Execution (Convenience API)

```c
int sqlite3_exec(sqlite3 *db, const char *sql,
                 int (*callback)(void *, int, char **, char **),
                 void *arg, char **errmsg);
```

Use for simple DDL or when you don't need parameter binding.

### Prepared Statements (Recommended)

```c
int sqlite3_prepare_v2(sqlite3 *db, const char *sql, int nByte,
                       sqlite3_stmt **ppStmt, const char **pzTail);
int sqlite3_step(sqlite3 *stmt);
int sqlite3_finalize(sqlite3 *stmt);
int sqlite3_reset(sqlite3 *stmt);
```

Always use `sqlite3_prepare_v2()` over the legacy `sqlite3_prepare()`. The `_v2` version auto-recompiles on schema changes.

## Binding Parameters

Parameters in SQL: `?`, `?NNN`, `:AAA`, `$AAA`, `@AAA`.

```c
int sqlite3_bind_blob(sqlite3_stmt *, int, const void *, int n, void(*)(void*));
int sqlite3_bind_double(sqlite3_stmt *, int, double);
int sqlite3_bind_int(sqlite3_stmt *, int, int);
int sqlite3_bind_int64(sqlite3_stmt *, int, sqlite3_int64);
int sqlite3_bind_text(sqlite3_stmt *, int, const char *, int n, void(*)(void*));
int sqlite3_bind_text64(sqlite3_stmt *, int, const char *, sqlite3_uint64, void(*)(void*), unsigned char encoding);
int sqlite3_bind_value(sqlite3_stmt *, int, const sqlite3_value *);
int sqlite3_bind_null(sqlite3_stmt *, int);
int sqlite3_clear_bindings(sqlite3_stmt *);
```

Parameter index starts at 1.

```c
sqlite3_stmt *stmt;
sqlite3_prepare_v2(db, "INSERT INTO users(name, email) VALUES(?1, ?2)", -1, &stmt, 0);
sqlite3_bind_text(stmt, 1, "Alice", -1, SQLITE_TRANSIENT);
sqlite3_bind_text(stmt, 2, "alice@example.com", -1, SQLITE_TRANSIENT);
sqlite3_step(stmt);
sqlite3_finalize(stmt);
```

## Reading Results

After `sqlite3_step()` returns `SQLITE_ROW`:

```c
const void *sqlite3_column_blob(sqlite3_stmt *, int iCol);
int sqlite3_column_bytes(sqlite3_stmt *, int iCol);
int sqlite3_column_bytes16(sqlite3_stmt *, int iCol);
double sqlite3_column_double(sqlite3_stmt *, int iCol);
int sqlite3_column_int(sqlite3_stmt *, int iCol);
sqlite3_int64 sqlite3_column_int64(sqlite3_stmt *, int iCol);
const char *sqlite3_column_text(sqlite3_stmt *, int iCol);
const unsigned char *sqlite3_column_text16(sqlite3_stmt *, int iCol);
int sqlite3_column_type(sqlite3_stmt *, int iCol);
sqlite3_value *sqlite3_column_value(sqlite3_stmt *, int iCol);
int sqlite3_column_count(sqlite3_stmt *pStmt);
const char *sqlite3_column_name(sqlite3_stmt *, int N);
```

Column index starts at 0. Data is valid until next `sqlite3_step()` or `sqlite3_finalize()`.

```c
sqlite3_stmt *stmt;
sqlite3_prepare_v2(db, "SELECT name, email FROM users WHERE id=?", -1, &stmt, 0);
sqlite3_bind_int(stmt, 1, 42);

while (sqlite3_step(stmt) == SQLITE_ROW) {
    const char *name = (const char *)sqlite3_column_text(stmt, 0);
    const char *email = (const char *)sqlite3_column_text(stmt, 1);
    printf("Name: %s, Email: %s\n", name, email);
}
sqlite3_finalize(stmt);
```

## Error Handling

```c
int sqlite3_errcode(sqlite3 *db);
int sqlite3_extended_errcode(sqlite3 *db);
const char *sqlite3_errmsg(sqlite3 *db);
const char *sqlite3_errmsg16(sqlite3 *db);
int sqlite3_errstr(int errcode);
```

On `sqlite3_stmt`:
```c
int sqlite3_stmt_errcode(sqlite3_stmt *stmt);
const char *sqlite3_stmt_errmsg(sqlite3_stmt *stmt);
```

Common return codes:
- `SQLITE_OK` (0) — success
- `SQLITE_ROW` (100) — another row ready
- `SQLITE_DONE` (101) — statement completed
- `SQLITE_ERROR` (1) — SQL error
- `SQLITE_BUSY` (5) — database is locked
- `SQLITE_MISUSE` (21) — API used incorrectly
- `SQLITE_NOMEM` (11) — memory allocation failure
- `SQLITE_CORRUPT` (11) — database disk image corrupted

Use `sqlite3_busy_timeout(db, ms)` to retry on busy instead of returning `SQLITE_BUSY`.

## Custom Functions

Register custom SQL functions:

```c
int sqlite3_create_function_v2(sqlite3 *db, const char *zFuncName, int nArg,
    int eTextRep, void *pApp,
    void (*xFunc)(sqlite3_context *, int, sqlite3_value **),
    void (*xStep)(sqlite3_context *, int, sqlite3_value **),
    void (*xFinal)(sqlite3_context *),
    void (*xDestroy)(void *));
```

For scalar functions, provide `xFunc`. For aggregate functions, provide `xStep` and `xFinal`.

```c
// Scalar function callback
void myFunc(sqlite3_context *ctx, int argc, sqlite3_value **argv) {
    double val = sqlite3_value_double(argv[0]);
    sqlite3_result_double(ctx, val * 2.0);
}

// Register
sqlite3_create_function(db, "double_val", 1, SQLITE_UTF8, NULL, myFunc, NULL, NULL, NULL);
```

Result functions:
```c
void sqlite3_result_blob(sqlite3_context *, const void *, int, void(*)(void*));
void sqlite3_result_double(sqlite3_context *, double);
void sqlite3_result_int(sqlite3_context *, int);
void sqlite3_result_int64(sqlite3_context *, sqlite3_int64);
void sqlite3_result_text(sqlite3_context *, const char *, int, void(*)(void*));
void sqlite3_result_null(sqlite3_context *);
void sqlite3_result_error(sqlite3_context *, const char *, int);
```

## Utility Functions

```c
const char *sqlite3_libversion(void);     // Version string
int sqlite3_libversion_number(void);       // Version number
const char *sqlite3_sourceid(void);        // Source ID
sqlite3_int64 sqlite3_last_insert_rowid(sqlite3 *db);
int sqlite3_changes(sqlite3 *db);
int sqlite3_total_changes(sqlite3 *db);
int sqlite3_threadsafe(void);              // Thread safety mode
int sqlite3_busy_timeout(sqlite3 *db, int ms);
void sqlite3_free(void *p);               // Free memory allocated by SQLite
char *sqlite3_mprintf(const char *zFormat, ...);
char *sqlite3_snprintf(int n, char *z, const char *zFormat, ...);
```

## Complete Example

```c
#include <stdio.h>
#include <sqlite3.h>

int main(void) {
    sqlite3 *db;
    int rc = sqlite3_open("example.db", &db);
    if (rc) {
        fprintf(stderr, "Cannot open: %s\n", sqlite3_errmsg(db));
        return 1;
    }

    // Enable foreign keys
    sqlite3_exec(db, "PRAGMA foreign_keys = ON;", NULL, NULL, NULL);

    // Create table
    const char *create_sql =
        "CREATE TABLE IF NOT EXISTS users("
        "  id INTEGER PRIMARY KEY,"
        "  name TEXT NOT NULL,"
        "  email TEXT UNIQUE"
        ");";
    rc = sqlite3_exec(db, create_sql, NULL, NULL, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Create error: %s\n", sqlite3_errmsg(db));
    }

    // Insert with prepared statement
    sqlite3_stmt *stmt;
    sqlite3_prepare_v2(db,
        "INSERT OR IGNORE INTO users(name, email) VALUES(?1, ?2)",
        -1, &stmt, NULL);
    sqlite3_bind_text(stmt, 1, "Alice", -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, "alice@example.com", -1, SQLITE_TRANSIENT);
    sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    // Query
    sqlite3_prepare_v2(db, "SELECT id, name, email FROM users ORDER BY id",
        -1, &stmt, NULL);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        const char *name = (const char *)sqlite3_column_text(stmt, 1);
        const char *email = (const char *)sqlite3_column_text(stmt, 2);
        printf("id=%d name=%s email=%s\n", id, name, email);
    }
    sqlite3_finalize(stmt);

    sqlite3_close(db);
    return 0;
}
```

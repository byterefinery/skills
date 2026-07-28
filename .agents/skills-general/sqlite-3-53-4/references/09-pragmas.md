# PRAGMA Commands

## Table of Contents

- [Overview](#overview)
- [Security & Integrity](#security--integrity)
- [Performance & Cache](#performance--cache)
- [Journaling & Transactions](#journaling--transactions)
- [Schema Introspection](#schema-introspection)
- [Connection Settings](#connection-settings)
- [Memory Management](#memory-management)
- [WAL Mode](#wal-mode)
- [Common Patterns](#common-patterns)

## Overview

PRAGMAs are SQLite-specific SQL commands that modify library operation or query internal data. They are not portable to other databases.

Syntax: `PRAGMA name;` (query) or `PRAGMA name = value;` (set).

Some PRAGMAs take effect during SQL compilation, not execution.

## Security & Integrity

| PRAGMA | Description |
|---|---|
| `foreign_keys` | Query/set FK enforcement. **OFF by default.** Use `PRAGMA foreign_keys=ON;` |
| `foreign_key_check` | Check for FK violations |
| `foreign_key_list(table)` | List FK constraints on a table |
| `defer_foreign_keys` | Defer FK checks until commit |
| `integrity_check` | Full database integrity check |
| `integrity_check(N)` | Check, report at most N errors |
| `integrity_check(table)` | Check specific table |
| `quick_check` | Faster, less thorough integrity check |
| `cell_size_check` | Enable extra b-tree page sanity checks |
| `ignore_check_constraints` | Disable CHECK constraint enforcement |
| `trusted_schema` | Allow/prevent prepared statements from being invalidated by schema changes |
| `secure_delete` | Overwrite deleted content with zeros |

```sql
-- Always enable foreign keys
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;  -- verify: returns 1

-- Check integrity
PRAGMA integrity_check;  -- returns 'ok' or error descriptions
PRAGMA quick_check;      -- faster check

-- Check foreign key violations
PRAGMA foreign_key_check;
```

## Performance & Cache

| PRAGMA | Description |
|---|---|
| `cache_size` | Max cached pages (positive) or KB (negative). Default: -2000 (2MB) |
| `cache_spill` | Enable/disable spilling dirty pages mid-transaction |
| `synchronous` | `OFF`, `NORMAL` (default), `FULL`, `EXTRA` |
| `temp_store` | `DEFAULT`, `FILE`, `MEMORY` |
| `mmap_size` | Max memory-mapped I/O bytes. Default: 0 (disabled) |
| `optimize` | Run ANALYZE and optimize query planner (since 3.32.0) |
| `automatic_index` | Enable/disable automatic indexing |
| `busy_timeout` | Milliseconds to wait on locked database |

```sql
-- Increase cache for large queries
PRAGMA cache_size = -65536;  -- 64MB

-- Reduce sync overhead (risk: corruption on crash)
PRAGMA synchronous = OFF;

-- Store temp data in memory
PRAGMA temp_store = MEMORY;

-- Wait 5 seconds on busy database
PRAGMA busy_timeout = 5000;

-- Optimize query planner
PRAGMA optimize;
```

## Journaling & Transactions

| PRAGMA | Description |
|---|---|
| `journal_mode` | `DELETE` (default), `TRUNCATE`, `PERSIST`, `MEMORY`, `WAL`, `OFF` |
| `journal_size_limit` | Max rollback journal size (negative = unlimited). Default: -1 |
| `locking_mode` | `NORMAL` (default) or `EXCLUSIVE` |
| `read_uncommitted` | Equivalent to `locking_mode=EXCLUSIVE` + `temp_store=MEMORY` |
| `wal_autocheckpoint` | Auto-checkpoint page count in WAL mode. Default: 1000 |
| `wal_checkpoint` | Manual WAL checkpoint: `PASSIVE`, `FULL`, `RESTART`, `TRUNCATE` |

```sql
-- Enable WAL mode (persistent across connections)
PRAGMA journal_mode = WAL;

-- Checkpoint WAL
PRAGMA wal_checkpoint(TRUNCATE);

-- Set journal size limit
PRAGMA journal_size_limit = 67108864;  -- 64MB
```

### Journal Mode Comparison

| Mode | Safety | Write Speed | Read Concurrency |
|---|---|---|---|
| `DELETE` | Full | Standard | Readers blocked during writes |
| `TRUNCATE` | Full | Faster (no directory change) | Readers blocked during writes |
| `PERSIST` | Full | Faster | Readers blocked during writes |
| `MEMORY` | None (corruption on crash) | Fastest | Readers blocked during writes |
| `WAL` | Full | Good | **Readers not blocked** |
| `OFF` | None | Fastest | Readers blocked during writes |

## Schema Introspection

| PRAGMA | Description |
|---|---|
| `table_info(table)` | Column names, types, notnull, dflt_value, pk |
| `table_xinfo(table)` | Extended info including generated columns |
| `index_list(table)` | Indices on a table |
| `index_info(index)` | Columns in an index |
| `index_xinfo(index)` | Extended index info |
| `foreign_key_list(table)` | FK constraints |
| `collation_list` | Collations registered for connection |
| `function_list` | SQL functions known to connection |
| `module_list` | Registered virtual table modules |
| `compile_options` | Compile-time options used |
| `database_list` | Attached databases |
| `schema_version` | Schema version number (readable/writable) |
| `user_version` | User version number (readable/writable) |
| `data_version` | Changes when data is modified by another connection |
| `page_count` | Number of pages in database |
| `freelist_count` | Number of unused pages |
| `page_size` | Database page size |
| `max_page_count` | Max allowed pages |
| `application_id` | 32-bit application ID |
| `encoding` | Text encoding: UTF-8, UTF-16le, UTF-16be |
| `table_list` | List of tables |
| `pragma_list` | List of all pragmas |

```sql
-- Inspect table schema
PRAGMA table_info(users);
-- cid | name | type | notnull | dflt_value | pk

-- List indices
PRAGMA index_list(users);

-- Check page count
PRAGMA page_count;
PRAGMA freelist_count;
```

## Connection Settings

| PRAGMA | Description |
|---|---|
| `query_only` | Read-only mode (no writes allowed) |
| `recursive_triggers` | Enable recursive triggers. Default: OFF |
| `reverse_unordered_selects` | Reverse row order for unordered SELECTs |
| `legacy_alter_table` | Legacy ALTER TABLE behavior |
| `legacy_file_format` | Use older file format |
| `threads` | Query/set number of worker threads |

## Memory Management

| PRAGMA | Description |
|---|---|
| `soft_heap_limit` | Soft limit on heap memory (SQLite tries to stay under) |
| `hard_heap_limit` | Hard limit (can only lower, not raise via PRAGMA) |
| `shrink_memory` | Try to release unused memory |

## WAL Mode

WAL (Write-Ahead Log) is the recommended journal mode for most applications:

```sql
PRAGMA journal_mode = WAL;
PRAGMA wal_autocheckpoint = 1000;  -- checkpoint every 1000 pages
PRAGMA wal_checkpoint(PASSIVE);    -- checkpoint, don't block writers
PRAGMA wal_checkpoint(FULL);       -- checkpoint, block writers if needed
PRAGMA wal_checkpoint(TRUNCATE);   -- checkpoint and truncate WAL file
```

WAL mode allows concurrent readers and writers. The WAL file persists until checkpointed.

## Common Patterns

```sql
-- Recommended connection setup
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA cache_size = -65536;
PRAGMA temp_store = MEMORY;
PRAGMA busy_timeout = 5000;

-- Before bulk insert
PRAGMA synchronous = OFF;
BEGIN TRANSACTION;
-- ... many INSERTs ...
COMMIT;
PRAGMA synchronous = NORMAL;  -- restore

-- Reclaim space
PRAGMA auto_vacuum = INCREMENTAL;
PRAGMA incremental_vacuum;
-- Or full rebuild:
VACUUM;

-- Check database health
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

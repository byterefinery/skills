# TinyDB 4.9.0 — Extensions and Upgrade

From `docs/extensions.rst`, `docs/intro.rst`, `docs/changelog.rst`, and `docs/upgrade.rst` (v4.9.0 tag).

## Project status

TinyDB is in **maintenance mode** — it has reached a mature, stable state where significant new features or architectural changes are not planned, though bugfix releases and community contributions still happen.

## When NOT to use TinyDB

From the docs, TinyDB is the wrong choice if you need:

- Access from multiple processes or threads (e.g. when using Flask!)
- Indexes for tables
- An HTTP server
- Managing relationships between tables or similar
- ACID guarantees
- High-speed performance

In those cases consider SQLite, Buzhug, CodernityDB, or MongoDB.

## Extensions ecosystem

| Extension | Status | Repo | Description |
|---|---|---|---|
| `tinydb-rust` | beta | https://github.com/itsmorninghao/tinydb-rust/ | Drop-in Rust reimplementation for better performance |
| `aiotinydb` | stable | https://github.com/ASMfreaK/aiotinydb | asyncio compatibility shim — use TinyDB in asyncio contexts without slow synchronous IO |
| `BetterJSONStorage` | stable | https://github.com/MrPigss/BetterJSONStorage | Faster storage using Orjson (parsing) and BLOSC (compression) |
| `tinydb-serialization` | stable | https://github.com/msiemens/tinydb-serialization | Serialization for objects TinyDB otherwise couldn't handle |
| `tinydb-smartcache` | stable | https://github.com/msiemens/tinydb-smartcache | Smart query cache that updates instead of invalidating on insert/remove/update |
| `tinyrecord` | stable | https://github.com/eugene-eeo/tinyrecord | Experimental atomic transaction support (record-first, then execute) |
| `tinydb-appengine` | inactive | https://github.com/imalento/tinydb-appengine | Storage for App Engine (JSON read-only) |
| `TinyDBTimestamps` | inactive | https://github.com/pachacamac/TinyDBTimestamps | Auto create-at/update-at timestamps |
| `tinyindex` | inactive | https://github.com/eugene-eeo/tinyindex | Document indexing for deterministic yielding |
| `tinymongo` | inactive | https://github.com/schapman1974/tinymongo | Flat-file drop-in replacement for MongoDB |
| `TinyMP` | inactive | https://github.com/alshapton/TinyMP | MessagePack-based storage |

## Changelog — v4.9.0 (2026-08-06)

- **Drop official support for Python 3.8 and 3.9** (both EOL) — TinyDB now requires Python 3.10+
- Fix: `Table.update(doc_ids=...)` and `Table.remove(doc_ids=...)` no longer raise `KeyError` for missing IDs — missing IDs are silently skipped and the returned list contains only IDs actually updated/removed (issue 591). Previously `update` could leave the table partially updated with a mix of existing and missing IDs.
- Fix: `Query.test()` no longer raises `TypeError` when passed unhashable extra arguments (lists, dicts) (issue 517)
- Fix: `FileNotFoundError` when creating a database file in the current directory without an explicit path prefix (PR 619)
- Fix: correctly handle falsy values (`0`, `None`) stored in `LRUCache`
- Improvement: more precise type hints for `Table.get` (PR 602)
- Improvement: type hints for `Table.update` and `tinydb.operations` use `MutableMapping`, so in-place mutating transforms type-check (issue 598)

### Recent prior releases

- **v4.8.2 (2024-10-12)** — fix: correctly update query cache when search results changed (issue 560)
- **v4.8.1 (2024-10-07)** — feature: persist empty tables (`persist_empty=True`, PR 518); fix: replacing `doc_id` type works properly (issue 545)
- **v4.8.0 (2023-06-12)** — feature: retrieve multiple documents by ID via `Table.get(doc_ids=[...])` (PR 504)
- **v4.7.0 (2022-02-19)** — feature: `insert_multiple` accepts `Document` instances (PR 455); performance: convert document IDs only when returning documents (PR 460)
- **v4.6.0 (2022-01-17)** — feature: `map()` query operation (PR 445) — note it may break queries on a field named `map` using property syntax; `typing-extensions` v4 support

## Upgrading to 4.x (from 3.x)

From `docs/upgrade.rst` — v4.0 API changes:

- `TinyDB.purge_tables(...)` → `TinyDB.drop_tables(...)`
- `TinyDB.purge_table(...)` → `TinyDB.drop_table(...)`
- `Table.purge()` → `Table.truncate()`
- `TinyDB(default_table='name')` → `TinyDB.default_table_name = 'name'`
- `TinyDB(table_class=Class)` → `TinyDB.table_class = Class`
- `TinyDB.DEFAULT_TABLE`, `TinyDB.DEFAULT_TABLE_KWARGS`, `TinyDB.DEFAULT_STORAGE` → use the class-variable hooks described in the extend docs

v3.0 query API changes that carry into 4.x:

- `where('...').contains('...')` → `where('...').search('...')`
- `where('foo').has('bar')` → `where('foo').bar` or `Query().foo.bar`
- Key existence checks are explicit: `where('foo').exists()`
- Non-identifier keys use array notation: `Query()['a.b.c']`
- `SmartCacheTable` moved to `msiemens/tinydb-smartcache`
- Serialization moved to `msiemens/tinydb-serialization`
- Empty storages return `None` instead of raising `ValueError`

## Upgrading to 4.9.0 specifically

- Requires **Python 3.10+** — bump your runtime if you were on 3.8/3.9.
- If you depended on `update(doc_ids=...)`/`remove(doc_ids=...)` raising `KeyError` for missing IDs, that no longer happens — check the length of the returned ID list instead.
- No other API changes; the rest are bug fixes.

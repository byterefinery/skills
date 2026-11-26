# Upstream Examples and Documentation Map

Source: `examples/` tree and `doc/build/` at tag `rel_2_1_9` of https://github.com/sqlalchemy/sqlalchemy (repo root: https://github.com/sqlalchemy/sqlalchemy/tree/rel_2_1_9). Published docs: https://docs.sqlalchemy.org/en/latest/ (2.1 series).

## Runnable demos in `examples/`

All are importable/runnable modules in the source repo. Study the local clone (`examples/<name>/`) rather than fetching docs when porting a pattern.

| Demo | What it shows (from the module docstring) | Key files |
|---|---|---|
| `asyncio` | asyncio engine feature | `async_orm.py` (full pattern in [09-async-support](09-async-support.md)), `basic.py`, `greenlet_orm.py`, `gather_orm_statements.py`, `async_orm_writeonly.py` |
| `association` | "association object" pattern — an intermediary class mediates the relationship between two others (many-to-many with attributes) | `basic_association.py`, `proxied_association.py` |
| `inheritance` | The three inheritance strategies | `joined.py`, `single.py`, `concrete.py` |
| `versioned_history` | Extension creating version tables; stores a record for each change ("history" rows) | `history_meta.py` |
| `versioned_rows` | Intercept UPDATEs and turn them into new row versions | see module |
| `extending_query` | Recipes augmenting ORM SELECT behavior with 2.0-style `Session.execute` | `temporal_range.py`, `filter_public.py` |
| `adjacency_list` | Dictionary-of-dictionaries mapped with an adjacency list model | see module |
| `materialized_paths` | Hierarchical data via materialized paths | see module |
| `nested_sets` | Nested-sets pattern for hierarchical data | see module |
| `graphs` | Graph stored as edges referencing "lower"/"upper" nodes in a nodes table | see module |
| `generic_associations` | Associating multiple parent types with one child type (polymorphic associations) | see module |
| `custom_attributes` | Modifications to SQLAlchemy's attribute management system | see module |
| `dynamic_dict` | "dynamic" relation — dict operations on a large collection without loading it all | see module |
| `dogpile_caching` | Embedding `dogpile.cache` with the ORM | see module |
| `sharding` | Horizontal sharding across multiple databases | see module |
| `performance` | Suites each focused on a use case with a specific performance profile | see module |
| `vertical` | "Vertical table" mappings — individual attributes stored as rows | see module |
| `space_invaders` | Space Invaders game using SQLite as the state machine (classic demo) | see module |
| `syntax_extensions` | Extending `Select` with a new non-standard clause (`QUALIFY`) | see module |

## Documentation map (`doc/build/`, at tag `rel_2_1_9`)

- `doc/build/tutorial/` — the **unified tutorial** (Core + ORM integrated): `engine.rst`, `metadata.rst`, `data_insert.rst`, `data_select.rst`, `data_update.rst`, `dbapi_transactions.rst`, `orm_related_objects.rst`, `orm_data_manipulation.rst`
- `doc/build/orm/quickstart.rst` — the canonical 2.x ORM example
- `doc/build/orm/queryguide/` — full query guide: `select.rst`, `dml.rst`, `relationships.rst`, `inheritance.rst`
- `doc/build/orm/relationships.rst`, `orm/cascades.rst`, `orm/inheritance.rst`, `orm/versioning.rst` — deep dives
- `doc/build/core/` — Core API: `engines_connections.rst`, `connections.rst`, `selectable.rst`, `dml.rst`, `type_api.rst`, `reflection.rst`, `events.rst`
- `doc/build/dialects/` — per-backend docs: `postgresql.rst` (psycopg 3, asyncpg), `mysql.rst`, `sqlite.rst`, `mssql.rst`, `oracle.rst`
- `doc/build/changelog/migration_21.rst` — **2.1 migration guide** (what this skill targets: greenlet install, autoflush, composites, drivers)
- `doc/build/changelog/migration_20.rst` — 2.0 migration guide (Query removal, connection/transaction rewrite, Result rules)
- `doc/build/changelog/whatsnew_20.rst` — 2.0 feature overview
- `doc/build/faq/` — troubleshooting: `sessions.rst`, `connections.rst`, `performance.rst`, `sqlexpressions.rst`
- `README.rst` / `README.dialects.rst` — feature list and dialect support table

## When to reach for which

- Need a relationship pattern (many-to-many with data, polymorphic) → `examples/association`, `examples/generic_associations`
- Tree/graph data → `adjacency_list`, `materialized_paths`, `nested_sets`, `graphs`
- Audit trail / temporal data → `versioned_history`, `versioned_rows`, `extending_query/temporal_range.py`
- Async code → `asyncio/async_orm.py` (complete, runnable)
- Caching or sharding → `dogpile_caching`, `sharding`

# Virtual Tables

## Table of Contents

- [Overview](#overview)
- [FTS5 Full-Text Search](#fts5-full-text-search)
- [R-Tree Spatial Index](#rtree-spatial-index)
- [Table-Valued Functions](#table-valued-functions)
- [Custom Virtual Tables](#custom-virtual-tables)

## Overview

Virtual tables look like regular tables to SQL but are implemented by callback methods. Created with `CREATE VIRTUAL TABLE`:

```sql
CREATE VIRTUAL TABLE table_name USING module_name(args);
```

Built-in modules: `fts5`, `rtree`, `dbstat`.

Limitations:
- No triggers on virtual tables
- No additional indices via `CREATE INDEX`
- No `ALTER TABLE ... ADD COLUMN`

## FTS5 Full-Text Search

FTS5 provides full-text search as a virtual table module. Built-in since 3.9.0.

### Creating FTS5 Tables

```sql
CREATE VIRTUAL TABLE documents USING fts5(
  title,
  body,
  content='source_table',     -- external content table
  tokenize='unicode61',       -- tokenizer
  prefix='2,4'                -- prefix indexes
);
```

### Tokenizers

| Tokenizer | Description |
|---|---|
| `unicode61` | Unicode normalization, lowercase, removes punctuation (default) |
| `unicode61 tokenchars='...'` | Keep specified characters as part of tokens |
| `unicode61 sep='-'` | Treat specified characters as separators |
| `ascii` | ASCII-only tokenizer |
| `porter` | Unicode61 with Porter stemming |
| `trigram` | Overlapping 3-character sequences |

### Querying

```sql
-- Basic search
SELECT * FROM documents WHERE documents MATCH 'hello world';

-- Phrase search
SELECT * FROM documents WHERE documents MATCH '"hello world"';

-- Prefix search
SELECT * FROM documents WHERE documents MATCH 'hello:*';

-- Boolean operators
SELECT * FROM documents WHERE documents MATCH 'hello AND world';
SELECT * FROM documents WHERE documents MATCH 'hello OR world';
SELECT * FROM documents WHERE documents MATCH 'hello AND NOT world';

-- NEAR operator
SELECT * FROM documents WHERE documents MATCH 'hello NEAR/10 world';

-- Column-specific search
SELECT * FROM documents WHERE documents MATCH 'title:hello';
SELECT * FROM documents WHERE documents MATCH 'body:hello AND title:world';
```

### Ranking and Highlighting

```sql
-- BM25 ranking (lower = better match)
SELECT rank, snippet(documents, 1, '[b]', '[/b]') AS highlighted
FROM documents
WHERE documents MATCH 'hello world'
ORDER BY bm25(documents)
LIMIT 10;
```

Auxiliary functions:
- `bm25(table, ...)` — relevance ranking
- `highlight(table, col, before, after)` — highlight matching terms
- `snippet(table, col, before, after, ellipsis, max_tokens)` — excerpt with context

### Maintenance

```sql
-- Rebuild index
INSERT INTO documents(documents) VALUES('rebuild');

-- Optimize
INSERT INTO documents(documents) VALUES('optimize');

-- Integrity check
INSERT INTO documents(documents) VALUES('integrity-check');

-- Delete all
INSERT INTO documents(documents) VALUES('delete-all');
```

### External Content Tables

```sql
-- Source data from another table
CREATE VIRTUAL TABLE docs_fts USING fts5(title, body, content=documents);

-- Sync FTS index with source table
CREATE TRIGGER docs_ai AFTER INSERT ON documents BEGIN
  INSERT INTO docs_fts(rowid, title, body) VALUES (new.rowid, new.title, new.body);
END;

CREATE TRIGGER docs_ad AFTER DELETE ON documents BEGIN
  INSERT INTO docs_fts(docs_fts, rowid, title, body) VALUES ('delete', old.rowid, old.title, old.body);
END;

CREATE TRIGGER docs_au AFTER UPDATE ON documents BEGIN
  INSERT INTO docs_fts(docs_fts, rowid, title, body) VALUES ('delete', old.rowid, old.title, old.body);
  INSERT INTO docs_fts(rowid, title, body) VALUES (new.rowid, new.title, new.body);
END;
```

## R-Tree Spatial Index

R-Tree provides efficient spatial indexing for 1D to ND data.

### Creating R-Tree Tables

```sql
CREATE VIRTUAL TABLE spatial_index USING rtree(
  id,          -- integer primary key
  minX, maxX,  -- 1D range
  minY, maxY   -- 2D range
);
```

### Querying

```sql
-- Point containment
SELECT * FROM spatial_index
WHERE minX <= 10 AND maxX >= 10 AND minY <= 20 AND maxY >= 20;

-- Overlap query
SELECT * FROM spatial_index
WHERE maxX >= 5 AND minX <= 15 AND maxY >= 10 AND minY <= 25;

-- Join with data table
SELECT d.*
FROM data_table d
JOIN spatial_index s ON d.id = s.id
WHERE s.minX <= 10 AND s.maxX >= 10 AND s.minY <= 20 AND s.maxY >= 20;
```

R-Tree tables support INSERT, UPDATE, DELETE. The id column must match the referenced data table.

## Table-Valued Functions

Since 3.16.0, PRAGMAs that return results can be used as table-valued functions:

```sql
SELECT * FROM pragma_table_info('users');
SELECT * FROM pragma_index_list('users');
SELECT * FROM pragma_foreign_key_list('users');
SELECT * FROM pragma_collation_list();
SELECT * FROM pragma_function_list();
```

JSON table-valued functions:
```sql
SELECT * FROM json_each('{"a":1,"b":2}');
SELECT * FROM json_tree('[1,[2,3]]');
```

## Custom Virtual Tables

Register via `sqlite3_create_module()`:

```c
int sqlite3_create_module(sqlite3 *db, const char *zName,
    const sqlite3_module *pModule, void *pAux);
```

The `sqlite3_module` struct defines callback methods: `xCreate`, `xConnect`, `xBestIndex`, `xDisconnect`, `xDestroy`, `xOpen`, `xClose`, `xFilter`, `xNext`, `xColumn`, `xRowid`, `xUpdate`, etc.

See the SQLite source code `ext/fts5/` and `ext/rtree/` for reference implementations.

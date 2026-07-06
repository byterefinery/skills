# SQLite Extensions Reference

rqlite loads SQLite extensions via `-extensions-path`. Paths can be directories, zipfiles, or tar.gz archives containing `.so` (Linux/macOS) or `.dll` (Windows) files.

## Loading Extensions

```bash
# Single directory
rqlited -extensions-path /opt/extensions /data/node1

# Multiple paths (comma-separated)
rqlited -extensions-path /opt/vec,/opt/sqlean /data/node1

# Zipfile
rqlited -extensions-path /opt/sqlite-vec.zip /data/node1

# tar.gz archive
rqlited -extensions-path /opt/extensions.tar.gz /data/node1
```

Extensions are loaded at startup and available to all connections. They must be present on every node in a cluster.

## Checking Loaded Extensions

Via CLI:
```bash
rqlite
>.extensions
# Output: vec, math, crypto, ...
```

Via HTTP:
```bash
curl 'http://localhost:4001/status?key=extensions'
# {"names": ["vec", "math"]}
```

## Bundled Extensions (Docker Image)

The official `rqlite/rqlite` Docker image includes pre-built extensions in `/opt/extensions/`. Enable via the `SQLITE_EXTENSIONS` environment variable:

```bash
docker run -e SQLITE_EXTENSIONS=vec,math rqlite/rqlite
```

Commonly available extensions:
- **sqlite-vec** — Vector search (ANN for embeddings)
- **sqlean** — Suite including: math functions, crypto (hash, HMAC), uuid, regex, csv
- **sqliteai** — AI/ML functions
- **rqlite-ext** — rqlite-specific extensions

Check the Dockerfile `tools/build-*` scripts for the complete list.

## Custom Extensions

Mount custom extensions:

```bash
docker run -v /my/extensions:/custom-ext \
  -e CUSTOM_SQLITE_EXTENSIONS_PATH=/custom-ext \
  rqlite/rqlite
```

Or combine with bundled extensions:
```bash
docker run -e SQLITE_EXTENSIONS=vec \
  -e CUSTOM_SQLITE_EXTENSIONS_PATH=/custom-ext \
  -v /my/extensions:/custom-ext \
  rqlite/rqlite
```

## Building Extensions

Extensions must be compiled as SQLite loadable extensions against the same SQLite version used by rqlite (3.35.2 in v10.2.1, upgraded to 3.53.0 in v10.0.1, current in v10.2.7).

### Linux Build Example

```bash
# Clone extension source
git clone https://github.com/asg017/sqlite-vec.git
cd sqlite-vec

# Build with gcc, targeting SQLite API
gcc -shared -fPIC -o vec.so vec.c -lsqlite3
```

The resulting `.so` file goes in your extensions directory.

### Cross-Platform Notes

- Linux/macOS: `.so` files
- Windows: `.dll` files
- Extensions must match the architecture (amd64/arm64)
- CGO is required for the SQLite driver; extensions use the same ABI

## Common Extension Use Cases

### Vector Search (sqlite-vec)

```sql
-- Create vector index
CREATE VIRTUAL TABLE item_embeddings USING vec0(
  embedding float[768]
);

-- Insert embeddings
INSERT INTO item_embeddings(rowid, embedding)
VALUES (1, '[0.1, 0.2, ...]');

-- Similarity search
SELECT rowid, distance
FROM item_embeddings
WHERE embedding MATCH '[0.15, 0.25, ...]'
AND k = 10;
```

### Math Functions (sqlean)

```sql
-- Trigonometric functions
SELECT sin(3.14), cos(0), tan(0.5);

-- Statistical functions
SELECT mean(values), stddev(values) FROM measurements;
```

### Cryptography (sqlean)

```sql
-- Hash functions
SELECT hash('sha256', 'hello world');
SELECT hmac('sha256', 'message', 'secret-key');

-- UUID generation
SELECT uuid4();
SELECT uuid7();
```

### Regex (sqlean)

```sql
SELECT * FROM users WHERE email REGEXP '^[a-z]+@example\\.com$';
```

## Extension Gotchas

- **Extensions must be on all nodes** — a cluster query routed to a node without the extension will fail
- **Extension versions must match** — mismatched extension versions across nodes cause undefined behavior
- **Binary compatibility matters** — extensions compiled against different SQLite versions may crash
- **No dynamic loading at runtime** — extensions are loaded at `rqlited` startup; restart required to add/change
- **Docker image extensions are baked in** — updating bundled extensions requires rebuilding the image or using custom extension paths

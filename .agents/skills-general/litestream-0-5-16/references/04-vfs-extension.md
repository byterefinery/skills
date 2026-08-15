# litestream-vfs Extension

Table of contents:
- [Overview](#overview)
- [Building](#building)
- [Configuration](#configuration)
- [Usage](#usage)
- [SQL functions](#sql-functions)
- [Time travel](#time-travel)
- [Write mode (experimental)](#write-mode-experimental)
- [Troubleshooting](#trleshooting)

## Overview

The Litestream VFS (`litestream-vfs.so` / `.dylib`) is a loadable SQLite extension that reads databases **directly from replica storage** (S3, GCS, ABS, OSS, file, SFTP, NATS, WebDAV) — no restore to local disk. A background goroutine polls for new LTX files, pages are served from an LRU cache (default 10 MB), and the extension supports time-travel queries and experimental write mode.

Requirements: SQLite 3.31.0+ runtime, CGO build. The default `litestream/litestream` Docker image ships the extension at `/usr/local/lib/litestream-vfs.so`; the hardened scratch image does not.

## Building

```bash
make vfs                    # current architecture
make vfs-linux-amd64        # dist/litestream-vfs-linux-amd64.so
make vfs-linux-arm64        # dist/litestream-vfs-linux-arm64.so
make vfs-darwin-amd64       # dist/litestream-vfs-darwin-amd64.dylib
make vfs-darwin-arm64       # dist/litestream-vfs-darwin-arm64.dylib
make vfs-test               # run the VFS test suite
```

## Configuration

The VFS is configured by environment variables read by the host process:

| Variable | Purpose | Default |
|---|---|---|
| `LITESTREAM_REPLICA_URL` | Replica URL (required) | — |
| `LITESTREAM_LOG_LEVEL` | `DEBUG` or `INFO` | `INFO` |
| `LITESTREAM_WRITE_ENABLED` | Enable write mode | `false` |
| `LITESTREAM_SYNC_INTERVAL` | Write-mode sync cadence | `1s` |
| `LITESTREAM_BUFFER_PATH` | Local write buffer file | temp file |

Credentials come from the same environment as the main binary (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`, ...).

## Usage

```sql
-- in sqlite3 or any host that can load extensions
.load /usr/local/lib/litestream-vfs.so
.open file:mydb.db?vfs=litestream
SELECT * FROM users;
```

The database name in `.open` is arbitrary — the replica URL determines the actual data.

Python:

```python
import os, sqlite3
os.environ["LITESTREAM_REPLICA_URL"] = "s3://my-bucket/mydb"

conn = sqlite3.connect(":memory:")
conn.enable_load_extension(True)
conn.load_extension("/usr/local/lib/litestream-vfs.so")

conn = sqlite3.connect("file:mydb.db?vfs=litestream")
for row in conn.execute("SELECT * FROM users"):
    print(row)
```

## SQL functions

| Function | Returns |
|---|---|
| `litestream_txid()` | Current view TXID as 16-hex string |
| `litestream_time()` | View timestamp (RFC 3339) or `latest` |
| `litestream_lag()` | Seconds since the last successful LTX poll; `-1` if never polled |

`litestream_lag()` is the primary health signal for a VFS-based read replica.

## Time travel

```sql
SELECT litestream_set_time('2024-01-15T10:30:00Z');  -- absolute (RFC 3339)
SELECT litestream_set_time('5 minutes ago');         -- relative expressions
SELECT litestream_set_time('yesterday');
SELECT COUNT(*) FROM orders;                          -- historical view
SELECT litestream_set_time('LATEST');                 -- back to present
```

Limitations:

- Rebuilding the page index for a historical view can take time on large databases.
- History is only available as long as the LTX files exist — L0 retention (default 5m) and snapshot retention bound how far back you can travel.
- Time travel is read-only; writes are disabled while viewing a historical state.

## Write mode (experimental)

```bash
export LITESTREAM_REPLICA_URL="s3://my-bucket/mydb"
export LITESTREAM_WRITE_ENABLED="true"
export LITESTREAM_SYNC_INTERVAL="1s"
```

- Writes land in a local buffer file for durability; dirty pages are packaged into an LTX and uploaded every `LITESTREAM_SYNC_INTERVAL` (and on close).
- Conflict detection: if the remote advanced unexpectedly, the write fails with `ErrConflict`.
- Single writer enforced at the SQLite lock level — a second writer gets `SQLITE_BUSY`. Multiple *connections* in write mode are fine (e.g. `database/sql` pools).
- Can create a brand-new database from scratch when no LTX files exist yet.

```sql
.load /usr/local/lib/litestream-vfs.so
.open file:newdb.db?vfs=litestream
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
INSERT INTO users (name) VALUES ('Alice');   -- synced to remote automatically
```

Treat write mode as experimental — for production replication, run the `litestream` daemon on the primary.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Extension fails to load | The extension must match the platform (`.so` on Linux, `.dylib`/`.so` on macOS) and the SQLite version (3.31+) |
| `no backup files available` | Check the replica URL, credentials, and that the primary replicated at least one transaction |
| High read latency | Increase the page cache, lower the poll interval, or use a nearer storage region |
| Need detail | `LITESTREAM_LOG_LEVEL=DEBUG` |

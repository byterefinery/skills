# Backups Reference

## Hot Backup via HTTP

Backup a running node without stopping it:

```bash
# SQLite binary backup (default)
curl -o backup.db 'http://localhost:4001/db/backup'

# SQL text dump
curl -o backup.sql 'http://localhost:4001/db/backup?fmt=sql'

# Compressed backup
curl -o backup.db.gz 'http://localhost:4001/db/backup?compress'

# Backup specific tables
curl -o backup.db 'http://localhost:4001/db/backup?tables=users,orders'

# VACUUM before backup (blocks writes during vacuum)
curl -o backup.db 'http://localhost:4001/db/backup?vacuum'
```

Backup always reads from the leader for consistency. Use `?noleader` to read from local copy (may be stale).

## Hot Backup via CLI

```bash
rqlite
>.backup /path/to/backup.db
```

## SQL Dump

Dump database as SQL text:

```bash
# Via HTTP
curl -o dump.sql 'http://localhost:4001/db/backup?fmt=sql'

# Via CLI
rqlite
>.dump dump.sql
>.dump dump.sql users,orders    # Specific tables only
```

## Restore to Cluster

Load data into a running cluster (works on any node, forwards to leader):

```bash
# SQLite binary file
curl -XPOST 'http://localhost:4001/db/load' --data-binary @backup.db

# SQL dump
curl -XPOST 'http://localhost:4001/db/load' --data-binary @dump.sql
```

SQL dumps are executed as a transaction with rollback on error.

Via CLI:
```bash
rqlite
>.restore /path/to/backup.db
>.restore /path/to/dump.sql
```

## Boot Single Node

For fresh nodes or single-node setups, boot directly from SQLite file (bypasses Raft, then snapshots):

```bash
curl -XPOST 'http://localhost:4001/boot' --data-binary @seed.db
```

Via CLI:
```bash
rqlite
>.boot /path/to/seed.db
```

**Warning:** Only safe on single-node clusters or during initial bootstrap. On multi-node clusters, use `/db/load` instead.

## Auto-Backup

Configure periodic backups to cloud storage or local filesystem with `-auto-backup`:

### S3 / MinIO Config

```json
{
  "type": "s3",
  "version": 1,
  "interval": "1h",
  "timestamp": false,
  "vacuum": false,
  "no_compress": false,
  "sub": {
    "endpoint": "https://s3.amazonaws.com",
    "region": "us-east-1",
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "bucket": "rqlite-backups",
    "path": "backups",
    "force_path_style": false
  }
}
```

For MinIO, set `endpoint` to your MinIO URL and `force_path_style: true`.

### Google Cloud Storage Config

```json
{
  "type": "gcs",
  "version": 1,
  "interval": "1h",
  "timestamp": false,
  "vacuum": false,
  "no_compress": false,
  "sub": {
    "bucket": "rqlite-backups",
    "path": "backups",
    "credentials_file": "/path/to/service-account.json"
  }
}
```

### Local Filesystem Config

```json
{
  "type": "file",
  "version": 1,
  "interval": "1h",
  "timestamp": false,
  "vacuum": false,
  "no_compress": false,
  "sub": {
    "dir": "/var/backups/rqlite",
    "name": "rqlite-backup.db"
  }
}
```

### Common Fields

| Field | Type | Description |
|---|---|---|
| `type` | string | `s3`, `gcs`, or `file` |
| `version` | int | Config version (1) |
| `interval` | duration | Backup frequency (e.g., `1h`, `30m`) |
| `timestamp` | bool | Append timestamp to backup filename |
| `vacuum` | bool | VACUUM before backup |
| `no_compress` | bool | Disable compression (default: compressed) |

Start with:
```bash
rqlited -auto-backup /path/to/backup-config.json /data/node1
```

## Auto-Restore

Restore from cloud storage on startup with `-auto-restore`:

```json
{
  "type": "s3",
  "version": 1,
  "timeout": "30s",
  "continue_on_failure": false,
  "sub": {
    "endpoint": "https://s3.amazonaws.com",
    "region": "us-east-1",
    "access_key_id": "AKIA...",
    "secret_access_key": "wJalrXUtnFEMI...",
    "bucket": "rqlite-backups",
    "path": "backups/latest.db"
  }
}
```

**Cannot be combined with `-join`** — a node either boots from backup or joins an existing cluster.

## Restore from Standalone SQLite

A regular SQLite database file can be loaded into rqlite:

```bash
# Create a standalone SQLite DB
sqlite3 mydb.db "CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT); INSERT INTO t VALUES(1,'hello');"

# Load into rqlite
curl -XPOST 'http://localhost:4001/db/load' --data-binary @mydb.db
```

## Backup Best Practices

- Run backups against the leader for consistency (default behavior)
- Use `?compress` for large databases to reduce transfer time
- Avoid `?vacuum` on busy production nodes — it blocks all writes
- Test restores regularly — a backup is only as good as its restore
- For point-in-time recovery, combine backups with CDC streaming

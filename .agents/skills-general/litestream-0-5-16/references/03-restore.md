# Restore

Table of contents:
- [Restore mechanics](#restore-mechanics)
- [Command reference](#command-reference)
- [Point-in-time restore](#point-in-time-restore)
- [Follow mode (read replica)](#follow-mode-read-replica)
- [v0.3.x backups](#v03x-backups)
- [Integrity checks](#integrity-checks)
- [JSON output](#json-output)
- [Typical workflows](#typical-workflows)

## Restore mechanics

`litestream restore` rebuilds a database from a replica:

1. **Plan** — `CalcRestorePlan` selects the minimal set of LTX files reaching the target (a level 9 snapshot covering the range plus WAL LTX files from the compaction levels above it).
2. **Download** — files are fetched in parallel (`-parallelism`, default 8).
3. **Apply** — files are applied to a fresh database file; the output path must not exist beforehand (unless `-force`).
4. **Verify** — optional post-restore `PRAGMA integrity_check` (`-integrity-check`).

Only the S3 backend (and thus S3-compatible replicas) implements the v0.3.x fallback; other backends speak LTX only.

## Command reference

```
litestream restore [arguments] DB_PATH
litestream restore [arguments] REPLICA_URL
```

| Flag | Default | Purpose |
|---|---|---|
| `-o PATH` | original DB path | Output path of the restored database |
| `-timestamp T` | latest | Restore to RFC 3339 time T |
| `-txid HEX` | highest | Restore to 16-hex TXID (inclusive) |
| `-f` | off | Follow mode (see below) |
| `-follow-interval D` | `1s` | Poll interval in follow mode |
| `-parallelism N` | 8 | Parallel WAL downloads |
| `-dry-run` | off | Print the restore plan, write nothing |
| `-force` | off | Overwrite an existing output DB and sidecar files |
| `-integrity-check MODE` | `none` | `none`, `quick`, `full` |
| `-if-db-not-exists` | off | Exit 0 if the output DB already exists |
| `-if-replica-exists` | off | Exit 0 if no backups are found |
| `-json` | off | JSON summary; logs go to stderr |
| `-config PATH` | — | Config for DB_PATH mode (rejected with REPLICA_URL) |
| `-no-expand-env` | off | Disable env expansion in config |

`DB_PATH` is resolved against the config file; `REPLICA_URL` (`s3://...` etc.) is used directly.

## Point-in-time restore

```bash
# Everything up to (and including) 2025-01-01T00:00:00Z
litestream restore -timestamp 2025-01-01T00:00:00Z -o /tmp/app.db /var/lib/app.db

# Up to a specific transaction (inclusive)
litestream restore -txid 00000000000000ff -o /tmp/app.db /var/lib/app.db

# Preview first — which files would be fetched and to what TXID
litestream restore -dry-run -timestamp 2025-01-01T00:00:00Z -o /tmp/app.db s3://bkt/db
```

How far back you can reach is bounded by what still exists on the replica: L0 raw files are pruned after `l0-retention` (default 5m), then by L1/L2/L3 compaction intervals, and finally by `snapshot.retention` (default 24h). For long retention, raise `snapshot.retention` (and note the level 9 snapshot is the floor — you cannot restore earlier than the oldest snapshot's min TXID).

## Follow mode (read replica)

```bash
litestream restore -f -o /tmp/ro.db s3://my-bucket/db
```

- Restores the latest state, then polls every `-follow-interval` (default 1s) and applies new LTX changes — a continuously updated read replica with `tail -f` semantics.
- Mutually exclusive with `-txid` and `-timestamp`.
- On restart, the process resumes from a `<db>-txid` sidecar file (crash recovery). If retention pruned history below the saved TXID, resumption fails — delete the database and the `-txid` sidecar to re-restore.
- Open the followed database **read-only** in consumers; a writer will conflict with the follower.

## v0.3.x backups

v0.5.x can restore databases backed up by Litestream v0.3.x (the pre-LTX `generations/{id}/snapshots` + `generations/{id}/wal` layout). The S3 client implements `ReplicaClientV3`, and when no LTX-era data covers the target, restore automatically falls back to the v0.3 format.

Consequences:

- Upgrading a v0.3.x deployment to v0.5.x works: new replication starts in LTX format and old backups remain restorable.
- **Rollback is not possible** — v0.3.x cannot read LTX data.
- Follow mode never uses the v0.3 path (no incremental following in that format).

## Integrity checks

`-integrity-check` runs after the restore:

| Mode | Check |
|---|---|
| `none` (default) | nothing |
| `quick` | `PRAGMA quick_check` |
| `full` | `PRAGMA integrity_check` |

`full` is slow on large databases but is the only mode that verifies checksums across all pages.

## JSON output

`-json` prints a summary to stdout (restore logs go to stderr, so stdout stays parseable):

```json
{
  "db_path": "/var/lib/app.db",
  "replica": "file",
  "txid": "0000000000000004",
  "duration_ms": 125,
  "integrity_check": "quick"
}
```

With `-dry-run -json` the output is the plan instead:

```json
{
  "source": "file:///backups/app.db",
  "target_path": "/var/lib/app.db",
  "replica": "file",
  "min_txid": "0000000000000001",
  "max_txid": "0000000000000004",
  "files": [
    {
      "level": 9,
      "name": "0000000000000001-0000000000000004.ltx",
      "min_txid": "0000000000000001",
      "max_txid": "0000000000000004",
      "size": 8192,
      "timestamp": "2026-04-24T12:00:00Z"
    }
  ]
}
```

New fields may be added in future releases; consumers should ignore unknown fields.

## Typical workflows

```bash
# Disaster recovery on a new host
litestream restore /var/lib/app.db            # from the config's replica
# or without the old config
litestream restore -o /var/lib/app.db s3://my-bucket/app

# Idempotent bootstrap (skip when the DB already exists)
litestream restore -if-db-not-exists -if-replica-exists /var/lib/app.db

# Verify a backup without touching the production path
litestream restore -dry-run s3://my-bucket/app
litestream restore -o /tmp/verify.db -integrity-check full s3://my-bucket/app

# Pre-maintenance snapshot (cron)
litestream replicate -once -force-snapshot -enforce-retention -config /etc/litestream.yml
```

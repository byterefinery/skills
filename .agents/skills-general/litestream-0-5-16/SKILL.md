---
name: litestream-0-5-16
description: Operate Litestream 0.5.16, a standalone disaster recovery tool for SQLite that replicates WAL changes to S3, GCS, Azure Blob, Alibaba OSS, SFTP, WebDAV, NATS, or local files. Use for configuring replication (YAML config or one-liner mode), checking replication status, restoring databases (latest, point-in-time via -timestamp or -txid, follow mode), managing the daemon over the control socket (start, stop, sync, register, unregister, list, info), and using the litestream-vfs SQLite extension to read databases directly from replica storage with time travel. Covers LTX files and compaction levels, S3-compatible provider quirks, the MCP server, and JSON output. Use whenever the user mentions litestream, SQLite replication, SQLite backups, LTX, or point-in-time recovery for SQLite.
license: Apache-2.0
metadata:
  tags:
    - database
    - sqlite
    - backup
    - disaster-recovery
    - replication
---

# litestream 0.5.16

## Overview

Litestream is a standalone disaster recovery tool for SQLite. It runs as a background process, watches the database's WAL file, converts changes to immutable, checksummed LTX files, and replicates them to a replica (cloud storage or local path). It interacts with SQLite only through the SQLite API, so it will not corrupt the database. On first open it automatically enables WAL mode and creates a `_litestream_seq` bookkeeping table in the database.

v0.5.x is a rewrite around the LTX storage layer (`github.com/superfly/ltx`). Replication state is organized in compaction levels — raw L0 files are compacted upward, with full snapshots held at level 9 — which enables point-in-time restore, `-f` follow mode (a continuously updated read replica), and a SQLite VFS extension that reads databases straight from replica storage. The main binary is a pure-Go build (no CGO, `modernc.org/sqlite`); only the optional `litestream-vfs` extension requires CGO.

### Replica Layout

```
<replica-prefix>/
├── ltx/0000/    # L0 raw LTX files (l0-retention, default 5m)
├── ltx/0001/    # L1 compaction (default 30s)
├── ltx/0002/    # L2 compaction (default 5m)
├── ltx/0003/    # L3 compaction (default 1h)
└── ltx/0009/    # level 9 full snapshots (default 24h interval, 24h retention)
```

LTX files are named `MIN-TXID-MAX-TXID.ltx` (16-hex-digit TXIDs) and are never modified after upload.

## Usage

### Install

```bash
# Binary — per-platform tarballs from the release page
# https://github.com/benbjohnson/litestream/releases/tag/v0.5.16

# Docker (default image is debian-slim with sqlite3 and litestream-vfs.so bundled)
docker run --rm -v app-db:/db -v app-config:/config:ro litestream/litestream \
  replicate -config /config/litestream.yml

# Build from source
go build -o dist/litestream ./cmd/litestream
```

### Quick Start

```bash
# One-liner — replicate a single database to a replica URL
litestream replicate /var/lib/app.db s3://my-bucket/app

# Config file mode (default /etc/litestream.yml, override with $LITESTREAM_CONFIG)
litestream replicate -config /etc/litestream.yml

# Inspect
litestream status
litestream ltx -level all /var/lib/app.db

# Restore latest to the original location
litestream restore /var/lib/app.db
```

### Minimal Config

```yaml
dbs:
  - path: /var/lib/app.db
    replica:
      url: s3://my-bucket/app

# Common overrides (global values act as defaults for every db/replica)
sync-interval: 1s
checkpoint-interval: 1m
snapshot:
  interval: 24h
  retention: 24h
levels:
  - interval: 30s   # L1
  - interval: 5m    # L2
  - interval: 1h    # L3
l0-retention: 5m
```

Environment variables in config values (`$VAR`, `$$` for a literal dollar, `$PID` for the process id) are expanded by default; disable with `-no-expand-env`. Full field reference in [01-configuration](references/01-configuration.md).

### Replicate Options

| Flag | Purpose |
|---|---|
| `-config PATH` | Config file (default `/etc/litestream.yml`, or `$LITESTREAM_CONFIG`) |
| `-exec CMD` | Run a subcommand; Litestream exits when the child exits |
| `-once` | Sync once and exit (cron mode); combines with the two flags below |
| `-force-snapshot` | Force a snapshot on all databases (requires `-once`) |
| `-enforce-retention` | Enforce snapshot retention (requires `-once`) |
| `-log-level LEVEL` | trace, debug, info, warn, error (overrides config) |
| `-restore-if-db-not-exists` | Restore from replica on start when the DB file is missing |
| `-no-expand-env` | Disable env var expansion in the config |

### Runtime Control (daemon socket)

`start`, `stop`, `sync`, `register`, `unregister`, `list`, and `info` operate on a running daemon through a Unix socket. Enable it in the daemon config first:

```yaml
socket:
  enabled: true
  path: /var/run/litestream.sock   # default, permissions 0600
```

```bash
litestream register /new/app.db -replica s3://my-bucket/app  # add a db at runtime
litestream start /new/app.db
litestream stop /old/app.db        # always waits for shutdown + final sync
litestream unregister /old/app.db -dry-run
litestream sync /var/lib/app.db -wait   # block until replicated remotely
litestream list -json
litestream info -json
```

### Status & LTX Inspection

```bash
litestream status [db-path]        # status, local TXID, WAL size
litestream ltx [db-path|replica-url]  # -level 0|1|...|9|all (default 0), -json
litestream databases               # databases from the config file
litestream version
```

`restore` and `ltx` accept either a database path from the config or a bare replica URL (e.g. `s3://bucket/prefix`). With a URL, `-config` is rejected — the replica client is built from the URL and its credentials alone.

### Restore

```bash
litestream restore /var/lib/app.db                          # latest, in place
litestream restore -o /tmp/app.db s3://my-bucket/app        # from replica URL
litestream restore -timestamp 2025-01-01T00:00:00Z /var/lib/app.db
litestream restore -txid 00000000000000ff /var/lib/app.db
litestream restore -dry-run -o /tmp/app.db s3://my-bucket/app
litestream restore -f -o /tmp/ro.db s3://my-bucket/app      # follow mode
```

| Flag | Purpose |
|---|---|
| `-o PATH` | Output path (default the original DB path) |
| `-timestamp T` | Restore to time T (RFC 3339); default latest |
| `-txid HEX` | Restore to TXID (inclusive); default highest |
| `-f` | Follow mode — keep applying new changes like `tail -f`; not with `-txid`/`-timestamp` |
| `-follow-interval D` | Follow poll interval (default 1s) |
| `-parallelism N` | Parallel WAL file downloads (default 8) |
| `-dry-run` | Print the restore plan without writing |
| `-force` | Overwrite an existing output DB and sidecar files |
| `-integrity-check MODE` | Post-restore check, none (default), quick, full |
| `-if-db-not-exists` | Exit 0 when the output DB already exists |
| `-if-replica-exists` | Exit 0 when no backups are found |
| `-json` | JSON summary (logs go to stderr, stdout stays parseable) |

Follow mode writes a `<db>-txid` sidecar for crash recovery; open the followed database read-only in consumers. Details and v0.3.x restore behavior in [03-restore](references/03-restore.md).

### MCP Server

Set `mcp-addr` in the config to expose a Streamable HTTP MCP server with the tools `litestream_databases`, `litestream_info`, `litestream_restore`, `litestream_version`, `litestream_ltx`, `litestream_status`, and `litestream_reset` (each wraps the matching CLI command with the daemon's config path).

### Directory Watching

A db entry can manage a whole directory of SQLite files instead of one path:

```yaml
dbs:
  - dir: /var/lib/data
    pattern: "*.db"
    recursive: true
    watch: true        # auto-register/forget dbs as files appear/disappear
    replica:
      url: s3://my-bucket/data
```

## Gotchas

- **age encryption is not supported in v0.5.x** — setting `age.identities` or `age.recipients` makes the CLI refuse to start. It was removed in the LTX rewrite (issue #790); use v0.3.x if you need at-rest encryption, or rely on backend encryption (SSE-KMS, SSE-C, SFTP host key, ...).
- **The 1 GB lock page is always skipped** — SQLite reserves a page at byte offset 0x40000000 (pgno 262145 for 4 KB pages, 131073 for 8 KB, 65537 for 16 KB, 32769 for 32 KB). It never appears in LTX files or restores.
- **LTX files are immutable** — recovery from a corrupted/missing LTX file is `litestream reset <db>` (clears local LTX state, forces a fresh snapshot on next sync; the DB file is untouched) or `auto-recover: true` on the replica, which does the reset automatically on LTX errors (off by default to avoid silent data loss).
- **Runtime control requires the socket** — `start`/`stop`/`sync`/`register`/`unregister`/`list`/`info` need `socket.enabled: true` on the daemon; without it, edit the config and restart.
- **v0.5.x restores v0.3.x backups, but not the reverse** — when no LTX-era data exists, the S3 backend automatically falls back to the legacy `generations/{id}/snapshots|wal` layout. v0.3.x cannot read LTX data, so once you replicate with v0.5.x you cannot roll back to v0.3.x.
- **`-config` and bare replica URLs are mutually exclusive** — passing `scheme://...` to `restore`/`ltx` builds the replica client from the URL only; drop `-config`.
- **`-once` is cron mode, not a daemon** — it syncs once and exits; `-force-snapshot` and `-enforce-retention` require `-once`. `-exec CMD` instead keeps Litestream alive for the lifetime of the child process.
- **S3-compatible providers need provider-specific settings** — R2, B2, DigitalOcean Spaces, MinIO, Hetzner, Tigris, Supabase and others differ in signing and path style. Litestream auto-detects known endpoint patterns and applies defaults, but verify against [02-storage-backends](references/02-storage-backends.md).
- **`l0-retention` defaults to only 5 minutes** — raw L0 files are pruned quickly; how far back point-in-time restore or VFS time travel can reach is bounded by L1+ compaction and snapshots, not L0.
- **`replicas:` (list) is deprecated in favor of `replica:` (single)** — v0.5.x replicates each database to exactly one destination.
- **The `wal` command is deprecated** — it warns and runs `litestream ltx` instead.
- **Level 9 is the snapshot level, not a compaction level** — the `levels` config covers L1..L8 only (L0 must have no interval; a level cannot exceed 8); level 9 is driven by `snapshot.interval` and `snapshot.retention`.
- **Env expansion in config is on by default** — `$HOME/db` is expanded at load time; escape with `$$` or pass `-no-expand-env`.
- **The restore output path must not exist** — `restore` fails if the target is present unless `-force` is used (follow mode resumes from the `-txid` sidecar instead).
- **Follow mode crash recovery has a horizon** — if retention pruned the history below the saved TXID, resumption fails and the database plus `-txid` file must be deleted to re-restore.
- **`heartbeat-interval` must be at least 1 minute** (default 5) — set `heartbeat-url` to GET-ping an endpoint such as a dead man's switch.
- **Docker images differ** — the default debian-slim image bundles sqlite3 and `litestream-vfs.so` at `/usr/local/lib/litestream-vfs.so`; the hardened scratch variant is static and has no VFS extension or sqlite3.
- **WAL mode is enforced, not optional** — Litestream runs `PRAGMA journal_mode = wal` and creates `_litestream_seq` on open; a database that cannot be switched to WAL (e.g. read-only mount) will fail to replicate.

## References

- [01-configuration](references/01-configuration.md) — Complete YAML config reference, all fields with defaults, env vars
- [02-storage-backends](references/02-storage-backends.md) — Replica URL schemes, S3 query parameters, provider compatibility, credentials
- [03-restore](references/03-restore.md) — Restore workflows, point-in-time, follow mode, v0.3.x restore, JSON contract
- [04-vfs-extension](references/04-vfs-extension.md) — litestream-vfs, direct cloud reads, SQL functions, time travel, write mode
- [05-ltx-format](references/05-ltx-format.md) — LTX file structure, naming, checksums, compaction levels
- [06-operations](references/06-operations.md) — Daemon socket endpoints, MCP server, JSON output, metrics, heartbeat, systemd, Docker

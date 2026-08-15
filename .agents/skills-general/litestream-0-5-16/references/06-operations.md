# Operations

Table of contents:
- [Daemon control socket](#daemon-control-socket)
- [MCP server](#mcp-server)
- [JSON output contract](#json-output-contract)
- [Metrics](#metrics)
- [Heartbeat](#heartbeat)
- [Reset and auto-recover](#reset-and-auto-recover)
- [systemd](#systemd)
- [Docker](#docker)
- [Cron-style one-shot replication](#cron-style-one-shot-replication)
- [Debugging](#debugging)

## Daemon control socket

Runtime commands (`start`, `stop`, `sync`, `register`, `unregister`, `list`, `info`) talk HTTP over a Unix socket exposed by a running `replicate` daemon. Enable with:

```yaml
socket:
  enabled: true            # default false
  path: /var/run/litestream.sock
  permissions: 0600
```

Endpoints (used by the CLI; all requests are JSON):

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/register` | Add a database at runtime (`path`, `replica_url`) |
| `POST` | `/unregister` | Remove a database (`path`, optional `timeout`) |
| `POST` | `/start` | Start replication for a database |
| `POST` | `/stop` | Stop replication (waits for shutdown + final sync) |
| `POST` | `/sync` | Force a sync (optionally wait) |
| `GET` | `/list` | List managed databases |
| `GET` | `/info` | Version, PID, uptime, database count |
| `GET` | `/txid?path=` | Current TXID of a database |
| `GET` | `/debug/pprof/*` | Go pprof endpoints |

CLI commands accept `-socket PATH` (default `/var/run/litestream.sock`) and `-timeout SECONDS` (default 30 for control ops, 10 for `list`/`info`), plus `-json`.

Runtime `register` takes exactly one replica: `litestream register <db> -replica <url>`. Runtime `unregister` supports `-dry-run`. Runtime `sync` supports `-wait` (block until remote replication completes).

## MCP server

Set `mcp-addr` (host:port) in the config and the daemon serves a Streamable HTTP MCP server. Tools (each wraps the corresponding CLI command using the daemon's config path):

| Tool | Wraps |
|---|---|
| `litestream_databases` | `databases` |
| `litestream_info` | `info` / `version` |
| `litestream_restore` | `restore` |
| `litestream_ltx` | `ltx` |
| `litestream_status` | `status` |
| `litestream_version` | `version` |
| `litestream_reset` | `reset` |

## JSON output contract

Commands accepting `-json` write a single JSON document to stdout; errors go to stderr with a non-zero exit. New fields may appear in later releases — ignore unknown fields.

| Command | Shape |
|---|---|
| `databases -json` | array of `{path, replica}` |
| `info -json` | `{version, pid, uptime_seconds, started_at, database_count}` |
| `list -json` | `{databases: [{path, status, last_sync_at?}]}` — status e.g. `replicating`, `open`, `stopped` |
| `ltx -json` | array of `{level, min_txid, max_txid, size, timestamp}` |
| `status -json` | array of `{database, status, local_txid, wal_size}` — status: `ok`, `not initialized`, `no database`, `error` |
| `restore -json` | `{db_path, replica, txid, duration_ms, integrity_check}` (with `-dry-run`: the plan — `source`, `target_path`, `replica`, `min_txid`, `max_txid`, `files[]`) |
| `start`/`stop`/`sync`/`register`/`unregister` `-json` | completion state; `already_<state>` (e.g. `already_registered`) when the requested state already holds |

## Metrics

```yaml
addr: 127.0.0.1:9090
```

Serves Prometheus metrics at `http://<addr>/metrics` (a port is required; an empty host binds localhost).

## Heartbeat

```yaml
heartbeat-url: https://heartbeat.example.com/ping/my-host
heartbeat-interval: 5m     # minimum 1m, request timeout 30s
```

Periodically GETs the URL — wire it to a dead man's switch to alert when replication is down. The interval is clamped to at least 1 minute and the URL must be HTTP/HTTPS.

## Reset and auto-recover

- `litestream reset <db-path>` clears local LTX state (metadata directory), forcing a fresh snapshot on the next sync. The database file itself is not modified. Use after corrupted/missing LTX files.
- `auto-recover: true` on a replica performs the equivalent reset automatically when LTX errors are detected. It is off by default because automatic resets can hide underlying storage problems.

## systemd

Shipped unit (`etc/litestream.service`):

```ini
[Unit]
Description=Litestream

[Service]
Restart=always
ExecStart=/usr/bin/litestream replicate

[Install]
WantedBy=multi-user.target
```

The default config path `/etc/litestream.yml` is used unless `LITESTREAM_CONFIG` or `-config` says otherwise.

## Docker

Image `litestream/litestream` (tag with the version, e.g. `:0.5.16`), entrypoint `/usr/local/bin/litestream`:

```bash
# daemon mode
docker run -d --name litestream \
  -v app-db:/var/lib/app -v app-config:/config:ro \
  litestream/litestream:0.5.16 replicate -config /config/litestream.yml

# one-shot restore into a volume
docker run --rm -v app-db:/var/lib/app litestream/litestream:0.5.16 \
  restore -o /var/lib/app/app.db s3://my-bucket/app
```

- **Default image** (debian-slim): includes `sqlite3` and `litestream-vfs.so` at `/usr/local/lib/litestream-vfs.so` — convenient for restore-and-query pipelines.
- **Hardened image** (scratch-based): static binary only, nonroot user, no sqlite3 and no VFS extension.
- A CA bundle is embedded in the build, so no certificate setup is needed for TLS replicas.

## Cron-style one-shot replication

```bash
# nightly full snapshot + retention enforcement
litestream replicate -once -force-snapshot -enforce-retention -config /etc/litestream.yml
```

`-once` performs a single sync of all configured databases and exits (non-zero on failure) — the building block for cron jobs and CI backup steps. `-force-snapshot` and `-enforce-retention` are only valid with `-once`.

## Debugging

- Logs are structured (`slog`): text or json via `logging.type`, level via `logging.level` or `-log-level`, `logging.stderr: true` to keep stdout clean for JSON consumers.
- `LITESTREAM_DEBUG=1` enables verbose S3 SDK logging for provider issues.
- Check replication health with `litestream status` (status, local TXID, WAL size) and `litestream ltx -level all` (what is actually on the replica).
- The daemon exposes pprof over the control socket (`/debug/pprof/*`) for goroutine/memory inspection.

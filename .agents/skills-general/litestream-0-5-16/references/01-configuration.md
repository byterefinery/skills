# Configuration Reference

Table of contents:
- [Locations and env expansion](#locations-and-env-expansion)
- [Top-level keys](#top-level-keys)
- [Global defaults](#global-defaults)
- [Database entry (dbs)](#database-entry-dbs)
- [Replica entry](#replica-entry)
- [Backend-specific settings](#backend-specific-settings)
- [Environment variables](#environment-variables)
- [Logging](#logging)

## Locations and env expansion

| Source | Value |
|---|---|
| Default path (non-Windows) | `/etc/litestream.yml` |
| Default path (Windows) | `C:\Litestream\litestream.yml` |
| Env override | `LITESTREAM_CONFIG` |
| CLI override | `-config PATH` (every command) |

Config values support `$VAR` expansion at load time. `$$` produces a literal `$`, and `$PID` is the daemon's process id. Disable expansion with `-no-expand-env` on any command.

## Top-level keys

| Key | Type | Default | Purpose |
|---|---|---|---|
| `dbs` | list of DB entries | — | Databases to manage (see below) |
| `socket.enabled` | bool | `false` | Enable the runtime control socket |
| `socket.path` | path | `/var/run/litestream.sock` | Socket location |
| `socket.permissions` | octal | `0600` | Socket file mode |
| `levels` | list of `{interval}` | L1 30s, L2 5m, L3 1h | Compaction levels L1..L8 (L0 always interval 0; max level 8) |
| `snapshot.interval` | duration | `24h` | Full snapshot frequency (level 9) |
| `snapshot.retention` | duration | `24h` | How long to keep level 9 snapshots |
| `l0-retention` | duration | `5m` | How long raw L0 files are kept on the replica |
| `l0-retention-check-interval` | duration | `15s` | How often L0 retention is enforced |
| `validation.interval` | duration | `0` (off) | Periodic local-vs-remote position validation |
| `verify-compaction` | bool | `false` | Log warnings on TXID gaps/overlaps after compaction |
| `retention.enabled` | bool | `true` | Enable replica retention pruning |
| `heartbeat-url` | URL | — | GET-ping endpoint (dead man's switch) |
| `heartbeat-interval` | duration | `5m` | Heartbeat cadence (minimum `1m`) |
| `addr` | host:port | — | Serve Prometheus metrics on `http://<addr>/metrics` (port required; empty host binds localhost) |
| `mcp-addr` | host:port | — | Serve the MCP Streamable HTTP server |
| `exec` | string | — | Subcommand to run; Litestream exits when it exits |
| `shutdown-sync-timeout` | duration | `30s` | Max time to keep syncing during shutdown |
| `shutdown-sync-interval` | duration | `500ms` | Retry cadence during shutdown sync |
| `logging` | object | `info`/text | See [Logging](#logging) |
| (all replica settings) | — | — | The replica settings below also work at the top level as defaults for every replica |

All durations accept Go duration syntax (`30s`, `5m`, `1h`, `24h`). All intervals must be > 0 where applicable; the CLI validates and names the offending key (e.g. `snapshot.interval: snapshot interval must be greater than 0`).

## Global defaults

| Setting | Default |
|---|---|
| `sync-interval` | `1s` |
| `monitor-interval` | `1s` |
| `checkpoint-interval` | `1m` |
| `busy-timeout` | `1s` |
| `snapshot.interval` | `24h` |
| `snapshot.retention` | `24h` |
| `l0-retention` | `5m` |
| `l0-retention-check-interval` | `15s` |
| `heartbeat-interval` | `5m` (min `1m`, request timeout 30s) |
| compaction levels | L1 `30s`, L2 `5m`, L3 `1h` |
| `shutdown-sync-timeout` | `30s` |
| `shutdown-sync-interval` | `500ms` |
| `socket.path` | `/var/run/litestream.sock` |
| `socket.permissions` | `0600` |
| restore parallelism | 8 |
| follow interval | `1s` |

## Database entry (`dbs`)

| Key | Type | Purpose |
|---|---|---|
| `path` | path | SQLite database file to replicate |
| `dir` | path | Directory to scan for databases (mutual use with `path`) |
| `pattern` | glob | Files to match in `dir` (e.g. `*.db`, `*.sqlite`) |
| `recursive` | bool | Scan `dir` subdirectories |
| `watch` | bool | Dynamically register/unregister dbs as files appear/disappear (fsnotify, 250ms debounce) |
| `meta-path` / `meta-dir` | path | Where local LTX state lives (defaults derived from the DB path) |
| `monitor-interval` | duration | WAL poll interval (default `1s`) |
| `checkpoint-interval` | duration | Checkpoint cadence (default `1m`) |
| `busy-timeout` | duration | SQLite busy timeout (default `1s`) |
| `min-checkpoint-page-count` | int | Skip checkpoints below this many dirty pages |
| `truncate-page-n` | int | Truncate checkpoint page bound |
| `max-sync-wal-bytes` | int | Cap bytes of WAL processed per sync |
| `restore-if-db-not-exists` | bool | Restore from replica on start when the DB file is missing |
| `snapshot` | object | Per-db `interval`/`retention` overrides |
| `replica` | object | The single replica destination |
| `replicas` | list | **Deprecated** — use `replica` |

A db entry has either `path` (single database) or `dir` (+ `pattern`/`recursive`/`watch`, directory mode).

## Replica entry

| Key | Type | Purpose |
|---|---|---|
| `url` | URL | Replica destination (`s3://bucket/prefix`, `gs://...`, `abs://...`, `oss://...`, `sftp://...`, `webdav://...`, `webdavs://...`, `nats://...`, or a local path) |
| `path` | path | Same as `url` but must not contain a scheme (URLs in `path` are rejected) |
| `type` | string | Explicit backend type (`file`, `s3`, ...); inferred from the URL scheme otherwise |
| `name` | string | **Deprecated** |
| `sync-interval` | duration | Replication cadence (default `1s`) |
| `validation-interval` | duration | Per-replica integrity validation cadence (0 disables) |
| `max-sync-ltx-files` | int | Max L0 files uploaded per sync run (0 = all pending) |
| `auto-recover` | bool | Auto-reset local state on LTX errors (default `false`) |
| backend settings | — | See [Backend-specific settings](#backend-specific-settings) |

## Backend-specific settings

### S3 (and S3-compatible)

`access-key-id`, `secret-access-key`, `region`, `bucket`, `endpoint`, `force-path-style`, `sign-payload`, `require-content-md5`, `skip-verify`, `storage-class`, `part-size` (default 5 MB), `concurrency` (default 5), `sse-customer-algorithm`, `sse-customer-key`, `sse-customer-key-path`, `sse-kms-key-id`. Every one of these is also accepted as an S3 URL query parameter (camelCase or hyphenated), which is the usual way to configure S3-compatible endpoints. Details in [02-storage-backends](02-storage-backends.md).

### ABS (Azure Blob)

`account-name`, `account-key`, `sas-token`. Auth priority: SAS token > account key > default credential chain (managed identity).

### SFTP

`host`, `user`, `password`, `key-path`, `concurrent-writes`, `host-key`. The SSH host key (`host-key`) is strongly recommended — take it from the server's `/etc/ssh/ssh_host_*.pub` or `ssh-keyscan`.

### WebDAV

`webdav-url`, `webdav-username`, `webdav-password`. `webdav://` for HTTP, `webdavs://` for HTTPS.

### NATS JetStream

`jwt`, `seed`, `creds`, `nkey`, `username`, `token`, `tls`, `root-cas`, `client-cert`, `client-key`, `max-reconnects`, `reconnect-wait`, `timeout`.

### Age (NOT functional in v0.5.x)

`age.identities` / `age.recipients` are parsed but **reject startup** — age encryption was removed in the LTX rewrite (issue #790). Do not configure them.

## Environment variables

| Variable | Purpose |
|---|---|
| `LITESTREAM_CONFIG` | Default config path |
| `LOG_LEVEL` | Log level override (also `logging.level` in config) |
| `LITESTREAM_DEBUG=1` | Verbose logging for S3 provider troubleshooting |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3 credentials (standard chain) |
| `LITESTREAM_ACCESS_KEY_ID` / `LITESTREAM_SECRET_ACCESS_KEY` | S3 credentials (litestream-specific fallback) |
| `LITESTREAM_S3_ENDPOINT` | S3 endpoint override |
| `LITESTREAM_S3_DEBUG` | S3 SDK debug mode (signing, request, response, ...) |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCS application default credentials |
| `LITESTREAM_AZURE_ACCOUNT_KEY` / `LITESTREAM_AZURE_SAS_TOKEN` | ABS credentials |
| `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_TENANT_ID` | ABS managed identity chain |

## Logging

```yaml
logging:
  level: info      # trace, debug, info, warn, error
  type: text       # text or json
  stderr: false    # write to stderr instead of stdout
  source: false    # include source file:line in log records
```

`-log-level` on `replicate` overrides `logging.level`.

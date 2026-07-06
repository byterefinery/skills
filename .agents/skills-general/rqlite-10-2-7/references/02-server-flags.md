# Server Flags Reference

All flags are passed to `rqlited`. The data directory is the final positional argument.

```bash
rqlited [flags] <data-directory>
```

## Network & Addressing

| Flag | Default | Description |
|---|---|---|
| `-http-addr` | `localhost:4001` | HTTP API bind address |
| `-http-adv-addr` | same as bind | Advertised HTTP address (use in containers/K8s) |
| `-raft-addr` | `localhost:4002` | Raft TCP bind address |
| `-raft-adv-addr` | same as bind | Advertised Raft address (use in containers/K8s) |
| `-node-id` | advertised Raft addr | Unique node identifier |
| `-http-allow-origin` | — | CORS `Access-Control-Allow-Origin` value |

**Important:** HTTP and Raft must use different ports. Advertised addresses must be routable (not `0.0.0.0`).

## Clustering & Discovery

| Flag | Default | Description |
|---|---|---|
| `-join` | — | Comma-separated `host:port` list to join existing cluster |
| `-join-attempts` | 5 | Number of join attempts |
| `-join-interval` | 3s | Delay between join attempts |
| `-join-as` | — | Auth username for joining (anonymous if unset) |
| `-bootstrap-expect` | 0 | Min nodes needed to form cluster (for simultaneous startup) |
| `-bootstrap-expect-timeout` | 120s | Max time waiting for bootstrap |
| `-disco-mode` | — | Discovery mode: `consul-kv`, `etcd-kv`, `dns`, `dns-srv` |
| `-disco-key` | `rqlite` | Key prefix for KV discovery services |
| `-disco-config` | — | Discovery config string or path to config file |
| `-cluster-connect-timeout` | 30s | Timeout for initial inter-node connections |

**Mutually exclusive:** `-join` and `-disco-mode` cannot be used together.

## TLS / HTTPS

### HTTP API TLS

| Flag | Default | Description |
|---|---|---|
| `-http-ca-cert` | — | CA certificate for HTTPS |
| `-http-cert` | — | Server X.509 certificate (must pair with `-http-key`) |
| `-http-key` | — | Server X.509 private key (must pair with `-http-cert`) |
| `-http-verify-client` | false | Enable mTLS for HTTP API |
| `-http-verify-common-name` | — | Required Common Name on client certs (requires `-http-verify-client`) |

### Node-to-Node TLS

| Flag | Default | Description |
|---|---|---|
| `-node-ca-cert` | — | CA certificate for inter-node encryption |
| `-node-cert` | — | Node X.509 certificate (must pair with `-node-key`) |
| `-node-key` | — | Node X.509 private key (must pair with `-node-cert`) |
| `-node-no-verify` | false | Skip all certificate verification (insecure) |
| `-node-verify-client` | false | Enable mTLS between nodes |
| `-node-verify-server-name` | — | Hostname to verify on peer certificates |
| `-node-verify-common-name` | — | Required Common Name on peer certs (requires `-node-verify-client`) |
| `-compress-snap-transport` | false | Compress snapshots during transfer (zstd) |

## Authentication

| Flag | Default | Description |
|---|---|---|
| `-auth` | — | Path to JSON credentials file (disables anonymous access when set) |

See [04-security](04-security.md) for credential file format.

## SQLite Configuration

| Flag | Default | Description |
|---|---|---|
| `-fk` | false | Enable foreign key constraints |
| `-db-max-ro-conns` | 256 | Max read-only database connections |
| `-auto-vacuum-int` | 0s (disabled) | Interval between automatic VACUUM |
| `-auto-optimize-int` | 24h | Interval between `PRAGMA optimize` (set to 0h to disable) |
| `-extensions-path` | — | Comma-separated paths to extension dirs, zipfiles, or tar.gz |

## Raft Configuration

| Flag | Default | Description |
|---|---|---|
| `-raft-log-level` | WARN | Raft log level: DEBUG, INFO, WARN, ERROR |
| `-raft-non-voter` | false | Run as read-only non-voting node |
| `-raft-snap` | 8192 | Log entries before snapshot triggers |
| `-raft-snap-wal-size` | 4194304 (4MB) | WAL size threshold for snapshot (0 to disable) |
| `-raft-snap-int` | 10s | Snapshot threshold check interval |
| `-raft-leader-lease-timeout` | 0s (default) | Leader lease timeout |
| `-raft-heartbeat-timeout` | 1s | Heartbeat interval |
| `-raft-commit-timeout` | 50ms | Commit timeout |
| `-raft-election-timeout` | 1s | Election timeout |
| `-raft-apply-timeout` | 10s | Apply timeout |
| `-raft-remove-shutdown` | false | Shutdown Raft when node is removed from cluster |
| `-raft-cluster-remove-shutdown` | false | Self-remove on graceful shutdown |
| `-raft-shutdown-stepdown` | true | Leader steps down before shutdown (default enabled) |
| `-raft-reap-node-timeout` | 0h (disabled) | Auto-remove unreachable voting nodes after timeout |
| `-raft-reap-read-only-node-timeout` | 0h (disabled) | Auto-remove unreachable non-voting nodes after timeout |

## Queued Writes

| Flag | Default | Description |
|---|---|---|
| `-write-queue-capacity` | 1024 | Max queued writes before rejecting |
| `-write-queue-batch-size` | 128 | Statements per batch flush |
| `-write-queue-timeout` | 50ms | Max wait before flushing batch |
| `-write-queue-tx` | false | Wrap each batch in a transaction |

## Change Data Capture

| Flag | Default | Description |
|---|---|---|
| `-cdc-config` | — | HTTP endpoint URL or path to CDC JSON config file |

CDC cannot be enabled on non-voting nodes (`-raft-non-voter`). See [06-cdc](06-cdc.md).

## Auto Backup / Restore

| Flag | Default | Description |
|---|---|---|
| `-auto-backup` | — | Path to auto-backup config file (S3, GCS, MinIO, local) |
| `-auto-restore` | — | Path to auto-restore config file (restore from cloud on startup) |

Auto-restore cannot be combined with `-join`.

## Profiling

| Flag | Default | Description |
|---|---|---|
| `-cpu-profile` | — | Write CPU profile to file |
| `-mem-profile` | — | Write memory profile to file |
| `-trace-profile` | — | Write execution trace to file |

## Other

| Flag | Default | Description |
|---|---|---|
| `-version` | — | Print version and exit |

## Docker Environment Variables

When using `rqlite/rqlite` Docker image, these environment variables override defaults:

| Variable | Maps To | Default |
|---|---|---|
| `HTTP_ADDR` | `-http-addr` | `0.0.0.0:4001` |
| `HTTP_ADV_ADDR` | `-http-adv-addr` | hostname:4001 |
| `RAFT_ADDR` | `-raft-addr` | `0.0.0.0:4002` |
| `RAFT_ADV_ADDR` | `-raft-adv-addr` | hostname:4002 |
| `NODE_ID` | `-node-id` | hostname |
| `DATA_DIR` | data directory | `/rqlite/file/data` |
| `SQLITE_EXTENSIONS` | extension names from bundled set | — |
| `CUSTOM_SQLITE_EXTENSIONS_PATH` | custom extension path | — |
| `ENABLE_FK` | `-fk` | — |
| `START_DELAY` | startup delay (seconds, for K8s DNS) | 5 (auto in K8s) |

Bundled extensions available via `SQLITE_EXTENSIONS`: `sqlite-vec`, `sqlean`, `sqliteai`, and others built from source.

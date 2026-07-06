---
name: rqlite-10-2-7
description: >
  Operate rqlite 10.2.7 — distributed SQLite database with Raft consensus.
  Use for deploying, configuring, querying, backing up, and managing rqlite clusters.
  Covers rqlited server flags, HTTP API (/db/execute, /db/query, /db/request),
  CLI (.status, .backup, .nodes), clustering (join, DNS, Consul, etcd, Kubernetes),
  TLS/mTLS auth, queued writes, CDC, consistency levels, SQLite extensions,
  and the built-in web console. Use whenever the user mentions rqlite,
  distributed SQLite, Raft database, or needs a lightweight fault-tolerant
  relational store.
metadata:
  tags:
    - database
    - distributed-systems
    - sqlite
    - raft
---

# rqlite 10.2.7

## Overview

rqlite is a lightweight, fault-tolerant, distributed relational database built on SQLite with Raft consensus. It provides full SQL support (including FTS5, JSON1) in a single binary with no external dependencies. The architecture is:

- **SQLite** — storage engine (WAL mode, `SYNCHRONOUS=off`; Raft provides durability)
- **Raft** — consensus via `hashicorp/raft` for replication and leader election
- **HTTP API** — RESTful interface on port 4001 (default)
- **Raft TCP** — inter-node communication on port 4002 (default)
- **Console** — built-in web UI at `/console/` for queries, schema management, and cluster monitoring

Three binaries are built: `rqlited` (server), `rqlite` (CLI client), `rqbench` (benchmarking).

### Data Flow

- **Writes**: HTTP → Raft consensus → FSM applies to SQLite → response
- **Reads**: HTTP → consistency check → query SQLite → response

Quorum requires `(N/2)+1` nodes: 3-node cluster tolerates 1 failure, 5-node tolerates 2.

### v10 Snapshot Architecture

v10 introduced a non-blocking Snapshot Store: snapshotting on the Leader no longer blocks when streaming a pre-existing snapshot to a Follower. Snapshotting is canceled and retried later if a long-running read is active. CRC32 checksumming (Castagnoli polynomial) is used comprehensively across snapshots, WAL files, and the snapshot store to detect filesystem corruption.

## Usage

### Quick Start (Docker)

```bash
# Single node
docker run -d --name rqlite -p 4001:4001 -v rqlite:/rqlite/file rqlite/rqlite

# Query via HTTP
curl -XPOST 'localhost:4001/db/execute?pretty' \
  -H 'Content-Type: application/json' \
  -d '["CREATE TABLE foo (id INTEGER PRIMARY KEY, name TEXT)"]'

curl -G 'localhost:4001/db/query?pretty' --data-urlencode 'q=SELECT * FROM foo'
```

### Quick Start (Binary)

```bash
# Download binary from https://github.com/rqlite/rqlite/releases/tag/v10.2.7
mkdir -p /opt/rqlite && tar xzf rqlite_linux_amd64.tar.gz -C /opt/rqlite
/opt/rqlite/rqlited -http-addr 0.0.0.0:4001 -raft-addr 0.0.0.0:4002 /data/rqlite
```

### CLI Usage

```bash
# Connect to local node (default http://127.0.0.1:4001)
rqlite

# Connect to remote node
rqlite -H 10.0.0.1 -p 4001

# HTTPS with insecure skip
rqlite -s https -i -H 10.0.0.1 -p 4001

# With basic auth
rqlite -u admin:password -H 10.0.0.1 -p 4001

# Using RQLITE_HOST env var
RQLITE_HOST=https://10.0.0.1:4001 rqlite -i

# With fallback hosts
rqlite -H 10.0.0.1 -p 4001 -a 10.0.0.2:4001,10.0.0.3:4001
```

Inside the CLI, use dot commands:

| Command | Description |
|---|---|
| `.help` | List all commands |
| `.status` | Node status and diagnostics |
| `.nodes [all]` | Cluster topology; `all` includes non-voters |
| `.leader` | Current Raft leader |
| `.tables` / `.indexes` / `.schema` | Database introspection |
| `.backup FILE` | Hot backup to file |
| `.restore FILE` | Restore from SQLite file or SQL dump |
| `.boot FILE` | Boot node with SQLite file (single-node only) |
| `.dump FILE [TABLES]` | SQL text dump, optionally per-table |
| `.read FILE` | Execute SQL statements from file |
| `.consistency [level]` | Set/read consistency: none, weak, linearizable, strong |
| `.mode [column\|csv\|json\|line]` | Output format |
| `.timer [on\|off]` | Show query timing |
| `.changes [on\|off]` | Show last insert ID after writes |
| `.forcewrites [on\|off]` | Force all statements through `/db/execute` |
| `.blobarray [on\|off]` | Display BLOB data as byte arrays |
| `.remove NODEID` | Remove node from cluster |
| `.snapshot [TRAILING_LOGS]` | Trigger Raft snapshot |
| `.reap` | Reap old snapshots and checkpoint WALs |
| `.stepdown [NODEID]` | Leader stepdown, optionally to specific node |
| `.extensions` | Loaded SQLite extensions |
| `.sysdump FILE` | Dump system diagnostics to file |
| `.expvar` | Go runtime metrics |
| `.ready` | Node readiness status |
| `.show` | Display all current CLI settings |
| `.output FILE` | Redirect output to file (or stdout) |
| `.quit` / `.exit` | Exit the CLI |

### HTTP API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/db/execute` | POST | Write operations (INSERT, UPDATE, DELETE, CREATE) |
| `/db/query` | GET/POST | Read operations (SELECT) |
| `/db/request` | POST | Unified endpoint for reads and writes |
| `/db/backup` | GET | Hot backup (SQLite binary or SQL dump) |
| `/db/load` | POST | Load SQLite file or SQL dump into cluster |
| `/boot` | POST | Boot single node with SQLite file |
| `/status` | GET | Node status; use `?key=X` to filter |
| `/readyz` | GET | Readiness probe (200 = ready) |
| `/nodes` | GET | Cluster topology (`?nonvoters` includes read-only) |
| `/leader` | GET/POST | Get leader info or trigger stepdown |
| `/remove` | POST | Remove a node from cluster |
| `/snapshot` | POST | Trigger Raft snapshot (`?trailing_logs=N`) |
| `/reap` | POST | Reap old snapshots |
| `/db/sql` | POST | SQL analysis (EXPLAIN QUERY PLAN) |
| `/console/` | GET | Built-in web console application |
| `/licenses` | GET | Third-party license information |
| `/debug/vars` | GET | Go expvar runtime metrics |
| `/debug/pprof/...` | GET | Go pprof profiling endpoints |

### Execute Request

```bash
# Single statement
curl -XPOST 'http://localhost:4001/db/execute' \
  -H 'Content-Type: application/json' \
  -d '{"statements": [{"sql": "CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)"}]}'

# Multiple statements (atomic batch — single Raft entry)
curl -XPOST 'http://localhost:4001/db/execute?pretty' \
  -H 'Content-Type: application/json' \
  -d '[
    "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)",
    "INSERT INTO users VALUES(1, ''alice'')"
  ]'

# With transaction wrapping
curl -XPOST 'http://localhost:4001/db/execute?transaction' \
  -H 'Content-Type: application/json' -d '["UPDATE t SET v=1", "UPDATE t SET v=2"]'

# Queued writes (returns immediately, batched automatically — much higher throughput)
curl -XPOST 'http://localhost:4001/db/execute?queue' \
  -H 'Content-Type: application/json' -d '["INSERT INTO t VALUES(1)"]'

# With timing info
curl -XPOST 'http://localhost:4001/db/execute?timings' \
  -H 'Content-Type: application/json' -d '["SELECT * FROM t"]'

# Associative JSON output (column names as keys)
curl -XPOST 'http://localhost:4001/db/execute?associative' \
  -H 'Content-Type: application/json' -d '["SELECT * FROM t"]'

# Include Raft index in response
curl -XPOST 'http://localhost:4001/db/execute?raft_index' \
  -H 'Content-Type: application/json' -d '["INSERT INTO t VALUES(1)"]'
```

### Query Request

```bash
# Basic query (use GET with url-encoded q parameter)
curl -G 'http://localhost:4001/db/query?pretty' --data-urlencode 'q=SELECT * FROM t'

# With consistency level
curl -G 'http://localhost:4001/db/query?level=linearizable' --data-urlencode 'q=SELECT * FROM t'

# POST with JSON body
curl -XPOST 'http://localhost:4001/db/query' \
  -H 'Content-Type: application/json' \
  -d '{"queries": [{"sql": "SELECT * FROM t"}]}'

# With freshness bound (for level=none)
curl -G 'http://localhost:4001/db/query?level=none&freshness=5s' --data-urlencode 'q=SELECT * FROM t'

# Qualify columns with table names
curl -G 'http://localhost:4001/db/query?qualify_columns' --data-urlencode 'q=SELECT * FROM t JOIN u ON t.id=u.id'
```

### Read Consistency Levels

Set via `?level=` query parameter or `.consistency` CLI command:

| Level | Behavior | Use Case |
|---|---|---|
| `weak` (default) | Checks local leadership state; ~1s staleness possible | General purpose, best performance |
| `linearizable` | Verifies leadership via quorum heartbeat before read | When reads must be up-to-date |
| `none` | Direct local read, no leader check; use `?freshness=5s` to bound staleness | Maximum read throughput |
| `strong` | Read goes through Raft log (slowest) | Testing and debugging |

For `level=none`, use `?freshness=DURATION` to ensure the node has been leader within that window. Add `freshness_strict` for strict enforcement.

### Queued Writes

Append `?queue` to `/db/execute`. Returns immediately; writes are batched and applied asynchronously. Default queue: capacity 1024, batch size 128, timeout 50ms. Configure with `-write-queue-capacity`, `-write-queue-batch-size`, `-write-queue-timeout`, `-write-queue-tx`.

### Non-deterministic Functions

`RANDOM()` and `datetime('now')` are automatically rewritten before Raft log storage to ensure identical results across replicas. Disable rewriting with `?norwrandom` or `?norwtime`.

## Gotchas

- **HTTP and Raft addresses must use different ports** — binding both to the same port fails validation. Use 4001/4002 convention.
- **Advertised addresses must be routable** — `0.0.0.0` is valid for bind but not for advertised address. Use `-http-adv-addr` and `-raft-adv-addr` in containers/Kubernetes.
- **`/boot` only works on single-node setups** — it bypasses Raft. For clusters, use `/db/load` instead.
- **Non-voting nodes cannot use CDC** — Change Data Capture requires voting nodes only.
- **DNS/dns-srv discovery requires `-bootstrap-expect N`** — voting nodes using DNS discovery must specify expected cluster size.
- **`-join` and `-disco-mode` are mutually exclusive** — choose one clustering method.
- **Auto-restore cannot be combined with `-join`** — a node either boots from backup or joins existing cluster.
- **SQLite runs with `SYNCHRONOUS=off`** — durability comes from Raft fsync, not SQLite. Do not rely on SQLite-level durability guarantees.
- **`RANDOM()` and time functions are rewritten** — results may differ from standalone SQLite. Use `?norwrandom`/`?norwtime` if you need raw SQLite behavior.
- **Queued writes trade durability for throughput** — data is acknowledged before Raft commitment. A leader crash before commit could lose queued writes.
- **Foreign keys are disabled by default** — enable with `-fk` flag on `rqlited`.
- **mTLS requires both cert and key** — `-http-cert` and `-http-key` must be set together (same for node certs).
- **CDC only captures INSERT/UPDATE/DELETE** — DDL changes (CREATE, ALTER, DROP) are not captured.
- **Backup with `?vacuum` triggers VACUUM before backup** — this blocks writes during vacuum; use carefully on busy nodes.
- **Leader stepdown waits for new election by default** (`?wait=true`) — omit `wait` for immediate stepdown without waiting.
- **`-on-disk-path` was removed in v10** — it is no longer supported. Migrate by backing up, deploying v10, and restoring.
- **`-raft-timeout` was renamed to `-raft-heartbeat-timeout` in v10** — old flag name no longer works.
- **v10 is not backward-compatible with pre-v10 clusters** — you cannot join a v10 node to a v9 (or earlier) cluster. Upgrade existing cluster first.
- **Snapshot transfer compression must be consistent** — if `-compress-snap-transport` is set on any node, it must be set on all nodes in the cluster.

## References

- [01-http-api](references/01-http-api.md) — Full HTTP API reference with all query parameters and response formats
- [02-server-flags](references/02-server-flags.md) — Complete rqlited configuration flags reference
- [03-clustering](references/03-clustering.md) — Clustering setup: manual join, DNS, Consul, etcd, Kubernetes
- [04-security](references/04-security.md) — Authentication file format, TLS/mTLS configuration, permissions
- [05-backups](references/05-backups.md) — Backup strategies, auto-backup to S3/GCS/MinIO, restore procedures
- [06-cdc](references/06-cdc.md) — Change Data Capture configuration and event format
- [07-extensions](references/07-extensions.md) — Loading SQLite extensions (sqlite-vec, sqlean, sqliteai)

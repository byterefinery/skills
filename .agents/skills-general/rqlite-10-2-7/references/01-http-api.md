# HTTP API Reference

## Endpoints

### `/db/execute` — Write Operations

**Method:** POST
**Body:** JSON array of SQL strings or `{"statements": [{"sql": "...", "params": [...]}]}`

```json
{
  "statements": [
    {"sql": "INSERT INTO users VALUES(?, ?)", "params": [["1", "alice"]]},
    {"sql": "INSERT INTO users VALUES(1, 'bob')"}
  ]
}
```

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `pretty` | flag | — | Pretty-print JSON response |
| `timings` | flag | — | Include per-statement timing |
| `transaction` | flag | — | Wrap all statements in single transaction |
| `queue` | flag | — | Queued writes (async, higher throughput) |
| `level` | string | — | Consistency level for queued writes |
| `timeout` | duration | 30s | Request timeout |
| `retries` | int | 0 | Retry count on leader change |
| `redirect` | flag | — | Return 301 redirect to leader instead of proxying |
| `noparse` | flag | — | Skip SQL parsing (no rewrite of RANDOM/time) |
| `norwrandom` | flag | — | Disable RANDOM() rewriting |
| `norwtime` | flag | — | Disable time function rewriting |
| `associative` | flag | — | Return column names as JSON keys |
| `blob_array` | flag | — | Render BLOBs as byte arrays |
| `qualify_columns` | flag | — | Prefix columns with table name |
| `raft_index` | flag | — | Include Raft commit index in response |
| `db_timeout` | duration | — | Per-statement SQLite timeout |

**Response:**

```json
{
  "results": [
    {
      "rowsaffected": 1,
      "lastinsertid": 1,
      "rf_index": 42
    }
  ],
  "time": 0.003
}
```

### `/db/query` — Read Operations

**Method:** GET (with `?q=`) or POST (JSON body)

```json
{"queries": [{"sql": "SELECT * FROM t WHERE id > ?", "params": [["1"]]}]}
```

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `q` | string | — | SQL query (GET only) |
| `level` | string | `weak` | Consistency: none, weak, linearizable, strong |
| `freshness` | duration | — | Max staleness for `level=none` |
| `freshness_strict` | flag | — | Strict freshness enforcement |
| `linearizable_timeout` | duration | 5s | Timeout for linearizable reads |
| `pretty` | flag | — | Pretty-print JSON |
| `timings` | flag | — | Include timing info |
| `associative` | flag | — | Column names as JSON keys |
| `blob_array` | flag | — | BLOBs as byte arrays |
| `qualify_columns` | flag | — | Prefix columns with table name |
| `timeout` | duration | 30s | Request timeout |
| `retries` | int | 0 | Retry count |
| `redirect` | flag | — | Redirect to leader |
| `db_timeout` | duration | — | Per-statement SQLite timeout |

**Response:**

```json
{
  "results": [
    {
      "columns": ["id", "name"],
      "types": ["INTEGER", "TEXT"],
      "values": [[1, "alice"], [2, "bob"]]
    }
  ],
  "time": 0.001
}
```

### `/db/request` — Unified Endpoint

**Method:** POST
Accepts both reads and writes in a single request. SQL parsing determines routing (writes go through Raft, reads query directly).

```json
{
  "queries": [
    {"sql": "SELECT count(*) FROM t"},
    {"sql": "INSERT INTO t VALUES(1)"}
  ]
}
```

Supports same query parameters as `/db/execute` and `/db/query`.

### `/db/backup` — Hot Backup

**Method:** GET

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `fmt` | string | `sqlite` | Output format: `sqlite` (binary) or `sql` (text dump) |
| `compress` | flag | — | gzip compression |
| `vacuum` | flag | — | VACUUM database before backup (blocks writes) |
| `tables` | string | — | Comma-separated table names to backup subset |
| `noleader` | flag | — | Backup local copy without leader check |
| `timeout` | duration | 30s | Request timeout |
| `redirect` | flag | — | Redirect to leader |

**Response:** SQLite binary file or SQL text (Content-Type varies).

### `/db/load` — Load Data

**Method:** POST
Accepts SQLite binary file or SQL dump text. Auto-detects format. For SQL dumps, wraps in transaction with rollback on error.

**Query Parameters:** `timeout`, `retries`, `redirect` (same as execute).

### `/boot` — Boot from SQLite File

**Method:** POST
Loads SQLite file directly, bypassing Raft. Then triggers snapshot to replicate. **Only for single-node or fresh cluster bootstrapping.** Not safe on running clusters — use `/db/load` instead.

### `/status` — Node Status

**Method:** GET

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| `key` | string | Filter to specific status section (e.g., `cluster`, `store`, `database`, `system`, `extensions`) |
| `pretty` | flag | Pretty-print JSON |

**Response sections:**
- `cluster` — Raft state, leader, peers
- `store` — Store configuration and stats
- `database` — SQLite version, WAL size, page count
- `system` — Go runtime stats, uptime
- `network` — Listen addresses
- `extensions` — Loaded SQLite extensions

### `/readyz` — Readiness Probe

**Method:** GET
Returns 200 if node is ready to serve requests, 503 otherwise. Suitable for Kubernetes readiness probes.

### `/nodes` — Cluster Topology

**Method:** GET

**Query Parameters:**

| Param | Type | Description |
|---|---|---|
| `nonvoters` | flag | Include non-voting (read-only) nodes |

**Response:**

```json
{
  "10.0.0.1:4002": {
    "address": "10.0.0.1:4002",
    "api_addr": "http://10.0.0.1:4001",
    "id": "10.0.0.1:4002",
    "leader": true,
    "reachable": true,
    "voter": true,
    "version": "v10.2.7"
  }
}
```

### `/leader` — Leader Info / Stepdown

**Method:** GET — returns leader node info.

**Method:** POST — trigger stepdown.

```json
{"id": "10.0.0.2:4002"}  // Optional: specify target new leader
```

**Query Parameters:** `wait` (flag) — wait for new leader election before returning.

### `/remove` — Remove Node

**Method:** POST

```json
{"id": "<node-id>"}
```

**Query Parameters:** `node_id` (string) — node ID to remove (alternative to body).

### `/snapshot` — Trigger Snapshot

**Method:** POST

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `trailing_logs` | int | 0 | Number of logs to keep after snapshot |

Returns 200 on success, 204 if nothing new to snapshot.

### `/reap` — Reap Old Snapshots

**Method:** POST
Removes old snapshots and checkpoints WAL files. After reaping, a Quick Integrity check is performed (not a Full check).

**Response:**

```json
{"snapshots_reaped": 3, "wals_checkpointed": 2}
```

### `/db/sql` — SQL Analysis

**Method:** POST

```json
{"sql": "SELECT * FROM users WHERE name = ?"}
```

Returns EXPLAIN QUERY PLAN output for query optimization analysis.

### `/console/` — Web Console

**Method:** GET
Built-in web application served at `/console/`. Supports running queries, viewing schema, managing tables, monitoring cluster state, and restoring from SQLite data. Redirected from `/` root path.

### `/licenses` — Third-Party Licenses

**Method:** GET
Returns license information for bundled dependencies.

### `/debug/vars` — Go expvar

**Method:** GET
Exposes Go runtime metrics (goroutines, allocations, etc.).

### `/debug/pprof/...` — Go pprof

**Method:** GET
Standard Go pprof endpoints for profiling.

## Common Response Headers

- `X-Rqlite-Version` — rqlite version string
- `X-Rqlite-Served-By` — Raft address of node that served the request (when redirected)
- `Access-Control-Allow-Origin` — set via `-http-allow-origin` flag

## Error Responses

| Status | Meaning |
|---|---|
| 400 | Bad request (invalid JSON, bad SQL, etc.) |
| 401 | Unauthorized (auth required) |
| 405 | Method not allowed |
| 503 | Leader not found / node not ready |

# Commands

How valkey-py exposes Valkey commands, plus the server/admin surface verified in `valkey/commands/core.py`.

## Exposure Model

- Built-in support exists for all out-of-the-box Valkey commands; they are exposed under their **raw Valkey command names** (`set`, `get`, `hset`, `hgetall`, `del`, ...) except where the name is a Python reserved word (README.md).
- The official Valkey command docs (https://valkey.io/commands) describe command semantics; valkey-py "attempts to adhere to the official command syntax".
- Known deviations (README "Advanced Topics"):
  - **MULTI/EXEC** — implemented by the `Pipeline` class; pipelines are wrapped with MULTI/EXEC by default (`transaction=False` disables it).
  - **SUBSCRIBE** — implemented by the `PubSub` class because subscription puts the underlying connection in a state where it cannot run other commands; `PUBLISH` is called on the client.
- Command implementations live in `valkey/commands/` (`core.py`, `cluster.py`, `sentinel.py`, `valkeymodules.py`, plus `json/`, `search/`, `bf/`, `graph/`, `timeseries/` packages). The complete catalog and exact signatures: check `valkey/commands/core.py` or the generated docs at https://valkey-py.readthedocs.io.

## Server / Admin Commands (verified in `valkey/commands/core.py`)

- **Info**: `ping`, `echo`, `info`, `dbsize`, `time`, `config_get`, `config_set`, `config_resetstat`, `config_rewrite`, `lastsave`, `slowlog_get`, `slowlog_len`, `slowlog_reset`, `command`, `command_info`, `command_count`, `command_list`, `command_getkeysandflags`, `command_docs`, `lolwut`.
- **Persistence / replication**: `save`, `bgsave`, `bgrewriteaof`, `sync`, `psync`, `replicaof`, `slaveof`, `wait`, `waitaof`, `role`.
- **Flush / db**: `flushall(asynchronous=False)`, `flushdb(asynchronous=False)`, `swapdb(first, second)` (client-level `SELECT` is intentionally not implemented — see SKILL.md Gotchas).
- **Client management**: `client_kill`, `client_kill_filter`, `client_info`, `client_list`, `client_getname`, `client_getredir`, `client_reply`, `client_id`, `client_tracking` (+ `client_tracking_on`/`client_tracking_off`/`client_trackinginfo`), `client_setname`, `client_setinfo`, `client_unblock`, `client_pause`, `client_unpause`, `client_no_evict`, `client_no_touch`.
- **ACL**: `acl_cat`, `acl_deluser`, `acl_dryrun`, `acl_genpass`, `acl_getuser`, `acl_help`, `acl_list`, `acl_log`, `acl_log_reset`, `acl_load`, `acl_save`, `acl_setuser`, `acl_users`, `acl_whoami`, `auth(password, username=None)`.
- **Memory / debug**: `object(infotype, key)`, `memory_doctor`, `memory_help`, `memory_stats`, `memory_malloc_stats`, `memory_usage`, `memory_purge`, `latency_doctor`, `latency_graph`, `latency_histogram`, `latency_history`, `latency_latest`, `latency_reset`, `debug_object`, `debug_segfault`.
- **Other**: `migrate`, `hello`, `failover`, `quit`, `shutdown`.
- **Bitfields**: bitfield `get`/`set`/`incrby` with offset syntax are part of the core string commands (`BitFieldOffsetT` helpers in `core.py`).

## Data-Structure Commands

String, hash, list, set, sorted-set, stream, geo, bitmap, and HyperLogLog commands are exposed under their raw Valkey names on the same client object (e.g. `r.hset(...)`, `r.lpush(...)`, `r.sadd(...)`, `r.zadd(...)`, `r.xadd(...)`). The README defers detailed semantics to https://valkey.io/commands — do not invent flag spellings from memory; verify exact options in `valkey/commands/core.py` or the official command docs.

## Cluster-Specific Command Behavior

Multi-key and non-key commands behave differently under `ValkeyCluster` (target_nodes, slot routing, `_nonatomic` variants) — see 05-cluster.

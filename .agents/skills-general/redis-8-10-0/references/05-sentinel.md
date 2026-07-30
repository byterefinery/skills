# Sentinel

Redis Sentinel provides high availability through monitoring, automatic failover, and client discovery.

## Architecture

- **Minimum 3 Sentinels** — prevents split-brain; quorum-based decisions
- **Monitoring** — Sentinels ping masters, replicas, and other Sentinels
- **Subjective Down (SDOWN)** — a single Sentinel's view that a node is unreachable
- **Objective Down (ODOWN)** — quorum of Sentinels agree the master is down
- **Leader election** — Raft-like election among Sentinels to perform failover
- **Automatic failover** — promote a replica to master, reconfigure other replicas

## Configuration

```bash
# sentinel.conf
port 26379

# Monitor a master
sentinel monitor mymaster 127.0.0.1 6379 2

# Time before considering master SDOWN (ms)
sentinel down-after-milliseconds mymaster 5000

# Parallel syncs during failover
sentinel parallel-syncs mymaster 1

# Failover timeout (ms)
sentinel failover-timeout mymaster 60000

# Deny scripts reconfig
sentinel deny-scripts-reconfig yes

# Sentinel announce IP/port (NAT)
sentinel announce-ip 1.2.3.4
sentinel announce-port 26379

# Auth passwords
sentinel auth-pass mymaster <password>

# TLS (if built with TLS)
sentinel tls-port 26379
sentinel tls-cert-file /path/to/sentinel.crt
sentinel tls-key-file /path/to/sentinel.key
sentinel tls-ca-cert-file /path/to/ca.crt
```

## Running Sentinel

```bash
# Start Sentinel
redis-server /path/to/sentinel.conf --sentinel

# Sentinel mode is indicated in the log and INFO output
```

## Sentinel Commands

- `SENTINEL masters` — list all monitored masters
- `SENTINEL master <name>` — details for a specific master
- `SENTINEL replicas <master-name>` — list replicas
- `SENTINEL get-master-addr-by-name <name>` — get current master address
- `SENTINEL reset <pattern>` — reset Sentinel state (e.g., `*` for all)
- `SENTINEL failover <master-name>` — manually trigger failover
- `SENTINEN cksync <master-name>` — force Sentinel to sync config
- `SENTINEL ck-quorum <master-name>` — check if quorum is available
- `SENTINEL remove <master-name>` — stop monitoring a master
- `SENTINEL monitor <name> <ip> <port> <quorum>` — add monitoring

## Failover Process

1. Sentinel detects master is SDOWN (no PONG after `down-after-milliseconds`)
2. Quorum of Sentinels agree → ODOWN
3. Leader election among Sentinels
4. Leader selects best replica (by priority, replication offset, run ID)
5. Leader promotes replica to master (`REPLICAOF NO ONE`)
6. Leader reconfigures other replicas to follow new master
7. Leader updates master entry with new address

## Client Discovery

Clients should connect to Sentinels (not directly to masters) and use:
- `SENTINEL get-master-addr-by-name <name>` to find the current master
- Redis clients with Sentinel support handle this automatically (e.g., redis-py, jedis)

## Sentinel Logging

Sentinel logs to stdout by default. Set `logfile` in sentinel.conf for file logging. Logs include:
- SDOWN/ODOWN transitions
- Failover progress
- Leader election
- Config changes

## Gotchas

- **Minimum 3 Sentinels** — with fewer, you risk split-brain or inability to reach quorum
- **`sentinel.conf is rewritten`** — Sentinel updates its config file at runtime. Don't hand-edit it while running.
- **`protected-mode no` by default in Sentinel** — Sentinel listens on all interfaces. Ensure firewall rules restrict access.
- **`parallel-syncs` controls replica cutover** — only this many replicas resync in parallel during failover. Others wait.
- **`failover-timeout` affects retry** — if failover fails, Sentinel waits this long before retrying.
- **Sentinel does not manage data** — it only handles failover. Use Cluster for data sharding.
- **`down-after-milliseconds` vs `failover-timeout`** — the former is detection time, the latter is the entire failover operation timeout.
- **Sentinel and Cluster are mutually exclusive** — a node cannot be in both Sentinel and Cluster mode simultaneously.
- **Auth passwords must match** — `sentinel auth-pass` must match the master's `requirepass`/ACL password.

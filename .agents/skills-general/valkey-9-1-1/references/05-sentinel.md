# Sentinel

Valkey Sentinel provides high availability through automatic failover. It monitors primaries and replicas, detects failures, and promotes a replica to primary when needed.

## Architecture

- Minimum 3 Sentinel instances (odd number preferred for quorum)
- Sentinels monitor primaries and auto-discover replicas
- Sentinels gossip with each other via the cluster bus protocol
- No single point of failure — quorum-based decisions

## Configuration (`sentinel.conf`)

```conf
# Sentinel listens on this port
port 26379

# Protected mode is off by default in sentinel mode
protected-mode no

# Monitor a primary: sentinel monitor <name> <ip> <port> <quorum>
# Quorum = number of sentinels that must agree on failure
sentinel monitor mymaster 127.0.0.1 6379 2

# Auth password for primary and replicas
sentinel auth-pass mymaster MySUPER--secret-@#2pass!

# Timeout before considering a primary as down (milliseconds)
sentinel down-after-milliseconds mymaster 30000

# Parallel syncs — how many replicas re-sync simultaneously during failover
sentinel parallel-syncs mymaster 1

# Failover timeout (milliseconds) — various operations must complete within this
sentinel failover-timeout mymaster 180000

# Script to run on events (optional)
# sentinel notification-script mymaster /var/redis/notify.sh
# sentinel client-reconfig-script mymaster /var/redis/reconfig.sh

# Deny scripts re-execution (safety)
sentinel deny-scripts-reconfig yes

# Working directory
dir /tmp

# Announce IP/port (NAT scenarios)
# sentinel announce-ip 1.2.3.4
# sentinel announce-port 26379
```

## Running Sentinel

```bash
# Sentinel mode uses the same binary
./src/valkey-server /path/to/sentinel.conf --sentinel
```

## Sentinel Commands

```bash
# Connect to sentinel
valkey-cli -p 26379

# Get primary address
SENTINEL get-master-addr-by-name mymaster

# List monitored primaries
SENTINEL masters

# List replicas of a primary
SENTINEL replicas mymaster

# List other sentinels monitoring the same primary
SENTINEL sentinels mymaster

# Trigger manual failover
SENTINEL failover mymaster

# Check quorum
SENTINEL ckquorum mymaster

# Monitor a new primary
SENTINEL monitor mynewmaster 10.0.0.2 6379 2

# Remove a primary from monitoring
SENTINEL remove mymaster

# Set sentinel configuration
SENTINEL set mymaster down-after-milliseconds 10000

# Get sentinel config
SENTINEL config mymaster

# Reset sentinels matching a primary name pattern
SENTINEL reset mymaster*
```

## Failure Detection

1. **Subjectively Down (SDOWN):** A single sentinel considers the primary unreachable after `down-after-milliseconds`
2. **Objectively Down (ODOWN):** Quorum of sentinels agree the primary is down
3. **Failover:** Election among sentinels — winner promotes a replica

## Replica Selection

During failover, Sentinel selects the best replica based on:
1. Replication offset (most data synced)
2. Run ID (preference for longer-running replicas)
3. Replica priority (`replica-priority` config on the Valkey instance)
4. Node ID (tiebreaker)

A replica with `replica-priority 0` is never promoted.

## Dynamic Config

Sentinel rewrites `sentinel.conf` automatically:
- Adds/discoveres replicas
- Updates primary address after failover
- Tracks other sentinels

Do not edit the sentinel.conf manually while Sentinel is running — changes will be overwritten.

## Sentinel and Cluster

Sentinel and Cluster are **mutually exclusive** HA approaches:
- **Sentinel:** Single primary, multiple replicas. Simple, automatic failover.
- **Cluster:** Multiple shards, horizontal scaling, built-in failover per shard.

Choose Sentinel for simple primary-replica HA. Choose Cluster for scaling and partitioning.

## Logging

Sentinel logs to the same log file/stdout as configured. Key log events:
- `+sdown`/`+odown` — failure detection
- `+try-failover`/`+failover-state` — failover progress
- `+switch-over` — replica promoted
- `+reboot` — instance rebooted

# Clustering Reference

rqlite uses Raft consensus for replication. A cluster needs `(N/2)+1` nodes for quorum:
- 3 nodes tolerates 1 failure
- 5 nodes tolerates 2 failures

## Manual Join

Start the first node normally, then join additional nodes:

```bash
# Node 1 (leader)
rqlited -http-addr 0.0.0.0:4001 -raft-addr 0.0.0.0:4002 /data/node1

# Node 2 (join via Raft address of node 1)
rqlited -http-addr 0.0.0.0:4003 -raft-addr 0.0.0.0:4004 \
  -join 10.0.0.1:4002 /data/node2

# Node 3 (can join via any known node, comma-separated for redundancy)
rqlited -http-addr 0.0.0.0:4005 -raft-addr 0.0.0.0:4006 \
  -join 10.0.0.1:4002,10.0.0.2:4004 /data/node3
```

Join uses the Raft address (`-raft-addr`), not the HTTP address.

## Simultaneous Bootstrap

When starting all nodes at once (e.g., in containers), use `-bootstrap-expect`:

```bash
# All 3 nodes started simultaneously with same flag
rqlited -http-addr 0.0.0.0:4001 -raft-addr 0.0.0.0:4002 \
  -bootstrap-expect 3 /data/node1
```

Nodes wait until `bootstrap-expect` count is reached, then form a cluster. Default timeout is 120s (`-bootstrap-expect-timeout`).

Cannot be combined with `-join` or KV discovery modes.

## DNS Discovery

Nodes discover each other via DNS A records:

```bash
rqlited -http-addr 0.0.0.0:4001 -raft-addr 0.0.0.0:4002 \
  -disco-mode dns -bootstrap-expect 3 \
  -disco-config '{"dns-name": "rqlite.myapp.local", "interval": "5s"}' \
  /data/node1
```

DNS must resolve `rqlite.myapp.local` to all node IPs. In Kubernetes, use a headless Service.

**Voting nodes require `-bootstrap-expect` with DNS discovery.** Non-voters (`-raft-non-voter`) do not.

## DNS-SRV Discovery

Uses SRV records for service discovery:

```bash
rqlited -disco-mode dns-srv -bootstrap-expect 3 \
  -disco-config '{"dns-name": "_rqlite._tcp.myapp.local"}' \
  /data/node1
```

## Consul KV Discovery

Register nodes in Consul KV store, then discover:

```bash
rqlited -disco-mode consul-kv \
  -disco-config '{"consul-address": "http://consul:8500", "consul-token": "my-token"}' \
  /data/node1
```

Nodes auto-register their Raft address under `rqlite/<node-id>` in Consul KV.

## etcd KV Discovery

Same pattern with etcd:

```bash
rqlited -disco-mode etcd-kv \
  -disco-config '{"etcd-addresses": "http://etcd:2379"}' \
  /data/node1
```

## Kubernetes Deployment

rqlite provides official Kubernetes manifests. Key patterns:

### Headless Service for DNS Discovery

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rqlite
spec:
  clusterIP: None
  ports:
    - port: 4001
      name: http
    - port: 4002
      name: raft
  selector:
    app: rqlite
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: rqlite
spec:
  replicas: 3
  serviceName: rqlite
  template:
    spec:
      containers:
        - name: rqlite
          image: rqlite/rqlite
          env:
            - name: DISCO_MODE
              value: "dns"
            - name: BOOTSTRAP_EXPECT
              value: "3"
          ports:
            - containerPort: 4001
            - containerPort: 4002
```

The Docker entrypoint auto-detects `KUBERNETES_SERVICE_HOST` and adds a 5-second startup delay for DNS propagation. Override with `START_DELAY` env var.

### Read-Only Replica Nodes

Scale read throughput with non-voting nodes:

```bash
rqlited -http-addr 0.0.0.0:4001 -raft-addr 0.0.0.0:4002 \
  -raft-non-voter -join 10.0.0.1:4002 /data/reader
```

Non-voters receive full replication but don't participate in elections. Useful for read scaling.

## Removing Nodes

Via CLI:
```bash
rqlite
>.remove <node-id>
```

Via HTTP:
```bash
curl -XPOST 'http://localhost:4001/remove?node_id=<node-id>'
```

With `-raft-remove-shutdown`, removed nodes automatically shut down their Raft layer.

## Node Reaping

Auto-remove unreachable nodes after a timeout:

```bash
rqlited -raft-reap-node-timeout 24h \
  -raft-reap-read-only-node-timeout 12h /data/node1
```

Reaping only applies to nodes that were previously reachable. Newly joined nodes are not reaped immediately.

## Non-Voting Node Limitations

Non-voting nodes (`-raft-non-voter`):
- Cannot be bootstrapped with `-bootstrap-expect`
- Cannot have CDC enabled
- Cannot be leaders (by definition)
- Receive full data replication
- Can serve read queries

## v10 Clustering Notes

- Rolling upgrades from v7+ are supported, but you cannot join a v10 node to a pre-v10 cluster
- During upgrade, back up first, then upgrade existing cluster before adding new v10 nodes
- Downgrade requires backup from v10 and restore on pre-v10 system
- The cluster client now limits connections to the cluster service and always retries at least once with a new connection
- Redirect following during cluster join is now limited to prevent infinite redirect loops

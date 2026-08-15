# Fleet operations

## Start a node

For local development, the default listeners are sufficient:

```sh
celld --bucket "$CELLD_BUCKET" --endpoint "$S3_ENDPOINT" --region "$AWS_REGION"
```

For a fleet node, bind the public and internal listeners separately. The ingress reaches the public listener; the other nodes reach the internal listener:

```sh
celld \
  --bucket "$CELLD_BUCKET" --endpoint "$S3_ENDPOINT" --region "$AWS_REGION" \
  --listen 0.0.0.0:8080 \
  --internal-listen 10.0.0.12:8081 \
  --advertise node-a.internal:8081
```

Listener pairing rules:

- An explicit advertised address requires an explicit internal-listener address — set both command-line options, or use their equivalent environment variables (`CELLD_ADVERTISE` + `CELLD_INTERNAL_ADDR`).
- celld also rejects an explicit non-loopback public listener without an explicit internal listener; the rule identifies an obsolete one-listener configuration.
- celld cannot verify that an advertised hostname or a translated port reaches the internal listener. You must route the advertised address to the internal listener, and you must not route it to the public Worker listener.

## Add nodes

Start each node with the same bucket settings. Give each internal listener a different address that the other nodes can reach, and set `--advertise` to that internal address. The nodes find each other through the leases in the bucket — there is no join command and no fixed membership list.

The bucket supplies discovery and authority, but not network reachability. The peer HTTP protocol is versioned, body-signed, HMAC-authenticated, clock-bounded, and replay-protected, but celld does not terminate TLS on it. Put the advertised addresses on a private network you trust, or on an encrypted overlay such as WireGuard or Tailscale.

celld has no central placement controller, so it does not rebalance the fleet when a node joins. Normal traffic places an unowned or released cell on a node with capacity.

## Shut down and roll out a node

celld shuts a node down gracefully on SIGTERM or SIGINT — the signals `systemctl stop`, `docker stop`, and a Kubernetes pod delete send. The sequence:

1. The `/__celld/health` path reports the node as unhealthy (503), so a load balancer stops routing to it.
2. The node answers each new request with a 503 and closes the connection, so a client retries on a healthy node.
3. The node hands every resident cell to a peer by releasing its ownership, and it finishes the requests already in flight. A cell that serves a request is handed off when that request finishes. A peer takes over each released cell at once, so the node leaves without the takeover gap of an abrupt kill.

The internal listener continues to accept `/state` requests during the drain; the response reports the `occupied`, `evicting`, and `restoring` values.

Tuning:

- `CELLD_RELEASES` bounds the concurrent ownership releases during handoff (default 128), keeping a node with many cells from flooding the object store at shutdown.
- `CELLD_SHUTDOWN_DRAIN_MS` bounds the whole drain (default 25000). The node exits when the handoff and the in-flight requests finish, or when this many milliseconds pass, whichever is first — an idle node exits immediately. Set it **below** the stop grace of your orchestrator (systemd `TimeoutStopSec`, Kubernetes `terminationGracePeriod`) so the orchestrator does not send SIGKILL.

Rolling update: use the rolling update of your orchestrator — stop each node with SIGTERM, wait for its replacement to report healthy, then move to the next node. celld has no rollout command, because the health signal lets the orchestrator pace the roll.

**The upgrade from v0.1.0 to v0.2.0 must not be a rolling update.** Stop every v0.1.0 node, then start the v0.2.0 nodes. Two changes require this: v0.2.0 nodes advertise the internal listener, so ownership records that v0.1.0 nodes wrote name an address that v0.1.0 peers cannot follow to a v0.2.0 node; and v0.2.0 compacts replicated data into block objects that a v0.1.0 reader cannot restore. A fleet must not mix the two versions.

## Operator API (alpha)

The internal listener provides an alpha operator API; a release can change its paths or response formats, so keep the operator tooling and the celld release together. The API does not authenticate its requests — restrict access with a firewall or private overlay.

| route | effect |
| --- | --- |
| `GET /state` | Reports occupancy, eviction, and restoration values. Remains available while a graceful shutdown drains existing work |
| `GET /cell/NAME` | Resolves or activates a cell for an operator check |
| `GET /evict/NAME` | Evicts a resident cell |
| `GET /do/NAME` | Sends a direct Durable Object request |
| `POST /shutdown` | Starts a graceful ownership handoff |
| `POST /shutdown?handoff=preserve` | Prepares a clean same-node reload and keeps the ownership records |
| `GET /__celld/probe` | Serves the signed diagnostic probe |

The peer protocol also uses reserved internal paths; an operator must not call them directly, and celld continues to authenticate each peer request. The internal listener does not pass an unknown path to the Worker — it returns 404, so an operator request cannot become an application request.

## Diagnose a fleet

`celld diagnose` reads the node leases in the bucket, then sends a signed probe to each live peer. It does not get a lease, and it does not change ownership:

```sh
celld diagnose --bucket "$CELLD_BUCKET" --endpoint "$S3_ENDPOINT" --region "$AWS_REGION"
```

- Pass one or more `--peer NODE_ID` options to probe only some nodes.
- The report keeps checking after an individual failure, and it distinguishes expired records, malformed or unsafe advertised addresses, unreachable peers, authentication failures, and protocol versions that do not agree.
- Each node line also shows coarse resident-cell, WebSocket, RSS, CPU, file-descriptor, pressure, and shedding samples, plus `restoring` — the count of each cold route that holds an activation permit or waits for one (a capacity waiter already holds a permit, so each cold route counts once).
- During a rolling update, wait for every node to report `restoring=0` before you restart the next node, so one restart's cold work finishes before the next restart removes more warm capacity.
- With a read-only credential, run `celld diagnose --read-only` to skip the storage probe (the probe writes one small object under `probe/`, then deletes it).

## Memory limits and pressure shedding

**Resident-cell limit** — set `CELLD_MAX_RESIDENT_CELLS` on each loaded node to cap resident cells, enforced at admission.

**Memory threshold** — celld enables a memory threshold at 80% of the available memory by default. Set `CELLD_MAX_RSS_MB` to change it, or `0` to disable it (and the absolute cap) together.

celld measures the memory that the cells hold, **not** the resident set size of the process. The two differ because the memory allocator keeps some freed pages instead of returning them to the operating system. Shedding a cell cannot return those pages, so a threshold on the resident set size holds a node in pressure after the node gives every cell back. The `/state` route reports both numbers.

**Absolute cap** — celld also applies an absolute cap to the resident set size of the process, at 95% of the available memory. It protects the node when the allocator holds memory that shedding cannot return, because the operating system stops a process that uses more memory than the machine has. The node logs a warning when this cap applies.

- The cap is a share of the machine; celld does not derive it from the threshold. A `CELLD_MAX_RSS_MB` at or above 95% of the available memory therefore reaches the cap, and the cap is then the effective limit. The node decides on its resident set size, and celld reports this at startup.
- When celld cannot read the size of the available memory, it applies a cap of 125% of an explicit threshold.

**Shedding behavior** — under pressure, celld durably replicates and fences the least-recently-used idle cells. It then publishes the cells as unowned without resetting their epochs. Those cells become inactive, and celld refuses to reacquire new unowned cells while in pressure. celld does not shed a cell with active work or a live host WebSocket.

Each limit releases separately: the threshold releases when the memory in use falls to 80% of the threshold, and the cap releases when the resident set size falls to 80% of the cap. A crossing of one limit does not hold the node against the other. A spare node receives no assignment; it acquires a released cell through the same bucket protocol when normal traffic reaches it.

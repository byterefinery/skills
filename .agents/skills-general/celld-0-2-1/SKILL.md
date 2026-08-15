---
name: celld-0-2-1
description: >
  Operate celld 0.2.1 — self-hosted distributed Durable Objects from Denoland.
  Runs Cloudflare Workers and Durable Objects on your own machines, with each
  cell backed by its own SQLite database replicated to an S3-compatible or
  Google Cloud Storage bucket you own. Use for deploying Worker projects with
  celld deploy, configuring object storage (S3, R2, GCS), starting and scaling
  fleet nodes, diagnosing leases, graceful shutdown and rolling updates, memory
  pressure shedding, DuckDB-backed telemetry, and mapping Cloudflare Workers API
  compatibility. Use whenever the user mentions celld, self-hosting Durable
  Objects, or running the Workers runtime off Cloudflare.
metadata:
  tags:
    - workers
    - durable-objects
    - distributed-systems
    - sqlite
---

# celld 0.2.1

## Overview

celld is an open-source daemon (Apache-2.0, Denoland) that runs Cloudflare Workers and Durable Objects on your own machines — a self-hosted, distributed Durable Objects runtime. The core ideas:

- **A cell is a Durable Object** — a named, single-threaded server with its own SQLite database. One cell per user, chat room, document, or AI agent. Two requests to the same cell never run at the same instant (interleaving only while the first awaits), and storage operations are synchronous, so a cell's state stays consistent. Cells share no database; the application shards by construction.
- **The bucket is the coordinator and durable source of truth** — one S3-compatible or GCS bucket holds deployments, cell state, ownership leases, node leases, and the peer-auth secret. No control plane, membership protocol, failure detector, or consensus. Object-storage compare-and-swap ensures exactly one node owns a cell at a time.
- **In-process replication with RPO=0** — each node embeds V8, executes Wrangler bundles, and continuously replicates each cell's SQLite database to the bucket. By default the response waits until the write is proven durable in the bucket, so a lost node cannot lose an acknowledged write. Nodes are replaceable; add a node by pointing it at the bucket.
- **Cell lifecycle** — resident (active while doing work, idle when waiting) → hibernated (keeps hibernatable WebSocket clients on its node) → inactive (only an object in the bucket, costs nearly nothing). Every cell starts inactive, and the constructor reruns on every activation. One 8 GB node holds ~1,000 resident cells (~$0.05/month each).
- **A fleet runs one application** — every node loads the latest successfully committed deployment from `deploy/current.json`.

## Usage

### Install

```sh
curl -fsSL https://celld.dev/install.sh | sh
```

- Pin or roll back a release with `CELLD_VERSION=v0.2.1`. Verify provenance with `gh attestation verify <asset> --repo denoland/celld`.
- `celld deploy` needs esbuild on `PATH` (or `CELLD_ESBUILD`); asset-only projects do not.
- Container: `ghcr.io/denoland/celld` (Linux x86-64 and ARM64).

### Configure object storage

```sh
# S3 / R2 — standard AWS credential chain
export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=auto S3_ENDPOINT=https://ACCOUNT.r2.cloudflarestorage.com
export CELLD_BUCKET=s3://YOUR-BUCKET

# Google Cloud Storage — Application Default Credentials
export CELLD_BUCKET=gs://YOUR-BUCKET
```

A `gs://` bucket takes no `S3_ENDPOINT` and no AWS credentials. A bucket value can add a key prefix (`s3://BUCKET/PREFIX`) so two fleets share one bucket. The store must implement conditional writes and read-after-write consistency — S3, R2, GCS, Azure Blob, and Tigris qualify; MinIO CE, Backblaze B2, Hetzner, and DigitalOcean Spaces do not. `celld diagnose` probes the bucket directly.

### Deploy

```sh
celld deploy . --bucket "$CELLD_BUCKET" --endpoint "$S3_ENDPOINT" --region "$AWS_REGION"
```

`celld deploy` builds a standard Wrangler project (`wrangler.jsonc` or `wrangler.json`, not `.toml`), invokes esbuild, and writes deployment objects directly to the bucket. It accepts module Workers, Durable Object bindings, static assets, and wasm imports; any unknown config key stops the deploy with an error naming the key.

### Start a node

```sh
celld \
  --bucket "$CELLD_BUCKET" --endpoint "$S3_ENDPOINT" --region "$AWS_REGION" \
  --listen 0.0.0.0:8080 \
  --internal-listen 10.0.0.12:8081 \
  --advertise node-a.internal:8081
```

- `--listen` is the public Worker listener; `--internal-listen` serves the peer protocol and the unauthenticated operator API — keep it on a trusted private network or an encrypted overlay (WireGuard, Tailscale).
- An explicit `--advertise` requires an explicit `--internal-listen`, and you must route the advertised address to the internal listener, never the public one.
- To add a node, start it with the same bucket settings and a different internal address. Nodes discover each other through bucket leases — there is no join command.

### Operate

```sh
celld diagnose --bucket "$CELLD_BUCKET"   # lease enumeration + signed probe of each live peer
```

- **Shutdown** — SIGTERM/SIGINT triggers a graceful drain (health flips to 503, cells are handed to peers). Keep `CELLD_SHUTDOWN_DRAIN_MS` (default 25000) below your orchestrator's stop grace.
- **Rolling update** — stop one node, wait for its replacement to report healthy, then the next; wait for `restoring=0` on every node before restarting the next. The v0.1.0 → v0.2.0 upgrade must not be rolling — stop all old nodes first.
- **Memory** — `CELLD_MAX_RSS_MB` sets the pressure-shedding threshold (default 80% of available memory; `0` disables it and the absolute cap). Under pressure celld durably replicates and sheds idle LRU cells. `CELLD_MAX_RESIDENT_CELLS` is a hard admission limit.
- **Telemetry** — `CELLD_OTEL=1` writes Parquet traces and logs under `telemetry/` in the bucket, queryable directly with DuckDB.

### Examples

Twelve small Wrangler projects in the [examples directory](https://github.com/denoland/celld/tree/v0.2.1/examples) demonstrate the Worker and Durable Object surface: `hello` (stateless fetch), `webapi`, `counter` (SQLite Durable Object), `vectordb` (vec0 search), `async`, `body`, `router`, `wsecho` (hibernatable WebSocket), `wsclient` (outbound WebSocket), `alarm`, `rpc` (JS RPC), `wasm` (Rust via workers-rs). Deploy one from its directory with `celld deploy . --bucket ...`.

## Gotchas

- **No local filesystem mode** — even on a laptop you need a real bucket (or a store with conditional writes). There is no single-node local mode.
- **Store qualification is a correctness issue** — on a store that ignores conditional headers (MinIO CE, B2, Hetzner, DO Spaces), two nodes can own one cell. `celld diagnose` runs a four-write probe, and each node re-runs it at startup (disable with `CELLD_STORAGE_PROBE=0`).
- **Never write under the reserved prefixes** — `cells/`, `nodes/`, `node-cells/`, `fleet/`, `deploy/`, `deploy-blobs/`, `wake/`, `probe/`, `telemetry/`. celld deletes objects under some of them.
- **The internal listener is unauthenticated and has no TLS** — anything that can reach it can inspect state, evict cells, or stop the process. Firewall it; the peer protocol's HMAC auth does not replace a private network.
- **The advertised address must hit the internal listener**, never the public Worker listener. celld cannot verify this; a wrong route breaks the fleet silently.
- **celld does not terminate public TLS** — put TLS termination and application authentication in your ingress proxy.
- **`--trust-forwarded-headers` only with a trusted proxy** that replaces both `X-Forwarded-Host` and `X-Forwarded-Proto`; otherwise requests see the node's own address.
- **Deploy config is a strict subset of Wrangler** — `wrangler.jsonc`/`wrangler.json` only, and unknown keys (`routes`, `kv_namespaces`, `triggers`, …) stop the deploy. Deploy those projects with Wrangler instead.
- **Known silent gaps in the runtime** — unimplemented `node:` modules give inert stubs instead of failing the import, and `cloudflare:sockets` `connect()` returns an inert stub. Verify behavior, do not assume.
- **`setInterval` throws** — use `setTimeout` or `scheduler.wait()`. `Response.redirect()`, `Response.error()`, and the `cache` request option are missing.
- **Outbound Durable Object WebSockets keep the cell resident** and do not continue when the cell moves nodes — store the connection intent in storage and reconnect after activation.
- **RPO=0 is a knob** — `CELLD_OUTPUT_GATE=0` removes the durability wait and accepts losing acknowledged writes.
- **A fleet runs exactly one application** — no multi-tenant scheduling, no account service. It is alpha; not safe for hostile multi-tenant use, and security fixes apply to the latest release only.
- **Windows unsupported; Intel Macs get no prebuilt binaries** (build from source works).

## References

- [01-install-and-storage](references/01-install-and-storage.md) — installer, container, S3/R2/GCS setup, reserved prefixes, full environment variable table
- [02-fleet-operations](references/02-fleet-operations.md) — node lifecycle, shutdown drain, rolling updates, diagnose, memory shedding, operator API
- [03-cloudflare-compat](references/03-cloudflare-compat.md) — full Workers API compatibility table, RPC, node: imports, compat flags, Wrangler config
- [04-ownership-and-fencing](references/04-ownership-and-fencing.md) — ownership records, epoch fencing, RPO=0 ack rule, epoch seal, bucket requirements
- [05-security](references/05-security.md) — listener separation, forwarded headers, operator API routes, bucket protection
- [06-telemetry](references/06-telemetry.md) — OTEL configuration, DuckDB queries, file layout, compaction
- [07-wasm](references/07-wasm.md) — wasm module imports, workers-rs, Worker Loader, limits

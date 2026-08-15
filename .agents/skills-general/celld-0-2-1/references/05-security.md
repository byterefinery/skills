# Security

celld is an alpha. It is not safe for hostile multi-tenant use. Security fixes apply to the latest release only, so older alpha builds do not receive fixes.

## Separate the public and internal listeners

celld opens two HTTP listeners. The public listener serves the deployed Worker; the internal listener serves the peer protocol and the operator API.

- `--listen` — the public listener. Expose only this listener through a load balancer, a reverse proxy, or a public firewall rule.
- `--internal-listen` — the internal listener. Its default address is `127.0.0.1:0`, so celld selects an available loopback port at each start; the startup output reports the selected address. Bind it to a private interface, or protect it with a private overlay. **Do not expose this listener to the public internet.**
- `--advertise` — gives peers the address of the internal listener.

An explicit advertised address requires an explicit internal-listener address — set both command-line options, or use their equivalent environment variables. celld also rejects an explicit non-loopback public listener without an explicit internal listener.

celld cannot verify that an advertised hostname or a translated port reaches the internal listener. You must route the advertised address to the internal listener, and you must not route it to the public Worker listener.

Path handling:

- The public listener reserves only `/__celld/health`. A healthy node returns 200 with `{"ok":true}`; an unhealthy node returns 503. The deployed Worker owns `/health` and every other public path.
- The internal listener does not pass an unknown path to the Worker — it returns 404, so an operator request cannot become an application request.

## Set the forwarded-header policy

A Worker reads the request URL from `request.url`. An application can route on the hostname and build absolute links from it. Therefore celld ignores `X-Forwarded-Host` and `X-Forwarded-Proto` by default.

Set `--trust-forwarded-headers` (or `CELLD_TRUST_FORWARDED_HEADERS=1`) only when a trusted proxy replaces both headers. celld then reads the last value in each header, so an earlier client value does not override the proxy value.

celld always takes the path and query from the request target. It ignores an absolute-form request target's scheme and authority, so a direct client cannot bypass the host policy through the request line.

## Protect the internal listener

The operator API does not authenticate its requests. A client that can reach the internal listener can inspect state, start direct work, evict a cell, or stop the process. A firewall or a private overlay must restrict access to trusted operators and fleet nodes.

Peer requests on the same listener keep their protocol authentication — each peer request has an HMAC, a body signature, a clock limit, and replay protection (the fleet secret is `fleet/peer-auth.json` in the bucket, created by the first current node). The private network adds protection, but it does not replace the peer authentication.

celld does not terminate TLS on the internal listener. Use an encrypted overlay such as WireGuard or Tailscale when the private network does not provide the required confidentiality.

### Internal operator API (alpha)

The operator API is available in the released binary. It is an alpha interface — a release can change its paths or response formats.

- `GET /state` — occupancy, eviction, and restoration values; remains available while a graceful shutdown drains existing work
- `GET /cell/NAME` — resolves or activates a cell for an operator check
- `GET /evict/NAME` — evicts a resident cell
- `GET /do/NAME` — sends a direct Durable Object request
- `POST /shutdown` — starts a graceful ownership handoff
- `POST /shutdown?handoff=preserve` — prepares a clean same-node reload and keeps the ownership records
- `GET /__celld/probe` — serves the signed diagnostic probe

The peer protocol also uses reserved internal paths. An operator must not call these paths directly, and celld continues to authenticate each peer request.

## Protect the fleet bucket

The fleet bucket is the root of authority for the fleet. It stores the deployments, the cell state, the ownership leases, the node leases, and the shared peer-authentication secret.

A person who holds the bucket credentials controls the fleet. Give each credential access to one fleet bucket only, and replace a credential after a suspected disclosure. Treat access to the bucket and its credentials as fleet administrator access.

## Keep one writer for each cell

Each cell is a SQLite database with one writer. One node owns a cell at a time, and an ownership epoch fences each cell — see [04-ownership-and-fencing](04-ownership-and-fencing.md). A node that loses its lease cannot modify the current cell state.

A fleet has no shared multi-tenant scheduler or shared placement layer. A defective cell can access only its own database, but it can consume resources on its fleet nodes.

## Protect the public application

celld does not authenticate the users of the deployed application. It also does not terminate public TLS. Put the required authentication and TLS in front of the public listener.

Keep the internal listener private, and keep the bucket credentials secret.

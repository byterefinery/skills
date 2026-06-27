# Security Reference

## Authentication File Format

Pass `-auth /path/to/creds.json` to enable authentication. When set, anonymous access is disabled.

The file is a JSON array of credential objects:

```json
[
  {
    "username": "admin",
    "password": "s3cret",
    "perms": ["all"]
  },
  {
    "username": "reader",
    "password": "r3ad",
    "perms": ["query", "status", "ready"]
  },
  {
    "username": "writer",
    "password": "wr1te",
    "perms": ["execute", "query", "status"]
  },
  {
    "username": "backup-user",
    "password": "bkup",
    "perms": ["backup", "status"]
  }
]
```

### Available Permissions

| Permission | Scope |
|---|---|
| `all` | Full access to everything |
| `join` | Join cluster as voting node |
| `join-read-only` | Join cluster as non-voting node |
| `remove` | Remove nodes from cluster |
| `execute` | Write operations (`/db/execute`) |
| `query` | Read operations (`/db/query`) |
| `status` | Node status (`/status`) |
| `ready` | Readiness check (`/readyz`) |
| `backup` | Backup operations (`/db/backup`) |
| `load` | Load/boot data (`/db/load`, `/boot`) |
| `snapshot` | Snapshot/reap operations |
| `leader-ops` | Leader stepdown and related ops |
| `ui` | Web console access |

### Special Username

`*` matches all users including anonymous requests. Useful for allowing public read access:

```json
[
  {"username": "*", "perms": ["query", "status"]},
  {"username": "admin", "password": "s3cret", "perms": ["all"]}
]
```

### HTTP Authentication

Use Basic Auth in requests:

```bash
# curl
curl -u admin:s3cret 'http://localhost:4001/db/execute' \
  -H 'Content-Type: application/json' -d '["SELECT 1"]'

# rqlite CLI
rqlite -u admin:s3cret

# RQLITE_HOST env var
RQLITE_HOST=http://admin:s3cret@localhost:4001 rqlite
```

## TLS / HTTPS

### Enabling HTTPS

Set both `-http-cert` and `-http-key` to enable HTTPS on the API:

```bash
rqlited -http-addr 0.0.0.0:4001 \
  -http-cert /certs/server.crt \
  -http-key /certs/server.key \
  -http-ca-cert /certs/ca.crt \
  /data/node1
```

Clients connect with `-s https` (CLI) or `https://` (curl). Use `-i` on CLI to skip cert verification.

### Mutual TLS (mTLS)

Enable client certificate verification:

```bash
rqlited -http-verify-client \
  -http-cert /certs/server.crt \
  -http-key /certs/server.key \
  -http-ca-cert /certs/ca.crt \
  /data/node1
```

Clients must present a valid certificate signed by the same CA.

Restrict to specific Common Name:

```bash
rqlited -http-verify-client \
  -http-verify-common-name "app-client" \
  ...
```

### Node-to-Node TLS

Encrypt inter-node Raft communication:

```bash
rqlited -node-cert /certs/node.crt \
  -node-key /certs/node.key \
  -node-ca-cert /certs/ca.crt \
  -node-verify-client \
  /data/node1
```

All nodes must share the same CA. Use `-node-verify-common-name` to restrict which nodes can join.

For development/testing, `-node-no-verify` skips all certificate checks (insecure).

### Generating Certificates

Using OpenSSL for a simple setup:

```bash
# CA
openssl req -x509 -newkey rsa:4096 -keyout ca.key -out ca.crt -days 3650 \
  -nodes -subj '/CN=rqlite-CA'

# Server cert
openssl req -newkey rsa:4096 -keyout server.key -out server.csr -nodes \
  -subj '/CN=server'
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out server.crt -days 3650 -extensions v3_ext \
  -extfile <(printf "[v3_ext]\nsubjectAltName=DNS:localhost,IP:127.0.0.1")

# Client cert
openssl req -newkey rsa:4096 -keyout client.key -out client.csr -nodes \
  -subj '/CN=client'
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out client.crt -days 3650
```

## CLI TLS Options

| Flag | Description |
|---|---|
| `-s https` | Use HTTPS scheme |
| `-i` | Skip server certificate verification |
| `-c /path/to/ca.crt` | Trusted CA certificate |
| `-d /path/to/client.crt` | Client certificate for mTLS |
| `-k /path/to/client.key` | Client private key for mTLS |

# Security

## ACL System

Redis ACL provides fine-grained access control with per-user command, key, and channel permissions.

### User Definition

```
user <name> [on|off] [passwords] [commands] [keys] [channels] [selectors]
```

**Example:**
```
user default on >mypassword ~* &* +@all
user ro-user on >ro_pass ~data:* &* +@read -@dangerous
user admin on >admin_pass ~* &* +@all +@admin
user nosql off >pass123 ~users:* +@string +hash.set +hash.get
```

**Components:**
- `on`/`off` — enable/disable user
- `>password` — add all-time password (use `#sha256` for hashed passwords)
- `~pattern` — key patterns (glob-style, e.g., `~users:*`, `~*`)
- `&pattern` — shard channel patterns
- `+command`/`-command` — allow/deny specific commands
- `+@category`/`-@category` — allow/deny command categories
- `allcommands`/`nocomands` — allow all or no commands

### Command Categories

| Category | Description |
|---|---|
| `@all` | All commands |
| `@read` | Read-only commands |
| `@write` | Write commands |
| `@admin` | Admin commands (CONFIG, DEBUG, etc.) |
| `@fast` | Fast commands |
| `@slow` | Slow commands |
| `@dangerous` | Potentially dangerous commands |
| `@connection` | Connection management |
| `@blocking` | Blocking commands |
| `@dangerous` | Commands that can cause data loss |
| `@keyspace` | Keyspace notification commands |
| `@scripting` | Scripting commands |
| `@sortedset` | Sorted set commands |
| `@list` | List commands |
| `@set` | Set commands |
| `@pair` | Pair commands |
| `@string` | String commands |
| `@bitmap` | Bitmap commands |
| `@hyperloglog` | HyperLogLog commands |
| `@stream` | Stream commands |
| `@geo` | Geo commands |
| `@hash` | Hash commands |
| `@pubsub` | Pub/Sub commands |
| `@transaction` | Transaction commands |
| `@module` | Module commands |
| `@array` | Array commands |
| `@default` | Default category for new commands |

### ACL Commands

- `ACL LIST` — list all users
- `ACL GETUSER <name>` — get user details
- `ACL SETUSER <name> [options]` — create/modify user
- `ACL DELUSER <name> [name ...]` — delete users
- `ACL WHOAMI` — current user
- `ACL CAT [category]` — list command categories
- `ACL GENPASS` — generate random password
- `ACL LOAD` — load ACL from file
- `ACL SAVE` — save ACL to file
- `ACL DRYRUN <user> <command>` — test if user can run command
- `ACL LOG [count|RESET]` — view/clear ACL deny log

### ACL File

```
aclfile /etc/redis/users.acl
```

Changes via `ACL SETUSER` are in-memory only. Use `ACL SAVE` to persist to the ACL file.

## Authentication

```bash
# Simple password (sets default user password)
requirepass <password>

# Or via ACL
user default on >password ~* &* +@all
```

**Client auth:**
```bash
redis-cli -a <password>
# or: AUTH <username> <password>
# or: AUTH <password>  (default user)
```

## TLS/SSL

**Build:** `make BUILD_TLS=yes` (built-in) or `make BUILD_TLS=module` (loadable)

**Config:**
```
tls-port 6379          # TLS port (0 = disable)
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
tls-auth-clients yes   # require client certificates
tls-replication yes     # use TLS for replication
tls-cluster yes         # use TLS for cluster bus
tls-prefer-server-ciphers yes
tls-ciphersuites TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
tls-protocols TLSv1.2 TLSv1.3
```

**Client TLS:**
```bash
redis-cli --tls --cert client.crt --key client.key --cacert ca.crt
```

## Hardened Configuration

```
protected-mode yes
bind 127.0.0.1 -::1
requirepass <strong-password>
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG "rename-config-command"
```

## TLS Peer Certificate Authentication (new in 8.10)

Server-to-server TLS authentication using peer certificates. Enables certificate-based auth between cluster nodes and replicas without shared passwords.

**Config:**
```
tls-auth-clients yes
tls-require-cert yes
tls-ca-cert-file /path/to/ca.crt
```

## Gotchas

- **`requirepass` is a compatibility layer** — it sets the password for the `default` user. Prefer explicit ACL user definitions.
- **`ACL SAVE` writes to `aclfile`** — not `redis.conf`. The ACL file is separate.
- **Key patterns use glob matching** — `~users:*` matches `users:1000` but not `users:1000:profile`. Use `~*` for all keys.
- **`rename-command` is deprecated** — use ACLs instead. `rename-command` removes commands entirely, which can break tools.
- **TLS requires build flag** — `BUILD_TLS=yes` or `BUILD_TLS=module`. Not available in default builds.
- **`tls-auth-clients yes` requires proper CA setup** — clients must present certificates signed by the trusted CA.
- **ACL log grows unbounded** — monitor with `ACL LOG` and clear with `ACL LOG RESET`. Configured via `acllog-max-len` (default 128).
- **`protected-mode yes` blocks external connections** — unless `requirepass` is set or `bind` restricts to localhost.
- **Command categories are additive** — `+@read +@write` grants both. Use `-@dangerous` to revoke specific dangerous commands.

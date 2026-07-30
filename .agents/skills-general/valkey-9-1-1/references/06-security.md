# Security

Valkey provides multi-layered security through ACLs, authentication, network hardening, and TLS encryption.

## ACL System

The Access Control List system replaces the legacy `requirepass` with fine-grained per-user permissions.

### ACL Format

```
user <username> [rules...]
```

**Rules:**

| Rule | Description |
|---|---|
| `on` / `off` | Enable/disable the user |
| `+<command>` / `-<command>` | Allow/deny specific command |
| `+@<category>` / `-@<category>` | Allow/deny command category |
| `allcommands` / `nocommands` | Alias for `+@all` / `-@all` |
| `~<pattern>` | Key pattern (glob-style, e.g., `~users:*`) |
| `%R~<pattern>` | Key read pattern |
| `%W~<pattern>` | Key write pattern |
| `allkeys` / `resetkeys` | All keys / clear key patterns |
| `&<pattern>` | Pub/Sub channel pattern |
| `allchannels` / `resetchannels` | All channels / clear channel patterns |
| `><password>` | Add password |
| `<<password>` | Remove password |
| `nopass` | No password required |
| `resetpass` | Clear all passwords |
| `reset` | Full reset (pass, keys, channels, off, -@all) |
| `db=<0-16>` | Database-level access (since 9.1.0) |
| `(<options>)` | Create a selector with scoped permissions |

### Examples

```conf
# Full admin
user admin on >strongpassword allcommands allkeys allchannels

# Read-only application user
user app-read on >password +@read ~app:*

# Write user with specific key patterns
user app-write on >password +@all -@admin -@dangerous ~app:* %W~app:write:*

# Service account with no password (internal only)
user internal on nopass +@connection +ping +info ~*

# Disabled user
user deprecated off
```

### ACL Commands

```bash
# List all users
ACL LIST

# Get user details
ACL GETUSER username

# Create/modify user
ACL SETUSER username on >password +@all ~*

# Delete user
ACL DELUSER username

# Save to file
ACL SAVE

# Load from file
ACL LOAD

# Check permissions
ACL WHOAMI
ACL DRYRUN username COMMAND arg1 arg2

# ACL log (denied commands)
ACL LOG
ACL LOG RESET
```

### ACL File

```conf
# Use external ACL file (cannot mix with inline user definitions)
aclfile /etc/valkey/users.acl

# Max ACL log entries
acllog-max-len 128
```

### Database-level ACLs (since 9.1.0)

```conf
# Restrict user to specific databases
user dbuser on >password +@all ~* db=0 db=1
```

### Selectors (prefix-aware ACLs)

```conf
# Create scoped permission set
user multi on >password (+@read ~cache:*) (+@write ~session:*)
```

## Authentication

```bash
# Legacy (sets default user password)
AUTH <password>

# ACL-style
AUTH <username> <password>

# Via config
requirepass foobared
```

**Note:** `requirepass` is a compatibility layer — it sets the password for the `default` user. It is incompatible with `aclfile` and `ACL LOAD`.

## Network Security

```conf
# Bind to specific interfaces
bind 127.0.0.1 -::1

# Protected mode — reject non-local connections without auth
protected-mode yes

# Disable TLS/SSL port (use only TLS)
port 0
tls-port 6379

# Rename dangerous commands (deprecated, prefer ACLs)
rename-command CONFIG ""
rename-command FLUSHALL ""
```

## TLS/SSL

```conf
# Enable TLS
tls-port 6379

# Server certificate and key
tls-cert-file /etc/valkey/tls/valkey.crt
tls-key-file /etc/valkey/tls/valkey.key
# tls-key-file-pass <passphrase>

# CA for client authentication
tls-ca-cert-file /etc/valkey/tls/ca.crt

# Client certificate requirements
# tls-auth-clients yes       # required
# tls-auth-clients optional  # accepted but not required
# tls-auth-clients no        # not accepted

# Auto-authenticate clients from certificate
tls-auth-clients-user URI

# TLS for replication and cluster
tls-replication yes
tls-cluster yes

# Auto-reload TLS materials (seconds, 0 = disabled)
tls-auto-reload-interval 86400

# TLS versions (default: TLSv1.2 + TLSv1.3)
tls-protocols "TLSv1.2 TLSv1.3"

# Cipher suites
tls-ciphers DEFAULT:!MEDIUM
tls-ciphersuites TLS_CHACHA20_POLY1305_SHA256

# Server preference over client
tls-prefer-server-ciphers yes

# Session caching
tls-session-caching yes
tls-session-cache-size 20480
tls-session-cache-timeout 300
```

### Building with TLS

```bash
# Built-in TLS
make BUILD_TLS=yes

# TLS as loadable module
make BUILD_TLS=module
```

### Generating test certs

```bash
./utils/gen-test-certs.sh
```

### Connecting with TLS

```bash
./src/valkey-cli --tls \
  --cert ./tests/tls/valkey.crt \
  --key ./tests/tls/valkey.key \
  --cacert ./tests/tls/ca.crt
```

## Hardened Security Configs

```conf
# Block sensitive config changes at runtime
enable-protected-configs no

# Block DEBUG command
enable-debug-command no

# Block MODULE command (prevent loading modules at runtime)
enable-module-command no

# Hide user data from logs
hide-user-data-from-log yes
```

Values: `no` (block always), `yes` (allow always), `local` (allow from localhost only).

## Pub/Sub ACL

```conf
# Default channel permission for new users
# allchannels — grant access to all
# resetchannels — revoke all (default)
acl-pubsub-default resetchannels
```

## Security Best Practices

1. **Never expose Valkey directly to the internet** — use firewalls, VPNs, or private networks
2. **Use ACLs** — create specific users for each application with minimum required permissions
3. **Enable TLS** — encrypt data in transit, especially for replication and cluster
4. **Use strong passwords** — Valkey is fast enough that brute force is trivial with weak passwords
5. **Disable dangerous commands** — use ACLs rather than `rename-command`
6. **Enable `hide-user-data-from-log`** — prevents PII leakage in logs
7. **Monitor ACL log** — `ACL LOG` shows denied commands, useful for detecting attacks
8. **Use `sanitize-dump-payload`** — prevents RDB/RESTORE corruption attacks

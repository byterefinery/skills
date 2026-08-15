# pocketbase 0.39.11 — Installation & CLI

## Installation

- **Prebuilt binary** (recommended): download `pocketbase_<version>_<os>_<arch>.zip` (or `.tar.gz`) from the GitHub releases page, extract, run. The binary, `pb_data/`, `pb_hooks/`, `pb_migrations/` travel together.
- **From source / Go module**: `go 1.25+`, `go get github.com/pocketbase/pocketbase@v0.39.11`. The repo's `examples/base/main.go` is the program behind the prebuilt binaries (registers `jsvm`, `migratecmd`, `ghupdate` plugins + static file serving).

```bash
# build the minimal standalone executable like the release ones
cd examples/base && GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build
./base serve
```

## Directory layout (around the executable)

```
myapp/
├── pocketbase            # the executable
├── pb_data/              # data directory (default; --dir flag)
│   ├── data.db           # main SQLite DB (collections, records, settings, _migrations)
│   ├── auxiliary.db      # ephemeral data (activity logs, etc.)
│   ├── settings.json     # app settings (SMTP, S3, backups, rate limits, ...)
│   ├── files/            # uploaded files (local storage mode)
│   └── types.d.ts        # ambient TypeScript declarations for pb_hooks
├── pb_hooks/             # JS app hooks (*.pb.js / *.pb.ts)
├── pb_migrations/        # JS migration files (auto-generated with automigrate)
└── pb_public/            # optional static files served at / (SPA fallback optional)
```

Paths are resolved relative to the executable (or CWD when running via `go run`).

## CLI commands

```bash
pocketbase --help          # global flags: --dir, --dev, --encryptionEnv, --queryTimeout
pocketbase version
```

### `serve [domain(s)]`

Starts the web server (API + dashboard UI). No domain args → `127.0.0.1:8090`; with domain args → `0.0.0.0:80` + `0.0.0.0:443` with automatic Let's Encrypt cert issuance (www variants added/redirected automatically).

```bash
pocketbase serve --http=0.0.0.0:8090
pocketbase serve --https=0.0.0.0:443          # TLS; HTTP auto-redirects to HTTPS
pocketbase serve --origins=http://a.com,https://b.com   # CORS (default: *)
pocketbase serve my.example.com               # ACME-managed TLS for the domain
```

### `superuser`

Manage the `_superusers` collection:

```bash
pocketbase superuser upsert admin@example.com "pass123"   # create or update
pocketbase superuser create admin@example.com "pass123"
pocketbase superuser update admin@example.com "newpass"
pocketbase superuser delete admin@example.com
pocketbase superuser otp admin@example.com                 # print a one-time OTP code
pocketbase superuser ips 127.0.0.1 10.0.0.0/24             # superuser IP whitelist (empty args clears)
```

### `migrate`

```bash
pocketbase migrate up              # run all pending migrations
pocketbase migrate down [number]   # revert last N applied migrations
pocketbase migrate create name     # new blank migration template (JS or Go, per config)
pocketbase migrate collections     # snapshot of all current collections config
pocketbase migrate history-sync    # drop _migrations rows whose files no longer exist
```

### `update`

`pocketbase update` — self-update the executable to the latest GitHub release (ghupdate plugin; the prebuilt binary only).

## Global flags

| Flag | Default | Purpose |
|---|---|---|
| `--dir` | `<exe>/pb_data` | data directory |
| `--dev` | auto-on for `go run` | print logs and executed SQL to stderr |
| `--encryptionEnv` | none | env var name holding a 32-char key that encrypts sensitive settings |
| `--queryTimeout` | 30 (s) | default SELECT query timeout |

Prebuilt-binary extra flags (examples/base): `--hooksDir`, `--hooksWatch` (default true), `--hooksPool` (default 15), `--migrationsDir`, `--automigrate` (default true), `--publicDir`, `--indexFallback` (default true).

## Settings (Settings > in Dashboard, or `pb_data/settings.json`)

Top-level groups: `meta` (appName, appURL), `smtp`, `backups` (local or S3), `s3`, `rateLimits`, `trustedProxy` (headers for reverse proxy), `batch` (enable + limits), `logs` (maxDays, logAuthId, logIP), `superuserIPs`.

The `/api/settings` endpoint is superuser-only (`GET`, `PATCH`, plus `POST /api/settings/test/s3`, `POST /api/settings/test/email`, `POST /api/settings/apple/generate-client-secret`).

## Health check

`GET /api/health` — always returns 200 with `{"code":200,"message":"API is healthy.","data":{}}`; superusers additionally get `canBackup`, `realIP`, and `possibleProxyHeader` hints.

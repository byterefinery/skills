# 01 — Overview & Architecture

## Core Architecture

PocketBase is a single-process Go application that bundles:
- **SQLite database** — embedded, zero-config, WAL mode by default
- **HTTP server** — built on Go's `net/http.ServeMux`
- **Admin dashboard** — Svelte-based SPA served from the binary
- **REST API** — JSON-based, stateless
- **Realtime** — Server-Sent Events (SSE) over the same HTTP connection
- **Filesystem** — local disk or S3-compatible storage
- **Mail client** — SMTP or Unix sendmail
- **Cron scheduler** — built-in job scheduler
- **JS VM** — goja-based ES5 engine (prebuilt binary only)

## Directory Structure

```
myapp/
├── pocketbase              # executable
├── pb_data/                # application data (created on first run)
│   ├── data.db             # main SQLite database
│   ├── auxiliary.db        # logs, migrations tracking
│   ├── backups/            # generated backups
│   ├── files/              # uploaded files (local storage)
│   │   └── {collectionId}/
│   │       └── {recordId}/
│   │           └── filename_XXXXXX.ext
│   ├── types.d.ts          # TypeScript declarations for JS hooks
│   └── .notify/            # internal sync watcher
├── pb_hooks/               # JavaScript hook files (*.pb.js)
├── pb_migrations/          # JavaScript migration files
├── pb_public/              # static files served by the app
├── migrations/             # Go migration files (when using as framework)
└── main.go                 # Go entry point (when using as framework)
```

## Configuration

### Console flags

```bash
./pocketbase serve [domain]                         # start server
  --dir=./pb_data                                   # data directory
  --http=0.0.0.0:8090                              # HTTP address
  --dev                                             # dev mode (logs to stderr)
  --encryptionEnv=PB_ENCRYPTION_KEY                 # 32-char env var for settings encryption
  --queryTimeout=30                                 # SELECT queries timeout in seconds
  --hooksDir=./pb_hooks                             # JS hooks directory
  --hooksWatch=true                                 # auto-restart on hook change (UNIX)
  --hooksPool=15                                    # prewarmed JS runtime pool size
  --migrationsDir=./pb_migrations                   # JS migrations directory
  --automigrate=true                                # auto-generate migrations on collection changes
  --publicDir=./pb_public                           # static files directory
  --indexFallback=true                              # fallback to index.html for SPA
```

### Go Config

```go
app := pocketbase.NewWithConfig(pocketbase.Config{
    HideStartBanner:    false,
    DefaultDev:         false,
    DefaultDataDir:     "./pb_data",
    DefaultEncryptionEnv: "PB_ENCRYPTION_KEY",
    DefaultQueryTimeout:  30 * time.Second,
    DataMaxOpenConns:     1,
    DataMaxIdleConns:     1,
    AuxMaxOpenConns:      1,
    AuxMaxIdleConns:      1,
    DBConnect:            nil, // custom SQLite driver (optional)
})
```

## Data Directory (`pb_data`)

- **`data.db`** — main SQLite database containing all collections, records, settings
- **`auxiliary.db`** — system data: logs (`_logs`), migrations history (`_migrations`)
- **`files/`** — uploaded files organized by `collectionId/recordId/filename_XXXXXX.ext`
- **`backups/`** — generated backup ZIP archives
- **`types.d.ts`** — auto-generated TypeScript declarations for JS hooks (regenerated on each start)

## Application Lifecycle

```
pocketbase.New()
    ↓
app.OnServe().BindFunc(...)    // register hooks
app.OnRecordCreateRequest(...).BindFunc(...)
    ↓
app.Start()                     // registers serve + superuser commands
    ↓
pb.Bootstrap()                  // called automatically
    ├── Create data directory
    ├── Open DB connections
    ├── Load settings
    ├── Run system migrations
    ├── Run app migrations
    ├── Load collections
    └── Start cron scheduler
    ↓
HTTP server starts              // listens on configured address
    ↓
SIGTERM/SIGINT received
    ↓
OnTerminate() hooks fire        // cleanup
app.ResetBootstrapState()       // close DB, stop cron
```

## System Collections

PocketBase manages internal collections automatically:

| Collection | Purpose |
|---|---|
| `_superusers` | Admin accounts (auth collection) |
| `_logs` | Application log entries |
| `_migrations` | Applied migration tracking |
| `_api_keys` | API key records (if enabled) |
| `_auth_origins` | OAuth2 auth origin tracking |
| `_external_authents` | External OAuth2 authentication records |
| `_fields_map` | Internal field mapping metadata |
| `_mfas` | Multi-factor authentication sessions |

## SQLite PRAGMAs

Default PRAGMAs applied to each connection:

```sql
PRAGMA busy_timeout = 10000;
PRAGMA journal_mode = WAL;
PRAGMA journal_size_limit = 200000000;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA temp_store = MEMORY;
PRAGMA cache_size = -32000;
```

## Custom SQLite Driver

```go
app := pocketbase.NewWithConfig(pocketbase.Config{
    DBConnect: func(dbPath string) (*dbx.DB, error) {
        return dbx.Open("sqlite3", "file:"+dbPath+"?_pragma=journal_mode(WAL)")
    },
})
```

To exclude the default pure Go driver and reduce binary size (~4MB):
```bash
go build -tags no_default_driver
```

## Cross-compilation targets

```
darwin  amd64, arm64
freebsd amd64, arm64
linux   386, amd64, arm, arm64, loong64, ppc64le, riscv64, s390x
windows 386, amd64, arm64
```

Build: `CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build`

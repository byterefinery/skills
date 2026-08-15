---
name: pocketbase-0-39-8
description: PocketBase v0.39.8 — open-source Go backend with embedded SQLite, realtime subscriptions, built-in files and users management, Admin dashboard, and REST-ish API. Covers Go framework extension, JS VM hooks, collections, records, authentication, migrations, realtime, file storage, and production deployment. Use when working with PocketBase apps, extending with Go or JavaScript, managing collections and records, or deploying PocketBase services.
license: MIT
compatibility: Requires Go 1.25+ for framework extension. Prebuilt binary works standalone. JS hooks require no extra dependencies.
metadata:
  tags:
    - backend
    - go
    - javascript
    - sqlite
    - realtime
    - api
    - auth
    - database
---

# pocketbase 0.39.8

## Overview

PocketBase is an open-source Go backend that bundles an embedded SQLite database with realtime subscriptions, built-in files and users management, a convenient Admin dashboard UI, and a simple REST-ish API. It can be used as a standalone prebuilt executable or as a Go framework/toolkit for building custom portable applications.

Two extension paths exist:
- **Go** — full control, better performance, access to any Go library. Use `pocketbase.New()` and register hooks via `app.OnServe()`, `app.OnRecordCreateRequest()`, etc.
- **JavaScript (JSVM)** — embedded ES5 engine via goja. Write `*.pb.js` files in `pb_hooks/` directory. camelCase APIs mirror Go equivalents. Prebuilt binary includes JSVM by default.

Core concepts:
- **Collections** — SQLite tables, three types: `base`, `view`, `auth`
- **Records** — individual rows within a collection
- **API Rules** — expression-based access controls per collection action (list, view, create, update, delete)
- **Realtime** — Server-Sent Events for record changes and custom topics
- **Filesystem** — local disk or S3-compatible storage abstraction

## Usage

### Standalone binary

```bash
# Download and run
./pocketbase serve                    # starts on :8090
./pocketbase serve yourdomain.com     # auto TLS with Let's Encrypt
./pocketbase serve --http=0.0.0.0:8080
./pocketbase superuser create EMAIL PASS
```

### Go framework

```go
package main

import (
    "log"
    "github.com/pocketbase/pocketbase"
    "github.com/pocketbase/pocketbase/core"
)

func main() {
    app := pocketbase.New()

    app.OnServe().BindFunc(func(se *core.ServeEvent) error {
        se.Router.GET("/hello", func(e *core.RequestEvent) error {
            return e.String(200, "Hello world!")
        })
        return se.Next()
    })

    if err := app.Start(); err != nil {
        log.Fatal(err)
    }
}
```

### JavaScript hooks

```javascript
// pb_hooks/main.pb.js
routerAdd("GET", "/hello", (e) => {
    return e.string(200, "Hello world!")
})

onRecordAfterUpdateSuccess((e) => {
    console.log("updated...", e.record.get("email"))
    e.next()
}, "users")
```

### Client SDKs

```javascript
// JavaScript SDK
import PocketBase from 'pocketbase'
const pb = new PocketBase('http://127.0.0.1:8090')
const record = await pb.collection('articles').create({ title: 'Hello' })
```

```dart
// Dart SDK
import 'package:pocketbase/pocketbase.dart'
final pb = PocketBase('http://127.0.0.1:8090')
final record = await pb.collection('articles').create({'title': 'Hello'})
```

## Gotchas

- **`e.App` vs parent scope `app`** — inside hook handlers, always use `e.App` (Go) or `e.app` (JS) to access the app instance. Using a parent-scope variable can cause deadlocks since hooks run inside DB transactions.
- **JS handler scope isolation** — each JS handler is serialized and executed in its own isolated context. Variables declared outside handlers are not accessible inside. Use `require()` with `__hooks` path for shared modules.
- **JS engine is not Node.js** — no `window`, `fs`, `fetch`, `buffer`, `setTimeout`, `setInterval`. Only CommonJS `require()` is supported (no ESM without bundling).
- **Fields are non-nullable** — all fields except `JSONField` use zero-default values (empty string, 0, false). JSONField defaults to `null`.
- **API rules also filter records** — listRule acts as both access control and data filter. Unsatisfied listRule returns 200 with empty items; unsatisfied view/update/delete returns 404; locked rules return 403 for non-superusers.
- **Superusers bypass all rules** — authenticated superusers can access and modify everything. Collection API rules are completely ignored for them.
- **No server-side sessions** — PocketBase is fully stateless. Auth tokens are JWTs, not stored on the server. "Logout" means clearing the token client-side.
- **Backup sets read-only mode** — during backup ZIP generation, the app is temporarily read-only. For large pb_data (2GB+), consider `sqlite3 .backup` + `rsync` strategy instead.
- **Relative paths in JS** — relative file paths resolve from CWD, not from `pb_hooks/`. Use `__hooks` global variable for absolute path to hooks directory.
- **Date format is RFC3399** — all dates follow `Y-m-d H:i:s.uZ` format (e.g., `2024-11-10 18:45:27.123Z`). Date comparisons are string-based.
- **`go run` auto-enables dev mode** — when running with `go run`, dev mode is automatically enabled (prints logs and SQL to console). Production builds with `go build` do not have this.
- **Realtime idle timeout is 5 minutes** — with absolute max of 30 minutes (`RealtimeConnectRequestEvent.MaxTimeout`). Connections auto-reconnect.
- **Cron system jobs** — `app.Cron()` is shared with system jobs (logs cleanup, auto-backups). IDs start with `__pb*__`. Avoid `RemoveAll()` or `Stop()`.
- **File upload max ~5MB default** — adjustable per field but large files degrade performance. Use S3 for large file storage.
- **MFA returns 401 with `mfaId`** — when MFA is enabled, first auth succeeds but returns 401 with `mfaId` in body. Second auth method must include the `mfaId`.

## References

- [01-overview-architecture](references/01-overview-architecture.md) — Core architecture, data model, directory structure, config
- [02-collections-fields](references/02-collections-fields.md) — Collection types, all 13 field types, API rules syntax
- [03-api-records](references/03-api-records.md) — REST API, CRUD operations, filters, sorting, pagination, expand
- [04-authentication](references/04-authentication.md) — Password, OTP, OAuth2, MFA, impersonation, API keys, tokens
- [05-go-framework](references/05-go-framework.md) — Go extension, event hooks, routing, records, collections, database
- [06-js-framework](references/06-js-framework.md) — JS VM, hooks, routing, records, global objects, limitations
- [07-migrations](references/07-migrations.md) — Go and JS migrations, collections snapshot, history sync
- [08-realtime](references/08-realtime.md) — Subscriptions, custom topics, client SDK realtime
- [09-files-storage](references/09-files-storage.md) — Upload, download, thumbs, S3, protected files
- [10-production-deploy](references/10-production-deploy.md) — Deployment, systemd, Docker, reverse proxy, security hardening

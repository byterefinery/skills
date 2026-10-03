# PocketBase overview

PocketBase is an open source Go backend consisting of an embedded SQLite database with realtime subscriptions, builtin authentication management, convenient admin dashboard UI, and a simple REST-ish JSON API. It can be used both as a **Go framework** and as a **standalone application**.

PocketBase is still pre-1.0 — full backward compatibility is not guaranteed. Read the changelog and apply manual migration steps when upgrading.

## Standalone binary

The prebuilt executable (from GitHub releases) is based on `examples/base/main.go` and ships with the JS VM plugin, `migrate`, and `update` commands enabled:

```bash
./pocketbase serve                  # starts on 127.0.0.1:8090
./pocketbase superuser create EMAIL PASS
```

On first start it generates an installer link (printed to the console) that opens in the browser to create the first superuser.

Default routes of the started server:

- `http://127.0.0.1:8090/` — serves static content from `pb_public/` (if the directory exists)
- `http://127.0.0.1:8090/_/` — superusers dashboard
- `http://127.0.0.1:8090/api/` — the REST-ish API

The executable manages two directories alongside it:

- `pb_data/` — application data: `data.db` (main SQLite), `auxiliary.db` (logs/ephemeral meta), `storage/` (uploaded files), `types.d.ts` (JSVM type declarations). Add to `.gitignore`.
- `pb_migrations/` — JS migration files with collection changes (can be committed).

## Go framework

PocketBase is a regular Go package; the result is still a single portable executable. Minimal example:

```go
package main

import (
    "log"
    "os"

    "github.com/pocketbase/pocketbase"
    "github.com/pocketbase/pocketbase/apis"
    "github.com/pocketbase/pocketbase/core"
)

func main() {
    app := pocketbase.New()

    app.OnServe().BindFunc(func(e *core.ServeEvent) error {
        // serves static files from pb_public (if exists)
        e.Router.GET("/{path...}", apis.Static(os.DirFS("./pb_public"), false))

        return e.Next()
    })

    if err := app.Start(); err != nil {
        log.Fatal(err)
    }
}
```

- Init deps: `go mod init myapp && go mod tidy`
- Run: `go run . serve`
- Static build: `CGO_ENABLED=0 go build`, then `./myapp serve`
- A bare Go app registers only `serve` and `superuser` commands; the release binary additionally registers `migrate`, `update`, and the JS VM (`jsvm.MustRegister(app, ...)`, `migratecmd.MustRegister(...)`, `ghupdate.MustRegister(...)` — see `examples/base/main.go`).

Config via `pocketbase.NewWithConfig(pocketbase.Config{...})`; notable options: `HideStartBanner`, `DefaultDev`, `DefaultDataDir` (default `./pb_data`), `DefaultEncryptionEnv`, `DefaultQueryTimeout`, `DataMaxOpenConns`/`DataMaxIdleConns`, `AuxMaxOpenConns`/`AuxMaxIdleConns`, `DBConnect` (custom SQLite driver — called twice, once for `data.db` and once for `auxiliary.db`).

Custom SQLite drivers: PocketBase uses the pure-Go `modernc.org/sqlite` (no CGO) by default. For ICU/FTS5 etc. register a driver like `github.com/mattn/go-sqlite3` (CGO) or `github.com/ncruces/go-sqlite3` via `dbx.RegisterDriver` + `Config.DBConnect`; call `core.DefaultDBConnect` inside the function to keep the built-in driver as fallback. `go build -tags no_default_driver` drops the pure-Go driver (~4MB) if you never fall back to it. Since v0.40.0 the DSN includes `_defensive=1` (SQLite defensive mode).

## v0.40.x notes

- Requires **Go 1.27+** (minimum version bumped in v0.40.0; migrated to `encoding/json/v2` — test locally before pushing updates to production).
- v0.40.1 only fixes two regressions from the v2 JSON migration (invalid-UTF8 mangling in JSON serialization, OAuth2 providers config merge) — safe minor bump, no manual steps.
- v0.40.0 also added `Cross-Origin-Opener-Policy: same-origin` to the default security headers and quotes the default `Content-Disposition` filename.
- `DELETE /api/logs` endpoint (truncate all logs without changing retention).
- New log settings: max `Log.Data` size (~16KB, truncated with `"__pb_truncated__":true` marker) and 8KB max log message.
- New `filesystem.NewWriter(key, opts)` helper + `OnNewWriter`/`OnDelete` hooks.
- Backups no longer transaction-lock the database during generation.
- Console command errors and recovered panics now propagate to `app.Start()` (non-zero exit) — a slight breaking change for chained commands (`&&`).
- `Record.GetInt64(field)` helper; `Store.Keys()` method.

## How to use it

- **Client-side SPA / mobile app + official SDK** is the primary design use case. Keep a single global SDK instance for the app lifetime; access control happens through collection API rules. See `03-api-rules-and-filters`.
- **Official SDKs**: JavaScript (`pocketbase/js-sdk` — browser, Node.js, React Native) and Dart (`pocketbase/dart-sdk` — web, mobile, desktop, CLI).
- **Server-side Node actions** (webhooks, extra validations): use a dedicated superuser client as a pure data store:

```js
import PocketBase from "pocketbase";
const superuserClient = new PocketBase('https://example.com');
superuserClient.autoCancellation(false); // shared client, async multi-user
await superuserClient.collection('_superusers').authWithPassword(EMAIL, PASS);
// or long-lived API key: superuserClient.authStore.save('SUPERUSER_TOKEN')
export default superuserClient;
```

- **JS SSR meta-frameworks** (SvelteKit/Nuxt/Next) with PocketBase behind them: possible but problematic — shared SDK instance state in a long-running server context, OAuth2 flow complications, duplicated realtime proxying, Node single-thread bottlenecks. Prefer a traditional client-side SPA or treat PocketBase as a pure data store for server-side actions.
- **htmx/Hotwire/Turbo**: not recommended — PocketBase's stateless JSON APIs lack SSR helpers (cookie/CORS/CSRF middlewares, custom auth endpoints). Collection API rules apply only to the builtin JSON routes.
- **Mobile auth persistence**: pass a custom async store (`AsyncAuthStore` in the JS SDK) so the token survives app restarts; Node/React Native need an `EventSource` polyfill for realtime (e.g. `react-native-sse`).

## Superusers

`_superusers` is a system auth collection (admins). Unlike regular auth collections: OAuth2 is not supported, and superusers ignore all collection API rules (full access). Manage them via the dashboard, the `superuser` CLI command, or `pb.collection('_superusers')`.

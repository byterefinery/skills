# pocketbase 0.39.11 — Go Extensions (PocketBase as a framework)

Contents: [Minimal app](#minimal-app) · [Event hooks](#event-hooks) · [Data access in Go](#data-access-in-go) · [Testing](#testing)

Import `github.com/pocketbase/pocketbase@v0.39.11` (Go 1.25+) and embed the backend in your own executable. The repo's `examples/base/main.go` is the canonical starting point (it's what the prebuilt binaries compile).

## Minimal app

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

    app.OnServe().BindFunc(func(se *core.ServeEvent) error {
        // custom route
        se.Router.GET("/hello", func(e *core.RequestEvent) error {
            return e.String(200, "Hello world!")
        })
        // serve static files from ./pb_public (SPA fallback: true)
        se.Router.GET("/{path...}", apis.Static(os.DirFS("./pb_public"), false))

        return se.Next()
    })

    if err := app.Start(); err != nil {
        log.Fatal(err)
    }
}
```

`app.Start()` registers the `serve` and `superuser` commands (plus `version`) and executes the CLI; `app.Bootstrap()` initializes resources (DB, settings) without starting a command. `pocketbase.NewWithConfig(pocketbase.Config{...})` exposes `DefaultDataDir`, `HideStartBanner`, DB connection limits, and a custom `DBConnect` func (called **twice**: for `pb_data/data.db` and `pb_data/auxiliary.db`) to plug alternate SQLite drivers (e.g. CGO `mattn/go-sqlite3` for ICU/FTS5).

Add the same plugins as the prebuilt binary:

```go
jsvm.MustRegister(app, jsvm.Config{ HooksDir: "", HooksWatch: true, HooksPoolSize: 15 })
migratecmd.MustRegister(app, app.RootCmd, migratecmd.Config{
    TemplateLang: migratecmd.TemplateLangGo, // or TemplateLangJS (needs jsvm)
    Automigrate:  false,
})
ghupdate.MustRegister(app, app.RootCmd, ghupdate.Config{})
```

Build: `CGO_ENABLED=0 go build` (pure-Go SQLite; supported targets: linux/darwin/freebsd + windows for amd64/arm64/arm/386/loong64/ppc64le/riscv64/s390x).

## Event hooks

All hooks: `hook.Bind(handler)` (handler has optional `Id`, `Priority`, required `Func`), `hook.BindFunc(fn)`, `hook.Unbind(id)` / `UnbindAll()`. Handlers are `func(e *T) error` and must call `e.Next()` to continue the chain; returning an error stops it.

Key hooks (full list in `core/app.go`):

- **App lifecycle**: `OnBootstrap`, `OnServe` (attach routes/middlewares), `OnTerminate`, `OnBackupCreate/Restore`
- **Model level** (any model: Record, Collection, Settings, ...): `OnModelValidate`, `OnModelCreate/Update/Delete`, `OnModelCreateExecute`/`...UpdateExecute`/`...DeleteExecute` (right before the SQL statement), and **`OnModelAfter{Create,Update,Delete}Success/Error`** — the `After*Success` hooks fire **only after the surrounding transaction commits** (delayed; not fired on rollback)
- **Record proxies**: `OnRecordEnrich` (add/hide fields for the current request — also used by realtime), `OnRecordValidate`, `OnRecordCreate/Update/Delete(+Execute/AfterSuccess/AfterError)`
- **Collection proxies**: `OnCollectionValidate/Create/Update/Delete(+Execute/After*)`
- **Request level**: `OnRecordCreateRequest`/`UpdateRequest`/`DeleteRequest`/`ViewRequest`/`RecordsListRequest`, `OnRecordAuth*Request` (all auth actions), `OnFileDownloadRequest`, `OnFileTokenRequest`, `OnRealtimeConnectRequest`/`SubscribeRequest`/`MessageSend`, `OnMailerSend` + per-template variants, `OnSettings*Request`, `OnBatchRequest`

Tagged hooks scope to collections/tables: `app.OnRecordAfterCreateSuccess("posts").BindFunc(...)`.

Firing order for a save: `OnModelCreate { OnModelValidate → OnModelCreateExecute }`; for a delete: `OnModelDelete { OnModelDeleteExecute }`.

**Pitfalls:** use `e.App` (event-scoped, possibly a transaction app) instead of the outer `app` variable inside handlers — the outer instance can deadlock; avoid global mutexes (handlers can be invoked recursively, e.g. cascade deletes).

## Data access in Go

```go
// records
app.FindRecordById("posts", "RECORD_ID")
app.FindFirstRecordByFilter("posts", "status={:status}", dbx.Params{"status": "public"})
app.FindRecordsByFilter("posts", "created >= {:c}", "-created", 10, 0, dbx.Params{"c": "2024-01-01"})
app.Save(record)              // validates + saves
app.SaveNoValidate(record)
app.RunInTransaction(func(txApp core.App) error { ... })

// collections
app.FindCollectionByNameOrId("posts")
app.FindCachedCollectionByNameOrId("posts") // read-only cache; don't mutate

// raw SQL (SELECTs route to the concurrent pool automatically)
app.DB().NewQuery("SELECT ...").One(&row)
app.AuxDB()                    // auxiliary.db (logs, etc.)
```

Request event helpers: `e.JSON(status, data)`, `e.String(...)`, `e.FileFS(...)`, `e.Redirect(...)`, `e.RealIP()`, `e.RequestInfo()`, `e.HasSuperuserAuth()`; middlewares: `apis.RequireSuperuserAuth()`, `apis.RequireAuth()`, `apis.RequireGuestOnly()`, `apis.BodyLimit(...)`, `apis.Gzip()`, `apis.CORS(...)`, `apis.Static(fsys, indexFallback)`, `apis.SkipSuccessActivityLog()`.

## Testing

The `tests` subpackage provides `tests.NewTestApp(dataDir)` (boots a full app against a test data dir, call `Cleanup()`) and `tests.ApiScenario` for table-driven API tests:

```go
func TestHello(t *testing.T) {
    scenarios := []tests.ApiScenario{{
        Name:           "as guest",
        Method:         http.MethodGet,
        URL:            "/my/hello",
        ExpectedStatus: 401,
        TestAppFactory: setupTestApp, // returns *tests.TestApp
    }}
    for _, sc := range scenarios {
        t.Run(sc.Name, func(t *testing.T) { sc.Test(t) })
    }
}
```

Typical flow: run the app once with a `test_pb_data/` dir, create fixtures in the Dashboard, commit `test_pb_data/`, then drive scenarios (guest / user token / superuser token) against it. Other helpers: `tests.MockMultipartData`, `tests.ApiSuccessResponse`/`tests.ApiErrorResponse`.

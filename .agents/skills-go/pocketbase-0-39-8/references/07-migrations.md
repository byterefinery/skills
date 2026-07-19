# 07 — Migrations

## Go Migrations

### Setup

```go
// main.go
package main

import (
    "log"

    "github.com/pocketbase/pocketbase"
    "github.com/pocketbase/pocketbase/plugins/migratecmd"
    "github.com/pocketbase/pocketbase/tools/osutils"

    _ "yourpackage/migrations"  // import migrations package
)

func main() {
    app := pocketbase.New()

    migratecmd.MustRegister(app, app.RootCmd, migratecmd.Config{
        Automigrate: osutils.IsProbablyGoRun(),  // auto-migrate only during dev
    })

    if err := app.Start(); err != nil {
        log.Fatal(err)
    }
}
```

### Create Migration

```bash
go run . migrate create "your_new_migration"
```

Generates `migrations/1655834400_your_new_migration.go`:

```go
package migrations

import (
    "github.com/pocketbase/pocketbase/core"
    m "github.com/pocketbase/pocketbase/migrations"
)

func init() {
    m.Register(func(app core.App) error {
        // up migration
        return nil
    }, func(app core.App) error {
        // down migration (optional)
        return nil
    })
}
```

### Run Migrations

```bash
go run . migrate up              # apply pending migrations
go run . migrate down            # revert last migration
go run . migrate down 3          # revert last 3 migrations
go run . migrate collections     # generate full collections snapshot
go run . migrate history-sync    # sync history with files on disk
```

Migrations auto-run on `serve`. Manual `migrate up/down` requires server restart.

### Migration Examples

**Raw SQL:**
```go
m.Register(func(app core.App) error {
    _, err := app.DB().NewQuery("UPDATE articles SET status = 'pending' WHERE status = ''").Execute()
    return err
}, nil)
```

**Create collection:**
```go
m.Register(func(app core.App) error {
    collection := core.NewAuthCollection("clients")
    collection.ListRule = types.Pointer("id = @request.auth.id")
    collection.ViewRule = types.Pointer("id = @request.auth.id")

    collection.Fields.Add(
        &core.TextField{ Name: "company", Required: true, Max: 100 },
        &core.URLField{ Name: "website", Presentable: true },
    )

    collection.PasswordAuth.Enabled = false
    collection.OTP.Enabled = true

    collection.AddIndex("idx_clients_company", false, "company", "")
    return app.Save(collection)
}, func(app core.App) error {
    collection, _ := app.FindCollectionByNameOrId("clients")
    return app.Delete(collection)
})
```

**Create superuser:**
```go
m.Register(func(app core.App) error {
    superusers, _ := app.FindCollectionByNameOrId(core.CollectionNameSuperusers)
    record := core.NewRecord(superusers)
    record.Set("email", "test@example.com")
    record.Set("password", "1234567890")
    return app.Save(record)
}, func(app core.App) error {
    record, _ := app.FindAuthRecordByEmail(core.CollectionNameSuperusers, "test@example.com")
    if record == nil { return nil }
    return app.Delete(record)
})
```

**Initialize settings:**
```go
m.Register(func(app core.App) error {
    settings := app.Settings()
    settings.Meta.AppName = "My App"
    settings.Meta.AppURL = "https://example.com"
    settings.Logs.MaxDays = 2
    return app.Save(settings)
}, nil)
```

**Collections snapshot:**
```bash
go run . migrate collections
```

Generates migration with `ImportCollectionsByMarshaledJSON(app, []byte{...}, false)`. Last argument `false` = extend mode (preserves missing collections/fields). Change to `true` to delete missing ones.

## JavaScript Migrations

### Setup

Prebuilt executable has `--automigrate=true` by default. JS migrations go in `pb_migrations/`.

```bash
./pocketbase migrate create "your_new_migration"
```

Generates `pb_migrations/1687801097_your_new_migration.js`:

```javascript
migrate((app) => {
    // up migration
}, (app) => {
    // down migration (optional)
})
```

### Commands

```bash
./pocketbase migrate up              # apply pending
./pocketbase migrate down            # revert last
./pocketbase migrate down 3          # revert last 3
./pocketbase migrate collections     # generate snapshot
./pocketbase migrate history-sync    # sync history
```

### JS Migration Examples

**Raw SQL:**
```javascript
migrate((app) => {
    app.db().newQuery("UPDATE articles SET status = 'pending' WHERE status = ''").execute()
})
```

**Create collection:**
```javascript
migrate((app) => {
    let collection = new Collection({
        type:     "auth",
        name:     "clients",
        listRule: "id = @request.auth.id",
        viewRule: "id = @request.auth.id",
        fields: [
            { type: "text", name: "company", required: true, max: 100 },
            { type: "url", name: "url", presentable: true },
        ],
        passwordAuth: { enabled: false },
        otp: { enabled: true },
        indexes: ["CREATE INDEX idx_clients_company ON clients (company)"],
    })
    app.save(collection)
}, (app) => {
    let collection = app.findCollectionByNameOrId("clients")
    app.delete(collection)
})
```

**Create superuser:**
```javascript
migrate((app) => {
    let superusers = app.findCollectionByNameOrId("_superusers")
    let record = new Record(superusers)
    record.set("email", "test@example.com")
    record.set("password", "1234567890")
    app.save(record)
}, (app) => {
    try {
        let record = app.findAuthRecordByEmail("_superusers", "test@example.com")
        app.delete(record)
    } catch {}
})
```

**Initialize settings:**
```javascript
migrate((app) => {
    let settings = app.settings()
    settings.meta.appName = "My App"
    settings.meta.appURL = "https://example.com"
    settings.logs.maxDays = 2
    app.save(settings)
})
```

## Migration History

Applied migrations tracked in `_migrations` table. During development with `--automigrate`, intermediate steps accumulate. Clean up:

1. Remove/squash unnecessary migration files
2. Run `migrate history-sync` to remove orphaned entries

## Collections Snapshot

```bash
# Go
go run . migrate collections

# JS (prebuilt)
./pocketbase migrate collections
```

Generates full collections state as a single migration file. Use for:
- Initial schema commit
- Syncing schema across environments
- Reverting to known good state

Extend mode (default): preserves collections/fields not in snapshot.
Delete mode: remove collections/fields not in snapshot (change last argument to `true`).

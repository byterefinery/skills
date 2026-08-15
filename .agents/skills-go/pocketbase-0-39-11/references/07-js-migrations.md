# pocketbase 0.39.11 — Migrations (JS)

User migrations live in `pb_migrations/` (default; `--migrationsDir` to change) as `*.js`/`*.ts` files. Each file has a single `migrate(upFunc, downFunc?)` call; both callbacks receive a **transactional app instance**. Unapplied migrations run automatically on `serve` (one transaction each); applied filenames are tracked in the `_migrations` table.

```js
// pb_migrations/1687801090_your_migration.js
migrate((app) => {
    // upgrade: runs once
}, (app) => {
    // optional downgrade to revert the upgrade
})
```

## CLI

```bash
pocketbase migrate up              # run all pending migrations
pocketbase migrate down [number]   # revert last N (restart serve afterwards to refresh cached collections)
pocketbase migrate create name     # scaffold a blank migration template
pocketbase migrate collections     # scaffold a full snapshot of current collections config
pocketbase migrate history-sync    # remove _migrations rows whose files no longer exist
```

`migrate collections` generates an `importCollections` call in **extend mode** (missing collections/fields preserved); pass `true` as the last arg of the generated `importCollections` to also delete missing ones.

## Automigrate (prebuilt binary default ON)

With `--automigrate` (default `true` in the prebuilt binary), every collection change made via Dashboard or Web API writes/updates a migration file in `pb_migrations/` automatically — handy locally, but it can clutter the migration history. For a clean history: remove/squash unwanted intermediate files, then `migrate history-sync`. Disable with `--automigrate=false`.

## Common patterns

```js
// raw SQL data migration
migrate((app) => {
    app.db().newQuery("UPDATE articles SET status = 'pending' WHERE status = ''").execute()
})

// initial settings
migrate((app) => {
    let settings = app.settings()
    settings.meta.appName = "myapp"
    settings.meta.appUrl = "https://example.com"
    app.save(settings)
})

// initial superuser
migrate((app) => {
    let superusers = app.findCollectionByNameOrId("_superusers")
    let record = new Record(superusers)
    record.set("email", $os.getenv("PB_SUPERUSER_EMAIL"))
    record.set("password", $os.getenv("PB_SUPERUSER_PASS"))
    app.save(record)
}, (app) => {
    try {
        let record = app.findAuthRecordByEmail("_superusers", "admin@example.com")
        app.delete(record)
    } catch { /* probably already deleted */ }
})

// create a collection
migrate((app) => {
    let collection = new Collection({
        type: "auth",
        name: "clients",
        listRule: "id = @request.auth.id",
        viewRule: "id = @request.auth.id",
        fields: [
            { type: "text", name: "company", required: true, max: 100 },
            { type: "url",  name: "url", presentable: true },
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

System fields (`id`, and auth fields on auth collections) are auto-initialized and merged with your config — don't redefine them.

## Go migrations

In Go apps the same runner works with Go migration files in `migrations/` (default dir for `TemplateLangGo`) registered via the `core.AppMigrations` list (`migratecmd` supports both `TemplateLangGo` and `TemplateLangJS`). System migrations (version bumps) always run as part of bootstrap.

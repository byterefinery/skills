# Extend with JavaScript (JS VM)

The prebuilt binary ships a Goja-based JS VM: put CommonJS-flavored JavaScript files in `pb_hooks/` (default) to extend the running app without Go. Every file matching `*.pb.js` or `*.pb.ts` in the directory is loaded (`main.pb.js` is just the conventional name from the docs examples); plain `*.js` files are *not* loaded as hooks — they are for modules you `require`. JS hooks mirror the Go hooks in camelCase, and Go exported names are camelCased (`app.FindRecordById` → `$app.findRecordById`).

## Global objects

- `__hooks` — absolute path to the `pb_hooks` directory
- `$app` — the running PocketBase app instance (records, collections, db, mailer, cron, log, settings, …)
- `$apis.*` — API routing helpers and middlewares (ex. `routerAdd("GET", "/hello", (e) => e.json(200, {...}))`, `$apis.requireAuth()`)
- `$os.*` — OS primitives (delete dirs, execute shell commands, …)
- `$security.*` — JWT create/parse, random strings, AES, …

Errors are thrown as regular JS exceptions (not returned as Go values).

## Example

```js
// pb_hooks/main.pb.js

routerAdd("GET", "/hello/{name}", (e) => {
    let name = e.request.pathValue("name")
    return e.json(200, { message: "Hello " + name })
})

onRecordAfterUpdateSuccess((e) => {
    console.log("user updated...", e.record.get("email"))
    e.next()
}, "users") // optional collection filter
```

Handlers are registered with an optional collection name as second argument, same as the Go hooks. Every handler receives the event object and must call `e.next()` to continue the chain.

## TypeScript declarations

`pb_data/types.d.ts` is generated with the JSVM types; reference it from your files for IDE completion:

```js
/// <reference path="../pb_data/types.d.ts" />
```

## Caveats

- **Handlers have no outer scope** — top-level variables in the same file are not visible inside handlers. For shared data, put it in a module and `require` it:
  ```js
  onBootstrap((e) => {
      e.next()
      const config = require(`${__hooks}/config.js`)
  })
  ```
- **Module loading** — `require` resolves from the current working directory, any `node_modules`, and any parent `node_modules`.
- **Relative paths** — resolved against the CWD, so prefer `` `${__hooks}/...` `` or absolute paths.
- Files are reloaded automatically on change in dev (`--hooksWatch`, disabled on Windows).

## Records / collections (JS)

```js
const record = await $app.findRecordById("articles", "RECORD_ID") // or findFirstRecordByData / findFirstRecordByFilter
const records = await $app.findRecordsByFilter("articles", filter, "-published", 10, 0, params)

const newRecord = $app.newRecord(collection) // core.NewRecord equivalent
newRecord.set("title", "Lorem")
newRecord.set("tags+", "id123")              // field modifiers work
await $app.save(newRecord)                    // $app.saveNoValidate / $app.delete(record)

// typed getters: get, getBool, getString, getInt, getInt64, getFloat, getDateTime, getStringSlice,
// getUnsavedFiles, expandedOne, expandedAll, publicExport
// auth: record.isSuperuser(), record.email()/setEmail, record.verified(), record.tokenKey(),
//        record.refreshTokenKey(), record.newAuthToken(), record.newStaticAuthToken(...)
```

Transactions: `$app.runInTransaction((txApp) => { ... })`.

## Hooks

camelCase versions of all Go hooks (see `07-go-framework` for semantics): `onBootstrap`, `onServe`-style routing via `$apis.routerAdd`/`routerAdd`, `onSettingsReload`, `onBackupCreate`, `onTerminate`, mailer hooks (`onMailerSend`, `onMailerRecord*Send`), realtime hooks, record model hooks (`onRecordEnrich`, `onRecordValidate`, `onRecordCreate/Update/Delete` + `Execute`/`After*Success`/`After*Error`), collection model hooks, and request hooks (`onRecordsListRequest`, `onRecordViewRequest`, `onRecordCreateRequest`, … auth request hooks, `onBatchRequest`).

## JS migrations

`pb_migrations/<timestamp>_<name>.js` files (created with `./pocketbase migrate create "name"`; the JSVM plugin also auto-generates them on collection changes when automigrate is enabled):

```js
// pb_migrations/1687801097_your_new_migration.js
migrate((app) => {
    // up — run once
    app.db().newQuery("UPDATE articles SET status = 'pending' WHERE status = ''").execute()
}, (app) => {
    // down
})
```

- `./pocketbase migrate up` — run pending migrations; `migrate down [n]`, `migrate collections` (snapshot), `migrate history-sync`
- `--automigrate` (default on) auto-generates migration files on collection changes
- `app.db()` supports the same query builder as Go (`app.db().select(...).from(...).andWhere(...).all()`)

## Other JSVM pages

`$os.*` (exec commands, file system), `$security.*` (jwt, aes, random), `$apis.*` (middlewares, static files), custom rendering/emails/HTTP requests all mirror the Go APIs — see the `js-*` docs pages for exact signatures (the `jsvm` typedoc reference in the site repo has the complete JSVM API).

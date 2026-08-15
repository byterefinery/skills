# pocketbase 0.39.11 — JS Hooks (pb_hooks)

The prebuilt binary (and the `examples/base` Go app) registers the `jsvm` plugin: an embedded goja JS engine for server-side JavaScript. Drop `*.pb.js` (or `*.pb.ts`) files into `pb_hooks/` next to the executable — files load in filename sort order, and the app **auto-restarts on file change** (UNIX only; `--hooksWatch=false` to disable).

## Handler basics

Every handler is `function(e) { ... e.next() }`. Throwing an error or omitting `e.next()` stops the hook chain (and the default action).

```js
onRecordAfterUpdateSuccess((e) => {
    console.log("user updated:", e.record.get("email"))
    e.next()
}, "users")   // optional tags: collection id/name (fires only for those)
```

JS names are camelCase versions of the Go API: `app.FindRecordById(...)` → `$app.findRecordById(...)`. Errors are thrown as JS exceptions, not returned.

**Isolation:** each handler is serialized and executed in its own context as a separate "program" — you cannot reference variables/functions declared outside the handler body. Share code by exporting CommonJS modules from `pb_hooks/` and `require()`-ing them inside handlers (module registry is shared; avoid mutating module state). Relative paths resolve against the **CWD**, not `pb_hooks` — use the `__hooks` global for absolute paths.

**Not Node.js:** no `setTimeout`/`setInterval`, `fetch`, `fs`, `window`; CommonJS `require` only (ESM needs bundling). `require("name")` searches CWD then `node_modules` (incl. parents).

## Registration helpers (top-level)

```js
// event hooks — camelCase of the Go On* hooks, e.g.:
onBootstrap((e) => { e.next(); console.log("started") })
onServe((e) => { e.next() })                    // register extra routes before server start
onRecordValidate((e) => { e.next() }, "posts")
onRecordAfterCreateSuccess((e) => { e.next() }, "posts", "comments")
onRecordCreateRequest((e) => { e.next() })      // request-level hooks (before/after the API action)
onModelAfterUpdateSuccess / onCollectionAfterDeleteSuccess / ... // all model/collection variants
onMailerSend((e) => { e.next() })               // email hooks
onRealtimeMessageSend / onRealtimeSubscribeRequest / onRealtimeConnectRequest
onBatchRequest / onSettingsUpdateRequest / onFileDownloadRequest / ...
// full list mirrors core.App (see Go source core/app.go)

// custom routes + middlewares (Go net/http ServeMux pattern syntax)
routerAdd("GET", "/hello/{name}", (e) => {
    return e.json(200, { "message": "Hello " + e.request.pathValue("name") })
})
routerAdd("POST", "/api/myapp/settings", handler, $apis.requireAuth())  // middleware
routerUse($apis.requireSuperuserAuth())  // global middleware (affects all routes)

// cron jobs
cronAdd("hello", "*/2 * * * *", () => { console.log("hi") })  // id, cron expr, handler
cronRemove("hello")

// custom CLI command
$app.rootCmd.addCommand(new Command({
    use: "hello",
    run: (cmd, args) => { console.log("Hello!") },
}))
```

Route patterns: `[METHOD ][HOST]/PATH` with `{param}` and `{param...}` wildcards; trailing `/` = prefix match; `{$}` = exact (e.g. `/static/{$}`). Prefix custom API routes with your app name (`/api/myapp/...`) to avoid collisions.

Request access in handlers: `e.request` (Go `*http.Request`), `e.auth` / `e.hasSuperuserAuth()`, `e.requestInfo()` (summarized request incl. `auth`, `query`, `body`, `context`), `e.response`, `e.json(status, data)`, `e.text(status, body)`, `e.file(...)`, `e.redirect(status, url)`, `e.next()`.

## Common globals

| Global | Purpose |
|---|---|
| `$app` | the app instance — `findRecordById(coll, id)`, `findFirstRecordByFilter(coll, filter, params)`, `findRecordsByFilter(...)`, `save(model)`, `delete(model)`, `runInTransaction(fn)`, `db()` (dbx), `settings()`, `newMailClient()`, `cron()`, `dataDir()` |
| `$apis.*` | `requireAuth()`, `requireSuperuserAuth()`, `requireGuestOnly()`, `requireSuperuserOrOwnerAuth()`, `static(fs, indexFallback)`, `gzip()`, `bodyLimit(size)`, `skipSuccessActivityLog()`, `enrichRecord/e.enrichRecords(e, record)`, `recordAuthResponse(...)` |
| `$os.*` | `getenv()`, `writeFile()`, `readFile()`, `mkdir()`, `exec()` (shell), `exists()`, ... |
| `$security.*` | `randomString(n)`, `randomInt()`, JWT `generateJWT`/`parseJWT`, AES `encrypt`/`decrypt` |
| `$mails` / `$filesystem` / `$filepath` / `$http` / `$dbx` | `$mails.sendRecordPasswordReset/Verification/ChangeEmail/OTP/AuthAlert(...)` (builtin email senders), filesystem helpers, path ops, http constants, dbx query helpers |
| `__hooks` | absolute path of the `pb_hooks` directory |
| `Record`, `Collection`, `DynamicModel`, `Command`, `Context` | model constructors: `new Record(collection)`, `record.set("f", v)`, `record.get("f")`, `record.expand("rel")` |
| `nullString()`, `nullInt()`, `nullBool()`, `nullFloat()`, `nullArray()`, `nullObject()` | nullable field markers for `DynamicModel` |
| `arrayOf(dynModel)`, `unmarshal(data, dst)`, `toString/toBytes/readerToString`, `sleep(ms)` | DB row mapping & helpers |

JS `db()` example:

```js
$app.db().newQuery("DELETE FROM articles WHERE status = 'archived'").execute()

const row = new DynamicModel({ "id": "", "total": 0 })
$app.db().newQuery("SELECT id, count(1) as total FROM posts GROUP BY id").one(row)
```

## TypeScript

`pb_data/types.d.ts` holds ambient declarations (auto-generated). Add `/// <reference path="pb_data/types.d.ts"/>` at the top of your `.pb.js` file, or rename it to `.pb.ts` for editor autocomplete/linting.

## Performance

A prewarmed pool of 15 goja runtimes executes handlers (`--hooksPool=N` to adjust). Keep heavy computation in Go bindings (`$security.randomString`, `$app.db()`) rather than pure JS (no concurrency inside one handler).

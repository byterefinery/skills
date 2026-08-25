# Extend with Go

PocketBase as a Go package: create an app instance with `pocketbase.New()` (or `pocketbase.NewWithConfig(config)`), register business logic via event hooks, then `app.Start()`. See `01-overview` for the minimal `main.go` and custom SQLite driver setup.

## Event hooks

Hooks support `Bind(handler)` (handler: optional `Id`, optional `Priority` — default 0, required `Func`) and `BindFunc(fn)`. Handlers call `e.Next()` to continue the chain; returning an error aborts it. Most model/request hooks accept optional collection names as arguments to scope them: `app.OnRecordCreateRequest("articles")`.

### App hooks

- `OnBootstrap` — after the app is initialized (before serving)
- `OnServe` — register routes: `e.Router.GET("/hello", func(e *core.RequestEvent) error {...})` (also `POST/PUT/PATCH/DELETE/GET/Any` etc.); `e.Router.HasRoute(...)` to check
- `OnSettingsReload`
- `OnBackupCreate` / `OnBackupRestore`
- `OnTerminate` — graceful shutdown
- `OnRealtimeConnectRequest` / `OnRealtimeSubscribeRequest` / `OnRealtimeMessageSend`
- `OnRecordsListRequest` / `OnRecordViewRequest` / `OnRecordCreateRequest` / `OnRecordUpdateRequest` / `OnRecordDeleteRequest` — the Web API request handlers (`*core.RecordRequestEvent`: `e.Record`, `e.Auth`, `e.HasSuperuserAuth()`, `e.BadRequestError(...)` etc.)
- `OnBatchRequest`
- Auth request hooks: `OnRecordAuthRequest`, `OnRecordAuthRefreshRequest`, `OnRecordAuthWithPasswordRequest`, `OnRecordAuthWithOAuth2Request`, `OnRecordAuthWithOTPRequest`, `OnRecordRequestOTPRequest`, `OnRecordRequestPasswordResetRequest`, `OnRecordConfirmPasswordResetRequest`, `OnRecordRequestVerificationRequest`, `OnRecordConfirmVerificationRequest`, `OnRecordRequestEmailChangeRequest`, `OnRecordConfirmEmailChangeRequest`

### Record model hooks (per create/update/delete)

`OnRecordEnrich` (populate default values before validation), `OnRecordValidate`, then per action: `OnRecordCreate` / `OnRecordCreateExecute` / `OnRecordAfterCreateSuccess` / `OnRecordAfterCreateError` (same pattern for Update and Delete). The model hooks receive `*core.RecordEvent` (`e.App`, `e.Record`, `e.Type`, `e.Context`); the `After*Error` variants receive `*core.RecordErrorEvent` (adds `e.Error`).

### Collection hooks

`OnCollectionValidate`, `OnCollectionCreate(+Execute/AfterCreateSuccess/AfterCreateError)`, `OnCollectionUpdate(...)`, `OnCollectionDelete(...)` — they receive `*core.CollectionEvent` (`e.App`, `e.Collection`, `e.Type`).

### Mailer hooks

`OnMailerSend` (all mails), plus per purpose: `OnMailerRecordAuthAlertSend`, `OnMailerRecordPasswordResetSend`, `OnMailerRecordVerificationSend`, `OnMailerRecordEmailChangeSend`, `OnMailerRecordOTPSend` — mutate `e.Message` (e.g. `e.Message.Subject += "..."`) before `e.Next()`. The record variants receive `*core.MailerRecordEvent` (`e.App`, `e.Mailer`, `e.Message`, `e.Record`, `e.Meta`).

## Records

```go
// fetch
record, err := app.FindRecordById("articles", "RECORD_ID")
record, err := app.FindFirstRecordByData("articles", "slug", "test")
record, err := app.FindFirstRecordByFilter("articles", "status = 'public' && category = {:category}", dbx.Params{"category": "news"})

records, err := app.FindRecordsByIds("articles", []string{"ID1", "ID2"})
total, err := app.CountRecords("articles", dbx.HashExp{"status": "pending"})
records, err := app.FindAllRecords("articles", dbx.HashExp{"status": "pending"})
records, err := app.FindRecordsByFilter("articles", filter, "-published", 10, 0, dbx.Params{...}) // sort, limit, offset

// query builder style
err := app.RecordQuery().
    AndWhere(dbx.HashExp{"system": true}).
    OrderBy("created DESC").
    All(&records)

// create / update / delete
collection, _ := app.FindCollectionByNameOrId("articles")
record := core.NewRecord(collection)
record.Set("title", "Lorem ipsum")
record.Set("slug:autogenerate", "post-")      // field modifiers work too
record.Set("documents", []*filesystem.File{f1, f2})
err = app.Save(record)                        // or app.SaveNoValidate(record)
err = app.Delete(record)

// transaction (rollback on returned error)
app.RunInTransaction(func(txApp core.App) error {
    ...txApp.Save(record)...
    return nil
})

// auth tokens (auth collections)
token, _ := record.NewAuthToken()
token, _ := record.NewVerificationToken()
token, _ := record.NewPasswordResetToken()
token, _ := record.NewEmailChangeToken(newEmail)
token, _ := record.NewFileToken()
token, _ := record.NewStaticAuthToken(duration) // nonrenewable (impersonation/API keys)
record, _ := app.FindAuthRecordByToken("YOUR_TOKEN", core.TokenTypeAuth)

// check access (respects API rules) — rule + requestInfo from a request event
info, _ := e.RequestInfo()
ok, _ := app.CanAccessRecord(record, info, record.Collection().ViewRule)
// custom rule: rule := types.Pointer("@request.auth.id != '' || status = 'public'")
```

Field values: `record.Get/GetString/GetInt/GetInt64/GetFloat/GetBool/GetDateTime/GetGeoPoint(...)`, `record.GetStringSlice`, `record.GetRaw`, and for file fields `record.GetUnsavedFiles(field)` / `record.GetUploadedFiles(field)`. There are no `GetSelect`/`GetFiles`/`GetRelationIDs` helpers — relations and selects are stored as id strings/slices, so use `GetString`/`GetStringSlice`/`Get`. `record.Hide("password")` / `record.Unhide(...)` control serialization; `record.PublicExport()` returns the JSON-safe data map. `record.IsNew()` (insert vs update), `record.Fresh()` (reset to last DB state), `record.Original()` (state before the current changes), `record.Clone()`. Auth records add: `Email()`, `SetEmail`, `EmailVisibility()`, `Verified()`/`SetVerified`, `TokenKey()`/`SetTokenKey`/`RefreshTokenKey`, `SetPassword`, `SetRandomPassword`, `ValidatePassword`, `IsSuperuser()`.

Intercepting a Web API request:

```go
app.OnRecordCreateRequest("articles").BindFunc(func(e *core.RecordRequestEvent) error {
    if e.HasSuperuserAuth() {
        return e.Next()
    }
    e.Record.Set("status", "pending") // overwrite submitted value
    return e.Next()
})
```

Programmatically expanding relations:

```go
errs := app.ExpandRecord(record, []string{"author", "categories"}, nil)
log.Println(record.ExpandedOne("author"))    // single relation
log.Println(record.ExpandedAll("categories")) // multi relation
```

## Collections

```go
collection, err := app.FindCollectionByNameOrId("example")
allCollections, err := app.FindAllCollections()
authAndViews, err := app.FindAllCollections(core.CollectionTypeAuth, core.CollectionTypeView)
// custom query: app.CollectionQuery().AndWhere(...).OrderBy(...).All(&collections)
```

`core.Collection` properties: `Id`, `Name`, `Type` ("base"/"view"/"auth"), `System`, `Fields` (`core.FieldsList`), `Indexes`, `ListRule/ViewRule/CreateRule/UpdateRule/DeleteRule` (`*string`), plus for auth collections `Options` (manageRule, auth token config, password/otp/mfa/oauth2 options, email templates).

Create programmatically: `core.NewCollection(name, core.CollectionTypeBase)` (or the direct `core.NewBaseCollection` / `core.NewAuthCollection` / `core.NewViewCollection`), build the field list with `core.NewFieldsList(&core.TextField{Name: "title"}, &core.BoolField{Name: "active"}, ...)` — fields are the concrete `core.*Field` types (`BoolField`, `TextField`, `NumberField`, `SelectField`, `RelationField`, `FileField`, `DateField`, `EmailField`, `EditorField`, `URLField`, `JSONField`, `AutodateField`, `GeoPointField`); the `core.Fields` registry maps type strings to their constructors. Assign `collection.Fields`, then `app.Save(collection)`; `app.Delete(collection)`. `collection.Indexes` is a JSON array of index definitions (`dbutils.Index` can parse/build them); a UNIQUE single-column index is required for non-email auth identity fields.

## Database

```go
// raw query — always use "{:name}" placeholders with dbx.Params, never string-concatenate input
res, err := app.DB().NewQuery("DELETE FROM articles WHERE status = 'archived'").Execute()
user := User{}
err := app.DB().NewQuery("SELECT * FROM users WHERE id = {:id}", dbx.Params{"id": "ID"}).One(&user)
rows := []User{}
err := app.DB().NewQuery("SELECT * FROM articles WHERE status = {:status}", dbx.Params{"status": "active"}).All(&rows)

// builder
users := []struct{ Id, Email string `db:"-" json:"-"` }{}
app.DB().Select("id", "email").From("users").
    AndWhere(dbx.Like("email", "example.com")).
    Limit(100).OrderBy("created ASC").All(&users)
// also: AndSelect/Distinct, Join/InnerJoin/LeftJoin, OrWhere, AndOrderBy, GroupBy, Having, Offset
// query methods: One(&dest), All(&slice), Row(&a, &b, ...), Column(&v), Rows(), Execute()
```

Structs need `db` + `json` tags. `app.RunInTransaction(...)` covers DB ops too. `dbx` expressions: `dbx.HashExp{"col": value}`, `dbx.NewExp("expr", params...)`, `dbx.Like("col", pattern)`, `dbx.In("col", values...)`, `dbx.NotIn(...)`. `app.AuxDB()` targets `auxiliary.db` (logs, ephemeral data) instead of the main `data.db`.

## Filesystem

```go
// local or S3 filesystem based on the app settings; call Close() when done
fs, err := app.NewFilesystem()               // record files ("storage")
backupsFs, err := app.NewBackupsFilesystem() // backups filesystem
fs.Upload([]byte("..."), "dir/file.txt")
fs.UploadFile(f, "dir/file.txt")
fs.UploadMultipart(fh, "dir/file.txt")
reader, err := fs.GetReader("dir/file.txt")
fs.Copy("src", "dst")
fs.Delete("dir/file.txt")
fs.CreateThumb("original.png", "thumb.png", "100x0")
```

`app.NewFilesystem()` (and `NewBackupsFilesystem`) is a **factory** returning `(*filesystem.System, error)` — there is no `app.FileStorage()` in v0.40. File factories: `filesystem.NewFileFromPath` / `NewFileFromBytes` / `NewFileFromMultipart` / `NewFileFromURL(ctx, url)` — each returns `(*File, error)`. Setting a file field on a record and `app.Save` handles old-file cleanup automatically; the lower-level `OnNewWriter`/`OnDelete` hooks (v0.40.0+) can intercept new/removed files.

## Jobs (cron)

```go
app.Cron().MustAdd("hello", "*/2 * * * *", func() { log.Println("Hello!") })
// also: app.Cron().Add(id, expr, fn) (returns error), Remove(id), RemoveAll(),
//       Jobs() []*Job, Total(), Stop(), Start(), SetInterval(d), SetTimezone(loc)
// jobs are listed/run via Dashboard or POST /api/crons/{jobId}
```

Cron expressions support lists, steps, ranges, and macros.

## Mails

```go
message := &mailer.Message{
    From: mail.Address{Address: app.Settings().Meta.SenderAddress, Name: app.Settings().Meta.SenderName},
    To:   []mail.Address{{Address: "dest@example.com"}},
    Subject: "Hi",
    Body:    "text/html body",
    TextBody: "plain text alternative",
}
client := app.NewMailClient() // SMTP if Settings().SMTP.Enabled, otherwise Sendmail; OnMailerSend is wired in
err := client.Send(message)
```

Override system mails via the `OnMailerRecord*Send` hooks (mutate `e.Message`); every mail also passes through `OnMailerSend` (`*core.MailerEvent`: `e.App`, `e.Mailer`, `e.Message`).

## Logging

```go
// app.Logger() returns a standard library *slog.Logger
app.Logger().Debug/Info/Warn/Error(message, key, value, ...)
logger := app.Logger().With(key, value, ...) // preset attributes
```

Intercept application log entries with `app.OnModelCreate(core.LogsTableName)` (the model is `*core.Log` — `Level`, `Message`, `Data`); configure retention (`maxDays`) and other log settings in Dashboard → Settings (`app.Settings().Logs`). Since v0.40.0: max log data size (~16KB, truncated with `"__pb_truncated__":true`) and 8KB max message.

## Rendering (templates)

```go
import "github.com/pocketbase/pocketbase/tools/template"

registry := template.NewRegistry().AddFuncs(template.FuncMap{"myFunc": func() string { return "..." }})
html, err := registry.LoadFiles("views/base.html", "views/partial.html").Render(data)
```

Layouts via template `define`/`template` blocks; `LoadFS(fsys, globPatterns...)` and `LoadString(text)` are the other two loading modes. Serve the result from a route with `e.String(200, html)` or `e.HTML(200, html)` (they set the Content-Type).

## Routing

In `OnServe`: `e.Router.GET("/path/{param}", handler).Bind(apis.RequireAuth())`. Public middlewares: `apis.RequireAuth(collectionNames...)` (optional collection scoping), `apis.RequireSuperuserAuth()`, `apis.RequireGuestOnly()`, `apis.RequireSuperuserOrOwnerAuth(ownerIdPathParam)`, `apis.RequireSameCollectionContextAuth(collectionPathParam)`, `apis.Static(fsys, indexFallback)`. Paths support `{param}` segments and `{path...}` wildcards; check an existing route with `e.Router.HasRoute(method, path)`. CORS, rate-limiting, body-size limits, GZIP and security headers are built in — no manual middleware needed for the builtin routes.

Inside a `*core.RequestEvent`: `e.Request.PathValue("param")`, `e.Request.URL.Query()`, headers, `e.FindUploadedFiles("fileKey")` (returns `[]*filesystem.File`), `e.RealIP()` (honors the TrustedProxy settings), `e.Auth` (authenticated record, nil for guests), `e.HasSuperuserAuth()`, `e.BindBody(&myStruct)` (form/JSON binding), and `e.RequestInfo()` — the `*core.RequestInfo` bundle (`Query`, `Headers`, `Body`, `Auth`, `Method`, `Context`) used for rule evaluation. Responses: `e.String(200, "ok")`, `e.HTML(...)`, `e.JSON(200, data)`, `e.XML(...)`, `e.Blob(status, contentType, b)`, `e.FileFS(fsys, name)`, `e.Redirect(status, url)`, `e.NoContent(status)`, `e.Stream(...)`; errors: `e.BadRequestError(msg, errData)`, `e.UnauthorizedError(...)`, `e.ForbiddenError(...)`, `e.NotFoundError(...)`, `e.TooManyRequestsError(...)`, `e.InternalServerError(...)` (all return `*ApiError`).

## Realtime (custom topics)

```go
message := subscriptions.Message{Name: "example", Data: rawJSON}
for _, chunk := range app.SubscriptionsBroker().ChunkedClients(300) {
    for _, client := range chunk {
        if client.HasSubscription("example") {
            client.Send(message)
        }
    }
}
```

Clients subscribe via the js-sdk `pb.realtime.subscribe("example", cb)`; builtin record event topics follow the `collectionName/*` / `collectionName/recordId` format. `app.SubscriptionsBroker()` also exposes `Clients()`, `ClientById(id)`, `TotalClients()`, `Register(client)`, `Unregister(clientId)`.

## Migrations (Go)

Application migrations are plain Go functions registered on the `core.AppMigrations` list (a `core.MigrationsList` sorted by file name):

1. Create a `migrations/` package with `init()` files:

```go
package migrations

import (
    "github.com/pocketbase/dbx"
    "github.com/pocketbase/pocketbase/core"
)

func init() {
    core.AppMigrations.Register(func(app core.App) error {
        _, err := app.DB().NewQuery("UPDATE articles SET status = 'pending' WHERE status = ''").Execute()
        return err
    }, func(app core.App) error { return nil }) // down
}
```

2. Blank-import it in `main`: `_ "yourpackage/migrations"`.
3. Migrations run automatically on `app.Start()` (system + app lists, tracked in the `_migrations` table). To apply them manually: `app.RunAllMigrations()`, `app.RunSystemMigrations()`, `app.RunAppMigrations()`.

For the prebuilt binary (and dev convenience) the `migratecmd` plugin additionally registers the `migrate` console command (`up` / `down [n]` / `create name` / `collections` / `history-sync`) with optional automigrations:

```go
import "github.com/pocketbase/pocketbase/plugins/migratecmd"

migratecmd.MustRegister(app, app.RootCmd, migratecmd.Config{
    TemplateLang: migratecmd.TemplateLangJS, // or the default Go templates
    Automigrate:  true, // auto-create migration files on collection changes
    Dir:          "pb_migrations", // optional; default pb_migrations (JS) / migrations (Go)
})
```

`Automigrate` keeps dev convenient but should be disabled in production builds (gate with `osutils.IsProbablyGoRun()` if needed). JS migrations (`pb_migrations/*.js`) are a JSVM feature — see `08-jsvm`.

## Misc

- `app.Store()` — in-memory key-value store (`Set`, `Get`/`GetOk`, `GetAll`, `Keys`, `Values`, `Has`, `Remove`, `RemoveAll`, `SetFunc`, `GetOrSet`, `Length`, `Reset`); survives settings reloads, not restarts
- `app.Settings()` — typed access to application settings: `SuperuserIPs`, `SMTP`, `Backups`, `S3`, `Meta`, `RateLimits`, `TrustedProxy`, `Batch`, `Logs`; mutate and `app.Save(settings)` (fires `OnSettingsReload`) or `app.ReloadSettings()`
- Backups/process control: `app.CreateBackup(ctx, name)`, `app.RestoreBackup(ctx, name)` (UNIX, experimental), `app.Restart()` (execve-based process replacement, UNIX only)
- App state: `app.IsDev()`, `app.DataDir()`, `app.IsBootstrapped()`, `app.Bootstrap()` (initialize before `Start`), `app.Terminate()`
- Security helpers: random string generation, constant-time compare, AES encrypt/decrypt (`tools/security`)

## Testing

Recommended pattern: keep hooks in a `bindAppHooks(app core.App)` function, prepare test data with `./pocketbase serve --dir=./test_pb_data`, then in integration tests create the app with the same hooks and exercise routes/records against the temp dir. For access-check logic: `app.CanAccessRecord(record, requestInfo, rule)` evaluates any `*string` rule (e.g. `record.Collection().ViewRule`) against a record for a `*core.RequestInfo` — superusers always pass, a `nil` rule is locked, an empty rule is public.

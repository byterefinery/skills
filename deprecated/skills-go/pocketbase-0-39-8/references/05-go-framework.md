# 05 — Go Framework Extension

## Getting Started

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

    // Serve static files
    app.OnServe().BindFunc(func(se *core.ServeEvent) error {
        se.Router.GET("/{path...}", apis.Static(os.DirFS("./pb_public"), false))
        return se.Next()
    })

    if err := app.Start(); err != nil {
        log.Fatal(err)
    }
}
```

```bash
go mod init myapp && go mod tidy
go run . serve               # development
CGO_ENABLED=0 go build       # production binary
```

## Event Hooks

All hooks share `func(e T) error` signature. Call `e.Next()` to continue the chain.

### Hook Registration

```go
// BindFunc — simple registration
app.OnRecordCreateRequest("posts").BindFunc(func(e *core.RecordRequestEvent) error {
    if !e.HasSuperuserAuth() {
        e.Record.Set("status", "pending")
    }
    return e.Next()
})

// Bind — with ID and priority
app.OnRecordCreateRequest("posts").Bind(&hook.Handler[*core.RecordRequestEvent]{
    Id:       "my_handler",
    Priority: 10,
    Func:     func(e *core.RecordRequestEvent) error { ... },
})

// Unbind
app.OnRecordCreateRequest("posts").Unbind("my_handler")
app.OnRecordCreateRequest("posts").UnbindAll()  // including system handlers
```

### Available Hooks

**Serve:**
- `OnServe()` — register routes and middlewares

**Bootstrap/Terminate:**
- `OnBootstrap()` — app initialization complete
- `OnTerminate()` — app shutdown

**Model lifecycle (Collection, Record, Settings):**
- `OnModelValidate()` / `OnRecordValidate()` / `OnCollectionValidate()`
- `OnModelCreate()` / `OnRecordCreate()` / `OnCollectionCreate()`
- `OnModelCreateExecute()` / `OnRecordCreateExecute()` / `OnCollectionCreateExecute()`
- `OnModelAfterCreateSuccess()` / `OnRecordAfterCreateSuccess()`
- `OnModelAfterCreateError()` / `OnRecordAfterCreateError()`
- `OnModelUpdate()` / `OnRecordUpdate()` / `OnCollectionUpdate()`
- `OnModelUpdateExecute()` / `OnRecordUpdateExecute()` / `OnCollectionUpdateExecute()`
- `OnModelAfterUpdateSuccess()` / `OnRecordAfterUpdateSuccess()`
- `OnModelAfterUpdateError()` / `OnRecordAfterUpdateError()`
- `OnModelDelete()` / `OnRecordDelete()` / `OnCollectionDelete()`
- `OnModelAfterDeleteSuccess()` / `OnRecordAfterDeleteSuccess()`
- `OnModelAfterDeleteError()` / `OnRecordAfterDeleteError()`

**Record API requests:**
- `OnRecordListRequest(collection)` — before list query
- `OnRecordViewRequest(collection)` — before single record view
- `OnRecordCreateRequest(collection)` — before record create
- `OnRecordUpdateRequest(collection)` — before record update
- `OnRecordDeleteRequest(collection)` — before record delete
- `OnRecordEnrich(collection)` — on every record serialization

**Auth:**
- `OnAuthRecordLoginRequest(collection)` — before auth login
- `OnAuthRecordMethodRequest(collection)` — before any auth method
- `OnAuthRecordVerifyRequest(collection)` — before verification

**Mailer:**
- `OnMailerRecordVerificationSend(collection)`
- `OnMailerRecordPasswordResetSend(collection)`
- `OnMailerRecordEmailChangeSend(collection)`
- `OnMailerRecordOTPSend(collection)`

**Realtime:**
- `OnRealtimeConnectRequest()` — before realtime connection
- `OnRealtimeMessageRequest()` — before realtime message

**Cron:**
- `OnCronJobRun()` — cron job execution

### Hook Examples

```go
// Intercept record creation
app.OnRecordCreateRequest("posts").BindFunc(func(e *core.RecordRequestEvent) error {
    // Before validation and DB insert
    e.Record.Set("slug:autogenerate", "post-")
    if err := e.Next(); err != nil {
        return err
    }
    // After successful insert
    e.App.Logger().Info("post created", "id", e.Record.Id)
    return nil
})

// Hide fields dynamically
app.OnRecordEnrich("articles").BindFunc(func(e *core.RecordEnrichEvent) error {
    if e.RequestInfo.Auth == nil ||
        (!e.RequestInfo.Auth.IsSuperuser() &&
         e.RequestInfo.Auth.GetString("role") != "staff") {
        e.Record.Hide("staffOnlyField")
    }
    return e.Next()
})

// After successful record update
app.OnRecordAfterUpdateSuccess("users").BindFunc(func(e *core.RecordEvent) error {
    e.App.Logger().Info("user updated", "id", e.Record.Id)
    return nil
})
```

## Routing

```go
app.OnServe().BindFunc(func(se *core.ServeEvent) error {
    // Simple route
    se.Router.GET("/hello/{name}", func(e *core.RequestEvent) error {
        name := e.Request.PathValue("name")
        return e.String(http.StatusOK, "Hello "+name)
    })

    // Authenticated route
    se.Router.POST("/api/myapp/settings",
        func(e *core.RequestEvent) error {
            return e.JSON(http.StatusOK, map[string]bool{"success": true})
        },
    ).Bind(apis.RequireAuth())

    // Superuser route
    se.Router.GET("/api/admin/stats",
        func(e *core.RequestEvent) error { ... },
    ).Bind(apis.RequireSuperuserAuth())

    // Route group
    g := se.Router.Group("/api/myapp")
    g.Bind(apis.RequireAuth())
    g.GET("", action1)
    g.GET("/example/{id}", action2)
    g.PATCH("/example/{id}", action3)

    return se.Next()
})
```

### Route Response Methods

```go
e.String(200, "text")
e.JSON(200, data)
e.JSONBlob(200, []byte{})
e.XML(200, data)
e.HTML(200, "<html>...")
e.File("path/to/file")
e.NoContent(204)
e.Redirect(302, "https://example.com")
```

### Reading Request Data

```go
// Path parameters
id := e.Request.PathValue("id")

// Auth state
authRecord := e.Auth
isGuest := e.Auth == nil
isSuperuser := e.HasSuperuserAuth()

// Query parameters
search := e.Request.URL.Query().Get("search")
arr := e.Request.URL.Query()["search"]  // multiple values

// Headers
token := e.Request.Header.Get("Some-Header")

// Body
var body struct {
    Title string `json:"title" form:"title"`
}
e.BindBody(&body)

// Uploaded files
files, err := e.FindUploadedFiles("document")
```

### Middlewares

```go
// Built-in middlewares
apis.RequireAuth()
apis.RequireSuperuserAuth()
apis.CORS(...)
apis.RateLimit(...)
apis.Static(dirfs, indexFallback)

// Custom middleware
se.Router.GET("/protected", handler).BindFunc(func(e *core.RequestEvent) error {
    // Before handler
    if e.Request.Header.Get("X-Custom") != "value" {
        return e.String(403, "Forbidden")
    }
    if err := e.Next(); err != nil {
        return err
    }
    // After handler
    e.Response.Header().Set("X-After", "done")
    return nil
})
```

## Database Operations

```go
// Raw query
res, err := app.DB().
    NewQuery("DELETE FROM articles WHERE status = 'archived'").
    Execute()

// Query with parameters
err := app.DB().
    NewQuery("SELECT name, created FROM posts WHERE created >= {:from}").
    Bind(dbx.Params{"from": "2023-06-25"}).
    All(&posts)

// Query builder
users := []User{}
app.DB().
    Select("id", "email").
    From("users").
    AndWhere(dbx.Like("email", "example.com")).
    Limit(100).
    OrderBy("created ASC").
    All(&users)

// Expressions
dbx.NewExp("total > {:min}", dbx.Params{"min": 10})
dbx.HashExp{"status": "public", "active": true}
dbx.Like("name", "john")
dbx.And(cond1, cond2)
dbx.Or(cond1, cond2)
```

## Logging

```go
app.Logger().Debug("message", "key", "value")
app.Logger().Info("message")
app.Logger().Warn("warning", "id", 123)
app.Logger().Error("error", "err", err)

// With attributes
l := app.Logger().With("total", 123)
l.Info("message A")
l.Info("message B", "name", "john")

// With group
l := app.Logger().WithGroup("sub")
l.Info("message", "total", 123)
// → {"sub": {"total": 123}}
```

## Cron Jobs

```go
// Every 2 minutes
app.Cron().MustAdd("hello", "*/2 * * * *", func() {
    log.Println("Hello!")
})

// Daily at midnight
app.Cron().MustAdd("cleanup", "0 0 * * *", func() {
    // cleanup task
})

// Macros: @yearly, @monthly, @weekly, @daily, @midnight, @hourly
app.Cron().MustAdd("hourly", "@hourly", func() { ... })

// Remove
app.Cron().Remove("hello")
```

## Console Commands

```go
app.RootCmd.AddCommand(&cobra.Command{
    Use: "hello",
    Run: func(cmd *cobra.Command, args []string) {
        log.Println("Hello world!")
    },
})
```

## Sending Emails

```go
message := &mailer.Message{
    From: mail.Address{
        Address: e.App.Settings().Meta.SenderAddress,
        Name:    e.App.Settings().Meta.SenderName,
    },
    To:      []mail.Address{{Address: e.Record.Email()}},
    Subject: "Welcome!",
    HTML:    "<p>Welcome to our app!</p>",
}
return e.App.NewMailClient().Send(message)
```

## Filesystem

```go
fsys, err := app.NewFilesystem()
if err != nil { return err }
defer fsys.Close()

// Read
r, err := fsys.GetReader("collectionId/recordId/filename.ext")
defer r.Close()

// Upload
err = fsys.Upload([]byte("content"), "key/path/file.txt")
err = fsys.UploadFile(file, "key/path/file.txt")

// Delete
err = fsys.Delete("key/path/file.txt")

// List
files, err := fsys.List("prefix/")
```

## Settings

```go
settings := app.Settings()
settings.Meta.AppName = "My App"
settings.Meta.AppURL = "https://example.com"
settings.Logs.MaxDays = 2
settings.Logs.LogAuthId = true
settings.Logs.LogIP = false
err := app.Save(settings)
```

## Plugins

```go
// JSVM (prebuilt binary)
jsvm.MustRegister(app, jsvm.Config{
    MigrationsDir: "./pb_migrations",
    HooksDir:      "./pb_hooks",
    HooksWatch:    true,
    HooksPoolSize: 15,
})

// Migrate command
migratecmd.MustRegister(app, app.RootCmd, migratecmd.Config{
    Automigrate: osutils.IsProbablyGoRun(),
})

// GitHub selfupdate
ghupdate.MustRegister(app, app.RootCmd, ghupdate.Config{})
```

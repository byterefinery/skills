# 06 — JavaScript Framework (JSVM)

## Overview

The prebuilt PocketBase executable includes an embedded ES5 JavaScript engine (goja). Write `*.pb.js` files in `pb_hooks/` directory. Files are loaded in filename sort order. Auto-restart on file change (UNIX only).

## Global Objects

| Object | Description |
|---|---|
| `$app` | PocketBase application instance |
| `$apis.*` | API routing helpers and middlewares |
| `$os.*` | OS primitives (shell commands, file ops) |
| `$security.*` | JWT creation/parsing, random strings, AES |
| `$dbx.*` | Database expression helpers |
| `__hooks` | Absolute path to `pb_hooks` directory |
| `console` | Standard console (log, info, warn, error) |

## TypeScript Declarations

```javascript
/// <reference path="../pb_data/types.d.ts" />

onBootstrap((e) => {
    e.next()
    console.log("App initialized!")
})
```

Use `.pb.ts` extension if editor doesn't lint with triple-slash directive.

## Event Hooks

```javascript
// Record hooks
onRecordCreateRequest((e) => {
    if (!e.hasSuperuserAuth()) {
        e.record.set("status", "pending")
    }
    e.next()
}, "posts")

onRecordAfterUpdateSuccess((e) => {
    console.log("updated...", e.record.get("email"))
    e.next()
}, "users")

onRecordEnrich((e) => {
    if (!e.requestInfo.auth) {
        e.record.hide("staffOnlyField")
    }
    e.next()
}, "articles")

// Collection hooks
onCollectionAfterUpdateSuccess((e) => {
    console.log("collection updated", e.collection.name)
    e.next()
})

// Bootstrap
onBootstrap((e) => {
    e.next()
    console.log("App initialized!")
})

// Serve
onServe((e) => {
    e.router.get("/hello", (req) => {
        return req.string(200, "Hello!")
    })
    e.next()
})
```

### Available JS Hooks

- `onBootstrap((e) => { e.next() })`
- `onTerminate((e) => { e.next() })`
- `onServe((e) => { e.next() })`
- `onRecordValidate((e) => {}, ...collections)`
- `onRecordCreate((e) => {}, ...collections)`
- `onRecordCreateExecute((e) => {}, ...collections)`
- `onRecordAfterCreateSuccess((e) => {}, ...collections)`
- `onRecordAfterCreateError((e) => {}, ...collections)`
- `onRecordUpdate((e) => {}, ...collections)`
- `onRecordUpdateExecute((e) => {}, ...collections)`
- `onRecordAfterUpdateSuccess((e) => {}, ...collections)`
- `onRecordAfterUpdateError((e) => {}, ...collections)`
- `onRecordDelete((e) => {}, ...collections)`
- `onRecordAfterDeleteSuccess((e) => {}, ...collections)`
- `onRecordAfterDeleteError((e) => {}, ...collections)`
- `onRecordListRequest((e) => {}, ...collections)`
- `onRecordViewRequest((e) => {}, ...collections)`
- `onRecordCreateRequest((e) => {}, ...collections)`
- `onRecordUpdateRequest((e) => {}, ...collections)`
- `onRecordDeleteRequest((e) => {}, ...collections)`
- `onRecordEnrich((e) => {}, ...collections)`
- `onCollectionValidate((e) => {})`
- `onCollectionCreate((e) => {})`
- `onCollectionCreateExecute((e) => {})`
- `onCollectionAfterCreateSuccess((e) => {})`
- `onCollectionAfterCreateError((e) => {})`
- `onCollectionUpdate((e) => {})`
- `onCollectionUpdateExecute((e) => {})`
- `onCollectionAfterUpdateSuccess((e) => {})`
- `onCollectionAfterUpdateError((e) => {})`
- `onCollectionDelete((e) => {})`
- `onCollectionAfterDeleteSuccess((e) => {})`
- `onCollectionAfterDeleteError((e) => {})`
- `onModelValidate((e) => {})`
- `onModelCreate((e) => {})`
- `onModelCreateExecute((e) => {})`
- `onModelAfterCreateSuccess((e) => {})`
- `onModelAfterCreateError((e) => {})`
- `onModelUpdate((e) => {})`
- `onModelUpdateExecute((e) => {})`
- `onModelAfterUpdateSuccess((e) => {})`
- `onModelAfterUpdateError((e) => {})`
- `onModelDelete((e) => {})`
- `onModelAfterDeleteSuccess((e) => {})`
- `onModelAfterDeleteError((e) => {})`
- `onMailerRecordVerificationSend((e) => {}, ...collections)`
- `onMailerRecordPasswordResetSend((e) => {}, ...collections)`
- `onMailerRecordEmailChangeSend((e) => {}, ...collections)`
- `onMailerRecordOTPSend((e) => {}, ...collections)`
- `onRealtimeConnectRequest((e) => {})`
- `onRealtimeMessageRequest((e) => {})`
- `onCronJobRun((e) => {})`

## Routing

```javascript
// Router helpers
routerAdd("GET", "/hello", (e) => {
    return e.string(200, "Hello world!")
})

routerAdd("GET", "/hello/{name}", (e) => {
    let name = e.request.pathValue("name")
    return e.string(200, "Hello " + name)
})

routerAdd("POST", "/api/data", (e) => {
    return e.json(200, { success: true })
})

// With middleware
routerAdd("GET", "/protected", (e) => {
    return e.string(200, "Secret!")
}, $apis.requireAuth())
```

## Records

```javascript
// Fetch
let record = $app.findRecordById("articles", "RECORD_ID")
let record = $app.findFirstRecordByData("articles", "slug", "test")
let record = $app.findFirstRecordByFilter("articles", "status = {:s}", { s: "public" })

let records = $app.findRecordsByIds("articles", ["ID1", "ID2"])
let total = $app.countRecords("articles", $dbx.hashExp({ status: "pending" }))
let records = $app.findAllRecords("articles", $dbx.hashExp({ status: "active" }))

// Auth records
let user = $app.findAuthRecordByEmail("users", "test@example.com")
let user = $app.findAuthRecordByToken("TOKEN", "auth")

// Custom query
let records = arrayOf(new Record)
$app.recordQuery("articles")
    .andWhere($dbx.hashExp({ status: "active" }))
    .orderBy("published DESC")
    .limit(10)
    .all(records)

// Create
let collection = $app.findCollectionByNameOrId("articles")
let record = new Record(collection)
record.set("title", "Lorem ipsum")
record.set("active", true)
record.set("slug:autogenerate", "post-")
$app.save(record)

// Update
let record = $app.findRecordById("articles", "ID")
record.set("title", "Updated")
$app.save(record)

// Delete
let record = $app.findRecordById("articles", "ID")
$app.delete(record)
```

## Collections

```javascript
// Fetch
let collection = $app.findCollectionByNameOrId("example")
let allCollections = $app.findAllCollections()
let authCollections = $app.findAllCollections("auth")

// Create
let collection = new Collection({
    type: "base",
    name: "articles",
    listRule: null,
    viewRule: "@request.auth.id != ''",
    fields: [
        { name: "title", type: "text", required: true, max: 100 },
        { name: "status", type: "select", values: ["draft", "public"] },
    ],
    indexes: ["CREATE INDEX idx_articles_title ON articles (title)"],
})
$app.save(collection)

// Update
let collection = $app.findCollectionByNameOrId("articles")
collection.fields.add(new EditorField({ name: "description", required: true }))
let titleField = collection.fields.getByName("title")
titleField.min = 10
$app.save(collection)

// Delete
let collection = $app.findCollectionByNameOrId("articles")
$app.delete(collection)
```

## Database

```javascript
// Raw query
$app.db().newQuery("DELETE FROM articles WHERE status = 'archived'").execute()

// With parameters
$app.db()
    .newQuery("SELECT name FROM posts WHERE created >= {:from}")
    .bind({ from: "2023-06-25" })
    .all(arrayOf(new DynamicModel()))

// Query builder
$app.db()
    .select("id", "email")
    .from("users")
    .andWhere($dbx.like("email", "example.com"))
    .limit(100)
    .orderBy("created ASC")
    .all(arrayOf(new DynamicModel()))

// Expressions
$dbx.exp("total > {:min}", { min: 10 })
$dbx.hashExp({ status: "public", active: true })
$dbx.like("name", "john")
$dbx.and(cond1, cond2)
$dbx.or(cond1, cond2)
```

## Logging

```javascript
$app.logger().debug("message", "key", "value")
$app.logger().info("message")
$app.logger().warn("warning", "id", 123)
$app.logger().error("error", "err", "error text")
```

## Cron Jobs

```javascript
$app.cron().add("hello", "*/2 * * * *", () => {
    console.log("Hello!")
})

$app.cron().add("daily", "0 0 * * *", () => {
    // daily task
})

$app.cron().remove("hello")
```

## Console Commands

```javascript
$app.rootCmd.addCommand(new Command({
    use: "hello",
    run: (cmd, args) => {
        console.log("Hello world!")
    },
}))
```

## Sending Emails

```javascript
let mailer = $app.newMailClient()
mailer.send({
    from:    { address: $app.settings().meta.senderAddress, name: $app.settings().meta.senderName },
    to:      [{ address: "user@example.com" }],
    subject: "Hello",
    html:    "<p>Hello!</p>",
})
```

## Filesystem

```javascript
let fsys = $app.newFilesystem()
try {
    let reader = fsys.getReader("collectionId/recordId/filename.ext")
    // use reader...
    reader.close()
} finally {
    fsys.close()
}

// Upload
fsys.upload(new TextEncoder().encode("content"), "key/file.txt")

// Delete
fsys.delete("key/file.txt")

// List
let files = fsys.list("prefix/")
```

## OS Utilities

```javascript
// Execute shell command
let result = $os.execSync("ls -la", { timeout: 10 })

// Get environment variable
let value = $os.getenv("MY_VAR")

// Read/write files
let content = $os.readFile("path/to/file.txt")
$os.writeFile("path/to/file.txt", "content")

// Directory operations
$os.deleteDir("path/to/dir")
let entries = $os.readDir("path/to/dir")
```

## Security Helpers

```javascript
// JWT
let token = $security.encodeJwt({ sub: "123" }, "secret", "HS256", 3600)
let payload = $security.decodeJwt("token", "secret")

// Random
let random = $security.randomString(10)

// AES
let encrypted = $security.aesEncrypt(data, key)
let decrypted = $security.aesDecrypt(encrypted, key)

// Hash
let hash = $security.hashBcrypt(password)
let valid = $security.compareHashBcrypt(password, hash)
```

## Caveats and Limitations

### Handler Scope Isolation

Each handler is serialized and executed in its own isolated context:

```javascript
// ❌ This FAILS — name is undefined inside handler
const name = "test"
onBootstrap((e) => {
    e.next()
    console.log(name)  // undefined!
})

// ✅ Share code via require()
onBootstrap((e) => {
    e.next()
    const utils = require(`${__hooks}/utils.js`)
    utils.hello("world")
})
```

### Module Loading

```javascript
// pb_hooks/utils.js
module.exports = {
    hello: (name) => { console.log("Hello " + name) }
}

// pb_hooks/main.pb.js
onBootstrap((e) => {
    e.next()
    const utils = require(`${__hooks}/utils.js`)
    utils.hello("world")
})
```

Only CommonJS (`require()`) is supported. ESM requires bundling (rollup, webpack, browserify).

### No Node.js/Browser APIs

No `window`, `fs`, `fetch`, `buffer`, `setTimeout`, `setInterval`. Use `$os.*` and `$security.*` instead.

### Relative Paths

Resolve from CWD, not from `pb_hooks/`. Use `__hooks` for absolute path:
```javascript
const config = require(`${__hooks}/config.js`)
```

### JSON Fields

Use `get()` and `set()` for JSON field values:
```javascript
record.get("jsonField")   // returns wrapped Go type
record.set("jsonField", value)
```

# 03 — API & Records

## REST API Endpoints

### Collections (superuser only)
```
GET    /api/collections                 # list all collections
GET    /api/collections/{id_or_name}    # view collection
POST   /api/collections                 # create collection
PATCH  /api/collections/{id_or_name}    # update collection
DELETE /api/collections/{id_or_name}    # delete collection
POST   /api/collections/{id}/truncate   # truncate records
POST   /api/collections/import          # import collections (superuser)
POST   /api/collections/export          # export collections (superuser)
POST   /api/collections/{id}/dry-run-view-query  # test view query
GET    /api/collections/{id}/list-all-oauth2-providers  # list OAuth2 providers
```

### Records
```
GET    /api/collections/{id}/records                  # list records
GET    /api/collections/{id}/records/{record_id}      # view record
POST   /api/collections/{id}/records                  # create record
PATCH  /api/collections/{id}/records/{record_id}      # update record
DELETE /api/collections/{id}/records/{record_id}      # delete record
```

### Auth Record Actions
```
POST   /api/collections/{id}/authWithPassword          # authenticate with password
POST   /api/collections/{id}/authWithOAuth2?provider=...&createUser=1&redirectURL=...  # OAuth2
POST   /api/collections/{id}/authWithOAuth2Code        # OAuth2 code exchange
POST   /api/collections/{id}/authWithOTP               # authenticate with OTP
POST   /api/collections/{id}/requestOTP                # request OTP code
POST   /api/collections/{id}/authRefresh               # refresh auth token
POST   /api/collections/{id}/verification-request      # request verification email
POST   /api/collections/{id}/verification-confirm      # confirm verification
POST   /api/collections/{id}/password-reset-request    # request password reset
POST   /api/collections/{id}/password-reset-confirm    # confirm password reset
POST   /api/collections/{id}/email-change-request      # request email change
POST   /api/collections/{id}/email-change-confirm      # confirm email change
POST   /api/collections/{id}/impersonate/{impersonate_as}  # impersonate (superuser)
```

### Other
```
GET    /api/health
GET    /api/files/{collection}/{record}/{filename}?thumb=wxh&download=1
POST   /api/settings                          # list settings
PATCH  /api/settings                          # update settings
POST   /api/settings/test-email               # test email
POST   /api/settings/test-s3                  # test S3
POST   /api/settings/apple/generate-client-secret  # Apple OAuth2
POST   /api/admins                            # list admins (deprecated)
```

## List Records Query Parameters

```
GET /api/collections/articles/records?filter=status='public'&sort=-published&expand=author&fields=id,title,author&page=1&perPage=20&skipTotal=0
```

| Param | Description |
|---|---|
| `filter` | Filter expression (same syntax as API rules) |
| `sort` | Sort expression, e.g. `-published`, `title` |
| `expand` | Comma-separated relation fields to expand |
| `fields` | Comma-separated fields to include (excludes others) |
| `page` | Page number (1-indexed) |
| `perPage` | Items per page (default 30) |
| `skipTotal` | Skip counting total items (improves performance) |

## Batch Operations

```javascript
// JS SDK
const results = await pb.collection('articles').batch([
    { type: 'create', data: { title: 'Article 1' } },
    { type: 'update', id: 'RECORD_ID', data: { title: 'Updated' } },
    { type: 'delete', id: 'RECORD_ID2' },
])
```

## Records via SDK

```javascript
// List
const result = await pb.collection('articles').getList(1, 20, {
    filter: "status = 'public'",
    sort: '-published',
    expand: 'author',
})
// result.items, result.totalItems, result.page, result.perPage, result.getPageTotal()

// Get one
const record = await pb.collection('articles').getOne('RECORD_ID', { expand: 'author' })

// Get first matching
const record = await pb.collection('articles').getFirstListitem("status = 'active'")

// Create
const record = await pb.collection('articles').create({ title: 'Hello', status: 'draft' })

// Update
const record = await pb.collection('articles').update('RECORD_ID', { title: 'Updated' })

// Delete
await pb.collection('articles').delete('RECORD_ID')
```

## Records in Go

```go
// Fetch single
record, err := app.FindRecordById("articles", "RECORD_ID")
record, err := app.FindFirstRecordByData("articles", "slug", "test")
record, err := app.FindFirstRecordByFilter("articles", "status = {:s}", dbx.Params{"s": "public"})

// Fetch multiple
records, err := app.FindRecordsByIds("articles", []string{"ID1", "ID2"})
total, err := app.CountRecords("articles", dbx.HashExp{"status": "pending"})
records, err := app.FindAllRecords("articles", dbx.HashExp{"status": "active"})
records, err := app.FindRecordsByFilter("articles", "status = {:s}", "-published", 10, 0, dbx.Params{"s": "public"})

// Auth records
user, err := app.FindAuthRecordByEmail("users", "test@example.com")
user, err := app.FindAuthRecordByToken("TOKEN", core.TokenTypeAuth)

// Custom query
records := []*core.Record{}
err := app.RecordQuery("articles").
    AndWhere(dbx.HashExp{"status": "active"}).
    OrderBy("published DESC").
    Limit(10).
    All(&records)
```

## Records in JavaScript (JSVM)

```javascript
// Fetch single
let record = $app.findRecordById("articles", "RECORD_ID")
let record = $app.findFirstRecordByData("articles", "slug", "test")
let record = $app.findFirstRecordByFilter("articles", "status = {:s}", { s: "public" })

// Fetch multiple
let records = $app.findRecordsByIds("articles", ["ID1", "ID2"])
let total = $app.countRecords("articles", $dbx.hashExp({ status: "pending" }))
let records = $app.findAllRecords("articles", $dbx.hashExp({ status: "active" }))
let records = $app.findRecordsByFilter("articles", "status = {:s}", "-published", 10, 0, { s: "public" })

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
```

## Record Model Methods

### Set/Get Fields
```go
record.Set("title", "example")
record.Set("users+", "RECORD_ID")   // append to existing
record.Load(data)                   // populate from map

// Get
record.Get("field")                 // any
record.GetBool("field")
record.GetString("field")
record.GetInt("field")
record.GetFloat("field")
record.GetDateTime("field")
record.GetStringSlice("field")
record.GetUnsavedFiles("fileField")
record.ExpandedOne("author")        // *core.Record
record.ExpandedAll("categories")    // []*core.Record
record.PublicExport()               // map[string]any
```

### Auth Accessors
```go
record.IsSuperuser()
record.Email() / record.SetEmail(email)
record.Verified() / record.SetVerified(bool)
record.TokenKey() / record.SetTokenKey(key)
record.RefreshTokenKey()
record.ValidatePassword(pass)
record.SetPassword(pass)
record.SetRandomPassword()
```

### Copies
```go
record.Original()  // original DB state
record.Fresh()     // latest state, no expand
record.Clone()     // full clone with everything
```

### Visibility
```go
record.Hide("field1", "field2")
record.Unhide("field1")
record.WithCustomData(true)  // allow custom fields in serialization
```

## Filter Syntax

Same expression syntax as API rules. Supports:
- Comparison: `=`, `!=`, `>`, `>=`, `<`, `<=`
- Pattern: `~` (LIKE), `!~` (NOT LIKE)
- Existence: `?=` (exists in), `!?=` (not exists in)
- Logical: `&&`, `||`, `!`
- Grouping: `()`
- SQL functions: `LOWER()`, `UPPER()`, `TRIM()`, `SUBSTR()`, `LENGTH()`, `INSTR()`, `REPLACE()`, `CAST()`, `COALESCE()`, `IFNULL()`, `NULLIF()`, `RANDOM()`, `ABS()`, `MIN()`, `MAX()`, `AVG()`, `SUM()`, `COUNT()`
- SQLite date: `DATE()`, `TIME()`, `DATETIME()`, `STRFTIME()`, `JULIANDAY()`
- JSON: `JSON_EXTRACT()`, `JSON_TYPE()`, `JSON_VALID()`
- Custom: `geoDistance()`, `strftime()`

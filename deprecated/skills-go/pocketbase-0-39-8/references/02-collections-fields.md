# 02 — Collections & Fields

## Collection Types

### Base Collection
Default type for application data (articles, products, posts). Supports full CRUD.

```go
collection := core.NewBaseCollection("articles")
```

### Auth Collection
Base collection plus authentication fields (`email`, `emailVisibility`, `verified`, `password`, `tokenKey`). Supports password auth, OTP, OAuth2, MFA.

```go
collection := core.NewAuthCollection("users")
```

### View Collection
Read-only collection backed by a SQL SELECT statement. No create/update/delete. No realtime events.

```go
collection := core.NewViewCollection("stats")
collection.ViewQuery = `
    SELECT posts.id, posts.name, count(comments.id) as totalComments
    FROM posts LEFT JOIN comments ON comments.postId = posts.id
    GROUP BY posts.id
`
```

## API Rules

Each collection has 5 rules: `listRule`, `viewRule`, `createRule`, `updateRule`, `deleteRule`. Auth collections add `manageRule`.

Rule values:
- `null` (locked) — superuser only (default)
- `""` (empty) — anyone
- `"expression"` — expression-based filter

```go
collection.ListRule   = types.Pointer("status = 'public'")
collection.ViewRule   = types.Pointer("id = @request.auth.id || status = 'public'")
collection.CreateRule = types.Pointer("@request.auth.id != ''")
collection.UpdateRule = types.Pointer("id = @request.auth.id")
collection.DeleteRule = types.Pointer("id = @request.auth.id")
```

### Rule Expression Syntax

**`@request.*` fields:**
- `@request.context` — `default`, `oauth2`, `otp`, `password`, `realtime`, `protectedFile`
- `@request.method` — HTTP method
- `@request.headers.*` — normalized headers (lowercase, `-` → `_`)
- `@request.query.*` — query parameters
- `@request.auth.*` — authenticated record fields
- `@request.body.*` — submitted body fields

**`@collection.*` cross-collection:**
```
@collection.news.categoryId ?= categoryId && @collection.news.author ?= @request.auth.id
```

**Modifiers:**
- `:isset` — check if field was submitted
- `:changed` — check if field was changed
- `:length` — array field item count
- `:each` — apply condition on each array item
- `:lower` — lowercase string comparison

**`@` datetime macros:**
`@now`, `@yesterday`, `@tomorrow`, `@todayStart`, `@todayEnd`, `@monthStart`, `@monthEnd`, `@yearStart`, `@yearEnd`, `@second`, `@minute`, `@hour`, `@weekday`, `@day`, `@month`, `@year`

**Functions:**
- `geoDistance(lonA, latA, lonB, latB)` — Haversine distance in km
- `strftime(format, time-value, modifiers...)` — date formatting

### Rule Response Codes
- Unsatisfied `listRule` → 200 with empty items
- Unsatisfied `createRule` → 400
- Unsatisfied `viewRule`, `updateRule`, `deleteRule` → 404
- Locked rule, non-superuser → 403

## Field Types (13 types)

### BoolField
Single `true`/`false` value. Default: `false`.

### NumberField
Float64 value. Default: `0`.
Modifiers: `field+` (add), `field-` (subtract).

### TextField
String value. Default: `""`.
Options: `Min`, `Max`, `Pattern`, `AutogeneratePattern`.
Modifier: `field:autogenerate` — auto-generate value from pattern.

### EmailField
Single email address. Default: `""`.

### URLField
Single URL string. Default: `""`.

### EditorField
HTML formatted text. Default: `""`.

### DateField
RFC3399 datetime string. Default: `""`.
Format: `Y-m-d H:i:s.uZ` (e.g., `2024-11-10 18:45:27.123Z`).
Date comparisons are string-based.

### AutodateField
Auto-set on create/update. Used for `created`/`updated` timestamps.

### SelectField
Single or multiple values from predefined list.
- Single (MaxSelect ≤ 1): string value
- Multiple (MaxSelect ≥ 2): string array
Modifiers: `field+` (append), `+field` (prepend), `field-` (remove).

### FileField
Single or multiple file uploads. Stores only filename in DB.
- Single: string filename
- Multiple: string array of filenames
Default max size: ~5MB per file.
Modifiers: `field+` (append), `+field` (prepend), `field-` (remove).
Options: `MaxSelect`, `MaxFileSize`, `MimeTypes`, `Thumbs` (image thumb sizes).

### RelationField
Single or multiple record references.
- Single: string record ID
- Multiple: string array of record IDs
Options: `CollectionId`, `MaxSelect`, `CascadeDelete`.
Modifiers: `field+` (append), `+field` (prepend), `field-` (remove).

### JSONField
Any serialized JSON value. Default: `null`. Only nullable field type.

### GeoPointField
Geographic point with `lat` and `lon` (float64). Default: `{lat: 0, lon: 0}`.

## Field Options

Common options across fields:
- `Name` — field identifier (used as column name)
- `Required` — whether the field is required
- `Hidden` — hide from regular user access
- `Presentable` — show in records list UI

## Indexes

```go
collection.AddIndex("idx_articles_status", false, "status", "")
collection.AddIndex("idx_articles_slug", true, "slug", "")  // unique
```

Or directly:
```go
collection.Indexes = append(collection.Indexes,
    "CREATE INDEX idx_example ON example (field1, field2)")
```

## Collection Properties (Go)

```go
type Collection struct {
    Id        string
    Name      string
    Type      string  // "base", "view", "auth"
    System    bool    // internal collections
    Fields    core.FieldsList
    Indexes   types.JSONArray[string]
    Created   types.DateTime
    Updated   types.DateTime
    ListRule  *string
    ViewRule  *string
    CreateRule *string
    UpdateRule *string
    DeleteRule *string
}
```

## Creating Collections Programmatically (Go)

```go
collection := core.NewBaseCollection("articles")

collection.ViewRule = types.Pointer("@request.auth.id != ''")
collection.CreateRule = types.Pointer("@request.auth.id != ''")

collection.Fields.Add(
    &core.TextField{
        Name:     "title",
        Required: true,
        Max:      100,
    },
    &core.RelationField{
        Name:          "author",
        Required:      true,
        Max:           1,
        CascadeDelete: true,
        CollectionId:  usersCollection.Id,
    },
)

collection.AddIndex("idx_articles_title", false, "title", "")
err := app.Save(collection)
```

## Creating Collections Programmatically (JS)

```javascript
let collection = new Collection({
    type:       "base",
    name:       "articles",
    listRule:   null,
    viewRule:   "@request.auth.id != ''",
    fields: [
        { name: "title", type: "text", required: true, max: 100 },
        { name: "author", type: "relation", collectionId: "users_id", maxSelect: 1 },
    ],
    indexes: ["CREATE INDEX idx_articles_title ON articles (title)"],
})

$app.save(collection)
```

# Collections

Collections represent application data — plain SQLite tables generated automatically from the collection `name` and `fields` (columns). A single entry is a **record** (one row). Manage collections from the Dashboard, via the Web APIs (superusers only, see `04-web-api`), or programmatically via Go/JS migrations.

## Collection types

- **Base** — default type, stores any application data (articles, products, posts).
- **View** — read-only collection populated from a plain SQL `SELECT` statement (aggregations, custom queries). Columns come from the query aliases; realtime events are not produced (no create/update/delete).
- **Auth** — everything from Base plus user management and authentication options. Each auth collection has fixed system fields: `email`, `emailVisibility`, `verified`, `password`, `tokenKey` (cannot be renamed/deleted, only configured). You can have many auth collections (users, managers, staffs…), each with its own login endpoints.

Example view collection query (fields become `id`, `name`, `totalComments`):

```sql
SELECT posts.id, posts.name, count(comments.id) as totalComments
FROM posts
LEFT JOIN comments on comments.postId = posts.id
GROUP BY posts.id
```

## Access control patterns (auth collections)

- **Role/Group** — a `select` field with roles; rule: `@request.auth.role = "staff"`
- **Ownership/Relation** — a `relation` field back to the auth collection; rule: `@request.auth.id != "" && author = @request.auth.id` (nested and back-relations work: `someRelField.anotherRelField.author = @request.auth.id`)
- **Managed** — auth collections have an extra `manageRule` letting one user (even from a different collection) fully manage another user's data (change email, password, …)
- **Mixed** — group with parentheses and `&&` / `||`:
  `@request.auth.id != "" && (@request.auth.role = "staff" || author = @request.auth.id)`

## Fields

All fields except `json` are non-nullable and fall back to a zero default when missing (empty string for `text`, 0 for `number`, etc.). `created`/`updated` are system `autodate` fields on every collection.

| Type | Stored value | Notes |
|---|---|---|
| `bool` | `false` / `true` | |
| `number` | float64: `0`, `2`, `-1`, `1.5` | modifiers `field+` (add), `field-` (subtract) |
| `text` | string | option `AutogeneratePattern`; submit `field:autogenerate` to generate |
| `email` | string | |
| `url` | string | |
| `editor` | HTML string | |
| `date` | RFC3399 string `"2022-01-01 00:00:00.000Z"` | compared as strings — filters need full datetime format |
| `autodate` | RFC3399 string | auto-set on create/update (use for `created`/`updated`-like fields) |
| `select` | single (MaxSelect=1): string; multiple: array of strings | modifiers `field+` / `+field` (append/prepend), `field-` (remove) |
| `file` | single: filename string; multiple: array of filenames | only the name is stored in DB; modifiers `field+` / `+field` / `field-` |
| `relation` | single: record id string; multiple: array of ids | modifiers `field+` / `+field` / `field-` |
| `json` | any JSON value (nullable) | no zero default |
| `geoPoint` | `{"lon": 23.32, "lat": 42.69}` | zero value is "Null Island" `{lon:0, lat:0}`; Go: `types.GeoPoint` or `map[string]any{"lon","lat"}` |

Modifier syntax (works in Web API bodies and record Set methods):

```js
// multi select: append / prepend / remove
pb.collection('example').update('ID', { 'tags+': 'a', '+tags': 'b', 'tags-': ['c'] })
// number: add / subtract
pb.collection('example').update('ID', { 'score+': 5, 'score-': 2 })
// text autogenerate
pb.collection('example').create({ 'slug:autogenerate': '' })
```

## Relations

- Single relation (MaxSelect=1) stores a record ID string; multiple stores an array of IDs.
- Expand nested records with the `expand` query parameter (up to 6 levels, e.g. `expand=relField1,relField2.subRelField`); results land under the record's `expand` property. Only relations the requester may view are expanded.
- Back-relations are filterable (`relField.backRelField.field = ...`).
- Setting a relation field to `""` / `[]` clears it.

## Indexes

Collections support extra SQL indexes (managed in the Dashboard or via `collection.Indexes`), including `UNIQUE` — required if you want to authenticate against a non-email identity field (e.g. `username`).

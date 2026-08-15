# pocketbase 0.39.11 — API Rules & Filter Language

## Rule semantics

Each collection has `listRule`, `viewRule`, `createRule`, `updateRule`, `deleteRule` (auth collections add `options.manageRule` — lets a user fully manage another user's record, e.g. change email/password; cannot be empty string).

| Rule value | Meaning |
|---|---|
| `null` ("locked", default) | superusers only |
| `""` | public — anyone (superusers, users, guests) |
| non-empty string | filter expression that the request must satisfy |

Rules act as **access control AND data filters** simultaneously (the rule expr is ANDed into the query). Status codes: unsatisfied `listRule` → 200 with empty items; unsatisfied `createRule` → 400; unsatisfied `view/update/deleteRule` → 404; locked rule + non-superuser → 403. Superusers bypass all rules. `manageRule` only affects auth field modifications (email, password, verified, tokenKey) on other users' records.

On record **create**, the create rule is evaluated against the submitted (not-yet-saved) record, and `verified` is forced to `false` for that check.

## Filter expression language

Used by rules, the `filter` query param, and (in Go/JS) `FindRecordsByFilter`.

### Operators

| Operator | Meaning | Example |
|---|---|---|
| `=` | equality (single or multi-value: matches if value is in the list) | `status = "active"`, `roles = "admin"` |
| `!=` | inequality | `status != "archived"` |
| `~` | contains (case-insensitive substring) | `title ~ "lorem"` |
| `!~` | not contains | `title !~ "spam"` |
| `<` `<=` `>` `>=` | comparisons (numbers, dates as strings) | `age >= 18` |
| `?=` | "any of" — at least one item in a multi-value field matches | `tags ?= "urgent"` |
| `?!=` | "none of" — no item matches | `roles ?!= "banned"` |
| `?~` `?!~` `?>` `?>=` `?<` `?<=` | "any" variants of the base operators | `files:length ?= 3` |

Combine with `&&` (AND), `||` (OR), and parentheses: `@request.auth.id != "" && (author = @request.auth.id || role = "staff")`.

### Fields available in rules

- **Collection schema fields**, including nested relation lookups: `someRelField.status != "pending"` (back-relations included). `id` is always available.
- **`@request.*`** — current request data:
  - `@request.auth.*` — authenticated record (guest → empty), e.g. `@request.auth.id != ""`
  - `@request.body.*` — submitted body fields
  - `@request.query.*` — query params as strings
  - `@request.headers.*` — headers as strings; keys normalized to lowercase with `-`→`_` (`X-Token` → `x_token`)
  - `@request.method` — HTTP method
  - `@request.context` — rule context: `default`, `oauth2`, `otp`, `password`, `realtime`, `protectedFile`
- **`@collection.<name>.*`** — fields of *other* collections joined by a shared value (for non-relation cross-collection checks): `@collection.news.author ?= @request.auth.id`. Join the same collection twice via alias: `@collection.news:other.author`.

### Field modifiers

| Modifier | Applies to | Meaning |
|---|---|---|
| `:isset` | `@request.*` | value was submitted with the request, e.g. `@request.body.role:isset = false` (block role changes) |
| `:changed` | `@request.body.*` | submitted AND different from the stored value |
| `:length` | multi `file`/`select`/`relation` (schema or body) | number of items, e.g. `photos:length > 0` |
| `:each` | multi `file`/`select`/`relation` | apply condition to every item, e.g. `roles:each != "banned"` |
| `:lower` | text | case-insensitive compare (SQLite `LOWER`; ASCII unless ICU) |

### Functions & macros

- `geoDistance(lonA, latA, lonB, latB)` — Haversine distance in km; works with `geoPoint` fields: `geoDistance(user.location.lon, user.location.lat, 12.3, 56.7) < 200`.
- `strftime(format, timeValue, modifiers...)` — SQLite-style date formatting, e.g. `strftime('%Y-%m', created) = "2024-06"`.
- Datetime macros (UTC): `@now`, `@yesterday`, `@tomorrow`, `@todayStart`, `@todayEnd`, `@monthStart`, `@monthEnd`, `@yearStart`, `@yearEnd`, `@second`, `@minute`, `@hour`, `@day`, `@weekday`, `@year`.
- Date values are compared as **full RFC3339 strings** — no partial dates or arithmetic in filters.

### Common rule patterns

```
# public read, only owners write
listRule:  "status = 'public'"
viewRule:  "status = 'public' || id = @request.auth.id"
createRule: "@request.auth.id != ''"
updateRule: "id = @request.auth.id"
deleteRule: "id = @request.auth.id && @request.auth.role = 'admin'"

# block guests entirely: leave rules locked (null)
# block submitting/renaming a field:
createRule: "@request.body.role:isset = false"
updateRule: "@request.body.role:changed = false"
```

### Client-side `filter`/`sort` restrictions

In request query params (not rules) only schema fields and `id` may be referenced — `@request.*` and `@collection.*` in client `filter`/`sort` values are rejected (superuser-only rule fields).

# API rules and filters

**API Rules** are collection access controls and data filters at the same time.

## The rules

Each collection has 5 rules, one per API action: `listRule`, `viewRule`, `createRule`, `updateRule`, `deleteRule`. Auth collections have an additional `options.manageRule` (lets one user fully manage another user's data).

Each rule can be:

- **"locked"** (`null`) — only an authorized superuser (this is the default)
- **Empty string** — anyone (superusers, authorized users, guests)
- **Non-empty string** — a filter expression; only clients satisfying it

Because rules act as filters, the API responds:

- unsatisfied `listRule` → **200** with empty `items`
- unsatisfied `createRule` → **400**
- unsatisfied `viewRule` / `updateRule` / `deleteRule` → **404**
- locked rule hit by a non-superuser → **403**

Rules are **ignored entirely** when the action is performed by an authorized superuser.

## Filter syntax

Format: `OPERAND OPERATOR OPERAND`, grouped with `(...)`, `&&` (AND), `||` (OR). Single-line comments with `//`.

OPERAND — any field literal, string (single or double quoted), number, `null`, `true`, `false`.

OPERATOR:

| Operator | Meaning |
|---|---|
| `=` / `!=` | equal / not equal |
| `>` / `>=` / `<` / `<=` | comparison |
| `~` / `!~` | Like/Contains (right string operand auto-wrapped in `%` if not specified); NOT Like |
| `?=` / `?!=` / `?>` / `?>=` / `?<` / `?<=` / `?~` / `?!~` | *any / at least one of* — `?`-prefixed variants of all operators, for array-like values and nested fields from multi-record sources |

By default, field expressions with array-like or multi-relation origin apply a **match-all** constraint; prefix the operator with `?` for *at-least-one-of* (e.g. `multiRelation.title ?= "test"`).

Field groups available:

- **Collection schema fields** — including nested relations: `someRelField.status != "pending"`, `id`, `created`, …
- **`@request.*`** — the current request data:
  - `@request.context` — where the rule is used: `default`, `oauth2`, `otp`, `password`, `realtime`, `protectedFile`
  - `@request.method` — e.g. `@request.method = "GET"`
  - `@request.headers.*` — header values as strings (keys lowercased, `-` → `_`; ex. `@request.headers.x_token`)
  - `@request.query.*` — query params as strings
  - `@request.auth.*` — the authenticated model (or empty record for guests); ex. `@request.auth.id != ""`
  - `@request.body.*` — submitted body params (uploaded files are NOT part of `@request.body` — they are evaluated separately)
- **`@collection.otherName`** — join another collection (not necessarily related) on a shared field: `@collection.news.categoryId ?= categoryId`. Join the same collection twice with an alias suffix: `@collection.registrations:user.user ?= @request.auth.id`

## Field modifiers

- **`:isset`** (`@request.*` only) — was the field submitted with the request. Disallow submitting a `role` field: `@request.body.role:isset = false`
- **`:changed`** (`@request.body.*` only) — submitted AND changed. Disallow changing `role`: `@request.body.role:changed = false`
- **`:length`** — number of items in an array field (multi `file`/`select`/`relation`), on schema fields or `@request.body.*`: `someRelationField:length = 2`
- **`:each`** (multi `select`/`file`/`relation` only) — apply a condition to every item: `someSelectField:each ~ "pb_%"`
- **`:lower`** — lower-cased string comparison (SQLite `LOWER`; ASCII only unless ICU is loaded): `title:lower ~ "test"`

Note: `@request.body.*` modifiers do not support checking *newly uploaded files* (evaluated separately, not serializable).

## Datetime macros (UTC)

```
@now @second @minute @hour @weekday @day @month @year
@yesterday @tomorrow
@todayStart @todayEnd @monthStart @monthEnd @yearStart @yearEnd
```

Ex. `@request.body.publicDate >= @now`

## Functions

- **`geoDistance(lonA, latA, lonB, latB)`** — Haversine distance in km between two points (works with `geoPoint` fields or numbers). Always a single-row value (any/at-least-one-of applies even with multi-relation args):
  `geoDistance(address.lon, address.lat, 23.32, 42.69) < 25`
- **`strftime(format, timeValue [, modifier, ...])`** — SQLite date formatting; modifiers per SQLite docs (up to 8):
  `strftime('%Y-%m', created) = "2026-01"` (match-all) or `?=` (at-least-one)

## Examples

```
// registered users only
@request.auth.id != ""

// registered users, active or pending records
@request.auth.id != "" && (status = "active" || status = "pending")

// registered users listed in a multi-relation allowed_users field
@request.auth.id != "" && allowed_users.id ?= @request.auth.id

// public: records whose title starts with "Lorem"
title ~ "Lorem%"

// owners only, with nested relation lookup
@request.auth.id != "" && author = @request.auth.id

// block a field from being changed by the client
@request.body.role:changed = false
```

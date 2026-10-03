# Web API reference

Base: `http://host:8090/api/`. Authenticated requests send the token as `Authorization: <token>` header (no `Bearer` prefix). Errors are JSON:

```json
{ "code": 400, "message": "The provided request body is missing the required field(s): title.", "data": { "title": { "code": "validation_required", "message": "Missing required value." } } }
```

List responses are paginated: `{ page, perPage, totalItems, totalPages, items }`.

## Records CRUD

| Action | Endpoint | Rule |
|---|---|---|
| List/search | `GET /api/collections/{idOrName}/records` | `listRule` |
| View | `GET /api/collections/{idOrName}/records/{recordId}` | `viewRule` |
| Create | `POST /api/collections/{idOrName}/records` | `createRule` |
| Update | `PATCH /api/collections/{idOrName}/records/{recordId}` | `updateRule` |
| Upsert | `PUT /api/collections/{idOrName}/records` (body must include `id`) | `updateRule` |
| Delete | `DELETE /api/collections/{idOrName}/records/{recordId}` | `deleteRule` |

`{idOrName}` accepts the collection ID or name. Create/Update accept `application/json` or `multipart/form-data` (files require multipart). Update is partial (only submitted fields change).

### List query parameters

- **`page`** (Number, default 1) — page offset
- **`perPage`** (Number, default 30) — max records per page
- **`sort`** (String) — ORDER BY fields, `-`/`+` prefix for DESC/ASC: `?sort=-created,id`. Supported fields: `@random`, `@rowid`, `id`, any collection field
- **`filter`** (String) — filter expression (see `03-api-rules-and-filters`), in addition to the collection's `listRule`: `?filter=(title~'abc' && created>'2022-01-01')`. Supported: `id` + any schema field
- **`fields`** (String) — comma-separated fields to return (default: all). `*` targets all keys of a depth level; supports `:excerpt(maxLength, withEllipsis?)` modifier, e.g. `?fields=*,description:excerpt(200,true)`
- **`expand`** (String) — auto-expand relations: `?expand=relField1,relField2.subRelField`. Up to 6 levels deep; results under the record's `expand` property; only view-permitted relations expand
- **`skipTotal`** (Boolean) — skips the total counts query (`totalItems`/`totalPages` become `-1`); big speedup when totals aren't needed. Set automatically by the SDKs' `getFirstListItem()`/`getFullList()`

## Batch

`POST /api/batch` — transactional batch of record create/update/upsert/delete in one request. **Must be explicitly enabled and configured in Dashboard → Settings → Application** (it runs in a single read&write transaction — keep max processing time/body limits small, avoid large file uploads over slow S3).

Body: `{ "requests": [ { "method": "POST", "url": "/api/collections/example/records?expand=user", "body": { ... } } ] }`

Supported actions: create `POST .../records`, update `PATCH .../records/{id}`, upsert `PUT .../records` (body must have `id`), delete `DELETE .../records/{id}`. Use the SDK: `const batch = pb.createBatch(); batch.collection('x').create({...}); await batch.send()`.

## Auth collection endpoints

All under `/api/collections/{idOrName}/`:

| Endpoint | Purpose |
|---|---|
| `GET auth-methods` | Public list of allowed auth methods (password identityFields, otp/mfa duration, oauth2 providers) |
| `POST auth-with-password` | Body: `identity`, `password` (identity field configurable) |
| `POST auth-with-otp` | Body: `otpId`, `password` |
| `POST request-otp` | Body: `email` → `{ otpId }` (sent even for unknown emails — enumeration protection) |
| `POST auth-with-oauth2` | Body: `provider`, `code`, `codeVerifier`, `redirectURL`, `createData?` — called right after the provider redirect |
| `GET /api/oauth2-redirect` | The OAuth2 redirect landing page (register this exact URL in the provider) |
| `POST auth-refresh` | New token + record for the current token; does NOT invalidate old tokens |
| `POST request-password-reset` | Body: `email` |
| `POST confirm-password-reset` | Body: `token`, `password`, `passwordConfirm` |
| `POST request-verification` | Body: `email` |
| `POST confirm-verification` | Body: `token` |
| `POST request-email-change` | Body: `newEmail` (authenticated) |
| `POST confirm-email-change` | Body: `token`, `password` (authenticated) |
| `POST impersonate/{recordId}` | Superuser only. Body: `duration` (seconds, 0 = default). Returns non-renewable token + record |

MFA: if enabled, the first auth method returns **401** with `{ "mfaId": "..." }`; complete with a second method passing `mfaId` in body or query. See `06-authentication`.

## Collections (superuser)

The collection body follows the `core.Collection` model — `name`, `type` (`base`/`view`/`auth`), `fields` (the same field types as in the Dashboard), `indexes` (raw SQL index expressions, e.g. `CREATE UNIQUE INDEX ...`), the five rules, and for auth collections an `options` object (`manageRule`, `authToken`, `passwordAuth`, `otp`, `mfa`, `oauth2`, plus the email templates). View collections carry their `SELECT` in `viewQuery`.

| Endpoint | Purpose |
|---|---|
| `GET /api/collections` | List (supports `filter`, `sort`, `perPage`, `page`) |
| `GET /api/collections/{idOrName}` | View |
| `POST /api/collections` | Create (body: `name`, `type`, `fields`, `indexes`, rules…) |
| `PATCH /api/collections/{idOrName}` | Update |
| `DELETE /api/collections/{idOrName}` | Delete (with its records) |
| `PUT /api/collections/import` | Import `{ collections, deleteMissing }` — `deleteMissing: true` deletes local collections not in the payload (with their data) |
| `DELETE /api/collections/{idOrName}/truncate` | Delete all records of the collection |
| `GET /api/collections/meta/scaffolds` | Type-indexed collection scaffolds with default field values |
| `GET /api/collections/meta/oauth2-providers` | All configurable OAuth2 providers |
| `POST /api/collections/meta/dry-run-view` | Body: `{ query }` — run a view collection query, return sample rows |

## Files

- `GET /api/files/{collectionIdOrName}/{recordId}/{filename}` — download/fetch a record file; `?download` forces attachment; `?thumb=` for image thumbs (see `05-files-handling`)
- `POST /api/files/token` — generates a temporary token for protected files (auth collection with protected file option)

## Settings (superuser)

- `GET /api/settings` / `PATCH /api/settings` — application meta (name, url, senderName/address), SMTP, S3 storage, log settings, security (rate limit, body size), batch config, User IP proxy headers
- `POST /api/settings/test/s3` — body `{ filesystem: "storage" | "avatars" }`
- `POST /api/settings/test/email` — body `{ email, template, collection }`
- `POST /api/settings/apple/generate-client-secret` — body `{ clientId, teamId, keyId, privateKey, duration }` → `{ secret }`

## Logs (superuser)

- `GET /api/logs` — list (`filter`, `sort`, `perPage`, `page`, `fields`)
- `GET /api/logs/{id}` — view
- `GET /api/logs/stats` — hourly stats (`filter` supported)
- `DELETE /api/logs` — truncate all logs (added in v0.40.0, doesn't change `maxDays` retention)

Log entry: `{ id, level: "info"|"error"|..., message, created, updated, data: {...} }`

## Backups (superuser)

- `GET /api/backups` — list `{ key, size, modified }[]`
- `POST /api/backups` — body `{ name }` — create a new backup
- `POST /api/backups/upload` — multipart `{ name }` + file — upload a backup
- `GET /api/backups/{key}` — download
- `POST /api/backups/{key}/restore` — restore (app must be stopped / single-instance)
- `DELETE /api/backups/{key}` — delete

## Crons (superuser)

- `GET /api/crons` — list scheduled jobs `{ id, cron, lastRun, nextRun, status, created, updated }`
- `POST /api/crons/{jobId}` — run a job manually

## SQL (superuser)

- `POST /api/sql` — body `{ query }` — runs a raw SQL query (SELECT and DDL/DML). Returns the result rows / affected counts.

## Health

- `GET/HEAD /api/health` — `{ "code": 200, "message": "Everything looks fine in the basement!" }`. Useful for load-balancer probes.

## Realtime

SSE (EventSource) based, two steps:

1. `GET /api/realtime?conn={CLIENT_ID}` — establishes the SSE connection (server pushes events; keep-alive `:ok` comments)
2. `POST /api/realtime` — body `{ clientId, subscriptions: [...] }` — sets the client's subscriptions (empty array unsubscribes from everything). Topic format: `COLLECTION_ID_OR_NAME/*` or `COLLECTION_ID_OR_NAME/RECORD_ID`; optional per-topic options appended as `TOPIC?options={"query":{...},"headers":{...}}`

Record events: `{ action: "create"|"update"|"delete", record: {...} }`. The subscription request must carry the same authorization as the connection (403 on mismatch). The js-sdk handles both steps automatically (see `12-js-sdk-records` / `13-js-sdk-services`).

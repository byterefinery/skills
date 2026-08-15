# pocketbase 0.39.11 — Records Web API

All record routes live under `/api/collections/{collectionIdOrName}` and accept either the collection ID or name. Responses are JSON envelopes: `{"code":200,"message":"","data":...}` (errors: non-2xx `code` + `message`).

## CRUD endpoints

| Method | Path | Access |
|---|---|---|
| GET | `/records` | per `listRule` (null → superuser only) |
| GET | `/records/{recordId}` | per `viewRule` |
| POST | `/records` | per `createRule` |
| PATCH | `/records/{recordId}` | per `updateRule` |
| DELETE | `/records/{recordId}` | per `deleteRule` |

## List query parameters (`GET /records`)

| Param | Default | Notes |
|---|---|---|
| `page` | 1 | 1-based page number |
| `perPage` | 30 | max 1000 |
| `sort` | — | comma list; prefix `-` DESC / `+` ASC (default ASC), e.g. `-created,title`. Special fields: `@random`, `@rowid`, plus `id` and any collection field |
| `filter` | — | filter expression (same language as API rules), applied on top of `listRule` |
| `expand` | — | comma list of relation fields to expand, supports nesting and options: `relField`, `relField.subField`, `relField{sort:created}`, `relField{filter:status="x"}` |
| `skipTotal` | false | skip the COUNT query (saves a roundtrip when total is unused) |

List response `data`: `{"page":1,"perPage":30,"totalItems":N,"totalPages":M,"items":[...]}`.

Single-record `GET /records/{id}` also accepts `expand`.

## Request body (create/update)

Send JSON (or `multipart/form-data` when uploading files). Keys are field names; field value **set modifiers**:

- `number` fields: `field+` (add), `field-` (subtract)
- `text` fields: `field:autogenerate` (fill via the field's AutogeneratePattern, e.g. `{"slug:autogenerate":"abc-"}`)
- multiple `select`/`file`/`relation` fields: `field+` append, `+field` prepend, `field-` remove — e.g. `{"roles+": "staff", "categories-": ["c1"]}`

Hidden fields are stripped from non-superuser submissions (except `password` on auth collections). View collections reject create/update/delete (400 "Unsupported collection type").

## File uploads

Uploads happen via the record create/update endpoints as `multipart/form-data` (JSON body fields and file parts together). File parts use the field name (or the `+field`/`field+`/`field-` modifier keys). Files are stored under `pb_data/files/{collectionId}/` with a sanitized original name + random suffix; the DB stores only the filename. See [05-realtime-files](05-realtime-files.md) for download URLs and protected-file tokens.

## Batch API

`POST /api/batch` — transactional multi-record create/update/upsert/delete in one request. **Disabled by default**; enable in Dashboard > Settings > Application (sets body size + processing time limits).

Body: `{"requests": [{"method":"POST","url":"/api/collections/example/records?expand=user","body":{...}, "headers":{...}}, ...]}`.

Supported actions per request: record create (`POST`), update (`PATCH`), upsert (`PUT` to `/records` — body must contain `id`), delete (`DELETE`). All batch requests share one auth state (no per-request `Authorization`). For file uploads send `multipart/form-data` with the JSON payload under the `@jsonPayload` field and files as `requests.N.fileField`. Response `data` is an array of `{"status": <http code>, "body": <per-request response body>}` objects; the whole batch runs in one transaction and rolls back on failure (400 `Batch transaction failed.`).

The default request body limit is **32 MiB** (`apis.BodyLimit` to change per route).

## Collection management API (superuser only)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/collections` | list (supports `page`, `perPage`, `sort`, `filter`) |
| POST | `/api/collections` | create |
| GET | `/api/collections/{idOrName}` | view (includes `indexes`) |
| PATCH | `/api/collections/{idOrName}` | update |
| DELETE | `/api/collections/{idOrName}` | delete |
| DELETE | `/api/collections/{idOrName}/truncate` | delete all records |
| PUT | `/api/collections/import` | import collections snapshot (`deleteMissing` optional) |
| GET | `/api/collections/meta/scaffolds` | field type scaffolds (UI templates) |
| GET | `/api/collections/meta/oauth2-providers` | list OAuth2 providers |
| POST | `/api/collections/meta/dry-run-view` | dry-run a view collection SELECT (returns sample rows) |

Collection create/update body: `type` (`base`|`auth`|`view`), `name`, the 5 rules (+ `options.manageRule` for auth), `fields` (array of field objects with `type`, `name`, and type-specific options), `indexes` (array of raw `CREATE INDEX ...` statements), `presentable`, and for views `viewQuery`.

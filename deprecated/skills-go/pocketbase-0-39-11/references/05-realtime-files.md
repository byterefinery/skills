# pocketbase 0.39.11 — Realtime & Files API

## Realtime (SSE)

Two operations over `/api/realtime`:

1. `GET /api/realtime` — opens the SSE stream; immediately receives a `PB_CONNECT` event with the `clientId`.
2. `POST /api/realtime` — sets the client's subscriptions (replaces previous ones; empty list = unsubscribe all). Body (JSON or multipart): `clientId`, `subscriptions` (array of topics `COLLECTION_ID_OR_NAME/*` for whole collection or `COLLECTION_ID_OR_NAME/RECORD_ID` for a single record), optional `options` (serialized JSON of per-topic query/header params, e.g. the `fields` selector).

Auth happens **on the first Set subscriptions call** (`Authorization` header), not on connect. Per-record subscriptions are checked against the collection's `viewRule`; whole-collection subscriptions against `listRule` (rule context = `realtime`, so rules can use `@request.context = "realtime"`).

Event payload (SSE `data:` for the topic name):

```json
{"action": "create|update|delete", "record": { ... }}
```

- The `record` in the payload respects the same hidden-field and email-visibility rules as REST responses.
- Per-subscription `fields` query option trims the record payload (picker syntax, e.g. `fields=id,title`).
- Idle disconnect after **5 minutes** without messages (max connection lifetime 30 minutes); SDKs auto-reconnect and resubscribe.
- View collections produce no events.
- Headers set on `X-Accel-Buffering: no` (disable proxy buffering, e.g. in nginx).

SDK usage (JavaScript):

```js
const cb = pb.collection('posts').subscribe('*', (e) => {
    // e.action, e.record
    pb.collection('posts').unsubscribeAll(); // stop everything
});
pb.collection('posts', 'RECORD_ID').subscribe('*', handler); // single record
```

## Files

Files are **uploaded/deleted via the records APIs** (multipart); the File API only serves them.

### Download

`GET /api/files/{collectionIdOrName}/{recordId}/{filename}`

| Query param | Purpose |
|---|---|
| `thumb` | return a resized thumb (`thumb=WIDTHxHEIGHT` or `thumb=` for the field default); non-images or missing thumb config → original file |
| `download` | truthy → `Content-Disposition: attachment` |
| `token` | **file token** for protected files |

Access checks: the file field's collection rules apply (file download uses the record's `viewRule` unless the field is protected). For **protected** file fields (checkbox in the field options) the file is only accessible with a valid short-lived file token or via superuser/auth with manage access.

### File tokens

`POST /api/files/token` (requires `Authorization: <token>` — superuser or auth record):

Body: `collectionIdOrName`, `recordId`, `filename` (repeat fields for multiple files). Returns `{"token": "...", "duration": 180}` — the token is a short-lived JWT (per collection `options.fileToken.duration`, default **180 s**) that grants access to exactly those protected file(s) without re-auth.

Typical flow: client with a user token requests file tokens for the files it needs, then opens the file URLs with `?token=...`.

## Logs & backups (superuser only)

- `GET /api/logs` (+ `?page&perPage&sort&filter`), `GET /api/logs/stats` (hourly), `GET /api/logs/{id}` — activity logs stored in `auxiliary.db` (retention via Settings > Logs `maxDays`).
- `GET /api/backups`, `GET /api/backups/{key}`, `POST /api/backups` (create, body `{name?}`), `DELETE /api/backups/{key}`, `POST /api/backups/{key}/restore` (UNIX only; restarts the app), `POST /api/backups/upload` (restore from uploaded ZIP). Backups are ZIP snapshots of `pb_data/` (local or S3 per Settings); generation puts the app in read-only mode.
- `GET /api/crons` / `POST /api/crons/{jobId}` — list registered cron jobs / trigger one manually.

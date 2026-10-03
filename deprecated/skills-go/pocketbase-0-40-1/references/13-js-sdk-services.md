# JS SDK — other services

All services are properties of the client and mirror the Web API (see `04-web-api`). All methods are async, take an optional `options` (see `11-js-sdk-overview`), and reject with `ClientResponseError`.

## pb.collections (superuser)

CRUD: `getList(page?, perPage?, options?)`, `getOne(idOrName)`, `create(body)`, `update(idOrName, body)`, `delete(idOrName)` — body is the collection model (`name`, `type`, `fields[]`, `indexes[]`, rules, auth `options`).

Special:

```js
await pb.collections.import(collections, deleteMissing = false); // PUT /api/collections/import — deleteMissing also drops local collections + their data
await pb.collections.truncate('COLLECTION_NAME');                // deletes all records of the collection
const scaffolds = await pb.collections.getScaffolds();            // type -> default collection model
const providers = await pb.collections.getAllOAuth2Providers();   // all configurable OAuth2 providers
const sample = await pb.collections.dryRunViewQuery('SELECT ...'); // run a view query, returns sample rows
```

Collection models: `BaseCollectionModel` (`type: "base"`), `ViewCollectionModel` (`type: "view"`, `viewQuery`), `AuthCollectionModel` (`type: "auth"`, `authRule/manageRule`, `authToken`, `passwordAuth`, `otp`, `mfa`, `oauth2`, `verificationTemplate`, …).

## pb.files

```js
// build a file URL (adds thumb/download query params; returns "" if record/filename incomplete)
const url = pb.files.getURL(record, 'filename_Ab24ZjL.png', { thumb: '100x300' });
// thumb formats: WxH, WxHt, WxHb, WxHf, 0xH, Wx0

const token = await pb.files.getToken(); // protected files short-lived token (requires auth)
```

Deprecated: `pb.files.getUrl()` → use `getURL`.

## pb.logs (superuser)

```js
const page = await pb.logs.getList(1, 30, { filter: 'level = "error"' });
const log = await pb.logs.getOne('LOG_ID');
const stats = await pb.logs.getStats({ filter: '...' }); // hourly [{ total, date }]
await pb.logs.truncate();                                 // DELETE /api/logs (v0.40.0+)
```

Log model: `{ id, level, message, created, updated, data }`.

## pb.settings (superuser)

```js
const settings = await pb.settings.getAll();
await pb.settings.update({ meta: { name: 'MyApp' } }); // partial update
await pb.settings.testS3('storage');                    // or 'avatars'
await pb.settings.testEmail('COLLECTION', 'dest@example.com', 'verification'); // template: verification | password-reset | email-change
const { secret } = await pb.settings.generateAppleClientSecret(clientId, teamId, keyId, privateKey, duration);
```

## pb.backups (superuser)

```js
const list = await pb.backups.getFullList();   // [{ key, size, modified }]
await pb.backups.create('mybackup');           // create backup (name = base filename)
await pb.backups.upload(formDataWithFile);     // upload a backup file
await pb.backups.restore('KEY');               // restore (app must not be serving writes)
await pb.backups.delete('KEY');
```

Download a backup by fetching the URL (superuser-authorized): `/api/backups/{key}`.

## pb.crons (superuser)

```js
const jobs = await pb.crons.getFullList(); // [{ id, cron, lastRun, nextRun, status, created, updated }]
await pb.crons.run('JOB_ID');             // manually run a scheduled job
```

## pb.sql (superuser)

```js
const result = await pb.sql.run('SELECT * FROM posts LIMIT 10');
// -> { execTime, affectedRows, columns: [{ name, type, nullable }], rows: [[...]] } // rows are raw arrays of strings/nulls
```

## pb.health

```js
const { code, message } = await pb.health.check(); // GET /api/health
```

## pb.createBatch() — transactional writes

Groups multiple record create/update/upsert/delete into a single `POST /api/batch` request (all-or-nothing transaction; the batch endpoint must be enabled in Settings):

```js
const batch = pb.createBatch();
batch.collection('example1').create({ title: 'a' });
batch.collection('example2').update('RECORD_ID', { title: 'b' });
batch.collection('example3').delete('RECORD_ID');
batch.collection('example4').upsert({ id: 'MAYBE_EXISTING_ID', title: 'c' }); // update if id exists, else create
const results = await batch.send();
// -> [{ status, body }, ...] per request
```

File handling in batch bodies: `File`/`Blob` values (or arrays of them) are moved to the multipart part automatically; mixed arrays of regular + file values get the `+` (append) field-name modifier applied so existing files aren't deleted.

## pb.realtime — low-level

`pb.collection(name).subscribe(...)` (see `12-js-sdk-records`) is built on top of `pb.realtime`, which can subscribe to **any** topic string:

```js
await pb.realtime.subscribe('my_custom_topic', (e) => console.log(e), options?); // -> unsubscribe function
await pb.realtime.unsubscribe('my_custom_topic');      // all subscriptions on the topic
await pb.realtime.unsubscribeByPrefix('my_custom');    // all topics starting with the prefix
await pb.realtime.unsubscribe();                        // everything
```

- One SSE connection per client (`GET /api/realtime?conn=...`), subscriptions are (re)sent via `POST /api/realtime` as `{ clientId, subscriptions }`.
- Auto-reconnect with backoff (200ms → 2s, capped 15s connect timeout); on reconnect the SDK resubmits the full subscription set.
- `pb.realtime.isConnected`, `pb.realtime.clientId`; `pb.realtime.onDisconnect = (activeSubscriptions) => {...}` for failure awareness.
- Per-subscription `options` (`fields`, `filter`, `expand`, headers, custom query) are attached to the topic as a serialized `options` query string.

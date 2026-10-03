# JS SDK — RecordService

Get one per collection (cached by name): `const service = pb.collection('posts')` or `pb.collection('COLLECTION_ID')`. Generic `pb.collection<MyType>('x')` types the results.

## CRUD

| Method | Request | Returns |
|---|---|---|
| `getList(page = 1, perPage = 30, options?)` | `GET /api/collections/{c}/records` | `ListResult<T>` = `{ page, perPage, totalItems, totalPages, items: T[] }` |
| `getFullList(options?)` or `getFullList(batch = 1000, options?)` | repeated `getList` | `T[]` (all pages, default batch 1000, `skipTotal` auto-set) |
| `getFirstListItem(filter, options?)` | `getList(1, 1, { filter, skipTotal })` | `T` — **throws 404** when nothing matches |
| `getOne(id, options?)` | `GET .../records/{id}` | `T` (throws 404 on empty id) |
| `create(bodyParams?, options?)` | `POST .../records` | `T` — body is a plain object or `FormData` |
| `update(id, bodyParams?, options?)` | `PATCH .../records/{id}` | `T` — partial update |
| `delete(id, options?)` | `DELETE .../records/{id}` | `true` |

Record objects carry `id`, `collectionId`, `collectionName`, `created`, `updated`, your fields, plus `expand` (nested relations) and `files`/system data as returned by the API.

`update`/`delete` have auth-aware side effects: if the updated/deleted record matches `pb.authStore.record`, the store is refreshed (merged fields) or cleared automatically.

### List/query options

```js
const result = await pb.collection('posts').getList(1, 50, {
    filter: 'created >= "2022-01-01 00:00:00" && status = "published"',
    sort: '-created,id',
    fields: '*,description:excerpt(200,true)',
    expand: 'author,categories',   // up to 6 levels, lands under record.expand
    skipTotal: false,
});
```

All options may also be placed under `options.query` — top-level unknown keys are treated as query params automatically.

## Authentication

All auth methods update `pb.authStore` on success and return `RecordAuthResponse` = `{ token, record, meta? }` (`meta` holds OAuth2 `accessToken`/`refreshToken` when applicable).

```js
// password
const authData = await pb.collection('users').authWithPassword('test@example.com', '1234567890', options?);

// OTP
const req = await pb.collection('users').requestOTP('test@example.com');  // -> { otpId }
await pb.collection('users').authWithOTP(req.otpId, 'THE_CODE');

// OAuth2 — modern realtime-popup form (no custom redirects; opens popup, round-trips code via one-off realtime subscription)
const authData = await pb.collection('users').authWithOAuth2({
    provider: 'google',
    // scopes: ['...'], createData: {...}, urlCallback: (url) => {...}
});
// OAuth2 — classic code-exchange form (after the provider redirect to /api/oauth2-redirect)
await pb.collection('users').authWithOAuth2Code('google', code, codeVerifier, redirectURL, createData?, options?);

// allowed methods (public)
const methods = await pb.collection('users').listAuthMethods();
// -> { mfa: {enabled, duration}, otp: {enabled, duration}, password: {enabled, identityFields}, oauth2: {enabled, providers: [{name, displayName, state, authURL, codeVerifier, ...}] } }

// refresh (validates token; does NOT invalidate old ones)
await pb.collection('users').authRefresh();
```

MFA flow: catch the 401 from the first method, read `err.response.mfaId`, then call the second method with `{ mfaId }` in options:

```js
try {
    await pb.collection('users').authWithPassword(email, pass);
} catch (err) {
    const mfaId = err.response?.mfaId;
    if (!mfaId) throw err;
    const otp = await pb.collection('users').requestOTP(email);
    await pb.collection('users').authWithOTP(otp.otpId, 'THE_CODE', { mfaId });
}
```

Password reset / verification / email change:

```js
await pb.collection('users').requestPasswordReset(email);
await pb.collection('users').confirmPasswordReset(token, password, passwordConfirm);

await pb.collection('users').requestVerification(email);
await pb.collection('users').confirmVerification(token);      // updates authStore.record.verified if it's the current record

await pb.collection('users').requestEmailChange(newEmail);    // authenticated
await pb.collection('users').confirmEmailChange(token, password); // clears authStore if it's the current record
```

### Superuser auto-refresh

`authWithPassword` on `_superusers` supports `autoRefreshThreshold` (seconds) in options — the SDK schedules `authRefresh` before the token expires and re-authenticates with the stored credentials on failure.

### Impersonation (superuser)

```js
await pb.collection('_superusers').authWithPassword('admin@example.com', 'pass');
const client = await pb.collection('users').impersonate('USER_RECORD_ID', 3600 /* duration seconds, optional */);
const items = await client.collection('example').getFullList();
// `client` is a standalone PocketBase instance with a memory store — the token lives only as long as `client`
```

### Linked OAuth2 accounts

Prefer plain collection access: `pb.collection('_externalAuths').getFullList({ filter: pb.filter('recordRef = {:id}', { id: recordId }) })` to list, and delete the matching record to unlink (`provider = 'google'` etc.). The old `listExternalAuths()`/`unlinkExternalAuth()` methods are deprecated wrappers.

## Realtime subscriptions

```js
// any record change in the collection
const unsubscribe = await pb.collection('example').subscribe('*', (e) => {
    // e.action = "create" | "update" | "delete"
    // e.record = the record data (respecting list/view rules of the subscriber)
    console.log(e.action, e.record);
}, { fields: '...', filter: '...', expand: '...' }); // per-subscription options

// single record
await pb.collection('example').subscribe('RECORD_ID', callback);

// remove one subscription
await unsubscribe();
// or remove all for the topic / the whole collection
await pb.collection('example').unsubscribe('RECORD_ID');
await pb.collection('example').unsubscribe('*');
await pb.collection('example').unsubscribe();
```

Subscribing multiple times to the same topic is fine — each `subscribe` returns its own unsubscribe function. The SDK maintains one SSE connection (`pb.realtime`) with auto-reconnect (exponential backoff 200ms→2s, up to 15s connect timeout) and resubmits the subscription set on connect.

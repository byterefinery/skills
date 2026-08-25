# PocketBase JavaScript SDK (v0.28.0)

Official client for **browser, Node.js, React Native** (and other JS runtimes). Package: `pocketbase` on npm.

```bash
npm install pocketbase   # or yarn/pnpm
```

Exports: ESM (`pocketbase`), CJS (`pocketbase/cjs`), UMD (`pocketbase/umd`). No runtime dependencies; supports `fetch` (override via options when needed).

## Creating a client

```js
import PocketBase from 'pocketbase';
const pb = new PocketBase('http://127.0.0.1:8090');         // baseURL, default "/"
const pb2 = new PocketBase('https://example.com', store);   // + custom authStore
const pb3 = new PocketBase('https://example.com', null, 'bg'); // + lang (Accept-Language, default "en-US")
```

- A single global instance for the app lifetime is safe (browser/mobile).
- **Node/React Native have no native `EventSource`** — install a polyfill (e.g. `react-native-sse`) before using realtime: `global.EventSource = eventsource`.
- For server-side shared/superuser clients disable auto-cancellation: `pb.autoCancellation(false)`.
- `pb.admins` is deprecated — use `pb.collection('_superusers')`.

## Auth store

`pb.authStore` holds the current auth token + record and is sent automatically as `Authorization` on every request.

| Store | Persistence | Use |
|---|---|---|
| `BaseAuthStore` | memory only | server-side / throwaway clients (also auto-selected under Deno) |
| `LocalAuthStore` | `localStorage` key `pocketbase_auth` | browsers (default when `window` exists) |
| `AsyncAuthStore` | custom `save`/`clear` functions | React Native/Flutter-style persistence (AsyncStorage, SharedPreferences, files…) |

```js
// React Native / Node example
import eventsource from 'react-native-sse';
import AsyncStorage from '@react-native-async-storage/async-storage';
global.EventSource = eventsource;
const store = new AsyncAuthStore();
const pb = new PocketBase('http://127.0.0.1:8090', store);
```

API: `pb.authStore.token`, `.record` (null when unauthenticated), `.model` (alias), `.isValid` (token not expired — JWT check, no server call), `.isSuperuser`, `.save(token, record?)`, `.clear()`, `.onChange(callback)` (store changes), `.loadFromCookie(cookie, key)` / `.exportToCookie(opts, key)` (key defaults to `pb_auth`). Deprecated: `isAdmin`, `isAuthRecord` — use `isSuperuser` / `!isSuperuser` or check `record.collectionName`.

## Services

Each `pb.<service>` wraps one API area (all async, all return Promises):

- `pb.collection(idOrName)` → **RecordService** (CRUD + auth; see `12-js-sdk-records`)
- `pb.collections` → CollectionService (superuser; see `13-js-sdk-services`)
- `pb.files`, `pb.logs`, `pb.settings`, `pb.backups`, `pb.crons`, `pb.sql`, `pb.health` → see `13-js-sdk-services`
- `pb.realtime` → low-level RealtimeService (subscribe to arbitrary topics)
- `pb.createBatch()` → BatchService (transactional multi-record writes)

## Send options

Every method accepts an options object (extends `RequestInit`). Unknown top-level keys are **automatically treated as query parameters** (so `fields`, `expand`, `filter`, `sort`, `page`, `perPage`, `skipTotal`, `batch` can be passed either at top level or under `query`/`params`).

- `query` / `params` — query parameters (merged)
- `headers`, `body`, `method`, `fetch` (custom fetch implementation), `signal`, … standard `RequestInit`
- `requestKey` — cancellation key (`null` disables; defaults to `METHOD+path`)
- `$autoCancel` / `$cancelKey` — legacy spellings (still work)
- Dates in query params are serialized to PocketBase datetime format; objects are JSON-stringified

Non-FormData bodies get `Content-Type: application/json` automatically; plain objects with `File`/`Blob` values are auto-converted to `FormData`. The `Accept-Language` header is set from `pb.lang`.

## Hooks

```js
// before each fetch — inspect/modify url+options; return { url, options } to replace entirely
pb.beforeSend = (url, options) => {
    options.headers = { ...options.headers, 'X-Custom': 'v' };
    return { url, options };
};

// after each fetch — inspect/modify the parsed data (throw ClientResponseError to fail)
pb.afterSend = (response, data, options) => data;
```

## Helpers

- `pb.buildURL(path)` — safely concatenate a path onto the base URL (browser-aware)
- `pb.filter(raw, params)` — build a filter expression with `{:param}` placeholders; values are quoted safely (strings JSON-quoted, booleans/numbers as-is, `Date` → PocketBase datetime, `null`/`undefined` → `null`, other objects JSON-stringified):
  ```js
  pb.collection('example').getFirstListItem(
      pb.filter('title ~ {:title} && created >= {:created}', { title: 'test', created: new Date() })
  );
  ```

## Errors

All failures reject with `ClientResponseError`:

- `err.status` — HTTP status (0 for network errors)
- `err.response` — parsed error body `{ code, message, data }` (`err.data` alias)
- `err.message` — `response.message`, or a helpful fallback (e.g. abort message, or "Failed to connect… Try changing the SDK URL from localhost to 127.0.0.1")
- `err.url` — full request URL
- `err.isAbort` — true when cancelled
- `err.originalError` / `err.cause` — underlying error

```js
try {
    await pb.collection('users').authWithPassword('a@b.c', 'wrong');
} catch (err) {
    console.log(err.status);        // 400
    console.log(err.response.data); // field-level validation errors
}
```

## Auto-cancellation

By default, sending a request cancels any pending request with the same `requestKey` (default: `METHOD + path`). This prevents stale duplicate requests but can surprise shared clients — disable globally with `pb.autoCancellation(false)`, per-request with `{ requestKey: null }` (or `$autoCancel: false`), and cancel manually with `pb.cancelRequest(key)` / `pb.cancelAllRequests()`.

## Security and SSR

- **CSP** — the auth token lives in `localStorage` by default; configure a basic Content-Security-Policy (meta tag or header) to reduce XSS risk that could steal it.
- **Filter injection** — when building `filter` strings with untrusted input, always use `pb.filter(expr, params)` with `{:param}` placeholders instead of string concatenation.
- **SSR pattern** — there is no one-size-fits-all SSR solution; the general idea is a cookie-based flow: create a new `PocketBase` instance per server-side request, feed `pb.authStore` from the request cookie via `authStore.loadFromCookie(cookieString)`, do the server-side work, then write the updated state back with `authStore.exportToCookie({ httpOnly, secure, sameSite, ... })` (default cookie key `pb_auth`).

# Data Fetching and Caching

Next.js 16 has **two caching models**. Choose first, then apply rules:

- **Previous model (default)** — no config flag. Caching via `fetch` options + route segment config exports. This is what most v16 apps run unless they set `cacheComponents`.
- **Cache Components (opt-in)** — `cacheComponents: true` in `next.config`. Caching via the `'use cache'` directive, `cacheLife`/`cacheTag`, and Partial Prerendering (PPR) as the default rendering behavior.

## Fetching data (Server Components)

Any async I/O works — `fetch` or an ORM/DB client directly:

```tsx
export default async function Page() {
  const data = await fetch('https://api.example.com/blog')
  const posts = await data.json()
  return <ul>{posts.map((p) => <li key={p.id}>{p.title}</li>)}</ul>
}
```

- **Identical `fetch` requests are memoized** within a component tree/request (deduplicated by URL + options) — fetch where the data is needed instead of drilling props.
- In the previous model, `fetch` is **not cached by default** and blocks rendering until complete.
- ORMs/DB clients are safe in Server Components: query logic and credentials never reach the client bundle.

### Parallel and sequential

`async/await` in a row is sequential. Fire promises first, then await:

```tsx
const artistData = getArtist(username)
const albumsData = getAlbums(username)
const [artist, albums] = await Promise.all([artistData, albumsData])
```

Layouts and pages at different segments render in parallel already; within one component, `Promise.all` (or `Promise.allSettled` to tolerate partial failure) is the pattern.

### Reusing data with `React.cache`

```ts
import { cache } from 'react'
export const getUser = cache(async () => {
  const res = await fetch('https://api.example.com/user')
  return res.json()
})
```

Memoization is **per request** — each request gets its own scope, nothing shared between requests (that is what the cache models below are for).

## Streaming

Slow data should not block the whole route. Two tools:

1. **`loading.tsx`** in the same folder as a page — streams the entire segment (auto `<Suspense>` wrapper; lives below the layout).
2. **`<Suspense>`** around the specific slow component — fine-grained, and the recommended tool for anything near runtime APIs.

```tsx
export default function BlogPage() {
  return (
    <>
      <header>…static, sent immediately…</header>
      <Suspense fallback={<BlogListSkeleton />}>
        <BlogList /> {/* async component; data streams in */}
      </Suspense>
    </>
  )
}
```

Pass promises instead of awaiting to stream into Client Components and resolve them with `use()`.

Bots/crawlers never see the shell — they get one fully rendered document, so anything that only works at build time will fail for them.

## Client Components

Two options: React's `use` API on a promise from the server, or a data library (SWR, React Query) for browser-side fetching. Libraries have their own cache semantics — coordinate with the server cache when mixing.

---

## Previous model (default in 16.3)

### `fetch` cache options

| `cache` option | Effect |
|---|---|
| *(unset, default)* | Fetched at request time (blocks rendering). Exception: during `next build`, fetches reachable *before* any request-time API run once at build time |
| `'force-cache'` | Cache forever-ish until revalidated (like `revalidate: Infinity`) |
| `'no-store'` | Never cached |

Per-request overrides via `next` options:

```tsx
await fetch(url, { next: { revalidate: 60 } })        // time-based, 60s
await fetch(url, { next: { tags: ['posts'] } })        // on-demand by tag
```

### Route segment config

Exported from `page.tsx` / `layout.tsx` / `route.ts` (still valid in 16.3 **unless** Cache Components is enabled, which removes `dynamic`/`revalidate`/`fetchCache`):

```tsx
export const dynamic = 'auto'        // 'auto' | 'force-dynamic' | 'error' | 'force-static'
export const revalidate = 60         // seconds; false = no time revalidation
export const fetchCache = 'auto'     // 'auto' | 'default-cache' | 'only-cache' | 'force-cache' | 'force-no-store' | ...
export const dynamicParams = true    // allow non-generateStaticParams values
```

- `force-dynamic` — render per request.
- `force-static` — force prerender; `cookies()`/`headers()`/`useSearchParams()` return empty values.
- `error` — build error if any request-time data is touched.

Reading `cookies()`, `headers()`, `searchParams`, or `useSearchParams()` **opts the whole route into dynamic rendering** in this model.

### `unstable_cache` for non-fetch functions

```ts
import { unstable_cache } from 'next/cache'
export const getUser = unstable_cache(
  async (id: string) => db.query(...),
  ['user'],                 // key prefix
  { tags: ['user'], revalidate: 3600 }
)
```

### On-demand revalidation

Call from a Server Action or Route Handler:

```ts
import { revalidateTag, revalidatePath } from 'next/cache'
revalidateTag('user', 'max')    // v16: second arg (cacheLife profile) is REQUIRED
revalidatePath('/profile')      // or by path — coarser, prefer tags
```

---

## Cache Components model (`cacheComponents: true`)

Every route produces a **static shell** (Partial Prerendering). Cached data goes into the shell; everything else streams behind a `<Suspense>` fallback at request time. The dev overlay surfaces "blocking prerender" insights when a route can't complete at build time.

### `'use cache'` directive

Caches the return value of async functions or components, at data level or UI level:

```ts
import { cacheLife } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheLife('hours')
  return db.query('SELECT * FROM products')
}

export default async function Page() {
  'use cache'            // caching a whole component/page
  cacheLife('hours')
  const users = await db.query('SELECT * FROM users')
  return <ul>{users.map(...)}</ul>
}
```

- Arguments and captured values form the **cache key** — different inputs, different entries.
- `'use cache'` at the top of a file caches **all exported functions** in it.
- Variants: **`'use cache: private'`** (reads cookies/headers/searchParams directly; result cached per-session in the browser only) and **`'use cache: remote'`** (durable shared store via a `cacheHandlers` config — pays off at high hit rates across instances).
- **Cannot be used directly in a Route Handler body** — extract to a helper function.

### `cacheLife`

Inside a `'use cache'` scope; pair it with every cache directive (implicit `default` otherwise).

| Profile | `stale` | `revalidate` | `expire` |
|---|---|---|---|
| `default` | 5m | 15m | never |
| `seconds` | 30s | 1s | 60s |
| `minutes` | 5m | 1m | 1h |
| `hours` | 5m | 1h | 1d |
| `days` | 5m | 1d | 1w |
| `weeks` | 5m | 1w | 30d |
| `max` | 5m | 30d | 1y |

`stale` — served from cache, refresh in background; `revalidate` — how long before revalidating; `expire` — hard removal. **Short-lived** caches (`seconds`, `revalidate: 0`, `expire` < 5m) are excluded from prerenders and become dynamic holes. Custom: `cacheLife({ stale: 3600, revalidate: 7200, expire: 86400 })`.

### `cacheTag` + `revalidateTag` / `updateTag`

```ts
export async function getPosts() {
  'use cache'
  cacheLife('hours')
  cacheTag('posts')
  return db.query(...)
}

// Server Action or Route Handler:
revalidateTag('posts', 'max')   // stale-while-revalidate — stale served while fresh loads

// Server Actions ONLY — immediate expiry, read-your-writes:
updateTag('posts')

// Refresh the client router from a Server Action:
refresh()
```

| | `updateTag` | `revalidateTag` |
|---|---|---|
| Where | Server Actions only | Server Actions + Route Handlers |
| Behavior | expires + refreshes in same request | stale-while-revalidate |
| Use | forms, settings, user's own data | catalogs, blog, docs |

### Rules for the static shell

- **Uncached data / runtime APIs** (`cookies()`, `headers()`, `searchParams`, `params`) must sit behind `<Suspense>` — otherwise the dev overlay shows a blocking-route insight.
- **Push async work down**: passing the `params`/`searchParams` promise to a child and awaiting it there (inside Suspense) keeps the layout static.
- **Random/time/crypto** (`Math.random()`, `Date.now()`, `crypto.randomUUID()`) must be explicit: `await connection()` then use, wrapped in Suspense (per-request values), or cache the value.
- **Predictable work** (module imports, `fs.readFileSync`, pure computation, sync DBs like `better-sqlite3`) prerenders automatically.
- **ISR**: `generateStaticParams()` prerenders listed params at build; unknown params serve the **App Shell** instantly and upgrade in the background with the real params.
- **Prefetching** (with `partialPrefetching` config): links prefetch the App Shell; `prefetch={true}` on a `<Link>` also resolves URL-derived `use cache` entries for the destination.
- **Storage**: prerendered HTML on disk/CDN; runtime `use cache` entries in an in-memory per-instance store by default (ephemeral on serverless) or a durable `cacheHandlers` store with `use cache: remote`. All stores reset on deploy (build id is in the key).

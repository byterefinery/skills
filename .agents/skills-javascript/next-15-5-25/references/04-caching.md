# Caching and Revalidation

## Static vs dynamic rendering

- **Static rendering** — the route is rendered once (at build, or on first visit) and served from cache.
- **Dynamic rendering** — rendered on every request. Triggered by **Dynamic APIs** (`cookies()`, `headers()`, `draftMode()`, `useSearchParams()`) or by uncached data (`fetch` without `cache` in 15).
- Under Partial Prerendering, a layout can be static while a `<Suspense>`-wrapped section streams dynamically (see PPR below).

Verify the actual mode from `next build` output: `○` = static, `ƒ` = dynamic.

## The four caches

| Cache | Scope | Lifetime | Invalidated by |
|---|---|---|---|
| **Request Memoization** | one server render pass | the request | automatically |
| **Data Cache** | server-side fetch results | across requests *and deployments* | `revalidateTag`, `revalidatePath`, time-based `next.revalidate`, `unstable_noStore` |
| **Full Route Cache** | rendered RSC payload + HTML of static routes | across requests; **cleared on deploy** | data revalidation, `revalidatePath`, Dynamic API usage |
| **Client Router Cache** | RSC payload of visited segments in the browser | until refresh or TTL (layouts 5 min default; pages not cached in 15) | `router.refresh`, `revalidatePath`, `revalidateTag`, `cookies.set/delete` |

Interactions: revalidating the Data Cache invalidates the Full Route Cache (render depends on data); invalidating the Full Route Cache does *not* touch the Data Cache. In a Server Action, both Data and Router caches are invalidated immediately; from a Route Handler, the Router Cache is *not* immediately invalidated (stale until refresh/TTL).

## Fetch options (server-side)

```ts
await fetch(url, {
  cache: 'force-cache' | 'no-store',
  next: { revalidate: 3600, tags: ['posts'] },
})
```

- **Default (`auto`)**: fetched once at `next build` for statically prerendered routes, but **not** stored in the Data Cache — dynamic routes refetch per request.
- `cache: 'force-cache'` — opt into the Data Cache (stale-while-revalidate: after `revalidate` elapses, stale data is served while a background refetch updates the cache).
- `cache: 'no-store'` — force per-request fetching even in static routes.
- `next.revalidate` — seconds; `false` = indefinite, `0` = never cache. A lower `revalidate` on any fetch in a route lowers the whole route's interval.
- `next.tags` — up to 128 tags, ≤256 chars each, for on-demand `revalidateTag`.
- **Conflicting options** (e.g. `{ revalidate: 3600, cache: 'no-store' }`) are *both ignored* with a dev warning.
- In dev: pages are never cached; the HMR fetch cache can serve stale data between edits (configurable via `serverComponentsHmrCache`, default applies to *all* fetches including `no-store`; cleared on navigation or full reload); hard refresh (`cache-control: no-cache`) bypasses all fetch cache options.

## Route Segment Config (per layout/page/route export)

```ts
export const dynamic = 'auto' | 'force-dynamic' | 'error' | 'force-static'
export const revalidate = false | 0 | 3600   // seconds; must be a literal
export const fetchCache = 'auto' | 'default-cache' | 'only-cache' | 'force-cache' | 'default-no-store' | 'only-no-store' | 'force-no-store'
export const dynamicParams = true | false
export const runtime = 'nodejs' | 'edge'
export const preferredRegion = 'auto' | 'global' | 'home' | string | string[]
export const maxDuration = 60
export const experimental_ppr = true
```

- `dynamic = 'force-dynamic'` — render every request (equivalent to all fetches `no-store` + `revalidate: 0`).
- `dynamic = 'error'` — like `getStaticProps`: build fails if any Dynamic API or uncached data is used.
- `dynamic = 'force-static'` — force static; Dynamic APIs return empty values.
- `revalidate` — the **lowest** value across a route's segments wins; `0` = always dynamic.
- `fetchCache` — advanced override of the default `cache` option for all fetches in a segment; use sparingly. In 15, the practical switch for restoring 14-style caching is `fetchCache = 'default-cache'`.
- Segment config is **disabled when the experimental `cacheComponents` flag is on** (the Cache Components model below takes over).

## On-demand revalidation

- `revalidatePath('/posts', 'page' | 'layout' | 'router')` — from Server Actions (and Route Handlers); updates route cache + client router cache immediately.
- `revalidateTag('posts')` — from Server Actions, Route Handlers, or a webhook endpoint; clears matching Data Cache entries.
- `unstable_cache(fn, keys, options)` — memoize non-fetch functions (DB clients, CMS SDKs) with the same `revalidate`/`tags` semantics; `unstable_noStore(fn)` opts a cached function out per call.

## Draft mode

Preview content not yet published (commonly CMS workflows):

```ts
import { draftMode } from 'next/headers'

export default async function Page() {
  const { isEnabled } = await draftMode()   // async in 15
  const posts = await getPosts({ draft: isEnabled })
  // ...
}
```

- Enable from a server context: `draftMode().enable()` sets a cookie (then `redirect`); disable with `.disable()`.
- A route that reads `draftMode()` is dynamic.

## Partial Prerendering (incremental in 15.5)

```js
// next.config.js
const nextConfig = { experimental: { ppr: 'incremental' } }
```

Then opt in per segment: `export const experimental_ppr = true` in a layout or page (applies to descendants; set `false` in a child to opt out). Without both, PPR is off. With PPR, the static shell is prerendered and content using Dynamic APIs or uncached fetches must sit inside `<Suspense>` to stream — otherwise the whole route goes dynamic.

## Experimental Cache Components model (15.5)

A second, additive caching model introduced experimentally in 15.5 — the direction 16 takes over. Data fetching happens **at runtime by default**; only code explicitly marked cacheable is prerendered and cached. Enable with either flag in `next.config`:

```js
// whole model — data fetching excluded from prerenders unless cached
const nextConfig = { experimental: { cacheComponents: true } }
// just the 'use cache' directive, without the runtime-by-default behavior
const nextConfig = { experimental: { useCache: true } }
```

With it enabled:

- **`'use cache'` directive** — at the top of a file, or inside a component/function. Everything in scope is cached; the cache key is build ID + function ID + serialized arguments.
- **`cacheLife`** (imported as `unstable_cacheLife` from `next/cache`) — sets the lifetime profile for a cached scope:

  ```tsx
  'use cache'
  import { unstable_cacheLife as cacheLife } from 'next/cache'

  export async function getPosts() {
    cacheLife('hours')   // profile: seconds | minutes | hours | days | weeks | max | default
    return db.query('SELECT * FROM posts')
  }
  ```

  Named profiles (`default`, `seconds`, `minutes`, `hours`, `days`, `weeks`, `max`) carry fixed `stale`/`revalidate`/`expire` values; define custom ones in the `cacheLife` config object. `staleTimes` and `expireTime` config options also tune the `default` profile.
- **`cacheTag`** (imported as `unstable_cacheTag` from `next/cache`) — tag a cached scope for on-demand invalidation via `revalidateTag`.
- **`connection()`** from `next/server` (stable since 15.0) — `await connection()` inside a component defers rendering until a real request arrives; use it for `Math.random()`, `new Date()`, or any value that must not be frozen at build time. Replaces `unstable_noStore`. Wrap in `<Suspense>` so the shell still streams.
- **`after()`** from `next/server` (stable since 15.1) — `after(callback)` schedules work (logging, webhooks) after the response or prerender finishes, in Server Components, Server Actions, Route Handlers, and Middleware. Not a Dynamic API; on static pages the callback runs at build/revalidate time.

Rule of thumb: treat this model as experimental — expect breaking changes before 16. Don't mix it with route segment config in the same segment (the config exports are disabled while `cacheComponents` is on).

## Static export

`output: 'export'` in next.config produces a fully static site: no SSR, no API routes, no ISR; every dynamic route must list its paths in `generateStaticParams`.

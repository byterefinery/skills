# Caching with Cache Components (v16)

The caching model introduced in Next.js 16. Enable it with `cacheComponents: true` in `next.config.ts`; without it, the project uses the previous model (`fetch` cache options, route segment configs) — a separate guide, [caching-without-cache-components](https://nextjs.org/docs/app/guides/caching-without-cache-components).

## Contents

- [Enable and what it changes](#enable-and-what-it-changes)
- [The static shell](#the-static-shell)
- [use cache](#use-cache)
- [cacheLife profiles](#cachelife-profiles)
- [Tags and revalidation](#tags-and-revalidation)
- [Runtime data and streaming](#runtime-data-and-streaming)
- [Dynamic routes under Cache Components](#dynamic-routes-under-cache-components)
- [Storage and durability](#storage-and-durability)
- [Adoption workflow](#adoption-workflow)
- [UI state preservation](#ui-state-preservation)
- [Debugging](#debugging)

## Enable and what it changes

```ts
const nextConfig: NextConfig = {
  cacheComponents: true,
}
```

- Requires the **Node.js runtime** — routes with the deprecated `runtime = 'edge'` export must migrate (use Proxy for edge-like needs).
- Implements **Partial Prerendering (PPR) as default**: Next.js prerenders a static HTML shell served immediately, with dynamic content streaming in when ready.
- Data fetching is **dynamic by default** — nothing is cached unless you add `use cache`.
- Route segment configs `dynamic`, `revalidate`, `fetchCache` **error** when exported; `dynamicParams` **fails the build**. Translate them (see [01-upgrade-to-v16](01-upgrade-to-v16.md)).
- Validation: in dev, Next.js checks whether each route renders instantly on navigation and surfaces errors/insights naming the blocking component.

## The static shell

Prerendering handles each part of a page differently:

| Part | Behavior |
| --- | --- |
| `use cache` (long-lived) | Result cached and included in the static shell |
| `<Suspense>` fallback | Fallback ships in the shell; content streams at request time |
| Predictable values (module imports, `fs.readFileSync`, pure compute) | Complete during prerender automatically |
| Random values/timestamps (`Math.random`, `Date.now`, `crypto.randomUUID`) | Must be handled explicitly — `connection()` + `<Suspense>`, or cached |

The shell is what direct navigation and (with Partial Prefetching) client transitions receive instantly. Deeper async access in the tree = more of the page in the shell — push `await`s down toward leaves.

**Bots and crawlers** are detected by user agent and get a fully dynamic render (no shell reuse), so anything your shell depends on must also work at request time.

## use cache

The `'use cache'` directive marks a route, component, or async function as cacheable:

```tsx
// Function level — data-level caching
export async function getProducts() {
  'use cache'
  cacheLife('hours')
  return db.query('SELECT * FROM products')
}

// Component level — UI-level caching
export async function LatestPosts() {
  'use cache'
  cacheLife('hours')
  return <PostsList />
}

// File level — every export becomes cached (and must be async)
'use cache'
```

Key rules:

- Cached functions must be **async**.
- The **cache key** is build ID + function location hash + serialized arguments + values captured from outer scopes (closures auto-become key parts). Different inputs → different entries.
- Args and return values must be **serializable** (primitives, plain objects, arrays, Dates, Maps/Sets, JSX pass-through). Class instances, functions, symbols, `URL` are not — pass-through patterns (e.g., `children`, Server Actions) work only if you never introspect the value.
- **No runtime APIs inside**: `cookies()`, `headers()`, `searchParams` are forbidden in a `use cache` scope (error `next-request-in-use-cache`), and the restriction follows the call stack. Read them outside and pass values as arguments. `draftMode()`'s `isEnabled` is the one exception.
- `React.cache` is **isolated** inside `use cache` — you cannot pass data into a cached scope through a shared store; use arguments.
- Variants: `'use cache: remote'` stores in a durable platform cache handler (network roundtrip, platform fees) — only worth it at high hit rates; `'use cache: private'` caches results that read runtime data directly, keyed per session (browser-side).

## cacheLife profiles

Set the lifetime in every `use cache` scope so behavior is explicit at the call site (otherwise the `default` profile applies implicitly):

| Profile | stale (client) | revalidate (server) | expire |
| --- | --- | --- | --- |
| `default` | 5m | 15m | never |
| `seconds` | 30s | 1s | 60s |
| `minutes` | 5m | 1m | 1h |
| `hours` | 5m | 1h | 1d |
| `days` | 5m | 1d | 1w |
| `weeks` | 5m | 1w | 30d |
| `max` | 5m | 30d | 1y |

- Custom and redefined profiles live in `next.config.ts` under `cacheLife` (including redefining `default`/`max`); types and autocomplete are generated from the config by `next dev`/`build`/`typegen`.
- A cache is **short-lived** with the `seconds` profile, `revalidate: 0`, or `expire` under 5 minutes — short-lived caches are excluded from prerenders and become dynamic holes instead.
- `stale`/`revalidate`/`expire` are all optional in an inline object; `expire` must be longer than `revalidate`.

## Tags and revalidation

Tag cached data with `cacheTag` inside a `use cache` scope, then invalidate on-demand:

```tsx
async function getProducts() {
  'use cache'
  cacheLife('max')
  cacheTag('products')
  return db.products.findMany()
}
```

| API | Where | Behavior | Use when |
| --- | --- | --- | --- |
| `updateTag(tag)` | Server Actions only | Expires and immediately refreshes (read-your-writes) | User must see their change now |
| `revalidateTag(tag, profile)` | Server Actions + Route Handlers | Stale-while-revalidate; **second argument required** (e.g., `'max'`) | Slight delay acceptable (content) |
| `revalidatePath(path)` | Server Actions + Route Handlers | Invalidates a whole route path | You do not track tags |
| `refresh()` | Server Actions | Refreshes the client router | Update a header count without navigating |

Pairing is common: `cacheLife('max')` + `cacheTag('posts')` + a CMS webhook calling `revalidateTag('posts', 'max')` — content changes only when published, and readers see stale-while-revalidate.

## Runtime data and streaming

Accessing `cookies()`, `headers()`, `searchParams`, or `params` (when dynamic) outside a `<Suspense>` boundary surfaces the **blocking-prerender-runtime** insight. The fix pattern:

```tsx
export default function Page({ searchParams }: PageProps<'/search'>) {
  return (
    <Suspense fallback={<p>Loading results...</p>}>
      <Results searchParams={searchParams} />
    </Suspense>
  )
}

async function Results({ searchParams }) {
  const { q } = await searchParams
  const results = await search(q)
  return <ul>{results.map(...)}</ul>
}

async function search(q) {
  'use cache'
  return db.search(q)
}
```

- Pass the Promise down as a prop and await inside the boundary (or unwrap with `.then()`); the page prerenders, only the leaf streams.
- Extract runtime values and pass them as arguments to a `'use cache'` function — the value becomes part of the cache key, and prefetch can resolve it per link.
- For a unique value per request (`crypto.randomUUID()` etc.), call `await connection()` from `next/server` before the call and wrap in `<Suspense>`; otherwise the build errors.

## Dynamic routes under Cache Components

- `generateStaticParams` **must return at least one param** — an empty array errors (`empty-generate-static-params`). Return a subset (even one); unknown params still render at request time via the App Shell, which is upgraded in the background (ISR with Cache Components).
- `dynamicParams` is **not supported** — build error. Reject unknown params with `notFound()` in the page instead.
- To keep the shell, pass the `params` Promise into a `<Suspense>` boundary instead of awaiting it at the top of the page/layout.

## Storage and durability

- Default storage is **in-memory, per server instance** — ephemeral on serverless (entries often do not persist across requests or deploys), persistent on self-hosted (size controlled by `cacheMaxMemorySize`).
- Durable, cross-instance caching: `'use cache: remote'` or a custom [cache handler](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheHandlers) in config.
- **All stores are scoped to a single deployment** — the cache key includes the build ID (or `deploymentId`), so a new deploy starts fresh even for durable stores. For data that must survive deploys, use the `fetch` Data Cache or `unstable_cache`.
- The browser keeps prefetched/cached RSC payloads fresh for the `stale` window (client enforces a minimum 30s stale time).

## Adoption workflow

Adopting Cache Components into an existing app (full details in the [migrating-to-cache-components guide](https://nextjs.org/docs/app/guides/migrating-to-cache-components)):

1. **Enable the flag** — `cacheComponents: true`. If the app already uses `'use cache'`, it errors until the flag is on; enabling first is not a regression.
2. **Translate old configs** — remove `dynamic`/`revalidate`/`fetchCache` exports, translating each to `use cache` + `cacheLife` (translate, don't delete — each encodes needed behavior; leave `// TODO` comments where you must defer).
3. **Opt out what is not ready** — `export const instant = false` on the segment that raised the insight (marks it allowed to block; does not force dynamic). One pass: `npx @next/codemod@canary cache-components-instant-false ./app`.
4. **Fix synchronous IO** — `new Date()`, `Math.random()`, `crypto.randomUUID()` during prerender are hard build errors that `instant = false` does not clear: move behind `<Suspense>` + `connection()` or into a Client Component.
5. **Convert one route at a time** — remove its `instant = false`, resolve the insights (cache with `use cache` or stream with `<Suspense>`), repeat until none remain.
6. An official agent skill drives this per feature with user checkpoints: `npx skills add vercel/next.js --skill next-cache-components-adoption` (see [07-agent-workflows](07-agent-workflows.md)).

## UI state preservation

With Cache Components, Next.js keeps hidden routes mounted via React `<Activity>` mode instead of unmounting: `useState` values, form inputs, and scroll position survive navigation back and forth. If code relied on unmount to reset state, add explicit resets:

- Dropdowns/popovers stay open on return — close them in a `useLayoutEffect` cleanup.
- Dialogs with init logic (focus, etc.) — derive dialog state from the URL.
- Forms after submit — reset values and `useActionState` results in the handler or a cleanup effect.

See the [preserving-ui-state guide](https://nextjs.org/docs/app/guides/preserving-ui-state) for patterns.

## Debugging

- `NEXT_PRIVATE_DEBUG_CACHE=1 next dev` (or `next start`) for verbose cache logging; cached function console logs appear with a `Cache` prefix in dev.
- **Build hang** — "Filling a cache during prerender timed out" means a `use cache` function is awaiting a Promise of runtime/uncached data (passed as a prop, closure, or from a shared `Map`). Await the source outside the cached scope and pass the value.
- `next build --debug-prerender` unminifies server code and continues past the first prerender error.
- Dev overlay fix cards and the MCP `get_errors` tool surface insights; the offending route still returns 200 in dev — insights appear only in the overlay, dev-server log, or MCP.

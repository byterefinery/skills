# Pages Router

The `pages/` directory router (pre-App-Router Next.js). Fully supported in 15 but in maintenance mode — new features (Server Components, streaming, PPR, Server Actions) are App Router only. New work should go to `app/`; use this reference for maintaining legacy code.

## Routing

- `pages/index.js` → `/`; nested folders nest URLs; `pages/api/...` becomes API routes.
- Dynamic: `pages/blog/[slug].js`; catch-all `pages/shop/[...slug].js`; optional catch-all `pages/docs/[[...slug]].js`.
- Special files (top-level of `pages/`):
  - `_app.js` — wraps every page (theme, global state); custom `App` component required to use `Component`/`pageProps`.
  - `_document.js` — the `<html>`/`<head>`/`<body>` shell (rarely needed; breaks SSR if misused).
  - `_error.js` — custom error page (receives `err`, `res`).
  - `404.js`, `500.js` — custom not-found / server-error pages.
- `<Head>` component (`next/head`) manages per-page `<head>` tags.
- Both routers can coexist; App Router wins on overlapping routes.

## Data fetching

### `getStaticProps` — SSG (rendered at build, or on-demand with ISR)

```ts
export const getStaticProps = async () => {
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()
  return { props: { posts }, revalidate: 60 * 60 }  // ISR: revalidate every hour
}
```

- Runs at `next build`, in the background during ISR, or on-demand via `revalidatePath`/`revalidate` in an API route.
- **Props ship to the client** for hydration — never return secrets.
- No access to the request (no headers/cookies) — that's `getServerSideProps`.

### `getStaticPaths` — which dynamic paths exist at build

```ts
export const getStaticPaths = async () => {
  const posts = await listPostSlugs()
  return { paths: posts.map((slug) => ({ params: { slug } })), fallback: false }
}
```

- `fallback: false` — unlisted paths 404. If the page has no `getStaticPaths` at all, every path is generated on demand at request time (the route stays dynamic).
- `fallback: true` — serve the page immediately with `fallback: null` in props, generate in the background (SSG + client-side fallback shell).
- `fallback: 'blocking'` — first visit waits for generation, then it's cached.

### `getServerSideProps` — SSR (every request)

```ts
export const getServerSideProps = async ({ req, res, params }) => {
  const session = getSession(req)
  return { props: { user: session?.user } }  // or { redirect: { destination, permanent } } / { notFound: true }
}
```

- Runs on every request; add `revalidate` to make it ISR instead.
- Has access to `req`/`res` (cookies, headers) — the only way in Pages Router to do per-user data.

### Automatic Static Optimization

The rendering mode is decided by what the page exports:

| Page exports | Mode |
|---|---|
| none | SSG |
| `getStaticProps` | SSG (+ ISR with `revalidate`) |
| `getServerSideProps` | SSR (+ ISR with `revalidate`) |
| client-side fetch only | CSR (no data in initial HTML) |

## API routes

`pages/api/hello.js` → `POST/GET /api/hello`:

```js
export default function handler(req, res) {
  if (req.method === 'POST') {
    res.status(200).json({ ok: true })
    return
  }
  res.status(405).end()
}
```

- `req`/`res` are the Node.js http API with a Next.js flavor (`req.query`, `res.status()`).
- Route config exports work: `export const config = { api: { responseLimit: '10mb', bodyParser: false, externalResolver, prefetch: false } }` plus `runtime = 'edge'` / `maxDuration`.
- CORS is your responsibility (there is no built-in CORS handling).
- API routes can trigger ISR: `res.revalidate(path)` or `res.revalidateTag(tag)` (13.3+).
- App Router equivalent is Route Handlers (see 05-route-handlers-middleware) — migrate new endpoints there.

## Preview mode (draft mode equivalent)

```js
// enable
res.setPreviewData({ role: 'admin' })  // sets a cookie
// read in getStaticProps/getServerSideProps:
context.preview === true
```

- Use for CMS previews of unpublished content.
- App Router equivalent: `draftMode()` from `next/headers` (see 04-caching).

## Migrating

See 09-migration-upgrading for the pages → app mapping (each `pages/` file has a direct `app/` counterpart).

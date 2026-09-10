# Migration and Upgrading

## Upgrading to 15

Automate first:

```bash
npx @next/codemod@canary upgrade latest
# or per-change: npx @next/codemod@latest next-async-request-api .
npm i next@15 react@19 react-dom@19 eslint-config-next@15
```

Then work through the 15.0 breaking changes (all from the official upgrade guide):

1. **React 19 minimum.** The App Router bundles React 19 canary-based releases built-in; the Pages Router uses your installed `react`/`react-dom` (19 minimum).
   - `useFormState` → **`useActionState`** (old name deprecated in React 19; the new hook also exposes `pending` directly).
   - `useFormStatus` gains `data`, `method`, `action` keys.
2. **Async Request APIs (breaking).** `params` and `searchParams` props, plus `cookies()`, `headers()`, `draftMode()`, become async — `await` them in 15. Sync access is *temporarily* tolerated in 15 (deprecated; cast types via `UnsafeUnwrappedCookies`/`UnsafeUnwrappedHeaders`/`UnsafeUnwrappedDraftMode` if you must bridge) and removed in 16. Affects `layout`, `page`, `route`, `default`, `generateMetadata`, image/icon generators.
3. **`fetch` no longer cached by default** (App Router). Opt in with `{ cache: 'force-cache' }` per request or `export const fetchCache = 'default-cache'` per segment.
4. **Route Handler `GET` no longer cached by default.** Add `export const dynamic = 'force-static'` (or `revalidate`) to restore.
5. **Client-side Router Cache** — page segments no longer reused on `<Link>`/`useRouter` navigation (still reused for back/forward and shared layouts). Re-enable with `experimental.staleTimes: { dynamic, static }` (seconds).
6. **`next/font` replaces `@next/font`** — package removed; codemod renames imports.
7. **`runtime: 'experimental-edge'` removed** — use `'edge'`; error otherwise.
8. **Config renames** — `experimental.bundlePagesExternals` → `bundlePagesRouterDependencies`; `experimental.serverComponentsExternalPackages` → `serverExternalPackages`.
9. **Speed Insights auto-instrumentation removed** — add `@vercel/speed-insights/next` manually to keep it.
10. **`NextRequest.geo` / `.ip` removed** — host-provided; on Vercel use `geolocation()`/`ipAddress()` from `@vercel/functions`.
11. **Node.js 18.18+** is the minimum.
12. **Turbopack** — stable for `next dev` (default in new apps), **beta** for `next build --turbopack`. Don't rely on Turbopack build output parity in 15.
13. **ESLint 9** is supported (flat config); `next lint` is deprecated in 15.5 (removed in 16) — plan to run ESLint (or Biome) directly.

## Pages Router → App Router

There is no single codemod for the whole migration — do it route by route. The mapping:

| Pages Router | App Router |
|---|---|
| `pages/index.js` | `app/page.tsx` |
| `pages/blog/[slug].js` | `app/blog/[slug]/page.tsx` |
| `pages/_app.js` | root `app/layout.tsx` (+ client provider components) |
| `pages/_document.js` | root layout `html`/`body`; global CSS in root layout |
| `pages/api/...` | `app/.../route.ts` Route Handlers |
| `getStaticProps` | async Server Component (fetch inline) + `generateStaticParams` |
| `getStaticPaths` fallback | `dynamicParams` / `loading.tsx` |
| `getServerSideProps` | dynamic rendering (Dynamic APIs) or `dynamic = 'force-dynamic'` |
| `<Head>` | `metadata` export / `generateMetadata` |
| Preview mode | Draft mode (`draftMode()`) |
| `next/link` `shallow` | not available; use `router.refresh()` patterns |
| Context providers in `_app` | Client Component provider inside the root layout |
| Client data (SWR/etc.) | unchanged — Client Components still fetch client-side |

Practical order:

1. Create `app/` next to `pages/` — they coexist; App Router wins on overlaps.
2. Start with the root layout + a few simple pages; run the app and fix hydration/context issues.
3. Migrate data fetching last (it changes when code runs).
4. Move API routes to Route Handlers; keep `pages/api` only where legacy clients hit it.
5. Delete `pages/` once traffic is fully on `app/`.

Codemods and step-by-step: the official `app-router-migration` guide in the repo docs; `from-create-react-app` and `from-vite` guides cover framework switches (Vite: port `vite.config` features to `next.config`, `public/` maps to `public/`, assets to imports).

## Upgrading within 15.x

15.x releases are additive; watch the release notes for: `next lint` deprecation (15.5), PPR incremental adoption (`experimental.ppr: 'incremental'`), the experimental `use cache` directive and `cacheComponents` model (15.5), typed routes, and `next typegen` (15.5). Pin a minor you've tested and upgrade deliberately.

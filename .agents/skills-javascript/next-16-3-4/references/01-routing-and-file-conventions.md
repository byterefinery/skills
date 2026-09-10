# Routing and File Conventions (App Router)

## Table of contents

1. [File conventions](#file-conventions)
2. [Routing patterns](#routing-patterns)
3. [Parallel and intercepted routes](#parallel-and-intercepted-routes)
4. [Component hierarchy](#component-hierarchy)
5. [Metadata and SEO files](#metadata-and-seo-files)
6. [Linking and navigation](#linking-and-navigation)
7. [Navigation APIs](#navigation-apis)

## File conventions

Files named by convention inside `app/` (or `src/app/`). A route is **not publicly accessible** until a `page` or `route` file exists in the segment; other colocated files are never routable.

| File | Ext | Purpose |
|---|---|---|
| `layout` | `.js/.jsx/.tsx` | Shared UI (nav, footer) wrapping child segments. Root layout (`app/layout.*`) is **required** and must contain `<html>` and `<body>` |
| `page` | `.js/.jsx/.tsx` | Renders a UI route. Receives `params` and `searchParams` **as Promises** |
| `loading` | `.js/.jsx/.tsx` | Suspense fallback; streams the whole segment while data resolves. Sits *below* `layout`, so it cannot cover runtime data accessed in the layout itself |
| `error` | `.js/.jsx/.tsx` | Client-side error boundary for the segment. **Must be a Client Component** and must accept `error` + `reset` props |
| `global-error` | `.js/.jsx/.tsx` | Error boundary at the root layout level (root layout has no parent boundary) |
| `not-found` | `.js/.jsx/.tsx` | 404 UI. Thrown by `notFound()` in any component |
| `template` | `.js/.jsx/.tsx` | Like layout but **remounts** when its own segment (incl. dynamic params) changes; layouts stay cached |
| `default` | `.js/.jsx/.tsx` | Fallback for parallel route slots. **Required in every `@slot` since v16** — builds fail without it |
| `route` | `.js/.ts` | API endpoint (Route Handler). Cannot coexist with `page` at the same segment |
| `unauthorized` / `forbidden` | `.js/.jsx/.tsx` | 401/403 UI triggered by `unauthorized()`/`forbidden()` |
| `instrumentation` | `.ts` | Project root: `register()` for global hooks (OpenTelemetry, logging) |
| `mdx-components` | `.js/.ts` | Global component overrides for MDX |

## Routing patterns

Folders map to URL segments; a route becomes public only when a `page`/`route` file exists.

```
app/
├── layout.tsx                  # root layout, wraps everything
├── page.tsx                    # /
├── (marketing)/                # route group — omitted from URL
│   ├── layout.tsx              # own layout for marketing section
│   └── about/page.tsx          # /about
├── blog/
│   ├── layout.tsx              # wraps /blog and children
│   ├── page.tsx                # /blog
│   ├── _components/            # private folder — not routable
│   │   └── Post.tsx
│   └── [slug]/
│       ├── page.tsx            # /blog/my-post
│       ├── loading.tsx         # streams /blog/[slug]
│       └── [comment]/page.tsx  # /blog/my-post/42
```

Dynamic segments (values accessed via the `params` promise):

| Path | URL pattern |
|---|---|
| `app/blog/[slug]/page.tsx` | `/blog/my-first-post` |
| `app/shop/[...slug]/page.tsx` | catch-all: `/shop/clothing`, `/shop/clothing/shirts` (`slug` is an array) |
| `app/docs/[[...slug]]/page.tsx` | optional catch-all: `/docs`, `/docs/a/b` |

- **Route groups** `(group)` organize without affecting the URL; the main use is giving a subset of routes its own layout. Multiple root layouts are possible by removing `app/layout.tsx` and placing one per top-level group (each needs `<html>`/`<body>`).
- **Private folders** `_name` opt the folder (and subfolders) out of routing. A URL segment starting with `_` needs `%5F` URL-encoding.
- **`src/` folder** is optional and just separates app code from root config.

## Parallel and intercepted routes

Named slots for UI patterns like modal-based details:

- **Parallel routes** — `app/@modal/` renders into a `<Modal/>` slot in a parent layout via `React.use()` on the `modal` slot promise. **Every slot needs a `default.tsx`** in v16 (call `notFound()` or return `null`).
- **Intercepting routes** — render another route inside the current layout, e.g. a details page opened as a modal over a list without changing URL:
  - `(.)folder` — intercept same level
  - `(..)folder` — intercept one level up (most common for list→detail modals)
  - `(...)folder` — intercept from the root

```tsx
// app/@modal/(.)about/page.tsx — /about shown as modal over current route
```

## Component hierarchy

Rendered in this order (deepest segment nested inside parents):

```
layout → template → error (boundary) → loading (suspense) → not-found (boundary) → page / nested layout
```

Key consequence: `loading.tsx` is *below* `layout.tsx`, so a layout that reads `cookies()`, `headers()`, or uncached fetch data **blocks navigation** (no loading fallback) — move such access into `page.tsx` or wrap it in its own `<Suspense>`.

## Metadata and SEO files

| File | Purpose |
|---|---|
| `icon.*` / `apple-icon.*` | App icons (file or `.tsx` generating them; generated-image `params`/`id` are **Promises** in v16) |
| `opengraph-image.*` / `twitter-image.*` | Social cards (file or `.tsx`; same async-params rule) |
| `sitemap.ts` | Generated sitemap; `id` from `generateSitemaps()` is a **Promise** in v16 |
| `robots.ts` | Generated robots file |

Code-based metadata: `export const metadata: Metadata`, `export const viewport: Viewport`, or `generateMetadata()` / `generateViewport()` functions (receive `params` as a Promise).

## Linking and navigation

`<Link>` from `next/link` is the primary navigation primitive (client-side, prefetches by default on viewport entry):

```tsx
import Link from 'next/link'

<Link href="/blog/some-post">Post</Link>
<Link href={{ pathname: '/docs', query: { slug: 'intro' } }}>Docs</Link>
<Link href="/about" replace scroll={false}>About</Link>
```

- `href` — string or object `{ pathname, query, hash }`. Relative paths required in App Router (no leading `/` for the same host is fine; `https://` and `mailto:` allowed).
- `prefetch` — `true` (default on hover/viewport), `false`, or `'viewport'`/`'popstate'`/`'always'`.
- `replace` — replaces history entry instead of pushing.
- `scroll` — defaults to `true`; `false` keeps scroll position.
- `onNavigate` — intercept/block navigation (return `false` to cancel).
- **Do not** use `<a>` tags for same-origin navigation — you lose client routing, prefetching, and RSC payload.
- Programmatic navigation: `useRouter()` (Client Component) — `router.push/replace/back/forward/refetch/prefetch`.

## Navigation APIs

| API | Where | Behavior |
|---|---|---|
| `redirect(url)` | Server Components, Server Actions, Route Handlers, proxy | Throws a redirect (307 by default; 308 if the URL is relative) |
| `permanentRedirect(url)` | same | 308 (301 for relative) |
| `notFound()` | anywhere on the server side | Triggers the nearest `not-found.tsx` |
| `unauthorized()` / `forbidden()` | server side | Triggers `unauthorized.tsx` / `forbidden.tsx` |
| `useRouter` / `usePathname` / `useParams` / `useSearchParams` | Client Components | Client navigation + URL state. `useSearchParams()` must be wrapped in `<Suspense>` during prerendering |
| `useSelectedLayoutSegment(s)` | Client Components | Dynamic param(s) of the nearest layout that did *not* re-render |
| `generateStaticParams()` | pages with dynamic segments | Prerenders listed param values at build time; `dynamicParams` (default `true`) controls whether unknown params still render |
| `useLinkStatus()` | Client Components | Prefetch state of a link (idle/loading/complete) |

`generateStaticParams` + `dynamicParams = false` gives fully-static routes with 404s for unknown params:

```tsx
export async function generateStaticParams() {
  return [{ slug: 'a' }, { slug: 'b' }]
}
export const dynamicParams = false
```

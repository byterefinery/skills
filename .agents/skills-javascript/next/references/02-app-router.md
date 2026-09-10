# App Router — structure, routing, and errors

How Next.js 16 resolves files into routes, and the conventions around layouts, navigation, and error handling.

## Contents

- [Project structure](#project-structure)
- [File conventions](#file-conventions)
- [Root layout](#root-layout)
- [Dynamic routes](#dynamic-routes)
- [Route groups and private folders](#route-groups-and-private-folders)
- [Parallel routes](#parallel-routes)
- [Navigation](#navigation)
- [Error handling](#error-handling)

## Project structure

```
app/                    # App Router routes
├── layout.tsx          # Root layout (required)
├── page.tsx            # /
├── blog/
│   ├── layout.tsx      # wraps /blog and descendants
│   ├── [slug]/
│   │   └── page.tsx    # /blog/:slug
│   └── _components/    # private folder, not routable
├── (marketing)/        # route group, omitted from URL
└── api/
    └── items/route.ts  # route handler
public/                 # static assets served at /
src/                    # optional wrapper around app/
proxy.ts                # request proxy (root or in src/)
next.config.ts
```

Top-level files: `next.config.ts` (or `.js/.mjs/.cjs`), `instrumentation.ts` (OpenTelemetry/OTel hooks), `.env*` files (never commit), `eslint.config.mjs`, `tsconfig.json`, `next-env.d.ts` (gitignore it).

If both `app/` and `src/app/` exist, Next.js builds `app/` and `src/app/` routes are shadowed and unbuilt — pick one tree.

## File conventions

| File | Purpose |
| --- | --- |
| `page.tsx` | Renders a route. A segment is public when it has `page` or `route` |
| `layout.tsx` | Shared UI wrapping child segments; the root layout must contain `<html>` and `<body>` |
| `loading.tsx` | Loading UI shown while the segment suspends |
| `error.tsx` | Client-component error boundary for the segment |
| `global-error.tsx` | Error boundary for the root layout itself |
| `not-found.tsx` | 404 UI (route level; root level for the app) |
| `unauthorized.tsx` | 401 UI, rendered when `unauthorized()` is invoked (experimental) |
| `forbidden.tsx` | 403 UI, rendered when `forbidden()` is invoked (experimental) |
| `route.ts` | Route handler (API endpoint) — `.ts`/`.js` only |
| `template.tsx` | Layout that re-renders on every navigation (no state preservation) |
| `default.tsx` | Fallback for a parallel route slot — **required in 16** |

A `route.ts` and `page.tsx` cannot share the same segment. Layouts are not re-created on navigation within their segment (that is what `template` is for).

## Root layout

Required, must render `<html>` and `<body>`. It wraps all routes. Under Cache Components, reading runtime data at the root layout makes the whole subtree request-bound — for `<html>` attributes driven by cookies (theme, locale), use the inline `<script>` pattern from the [preventing-flash-before-hydration](https://nextjs.org/docs/app/guides/preventing-flash-before-hydration) guide instead of reading the cookie on the server.

## Dynamic routes

Square-bracket segments: `[slug]`, catch-all `[...slug]`, optional catch-all `[[...slug]]`.

In 16, `params` is a **Promise** — always `await` it:

```tsx
export default async function Page({ params }: PageProps<'/blog/[slug]'>) {
  const { slug } = await params
  return <article>{slug}</article>
}
```

`generateStaticParams()` lists the param values to prerender at build time. Under Cache Components it must return **at least one** value (an empty array errors); unknown paths still render at request time via the App Shell. `dynamicParams` is **not supported** with `cacheComponents` — call `notFound()` when a param resolves to no data. See [04-caching](04-caching.md) for the full prerendering model.

## Route groups and private folders

- **Route groups** `(marketing)` organize code without changing the URL; they let you scope layouts per group.
- **Private folders** `_components`, `_lib` are never routable — the safe place for colocated UI and helpers.

## Parallel routes

Segments prefixed with `@` (e.g., `app/@modal/(.).../route.ts` patterns) render multiple slots of the same URL concurrently. In 16 **every slot needs a `default.tsx`** (fallback when no match), or the build fails:

```tsx
// app/@modal/default.tsx
import { notFound } from 'next/navigation'
export default function Default() {
  notFound()
}
```

## Navigation

- `<Link href="/x">` is the primary primitive — it prefetches and transitions client-side.
- `useRouter` from `next/navigation` for programmatic `push`/`replace`/`back`; `redirect()` and `notFound()` from Server Components/Server Actions; `usePathname`, `useParams`, `useSearchParams` in Client Components (`useSearchParams` always needs a `<Suspense>` boundary).
- Under Cache Components, when a route has dynamic params not covered by `generateStaticParams`, components that read `usePathname`/`useParams`/`useSelectedLayoutSegment(s)` suspend while the static shell is generated — wrap them in `<Suspense>` and push the read to the smallest leaf component.
- Prefetching: with Partial Prefetching enabled, the router prefetches each route's App Shell by default; `prefetch={true}` on a `<Link>` additionally resolves URL data (searchParams/params) at prefetch time.

## Error handling

- **`error.tsx`** is a **Client Component** (it must be, to use hooks/state for recovery UI) and catches errors from rendering within its segment. Pair it with `useErrorBoundary`-style state or plain conditional UI.
- **`notFound()`** throws a special not-found error; the nearest `not-found.tsx` renders. `forbidden()` and `unauthorized()` work the same for 403/401 (experimental in 16).
- **`loading.tsx`** renders while the segment's Promise suspends; it doubles as the fallback for the whole segment.
- In 16, use the [`catchError`](https://nextjs.org/docs/app/api-reference/functions/catchError) function for component-level error boundaries instead of only file conventions.
- A **Suspense boundary contains async access**; an **error boundary contains failures** — wrap subtrees that might error while rendering.
- Debug build-time rendering failures with `next build --debug-prerender` (unminifies server code and continues past the first failure).

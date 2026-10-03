---
name: next-15-5-25
description: >
  Next.js 15.5.25 — React meta-framework for full-stack web apps built on React Server
  Components, file-based routing (App Router and legacy Pages Router), streaming, caching,
  and Server Actions. Covers App Router file conventions (layout, page, loading, error,
  template, route), server/client component boundaries, async request APIs (params,
  searchParams, cookies, headers, draftMode), data fetching and the four caches,
  revalidation, draft mode, Partial Prerendering, the experimental use cache / cacheLife /
  cacheTag Cache Components model, Server Actions and forms, Route Handlers, middleware on
  Edge or Node.js runtime, metadata and OG images, next/image and next/font, Pages Router
  maintenance, upgrading from 14, and the CLI and config. Use when creating, modifying, or
  debugging Next.js 15 apps, or maintaining a Pages Router codebase.
license: MIT
compatibility: Node.js 18.18+; React 19; Turbopack for dev (beta for build); npm, pnpm, yarn, or bun
metadata:
  tags:
    - javascript
    - frontend
    - framework
    - react
    - nextjs
    - ssr
    - server-components
---

# next 15.5.25

## Overview

Next.js 15 is a React meta-framework for full-stack web applications, built on React Server Components, file-system routing, and Rust-based build tooling (Turbopack). This skill targets **version 15.5.25**, using the official 15.5.25 docs as the source of truth.

Next.js ships two routers. New work should use the **App Router** (`app/` directory) — it supports Server Components, streaming, Server Actions, and Partial Prerendering. The **Pages Router** (`pages/`) remains fully supported for existing projects but is in maintenance mode. Both can coexist in one project.

Version 15 is not a cosmetic release. The changes that most often break code or assumptions:

1. **Async Request APIs** — `params` and `searchParams` props, and the `cookies()`, `headers()`, and `draftMode()` functions, are now `Promise`-based. Synchronous access still works in 15 but is deprecated and was removed in 16.
2. **React 19** — the App Router bundles React 19 (canary-based) built-in; `react`/`react-dom` 19 is the minimum for the Pages Router. React 19 renamed `useFormState` to `useActionState`.
3. **`fetch` is not cached by default** — server-side `fetch` and Route Handler `GET` methods no longer use the Data Cache unless you opt in with `{ cache: 'force-cache' }` or a `fetchCache` segment config.
4. **Turbopack** — stable for `next dev` (`--turbopack` flag, the default in new apps), still beta for `next build --turbopack`.
5. **Client-side Router Cache** — page segments are no longer reused between navigations (layouts and loading states still are), fixing stale-content bugs but changing what you can expect after `<Link>` navigation.

15.5 additions on top of that (full details in the references): **PPR incremental adoption** (`experimental.ppr: 'incremental'` + `experimental_ppr` per segment), the **experimental Cache Components model** (`use cache` directive, `cacheLife`/`cacheTag`, `connection()`), **`next typegen`** for route types without a build, **Node.js runtime for middleware**, stable **`after()`** for post-response work, and the **`next lint` deprecation** (removed in 16).

## Usage

Scaffold a new app (defaults: TypeScript, ESLint, Tailwind, App Router, Turbopack, `@/*` alias):

```bash
npx create-next-app@15 my-app --yes   # pin major 15 for a 15.x project
cd my-app
npm run dev                            # http://localhost:3000
```

Common workflows, by reference:

- **New route or component** — file conventions and structure in [01-app-router](references/01-app-router.md).
- **Components and data fetching** — Server vs Client Components, streaming, `use` hook in [02-server-client-components](references/02-server-client-components.md).
- **Mutations and forms** — Server Actions, `useActionState`, `<Form>`, revalidation, redirects in [03-server-actions](references/03-server-actions.md).
- **Caching and revalidation** — the four caches, fetch options, route segment config, draft mode, PPR, experimental Cache Components in [04-caching](references/04-caching.md).
- **APIs and request interception** — Route Handlers and middleware in [05-route-handlers-middleware](references/05-route-handlers-middleware.md).
- **SEO and sharing** — metadata, `generateMetadata`, OG images, robots, sitemap in [06-metadata-og](references/06-metadata-og.md).
- **Images, fonts, CSS** — `next/image`, `next/font`, styling conventions in [07-assets](references/07-assets.md).
- **Legacy `pages/` projects** — data fetching methods and API routes in [08-pages-router](references/08-pages-router.md).
- **Upgrading to 15 or migrating routers** — breaking changes, codemods, migration steps in [09-migration-upgrading](references/09-migration-upgrading.md).
- **Build, deploy, diagnose** — CLI commands, `next.config`, environment variables in [10-cli-config](references/10-cli-config.md).

Decision guidance when touching an existing project:

- Check the `next` version in `package.json` first. This skill is pinned to 15.5.25; a project on 14 or 16 needs its own docs as the source of truth (15→16 is a major rework, not a drop-in — sync request APIs were removed, `middleware` was renamed to `proxy`, Turbopack became the default).
- In App Router code, always `await params`/`searchParams` and treat `cookies()`/`headers()` as async, even though 15 tolerates sync access.
- Verify what a route actually renders (static vs dynamic) via the `next build` output table (`○` static, `ƒ` dynamic) rather than assuming from the code.

## Gotchas

- **`params` and `searchParams` are Promises in the App Router.** `const { slug } = params` is a 14-era bug; use `const { slug } = await params` in Server Components, or `use(params)` in Client Components. Sync access still works in 15 but is deprecated and errors in 16.
- **`fetch` is uncached by default since 15.** A `fetch` in a Server Component or Route Handler with no `cache` option hits the source on every request in a dynamic route, and the route itself becomes dynamic. Cache explicitly with `{ cache: 'force-cache', next: { revalidate: 3600 } }`, or flip the whole segment with `export const fetchCache = 'default-cache'`.
- **Conflicting fetch options are silently ignored.** `{ revalidate: 3600, cache: 'no-store' }` on one request means *neither* is applied, with a warning in dev. Pick one semantics per request.
- **Pages are never cached in development.** `next dev` always renders on demand, and the HMR fetch cache (`serverComponentsHmrCache`) can serve stale data between edits. Don't debug caching behavior against the dev server — run `next build && next start`.
- **Route Handlers have no cache by default; only `GET` can opt in.** `export const dynamic = 'force-static'` (or `revalidate`) applies to `GET` only; other verbs are always dynamic.
- **`route.ts` and `page.ts` cannot share a directory.** Each file claims every HTTP verb for its path; put APIs under `app/api/...` or a sibling folder. Route Handlers also skip layouts and client-side navigation.
- **`useSearchParams` requires a `<Suspense>` boundary** in a statically rendered route, or the whole component tree above the boundary is force-rendered on the client. Wrap the component that reads search params, not the whole page.
- **`redirect()` throws.** Code after `redirect(...)` in a Server Action never runs; call `revalidatePath`/`revalidateTag` *before* it.
- **`useFormState` is deprecated** — React 19 renamed it to `useActionState` (also gains a `pending` property). Use the new name in new code.
- **Middleware fetches are never cached** — `cache`, `next.revalidate`, and `next.tags` options have no effect inside middleware. Also avoid slow data fetching and session management there; only one `middleware.ts` per project is allowed. (Since 15.5 middleware can run on the Node.js runtime via `config.runtime = 'nodejs'`, but it stays on the hot path.)
- **`revalidate` values must be statically analyzable.** `revalidate = 60 * 10` is invalid; write `revalidate = 600`. The lowest `revalidate` across a route's layouts and pages wins for the whole route.
- **Root layout is mandatory** — `app/layout.tsx` must contain the `<html>` and `<body>` tags. `next dev` auto-creates it if missing, but builds expect it.
- **Parallel routes need a `default.js` fallback** in every `@slot` folder without a matching route, or the build fails.
- **Partial Prerendering requires both a config flag and a segment export** — `experimental.ppr: 'incremental'` in config plus `export const experimental_ppr = true` on a route segment; without both, PPR does nothing.
- **The `use cache` directive is a no-op without its flag** — enable `experimental.useCache: true` or `experimental.cacheComponents: true`; with `cacheComponents` on, route segment config exports are disabled and data fetching is runtime by default unless marked `'use cache'`.
- **`next lint` is deprecated in 15.5** (removed in 16) — prefer calling ESLint (or Biome) directly; `next build` still lints unless `--no-lint`.
- **`@next/font` is gone** — the package was removed in 15; import from `next/font/google` and `next/font/local`.
- **`NextRequest.geo` and `.ip` were removed in 15** — the hosting provider supplies those; on Vercel use `@vercel/functions`.
- **Client router cache no longer reuses page segments in 15.** State and effects in page components re-run on `<Link>` navigation (layouts and `loading` states are still reused). If old code depended on pages sticking around, that assumption is now wrong.
- **In `pages/` router, `getStaticProps` props are public** — everything returned from `getStaticProps` ships to the client for hydration. Keep secrets server-side.
- **`output: 'export'` disables SSR, API routes, and dynamic rendering** — all routes must be statically renderable; dynamic routes need complete `generateStaticParams` (or `getStaticPaths` in Pages Router).

## References

- [01-app-router](references/01-app-router.md) — file conventions, route groups, dynamic segments, `generateStaticParams`, parallel and intercepting routes, navigation
- [02-server-client-components](references/02-server-client-components.md) — RSC model, `use client`, data fetching on each side, streaming, third-party libraries, env hygiene
- [03-server-actions](references/03-server-actions.md) — `'use server'`, forms, `useActionState`, `<Form>`, `useOptimistic`, revalidation, redirects, client navigation hooks
- [04-caching](references/04-caching.md) — static vs dynamic rendering, the four caches, fetch options, route segment config, draft mode, PPR, experimental Cache Components (`use cache`, `cacheLife`, `cacheTag`, `connection`), static export
- [05-route-handlers-middleware](references/05-route-handlers-middleware.md) — Route Handlers, middleware (Edge and Node.js runtime), matchers, config-based redirects/rewrites/headers
- [06-metadata-og](references/06-metadata-og.md) — `metadata`/`generateMetadata`, viewport, file conventions for icons and OG images, `imageResponse`
- [07-assets](references/07-assets.md) — `next/image`, `next/font`, CSS, public folder
- [08-pages-router](references/08-pages-router.md) — `pages/` routing, `_app`/`_document`, `getStaticProps`/`getServerSideProps`, API routes, preview mode
- [09-migration-upgrading](references/09-migration-upgrading.md) — 14→15 breaking changes and codemods, Pages→App migration, from Vite/CRA
- [10-cli-config](references/10-cli-config.md) — `create-next-app` and `next` CLI, `next.config` options, environment variables

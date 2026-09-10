---
name: next
description: Develops Next.js 16 (App Router) applications using the 16.3.4 docs as the source of truth. Use when creating or editing Next.js projects — new apps via create-next-app, App Router pages and layouts, server and client components, Cache Components caching (use cache, cacheLife, cacheTag, revalidateTag, updateTag), proxy and route handlers, or upgrading from version 15 to 16. Covers breaking changes, codemods, and AI agent verification workflows.
license: MIT
compatibility: Node.js 20.9+ (Node 18 unsupported); TypeScript 5.1+; Turbopack is the default bundler; bundled docs at node_modules/next/dist/docs/ on 16.2+
metadata:
  tags:
    - web
    - frontend
    - react
    - framework
---

# next

## Overview

Next.js 16 is a React framework for full-stack web apps, built around the App Router, React Server Components, and Turbopack. This skill targets version 16.3.4 and the App Router.

Version 16 is a major rework, not a patch-level change. The four pillars to internalize before touching any 16.x codebase:

1. **Turbopack is the default** bundler for `next dev` and `next build`; Webpack is opt-out.
2. **All Request APIs are async only** — `params`, `searchParams`, `cookies()`, `headers()`, `draftMode()` are Promises; the sync compatibility from 15 is gone.
3. **`middleware` is deprecated and renamed to `proxy`** (Node.js runtime only; `edge` stays on the old name).
4. **Cache Components** (`cacheComponents: true`) is the new caching model — Partial Prerendering is its default behavior, `use cache` + `cacheLife` replace route segment configs and `unstable_cache`, and data fetching is dynamic by default.

Next.js 16.x ships version-matched docs inside the `next` package at `node_modules/next/dist/docs/` (since 16.2). In any 16.x project, treat those docs as the source of truth — the API surface may differ from your training data. Read the relevant guide there before writing code.

## Usage

Scaffold a new app:

```bash
npx create-next-app@latest my-app --yes   # TypeScript, ESLint, Tailwind, App Router, Turbopack, AGENTS.md
cd my-app
npm run dev                               # http://localhost:3000
```

Common workflows, by reference:

- **Upgrade 15 to 16** — `npx @next/codemod@latest upgrade latest`, then work through [01-upgrade-to-v16](references/01-upgrade-to-v16.md).
- **New route or component** — follow the structure and file conventions in [02-app-router](references/02-app-router.md) and [03-server-client-data](references/03-server-client-data.md).
- **Caching and revalidation** — decide first whether the project uses `cacheComponents`; the two models are not interchangeable. See [04-caching](references/04-caching.md).
- **Auth, redirects, request interception** — prefer `next.config` redirects first, then `proxy.ts` in [05-proxy-route-handlers](references/05-proxy-route-handlers.md).
- **Build, typecheck, diagnose** — CLI commands and config options in [06-cli-config](references/06-cli-config.md).
- **Verify changes as an agent** — the `next dev` + MCP + browser loop and official Next.js skills in [07-agent-workflows](references/07-agent-workflows.md).
- **Images, fonts, CSS, metadata** — v16 image security changes and asset conventions in [08-assets-media](references/08-assets-media.md).

Before editing an existing Next.js 16 project, read its `AGENTS.md` if present — it points at the version-matched docs for that exact install.

## Gotchas

- **This is NOT the Next.js you know.** 16 changed APIs, conventions, and file structure. Do not rely on training-data patterns; read the bundled docs in `node_modules/next/dist/docs/` (resolve the path from the `AGENTS.md` managed block) before writing code.
- **Request APIs are Promises now.** `const { slug } = params` at a page top is a 15-era bug; it must be `await params`. Same for `searchParams`, `cookies()`, `headers()`, `draftMode()`. Run `npx @next/codemod@latest next-async-request-api .` on legacy code.
- **Turbopack by default, and it guards you.** A project with a custom `webpack` config will **fail** `next build` to prevent silent misconfiguration. Use `--webpack` to opt out, `--turbopack` to force Turbopack and ignore the webpack config, or migrate the config. Drop the now-unneeded `--turbopack` from package.json scripts.
- **`middleware.ts` is deprecated — rename to `proxy.ts`.** The export function must be named `proxy` (default export still works). `proxy` runs on the Node.js runtime only and the `runtime` option cannot be set; if you need the `edge` runtime, keep using `middleware`. Config flags follow the rename (e.g., `skipProxyUrlNormalize`).
- **`revalidateTag` now requires a second argument** — a `cacheLife` profile (e.g., `revalidateTag('posts', 'max')`). The single-argument form is deprecated and is a TypeScript error. For read-your-writes from a Server Action, use `updateTag` instead.
- **`cacheComponents` invalidates the old caching configs.** Once enabled, `dynamic`, `revalidate`, and `fetchCache` route segment exports error, and `dynamicParams` fails the build. Everything is dynamic by default; opt *in* to caching per function/component with `use cache`.
- **Under Cache Components, `generateStaticParams` must return at least one param** — an empty array errors (it previously meant "render everything at runtime"). Await `params` inside a `<Suspense>` boundary if you want the static shell, not at the top of the component.
- **Parallel route slots require an explicit `default.js`** in 16 — builds fail without them. Add one that calls `notFound()` or returns `null`.
- **`next lint` is removed.** Run ESLint (flat config is the default for `@next/eslint-plugin-next`) or Biome directly; `next build` no longer lints. The `eslint` key in next.config is gone.
- **`next/image` got stricter.** Local image sources with query strings (`/img/x?v=1`) now require `images.localPatterns.search`. Defaults changed: `minimumCacheTTL` 60s → 4h, `imageSizes` no longer includes 16, `qualities` is `[75]`, `maximumRedirects` 3, and local-IP optimization is blocked unless `dangerouslyAllowLocalIP`.
- **Build output no longer shows `size` / `First Load JS`** — the metrics were removed as unreliable under RSC. Measure with Lighthouse or Vercel Analytics instead.
- **`process.argv` no longer contains `'dev'` during `next dev`** — the config is loaded once now, not twice. Check `NODE_ENV` or the `phase` instead.
- **Node.js 20.9+ is the minimum** (18 is unsupported), TypeScript 5.1+, React 19.2 is bundled for the App Router.
- **UI state survives navigation under Cache Components.** Next.js keeps hidden routes mounted via React `<Activity>`; code that relied on unmount to reset dropdowns, dialogs, or forms needs explicit reset logic.
- **`next dev` and `next build` can run concurrently** (dev outputs to `.next/dev`), but a lockfile blocks two dev or two build instances on the same project — a second `next dev` prints the running server's URL and PID.

## References

- [01-upgrade-to-v16](references/01-upgrade-to-v16.md) — version 15 → 16 migration; codemods, breaking changes, removed features
- [02-app-router](references/02-app-router.md) — project structure, file conventions, layouts and pages, dynamic routes, navigation, error handling
- [03-server-client-data](references/03-server-client-data.md) — server and client components, data fetching, mutations, Server Actions
- [04-caching](references/04-caching.md) — Cache Components; use cache, cacheLife, cacheTag, revalidation, static shell, adoption workflow
- [05-proxy-route-handlers](references/05-proxy-route-handlers.md) — proxy.ts (middleware replacement), matchers, route handlers, redirects and rewrites
- [06-cli-config](references/06-cli-config.md) — next CLI commands and options, next.config.ts, Turbopack options, environment variables, typegen
- [07-agent-workflows](references/07-agent-workflows.md) — AGENTS.md, bundled docs, MCP server, dev loop, official Next.js skills, error-driven fixes
- [08-assets-media](references/08-assets-media.md) — next/image (v16 security changes), fonts, CSS, metadata and OpenGraph images

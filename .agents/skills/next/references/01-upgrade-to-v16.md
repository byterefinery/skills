# Upgrade to Next.js 16

Source of truth for migrating an app from Next.js 15 to 16, plus the manual steps the codemod cannot make. Distilled from the official [Version 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16) (v16.3.4 docs).

## Contents

- [Upgrade path](#upgrade-path)
- [Codemods](#codemods)
- [Runtime requirements](#runtime-requirements)
- [Turbopack by default](#turbopack-by-default)
- [Async Request APIs](#async-request-apis)
- [Caching APIs](#caching-apis)
- [Partial Prerendering](#partial-prerendering)
- [middleware to proxy](#middleware-to-proxy)
- [next/image changes](#nextimage-changes)
- [Routing, navigation, and rendering](#routing-navigation-and-rendering)
- [Removed features](#removed-features)
- [Other changes](#other-changes)
- [Verification](#verification)

## Upgrade path

Prefer the codemod — it handles the mechanical migrations (config, proxy rename, `unstable_` removal, `experimental_ppr` removal) and the package bump:

```bash
npx @next/codemod@latest upgrade latest   # or pnpm dlx / yarn dlx / bunx
```

It auto-runs non-interactively when stdin is not a TTY (CI, agents). If the app used sync `params`/`searchParams`/`cookies()`/`headers()`/`draftMode()` during the 15 compatibility period, also run:

```bash
npx @next/codemod@latest next-async-request-api .
```

Manual alternative: `npm install next@latest react@latest react-dom@latest` (plus latest `@types/react` and `@types/react-dom` for TypeScript), then work through the breaking changes below.

The codemod is *not* the whole job: it does not run every migration, and runtime behavior (async APIs, cache configs, image patterns) still needs review. Inspect the diff, run dev and build, and fix the remainder by hand.

## Codemods

| Codemod | Command |
| --- | --- |
| Upgrade everything (16.0) | `npx @next/codemod@latest upgrade latest` |
| Async Request APIs (15.0) | `npx @next/codemod@latest next-async-request-api .` |
| middleware to proxy (16.0) | `npx @next/codemod@latest middleware-to-proxy .` |
| next lint to ESLint CLI (16.0) | `npx @next/codemod@latest next-lint-to-eslint-cli .` |
| Remove `unstable_` prefix (16.0) | `npx @next/codemod@latest remove-unstable-prefix .` |
| Remove `experimental_ppr` segment config (16.0) | `npx @next/codemod@latest remove-experimental-ppr .` |
| Opt every route out of Cache Components validation (16.3) | `npx @next/codemod@canary cache-components-instant-false ./app` |
| Remove `prefetch = 'partial'` after enabling Partial Prefetching (16.3) | `npx @next/codemod@canary remove-partial-prefetch ./app` |

Run from the project root. `--dry` previews without editing. `cache-components-instant-false` takes `./app` (or `./src/app`) and reports `0 ok` instead of failing on a wrong path — check the file count. There is also a `next upgrade` CLI command (`next upgrade --revision <version>`) added in 16.1.

## Runtime requirements

- **Node.js 20.9+** — 18 is no longer supported.
- **TypeScript 5.1+** minimum.
- Browsers: Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+.

## Turbopack by default

Turbopack is stable and the default bundler for `next dev` and `next build`.

- Remove `--turbopack` from package.json scripts — it is redundant.
- A project with a custom `webpack` config **fails `next build`** to prevent silent misconfiguration. Options: build with `next build --turbopack` (ignore webpack config), migrate the config to Turbopack, or opt out with `next build --webpack`. Plugins that inject a `webpack` option are a common surprise cause.
- `experimental.turbopack` config moves to a top-level `turbopack` key in `next.config.ts`. New options include advanced webpack loader conditions and `debugIds`.
- Webpack `resolve.fallback` is replaced by `turbopack.resolveAlias` (e.g., map `fs` to an empty module for the browser). Prefer refactoring imports so client code never touches Node.js native modules.
- Sass: no tilde (`~`) prefix in `@import` under Turbopack (`@import 'bootstrap/...'`, not `'~bootstrap/...'`). `resolveAlias: { '~*': '*' }` is the escape hatch. `sass-loader` v16 enables the modern Sass API.
- Turbopack filesystem caching (compiler artifacts on disk) is on by default for both dev and build; configure via `turbopackFileSystemCache`.

## Async Request APIs

Synchronous access is **fully removed**. These can only be accessed asynchronously:

- `cookies()`, `headers()`, `draftMode()` from `next/headers`.
- `params` in `layout`, `page`, `route`, `default`, `opengraph-image`, `twitter-image`, `icon`, `apple-icon`.
- `searchParams` in `page`.

```tsx
// Next.js 16 — params and searchParams are Promises
export default async function Page({ params, searchParams }: PageProps<'/blog/[slug]'>) {
  const { slug } = await params
  const query = await searchParams
  return <h1>Blog Post: {slug}</h1>
}
```

`npx next typegen` generates the global `PageProps`, `LayoutProps`, and `RouteContext` type helpers for type-safe migration (typegen has existed since 15.5; the helpers were motivated by this change).

**Image generation functions** (`opengraph-image`, `twitter-image`, `icon`, `apple-icon`) now receive `params` and `id` as Promises — the default export must be `async` and `await` both. `generateImageMetadata` still receives sync `params`. The **`sitemap`** generation function receives `id` as a Promise too.

## Caching APIs

- **`revalidateTag` requires a second argument** — a `cacheLife` profile, e.g., `revalidateTag('posts', 'max')`. The single-argument form is deprecated and errors in TypeScript.
- **`updateTag`** (new) — Server Actions only. Expires and immediately refreshes the tagged cache within the same request (read-your-writes). Use after mutations the user must see instantly.
- **`refresh`** (new) — from a Server Action, refreshes the client router after the action completes.
- **`cacheLife` and `cacheTag` are stable** — drop the `unstable_` import aliases (`import { cacheLife, cacheTag } from 'next/cache'`).

Choose by semantics: `updateTag` for "user must see their change now" (forms, settings); `revalidateTag` with `'max'` for stale-while-revalidate (content where a short delay is fine); `revalidatePath` remains for path-based invalidation.

## Partial Prerendering

The experimental PPR flag and config are **removed**: `experimental.ppr` and the `experimental_ppr` route segment config no longer exist. PPR is now the default behavior of **Cache Components** — opt in with the top-level `cacheComponents: true` config. 16's PPR works differently from the 15 canaries; if you used the 15 experimental PPR, follow the [Migrating to Cache Components](https://nextjs.org/docs/app/guides/migrating-to-cache-components) guide (see [04-caching](04-caching.md)).

## middleware to proxy

The `middleware` file convention is deprecated and renamed to **`proxy`** (file `proxy.ts`/`proxy.js` at project root or in `src`, next to `app`/`pages`).

- Rename the file and the named export: `export function proxy(request)`. Default export still works, but the function name should become `proxy`.
- The `proxy` runtime is **`nodejs` and cannot be configured** — the `edge` runtime is not supported in proxy. If you need `edge`, keep using `middleware`.
- Config flags rename with the feature: `skipMiddlewareUrlNormalize` → `skipProxyUrlNormalize`.
- Codemod: `npx @next/codemod@latest middleware-to-proxy .`

See [05-proxy-route-handlers](05-proxy-route-handlers.md) for the full proxy API.

## next/image changes

All of the following are breaking:

| Change | Fix |
| --- | --- |
| Local image sources with query strings (`/assets/p?v=1`) now blocked to prevent enumeration attacks | Add `images.localPatterns: [{ pathname: '/assets/**', search: '?v=1' }]` |
| `images.minimumCacheTTL` default 60s → **4 hours** | Set `minimumCacheTTL: 60` to restore old behavior |
| `16` removed from default `images.imageSizes` | Add `imageSizes: [16, 32, 48, ...]` if you serve 16px images |
| `images.qualities` default now **`[75]`** only (other qualities coerced to closest) | Set `qualities: [50, 75, 100]` for multiple levels |
| Local IP optimization blocked by default (SSRF protection) | `images.dangerouslyAllowLocalIP: true` only for private networks with split-horizon DNS |
| `images.maximumRedirects` unlimited → **3** | Set `maximumRedirects: 0` or higher explicitly |

Deprecated: `next/legacy/image` (use `next/image`) and `images.domains` (use `images.remotePatterns`).

## Routing, navigation, and rendering

- **Enhanced routing** — layout deduplication and incremental prefetching make transitions leaner. No code changes; expect more, smaller prefetch requests.
- **Concurrent `next dev` and `next build`** — dev now outputs to `.next/dev` instead of `.next`; a lockfile prevents two dev or two build instances on the same project.
- **Parallel routes require `default.js`** in every slot — builds fail without them. Add one that calls `notFound()` or returns `null`.
- **`scroll-behavior` override removed** — Next.js no longer forces `scroll-behavior: auto` during navigation. If you want the old override, add `data-scroll-behavior="smooth"` to `<html>`.
- **ESLint Flat Config** — `@next/eslint-plugin-next` defaults to flat config (ESLint v10 drops legacy `.eslintrc`); migrate if you use the legacy format.
- **React 19.2** — the App Router uses React 19.2 canary: View Transitions, `useEffectEvent`, `Activity`.
- **React Compiler stable** — `reactCompiler: true` in next.config (not default) plus `babel-plugin-react-compiler` as a dev dependency. Expect higher compile times.
- **Build Adapters** — first alpha of the RFC'd adapter API; `adapterPath` was promoted to a stable top-level option in 16.2.

## Removed features

Previously deprecated, now gone:

- **AMP** — `amp` config, `useAmp`, `export const config = { amp: true }`.
- **`next lint`** — use ESLint or Biome directly; `next build` no longer lints; the `eslint` config key is removed.
- **Runtime config** — `serverRuntimeConfig`/`publicRuntimeConfig` and `next/config` are out. Read `process.env` directly in Server Components; use `NEXT_PUBLIC_` prefixed vars for client access; call `connection()` before reading env if the value must be read at runtime, not bundled at build time. Use the `taint` API to keep server secrets out of Client Components.
- **`devIndicators` options** — `appIsrStatus`, `buildActivity`, `buildActivityPosition` removed (the indicator itself remains).
- **`experimental.dynamicIO` and `experimental.useCache`** — replaced by top-level `cacheComponents`. Enabling it is not a rename-only change: it can surface build errors for uncached data outside `<Suspense>`.
- **`unstable_rootParams`** — use `next/root-params`.

## Other changes

- **Build output** drops the `size` and `First Load JS` columns — removed as inaccurate under RSC. Use Lighthouse or Vercel Analytics for real route metrics.
- **Config load in dev** — `next dev` no longer loads the config file twice; `process.argv.includes('dev')` is now `false` during `next dev` (it still works for `typegen` and `build`). Use `NODE_ENV` or `phase` for dev-only side effects.

## Verification

After upgrading:

1. `npm run dev` — watch for deprecation warnings and the AGENTS.md managed block (see [07-agent-workflows](07-agent-workflows.md)).
2. `npm run build` — fix remaining breaking changes; `--debug-prerender` for prerender errors.
3. Open key interactive UI states in a browser; check the Next dev indicator plus browser and server logs.
4. If you use an agent for the upgrade, the official prompt in the upgrade guide (AI agent section) drives the codemod, the fix pass, and the runtime verification via the `next-dev-loop` skill.

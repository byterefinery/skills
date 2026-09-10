# CLI and Configuration

## create-next-app

```bash
npx create-next-app@15 my-app [options]
```

| Option | Effect |
|---|---|
| `--yes` | Use saved preferences or defaults (TS, ESLint, Tailwind, App Router, Turbopack, `@/*`) |
| `--ts` / `--js` | TypeScript (default) / JavaScript |
| `--eslint` / `--biome` / `--no-linter` | Linter choice |
| `--tailwind` | Tailwind CSS (default on) |
| `--app` | App Router (default) |
| `--api` | Route-handlers-only project |
| `--src-dir` | Code inside `src/` |
| `--turbopack` | Turbopack for dev (default on) |
| `--import-alias <alias>` | Default `@/*` |
| `--empty` | No starter UI |
| `-e/--example [name] [url]` | Bootstrap from an example (GitHub) |
| `--use-npm` / `--use-pnpm` / `--use-yarn` / `--use-bun` | Package manager |
| `--skip-install`, `--disable-git`, `--reset-preferences` | Utilities |

`--no-*` negates defaults (e.g. `--no-tailwind`).

## next CLI

`npx next [command]`. Running `next` alone is `next dev`.

- **`next dev`** — HMR dev server. `--turbopack` (or `--turbo`) for Turbopack; `-p/--port` (default 3000, env `PORT`); `-H/--hostname`; `--experimental-https` (self-signed).
- **`next build`** — production build + route table (`○` static, `ƒ` dynamic, `Size` / `First Load JS` per route, gzip-compressed). `--turbopack` (beta in 15); `-d/--debug` (shows rewrites/redirects/headers); `--profile`; `--no-lint`; `--no-mangling`; `--experimental-app-only`; `--debug-prerender`.
- **`next start`** — serve the build. `-p/--port`, `-H/--hostname`, `--keepAliveTimeout`.
- **`next info`** — system/package diagnostics for bug reports.
- **`next lint`** — **deprecated in 15, removed in 16.** Use the ESLint CLI directly.
- **`next telemetry`** — `--enable` / `--disable` (anonymous, optional).
- **`next typegen`** — generate route param types without a full build.

## next.config.js

A Node module at the project root (not JSON, not bundled into the browser). Supported formats:

- `next.config.js` — CJS default export (object or function).
- `next.config.mjs` — ESM. (`.cjs`/`.cts`/`.mts` are **not** supported.)
- `next.config.ts` — TypeScript (typed via `import type { NextConfig } from 'next'`).
- Function form gets `(phase, { defaultConfig })`; `phase` from `next/constants` (e.g. `PHASE_DEVELOPMENT_SERVER`); async is allowed since 12.1.

### Common options

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',            // or 'export' for a static site
  distDir: '.next',
  basePath: '',                    // e.g. '/app' when not at the domain root
  assetPrefix: '',
  poweredByHeader: true,
  env: {},                         // custom env vars inlined for client+server
  publicRuntimeConfig: {},         // Pages Router only (App Router: use env)
  trailingSlash: false,
  typescript: { ignoreBuildErrors: false },
  eslint: { ignoreDuringBuilds: false },
  images: { remotePatterns: [], loader: 'imgix', unoptimized: false },
  headers: async () => [],
  redirects: async () => [],
  rewrites: async () => [],        // or { beforeFiles, afterFiles, fallback }
  serverExternalPackages: [],      // keep Node deps out of the server bundle
  bundlePagesRouterDependencies: false, // Pages Router server deps bundling
  transpilePackages: [],           // packages to run through your toolchain
  logging: { fetches: { fullUrl: true } }, // dev fetch logging
  experimental: {
    ppr: 'incremental',            // Partial Prerendering (15.5)
    staleTimes: { dynamic: 30, static: 180 }, // client router cache page reuse (seconds)
    serverComponentsHmrCache: 'bypass',       // dev HMR fetch cache
    typedRoutes: true,
  },
}
module.exports = nextConfig
```

- `output: 'standalone'` — minimal `node server.js` deployment (Docker-friendly); still needs static assets copied separately.
- `webpack` — custom webpack function (App Router + Turbopack ignores it; a custom webpack config is what makes `next build` fail in 16, so migrate off it).
- `i18n` — Pages Router internationalization only; App Router uses locale route segments.
- Config is loaded once per process in 15 (no more double-load between `next dev` phases); don't branch on `process.argv` containing `'dev'`.

## Environment variables

- Loaded from `.env` (all), `.env.local` (all, gitignored), `.env.production`, `.env.development`, plus `.env.[mode].local`.
- **`NEXT_PUBLIC_`-prefixed** vars are inlined into the client bundle at build time; everything else is server-only.
- `process.env.X` in Server Components is inlined when serialized to the client — treat server env as secret unless it's `NEXT_PUBLIC_`.
- `publicRuntimeConfig` (Pages Router) is the legacy client-exposure mechanism; prefer env vars.
- Changing env vars requires a rebuild for the client (values are baked in), but server reads them fresh per process start.
- The `METADATA_BASE` env var sets the metadata base URL without a config change.

## Deployment notes

- Vercel: zero-config; framework detection handles everything, plus preview deployments per branch.
- Self-host: `next build` then `next start` behind a proxy (set `x-forwarded-host` correctly for URLs/rewrites); `output: 'standalone'` or static `output: 'export'` for containers/CDNs.
- CI caching: cache the `node_modules/.cache/next` and Turbopack caches per lockfile to speed `next build`.

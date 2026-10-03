# next.config and CLI

## Table of contents

1. [next.config file](#nextconfig-file)
2. [Turbopack configuration](#turbopack-configuration)
3. [Key options](#key-options)
4. [Images](#images)
5. [CLI](#cli)
6. [Environment variables](#environment-variables)

## next.config file

`next.config.js` (or `.ts` — supported natively, or `.mjs`/`.cjs`) at the project root (or in `src/`). Export an object or an async function (receiving `{ dev, isTurbo, ... }`):

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  /* options */
}
export default nextConfig
```

- ESM: `export default` in `.mjs` or with `"type": "module"`.
- `process.argv` during `next dev` **no longer contains `'dev'`** in 16 (config is loaded once, not twice) — check `NODE_ENV === 'development'` or the `phase` argument instead.

## Turbopack configuration

Turbopack is the default bundler for `next dev` **and** `next build` since 16. Config moved from `experimental.turbopack` to a top-level `turbopack` key:

```ts
const nextConfig: NextConfig = {
  turbopack: {
    resolveAlias: {
      fs: { browser: './empty.ts' },  // Turbopack answer to webpack resolve.fallback
      '~*': '*',                     // legacy Sass tilde imports
    },
    debugIds: true,
  },
}
```

- A custom top-level `webpack` option makes `next build` **fail on purpose** in 16. Options: build with `--turbopack` (ignore webpack config), migrate, or opt out with `next build --webpack`. Plugins that inject `webpack` are a common hidden cause.
- Opt out per script: `"build": "next build --webpack"`.
- Filesystem caching is on by default for dev and build (`turbopackFileSystemCache` config to tune/disable).

## Key options

| Option | Purpose |
|---|---|
| `cacheComponents` | Enable Cache Components (PPR model). `true` removes `dynamic`/`revalidate`/`fetchCache` segment config |
| `partialPrefetching` | Router prefetches each route's App Shell (Cache Components) |
| `reactCompiler` | Stable in 16 — automatic memoization. Needs `babel-plugin-react-compiler` as devDep. Expect slower compiles |
| `output` | `'standalone'` (self-contained server for Docker), `'export'` (static HTML/JS, no server), `'tracking'`/`'file-tracing'` (advanced) |
| `serverActions` | `{ enabled, bodySizeLimit }` — Server Actions toggle + body size |
| `images` | See below |
| `headers` / `redirects` / `rewrites` | Array of `{ source, has?, missing?, ... }` rules — use these before reaching for proxy for simple static rules |
| `redirects` | Simple redirects without code — prefer over proxy when no request data needed |
| `basePath` / `assetPrefix` | Host the app under a path / different CDN |
| `trailingSlash` | `/about/` vs `/about` (default `false`) |
| `experimental` → removed in 16 | `dynamicIO`, `useCache` gone → use `cacheComponents`; `adapterPath` promoted to top-level in 16.2 |
| `serverExternalPackages` | Packages that must stay external (CommonJS, native, large) — avoids bundling breakage |
| `transpilePackages` | Babel-transpile packages that ship ESM-only or need React transforms |
| `optimizePackageImports` | Auto tree-shake heavy packages (e.g. `date-fns`, `lodash`) |
| `pageExtensions` | Non-standard page extensions (e.g. `['jsx', 'tsx', 'mdx']`) |
| `env` / `publicRuntimeConfig` | `env` merges vars into `process.env`; **`publicRuntimeConfig`/`serverRuntimeConfig` removed in 16** — use `NEXT_PUBLIC_` env vars |
| `taint` | Mark strings as tainted to detect secrets leaking to the client |
| `distDir` | Custom build output (`.next` default); dev writes to `<distDir>/dev` in 16 |
| `compress` | Gzip responses (default `true`) |
| `poweredByHeader` | `x-powered-by` header (default `true`) |
| `logging` | Dev `fetch` logging (on by default in 16) |
| `cacheHandlers` | Durable cache store config for `use cache: remote` |
| `cacheLife` / `staleTimes` | Override built-in cacheLife profiles app-wide |
| `instrumentationClientInject` | Load `instrumentation-client.js` for the client |
| `devIndicators` | Dev tools indicator (some options removed in 16: `appIsrStatus`, `buildActivity*`) |
| `htmlLimitedBots` | Restrict which bots get the full (non-streamed) HTML |
| `mdxRs` | Enable mdx-rs for MDX files |
| `sassOptions` | Sass compiler options (modern Sass API in 16) |

## Images

v16 tightened `next/image` (defaults all changed — see upgrading guide):

| Option | Default in 16 | Notes |
|---|---|---|
| `localPatterns[].search` | none | **Required** for local image `src` with query strings (`/img?a=1`), e.g. `{ pathname: '/assets/**', search: '?v=1' }` |
| `minimumCacheTTL` | 14400 (4h, was 60s) | Revalidation floor for images lacking `cache-control` |
| `imageSizes` | `[16] removed` | Was `16,32,48,...,1920`; add 16 back if needed |
| `qualities` | `[75]` (was all) | Unknown `quality` prop coerced to nearest |
| `maximumRedirects` | 3 (was unlimited) | `0` disables |
| `dangerouslyAllowLocalIP` | `false` | Blocks local-IP optimization (SSRF guard); enable only for VPC split-horizon DNS 400s |
| `remotePatterns` | — | Replaces deprecated `domains` |

`next/legacy/image` is deprecated — use `next/image`.

## CLI

| Command | Description |
|---|---|
| `next dev` | Dev server with HMR (Turbopack default; `--webpack` to opt out). Writes to `.next/dev`. `next` alone is an alias for `dev` |
| `next build` | Production build (Turbopack default; fails if a `webpack` config exists). No lint step, no `size`/`First Load JS` metrics in 16 |
| `next start` | Serve a built app (port 3000 default; `PORT` env) |
| `next info` | System/dependency details for bug reports |
| `next telemetry` | Enable/disable anonymous telemetry |
| `next typegen [dir]` | Generate route TS types (`PageProps`, `LayoutProps`, `RouteContext`) without a full build — for CI type-checking |
| `next upgrade` | Bump `next`, `react`, `react-dom` (+ bundled docs in `node_modules/next/dist/docs/`) |
| `next experimental-analyze` | Bundle analysis via Turbopack, no artifacts |

Useful `next dev`/`next build` flags: `-p/--port`, `-H/--hostname`, `--webpack`, `--turbopack`, `--experimental-https`. Lockfiles prevent two concurrent `dev` or `build` on the same project; dev and build can now run **concurrently** (separate output dirs).

## Environment variables

| File | Purpose |
|---|---|
| `.env` | All environments (committed) |
| `.env.local` | All environments (gitignored) |
| `.env.development` / `.env.production` | Per `NODE_ENV` (gitignored: `.env.local.*`) |

- Precedence: production-specific > environment-specific > `.env.local` > `.env` (roughly; process env always wins).
- Only **`NEXT_PUBLIC_*`** vars are exposed to client code (inlined at build time).
- Reading `process.env` in Server Components works for all vars.
- `connection()` (from `next/server`) forces runtime env reads instead of build-time bundling.
- Never prefix sensitive values with `NEXT_PUBLIC_`; use `taint` to catch leaks.

# CLI and configuration

The `next` CLI in v16 and the `next.config.ts` options that matter.

## Contents

- [CLI commands](#cli-commands)
- [v16 CLI notes](#v16-cli-notes)
- [next.config.ts](#nextconfigts)
- [Turbopack config](#turbopack-config)
- [Environment variables](#environment-variables)
- [TypeScript and typegen](#typescript-and-typegen)

## CLI commands

| Command | Purpose |
| --- | --- |
| `next dev` | Dev server with HMR (alias: bare `next`) |
| `next build` | Production build; prints the route table (○ static / ƒ dynamic) |
| `next start` | Serve a production build |
| `next info` | System/package report for bug reports (`--verbose`) |
| `next telemetry --enable\|--disable` | Anonymous telemetry toggle |
| `next typegen` | Generate route types without a full build |
| `next upgrade` | Upgrade to a new version (`--revision <version>`) |
| `next experimental-analyze` | Turbopack bundle analysis UI (no build artifacts) |

Key options:

- **dev**: `-p/--port` (default 3000, env `PORT`), `-H/--hostname`, `--webpack` (opt out of Turbopack), `--turbopack` (redundant, force), `--experimental-https` (self-signed via mkcert), `--experimental-cpu-prof`.
- **build**: `--webpack` / `--turbopack`, `-d/--debug` (show rewrites/redirects/headers), `--debug-prerender` (unminified server code, continue past first prerender failure — dev only, never deploy such builds), `--debug-build-paths="app/page.tsx,..."` (globs, `!` excludes), `--profile`, `--no-mangling`, `--experimental-build-mode [compile|generate]`.
- **start**: `-p/--port`, `--keepAliveTimeout <ms>` (set larger than your downstream proxy's timeouts, e.g., 70000 behind ELB).
- Any Node argument works: `NODE_OPTIONS='--inspect' next dev`.
- With `npm run`, pass `--` before CLI flags (`npm run dev -- --port 4000`); pnpm/yarn/bun forward directly.
- `PORT` cannot be set in `.env` — the server boots before env files load; use the shell or `-p`.

## v16 CLI notes

- **Dev output goes to `.next/dev`** (not `.next`) — `next dev` and `next build` can run concurrently.
- A **lockfile** blocks two dev or two build instances on one project; a second `next dev` prints the running server's URL and the PID to kill. Agents should reuse the running server.
- `next build` output no longer shows `size` / `First Load JS` columns.
- The Turbopack tracing command is `npx next internal trace .next-profiles/trace-turbopack.bin`.

## next.config.ts

TypeScript config is supported (`next.config.ts`, importing `type { NextConfig }`). Options most relevant in v16:

| Option | Note |
| --- | --- |
| `turbopack` | Top-level (was `experimental.turbopack`); see below |
| `cacheComponents` | Enable Cache Components / PPR (boolean) |
| `cacheLife` | Custom and redefined cache profiles for `cacheLife()` |
| `cacheHandlers` | Durable cache handlers (e.g., platform KV) for `use cache` |
| `cacheMaxMemorySize` | In-memory cache size, self-hosted |
| `staleTimes` | Override client `stale` windows |
| `partialPrefetching` | Enable Partial Prefetching (App Shell prefetching) |
| `prefetchInlining` / `prefetch` segment config | Tune link prefetching |
| `reactCompiler` | Enable React Compiler (install `babel-plugin-react-compiler`) |
| `typedRoutes` | Typed `href` for `next/link` and navigation |
| `output` | `standalone`, `export` (static export), `default` |
| `images` | See [08-assets-media](08-assets-media.md) |
| `redirects` / `rewrites` / `headers` | Config-level routing rules |
| `serverActions` | `{ enabled, bodySizeLimit }` |
| `experimental.adapterPath` | Build adapters (top-level `adapterPath` stable since 16.2) |
| `skipProxyUrlNormalize`, `skipTrailingSlashRedirect` | Proxy advanced flags |
| `taint` / `experimental.taint` | Taint server values so they cannot leak into Client Components |
| `agentRules` | `false` opts out of the auto-generated AGENTS.md/CLAUDE.md managed block (16.3+) |
| `logging` | e.g., `browserToTerminal` forwards browser console to the terminal |
| `distDir` | Default `.next`; dev uses `<distDir>/dev` |
| `poweredByHeader`, `compress`, `trailingSlash`, `basePath`, `assetPrefix` | Standard server behavior |

Gotchas:

- `experimental.dynamicIO` / `experimental.useCache` are removed (use `cacheComponents`); `dynamicIO` aborts before any build.
- `experimental.ppr` and the `experimental_ppr` segment config are removed.
- The `eslint` key is removed — configure ESLint/Biome directly.
- `serverRuntimeConfig` / `publicRuntimeConfig` are removed — use env vars.
- Under `next dev`, `process.argv` no longer contains `'dev'`; use `NODE_ENV === 'development'` or the config `phase`.

## Turbopack config

```ts
const nextConfig: NextConfig = {
  turbopack: {
    resolveAlias: {
      fs: { browser: './empty.ts' },   // replaces webpack resolve.fallback
      '~*': '*',                        // legacy tilde sass imports
    },
  },
}
```

- `resolveAlias` — per-target (browser/node) module aliases.
- `debugIds` — stable IDs across dev and build (better stack traces).
- `turbopackFileSystemCache` (config key) — filesystem caching of compiler artifacts, on by default for dev and build; disable or configure the directory there.
- `turbopackIgnoreIssue`, `turbopackChunking`, `turbopackMemoryEviction`, `useLightningcss` — tuning.
- A custom `webpack` config + `next build` **fails** by design (Turbopack is default): migrate, or pass `--webpack` / `--turbopack`.

## Environment variables

- Files: `.env`, `.env.local` (gitignored), `.env.production`, `.env.development` (and `.env.[mode].local`). Load order and `.env.local` precedence follow Node conventions; `process.env` set in your shell wins.
- **`NEXT_PUBLIC_` prefix** is the only way a variable reaches client code — it is inlined at build time.
- Server components may read any server variable via `process.env`.
- To read a variable **at runtime** (not bundled at build), `await connection()` from `next/server` before reading it.
- Keep secrets server-side; use `taint` to fail loudly if a tainted value flows toward a Client Component.

## TypeScript and typegen

- `next typegen` writes route types to `<distDir>/types` (`.next/dev/types` in dev, `.next/types` in prod) and generates `next-env.d.ts` — run it before `tsc --noEmit` in CI instead of booting a build.
- Global helper types: `PageProps<'/blog/[slug]'>`, `LayoutProps<...>`, `RouteContext<...>` — generated for the async `params`/`searchParams` migration.
- `next-env.d.ts` should be gitignored.
- The `cacheLife` function's types are generated from your `next.config.ts` profile definitions, so autocomplete reflects your custom profiles.

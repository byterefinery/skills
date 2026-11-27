# Setup and integrations

All packages are version-locked to 4.3.5 in the monorepo.

## Vite — @tailwindcss/vite

Register the plugin; Tailwind takes over any CSS file that uses Tailwind features (it returns `false` for plain CSS, so non-Tailwind files pass through untouched).

```ts
// vite.config.ts (playgrounds/vite from the repo)
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

```css
/* src/index.css */
@import 'tailwindcss';
```

Plugin options (`PluginOptions`):

```ts
export type PluginOptions = {
  /** Optimize and minify the output CSS. */
  optimize?: boolean | { minify?: boolean }
}
```

Defaults: CSS is optimized during builds (minification also follows Vite's `build.cssMinify`). Override with `tailwindcss({ optimize: false })` or `tailwindcss({ optimize: { minify: false } })`. The plugin runs in both serve and build modes; scanned files are registered as watch dependencies.

## PostCSS — @tailwindcss/postcss

```js
// postcss.config.js (playgrounds/nextjs from the repo)
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

## CLI — @tailwindcss/cli

The bin is named `tailwindcss`. Two commands — `build` (default) and `canonicalize` (canonicalize a candidate list, e.g. collapse `text-foreground text-primary` to `text-primary`):

```
tailwindcss [--input input.css] [--output output.css] [--watch] [--poll=ms] [options…]
tailwindcss build
tailwindcss canonicalize
```

Build options:

- `--input` / `-i` — input file
- `--output` / `-o` — output file (default `-` = stdout)
- `--watch` / `-w` — watch and rebuild; value `always` keeps watching when stdin is closed
- `--poll` — poll instead of filesystem events (optional `ms` value)
- `--minify` / `-m` — optimize and minify
- `--optimize` — optimize without minifying
- `--cwd` — working directory (default `.`)
- `--map` — generate a source map
- `--silent` — suppress non-error output

## Turbopack — @tailwindcss/turbopack

Turbopack loader for using Tailwind CSS with Next.js (added in 4.3.4). Note the 4.3.5 changelog explicitly removes `as: '*.css'` from its documented setup because it breaks CSS modules.

## Webpack — @tailwindcss/webpack

Webpack integration package (rebuilds when the input CSS changes — fixed in 4.3.4).

## Browser — @tailwindcss/browser

In-browser compiler, no build step. The published entry is a global script (`dist/index.global.js`). Behavior from the source:

- Collects every `<style type="text/tailwindcss">…</style>` tag on the page and concatenates them as the input CSS.
- If none of the collected sheets contain an `@import`, it prepends `@import "tailwindcss";` automatically — otherwise your imports control the build.
- Resolves the virtual sheets `tailwindcss`, `tailwindcss/preflight`, `tailwindcss/theme`, `tailwindcss/utilities` from bundled assets, and reloads everything when a `text/tailwindcss` stylesheet changes.
- Classes are tracked incrementally; only new candidates are compiled.

## Upgrading from v3 — @tailwindcss/upgrade

```bash
npx @tailwindcss/upgrade
```

- Requires a clean git tree (stash/commit first) unless you pass `--force` / `-f`.
- Fails on a version mismatch between the installed `tailwindcss` and the expected v4 release — reinstall and retry.
- Options: `--config` / `-c` (path to the configuration file), `--version` / `-v`.
- Migrations: JS config files, PostCSS configs, stylesheets (analysis → linking → migration → splitting → sorting), and template codemods.

## Package entry points (tailwindcss)

`package.json` exports (same shape for dev source and published builds):

- `.` — the compiler API (Node) / `index.css` via the `style` condition (bundler)
- `./index.css`, `./preflight.css`, `./theme.css`, `./utilities.css` (also resolvable without the `.css` suffix)
- `./plugin` — the `plugin()` helper for JS plugins (v3-compatible API)
- `./colors`, `./defaultTheme`, `./lib/util/flattenColorPalette` — v3 compatibility exports
## Next.js

### App Router

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: {
      rules: {
        '*.css': {
          loaders: ['@tailwindcss/webpack'],
        },
      },
    },
  },
}
module.exports = nextConfig
```

### CSS Entry

```css
/* app/globals.css */
@import "tailwindcss";
```

## Performance

- v4 uses a Rust engine for significantly faster builds
- No JIT compilation step — utilities are generated on-demand during CSS parsing
- Incremental builds are faster with file watchers
- Use `@source` to limit content scanning to relevant directories

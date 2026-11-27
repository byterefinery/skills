# Migrating to Vue Router 5

Vue Router 5 is a transition release that merges [unplugin-vue-router](https://uvr.esm.is) (file-based routing) into the core package.

## From Vue Router 4 (without file-based routing)

**No breaking changes** — you can upgrade without any code modifications:

```bash
pnpm update vue-router@5
```

The only exception: the **iife build no longer bundles `@vue/devtools-api`** — devtools v8 does not expose an IIFE build itself, so a browser build without a bundler that relied on devtools must import it explicitly.

Road ahead: **Vue Router 6 will be ESM-only and will remove deprecated APIs** (including `next` in navigation guards). v5 is the preparation window — migrate off deprecated APIs now.

## From unplugin-vue-router

If you were using unplugin-vue-router for file-based routing, the migration is mostly import path changes.

### 1. Update dependencies

```bash
pnpm remove unplugin-vue-router
pnpm update vue-router@5
```

### 2. Update imports

**Vite plugin:**

```ts
import VueRouter from 'unplugin-vue-router/vite' // old
import VueRouter from 'vue-router/vite'          // new
```

Other build tools import from `vue-router/unplugin`:

```ts
import VueRouter from 'vue-router/unplugin'
VueRouter.webpack({ /* ... */ })
VueRouter.rollup({ /* ... */ })
// etc.
```

**Data loaders:**

```ts
// old
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic'
import { defineColadaLoader } from 'unplugin-vue-router/data-loaders/pinia-colada'
import { DataLoaderPlugin } from 'unplugin-vue-router/data-loaders'

// new
import { defineBasicLoader, DataLoaderPlugin } from 'vue-router/experimental'
import { defineColadaLoader } from 'vue-router/experimental/pinia-colada'
```

**Unplugin utilities (for custom integrations) and types:**

```ts
import {
  VueRouterAutoImports,
  EditableTreeNode,
  createTreeNodeValue,
  createRoutesContext,
  getFileBasedRouteName,
  getPascalCaseRouteName,
} from 'vue-router/unplugin'

import type { Options, EditableTreeNode } from 'vue-router/unplugin'
```

**Volar plugins** (`tsconfig.json`):

```jsonc
{
  "vueCompilerOptions": {
    "plugins": [
      "vue-router/volar/sfc-typed-router",  // was "unplugin-vue-router/volar/sfc-typed-router"
      "vue-router/volar/sfc-route-blocks"   // was "unplugin-vue-router/volar/sfc-route-blocks"
    ]
  }
}
```

### 3. Update `vite.config.ts` and `tsconfig.json`

It is recommended to move the generated types file inside `src/` and rename it to `route-map.d.ts`, as it is automatically included by most setups:

```ts
// vite.config.ts
export default defineConfig({
  plugins: [
    VueRouter({
      dts: 'src/route-map.d.ts',
    }),
  ],
})
```

Remove the old client types reference — the `unplugin-vue-router/client` triple-slash reference (commonly in `env.d.ts`) and/or the `unplugin-vue-router/client` entry in `tsconfig.json` `include`.

### Troubleshooting

- **Types not recognized** — restart your TypeScript server and check that your generated types file (e.g., `src/route-map.d.ts`) is included in your tsconfig.
- **Routes not generating** — verify your `routesFolder` path and check file extensions.
- **Route name errors** — use the generated names or add `definePage({ name: 'custom-name' })` to your components.

## New exports reference

| Export | Purpose |
|---|---|
| `vue-router` | Main API (unchanged) |
| `vue-router/vite` | Vite plugin |
| `vue-router/auto-routes` | Generated routes |
| `vue-router/unplugin` | Webpack/Rollup/esbuild + utilities |
| `vue-router/experimental` | Data loaders, experimental router, param parsers, scroll restoration |
| `vue-router/experimental/pinia-colada` | Pinia Colada loader |

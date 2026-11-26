# File-Based Routing (core since v5)

Vue Router 5 includes the file-based routing plugin in core — routes and types are generated from page components. No more manual `routes` array.

## Setup

```ts
// vite.config.ts
import VueRouter from 'vue-router/vite'

export default defineConfig({
  plugins: [
    VueRouter({
      dts: 'src/route-map.d.ts', // generated types file
    }),
    // ⚠️ Vue must be placed after VueRouter()
    Vue(),
  ],
})
```

Other bundlers import from `vue-router/unplugin/rollup`, `vue-router/unplugin/webpack`, `vue-router/unplugin/esbuild`.

Start the dev server once to generate the types file; add it to `tsconfig.json` `include` (and set `"moduleResolution": "Bundler"`). The file is meant to be committed.

Create the router from the generated routes:

```ts
import { routes } from 'vue-router/auto-routes'

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
```

## File conventions (default folder `src/pages`)

```text
src/pages/
├── index.vue            -> /
├── about.vue            -> /about
└── users/
    ├── index.vue        -> /users
    └── [id].vue         -> /users/:id
```

- `index.vue` (**must be all lowercase**) generates the empty path.
- `[id]` is a param; `[id]+` repeatable; `[[id]]` optional.
- A `.` in a file name becomes a `/` in the path — `users.create.vue` produces `/users/create` **without** nesting inside `users.vue`.
- A file next to a same-named folder becomes the parent layout: `users.vue` wraps `users/`'s children in its `<RouterView>`. Alternatively, name the parent `users/_parent.vue` (anonymous route; only children are navigable).
- Route groups: `(admin)/dashboard.vue` → `/dashboard` — the folder name is ignored in the URL.
- Generated routes get `name` from the file path (override with `getRouteName()`).

## Typing pages

Use `useRoute(path)` to get the typed route for a page:

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute('/users/[id]')
route.params.id  // typed
</script>
```

Pass route params to the component as typed props:

```vue
<script setup lang="ts">
defineProps<{ userId: number }>()

definePage({
  params: { path: { userId: 'number' } },
  props: true,  // passes route.params as props and types defineProps()
})
</script>
```

With the `sfc-typed-router` Volar plugin, TS checks `props` against route params and page props.

## `definePage()` macro

Configure any route option per page. The argument is **extracted at build time** — no variables, and `beforeEnter` guards are not supported (use global guards with `meta`, or add guards at runtime).

```vue
<script setup lang="ts">
definePage({
  alias: ['/n/:name'],
  meta: { requiresAuth: true },
  redirect: to => ({ path: '/users', query: to.query }),
})
</script>
```

The `<route>` SFC custom block works too (`lang="json"`/`"yaml"`; JSON5 by default):

```vue
<route lang="json">
{ "name": "name-override", "meta": { "requiresAuth": false } }
</route>
```

## Runtime route extension

Escape hatch: import `routes` from `vue-router/auto-routes`, clone/modify the array, then pass it to `createRouter()`. Runtime changes are not reflected in the generated types.

## Volar plugins

```jsonc
// tsconfig.json
{
  "vueCompilerOptions": {
    "plugins": [
      "vue-router/volar/sfc-typed-router",
      "vue-router/volar/sfc-route-blocks"
    ]
  }
}
```

## HMR

With `definePage()`/`<route>` blocks, HMR for routes is supported (**Vite only**) — no page or server reload needed when routes change:

```ts
import { routes, handleHotUpdate } from 'vue-router/auto-routes'

export const router = createRouter({ history: createWebHistory(), routes })

if (import.meta.hot) handleHotUpdate(router)
```

Routes added at runtime must also be re-added inside the `handleHotUpdate` callback (it only runs on updates, not on initial load — keep the regular call).

## ESLint

For ESLint, declare `definePage` as a global and use the provided rules to validate `definePage()` arguments.

## SSR

The plugin supports SSR; configure via the plugin options (see `SSR` in the docs `configuration.md`).

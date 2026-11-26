# SSR and Nuxt

## Plain SSR (no Nuxt)

Creating stores works out of the box as long as `useStore()` calls happen at the top of `setup()` functions, getters, and actions — pinia knows which app is running there.

Outside `setup()`, pass the pinia instance to `useStore(pinia)` so the correct store is used for the currently running app (e.g. inside router guards). Pinia also registers itself as `$pinia` on the app, available in `serverPrefetch()`:

```js
export default {
  serverPrefetch() {
    const store = useStore(this.$pinia)
  },
}
```

With `onServerPrefetch()` nothing special is needed:

```vue
<script setup>
const store = useStore()
onServerPrefetch(async () => {
  await store.fetchData()
})
</script>
```

## State hydration

Serialize the root state into the HTML after server rendering — read it from `pinia.state.value`. **Escape the state for security** (XSS) when the content can be user-influenced; the docs recommend [devalue](https://github.com/Rich-Harris/devalue) (what Nuxt uses). If the state round-trips through `JSON.stringify()`/`JSON.parse()`, that is a valid, faster alternative:

```js
import devalue from 'devalue'
// server side, after rendering:
devalue(pinia.state.value) // serialize + escape, embed in HTML
```

On the client, set the initial state **before any `useStore()` call**:

```ts
const pinia = createPinia()
const app = createApp(App)
app.use(pinia)

if (isClient) {
  pinia.state.value = JSON.parse(window.__pinia)
}
```

Note: SSR hydration of reactive Set/Map state in 4.0.3+ **replaces** the value instead of unioning it.

## Nuxt

Nuxt handles serialization and XSS for you. Install the module:

```bash
npx nuxi@latest module add pinia
```

This adds `@pinia/nuxt` and `pinia`. If `pinia` itself is not installed, install it manually — and since v4 also `@vue/devtools-api`: `npm i pinia @vue/devtools-api`. Then add the module to `nuxt.config.js`:

```js
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
})
```

With npm you may hit an `ERESOLVE unable to resolve dependency tree` error; add `"overrides": { "vue": "latest" }` to `package.json`.

### Awaiting actions in pages

Use `callOnce()` to run a store action once (avoids refetching data already present):

```vue
<script setup>
const store = useStore()
await callOnce('user', () => store.fetchUser())
// run on every navigation instead (like useFetch/useAsyncData):
// await callOnce('user', () => store.fetchUser(), { mode: 'navigation' })
</script>
```

Outside `setup()` (guards, other stores, middlewares), remember to pass the pinia instance to `useStore(pinia)`.

### Auto imports

`@pinia/nuxt` auto-imports: `usePinia()` (better than `getActivePinia()` in Nuxt), `defineStore()`, `storeToRefs()`, `acceptHMRUpdate()`, and **all stores** in the `stores` folder (`app/stores` in Nuxt 4; nested folders are not looked up). Customize with the `storesDirs` option:

```ts
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
  pinia: {
    storesDirs: ['./stores/**', './custom-folder/stores/**'],
  },
})
```

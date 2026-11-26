# Getting Started

## Installation

Since v4 you must install `pinia` **and** `@vue/devtools-api` — the latter is a required peer dependency used by the devtools integration:

```bash
npm install pinia @vue/devtools-api
# or
yarn add pinia @vue/devtools-api
pnpm add pinia @vue/devtools-api
bun add pinia @vue/devtools-api
deno add pinia @vue/devtools-api
```

Peer dependencies (from the published package): `vue ^3.5.11` (required), `@vue/devtools-api ^8.2.1` (required), `typescript >=5.6.0` (optional). Pinia 4 is ESM-only.

Create a pinia instance (the root store) and pass it to the app as a plugin:

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.mount('#app')
```

## What is a Store

A store is an entity holding state and business logic that is not bound to the component tree — it hosts **global state**. It has three concepts, the equivalents of `data`, `computed`, and `methods`:

- [state](03-state.md)
- [getters](04-getters.md)
- [actions](05-actions.md)

## When to use a store

Put data in a store when it can be accessed throughout the app — user information shown in the navbar, or state that must survive page changes, e.g. a complicated multi-step form.

Avoid putting local component data in a store (e.g. visibility of an element local to a page). If you feel the app is over-using stores, some logic should probably be composables and some state should be component-local.

## Vuex comparison (v4)

Pinia replaces Vuex. Key differences:

- No `mutations` — state is mutated directly or via `$patch()`.
- No magic strings — import and call store functions, autocompletion included.
- No dynamically registered stores or nested modules — stores are flat and all dynamic by default; a store can import and use another store, even circularly.
- Full TypeScript inference with `strict` (or at least `noImplicitThis`) — no custom wrappers needed.

## Map helpers

If you are not using `setup()`, Pinia provides Vuex-style helpers: `mapStores()`, `mapState()`, `mapWritableState()`, `mapGetters()` (migration convenience — prefer `mapState()`), and `mapActions()`. See [10-options-api-hmr](10-options-api-hmr.md).

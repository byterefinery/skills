---
name: pinia-4-1-0
description: Pinia 4.1.0 — the official Vue.js state management library, ESM-only. Covers store definition (Option and Setup stores), reactive state with $patch/$subscribe/$reset, getters, actions, $onAction, plugins, composing stores, composables with skipHydrate(), SSR hydration, Nuxt integration, testing with @pinia/testing, Options API map helpers, and HMR. Use when working with Pinia stores, state management in Vue 3 apps, migrating from Vuex, or debugging reactive store issues.
license: MIT
compatibility: Requires Vue 3.5.11+ and @vue/devtools-api 8.2.1+ (required peer dependency, install it manually). TypeScript 5.6.0+ optional. ESM only, no CJS builds.
metadata:
  tags:
    - javascript
    - vue
    - state-management
    - store
    - reactive
    - frontend
---

# pinia 4.1.0

## Overview

Pinia (pronounced "peenya") is the official state management library for Vue.js and the recommended replacement for Vuex. A store hosts state (like `data`), getters (like `computed`), and actions (like `methods`) outside the component tree. Stores are singletons per pinia instance and fully reactive, so state and getters are accessed on the store without `.value`. Pinia is ~1.5kb and works with both the Options API and the Composition API.

Pinia 4 is ESM-only (CJS builds were dropped in 4.0) and its errors/dev warnings are built on Nostics for actionable diagnostics. Since v4, `@vue/devtools-api` is a required peer dependency that you install yourself. New in 4.1.0, `getStores(pinia)` returns a copy of the store registry so you can safely iterate over all stores of a pinia instance.

## Usage

Install pinia together with the required devtools peer dependency:

```bash
npm install pinia @vue/devtools-api
```

Create the pinia instance and install it as a plugin:

```js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const pinia = createPinia()
const app = createApp(App)
app.use(pinia)
app.mount('#app')
```

Define each store in its own file:

```js
// stores/counter.js
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  getters: {
    doubleCount: (state) => state.count * 2,
  },
  actions: {
    increment() {
      this.count++
    },
  },
})
```

Use it in a component:

```vue
<script setup>
import { storeToRefs } from 'pinia'
import { useCounterStore } from '@/stores/counter'

const store = useCounterStore()
// destructure state/getters reactively
const { count, doubleCount } = storeToRefs(store)
// actions are bound to the store; destructure them directly
const { increment } = store
</script>
```

Setup stores pass a function instead of the options object; returned refs become state, computed become getters, functions become actions:

```js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }
  return { count, doubleCount, increment }
})
```

## Gotchas

- **Install `@vue/devtools-api` manually** — required peer dependency since v4; pinia does not bundle it.
- **ESM only** — `require('pinia')` no longer works; v4 dropped CJS builds.
- **Return every state property from setup stores** — Pinia only picks up returned refs as state; "private" or readonly state breaks SSR hydration, devtools, and plugins.
- **Never destructure the store directly** — the store is `reactive()`; destructuring loses reactivity. Use `storeToRefs(store)` for state/getters; actions may be destructured (they are bound).
- **You cannot add state properties not declared in `state()`** — every piece of state needs an initial value there (even `undefined`).
- **`store.$state = {...}` does not replace state** — it calls `$patch()` internally; exact replacement would break reactivity.
- **`$reset()` exists only on Option stores** — Setup stores must define their own reset action.
- **Getters cannot take parameters** — they are computed; return a function from the getter instead (which stops caching). Getters that use `this` need an explicit return type in TypeScript.
- **`useStore()` outside components** — in SPAs it only works after `app.use(pinia)`; in SSR apps always pass the pinia instance (`useStore(pinia)`) so the right app instance is used. Defer the call into guards/prefetch functions.
- **In SSR, call `useOtherStore()` at the top of an action, before any `await`** — calling after an `await` can resolve the wrong pinia instance.
- **Plugins only apply to stores created after `pinia.use()` and after the app installs pinia** — existing stores are not retro-augmented.
- **Composables in stores under SSR** — Option stores need a `hydrate(state, initialState)` function because `state()` is not called when hydrating; Setup stores mark non-hydratable state with `skipHydrate()`.
- **Stores using each other** — two stores must not read each other's state in the setup function body (infinite loop); read the other store inside computed or actions.

## References

- [01-getting-started](references/01-getting-started.md) — installation, pinia instance, when to (not) use stores
- [02-defining-stores](references/02-defining-stores.md) — defineStore, Option vs Setup stores, storeToRefs
- [03-state](references/03-state.md) — state, $patch, $reset, $subscribe, TypeScript
- [04-getters](references/04-getters.md) — getters, parameterized getters, cross-store getters
- [05-actions](references/05-actions.md) — actions, async, $onAction subscriptions
- [06-plugins](references/06-plugins.md) — pinia.use, augmenting stores, custom options, TypeScript
- [07-composing-stores](references/07-composing-stores.md) — stores using stores, composables, skipHydrate
- [08-ssr-nuxt](references/08-ssr-nuxt.md) — SSR hydration, devalue, Nuxt module
- [09-testing](references/09-testing.md) — unit tests, @pinia/testing, stubbing actions
- [10-options-api-hmr](references/10-options-api-hmr.md) — mapStores/mapState/mapActions, setMapStoreSuffix, HMR

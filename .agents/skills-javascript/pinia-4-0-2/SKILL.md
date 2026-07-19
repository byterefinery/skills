---
name: pinia-4-0-2
description: Pinia 4.0.2 — the official Vue.js state management library. Covers store definition (Options and Setup APIs), reactive state with $patch/$subscribe/$reset, getters, actions, plugins, SSR hydration, storeToRefs, map helpers for Options API components, HMR, and build-less browser usage via CDN (IIFE and ESM builds). Use when working with Pinia stores, state management in Vue 3 apps, migrating from Vuex, or debugging reactive store issues.
license: MIT
compatibility: Requires Vue 3.5.11+ and @vue/devtools-api 8.1.5+. TypeScript 5.6.0+ optional. Browser: ES module support + import maps (Safari 16.4+).
metadata:
  tags:
    - javascript
    - vue
    - state-management
    - store
    - reactive
    - frontend
---

# pinia 4.0.2

## Overview

Pinia is the official state management library for Vue.js. It lets you define stores — reactive containers that hold shared state, computed getters, and actions. Stores are singleton per Pinia instance and work seamlessly with Vue's reactivity system. Pinia replaced Vuex as the recommended solution and supports both Composition API (Setup Stores) and Options API (Option Stores) styles.

Pinia ships multiple build formats: an ESM build for bundlers (`dist/pinia.js`), ESM browser builds (`dist/pinia.esm-browser.js`), and IIFE global builds (`dist/pinia.iife.js`) for direct browser use without any build step. The IIFE build bundles the `nostics` diagnostic library but externalizes Vue as a global dependency.

Core concepts:
- **`createPinia()`** — creates a Pinia instance to install via `app.use()`
- **`defineStore(id, options)`** — defines a store (Options API: state/getters/actions, or Setup API: a function returning reactive state)
- **`useStore()`** — retrieves (or creates) a store instance inside components or composables
- **`$patch()`** — applies partial state updates or mutation functions
- **`$subscribe()`** — watches state changes
- **`$onAction()`** — intercepts action calls with before/after/onError hooks
- **`storeToRefs()`** — extracts all state and getters as refs, preserving reactivity when destructuring

## Usage

### Build-less browser usage (no build step)

Load Pinia via the IIFE global build. Vue must be loaded first as a global:

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="https://unpkg.com/pinia@4.0.2/dist/pinia.iife.js"></script>
<script>
  const { createApp, ref, computed } = Vue
  const { createPinia, defineStore } = Pinia

  const useCounter = defineStore('counter', {
    state: () => ({ count: 0 }),
    getters: { double: (state) => state.count * 2 },
    actions: { increment() { this.count++ } }
  })

  const app = createApp({
    setup() {
      const store = useCounter()
      return { store }
    },
    template: `
      <div>
        <p>Count: {{ store.count }}</p>
        <p>Double: {{ store.double }}</p>
        <button @click="store.increment()">+</button>
      </div>
    `
  })

  app.use(createPinia())
  app.mount('#app')
</script>
```

For production, use `pinia.iife.prod.js` (minified, dev checks stripped). The global object is `Pinia`. See [01-build-less](references/01-build-less.md) for ESM browser builds, import maps, and production deployment.

### Standard setup with a build tool

```js
// stores/counter.js
import { defineStore } from 'pinia'

export const useCounter = defineStore('counter', {
  state: () => ({ count: 0, name: 'pinia' }),
  getters: {
    doubleCount: (state) => state.count * 2,
  },
  actions: {
    increment() { this.count++ },
    reset() { this.$reset() },
  },
})

// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')

// In any component:
// const counter = useCounter()
// counter.increment()
```

### Setup Store (Composition API style)

```js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCounter = defineStore('counter', () => {
  const count = ref(0)
  const double = computed(() => count.value * 2)

  function increment() { count.value++ }

  return { count, double, increment }
})
```

Setup stores use `ref()` for state and `computed()` for getters. All returned functions are automatically treated as actions with `$onAction` support. Setup stores do not implement `$reset()` — there is no initial state to reset to.

### Using stores in components

```vue
<script setup>
import { useCounter } from './stores/counter'
import { storeToRefs } from 'pinia'

const counter = useCounter()

// Destructure with storeToRefs to keep reactivity
const { count, double } = storeToRefs(counter)
const { increment } = counter  // actions can be destructured directly
</script>

<template>
  <p>Count: {{ count }}</p>
  <button @click="increment">+</button>
</template>
```

## Gotchas

- **`storeToRefs()` is required when destructuring state** — plain destructuring `const { count } = store` loses reactivity because `count` becomes a plain value snapshot. Use `const { count } = storeToRefs(store)` to get reactive refs. Actions and getters can be destructured directly from the store without `storeToRefs()` for actions, but `storeToRefs()` handles both correctly.
- **`$reset()` only works on Option Stores** — Setup Stores have no declared initial state, so `$reset()` throws. Implement a manual reset action instead.
- **`defineStore` state function must be an arrow function** — using `function() {}` breaks TypeScript inference of the store type. Always use `state: () => ({ count: 0 })`.
- **Stores are singletons per Pinia instance** — calling `useStore()` multiple times returns the same instance. The store is lazily created on first call and cached in `pinia._s`.
- **`useStore()` must be called during setup** — like all composables, call `useStore()` at the top level of `setup()` or `<script setup>`. Calling it conditionally or inside async callbacks breaks reactivity tracking.
- **SSR requires `setActivePinia()`** — on the server, set the active pinia at the top of request handlers. Without it, `useStore()` falls back to a global `activePinia` which causes cross-request state pollution.
- **`$patch()` with a function must be synchronous** — `store.$patch(state => { ... })` cannot be async. Pinia enforces this at the type level. For async operations, use an action that calls `$patch` inside.
- **Plugins run for every store** — `pinia.use(plugin)` extends every store created after the plugin is registered. Order matters: later plugins can override earlier ones. Plugins added before `app.use(pinia)` are queued and applied after installation.
- **Build-less IIFE requires Vue global first** — the IIFE build expects `Vue` on `window`. Load Vue's global build before Pinia's IIFE build. The global object is `Pinia`.
- **`mapStores()` takes arguments, not an array** — `mapStores(useA, useB)` not `mapStores([useA, useB])`. The array form was deprecated and will fail in production builds.
- **Setup store `$subscribe` hydration** — in setup stores, refs created with `ref()` are transferred to `pinia.state.value` to keep everything in sync. If you return a non-state object (like a router instance), wrap it with `skipHydrate()` to prevent Pinia from trying to hydrate it.
- **`__DEV__` guards strip dev-only code** — in production builds, error checks, HMR support, and devtools features are removed. Code guarded by `__DEV__` or `__USE_DEVTOOLS__` will not execute.

## References

- [01-build-less](references/01-build-less.md) — IIFE global build, ESM browser build, import maps, production deployment, CDN URLs, splitting into modules
- [02-defining-stores](references/02-defining-stores.md) — Option Stores vs Setup Stores, defineStore signatures, state/getters/actions, store IDs, useStore()
- [03-state](references/03-state.md) — $patch (object and function forms), $subscribe, $reset, $dispose, reactivity model, pinia.state.value
- [04-getters](references/04-getters.md) — getters as computed properties, accessing other getters and state, writable getters, this context
- [05-actions](references/05-actions.md) — action definition, $onAction lifecycle (before/after/onError), async actions, action tracking
- [06-plugins](references/06-plugins.md) — plugin interface, PiniaPluginContext, extending stores, adding custom properties, ordering, devtools integration
- [07-advanced](references/07-advanced.md) — SSR hydration, setActivePinia/getActivePinia, HMR with acceptHMRUpdate, storeToRefs, map helpers, testing with createTestingPinia, disposePinia

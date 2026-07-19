# Defining Stores

Stores are the core building block of Pinia. Each store is identified by a unique string `id` and is a singleton per Pinia instance. There are two ways to define stores: **Option Stores** (object-based, similar to Vuex) and **Setup Stores** (function-based, using Composition API primitives).

## Option Stores

Option stores use an object with `state`, `getters`, and `actions` properties — similar to Vue's Options API:

```js
import { defineStore } from 'pinia'

export const useCounter = defineStore('counter', {
  state: () => ({
    count: 0,
    name: 'pinia',
    hasChanged: false,
  }),

  getters: {
    doubleCount: (state) => state.count * 2,
    doublePlusOne: (state) => state.doubleCount + 1,
  },

  actions: {
    increment() {
      this.count++
      this.hasChanged = true
    },
    reset() {
      this.$reset()
    },
  },
})
```

### State

The `state` property is a function that returns the initial state object. It must be an arrow function for correct TypeScript inference:

```js
state: () => ({ count: 0, items: [] })
```

The state function is called once per Pinia instance when the store is first created. The returned object is stored in `pinia.state.value[id]` and made reactive through Vue's reactivity system.

### Getters

Getters are computed properties defined as functions that receive the state:

```js
getters: {
  doubleCount: (state) => state.count * 2,
  filteredItems: (state) => (search) =>
    state.items.filter(item => item.name.includes(search)),
}
```

- Getters are read-only and reactive — they update when their dependencies change
- Use `this` to access other getters, state, and actions (same as actions)
- Parameterized getters return a function (curried pattern) for dynamic filtering

### Actions

Actions are methods that can mutate state and perform side effects:

```js
actions: {
  increment() {
    this.count++           // direct state mutation
  },
  incrementBy(amount) {
    this.count += amount
  },
  async fetchData() {
    const res = await fetch('/api/data')
    this.data = await res.json()
  },
}
```

- Actions have full access to `this` — state, getters, other actions, and store methods (`$patch`, `$reset`, etc.)
- Actions can be synchronous or asynchronous
- Actions are automatically tracked by `$onAction()`

### Store ID

The first argument to `defineStore()` is a unique string ID. It must be unique across all stores in the application and is used internally for:

- Caching the store singleton in `pinia._s`
- Storing state in `pinia.state.value[id]`
- Devtools display
- SSR state serialization

```js
defineStore('counter', { /* ... */ })
defineStore('user', { /* ... */ })
```

## Setup Stores

Setup stores use a function that returns reactive state, computed values, and actions — similar to Vue's Composition API `<script setup>`:

```js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCounter = defineStore('counter', () => {
  const count = ref(0)
  const name = ref('pinia')

  const doubleCount = computed(() => count.value * 2)

  function increment() {
    count.value++
  }

  async function fetchData() {
    const res = await fetch('/api/data')
    count.value = await res.json()
  }

  return { count, name, doubleCount, increment, fetchData }
})
```

### Key differences from Option Stores

| Feature | Option Store | Setup Store |
|---|---|---|
| State | `state: () => ({})` | `ref()`, `reactive()` |
| Getters | `getters: {}` | `computed()` |
| Actions | `actions: {}` | plain functions |
| `$reset()` | Available | Not available |
| `this` context | Yes | No — use returned refs |
| Hydration | Automatic | Manual for complex refs |

### When to use Setup Stores

- You prefer Composition API patterns
- You need dynamic state shapes
- You want to reuse logic across stores (composables)
- You are migrating from a Composition API codebase

### When to use Option Stores

- You prefer explicit separation of state/getters/actions
- You need `$reset()` to restore initial state
- You are migrating from Vuex
- You want clearer devtools display of store structure

## Retrieving Stores

The `defineStore()` function returns a `useStore` function that retrieves the store instance:

```js
import { useCounter } from './stores/counter'

// Inside a component setup or composable:
const counter = useCounter()

// The store is a singleton — same instance everywhere:
const counter2 = useCounter()
console.log(counter === counter2) // true
```

### Outside components

When calling `useStore()` outside of a component (e.g., in a module-level composable or server handler), you must either:

1. Pass the Pinia instance explicitly: `useCounter(pinia)`
2. Set the active Pinia: `setActivePinia(pinia)`

```js
import { useCounter } from './stores/counter'
import { setActivePinia } from 'pinia'

// In a server request handler:
setActivePinia(pinia)
const counter = useCounter()  // picks up activePinia
```

### Store type extraction

Pinia provides utility types for extracting store parts:

```ts
import { StoreState, StoreGetters, StoreActions } from 'pinia'
import { useCounter } from './stores/counter'

type CounterState = StoreState<ReturnType<typeof useCounter>>
type CounterGetters = StoreGetters<ReturnType<typeof useCounter>>
type CounterActions = StoreActions<ReturnType<typeof useCounter>>
```

## Cross-store access

Stores can access each other by calling their `useXxx()` function inside actions or getters:

```js
// stores/cart.js
import { defineStore } from 'pinia'
import { useUser } from './user'

export const useCart = defineStore('cart', {
  state: () => ({ items: [] }),
  actions: {
    addItem(product) {
      const user = useUser()
      if (!user.isAuthenticated) {
        throw new Error('Must be logged in')
      }
      this.items.push(product)
    },
  },
})
```

In setup stores, call the other store's `useXxx()` inside an action:

```js
export const useCart = defineStore('cart', () => {
  const items = ref([])

  function addItem(product) {
    const user = useUser()
    if (!user.isAuthenticated) throw new Error('Must be logged in')
    items.value.push(product)
  }

  return { items, addItem }
})
```

## Gotchas

- **State function must be an arrow function** — `state: () => ({})` not `state: function() {}`. Regular functions break TypeScript inference of the store type.
- **Store ID must be unique** — duplicate IDs cause the second store to reuse the first store's state. Pinia warns in dev mode.
- **`defineStore` is called once, `useStore` is called per-component** — `defineStore()` creates the store definition (called once at module load). `useStore()` retrieves the singleton instance (called per component, returns the same instance).
- **Setup stores cannot use `this`** — all state access must go through the returned refs. Use `count.value` not `this.count`.
- **`$reset()` throws on setup stores** — setup stores have no declared initial state shape, so there is nothing to reset to. Implement a manual reset action if needed.
- **Circular store dependencies work** — stores can reference each other inside actions. Pinia stores a partial store in `pinia._s` before the setup function completes, allowing cross-references without infinite loops.
- **Non-state objects in setup stores** — if you return a non-reactive object (like a router or API client), wrap it with `skipHydrate()` to prevent Pinia from trying to hydrate it during SSR.

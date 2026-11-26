# Defining a Store

A store is defined with `defineStore()` and requires a **unique** id (name) as its first argument — Pinia uses it to connect the store to devtools. By convention the returned function is named `use<Store>Store` (e.g. `useUserStore`, `useCartStore`).

```js
import { defineStore } from 'pinia'

export const useAlertsStore = defineStore('alerts', {
  // state, getters, actions...
})
```

The second argument is either an **Options object** or a **Setup function**.

## Option Stores

Like Vue's Options API: `state`, `getters`, and `actions` properties.

```js
export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0, name: 'Eduardo' }),
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

Think of `state` as `data`, `getters` as `computed`, `actions` as `methods`. Option stores are the easiest way to start.

## Setup Stores

Like Vue's `setup()`: a function that defines reactive properties and methods and returns the object to expose.

```js
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const name = ref('Eduardo')
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }
  return { count, name, doubleCount, increment }
})
```

In setup stores, `ref()`s become state, `computed()`s become getters, `function()`s become actions. Rules:

- **You must return all state properties** for Pinia to pick them up as state. Private or readonly state is not possible and would break SSR, devtools, and plugins.
- Setup stores are more flexible: watchers and any composable can be used inside.
- Properties provided at the App level can be accessed with `inject()`, and `useRoute()` works too — but do **not** return properties like `route`; components access them directly.

## Which syntax

Pick what you are most comfortable with: Option stores are easier, Setup stores are more flexible and powerful. Both are fully supported.

## Using the store

Calling `use...Store()` inside `<script setup>` (or `setup()`) returns the store instance. Define **each store in its own file** so the bundler can code-split and TypeScript inference stays precise.

The store is an object wrapped with `reactive()`: no `.value` on getters or state, but **you cannot destructure it** directly:

```vue
<script setup>
import { useCounterStore } from '@/stores/counter'
import { computed } from 'vue'

const store = useCounterStore()

// breaks reactivity — never do this
const { name, doubleCount } = store

// reactive — or just use store.doubleCount directly
const doubleValue = computed(() => store.doubleCount)
</script>
```

## Destructuring from a store

Use `storeToRefs()` to extract reactive refs for every reactive property (state and getters, including properties added by plugins; actions and non-reactive properties are skipped). Actions can be destructured from the store directly because they are bound:

```vue
<script setup>
import { storeToRefs } from 'pinia'
import { useCounterStore } from '@/stores/counter'

const store = useCounterStore()
// reactive refs
const { name, doubleCount } = storeToRefs(store)
// bound action — safe to destructure
const { increment } = store
</script>
```

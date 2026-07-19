# Getters

Getters are computed properties on a store. They are reactive — they automatically update when their dependencies change — and are cached based on their dependencies.

## Option Store Getters

In option stores, getters are defined as an object of functions that receive the state:

```js
const useCounter = defineStore('counter', {
  state: () => ({ count: 0, items: [] }),

  getters: {
    // Simple getter — receives state
    doubleCount: (state) => state.count * 2,

    // Accessing other getters via this
    doublePlusOne: (state) => state.doubleCount + 1,

    // Parameterized getter (returns a function)
    filterItems: (state) => (search) =>
      state.items.filter(item => item.name.includes(search)),
  },
})
```

### `this` context

In option store getters, `this` refers to the store instance:

```js
getters: {
  // These are equivalent:
  doubleA: (state) => state.count * 2,
  doubleB: () => this.count * 2,

  // Access other getters:
  triple: () => this.doubleCount + this.count,
}
```

Using `this` allows accessing other getters, state properties, and even actions. However, using the `state` parameter is preferred for clarity and explicitness.

### Parameterized getters

When a getter needs an argument, return a function (curried pattern):

```js
getters: {
  // Returns a function that takes a search string
  filterByCategory: (state) => (category) =>
    state.items.filter(item => item.category === category),
}

// Usage:
const electronics = store.filterByCategory('electronics')
```

The returned function is not reactive itself — it is called each time the template evaluates it. For reactive parameterized access, use a computed that wraps the call:

```js
const category = ref('electronics')
const filtered = computed(() => store.filterByCategory(category.value))
```

## Setup Store Getters

In setup stores, use `computed()` from Vue:

```js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounter = defineStore('counter', () => {
  const count = ref(0)
  const items = ref([])

  const doubleCount = computed(() => count.value * 2)

  const filterItems = (search) =>
    items.value.filter(item => item.name.includes(search))

  return { count, items, doubleCount, filterItems }
})
```

- `computed()` creates a reactive getter (same as option store getters)
- Plain functions act as parameterized getters (same curried pattern)

## Writable Getters

Getters can be made writable using a `computed` with a setter. This works in both styles:

### Option Store

```js
getters: {
  fullName: {
    get: (state) => state.firstName + ' ' + state.lastName,
    set: (value) => {
      const [firstName, lastName] = value.split(' ')
      state.firstName = firstName
      state.lastName = lastName
    },
  },
}
```

### Setup Store

```js
const fullName = computed({
  get: () => firstName.value + ' ' + lastName.value,
  set: (value) => {
    const [firstNameVal, lastNameVal] = value.split(' ')
    firstName.value = firstNameVal
    lastName.value = lastNameVal
  },
})
```

Writable getters appear as writable properties on the store and work with `storeToRefs()`.

## Getters and Reactivity

Getters are backed by Vue's `computed()` and inherit all its reactivity behavior:

- **Lazy evaluation** — getters are computed only when first accessed, then cached
- **Dependency tracking** — getters automatically re-compute when accessed state changes
- **Stale caching** — getters retain their cached value until a dependency changes
- **Cross-store reactivity** — reading another store's state inside a getter creates a reactive dependency

```js
getters: {
  // Reading another store creates a reactive dependency
  totalWithUser: (state) => {
    const user = useUser()
    return state.count + user.score
  },
}
```

## Getters in Templates

Getters are accessed like any other property on the store:

```vue
<script setup>
const counter = useCounter()
</script>

<template>
  <p>{{ counter.doubleCount }}</p>
  <p>{{ counter.filterItems('vue') }}</p>
</template>
```

When destructured, use `storeToRefs()` to keep getter reactivity:

```js
const { doubleCount } = storeToRefs(counter)  // ComputedRef
```

## Gotchas

- **A getter cannot share a name with a state property** — Pinia detects this conflict and emits a dev warning (PINIA_R1002). Rename either the getter or the state property.
- **Parameterized getters are not cached** — the returned function is called on every access. Cache the result with a `computed()` that wraps the call if the computation is expensive.
- **`this` in getters refers to the store** — use `this` to access other getters and state. However, arrow functions with `() =>` capture `this` from the defining scope, which is the store. Named functions with `function() {}` also get `this` bound to the store.
- **Getters are read-only by default** — trying to assign to a getter throws in strict mode. Use a computed with a setter for writable getters.
- **Setup store getters are `computed()` refs** — inside the store function, access them with `.value`. On the store instance, they are auto-unwrapped (like all refs in reactive objects).
- **Cross-store getters create dependencies** — accessing another store's state inside a getter makes the getter reactive to that store's changes. This is usually desired but can cause unexpected re-computations.

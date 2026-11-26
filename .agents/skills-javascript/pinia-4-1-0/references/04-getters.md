# Getters

Getters are computed values over the store state. They receive `state` as first parameter (arrow function encouraged):

```js
export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  getters: {
    doubleCount: (state) => state.count * 2,
  },
})
```

## Accessing other getters

Use a regular function to get `this` (the whole store) — but in TypeScript you **must specify the return type** when a getter uses `this`. This does not affect arrow-function getters or getters that do not use `this`. In JavaScript, use JSDoc `@returns` for the same.

```ts
getters: {
  doubleCount(state) {
    return state.count * 2 // inferred as number
  },
  doublePlusOne(): number {
    return this.doubleCount + 1
  },
}
```

Access getters directly on the store instance: `store.doubleCount`.

## Passing arguments to getters

Getters are computed — you cannot pass parameters. Return a function from the getter instead:

```js
getters: {
  getUserById: (state) => {
    return (userId) => state.users.find((user) => user.id === userId)
  },
}
```

In `<script setup>` the function comes from `storeToRefs()` so you need `getUserById.value` there; in the template just call `getUserById(2)`.

**Note:** once a getter returns a function it is no longer cached — it is simply a function you invoke. You can cache results inside the getter if needed:

```js
getters: {
  getActiveUserById(state) {
    const activeUsers = state.users.filter((user) => user.active)
    return (userId) => activeUsers.find((user) => user.id === userId)
  },
}
```

## Accessing other stores' getters

Use the other store inside the getter:

```js
import { useOtherStore } from './other-store'

export const useStore = defineStore('main', {
  state: () => ({ /* ... */ }),
  getters: {
    otherGetter(state) {
      const otherStore = useOtherStore()
      return state.localData + otherStore.data
    },
  },
})
```

## Options API

Same `mapState()` helper as for state — getters are mapped as readonly computed properties. `mapGetters()` exists only for migration convenience; prefer `mapState()`.

# State

- TypeScript
- Accessing and mutating
- Resetting the state
- Mutating with $patch
- Replacing the state
- Subscribing to state (flush timing, detaching)
- Disposing a store ($dispose)
- Disposing the whole pinia (disposePinia)
- Options API helpers

State is defined as a **function returning the initial state** — this is what lets Pinia work on both server and client.

```js
export const useStore = defineStore('storeId', {
  // arrow function recommended for full type inference
  state: () => {
    return {
      count: 0,
      name: 'Eduardo',
      isAdmin: true,
      items: [],
      hasChanged: true,
    }
  },
})
```

Declare **every** piece of state in `state()`, even if its initial value is `undefined`. You cannot add a new state property later (`store.secondCount = 2` is not possible unless `secondCount` is in `state()`).

## TypeScript

With `strict` (or at least `noImplicitThis`) enabled, state types are inferred automatically. Help inference for initially empty or unloaded data:

```ts
export const useUserStore = defineStore('user', {
  state: () => {
    return {
      userList: [] as UserInfo[],   // initially empty list
      user: null as UserInfo | null // data not yet loaded
    }
  },
})
```

Or type the return of `state()` with an interface (`state: (): State => {...}`).

## Accessing and mutating

Read and write state directly on the store — no verbose wrappers. State can be bound to `v-model`:

```vue-html
<input v-model="store.count" type="number" />
```

## Resetting the state

Option stores get `$reset()` for free — it calls `state()` and replaces the current state. Setup stores must define their own reset:

```ts
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  function $reset() {
    count.value = 0
  }
  return { count, $reset }
})
```

## Mutating with $patch

Besides direct mutation (`store.count++`), call `$patch()` with a partial state object to group several changes into one devtools entry:

```js
store.$patch({
  count: store.count + 1,
  age: 120,
  name: 'DIO',
})
```

For collection changes (push, splice, ...), use the function form, which receives the state:

```js
store.$patch((state) => {
  state.items.push({ name: 'shoes', quantity: 1 })
  state.hasChanged = true
})
```

Both direct changes and `$patch()` are tracked in devtools and can be time-traveled.

## Replacing the state

You **cannot exactly replace** state (that would break reactivity). `store.$state = { count: 24 }` internally calls `store.$patch({ count: 24 })`. To set the initial state of the whole app (e.g. for SSR hydration), set `pinia.state.value`.

## Subscribing to state

`$subscribe()` watches the state like Vuex's `subscribe`, but a subscription fires **once per patch** (the function form is batched). The callback receives `(mutation, state)`:

```js
cartStore.$subscribe((mutation, state) => {
  mutation.type // 'direct' | 'patch object' | 'patch function'
  mutation.storeId // same as cartStore.$id
  mutation.payload // only for mutation.type === 'patch object'
  localStorage.setItem('cart', JSON.stringify(state))
})
```

### Flush timing

`$subscribe()` accepts `watch()` options. `{ flush: 'sync' }` runs the callback after **every** state change instead of batching — useful for persistence, but it has a performance cost if state changes often. It also matters for correctness in a niche case: a direct mutation happening in the same tick right after a `$patch()` will not trigger a non-sync subscription on its own.

### Detaching subscriptions

By default a subscription added in a component's `setup()` is removed on unmount. Pass `{ detached: true }` as second argument to keep it alive:

```js
someStore.$subscribe(callback, { detached: true })
```

You can also watch the whole pinia state with one `watch(pinia.state, cb, { deep: true })`.

## Disposing a store ($dispose)

`$dispose()` stops the store's effect scope, clears subscriptions and action listeners, and removes the store from the registry:

```js
counter.$dispose()
```

After disposal:
- The store's effect scope is stopped
- All `$subscribe` and `$onAction` callbacks are cleared
- The store is removed from `pinia._s`
- The state remains in `pinia.state.value` (delete manually if needed)

If the store is used again after disposal, it will be recreated. If you want to also delete the persisted state:

```js
delete pinia.state.value[counter.$id]
```

## Disposing the whole pinia (disposePinia)

`disposePinia(pinia)` (exported from 'pinia' in 4.1.0) destroys the entire pinia instance: every store is disposed (effect scopes stopped), all subscriptions and action listeners are cleared, and all state is removed — the superset of calling `$dispose()` on each store. Mainly useful in tests, to tear down the pinia created with `setActivePinia(createPinia())` between test runs.

## Options API helpers

```js
import { mapState, mapWritableState } from 'pinia'

export default {
  computed: {
    // read-only computed properties, this.count
    ...mapState(useCounterStore, ['count']),
    // custom names and functions (fn gets the store)
    ...mapState(useCounterStore, {
      myOwnName: 'count',
      double: (store) => store.count * 2,
    }),
    // writable — this.count++ works (no function form)
    ...mapWritableState(useCounterStore, ['count']),
  },
}
```

You only need `mapWritableState()` when replacing whole collections (`cartItems = []`); `mapState()` still lets you call methods on collections.

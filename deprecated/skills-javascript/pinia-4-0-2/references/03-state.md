# State

Pinia state is stored in a centralized reactive tree at `pinia.state.value`, keyed by store ID. Each store's state is a reactive object that can be accessed directly on the store instance or through `store.$state`.

## Accessing State

State properties are directly accessible on the store instance:

```js
const counter = useCounter()

counter.count        // direct access
counter.$state.count // same value, via $state
counter.$state       // entire state object
```

Direct access (`counter.count`) and `$state` access (`counter.$state.count`) are equivalent. The store instance is a reactive proxy that delegates state property access to the underlying reactive state.

### Setting `$state`

Assigning to `$state` patches the current state with the new object:

```js
counter.$state = { count: 42, name: 'new' }
// Equivalent to:
counter.$patch((state) => Object.assign(state, { count: 42, name: 'new' }))
```

This triggers subscriptions and updates all reactive bindings.

## $patch

`$patch()` applies changes to the state. It accepts two forms: an object for partial updates, or a function for complex mutations.

### Object form (shallow merge)

```js
counter.$patch({
  count: counter.count + 1,
  name: 'updated',
})
```

The object is merged into the state using `mergeReactiveObjects()`, which performs a shallow merge. Nested plain objects are merged recursively, but arrays and other types are replaced entirely.

### Function form

```js
counter.$patch((state) => {
  state.count++
  state.items.push(newItem)
  state.hasChanged = true
})
```

The function receives the raw state object and mutates it directly. This form is useful for:

- Array operations (`push`, `splice`, `unshift`)
- Multiple related mutations in one atomic operation
- Complex logic that doesn't fit the object patch pattern

The function **must be synchronous**. Pinia enforces this at the type level — async functions are rejected by TypeScript.

### Subscriptions and $patch

Both forms of `$patch` trigger `$subscribe` callbacks. The subscription receives a mutation object with `type: MutationType.patchObject` (object form) or `type: MutationType.patchFunction` (function form).

## $subscribe

`$subscribe()` sets up a watcher on the store's state. It is called whenever the state changes — through direct mutation, `$patch()`, or action side effects.

```js
const unsubscribe = counter.$subscribe((mutation, state) => {
  console.log(mutation.type, mutation.storeId)
  console.log('New state:', state)
})

// Later, remove the subscription:
unsubscribe()
```

### Mutation object

The `mutation` argument contains:

```ts
interface SubscriptionCallbackMutation {
  type: MutationType.direct | MutationType.patchObject | MutationType.patchFunction
  storeId: string
  events?: DebuggerEvent[]    // dev only
}
```

- `MutationType.direct` — direct state mutation (`store.count = 5`)
- `MutationType.patchObject` — `$patch({ ... })` with an object
- `MutationType.patchFunction` — `$patch(state => { ... })` with a function

### Options

```js
counter.$subscribe((mutation, state) => {
  // callback
}, {
  flush: 'sync',      // 'pre' (default), 'post', or 'sync'
  detached: true,     // detach from component lifecycle
})
```

- `flush: 'sync'` — fires synchronously on every change (default is `'pre'`, fires before DOM updates). Note: `$patch()` always triggers subscriptions synchronously regardless of `flush`.
- `detached: true` — prevents automatic cleanup when the component unmounts. By default, subscriptions set up inside a component are cleaned up on unmount.

### Subscription deduplication

Passing the same callback function to `$subscribe()` more than once is a no-op — Pinia deduplicates subscriptions and only keeps one copy. A dev warning is emitted.

## $reset

`$reset()` restores the store to its initial state. It is only available on **Option Stores**:

```js
// Option Store
const counter = useCounter()
counter.count = 42
counter.$reset()
console.log(counter.count) // 0 — back to initial state
```

For setup stores, `$reset()` throws an error because there is no declared initial state shape. Implement a manual reset:

```js
// Setup Store — manual reset
export const useCounter = defineStore('counter', () => {
  const count = ref(0)

  function reset() {
    count.value = 0
  }

  return { count, reset }
})
```

## $dispose

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

## pinia.state.value

The root state tree stores all state keyed by store ID:

```js
const pinia = createPinia()

// After stores are created:
pinia.state.value
// {
//   counter: { count: 0, name: 'pinia' },
//   user: { id: 1, name: 'John' },
// }
```

This is useful for:
- **SSR serialization** — serialize `pinia.state.value` to pass to the client
- **State inspection** — debug or log all state at once
- **State reset** — `pinia.state.value = {}` clears all state

## Reactive State Model

Pinia stores are reactive Vue proxies. The store instance wraps the state, getters, and actions in a single reactive object. This means:

- State changes trigger reactivity (computed, watchers, component re-renders)
- Getters are Vue `computed()` properties
- The store itself can be passed around as a single reactive reference

### Keeping reactivity when destructuring

Plain destructuring loses reactivity:

```js
// ❌ Loses reactivity
const { count } = counter
count // static value, not reactive

// ✅ Keeps reactivity with storeToRefs
import { storeToRefs } from 'pinia'
const { count } = storeToRefs(counter)
count.value // reactive ref
```

Actions can be destructured directly without `storeToRefs()`:

```js
const { increment, reset } = counter  // functions, no reactivity needed
```

But `storeToRefs()` handles everything correctly — it extracts state and getters as refs and skips non-reactive properties like actions and internal properties.

## skipHydrate

In setup stores, wrap non-state objects with `skipHydrate()` to prevent Pinia from trying to hydrate them during SSR:

```js
import { defineStore } from 'pinia'
import { skipHydrate } from 'pinia'
import { useRouter } from 'vue-router'

export const useAuth = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const router = skipHydrate(useRouter())  // don't hydrate router

  return { isAuthenticated, router }
})
```

`shouldHydrate(obj)` returns the inverse — `true` if the object should be hydrated, `false` if it was wrapped with `skipHydrate()`.

## Gotchas

- **`$patch()` function form must be synchronous** — async functions are rejected at the type level. For async mutations, wrap the logic in an action that calls `$patch` inside.
- **`$patch()` object form does shallow merge at top level** — nested plain objects are merged recursively, but arrays are replaced entirely. Use the function form for array mutations.
- **`$subscribe` with `flush: 'sync'` fires for every mutation** — including those inside `$patch()`. Default `flush: 'pre'` batches mutations but `$patch()` always triggers synchronously.
- **`$reset()` is an option-store-only feature** — setup stores throw when `$reset()` is called. The error message is clear in dev mode but silent in production (noop).
- **`pinia.state.value` holds raw state** — the values in `pinia.state.value[id]` are the reactive state objects, not the store instances. For setup stores, refs created inside the store are transferred to `pinia.state.value` to keep everything in sync.
- **Subscriptions auto-clean in components** — `$subscribe()` called inside a component's setup is automatically cleaned up on unmount. Use `detached: true` to persist beyond the component lifecycle.

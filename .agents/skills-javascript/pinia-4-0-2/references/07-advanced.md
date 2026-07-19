# Advanced Topics

Covers SSR hydration, HMR, store utilities, map helpers for Options API components, testing, and instance management.

## SSR (Server-Side Rendering)

Pinia supports SSR by serializing the server's state and hydrating it on the client.

### Server side

```js
// Create a fresh pinia instance per request
const pinia = createPinia()

// Set it as active so useStore() works outside components
setActivePinia(pinia)

// Use stores during request handling
const counter = useCounter()
counter.increment()

// After rendering, serialize the state
const state = pinia.state.value
// Pass `state` to the client (e.g., inline in HTML or via JSON)
```

Each request gets its own Pinia instance to avoid cross-request state pollution.

### Client side

```js
import { createPinia, setActivePinia } from 'pinia'

const pinia = createPinia()

// Hydrate from server state
pinia.state.value = serverState

// Install
app.use(pinia)
```

The client creates a Pinia instance and sets `pinia.state.value` to the serialized server state before installing. When stores are first accessed, they find their state already in the state tree and use it directly.

### setActivePinia / getActivePinia

```js
import { setActivePinia, getActivePinia } from 'pinia'

// Set the active pinia (SSR, testing, outside components)
setActivePinia(pinia)

// Get the currently active pinia
const currentPinia = getActivePinia()
```

- `setActivePinia(pinia)` — sets the global active Pinia instance. Required when calling `useStore()` outside of a component's setup function.
- `setActivePinia(undefined)` — clears the active pinia.
- `getActivePinia()` — returns the current active pinia. Inside components, it first tries Vue's injection context, then falls back to the global `activePinia`.

### SSR gotchas

- **One Pinia instance per request** — never reuse a Pinia instance across requests. Create a new one for each request.
- **Call `setActivePinia()` at the top of request handlers** — without it, `useStore()` cannot find the pinia and falls back to a potentially stale global.
- **Custom refs need manual hydration** — if your state contains `customRef()`, `computed()`, or `ref()` with different server/client values, implement the `hydrate` option in option stores or use `skipHydrate()` in setup stores.
- **PINIA_R1004 warning** — emitted in dev mode when `getActivePinia()` falls back to the global `activePinia` on the server. This indicates potential cross-request pollution.

## HMR (Hot Module Replacement)

Pinia supports HMR for stores in Vite applications. Use `acceptHMRUpdate()` to preserve store state during hot updates:

```js
// stores/counter.js
import { defineStore } from 'pinia'
import { acceptHMRUpdate } from 'pinia'

export const useCounter = defineStore('counter', {
  state: () => ({ count: 0 }),
  actions: { increment() { this.count++ } },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useCounter, import.meta.hot))
}
```

### How HMR works

1. Vite detects a change in the store file
2. `acceptHMRUpdate()` receives the new module
3. Pinia finds the existing store by ID and patches it in place
4. State is preserved, new actions/getters are swapped in

### Store ID changes

If the store ID changes between hot updates, Pinia detects the mismatch and forces a full reload (with a dev warning PINIA_R1005).

### HMR is dev-only

The `acceptHMRUpdate()` function returns a no-op in production builds. All HMR code is guarded by `__DEV__`.

## storeToRefs

`storeToRefs()` extracts all reactive state properties and getters from a store as refs, ignoring actions and internal properties:

```js
import { storeToRefs } from 'pinia'

const counter = useCounter()
const { count, doubleCount } = storeToRefs(counter)

// count is a Ref, doubleCount is a ComputedRef
// Both stay reactive when used in templates or computed
```

### What it extracts

- **State properties** — converted to `ToRef` (reactive refs tied to the store)
- **Getters** — converted to `ComputedRef` (or `WritableComputedRef` for writable getters)
- **Plugin-added state properties** — included if they are refs or reactive
- **Skipped** — actions, `$id`, `$state`, `$patch`, internal properties (`_p`, `_hmrPayload`)

### Why not plain destructuring

```js
// ❌ Loses reactivity
const { count } = counter
// count is now a plain number, disconnected from the store

// ✅ Keeps reactivity
const { count } = storeToRefs(counter)
// count is a Ref, stays connected to the store
```

### Actions don't need storeToRefs

Actions are plain functions — they don't need reactivity:

```js
const { increment } = counter  // ✅ safe
const { increment } = storeToRefs(counter)  // also works, but unnecessary
```

## Map Helpers (Options API)

Map helpers allow using Pinia stores in Options API components without `setup()`:

### mapState

Maps state properties and getters to computed properties:

```js
import { mapState } from 'pinia'
import { useCounter } from './stores/counter'

export default {
  computed: {
    // Array form — maps property names directly
    ...mapState(useCounter, ['count', 'doubleCount']),

    // Object form — custom names or functions
    ...mapState(useCounter, {
      n: 'count',
      triple: (store) => store.count * 3,
      custom(store) {
        return this.someComponentValue + store.count
      },
    }),
  },
}
```

### mapActions

Maps actions to component methods:

```js
import { mapActions } from 'pinia'

export default {
  methods: {
    ...mapActions(useCounter, ['increment', 'reset']),

    // Custom names:
    ...mapActions(useCounter, { more: 'increment', setIt: 'setCount' }),
  },
}
```

### mapWritableState

Maps state properties to writable computed properties:

```js
import { mapWritableState } from 'pinia'

export default {
  computed: {
    ...mapWritableState(useCounter, ['count']),
    // Now this.count = 5 works in templates and methods
  },
}
```

### mapStores

Maps entire stores to computed properties:

```js
import { mapStores } from 'pinia'
import { useCounter } from './stores/counter'
import { useUser } from './stores/user'

export default {
  computed: {
    ...mapStores(useCounter, useUser),
  },
  created() {
    this.counterStore  // useCounter store
    this.userStore     // useUser store
  },
}
```

Stores are suffixed with `Store` by default. Customize with `setMapStoreSuffix()`:

```js
import { setMapStoreSuffix } from 'pinia'
setMapStoreSuffix('')  // no suffix: this.counter, this.user
```

### mapGetters

Alias for `mapState()`. Use `mapState()` instead.

## Testing

Pinia provides `createTestingPinia()` from `@pinia/testing` for unit testing stores in isolation:

```js
import { createTestingPinia } from '@pinia/testing'
import { useCounter } from './stores/counter'

const pinia = createTestingPinia({
  initialState: {
    counter: { count: 10 },
  },
  stubActions: false,  // execute real actions (default: true — stub all)
})

const counter = useCounter()
counter.increment()
expect(counter.count).toBe(11)
```

### TestingOptions

| Option | Default | Description |
|---|---|---|
| `initialState` | `{}` | Partial initial state keyed by store ID |
| `plugins` | `[]` | Plugins to install before the testing plugin |
| `stubActions` | `true` | `true` = stub all, `false` = spy only, `string[]` = stub specific, `fn` = custom predicate |
| `stubPatch` | `false` | Stub `$patch()` calls |
| `stubReset` | `false` | Stub `$reset()` calls |
| `fakeApp` | `false` | Create a fake Vue app and call `app.use(pinia)` |
| `createSpy` | auto | Spy factory (`jest.fn`, `vi.fn`, or custom) |

### Stubbing actions

```js
// Stub all actions (default)
createTestingPinia({ stubActions: true })

// Don't stub — execute real actions
createTestingPinia({ stubActions: false })

// Stub specific actions
createTestingPinia({ stubActions: ['fetchData'] })

// Custom predicate
createTestingPinia({
  stubActions: (name, store) => name.startsWith('fetch'),
})
```

### Writable computed in tests

`createTestingPinia()` installs a plugin that allows manually overriding computed getters. Set a getter's value directly and it persists until reset:

```js
const counter = useCounter()
counter.doubleCount = 99  // override the computed
expect(counter.doubleCount).toBe(99)
counter.doubleCount = undefined  // reset to original computed
```

## disposePinia

`disposePinia()` completely tears down a Pinia instance:

```js
import { createPinia, disposePinia } from 'pinia'

const pinia = createPinia()
// ... use the pinia
disposePinia(pinia)
```

After disposal:
- The effect scope is stopped
- All stores are removed from the registry
- All plugins are cleared
- State is reset to `{}`
- The pinia instance cannot be used again

Useful in tests and applications that create multiple Pinia instances.

## Gotchas

- **`setActivePinia()` is required for SSR** — without it, `useStore()` falls back to a global `activePinia` which causes cross-request pollution. Always set it at the top of request handlers.
- **`acceptHMRUpdate()` is dev-only** — it returns a no-op in production. The entire HMR flow is guarded by `__DEV__`.
- **`mapStores()` takes spread args, not an array** — `mapStores(useA, useB)` not `mapStores([useA, useB])`. The array form emits PINIA_R1001 and fails in production.
- **`createTestingPinia()` stubs actions by default** — actions are replaced with spies and do not execute. Set `stubActions: false` to run real actions.
- **`createTestingPinia()` needs a spy factory** — it auto-detects `jest.fn` and `vi.fn`. If neither is available, provide `createSpy` manually.
- **`disposePinia()` doesn't delete state** — it clears the effect scope and store registry but leaves `pinia.state.value` intact. Delete `pinia.state.value[store.$id]` manually if needed.
- **Map helpers are for Options API only** — in Composition API / `<script setup>`, use `useStore()` directly. Map helpers generate computed/method objects for the Options API.

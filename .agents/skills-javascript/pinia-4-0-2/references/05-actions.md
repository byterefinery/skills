# Actions

Actions are functions on a store that perform mutations, side effects, and business logic. They are the primary way to change state in a controlled, trackable manner.

## Defining Actions

### Option Store

```js
const useCounter = defineStore('counter', {
  state: () => ({ count: 0, items: [] }),

  actions: {
    // Simple action — direct state mutation via this
    increment() {
      this.count++
    },

    // Action with parameters
    incrementBy(amount) {
      this.count += amount
    },

    // Action using $patch
    setCount(value) {
      this.$patch({ count: value })
    },

    // Async action
    async fetchCount() {
      const res = await fetch('/api/count')
      const data = await res.json()
      this.count = data.count
    },

    // Action calling other actions
    incrementAndLog() {
      this.increment()
      console.log('Count is now', this.count)
    },
  },
})
```

### Setup Store

```js
import { ref } from 'vue'

export const useCounter = defineStore('counter', () => {
  const count = ref(0)
  const items = ref([])

  function increment() {
    count.value++
  }

  function incrementBy(amount) {
    count.value += amount
  }

  async function fetchCount() {
    const res = await fetch('/api/count')
    const data = await res.json()
    count.value = data.count
  }

  return { count, items, increment, incrementBy, fetchCount }
})
```

All returned functions are automatically treated as actions with full `$onAction` support.

## $onAction

`$onAction()` sets up a listener that is called before every action invocation. It provides hooks for before, after, and error handling:

```js
const unsubscribe = counter.$onAction(({ name, store, args, after, onError }) => {
  console.log(`Action "${name}" called on ${store.$id} with args:`, args)

  after((result) => {
    console.log(`Action "${name}" succeeded with:`, result)
  })

  onError((error) => {
    console.error(`Action "${name}" failed with:`, error)
  })
})

// Remove the listener:
unsubscribe()
```

### Context object

```ts
interface StoreOnActionListenerContext {
  name: string              // Action name
  store: Store              // Store instance
  args: any[]               // Arguments passed to the action
  after: (callback) => void // Hook called after action completes
  onError: (callback) => void // Hook called if action throws
}
```

### after() callback

The `after()` callback receives the resolved return value of the action. For async actions, the Promise is unwrapped:

```js
counter.$onAction(({ name, after, onError }) => {
  after((result) => {
    // For sync actions: result is the return value
    // For async actions: result is the resolved value (Promise unwrapped)
    console.log(`${name} returned:`, result)
  })
})
```

### onError() callback

The `onError()` callback receives the error if the action throws:

```js
counter.$onAction(({ onError }) => {
  onError((error) => {
    console.error('Action failed:', error)
    // Return false to catch the error and stop propagation
    // return false
  })
})
```

### Lifecycle

```
Action called
  → $onAction callback fires (before hooks)
    → after() callbacks registered
    → onError() callbacks registered
  → Action executes
    → Success: after() callbacks fire with return value
    → Error: onError() callbacks fire with error
      → Return false in onError to suppress the error
```

For async actions, `after()` fires when the Promise resolves, and `onError()` fires when it rejects.

### Detached listeners

By default, `$onAction()` listeners set up inside a component are cleaned up when the component unmounts. Use `detached: true` to persist:

```js
counter.$onAction(({ name, after }) => {
  after((result) => log(name, result))
}, true)  // detached — survives component unmount
```

## Action Internals

Pinia wraps every action function with a marker and name symbol:

- `ACTION_MARKER` — identifies a function as an action (for `$onAction` tracking)
- `ACTION_NAME` — stores the action name string

This wrapping is transparent — actions behave like normal functions but are intercepted by the internal action wrapper that sets the active Pinia and triggers subscriptions.

### Actions inside stores

When an action calls another action within the same store, the `$onAction` listener fires for each call. The internal `action()` helper from setup store helpers can be used to manually mark functions:

```js
export const useStore = defineStore('my', (helpers) => {
  const count = ref(0)

  // Manually wrap for $onAction tracking (advanced use)
  const internalAction = helpers.action(() => {
    count.value++
  }, 'internalAction')

  return { count, internalAction }
})
```

This is rarely needed in applications — it is intended for advanced use cases like Pinia Colada.

## Actions and Reactivity

Actions are plain functions (not reactive). They can be destructured directly from the store:

```js
const { increment, reset } = counter  // ✅ safe — functions don't need reactivity
```

Actions always have access to the current store state because they read from the reactive store instance at call time, not at definition time.

## Gotchas

- **Actions are not reactive** — they are plain functions. Destructuring them from the store is safe and does not lose reactivity.
- **`this` in option store actions refers to the store** — use `this.count`, `this.$patch()`, `this.$reset()`. In setup stores, use the returned refs directly (`count.value`).
- **Async actions work with $onAction** — `after()` receives the resolved value, `onError()` receives the rejection. The Promise is unwrapped automatically.
- **Action wrapping preserves return values** — the internal wrapper returns whatever the original action returns. Chaining and composition work normally.
- **`$onAction` fires for every action call** — including calls from within other actions. Use this for logging, analytics, or validation.
- **Actions can access other stores** — call `useOtherStore()` inside an action. The action wrapper ensures the active Pinia is set correctly.

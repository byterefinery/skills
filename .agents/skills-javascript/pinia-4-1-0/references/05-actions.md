# Actions

Actions are the store's methods — the right place for business logic. Defined in the `actions` property of `defineStore()`:

```js
export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  actions: {
    // relies on `this` — cannot be an arrow function
    increment() {
      this.count++
    },
    randomizeCounter() {
      this.count = Math.round(100 * Math.random())
    },
  },
})
```

Actions get the whole store via `this` with full typing. **Unlike getters, actions can be asynchronous** — `await` API calls or other actions. You can set whatever arguments you want and return anything (e.g. an error from a `catch` so the calling component can display it):

```js
actions: {
  async registerUser(login, password) {
    try {
      this.userData = await api.post({ login, password })
      showTooltip('Welcome back!')
    } catch (error) {
      showTooltip(error)
      return error
    }
  },
}
```

Call actions like methods, in `<script setup>` or in the template (`@click="store.randomizeCounter()"`).

## Accessing other stores' actions

Use the other store inside the action:

```js
actions: {
  async fetchUserPreferences() {
    const auth = useAuthStore()
    if (auth.isAuthenticated) {
      this.preferences = await fetchPreferences()
    } else {
      throw new Error('User must be authenticated')
    }
  },
}
```

In SSR apps, keep all `useStore()` calls **before any `await`** (see [07-composing-stores](07-composing-stores.md)).

## Subscribing to actions

`store.$onAction()` observes actions. The callback runs before the action; `after` handles the resolved result; `onError` handles throws/rejections — useful for runtime error tracking. It returns an `unsubscribe` function:

```js
const unsubscribe = someStore.$onAction(({ name, store, args, after, onError }) => {
  const startTime = Date.now()
  console.log('Start action ' + name + ' with params ' + args.join(', '))
  after((result) => {
    console.log('Finished after ' + (Date.now() - startTime) + 'ms')
  })
  onError((error) => {
    console.warn('Failed — ' + error)
  })
})

// manually remove the listener
unsubscribe()
```

As with state subscriptions, action subscriptions bound to a component are removed on unmount; pass `true` as second argument to detach (`someStore.$onAction(callback, true)`).

## Options API

Use `mapActions()` to expose actions as component methods:

```js
import { mapActions } from 'pinia'

export default {
  methods: {
    ...mapActions(useCounterStore, ['increment']),
    ...mapActions(useCounterStore, { myOwnName: 'increment' }),
  },
}
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


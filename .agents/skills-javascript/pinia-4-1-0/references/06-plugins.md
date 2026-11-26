# Plugins

- Augmenting a store
- Adding new state (incl. resetting plugin state)
- Non-reactive external objects
- Subscriptions inside plugins
- Custom store options
- TypeScript
- Nuxt

Pinia stores can be fully extended through plugins: add properties or methods to stores, add options consumed at `defineStore()` time, wrap existing methods, intercept actions and results, implement side effects (e.g. localStorage), or target only specific stores.

Plugins are registered on the pinia instance with `pinia.use()`:

```js
const pinia = createPinia()
pinia.use(myPiniaPlugin)
```

A plugin is a function that takes one optional **context** argument and may return an object of properties to add to the store:

```js
export function myPiniaPlugin(context) {
  context.pinia    // the pinia created with createPinia()
  context.app      // the current app created with createApp()
  context.store    // the store the plugin is augmenting
  context.options  // the options object passed to defineStore()
}
```

**Plugins are only applied to stores created after the plugin is installed and after pinia is passed to the app** — otherwise they are silently skipped.

## Augmenting a store

Returning an object adds the properties to every store:

```js
pinia.use(() => ({ hello: 'world' }))
```

You can also set properties directly on `store`, but prefer the return form so devtools track them automatically. Properties set directly on the store are invisible to devtools unless you register them in dev mode:

```js
pinia.use(({ store }) => {
  store.hello = 'world'
  if (process.env.NODE_ENV === 'development') {
    store._customProperties.add('hello')
  }
})
```

Every store is wrapped with `reactive()`, so any `ref()` you attach is unwrapped automatically — which is why state and getters are accessed without `.value`. Shared refs give every store the same value; per-store refs give each store its own.

## Adding new state

State a plugin adds must be registered **in two places**: on `store` (so `store.myState` works) and on `store.$state` (so devtools and SSR serialization see it). Use a `ref()` to share the value across both accesses:

```js
import { toRef, ref } from 'vue'

pinia.use(({ store }) => {
  if (!Object.hasOwn(store.$state, 'hasError')) {
    store.$state.hasError = ref(false)
  }
  store.hasError = toRef(store.$state, 'hasError')
  // do not return hasError — it already appears under state in devtools
})
```

State changes inside a plugin (including `store.$patch()`) happen before the store is active and **do not trigger subscriptions**.

### Resetting plugin state

`$reset()` does not reset state added by plugins; override it to do so:

```js
pinia.use(({ store }) => {
  const originalReset = store.$reset.bind(store)
  return {
    $reset() {
      originalReset()
      store.hasError = false
    },
  }
})
```

## Non-reactive external objects

Wrap class instances and other non-reactive objects with `markRaw()` before attaching them (e.g. adding the router to every store).

## Subscriptions inside plugins

`store.$subscribe()` and `store.$onAction()` work inside plugins too.

## Custom store options

Define extra options in `defineStore()` and consume them in a plugin — e.g. a `debounce` option mapping action names to milliseconds. The plugin returns a replacement object to override actions (e.g. with a debounced version). With setup stores the custom options are the **third argument** to `defineStore(id, setupFn, options)`.

## TypeScript

- Type the context as `PiniaPluginContext` (imported from 'pinia').
- New store properties extend `PiniaCustomProperties` (supports getter/setter declarations to allow both plain values and refs).
- When extending the generic form, the type parameters must be named exactly `Id`, `S`, `G`, `A` (State, Getters, Actions).
- New **state** extends `PiniaCustomStateProperties<S>` (only the State generic).
- New `defineStore()` options extend `DefineStoreOptionsBase<S, Store>`; `DefineStoreOptions` / `DefineSetupStoreOptions` target option/setup stores only.
- A `StoreGetters` type extracts getters from a store type.

## Nuxt

With Nuxt, create a Nuxt plugin that receives `$pinia` and calls `$pinia.use(myPlugin)`.

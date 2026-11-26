# Plugins

Pinia's plugin system allows extending every store with custom properties, state, actions, or getters. Plugins are functions that receive a context object and return an object to merge into the store.

## Plugin Interface

A Pinia plugin is a function that receives a `PiniaPluginContext` and optionally returns an object:

```js
function myPlugin({ pinia, app, store, options }) {
  // Extend the store
  return {
    customProperty: 'hello',
    customAction() {
      console.log('Custom action on', store.$id)
    },
  }
}

// Install the plugin:
const pinia = createPinia()
pinia.use(myPlugin)

// Or before app.use():
pinia.use(myPlugin)
app.use(pinia)
```

## PiniaPluginContext

The context object passed to every plugin:

| Property | Type | Description |
|---|---|---|
| `pinia` | `Pinia` | The Pinia instance |
| `app` | `App` | The Vue app instance (from `createApp()`) |
| `store` | `Store` | The store being extended |
| `options` | `DefineStoreOptionsInPlugin` | The original options passed to `defineStore()` |

### Using the context

```js
function injectApi({ store, options }) {
  // Access the store's id
  console.log('Extending store:', store.$id)

  // Check if this is an option store or setup store
  const isOptionStore = !!options.state

  return {
    // Add a custom property
    $myId: store.$id,

    // Add a custom action
    $log() {
      console.log('Store', store.$id, 'state:', store.$state)
    },
  }
}
```

## Adding Custom Properties

Plugins can add any kind of property to stores:

### Custom state properties

```js
function timestampPlugin({ store }) {
  return {
    createdAt: Date.now(),
    updatedAt: Date.now(),
  }
}
```

Custom state properties are accessible on `store.$state` if they are reactive (refs, reactive objects).

### Custom actions

```js
function loggingPlugin({ store }) {
  return {
    $logState() {
      console.log(store.$id, JSON.stringify(store.$state))
    },
  }
}
```

### Custom getters

```js
function metaPlugin({ store }) {
  return {
    $meta: computed(() => ({
      id: store.$id,
      stateKeys: Object.keys(store.$state),
    })),
  }
}
```

## Adding Custom State Properties

To add properties that appear on `store.$state`, use reactive values:

```js
import { ref } from 'vue'

function statePlugin({ store }) {
  return {
    _isLoading: ref(false),
    _error: ref(null),
  }
}
```

These properties are reactive and appear in `storeToRefs()` output.

## TypeScript: Custom Properties

Extend the `PiniaCustomProperties` and `PiniaCustomStateProperties` interfaces for type safety:

```ts
import 'pinia'

declare module 'pinia' {
  export interface PiniaCustomProperties<
    Id extends string,
    S extends StateTree,
    G,
    A
  > {
    $log: () => void
    $meta: ComputedRef<{ id: string; stateKeys: string[] }>
  }

  export interface PiniaCustomStateProperties<S extends StateTree> {
    _isLoading: Ref<boolean>
    _error: Ref<Error | null>
  }
}
```

After extending, these properties are available on all store types.

## Plugin Ordering

Plugins are applied in registration order. Later plugins can override properties added by earlier plugins:

```js
pinia.use(pluginA)  // adds $meta
pinia.use(pluginB)  // can override $meta
```

Plugins registered before `app.use(pinia)` are queued and applied after installation:

```js
const pinia = createPinia()
pinia.use(pluginA)  // queued
app.use(pinia)      // plugins applied here
pinia.use(pluginC)  // applied immediately
```

## Devtools Plugin

Pinia includes a built-in devtools plugin that integrates with Vue Devtools. It is automatically registered when:

- `__USE_DEVTOOLS__` is true (dev builds)
- Running in a browser environment (`IS_CLIENT`)
- `Proxy` is available

The devtools plugin:
- Registers stores with Vue Devtools
- Tracks state mutations with timestamps
- Displays custom properties added by other plugins
- Supports time-travel debugging

The devtools plugin relies on dev-only features and is stripped in production builds.

## Conditional Plugins

Plugins can skip certain stores or return nothing:

```js
function conditionalPlugin({ store, options }) {
  // Skip specific stores
  if (store.$id === 'exclude-me') {
    return
  }

  // Only extend option stores
  if (!options.state) {
    return
  }

  return { $custom: 'value' }
}
```

Returning `undefined` or `void` means the plugin does not extend that store.

## Accessing Vue App

The `app` property allows integrating with Vue's plugin system:

```js
function vueIntegrationPlugin({ app, store }) {
  // Register a global property
  app.provide('myKey', store.$id)

  // Use other Vue plugins' provides
  const config = app.config.globalProperties.$myConfig

  return { $config: config }
}
```

## Real-world Plugin Examples

### Persisted state

```js
function persistPlugin({ store, options }) {
  if (!options.persist) return

  const key = `pinia:${store.$id}`

  // Restore from localStorage
  const saved = localStorage.getItem(key)
  if (saved) {
    store.$patch(JSON.parse(saved))
  }

  // Save on changes
  store.$subscribe((mutation, state) => {
    localStorage.setItem(key, JSON.stringify(state))
  })
}
```

### Request state management

```js
import { ref, computed } from 'vue'

function requestStatePlugin({ store }) {
  const isLoading = ref(false)
  const error = ref(null)

  return {
    $isLoading: isLoading,
    $error: error,
    $setError(err) { error.value = err },
    $setLoading(val) { isLoading.value = val },
  }
}
```

## Gotchas

- **Plugins run for every store** — there is no per-store plugin registration. Use conditional returns to skip specific stores.
- **Non-reactive objects trigger warnings** — if a plugin returns a plain object as a property value (not a ref, reactive, or `markRaw`), Pinia warns in dev mode (PINIA_R1006). Use `ref()`, `reactive()`, or `markRaw()` for non-reactive values.
- **Plugin order matters** — later plugins can override earlier ones. Design plugins to be composable or document ordering requirements.
- **`app` is available in plugins** — the `app` property is the Vue app instance. Use it for `provide()`, accessing global properties, or integrating with other Vue plugins.
- **Devtools plugin is automatic** — do not manually register the devtools plugin. It is added by `createPinia()` when running in a dev browser environment.
- **TypeScript requires interface extension** — custom properties are not typed on stores until you extend `PiniaCustomProperties` and `PiniaCustomStateProperties`. Without extension, custom properties are `any`.

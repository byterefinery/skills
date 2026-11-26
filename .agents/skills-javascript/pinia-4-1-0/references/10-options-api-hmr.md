# Options API and HMR

## Map helpers

Pinia provides Vuex-style helpers for components that do not use `setup()`:

| Helper | Purpose |
|---|---|
| `mapStores()` | Expose whole stores as computed properties |
| `mapState()` | Read-only computed for state + getters |
| `mapWritableState()` | Writable computed for state (no function form) |
| `mapGetters()` | Migration convenience — prefer `mapState()` |
| `mapActions()` | Expose actions as methods |

### mapStores

Spread into `computed`; each store is accessible as its id plus the suffix (default `Store`):

```js
import { mapStores } from 'pinia'

export default {
  computed: {
    // note: one store after another, not an array
    ...mapStores(useCartStore, useUserStore),
  },
  methods: {
    async buyStuff() {
      if (this.userStore.isAuthenticated()) {
        await this.cartStore.buy()
      }
    },
  },
}
```

### setMapStoreSuffix

Change or remove the suffix:

```js
import { createPinia, setMapStoreSuffix } from 'pinia'

setMapStoreSuffix('')      // this.user, this.cart
setMapStoreSuffix('_store') // this.user_store, this.cart_store
export const pinia = createPinia()
```

If you change the suffix under TypeScript, declare it so types match:

```ts
setMapStoreSuffix('')
declare module 'pinia' {
  export interface MapStoresCustomization {
    suffix: ''
  }
}
```

In a `.d.ts` file (e.g. `global.d.ts`), `import 'pinia'` at the top to expose all existing types.

## HMR (Hot Module Replacement)

Pinia supports HMR — edit stores without reloading the page while keeping existing state. Vite is the officially supported bundler (anything implementing the `import.meta.hot` spec). Add a snippet next to each store declaration, passing the **store definition**:

```js
import { defineStore, acceptHMRUpdate } from 'pinia'

export const useAuth = defineStore('auth', {
  // options...
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuth, import.meta.hot))
}
```

Note: Nuxt auto-imports `acceptHMRUpdate()` (see [08-ssr-nuxt](08-ssr-nuxt.md)).

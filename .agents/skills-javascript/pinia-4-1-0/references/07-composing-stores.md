# Composing Stores

- Setup stores using another store
- Shared getters and actions
- Composables in stores
- SSR with composables (hydrate, skipHydrate)

Stores can use each other. The one rule: if **two or more stores use each other**, they must not create an infinite loop through getters or actions, and they cannot **both** read each other's state in the setup function body. Reading the other store inside computed or actions is fine.

```js
const useX = defineStore('x', () => {
  const y = useY()
  // ❌ not possible if y also reads x.name in its setup body
  // y.name
  function doSomething() {
    const yName = y.name // ✅ inside actions/computed
  }
  return { name: ref('I am X') }
})
```

## Setup stores using another store

Use the other store at the top of the setup function:

```ts
export const useCartStore = defineStore('cart', () => {
  const user = useUserStore()
  const list = ref([])
  const summary = computed(() => {
    return 'Hi ' + user.name + ', you have ' + list.value.length + ' items in your cart.'
  })
  function purchase() {
    return apiPurchase(user.id, list.value)
  }
  return { list, summary, purchase }
})
```

## Shared getters and actions

Option stores: call `useOtherStore()` inside a getter or action. Since actions can be asynchronous, make sure **all `useStore()` calls appear before any `await`** — otherwise you may end up using the wrong pinia instance in SSR apps:

```js
actions: {
  async orderCart() {
    // ✅ at the top, before any await
    const user = useUserStore()
    try {
      await apiOrderCart(user.token, this.items)
      this.emptyCart()
    } catch (err) {
      displayError(err)
    }
  },
}
```

## Composables in stores

Composables work fully inside stores.

**Option stores** — call the composable inside `state()`, but only if it returns **writable state** (a `ref()`):

```ts
import { useLocalStorage } from '@vueuse/core'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: useLocalStorage('pinia/auth/login', 'bob'),
  }),
})
```

Composables exposing functions or readonly data (e.g. `useMediaControls`, `useMemoryInfo`) cannot be used in option stores — use a setup store instead.

**Setup stores** — almost any composable works, since every returned property is discerned as state, action, or getter. Do not return non-serializable client-only refs (e.g. a `ref<HTMLVideoElement>()` holding a DOM element):

```ts
export const useVideoPlayer = defineStore('video', () => {
  const videoElement = ref<HTMLVideoElement>()
  const src = ref('/data/video.mp4')
  const { playing, volume, currentTime, togglePictureInPicture } =
    useMediaControls(videoElement, { src })
  return { src, playing, volume, currentTime, togglePictureInPicture }
})
```

## SSR with composables

- **Option stores**: define a `hydrate(state, initialState)` function — it is called on the client when an initial state exists, because `state()` is **not** called during hydration.
- **Setup stores**: wrap non-hydratable state with `skipHydrate()` (applies to state properties only):

```ts
import { defineStore, skipHydrate } from 'pinia'

export const useColorStore = defineStore('colors', () => {
  const { isSupported, open, sRGBHex } = useEyeDropper()
  const lastColor = useLocalStorage('lastColor', sRGBHex)
  return {
    lastColor: skipHydrate(lastColor), // Ref<string>
    open,          // Function
    isSupported,   // boolean, not even reactive
  }
})
```

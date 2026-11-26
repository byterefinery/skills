# Data Loaders (experimental)

Data loaders move async state management (data fetching) **out of the component `setup`** — loading logic runs independently of the component lifecycle, is collected and awaited inside a navigation guard, so data is ready before the component renders. Not production-ready; API may change.

Features: parallel fetching and deduplication, automatic loading-state management, error handling, extensible loader implementations, SSR support, prefetching support.

## Setup

Install `DataLoaderPlugin` **before the router**:

```ts
import { createApp } from 'vue'
import { routes } from 'vue-router/auto-routes'
import { createRouter, createWebHistory } from 'vue-router'
import { DataLoaderPlugin } from 'vue-router/experimental'

const router = createRouter({ history: createWebHistory(), routes })

const app = createApp({})
app.use(DataLoaderPlugin, { router }) // before the router
app.use(router)
app.mount('#app')
```

## Defining loaders

Loaders are composables returned by a `defineLoader` function. **Define and export** them from the page component (or a loaders module): the loader receives the target location and an `AbortSignal`.

```vue
<!-- src/pages/users/[id].vue -->
<script lang="ts">
import { defineBasicLoader } from 'vue-router/experimental'
import { getUserById } from '../api'

export const useUserData = defineBasicLoader((to, { signal }) => {
  return getUserById(to.params.id, { signal })
}, {
  // used for SSR only
  key: 'user-data',
})
</script>
```

Use the loader in the component like any composable — the data ref is named after the loader (`useUserData` → `user`), plus `error`, `isLoading`, and `reload()`:

```vue
<script lang="ts" setup>
const { user, error, isLoading, reload } = useUserData()
</script>
```

Implementations:

- **Basic loader** — `defineBasicLoader(fn, options?)` from `vue-router/experimental`. Always reruns on navigation.
- **Colada loader** — `defineColadaLoader` from `vue-router/experimental/pinia-colada` (wraps [@pinia/colada](https://github.com/posva/pinia-colada); requires `pinia` + `@pinia/colada`). Deduplicates and caches requests across navigations.

Loader functions may throw errors (error handling is automatic) and may call `reroute()` to control navigation.

## `reroute()` — redirecting from a loader

`reroute()` changes the current navigation from within a data loader. It accepts the same values as a navigation-guard return **that change the navigation** — a location to redirect to, or `false` to cancel. It does not accept `true`/`undefined`. It **throws internally** to stop loader execution immediately. (In 5.5.x, this replaces the removed `new NavigationResult(to)`.)

```ts
import { defineBasicLoader, reroute } from 'vue-router/experimental'

export const useUserData = defineBasicLoader('/users/[id]', async to => {
  const user = await fetchUser(to.params.id)
  if (!user) reroute('/404')
  return user
})

// or cancel the navigation
export const useGuarded = defineBasicLoader('/admin', async () => {
  const session = await getSession()
  if (!session.isAdmin) reroute(false)
})
```

## Nested loaders

When requests depend on other fetched data, import the other loader and **call and `await` it inside** your loader. It is fetched only once no matter how many times it is called during a navigation — the in-loader call returns a Promise of the data, distinct from the composable form used in components:

```ts
export const useUserCommonFriends = defineBasicLoader(async () => {
  const user = await useUserData()   // loaders must be awaited inside loaders
  const me = await getCurrentUser()
  return { ...user, commonFriends: await getCommonFriends(me.id, user.id) }
})
```

Two loaders cannot use each other — that creates a deadlock.

## Cancellation

Loaders receive an `AbortSignal` (second argument); pass it to your fetch to cancel in-flight requests when a new navigation supersedes the current one. `reload()` (returned by the component composable) forces a refetch.

## SSR

Data loaders support SSR — the loader options include a `key` used for SSR state serialization (see `ssr.md` in the docs for the full setup).

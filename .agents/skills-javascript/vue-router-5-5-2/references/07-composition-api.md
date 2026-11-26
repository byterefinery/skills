# Composition API

## useRouter / useRoute

```js
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()  // the router instance (same as this.$router)
const route = useRoute()    // reactive object for the current route
```

`route` is reactive — `route.params.id`, `route.query`, `route.hash`, `route.fullPath`, etc. All update without watchers when navigation completes.

## Component guards

```js
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'

onBeforeRouteLeave(to => {
  // leave guard — return false to cancel
})

onBeforeRouteUpdate(async to => {
  // same component, different params — reload data
})
```

These replace the Options API `beforeRouteLeave`/`beforeRouteUpdate`. `beforeRouteEnter` has no Composition API equivalent — use the experimental data loaders for pre-render data.

## inject() inside navigation guards

Since Vue 3.3, `inject()` works inside `router.beforeEach`, `beforeResolve`, and `afterEach` — anything registered with `app.provide()` (including Pinia stores) is accessible:

```js
router.beforeEach((to, from) => {
  const userStore = useAuthStore() // Pinia store
  if (!userStore.isAuthenticated && to.meta.requiresAuth) return { name: 'Login' }
})
```

## Watching route changes

```js
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

watch(
  () => route.params.id,
  (newId, oldId) => { /* react */ }
)
```

Watch any part of `route` — params, query, hash — to drive side effects that the component's lifecycle cannot observe (the component instance is reused across param-only navigations).

## Options API equivalents

| Composition API | Options API |
|---|---|
| `useRouter()` | `this.$router` |
| `useRoute()` | `this.$route` |
| `onBeforeRouteLeave(fn)` | `beforeRouteLeave(to, from)` |
| `onBeforeRouteUpdate(fn)` | `beforeRouteUpdate(to, from)` |
| `watch(() => route.params.id, ...)` | `this.$watch(() => this.$route.params.id, ...)` |

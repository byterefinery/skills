# Navigation Guards

Guards redirect or cancel navigations. There are three scopes — global, per-route, in-component — plus a strict call order:

`beforeRouteLeave` (leaving component) → global `beforeEach` → `beforeRouteUpdate` (reused component) → `beforeEnter` (route record) → `beforeRouteEnter` (entering component, no `this`) → global `beforeResolve` → `afterEach`.

Return values from any guard (guards may be async):

- `false` — cancel the navigation; the URL is reset to the `from` route.
- A route location (`'/login'`, `{ name: 'Login' }`) — redirect; the current navigation is dropped and a new one starts from the same `from`.
- `undefined` / `true` / nothing — navigation is validated and the next guard runs.
- Thrown `Error` — cancels the navigation and invokes `router.onError()`.

## Global before guards

```js
router.beforeEach((to, from) => {
  if (!isAuthenticated && to.name !== 'Login') return { name: 'Login' }
})
```

`to` and `from` are normalized route locations. Guards are called in creation order; the navigation is **pending** until all hooks resolve.

## Global resolve guards

`router.beforeResolve` triggers on every navigation but runs right before the navigation is confirmed, **after** in-component guards and async components resolve — the ideal place for work you want to avoid if the user cannot enter the page (e.g., asking for camera permission).

## Global after hooks

`router.afterEach` cannot affect navigation; useful for analytics, titles, accessibility announcements. It receives a third `failure` argument:

```js
router.afterEach((to, from, failure) => {
  if (!failure && typeof to.meta.title === 'string') document.title = to.meta.title
})
```

## `next` is deprecated — use returns

Since 5.0.3, declaring or calling `next` logs a deprecation warning in development. Migration:

- `next()` → `return` (or no return)
- `next(false)` → `return false`
- `next('/login')` / `next({ name: 'Login' })` → `return '/login'` / `return { name: 'Login' }`

Remove the `next` parameter itself — as long as a guard declares it, the router expects it to be called exactly once, even if the guard also returns a value. To await callback-based APIs, make the guard `async` and wrap in a Promise.

## Per-route guard (`beforeEnter`)

Defined on the route record; triggers **only when entering the route**, not on param/query/hash changes. Accepts an array of functions for reuse:

```js
const routes = [
  {
    path: '/users/:id',
    component: UserDetails,
    beforeEnter: [removeQueryParams, removeHash],  // or a single function
  },
]
```

On a parent route, `beforeEnter` does not trigger when moving between its children.

## In-component guards

Options API options (not called when `__VUE_OPTIONS_API__` is false):

- `beforeRouteEnter(to, from)` — no `this` (component not created yet). The deprecated `next(vm => ...)` callback gives the instance after the navigation is confirmed.
- `beforeRouteUpdate(to, from)` — component reused with different params; `this` available.
- `beforeRouteLeave(to, from)` — about to leave; `this` available; `return false` cancels (unsaved-changes confirmations).

Composition API equivalents (recommended):

```js
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'

onBeforeRouteLeave(to => {
  const ok = window.confirm('Unsaved changes. Leave?')
  if (!ok) return false
})

onBeforeRouteUpdate(async to => {
  userData.value = await fetchUser(to.params.id)
})
```

For pre-render data fetching in entering components, prefer the experimental [data loaders](13-data-loaders.md) over the deprecated `beforeRouteEnter` + `next` callback pattern.

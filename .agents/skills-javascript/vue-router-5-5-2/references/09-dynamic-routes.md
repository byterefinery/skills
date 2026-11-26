# Dynamic Routing

## Adding routes

```js
router.addRoute({ path: '/about', component: About })
```

`addRoute` **only registers** the route — if the new route matches the current location, you must manually navigate to display it. Use `router.replace(router.currentRoute.value.fullPath)` (instead of `push`, to avoid a duplicate history entry):

```js
router.addRoute({ path: '/about', component: About })
await router.replace(router.currentRoute.value.fullPath)
```

`addRoute()` returns a **dispose function** — call it to remove the route (works for unnamed routes).

## Adding routes inside navigation guards

Do not call `router.replace()` inside a guard — return the new location to trigger a redirection instead:

```js
router.beforeEach(to => {
  if (!hasNecessaryRoute(to)) {
    router.addRoute(generateRoute(to))
    return to.fullPath  // restart navigation against the new route
  }
})
```

`hasNecessaryRoute()` must return `true` after adding the route, or the guard redirects forever. In real-world apps, adding routes more often happens outside guards (e.g., when a view mounts).

## Removing routes

Three ways:

1. **Add a route with the same name** — the existing route is removed first, then the new one added (names are unique across all routes).
2. **Dispose function** — `const remove = router.addRoute(record); remove()`.
3. **`router.removeRoute('name')`** — remove by name. `Symbol`s are valid names if you want to avoid string collisions.

Whenever a route is removed, **all of its aliases and children** are removed with it.

## Adding nested routes

Pass the parent route's **name** as the first argument:

```js
router.addRoute({ name: 'admin', path: '/admin', component: Admin })
router.addRoute('admin', { path: 'settings', component: AdminSettings })
```

Equivalent to declaring the child under the parent's `children`.

## Looking at existing routes

- `router.hasRoute(name)` — check if a route exists.
- `router.getRoutes()` — array of all (normalized) route records.
- `router.clearRoutes()` — remove every route; re-add what you need afterward.

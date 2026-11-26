# Programmatic Navigation

Access the router via `this.$router` (Options API), `useRouter()` (Composition API), or by importing the exported router instance.

## push — new history entry

```js
router.push('/users/eduardo')                          // literal string
router.push({ path: '/users/eduardo' })                // object with path
router.push({ name: 'user', params: { username: 'eduardo' } })  // named + params
router.push({ path: '/register', query: { plan: 'private' } })  // -> /register?plan=private
router.push({ path: '/about', hash: '#team' })         // -> /about#team
```

`<router-link :to="...">` is equivalent to `router.push(...)`. Returns a Promise that resolves when the navigation finishes.

## replace — no new history entry

`router.replace(...)` takes the same argument as `push` but replaces the current history entry. Equivalent to `<router-link :to="..." replace>`.

## params, query, hash rules

- `params` are **ignored** when a `path` is provided. Use `name` + `params`, or build the whole encoded path manually.
- For regular params pass a `string` or `number`; for repeatable params always pass an **array** (even with one item); `[]` or `null` removes an optional repeatable param; `null` removes an optional single param. Other types (objects, booleans) are stringified.
- `query` and `hash` merge into the location freely with `path`.

```js
const username = 'eduardo/san martin'
// manual encoding — encodeURIComponent encodes each segment
router.push(`/user/${encodeURIComponent(username)}`)          // /user/eduardo%2Fsan%20martin
// preferred: named route encodes automatically
router.push({ name: 'user', params: { username } })
// params with path are dropped:
router.push({ path: '/user', params: { username } })         // -> /user
```

The same rules apply to the `to` prop of `<RouterLink>`:

```vue
<RouterLink :to="{ name: 'user', params: { username } }">User</RouterLink>
<RouterLink :to="`/user/${encodeURIComponent(username)}`">User</RouterLink>
```

## go / back / forward

```js
router.go(1)       // step forward
router.go(-1)      // step back
router.back()      // alias for go(-1)
router.forward()   // alias for go(1)
```

## resolve — build the location without navigating

```js
const resolved = router.resolve({ name: 'user', params: { username: 'eduardo' } })
// resolved.path, resolved.params, resolved.query, resolved.href
```

Useful for generating real URLs (e.g., in SSR or for sharing links) without triggering navigation.

## Waiting for navigation to finish

All navigation methods return a Promise. `router.isReady()` resolves when the initial navigation is finished — await it before mounting when the first render must reflect the resolved route (e.g., SSR).

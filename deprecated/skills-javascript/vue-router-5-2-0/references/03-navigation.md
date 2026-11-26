# Navigation

## Programmatic navigation

### `router.push()`

Navigate to a new route, adding a history entry:

```js
// String path
router.push('/users/42')

// Object with path
router.push({ path: '/users/42' })

// Named route with params
router.push({ name: 'user', params: { id: '42' } })

// With query
router.push({ path: '/search', query: { q: 'vue router' } })

// With hash
router.push({ path: '/guide', hash: '#installation' })

// With all options
router.push({
  name: 'user',
  params: { id: '42' },
  query: { tab: 'profile' },
  hash: '#info',
})
```

### `router.replace()`

Navigate without adding a history entry (replaces current entry):

```js
router.replace('/dashboard')
router.replace({ name: 'home' })
```

### `router.go()`, `router.back()`, `router.forward()`

Traverse history:

```js
router.go(-1)   // equivalent to router.back()
router.go(1)    // equivalent to router.forward()
router.go(-2)   // go back two entries
```

## Navigation location formats

### String

```js
router.push('/users/42?tab=profile#info')
```

### Path object

```js
router.push({ path: '/users/42', query: { tab: 'profile' }, hash: '#info' })
```

When using `path`, `params` are ignored.

### Named route object

```js
router.push({ name: 'user', params: { id: '42' } })
```

When using `name`, `path` is ignored and the path is resolved from the route record.

### Relative navigation

Named routes can navigate relative to the current route's params:

```js
// At /users/42/posts
router.push({ name: 'comment', params: { commentId: '1' } })
// Resolves to /users/42/posts/1 (merges with parent params)
```

## Extra navigation options

### `replace`

Replace instead of push:

```js
router.push({ path: '/home', replace: true })
```

### `force`

Trigger navigation even to the same location:

```js
router.push({ path: '/current', force: true })
```

This runs guards and triggers reactivity even when the URL is unchanged.

### `state`

Attach HTML5 history state:

```js
router.push({
  path: '/checkout',
  state: { cartId: 'abc123', step: 2 },
})
```

State is accessible via `history.state` and is restored on back/forward navigation. Values must be structured-cloneable (no functions, Symbols, etc.).

## `router.resolve()`

Resolve a location without navigating. Returns a `RouteLocationResolved` with `href`, `route`, `normalizedTo`:

```js
const resolved = router.resolve('/users/42')
console.log(resolved.href)       // Full URL string
console.log(resolved.route.name) // Route name
console.log(resolved.route.params) // { id: '42' }
```

Use for generating external links:

```vue
<a :href="router.resolve('/users/42').href" target="_blank">
  Open in new tab
</a>
```

## `router.getRoutes()`

Get all registered route records:

```js
const allRoutes = router.getRoutes()
// Returns array of normalized route records
```

## `router.hasRoute()`

Check if a named route exists:

```js
if (router.hasRoute('admin')) {
  router.push({ name: 'admin' })
}
```

## Handling navigation results

`router.push()` and `router.replace()` return Promises:

```js
router.push('/home').catch((err) => {
  if (isNavigationFailure(err, NavigationFailureType.duplicated)) {
    // Already at this route — often safe to ignore
    return
  }
  console.error('Navigation failed:', err)
})
```

### Navigation failure types

```js
import { isNavigationFailure, NavigationFailureType } from 'vue-router'

router.push('/path').catch((err) => {
  if (isNavigationFailure(err, NavigationFailureType.aborted)) {
    // A guard returned false
  }
  if (isNavigationFailure(err, NavigationFailureType.cancelled)) {
    // A newer navigation replaced this one
  }
  if (isNavigationFailure(err, NavigationFailureType.duplicated)) {
    // Already at the same location
  }
})
```

## Current route

Access the reactive current route:

```js
// In components (Options API)
this.$route.path
this.$route.params.id
this.$route.query.tab

// In composition API
import { useRoute } from 'vue-router'
const route = useRoute()
route.path
route.params.id
route.query.tab
```

The route object properties:

| Property | Type | Description |
|---|---|---|
| `path` | `string` | Decoded path, always starts with `/` |
| `params` | `object` | Key-value pairs from dynamic segments |
| `query` | `object` | Parsed query string as object |
| `hash` | `string` | Hash including `#`, decoded |
| `fullPath` | `string` | Full encoded URL (path + query + hash) |
| `name` | `string` | Name of the matched route |
| `matched` | `RouteRecord[]` | Array of all matched route records |
| `meta` | `RouteMeta` | Merged meta from all matched records |
| `redirectedFrom` | `RouteLocation` | Location we were redirected from, if any |

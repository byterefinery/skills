# Error Handling

## Navigation failures

`router.push()` and `router.replace()` return Promises that reject with a `NavigationFailure` when navigation is aborted, cancelled, or duplicated.

```js
router.push('/path').catch((err) => {
  // Handle navigation failure
})
```

## Failure types

```js
import { isNavigationFailure, NavigationFailureType } from 'vue-router'
```

| Type | Value | Cause |
|---|---|---|
| `aborted` | Navigation guard returned `false` | Explicit rejection by a guard |
| `cancelled` | A newer navigation started | Superseded by another navigation |
| `duplicated` | Already at the same location | Pushing to current route |

## Checking failure type

```js
router.push('/path').catch((err) => {
  // Any navigation failure
  if (isNavigationFailure(err)) {
    console.log('Navigation failed:', err.message)
  }

  // Specific type
  if (isNavigationFailure(err, NavigationFailureType.duplicated)) {
    // Already here — safe to ignore
    return
  }

  // Multiple types
  if (isNavigationFailure(err, NavigationFailureType.aborted | NavigationFailureType.cancelled)) {
    console.log('Navigation was aborted or cancelled')
  }
})
```

## Ignoring duplicated navigations

The most common pattern — silently ignore when already at the target:

```js
async function navigateTo(path) {
  try {
    await router.push(path)
  } catch (err) {
    if (!isNavigationFailure(err, NavigationFailureType.duplicated)) {
      throw err
    }
  }
}
```

## Global error handler

Register a handler for uncaught navigation errors:

```js
router.onError((error, to, from) => {
  if (isNavigationFailure(error, NavigationFailureType.duplicated)) {
    return // Ignore duplicated
  }
  console.error('Navigation error:', error)
})
```

Errors not handled by `onError` are logged to the console.

## Matcher errors

When a location cannot be matched to any route, a `MatcherError` is thrown:

```js
import { isNavigationFailure } from 'vue-router'

router.onError((error, to, from) => {
  if (error.type === 1) { // ErrorTypes.MATCHER_NOT_FOUND
    console.error('No match for:', error.location)
  }
})
```

## Handling errors in guards

Guards can throw errors or return errors:

```js
router.beforeEach((to, from) => {
  try {
    const user = checkAuth()
    if (!user && to.meta.requiresAuth) {
      return { name: 'login' }
    }
  } catch (err) {
    // Error in guard — navigation is cancelled
    throw err
  }
})
```

## Async component loading errors

When a lazy-loaded component fails to load:

```js
// Route with error handling
{
  path: '/heavy',
  component: () =>
    import('./HeavyPage.vue').catch(() =>
      import('./ErrorPage.vue')
    ),
}
```

Or handle at the router level:

```js
router.onError((error) => {
  if (error.message && error.message.includes('Failed to fetch')) {
    // Network error loading a chunk
    router.replace('/error/network')
  }
})
```

## Error types reference

Internal error types (bit flags):

```js
const ErrorTypes = {
  MATCHER_NOT_FOUND: 1,
  NAVIGATION_GUARD_REDIRECT: 2,
  NAVIGATION_ABORTED: 4,
  NAVIGATION_CANCELLED: 8,
  NAVIGATION_DUPLICATED: 16,
}
```

These can be combined with bitwise OR for `isNavigationFailure`:

```js
isNavigationFailure(err, ErrorTypes.NAVIGATION_ABORTED | ErrorTypes.NAVIGATION_CANCELLED)
```

## Navigation redirect errors

Redirects in guards produce a `NavigationRedirectError` internally. These are handled automatically by the router — they trigger a new navigation to the redirect target. You typically don't need to handle these directly.

## Error flow

1. Guard throws error or returns error → navigation cancelled
2. Error propagates to the Promise returned by `router.push()`
3. `router.onError()` handlers are called
4. If no handler catches it, error is logged to console
5. Router is marked as ready (errors don't block readiness)

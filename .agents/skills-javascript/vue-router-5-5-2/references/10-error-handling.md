# Navigation Failures and Error Handling

`router.push()` and `router.replace()` return a Promise that resolves to `undefined` on success or to a **NavigationFailure** object on failure — they do not reject for guarded cancellations, so catch the resolved value:

```js
const failure = await router.push({ name: 'post', params: { id: 1 } }).catch(err => err)
if (isNavigationFailure(failure, NavigationFailureType.duplicated)) {
  return  // navigating to the same location — safe to ignore
}
```

`isNavigationFailure(value, type?)` checks whether a value is a navigation failure; optionally narrow to a type. Types can be combined with `|`:

```js
// from router.afterEach's third argument
router.afterEach((to, from, failure) => {
  if (isNavigationFailure(failure)) { /* any failure */ }
  if (isNavigationFailure(failure, NavigationFailureType.duplicated)) { /* duplicated */ }
  if (isNavigationFailure(failure, NavigationFailureType.aborted | NavigationFailureType.cancelled)) { /* aborted or cancelled */ }
})
```

## Failure types (`NavigationFailureType`)

- `aborted` — a navigation guard returned `false` (or `next(false)`), failing the navigation.
- `cancelled` — a more recent navigation started, so this one was dropped.
- `duplicated` — navigation was initiated while already at the exact same location.

A failure object carries `type` (one of the above), `from` (normalized location being left), and `to` (normalized location being navigated to).

## Global navigation failures

`router.onError(callback)` receives every error that **causes** a navigation failure — errors thrown in guards, in async components, etc. Callback signature: `(error, to, from)`.

```js
router.onError((error, to, from) => {
  // crash reporting, or handling failed chunk imports after a deploy
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    location.reload()
  }
})
```

Note the difference: a guard that **returns `false`** cancels silently (no `onError`); a guard that **throws** an `Error` cancels the navigation **and** triggers `onError`. Use thrown errors for unexpected situations.

## Detecting redirections

A redirect does not fail the original navigation — it starts a new one. Detect it with the `redirectedFrom` property on the current route location after the navigation settles:

```js
await router.push('/my-profile')
if (router.currentRoute.value.redirectedFrom) {
  // redirectedFrom is a resolved route location, like `to`/`from` in guards
}
```

## Errors in async components

Failed dynamic imports (e.g., stale chunk names after a deploy) surface through the navigation Promise and `onError`. A common recovery is to reload the page when the error message indicates a missing dynamic module.

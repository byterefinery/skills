# Navigation Guards

## Guard lifecycle

Navigations trigger guards in this strict order:

1. **Navigation triggered** — user clicks a link or calls `router.push()`
2. **`beforeRouteLeave`** — in the component being left
3. **Global `beforeEach`** — application-level guards
4. **`beforeRouteUpdate`** — in the component being reused (e.g., same component, different params)
5. **`beforeEnter`** — on the route record being entered
6. **Lazy loading** — components are resolved (dynamic imports)
7. **`beforeRouteEnter`** — in the component being entered
8. **Global `beforeResolve`** — called before navigation is confirmed
9. **Navigation confirmed** — all guards passed
10. **`afterEach`** — hooks called after navigation

At any point, a guard can:
- **Allow**: return a truthy value (or nothing)
- **Abort**: return `false`
- **Redirect**: return a route location (string or object)
- **Throw an error**: reject the navigation

## Global guards

### `beforeEach`

Called before every navigation. Runs in registration order:

```js
router.beforeEach((to, from) => {
  // Auth check
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // Set document title
  document.title = to.meta.title ? `${to.meta.title} - App` : 'App'
})
```

### `beforeResolve`

Called after all component-level guards and before navigation confirmation. Useful for logic that needs all components resolved:

```js
router.beforeResolve((to, from) => {
  // Analytics — fire after all guards pass
  trackPageView(to.fullPath)
})
```

### `afterEach`

Called after navigation is confirmed. Cannot change the navigation:

```js
router.afterEach((to, from, failure) => {
  if (failure) {
    console.warn('Navigation failed:', failure.message)
    return
  }
  // Log successful navigation
  console.log(`Navigated to ${to.fullPath}`)
})
```

## Per-route guards

### `beforeEnter`

Defined on the route record. Runs before component guards:

```js
{
  path: '/admin',
  component: Admin,
  beforeEnter: (to, from) => {
    if (!isAdmin()) {
      return { name: 'forbidden' }
    }
  },
}
```

Multiple `beforeEnter` guards:

```js
{
  path: '/admin',
  component: Admin,
  beforeEnter: [checkAuth, checkRole],
}
```

Note: `beforeEnter` is skipped if the route has a `redirect`.

## Component-level guards

### `beforeRouteLeave`

Guard the component being left. `this` refers to the component instance:

```js
export default {
  beforeRouteLeave(to, from) {
    if (this.unsavedChanges) {
      return confirm('You have unsaved changes. Leave anyway?')
    }
  },
}
```

### `beforeRouteUpdate`

Guard when the route changes but the component is reused (e.g., `/users/1` → `/users/2`):

```js
export default {
  beforeRouteUpdate(to, from) {
    // Reset form when switching users
    this.resetForm()
  },
}
```

### `beforeRouteEnter`

Guard before the component is created. `this` is `undefined` — access the instance via `next`:

```js
export default {
  beforeRouteEnter(to, from, next) {
    // Cannot access `this` here
    fetchUser(to.params.id).then(user => {
      next(vm => {
        // vm is the component instance
        vm.user = user
      })
    }).catch(err => {
      next({ name: 'not-found' })
    })
  },
}
```

## Guard return values

| Return | Effect |
|---|---|
| (nothing / `undefined`) | Navigation proceeds |
| `true` | Navigation proceeds |
| `false` | Navigation aborted |
| `'/path'` | Redirect to path |
| `{ name: 'home' }` | Redirect to named route |
| `Promise` that resolves to above | Async resolution |
| `throw error` / `return new Error()` | Navigation cancelled with error |

## Async guards

Guards can be async functions or return Promises:

```js
router.beforeEach(async (to, from) => {
  const user = await fetchCurrentUser()
  if (to.meta.requiresRole && !user.roles.includes(to.meta.requiresRole)) {
    return { name: 'forbidden' }
  }
})
```

The navigation waits for the Promise to resolve. A newer navigation cancels pending guards automatically.

## Composition API guards

Use `onBeforeRouteLeave` and `onBeforeRouteUpdate` in setup:

```js
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'

export default {
  setup() {
    onBeforeRouteLeave((to, from) => {
      if (hasUnsavedChanges.value) {
        return confirm('Leave with unsaved changes?')
      }
    })

    onBeforeRouteUpdate((to, from) => {
      // Reset state for new route params
      formData.value = getDefaultForm()
    })
  },
}
```

Guards registered with composition API are automatically removed when the component is unmounted.

## Guard parameters

Every guard receives:

| Parameter | Type | Description |
|---|---|---|
| `to` | `RouteLocationNormalized` | Target route location |
| `from` | `RouteLocationNormalizedLoaded` | Current route location |
| `next` | `NavigationGuardNext` | Legacy callback (deprecated, use return values instead) |

The `next` callback is deprecated. Return values replace it:

```js
// Old style (still works but deprecated)
beforeEach((to, from, next) => {
  next(true)    // allow
  next(false)   // abort
  next('/path') // redirect
})

// New style (preferred)
beforeEach((to, from) => {
  return true    // allow
  return false   // abort
  return '/path' // redirect
})
```

## Detecting initial navigation

Use `START_LOCATION` to detect the first page load:

```js
import { START_LOCATION } from 'vue-router'

router.beforeEach((to, from) => {
  if (from === START_LOCATION) {
    // This is the initial navigation (page load)
    // e.g., restore session, check auth token
  }
})
```

## Common patterns

### Auth guard with redirect

```js
router.beforeEach((to) => {
  const isAuthenticated = !!localStorage.getItem('token')

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'login' && isAuthenticated) {
    return { name: 'dashboard' }
  }
})
```

### Redirect after login

```js
// In login component
async function login(credentials) {
  await auth.login(credentials)
  const redirect = route.query.redirect || '/dashboard'
  router.replace(redirect)
}
```

### Unsaved changes guard

```js
export default {
  data() {
    return { form: {}, hasChanges: false }
  },
  watch: {
    form: {
      deep: true,
      handler() {
        this.hasChanges = !isEqual(this.form, this.originalForm)
      },
    },
  },
  beforeRouteLeave(to, from) {
    if (this.hasChanges) {
      return confirm('You have unsaved changes. Discard them?')
    }
  },
}
```

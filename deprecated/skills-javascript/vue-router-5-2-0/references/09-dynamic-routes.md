# Dynamic Routes

## Adding routes at runtime

Add new route records after the router is created:

```js
// Add a top-level route
const removeRoute = router.addRoute({
  name: 'admin',
  path: '/admin',
  component: AdminPanel,
})

// Add as child of an existing named route
router.addRoute('settings', {
  path: 'danger-zone',
  component: DangerZone,
})
// Creates /settings/danger-zone as a child of 'settings'
```

### Remove function

`addRoute` returns a function to remove the added route:

```js
const removeAdmin = router.addRoute({
  name: 'admin',
  path: '/admin',
  component: AdminPanel,
})

// Later, when user logs out:
removeAdmin()
```

## Removing routes

Remove by name:

```js
router.removeRoute('admin')
```

Remove all routes:

```js
router.clearRoutes()
```

## Checking route existence

```js
if (router.hasRoute('admin')) {
  // Route exists
}
```

## Listing all routes

```js
const routes = router.getRoutes()
// Returns array of normalized route records
```

## Common patterns

### Role-based routes

Add routes after authentication based on user role:

```js
async function setupRoutes(user) {
  if (user.role === 'admin') {
    router.addRoute({
      name: 'admin',
      path: '/admin',
      component: () => import('./AdminPanel.vue'),
      children: [
        { path: 'users', component: () => import('./AdminUsers.vue') },
        { path: 'settings', component: () => import('./AdminSettings.vue') },
      ],
    })
  }

  if (user.role === 'editor') {
    router.addRoute({
      name: 'editor',
      path: '/editor',
      component: () => import('./EditorPanel.vue'),
    })
  }

  // Navigate after routes are ready
  await router.isReady()
  router.push(user.lastPath || '/')
}
```

### Feature flags

Conditionally add routes based on feature flags:

```js
const features = await fetchFeatureFlags()

if (features.betaDashboard) {
  router.addRoute({
    path: '/beta-dashboard',
    component: BetaDashboard,
    meta: { beta: true },
  })
}
```

### Plugin routes

Allow plugins to contribute routes:

```js
// Plugin
export function installMyPlugin(router) {
  router.addRoute({
    path: '/my-plugin',
    component: MyPluginView,
  })
}

// App setup
import { installMyPlugin } from 'my-plugin'
installMyPlugin(router)
```

### Temporary routes

Add and remove routes for temporary workflows:

```js
// Wizard flow
const removeWizard = router.addRoute({
  path: '/wizard',
  component: WizardLayout,
  children: [
    { path: 'step-1', component: Step1 },
    { path: 'step-2', component: Step2 },
    { path: 'complete', component: Complete },
  ],
})

// After wizard completes
removeWizard()
router.push('/dashboard')
```

## Dynamic routes and navigation guards

Guards apply to dynamically added routes just like static routes:

```js
router.addRoute({
  name: 'premium',
  path: '/premium',
  component: PremiumFeature,
  beforeEnter: (to, from) => {
    if (!user.hasPremium) {
      return { name: 'upgrade' }
    }
  },
})
```

## Replacing routes

Remove and re-add to replace a route:

```js
router.removeRoute('dashboard')
router.addRoute({
  name: 'dashboard',
  path: '/dashboard',
  component: NewDashboard,
})
```

## Routes and SSR

Dynamically added routes are not available on the server unless added before rendering. For SSR, add all routes before creating the app:

```js
// Server entry
const serverRouter = createRouter({
  history: createMemoryHistory(),
  routes: getStaticRoutes(),
})

// Add dynamic routes before rendering
addDynamicRoutes(serverRouter, user)
await serverRouter.push(req.url)
await serverRouter.isReady()
```

## Watching route changes

Monitor when routes are added or removed:

```js
watch(
  () => router.getRoutes().length,
  (newCount, oldCount) => {
    console.log(`Routes changed: ${oldCount} → ${newCount}`)
  }
)
```

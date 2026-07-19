# Advanced Patterns

## History state

Pass structured data through the HTML5 history API:

```js
router.push({
  path: '/checkout',
  state: { cartId: 'abc123', step: 2 },
})
```

Access state from history:

```js
const state = history.state
// { cartId: 'abc123', step: 2, scroll: ..., back: ..., current: ..., forward: ..., position: ... }
```

State values must be structured-cloneable — no functions, Symbols, or class instances. State is preserved across back/forward navigation and page reloads.

## Force navigation

Trigger navigation to the same route, running all guards:

```js
router.push({ path: '/current', force: true })
```

Useful for forcing a page refresh or re-running guards:

```js
// Force re-auth check
router.push({ ...route.fullPath, force: true })
```

## View transitions

Use the CSS View Transitions API for animated route changes:

```vue
<RouterLink to="/about" view-transition>
  About
</RouterLink>
```

Or programmatically:

```js
if ('startViewTransition' in document) {
  document.startViewTransition(() => router.push('/about'))
} else {
  router.push('/about')
}
```

## Custom query parsing

Provide custom `parseQuery` and `stringifyQuery` functions:

```js
import qs from 'qs'

const router = createRouter({
  history: createWebHistory(),
  routes,
  parseQuery: (search) => qs.parse(search),
  stringifyQuery: (query) => qs.stringify(query),
})
```

This enables nested query objects and custom encoding.

## Redirect with preserved query/hash

Redirects automatically preserve query and hash:

```js
{
  path: '/old-path',
  redirect: { name: 'new-path' },
}
// /old-path?tab=profile#info → /new-path?tab=profile#info
```

Override by specifying query/hash in the redirect target:

```js
{
  path: '/old',
  redirect: { name: 'new', query: { forced: 'true' } },
}
```

## Passthrough routes

Routes with no component but with children — the parent passes through to its children:

```js
{
  path: '/admin',
  // No component — acts as a namespace
  beforeEnter: checkAdmin,
  children: [
    { path: '', redirect: 'users' },
    { path: 'users', component: AdminUsers },
    { path: 'settings', component: AdminSettings },
  ],
}
```

## Route-level beforeEnter arrays

Multiple guards on a single route:

```js
{
  path: '/admin',
  component: Admin,
  beforeEnter: [checkAuth, checkRole, checkMfa],
}
```

Guards run sequentially. Any guard returning `false` or a redirect stops the chain.

## Conditional routes

Build route arrays conditionally:

```js
const routes = [
  { path: '/', component: Home },
  ...userIsAdmin ? [
    { path: '/admin', component: Admin },
  ] : [],
  { path: '/:pathMatch(.*)*', component: NotFound },
]
```

## Route grouping with redirects

Create a parent route that redirects to a default child:

```js
{
  path: '/account',
  redirect: '/account/profile',
  children: [
    { path: 'profile', component: Profile },
    { path: 'settings', component: Settings },
    { path: 'billing', component: Billing },
  ],
}
```

## External links from router

Generate proper hrefs for external links:

```js
const resolved = router.resolve({ name: 'user', params: { id: 42 } })

// In template
<a :href="resolved.href" target="_blank">Open profile</a>

// Share URL
navigator.share({ url: window.origin + resolved.href })
```

## Router-ready callback

Wait for the router to finish initial navigation:

```js
router.isReady().then(() => {
  // Initial navigation complete
  // Safe to read router.currentRoute.value
  console.log('Current route:', router.currentRoute.value.fullPath)
}).catch((err) => {
  // Initial navigation failed
  console.error('Router failed to start:', err)
})
```

## Multiple apps with one router

Share a router between multiple Vue apps:

```js
const router = createRouter({ /* ... */ })

const app1 = createApp(Component1)
const app2 = createApp(Component2)

app1.use(router)
app2.use(router)

app1.mount('#app1')
app2.mount('#app2')
```

The router cleans up when all apps are unmounted.

## Testing with memory history

```js
import { createRouter, createMemoryHistory } from 'vue-router'
import { mount } from '@vue/test-utils'

const router = createRouter({
  history: createMemoryHistory('/initial'),
  routes,
})

const wrapper = mount(App, { global: { plugins: [router] } })

await router.push('/test-route')
await wrapper.vm.$nextTick()

expect(router.currentRoute.value.path).toBe('/test-route')
```

## Route metadata for layout

Use meta to control which layout wraps a route:

```js
const routes = [
  {
    path: '/',
    component: () => import('./layouts/AuthLayout.vue'),
    children: [
      { path: 'login', component: Login },
      { path: 'register', component: Register },
    ],
  },
  {
    path: '/',
    component: () => import('./layouts/AppLayout.vue'),
    children: [
      { path: 'dashboard', component: Dashboard },
      { path: 'profile', component: Profile },
    ],
  },
]
```

## Catch-all with typed params

```js
{
  path: '/:pathMatch(.*)*',
  component: NotFound,
}

// In component
const route = useRoute()
// route.params.pathMatch is a string (or string array for repeated segments)
```

## Encoding and decoding

The router handles URL encoding automatically. Manual encoding/decoding:

```js
import { parseQuery, stringifyQuery } from 'vue-router'

const query = parseQuery('foo=bar&baz=qux')
// { foo: 'bar', baz: 'qux' }

const search = stringifyQuery({ foo: 'bar', baz: 'qux' })
// 'foo=bar&baz=qux'
```

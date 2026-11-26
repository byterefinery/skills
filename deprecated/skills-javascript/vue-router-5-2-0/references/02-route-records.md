# Route Records

## Basic route record

A route record maps a URL path to a component:

```js
const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About },
]
```

## Route record options

| Option | Type | Description |
|---|---|---|
| `path` | `string` | URL pattern. Must start with `/` for top-level routes |
| `name` | `string` | Unique name for named route navigation |
| `component` | `Component \| () => Promise` | Component to render (lazy loading via function) |
| `components` | `Record<string, Component>` | Named views — multiple components at one route |
| `redirect` | `string \| object \| function` | Redirect matched navigation to another location |
| `alias` | `string \| string[]` | Alternate paths that behave identically to the route |
| `children` | `RouteRecordRaw[]` | Nested routes rendered in child `<RouterView>` |
| `props` | `boolean \| object \| function` | Pass route params as component props |
| `beforeEnter` | `NavigationGuard \| NavigationGuard[]` | Per-route guard (skipped if `redirect` is set) |
| `meta` | `RouteMeta` | Arbitrary metadata attached to the record |

## Dynamic segments

Colon prefix marks a dynamic segment captured as a param:

```js
{ path: '/users/:id', component: User }
// /users/42 → route.params.id === '42'
```

Multiple segments:

```js
{ path: '/posts/:postId/comments/:commentId', component: Comment }
```

### Modifiers

- `:id?` — optional param (matches with or without the segment)
- `:id*` — zero or more repeats
- `:id+` — one or more repeats

```js
{ path: '/users/:id?', component: User }
// /users → params.id is empty
// /users/42 → params.id === '42'
```

### Catch-all routes

Three dots match any remaining path:

```js
{ path: '/:pathMatch(.*)*', component: NotFound }
// Access via route.params.pathMatch
```

Without the regex constraint, `(.*)` is implied:

```js
{ path: '/:catchAll(.*)', component: NotFound }
```

## Named routes

Name a route for reference in navigation:

```js
{ name: 'user', path: '/users/:id', component: User }
```

Navigate by name:

```js
router.push({ name: 'user', params: { id: '42' } })
```

Named routes in templates:

```vue
<RouterLink :to="{ name: 'user', params: { id: 42 } }">User 42</RouterLink>
```

## Nested routes

Children render in nested `<RouterView>` components. Child paths that start with `/` are treated as root paths; children without leading `/` are relative to the parent:

```js
const routes = [
  {
    path: '/settings',
    component: SettingsLayout,
    children: [
      { path: '', component: SettingsGeneral },     // /settings
      { path: 'profile', component: SettingsProfile }, // /settings/profile
      { path: 'security', component: SettingsSecurity }, // /settings/security
    ],
  },
]
```

Template with nested views:

```vue
<template>
  <div class="settings-layout">
    <aside>
      <RouterLink to="/settings">General</RouterLink>
      <RouterLink to="/settings/profile">Profile</RouterLink>
      <RouterLink to="/settings/security">Security</RouterLink>
    </aside>
    <RouterView />
  </div>
</template>
```

### Empty child path

Use `path: ''` for the default child that renders at the parent's URL:

```js
{
  path: '/account',
  component: AccountLayout,
  children: [
    { path: '', component: AccountOverview },
    { path: 'billing', component: AccountBilling },
  ],
}
// /account → AccountLayout + AccountOverview
// /account/billing → AccountLayout + AccountBilling
```

## Redirects

### String redirect

```js
{ path: '/users', redirect: '/' }
```

### Object redirect

```js
{ path: '/users', redirect: { name: 'home' } }
{ path: '/users', redirect: { path: '/dashboard' } }
```

### Function redirect

Receive the target route location and return a new location:

```js
{
  path: '/users/:id',
  redirect: (to) => ({
    name: 'user-profile',
    params: { id: to.params.id },
  }),
}
```

Query and hash are preserved automatically during redirects.

## Aliases

Aliases create alternate paths for the same route. The original path and all aliases behave identically:

```js
{
  path: '/users/:id',
  alias: '/u/:id',
  component: User,
}
// /users/42 and /u/42 both render User with params.id === '42'
```

Multiple aliases:

```js
{
  path: '/users/:id',
  alias: ['/u/:id', '/profile/:id'],
  component: User,
}
```

Alias arrays must share the same param structure as the path.

## Props

Pass route params as component props instead of reading `$route.params`:

### Boolean (params as props)

```js
{ path: '/users/:id', component: User, props: true }
// User receives props: { id: '42' }
```

### Static object

```js
{ path: '/help', component: Help, props: { showSearch: true } }
```

### Function

```js
{
  path: '/users/:id',
  component: User,
  props: (route) => ({
    userId: route.params.id,
    fromRoute: true,
  }),
}
```

### Named views

```js
{
  path: '/dashboard',
  components: { default: DashboardMain, sidebar: DashboardSidebar },
  props: { default: true, sidebar: { expanded: false } },
}
```

## Meta fields

Attach arbitrary data to route records. Augment the `RouteMeta` interface for TypeScript:

```js
// Route record
{
  path: '/admin',
  component: Admin,
  meta: { requiresAuth: true, roles: ['admin'] },
}

// Access in guards
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: 'login' }
  }
})
```

TypeScript augmentation:

```ts
// typings.d.ts
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: string[]
    title?: string
  }
}
```

## Lazy loading components

Use a function returning a dynamic import for code splitting:

```js
{
  path: '/heavy-page',
  component: () => import('./HeavyPage.vue'),
}
```

The router starts the import during the guard pipeline and replaces the function with the resolved component. Never pass the import call directly — it must be wrapped in a function:

```js
// Wrong — fires import immediately at route definition time
{ path: '/page', component: import('./Page.vue') }

// Correct — lazy loads on first navigation
{ path: '/page', component: () => import('./Page.vue') }
```

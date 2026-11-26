# Route Records

## Basic configuration

```js
const routes = [
  { path: '/', component: HomeView },
  { path: '/about', component: AboutView },
  { path: '/users/:id', component: User },
]
```

`path` + `component` are the minimum. The `component` option is what `<RouterView>` renders.

## Dynamic segments (params)

A param is denoted by a colon: `/users/:id`. Matched values appear in `route.params`:

| pattern | matched path | route.params |
|---|---|---|
| `/users/:username` | `/users/eduardo` | `{ username: 'eduardo' }` |
| `/users/:username/posts/:postId` | `/users/eduardo/posts/123` | `{ username: 'eduardo', postId: '123' }` |

The default param regex is `([^/]+)` — at least one non-slash character.

## Catch-all / 404

Match anything including slashes with a custom regex + repeatable modifier:

```js
// matches any path, stored in route.params.pathMatch
{ path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
```

When navigating to the named catch-all from the current path, split into segments:

```js
router.push({
  name: 'NotFound',
  params: { pathMatch: route.path.substring(1).split('/') },
  query: route.query,
  hash: route.hash,
})
```

`pathMatch` is a convention; any descriptive name works.

## Advanced matching syntax

Custom regex in a param — escape backslashes in JS strings:

```js
{ path: '/:orderId(\\d+)' }      // matches only numbers
{ path: '/:productName' }         // matches anything else
```

The order of the `routes` array no longer matters — specificity wins. Nested regex groups must be non-capturing (`(?:...)`) and escape the closing paren.

Repeatable params (0 or more / 1 or more) yield **arrays**:

```js
{ path: '/:chapters+' }   // matches /one, /one/two, ...
{ path: '/:chapters*' }   // also matches /
{ path: '/:chapters(\\d+)+' }  // combine with custom regex
```

Optional params with `?` (0 or 1):

```js
{ path: '/users/:userId?' }   // matches /users and /users/posva
{ path: '/users/:userId(\\d+)?' }
```

A segment containing more than just an optional param does not match without the trailing slash: `/users/:uid?-:name?` does not match `/users`.

Case and trailing-slash sensitivity — settable at router or route level:

```js
const router = createRouter({
  history: createWebHistory(),
  strict: true,     // /users/posva/ no longer matches
  routes: [
    { path: '/users/:id', sensitive: true },  // /Users/posva no longer matches
  ],
})
```

Debugging: the [path ranker tool](https://paths.esm.dev) shows how routes transform into regexes and supports sharing via URL.

## Named routes

```js
const routes = [
  { path: '/users/:id', component: User, name: 'user' },
  { path: '/users', component: Users, name: 'users' },
  // nested: name the child, not the parent
  {
    path: '/user/:id',
    component: User,
    children: [{ path: '', name: 'user', component: UserHome }],
  },
]

router.push({ name: 'user', params: { id: 'eduardo' } })
```

Named routes avoid manually building and encoding URLs.

## Nested routes

Use `children` to nest components; a rendered component can contain its own `<router-view>`:

```js
const routes = [
  {
    path: '/user/:id',
    component: User,
    children: [
      { path: 'profile', component: UserProfile },   // inside User's <router-view>
      { path: 'posts', component: UserPosts },
      { path: '', component: UserHome },            // renders for /user/:id itself
    ],
  },
]
```

- Nested paths starting with `/` are treated as root paths (component nesting without URL nesting).
- `children` is recursive — nest as deep as needed.
- Omitting the parent `component`/`components` groups children under a common path prefix or for shared `beforeEnter`/`meta`; `<router-view>` skips the parent and renders the child directly.

## Redirects

```js
{ path: '/home', redirect: '/' }
{ path: '/home', redirect: { name: 'homepage' } }
{
  path: '/search/:searchText',
  redirect: to => ({ path: '/search', query: { q: to.params.searchText } }),
}
```

- Navigation guards are not applied on the redirecting route, only its target.
- `component` can be omitted on redirect-only routes, **except** when the record also has `children` (then it needs a component).
- Relative redirects are allowed in the stable router; in the experimental router a record `redirect` must return a named location or an absolute path (copy params/query/hash from `to` to keep them).

## Aliases

An alias keeps the user's URL but matches as another path:

```js
// visiting /home matches the "/" record, URL stays /home
{ path: '/', component: Homepage, alias: '/home' }
// multiple aliases via array; relative ones inherit the parent path
{ path: 'list', component: UserList, alias: ['/people', 'list'] }
```

Include params in absolute aliases (`alias: '/:id'`). Define canonical links for SEO when using aliases.

## Meta fields

Any custom data goes in `meta` (merged from parent to child; child wins):

```js
const routes = [
  { path: '/', component: Home, meta: { title: 'Home', requiresAuth: true } },
  { path: '/about', component: About, meta: { title: 'About' } },
]

// in a guard
router.beforeEach(to => {
  if (to.meta.requiresAuth && !isAuthenticated()) return { name: 'Login' }
})
```

Update `document.title` from `afterEach` using `to.meta.title`. Augment the `RouteMeta` TypeScript interface with your fields (see 03-navigation and the typed routes docs).

## Lazy loading

```js
const routes = [
  { path: '/users/:id', component: () => import('./views/User.vue') },
]
```

The component must be a function returning a Promise; the router starts the import during guard resolution and replaces the function with the resolved component.

Group nested route components into one chunk: with Vite, list the modules under `build.rollupOptions.output.manualChunks`; with webpack, use `import(/* webpackChunkName: "group-user" */ './UserDetails.vue')` so same-named modules share an async chunk.

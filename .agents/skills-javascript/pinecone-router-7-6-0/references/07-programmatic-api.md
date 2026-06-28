# Programmatic API

## PineconeRouter Object

Access the router from multiple contexts:

| Context | Access |
|---|---|
| Alpine magic helper | `$router` |
| Alpine global | `Alpine.$router` |
| Global JS | `window.PineconeRouter` or `PineconeRouter` |
| ES module import | `import PineconeRouter from 'pinecone-router'` |

## Object Reference

```ts
interface PineconeRouter {
  readonly name: string        // "pinecone-router"
  readonly version: string     // "7.6.0"

  routes: RoutesMap            // Map of registered routes
  context: Context             // Current route context
  settings: (value?: Partial<Settings>) => Settings
  history: NavigationHistory

  loading: boolean             // True while templates are rendering

  add(path: string, options: RouteOptions): void
  remove(path: string): boolean
  navigate(path: string): Promise<void>
  match(path: string): { route: Route; params: Record<string, string> }
}
```

## Adding Routes

```js
PineconeRouter.add('/dynamic', {
  templates: ['/header.html', '/body.html'],
  handlers: [checkAuth, render],
  targetID: 'app',
  interpolate: true,
  preload: true,
  name: 'dynamicPage',
})
```

### RouteOptions

| Option | Type | Description |
|---|---|---|
| `handlers` | `Handler[]` | Functions to run on route match |
| `templates` | `string[]` | URLs of external templates |
| `targetID` | `string` | Element ID to render into |
| `interpolate` | `boolean` | Enable param interpolation in template URLs |
| `preload` | `boolean` | Preload templates after first load |
| `name` | `string` | Optional route name |

### Programmatic templates

When adding templates programmatically, Pinecone Router creates a `<template>` element and appends it to `<body>`. The template functions identically to declarative templates — it's hidden automatically on route changes and shown when its route matches.

If no `targetID` is provided (neither in options nor in global settings), content renders at the bottom of `<body>` after the created template tag.

## Removing Routes

```js
const removed = PineconeRouter.remove('/dynamic')
// returns true if the route existed and was removed
```

Removing a route also removes any associated template element from the DOM.

## Navigate

```js
await PineconeRouter.navigate('/path')
```

Navigation is async. It cancels any ongoing handlers, runs the new route's handlers, renders templates, and updates the context. The URL changes via `history.pushState()` (unless `pushState: false`).

## Match

Check if a path matches a registered route without navigating:

```js
const { route, params } = PineconeRouter.match('/users/42')
console.log(route.path)   // "/users/:id"
console.log(params)       // { id: "42" }
```

Returns the matched route and extracted params. Falls back to the `notfound` route if no match.

## Context Object

```ts
interface Context {
  readonly path: string                              // Current path
  readonly route?: Route                             // Matched route object
  readonly params: Record<string, string | undefined> // Extracted params
}
```

Access from Alpine: `$router.context.path`, `$router.context.params`

The context is updated **after** handlers finish. Inside handlers, use the `context` parameter instead of the global `$router.context`.

## Route Object

```ts
interface Route {
  readonly pattern: RegExp          // Internal regex pattern
  readonly path: string             // Raw route path
  readonly name: string             // Route name (path if unnamed)
  match(path: string): MatchResult  // Test path against this route
  handlers: Handler[]               // Route-specific handlers
  templates: string[]               // Template URLs
}
```

## RoutesMap

```ts
type RoutesMap = Map<string, Route> & {
  get(key: 'notfound'): Route  // Guaranteed to exist
}
```

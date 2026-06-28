# Gotchas & Upgrade Guide

## Common Gotchas

### Empty `x-template` required for inline content

In v7, inline templates require the empty `x-template` attribute:

```html
<!-- v7 — correct -->
<template x-route="/" x-template>
  <h1>Home</h1>
</template>

<!-- v6 — no longer works -->
<template x-route="/">
  <h1>Home</h1>
</template>
```

### Handlers see stale context

The global `$router.context` is not updated until handlers finish. Always use the `context` parameter:

```js
// Wrong — context not updated yet
function handler() {
  console.log(this.$router.context.params) // stale
}

// Correct — use the parameter
function handler(context) {
  console.log(context.params) // current
}
```

### Templates don't re-render on param changes

Visiting `/user/1` then `/user/2` on the same route does not re-render the template. Use `x-effect` for reactive updates:

```html
<div x-data="page" x-effect="loadData"></div>

<script>
Alpine.data('page', () => ({
  data: null,
  async loadData() {
    this.data = await fetch(`/api/${this.$params.id}`).then(r => r.json())
  },
}))
</script>
```

### `x-run.once` scope

Without an `id`, `x-run.once` is per-route. With an `id`, it's global:

```html
<script x-run.once>
  // Runs once per route visit (same route, different visits)
</script>

<script x-run.once id="global-init">
  // Runs once ever, even across different routes
</script>
```

### BasePath auto-prefixing

When `basePath` is set, don't manually prefix paths:

```js
// With basePath: '/app'
PineconeRouter.add('/about', {})       // registers /app/about ✓
PineconeRouter.add('/app/about', {})   // registers /app/app/about ✗
```

### Hash routing and basePath

With `hash: true`, basePath is only added to template URLs, not to hash fragments:

```js
// hash: true, basePath: '/app'
// Route /about → URL #/about (not #/app/about)
// Template /view.html → fetches /app/view.html
```

### Duplicate route error

Adding a route that already exists throws, except for `notfound`:

```js
PineconeRouter.add('/about', {})
PineconeRouter.add('/about', {})  // throws: Route already exists: /about

PineconeRouter.add('notfound', {}) // OK — notfound can be re-added
PineconeRouter.add('notfound', {}) // OK — notfound can be re-added again
```

### Handler `this` context

Handlers defined as methods on Alpine data components have `this` bound to the component:

```html
<template x-route="/hello" x-handler="greet"></template>
```

```js
Alpine.data('app', () => ({
  name: 'World',
  greet(context) {
    console.log(this.name) // "World" — this is the Alpine component
    this.$router.navigate('/') // works — $router is available on component
  },
}))
```

Handlers added programmatically do **not** have access to Alpine component `this`:

```js
PineconeRouter.add('/hello', {
  handlers: [(ctx) => {
    // this is NOT the Alpine component
    // Use PineconeRouter directly
    window.PineconeRouter.navigate('/')
  }],
})
```

## v6 → v7 Migration

### Magic helpers

| v6 | v7 |
|---|---|
| `$router` (was Context) | `$router` (is PineconeRouter object) |
| `$router.params` | `$params` |
| `$router.route` | `$router.context.route` |
| `$router.redirect()` | `$router.navigate()` |

### Context access

| v6 | v7 |
|---|---|
| `$router.path` | `$router.context.path` |
| `$router.params` | `$params` or `$router.context.params` |
| `$router.query` | `window.location.search` |
| `$router.hash` | `window.location.hash` |

### Navigation history

| v6 | v7 |
|---|---|
| `$router.back()` | `$history.back()` |
| `$router.forward()` | `$history.forward()` |
| `$router.canGoBack()` | `$history.canGoBack()` |
| `$router.canGoForward()` | `$history.canGoForward()` |
| `PineconeRouter.history` | `PineconeRouter.history` (same) |

### Handler changes

| v6 | v7 |
|---|---|
| `context.redirect('/path')` | `this.$router.navigate('/path')` |
| `context.navigate('/path')` | `this.$router.navigate('/path')` |
| Handler receives `(context)` | Handler receives `(context, controller)` |
| Global context updated before handlers | Global context updated after handlers |

### Template changes

| v6 | v7 |
|---|---|
| `<template x-route="/">` renders children | Need `<template x-route="/" x-template>` for inline |
| Single root element only | Multiple root elements supported |
| Single script per template | Multiple scripts supported |

### Event renames

| v6 | v7 |
|---|---|
| `pinecone-start` | `pinecone:start` |
| `pinecone-end` | `pinecone:end` |
| `fetch-error` | `pinecone:fetch-error` |

### Settings

| v6 | v7 |
|---|---|
| `PineconeRouter.Settings` (object) | `PineconeRouter.settings()` (function) |
| `Settings.templateTargetId` | `Settings.targetID` |
| `Settings.interceptLinks` | `Settings.handleClicks` |
| `Settings.alwaysSendLoadingEvents` | Removed (now default) |

### Settings usage

```js
// v6
PineconeRouter.Settings.basePath = '/app'

// v7
PineconeRouter.settings({ basePath: '/app' })
PineconeRouter.settings().basePath // read
```

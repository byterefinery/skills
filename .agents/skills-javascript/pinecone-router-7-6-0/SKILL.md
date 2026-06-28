---
name: pinecone-router-7-6-0
description: >
  Feature-packed client-side router for Alpine.js (v3). Use when building SPAs with Alpine.js that need
  declarative route definitions (x-route), inline and external templates (x-template), route handlers
  with abort support (x-handler), navigation history ($history), hash routing, basePath support,
  automatic link interception, and TypeScript types. Covers installation via CDN/NPM/ESM, route
  matching patterns (named, optional, rest, wildcard, suffix), template modifiers (.target, .preload,
  .interpolate), x-run script directives, programmatic route management, and event handling.
metadata:
  tags:
    - javascript
    - alpinejs
    - router
    - spa
---

# pinecone-router 7.6.0

Pinecone Router is a small, feature-packed client-side router for Alpine.js. It provides declarative route definitions via `x-route`, template rendering via `x-template`, and route handlers via `x-handler`. It integrates with Alpine.js as a plugin and exposes three magic helpers (`$router`, `$history`, `$params`).

## Overview

- **Declarative routes** — define routes on `<template>` elements with `x-route`
- **Templates** — inline (`x-template`) or external (`x-template="/page.html"`) content rendering
- **Handlers** — run async functions on route match with `AbortController` cancellation
- **Navigation history** — independent history stack with `$history.back()`, `.forward()`, `.to(index)`
- **Magic helpers** — `$router` (full router), `$history` (navigation history), `$params` (route params)
- **Settings** — hash routing, basePath, global handlers, preload, click interception toggle
- **Automatic link handling** — intercepts anchor clicks; bypass with `native` or `data-native` attribute
- **TypeScript** — full type definitions for handlers, context, routes, and settings

### Architecture

Routes are declared on `<template>` elements. On navigation, Pinecone Router matches the URL against registered routes, runs global then route-specific handlers (awaited in sequence), then renders templates. The router maintains its own navigation history separate from the browser API, deduplicating entries and excluding redirects.

## Usage

### Minimal setup

```html
<div x-data="app">
  <template x-route="/" x-template>
    <h1>Home</h1>
  </template>

  <template x-route="/:name" x-handler="greet" x-template>
    <h1>Hello <span x-text="$params.name"></span>!</h1>
  </template>

  <template x-route="notfound" x-template="/404.html"></template>
</div>

<script>
  document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
      greet(context) {
        console.log('Greeting', context.params.name)
      },
    }))
  })
</script>
```

### Installation

| Method | Usage |
|---|---|
| CDN | `<script src="https://cdn.jsdelivr.net/npm/pinecone-router@7.6.0/dist/router.min.js"></script>` (before Alpine) |
| NPM | `npm install pinecone-router` then `Alpine.plugin(PineconeRouter)` |
| ESM | `import PineconeRouter from 'https://cdn.jsdelivr.net/npm/pinecone-router@7.6.0/dist/router.esm.js'` |

See [01-installation-setup](references/01-installation-setup.md) for full setup details and Alpine.js integration patterns.

### Declaring routes

Use `x-route` on `<template>` elements. Supports literal, named (`:name`), optional (`:name?`), rest (`:rest+`), wildcard (`:path*`), and suffix patterns (`:title.mp4`).

```html
<template x-route="/about"></template>
<template x-route="/users/:id"></template>
<template x-route="/files/:path*"></template>
<template x-route="/videos/:title.(mp4|mov)"></template>
```

See [02-route-matching](references/02-route-matching.md) for segment types, param access, and matching rules.

### Templates

Inline templates use empty `x-template`. External templates specify URLs. Modifiers: `.target.id` (render into element), `.preload` (fetch on first load), `.interpolate` (inject params into URLs).

```html
<!-- Inline -->
<template x-route="/" x-template><h1>Home</h1></template>

<!-- External with target -->
<template x-route="/profile/:id" x-template.target.app="/profile.html"></template>

<!-- Preloaded 404 -->
<template x-route="notfound" x-template.preload="/404.html"></template>

<!-- Interpolated URLs -->
<template x-route="/dynamic/:name" x-template.interpolate="/api/:name.html"></template>
```

See [03-templates](references/03-templates.md) for embedded scripts, `x-run` directives, and template lifecycle.

### Handlers

Handlers run before templates and before the route is added to navigation history. They receive `(context, controller)` and can redirect via `this.$router.navigate()` or cancel via `controller.abort()`.

```html
<template x-route="/hello/:name" x-handler="[checkName, hello]"></template>
```

```js
Alpine.data('app', () => ({
  checkName(context, controller) {
    if (controller.signal.aborted) return
    if (context.params.name === 'admin') {
      this.$router.navigate('/admin')
    }
  },
  hello(context) {
    document.querySelector('#app').innerHTML =
      `<h1>Hello, ${context.params.name}</h1>`
  },
}))
```

See [04-handlers](references/04-handlers.md) for handler chaining, data passing, async patterns, and global handlers.

### Navigation history

Access via `$history` magic helper or `PineconeRouter.history`. Supports `back()`, `forward()`, `canGoBack()`, `canGoForward()`, `to(index)`.

```html
<button @click="$history.back()" :disabled="!$history.canGoBack()">Back</button>
<button @click="$history.forward()" :disabled="!$history.canGoForward()">Forward</button>
```

See [05-navigation-history](references/05-navigation-history.md) for history behavior and edge cases.

### Settings

Configure via `PineconeRouter.settings({...})` or `$router.settings({...})`.

```js
PineconeRouter.settings({
  hash: true,
  basePath: '/app',
  targetID: 'app',
  preload: true,
  handleClicks: true,
  pushState: true,
  globalHandlers: [authCheck],
})
```

See [06-settings-configuration](references/06-settings-configuration.md) for all settings and their effects.

### Programmatic API

Add/remove routes, navigate, and match paths from JavaScript.

```js
PineconeRouter.add('/dynamic', {
  templates: ['/header.html', '/body.html'],
  handlers: [checkAuth],
  targetID: 'app',
})

PineconeRouter.remove('/dynamic')
PineconeRouter.navigate('/path')
PineconeRouter.match('/path') // { route, params }
```

See [07-programmatic-api](references/07-programmatic-api.md) for the full API surface.

### Events

Listen for `pinecone:start`, `pinecone:end`, `pinecone:fetch-error`, `pinecone:handler-error` on `document`.

```js
document.addEventListener('pinecone:start', () => NProgress.start())
document.addEventListener('pinecone:end', () => NProgress.done())
```

See [08-events-link-handling](references/08-events-link-handling.md) for event details and link interception control.

## Gotchas

- **Empty `x-template` is required for inline content** — unlike v6, inline templates need the empty `x-template` attribute on the route template element
- **Handlers run before context updates** — the global `$router.context` is not updated until handlers finish; always use the `context` parameter passed to handlers
- **`$router` is the full router, not context** — in v7, `$router` is the PineconeRouter object; use `$router.context` for path/params/route info
- **Templates don't re-render on param changes** — visiting `/user/1` then `/user/2` on the same route won't re-render; use `x-effect` or `$watch` on `$params` for reactive updates
- **`x-run.once` is per-route by default** — without an `id` attribute, the once check is per-route visit. Add `id="unique"` to make it global across routes
- **Global handlers always run before route handlers** — order matters; use global handlers for auth checks and redirects
- **BasePath is auto-prefixed** — when `basePath` is set, it's automatically added to routes, navigation, and template URLs; don't manually prefix
- **Hash routing ignores basePath for navigation** — with `hash: true`, basePath is only added to template URLs, not to hash fragments
- **`notfound` is reserved** — `notfound` is the only route name that can be re-added without throwing a duplicate error
- **Handler abort cancels subsequent handlers** — `controller.abort()` stops the handler chain and prevents template rendering; navigation redirects also cancel queued handlers
- **Link interception respects modifier keys** — clicks with Ctrl, Meta, Alt, or Shift are always passed to the browser
- **Programmatic templates need targetID** — when adding templates via `PineconeRouter.add()`, either set `targetID` in options or configure it globally in settings

## References

- [01-installation-setup](references/01-installation-setup.md) — CDN, NPM, ESM installation and Alpine.js plugin registration
- [02-route-matching](references/02-route-matching.md) — Segment types, param access, named routes, matching rules
- [03-templates](references/03-templates.md) — Inline/external templates, modifiers, embedded scripts, x-run directives
- [04-handlers](references/04-handlers.md) — Handler chain, data passing, async patterns, AbortController, global handlers
- [05-navigation-history](references/05-navigation-history.md) — NavigationHistory object, $history helper, history behavior
- [06-settings-configuration](references/06-settings-configuration.md) — All settings, defaults, configuration patterns
- [07-programmatic-api](references/07-programmatic-api.md) — PineconeRouter object, add/remove routes, navigate, match
- [08-events-link-handling](references/08-events-link-handling.md) — Events, loading states, link interception, bypass patterns
- [09-typescript](references/09-typescript.md) — TypeScript types, imports, Handler generics, type declarations
- [10-gotchas-upgrade](references/10-gotchas-upgrade.md) — Common pitfalls, v6 to v7 migration guide

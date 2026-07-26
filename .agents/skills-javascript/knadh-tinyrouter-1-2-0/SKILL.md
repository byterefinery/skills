---
name: knadh-tinyrouter-1-2-0
description: >
  Knadh TinyRouter 1.2.0 — a zero-dependency client-side router (~950 bytes
  min+gzip) built on `window.history`. Use when building vanilla JS SPAs,
  Alpine.js apps, or lightweight frontend routing without React/Vue. Supports
  dynamic params (`{id}`), route groups, before/after hooks, and automatic
  `data-route` link binding.
license: MIT
compatibility: Browser environment with History API (all modern browsers)
metadata:
  tags:
    - javascript
    - frontend
    - router
    - spa
---

# knadh-tinyrouter 1.2.0

## Overview

TinyRouter is a minimal client-side router by Kailash Nadh. It wraps `window.history` (pushState/replaceState + popstate) and provides:

- **Route registration** with `{param}` dynamic segments
- **Route groups** — prefix a set of routes and share `before`/`after` handlers
- **Handler lifecycle** — `before`, `on`, `after` callbacks per route
- **Automatic link binding** — add `data-route` to any element for click-to-navigate
- **Programmatic navigation** via `navigate(path, query, hash, pushState)`

The library is a single ES module export with a `router.new(options)` factory. No dependencies.

## Usage

### Installation

```bash
npm install @knadh/tinyrouter
```

### Basic setup

```javascript
import router from '@knadh/tinyrouter';

const r = router.new({
    defaultHandler: (ctx) => console.log('404', ctx.path)
});

r.on('/', (ctx) => console.log('Home'));
r.on('/users/{id}', (ctx) => console.log('User', ctx.params.id));

r.ready();
```

### Route with lifecycle hooks

```javascript
r.on('/posts/{id}', {
    before: (ctx) => { /* auth check, analytics */ },
    on: (ctx) => { /* render content */ },
    after: (ctx) => { /* cleanup, post-render */ }
});
```

`before` and `after` accept single functions or arrays of functions — they are flattened and run in order.

### Route groups

```javascript
const admin = r.group('/admin', {
    before: (ctx) => checkAdminAuth()
});

admin.on('/dashboard', (ctx) => renderDashboard());
admin.on('/users/{id}', (ctx) => renderUserEditor(ctx.params.id));
```

Group `before` handlers run before the route's own handlers. Route `on` overrides group `on`. Group and route `after` handlers both run.

### Programmatic navigation

```javascript
// navigate(path, query, hash, pushState)
r.navigate('/users/42', { filter: 'active' }, 'settings');
r.navigate('/login', {}, '', false);  // replaceState instead of pushState
```

Query can be a plain object or `URLSearchParams`. `pushState = false` uses `replaceState`.

### Link binding

Add `data-route` to any clickable element — the router intercepts clicks and calls `navigate()`:

```html
<a href="/users/42" data-route>View User</a>
<button data-route="/settings">Settings</button>
```

The path comes from the `data-route` attribute value first, then falls back to `href`. Customize the attribute name via `selectorAttrib` option:

```javascript
const r = router.new({ selectorAttrib: 'data-nav' });
```

Call `r.bind(parentElement)` to bind routes inside a dynamically inserted container (e.g., after AJAX content load).

### Handler context

Every handler receives a `ctx` object:

| Property | Description |
|---|---|
| `ctx.path` | The registered route pattern (e.g., `/users/{id}`) |
| `ctx.params` | Object of extracted params (e.g., `{ id: "42" }`) |
| `ctx.state` | `window.history.state` |
| `ctx.location` | `window.location` |

## Gotchas

- **`ready()` must be called after all routes are registered** — it attaches the `popstate` listener and triggers the initial navigation. Calling it before `on()` registrations means those routes won't match.
- **First match wins** — routes are checked in registration order. Register more specific routes before generic ones.
- **`navigate()` on the same URL skips history** — if the target URL equals the current `pathname + search + hash`, no pushState/replaceState occurs, but handlers still execute. Use this for re-rendering without polluting history.
- **`data-route` binding is one-shot** — once an element is bound, `el.dataset.router` is set to `true` and re-binding is skipped. Call `bind()` only on fresh DOM subtrees.
- **Dynamic DOM content needs re-binding** — if you inject new `data-route` elements after initial load, call `r.bind(container)` on the parent.
- **No hash-mode routing** — TinyRouter uses path-based routing only. It does not support `#`-prefixed URLs or hashchange events.
- **Params are always strings** — `ctx.params.id` is a string even if the URL segment is numeric. Parse with `parseInt()` or `Number()` as needed.
- **`before` handlers are synchronous** — there is no async/await chain or abort mechanism. All before/on/after handlers fire sequentially regardless of return values.

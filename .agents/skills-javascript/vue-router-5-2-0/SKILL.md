---
name: vue-router-5-2-0
description: Vue Router 5.2.0 — the official router for Vue 3. Covers route configuration, navigation guards, programmatic navigation, RouterLink/RouterView components, composition API (useRouter/useRoute), history modes (HTML5, hash, memory), scroll behavior, dynamic routing, build-less browser usage via CDN, and advanced patterns. Use when working with Vue 3 routing, SPA navigation, or client-side URL management.
license: MIT
compatibility: Requires Vue 3.5.34+ or Vue 4.0.0+
metadata:
  tags:
    - javascript
    - vue
    - routing
    - frontend
---

# vue-router 5.2.0

## Overview

Vue Router is the official router for Vue 3, providing declarative route-to-component mapping with nested routes, dynamic segments, params, query handling, and a full navigation guard lifecycle. Version 5.2.0 supports Vue 3.5.34+ and Vue 4.0.0+, and ships multiple build formats including a global IIFE for direct browser use without any build step.

The router creates a reactive `currentRoute` that drives `<RouterView>` rendering. Navigation flows through a guard pipeline: `beforeRouteLeave` → global `beforeEach` → `beforeRouteUpdate` → `beforeEnter` → `beforeRouteEnter` (component) → global `beforeResolve` → `afterEach`. Guards can allow, redirect, or abort navigation.

## Usage

### Build-less browser usage

Load Vue and Vue Router from a CDN — no build tool needed:

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="https://unpkg.com/vue-router@5.2.0/dist/vue-router.global.js"></script>
<script>
  const { createApp, h } = Vue
  const { createRouter, createWebHistory, RouterLink, RouterView } = VueRouter

  const Home = { template: '<h1>Home</h1>' }
  const About = { template: '<h1>About</h1>' }

  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', component: Home },
      { path: '/about', component: About },
    ],
  })

  const app = createApp({
    setup() {
      return () => h('div', [
        h(RouterLink, { to: '/' }, () => 'Home'),
        h(RouterLink, { to: '/about' }, () => 'About'),
        h(RouterView, null),
      ])
    },
  })

  app.use(router)
  app.mount('#app')
</script>
```

For production, use the minified build: `vue-router.global.prod.js`.

### Module usage (ESM build for browsers)

The ESM browser build bundles everything including Vue — useful for module-native contexts:

```html
<script type="module">
  import { createApp } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
  import { createRouter, createWebHistory } from 'https://unpkg.com/vue-router@5.2.0/dist/vue-router.esm-browser.js'
  // ... same setup as above
</script>
```

### Standard setup with a build tool

```js
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/about', component: About },
    { path: '/users/:id', component: User },
    { path: '/:pathMatch(.*)*', component: NotFound },
  ],
})

createApp(App).use(router).mount('#app')
```

## Gotchas

- **Always pass `history` to `createRouter`** — it is required and throws if missing. Pick `createWebHistory()` (HTML5 pushState), `createWebHashHistory()` (hash-based), or `createMemoryHistory()` (SSR/testing).
- **`RouterLink` replaces `<a>` tags** — use `to` prop instead of `href`. Passing both causes double navigation. Add `custom` prop to render a non-`<a>` element while keeping routing behavior.
- **Navigation guards run in a strict order** — `beforeRouteLeave` (leaving component) → global `beforeEach` → `beforeRouteUpdate` (reused component) → `beforeEnter` (route record) → `beforeRouteEnter` (entering component, no `this`) → global `beforeResolve` → `afterEach`. Returning `false` aborts; returning a location redirects.
- **`beforeRouteEnter` has no component instance** — `this` is `undefined`. Access the instance via the `next` callback's third argument: `next(vm => { /* vm is the instance */ })`.
- **Lazy-loaded components must be functions** — use `() => import('./Page.vue')`, not `import('./Page.vue')` directly. The router starts the import during guard resolution and replaces the function with the resolved component.
- **`props: true` passes params as props** — on the route record, not as a component option. Use `props: true` for params-as-props, `props: route => ({ ... })` for custom mapping, or `props: { static: 'value' }` for static props.
- **Catch navigation failures** — `router.push()` returns a Promise that can reject with a `NavigationFailure`. Check with `isNavigationFailure(err, NavigationFailureType.duplicated)` to ignore redundant navigations silently.
- **`RouterView` depth auto-increments** — nested `<RouterView>` components automatically render the next matched segment. Use the `name` prop for named views rendered at the same depth.
- **Hash history ignores `file://` base** — when running from local files, `createWebHashHistory()` ignores the base parameter. URLs always use `#` prefix.
- **`scrollBehavior` requires a function** — return `{ top: 0 }` to scroll to top on every navigation, or return `savedPosition` to restore back/forward scroll. Return `false` to skip scrolling entirely.
- **Dynamic `addRoute` returns a dispose function** — call the returned function to remove the dynamically added route. Use `removeRoute(name)` to remove by name.
- **`START_LOCATION` detects initial navigation** — compare `from === START_LOCATION` in guards to distinguish the first page load from subsequent navigations.
- **Query params are always strings** — `route.query` normalizes all values to strings (or arrays of strings). Use `parseQuery`/`stringifyQuery` for custom encoding.
- **`<RouterView>` inside `<transition>` or `<keep-alive>`** — wrap `<RouterView>` directly, not the other way around. The deprecated pattern was `<keep-alive><router-view/></keep-alive>`; the correct pattern is `<transition><RouterView/></transition>`.

## References

- [01-getting-started](references/01-getting-started.md) — Installation, CDN builds, project setup, app mounting
- [02-route-records](references/02-route-records.md) — Route configuration, dynamic segments, nested routes, aliases, redirects
- [03-navigation](references/03-navigation.md) — Programmatic navigation, router.push/replace, resolve, go/back/forward
- [04-navigation-guards](references/04-navigation-guards.md) — Guard lifecycle, global guards, per-route guards, component guards
- [05-components](references/05-components.md) — RouterLink, RouterView, useLink composable, named views
- [06-history-modes](references/06-history-modes.md) — HTML5 history, hash history, memory history, base paths
- [07-composition-api](references/07-composition-api.md) — useRouter, useRoute, onBeforeRouteLeave, onBeforeRouteUpdate
- [08-scroll-behavior](references/08-scroll-behavior.md) — Scroll restoration, custom scroll targets, element-based scrolling
- [09-dynamic-routes](references/09-dynamic-routes.md) — Runtime route management, addRoute, removeRoute, clearRoutes
- [10-error-handling](references/10-error-handling.md) — Navigation failures, error types, onError handler
- [11-typed-routes](references/11-typed-routes.md) — TypeScript support, RouteMeta augmentation, type-safe navigation
- [12-advanced-patterns](references/12-advanced-patterns.md) — State passing, force navigation, view transitions, custom query parsing

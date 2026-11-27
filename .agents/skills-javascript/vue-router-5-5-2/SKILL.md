---
name: vue-router-5-5-2
description: Vue Router 5.5.2 — the official client-side router for Vue 3. Covers route configuration and matching syntax (dynamic segments, custom regex, repeatable and optional params), nested routes, programmatic navigation, navigation guards with return-based results (next is deprecated), RouterLink/RouterView components, composition API, history modes, scroll behavior, dynamic routes, file-based routing via the core vue-router/vite plugin, and 5.5.x features including the experimental resolver-based router with typed params and query values, custom param parsers, data loaders with reroute, scroll restoration, and vapor mode. Use when working with Vue 3 routing, SPA navigation, client-side URL management, or migrating from Vue Router 4 or unplugin-vue-router.
license: MIT
compatibility: Requires Vue ^3.5.34, 3.6.0-0, or 4.0.0 or later. File-based routing and the Vite plugin require Vite ^7.3.0 or 8.0.0. Pinia Colada data loaders require pinia ^3.0.4 or ^4.0.2 and @pinia/colada >=0.21.2. Vapor mode requires Vue 3.6 or later.
metadata:
  tags:
    - javascript
    - vue
    - routing
    - frontend
---

# vue-router 5.5.2

## Overview

Vue Router is the official client-side routing solution for Vue, built on Vue's component system. You configure **routes** that map URL paths to components; `<RouterView>` renders the matched component for the current URL. Navigation flows through a guard pipeline — `beforeRouteLeave` → global `beforeEach` → `beforeRouteUpdate` → `beforeEnter` → `beforeRouteEnter` → global `beforeResolve` → `afterEach` — where each guard can confirm, redirect, or cancel.

Vue Router 5 is a transition release that merged unplugin-vue-router (file-based routing) into the core package. For users without file-based routing, the stable API is unchanged from Vue Router 4. Version 5.5.x adds:

- **File-based routing in core** — the `vue-router/vite` plugin generates routes from `src/pages` files, with `definePage()` for per-route config and typed `useRoute(path)` per page.
- **Experimental router** (`vue-router/experimental`) — a resolver-based matching layer previewing the next major version: typed params/query/hash, custom param parsers, array-typed query values, and `new URL()`-style string normalization.
- **Data loaders** — `defineBasicLoader` / `defineColadaLoader` with `reroute()` for redirecting from within a loader.
- **Scroll restoration** — `useScrollRestoration()` and `onRouteRendered()` composables; positions are stored in sessionStorage.
- **Vapor mode** — Vapor versions of `<RouterLink>`/`<RouterView>` from `vue-router/experimental/vapor` (requires Vue 3.6+).

## Usage

### Install

```bash
npm install vue-router   # also works with pnpm, yarn, bun
```

New projects: `npm create vue@latest` scaffolds a Vite project with the option to include Vue Router.

### Standard setup

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

`App.vue` uses the globally registered components (no import needed in templates):

```vue
<template>
  <nav>
    <RouterLink to="/">Home</RouterLink>
    <RouterLink to="/about">About</RouterLink>
  </nav>
  <RouterView />
</template>
```

### File-based routing (core since v5)

```ts
// vite.config.ts
import VueRouter from 'vue-router/vite'

export default defineConfig({
  plugins: [VueRouter({ dts: 'src/route-map.d.ts' }), vue()],
})
```

Routes are generated from `src/pages` files — `about.vue` becomes `/about`, `users/[id].vue` becomes `/users/:id`. Configure pages with `definePage()` and read typed params with `useRoute('/users/[id]')`.

### Experimental router

```ts
// src/router/index.ts
import { createWebHistory } from 'vue-router'
import { experimental_createRouter as createRouter } from 'vue-router/experimental'
import { resolver } from 'vue-router/auto-resolver'

export const router = createRouter({ history: createWebHistory(), resolver })
```

Register `RouterLink`/`RouterView` yourself (the experimental router does not). In the experimental router, every `route.query` value is an **array**, and string locations are normalized like `new URL()` — no manual encoding.

### Browser without a build step

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="https://unpkg.com/vue-router@5.5.2/dist/vue-router.global.js"></script>
```

Pin exact versions in CDN URLs. Production builds are `vue-router.global.prod.js` and `vue-router.esm-browser.prod.js`. The `@vue/devtools-api` import is only needed with the development ESM build.

## Gotchas

- **Always pass `history` to `createRouter`** — it is required. Pick `createWebHistory()` (pushState), `createWebHashHistory()` (hash), or `createMemoryHistory()` (SSR/testing).
- **`next` in navigation guards is deprecated** — since 5.0.3, declaring or calling `next` logs a deprecation warning in development. Return values instead — `false` cancels, a location redirects, nothing/`true` continues. If a guard still declares `next`, the router expects it to be called exactly once even if you also return a value.
- **`params` are ignored when `path` is provided** — `router.push({ path: '/users/1', params: ... })` drops the params. Use `name` + `params` to get automatic URL encoding, or build a fully encoded path yourself.
- **Encode string paths yourself** — when providing a literal path or an object `path` (stable router), each dynamic segment must be encoded with `encodeURIComponent`. Named locations + params never need manual encoding.
- **Repeatable params are always arrays** — pass `{ chapters: ['a', 'b'] }` even for one item; `[]` or `null` removes an optional repeatable param. A non-repeatable param passed as `null` removes an optional param. Other types (objects, booleans) are stringified.
- **`beforeRouteEnter` has no component instance** — `this` is undefined because the component is not created yet. The `next(vm => ...)` callback workaround is deprecated along with `next`; use the experimental data loaders for pre-render data instead.
- **The component instance is reused when only params change** — navigating `/users/1` → `/users/2` reuses the component, so lifecycle hooks do not fire. Watch `route.params` or use `beforeRouteUpdate`/`onBeforeRouteUpdate`.
- **Catch-all named routes need array params** — for `/:pathMatch(.*)*`, navigate with `params: { pathMatch: route.path.substring(1).split('/') }`, not a single string, or the router percent-encodes the slashes.
- **Avoid slow regex in the middle of paths** — a repeatable `.*` param (`/:p(.*)*/suffix`) causes serious performance issues. Put match-everything params at the very end, or make a mid-path param non-repeatable.
- **`RouterLink` replaces `<a>`** — use `to`, not `href`. Use the `custom` prop to render a non-anchor element while keeping routing behavior.
- **Lazy components must be functions** — `component: () => import('./Page.vue')`, not the Promise directly. The router starts the import during guard resolution.
- **`<RouterView>` can display a route other than the URL one** — pass a resolved location to the `route` prop (the modal-with-own-URL pattern); load its lazy components first with `loadRouteLocation()`, and note that inside that view `useRoute()`/nested `<RouterView>`s follow the displayed route (v5.5 behavior — v5.4 and earlier used the current route). Navigation objects also accept `state`, stored in HTML5 `history.state` (see 05-components).
- **`router.push()` returns a Promise** — catch it and check `isNavigationFailure(err, NavigationFailureType.duplicated)` to ignore redundant navigations silently.
- **`addRoute(name, record)` returns a dispose function** — call it to remove the route; `removeRoute(name)` also works.
- **Detect initial navigation with `from === START_LOCATION`** — `START_LOCATION` is exported from `vue-router`.
- **5.5.x breaking changes** — `new NavigationResult(to)` is removed: use `reroute(to)` inside data loaders. Experimental matchers return `null` on a match miss (no more thrown `MatchMiss`). `onRouteRendered()`/`useScrollRestoration()` are no longer called for the initial navigation when the hook lives outside a `<RouterView>` — move it into a page/layout component.
- **Experimental query values are arrays** — `route.query.q` is `['vue']`, not `'vue'`; a valueless key gives `[null]`, a missing key is `undefined`. Pass arrays when navigating.
- **Vapor mode needs Vue 3.6+** and manual registration of the Vapor components from `vue-router/experimental/vapor`; no Options API, no `$route` in templates, no SSR hydration yet.
- **File-based routing** — `index.vue` must be all lowercase; repeatable params use `[id]+`, optional use `[[id]]`; param parsers via `[id=int]` or `definePage({ params })`.
- **`DataLoaderPlugin` must be registered before the router** — `app.use(DataLoaderPlugin, { router })` then `app.use(router)`.
- **`scrollBehavior` requires a function** — return `{ top: 0 }`, `savedPosition` for back/forward, or `false` to skip. For full browser back/forward scroll restoration, use the experimental `useScrollRestoration()`.

## References

- [01-getting-started](references/01-getting-started.md) — Installation, CDN builds, standard setup, accessing router and route
- [02-route-records](references/02-route-records.md) — Route configuration, matching syntax, nested routes, redirects, aliases, meta fields
- [03-navigation](references/03-navigation.md) — Programmatic navigation, push/replace, params and encoding rules, go/back/forward, history state, custom query parsing, loadRouteLocation
- [04-navigation-guards](references/04-navigation-guards.md) — Guard lifecycle, global/per-route/component guards, migrating from next
- [05-components](references/05-components.md) — RouterLink, useLink, RouterView, the `route` prop (modals with their own URL), named views, active links, transitions
- [06-history-modes](references/06-history-modes.md) — HTML5, hash, memory history, base paths, server configurations
- [07-composition-api](references/07-composition-api.md) — useRouter, useRoute, onBeforeRouteLeave/Update, inject in guards
- [08-scroll](references/08-scroll.md) — scrollBehavior and experimental scroll restoration (useScrollRestoration, onRouteRendered)
- [09-dynamic-routes](references/09-dynamic-routes.md) — addRoute, removeRoute, clearRoutes, nested dynamic routes
- [10-error-handling](references/10-error-handling.md) — Navigation failures, isNavigationFailure, router.onError
- [11-file-based-routing](references/11-file-based-routing.md) — vue-router/vite plugin, file conventions, definePage, typed routes, Volar
- [12-experimental-router](references/12-experimental-router.md) — experimental_createRouter, typed params and query, param parsers, encoding, vapor mode
- [13-data-loaders](references/13-data-loaders.md) — defineBasicLoader, defineColadaLoader, reroute, SSR, navigation awareness, loaders vs component lifecycle
- [14-migration-v4-to-v5](references/14-migration-v4-to-v5.md) — no breaking changes for v4 users, iife/devtools caveat, v6 ESM-only plan, unplugin-vue-router import changes, new exports

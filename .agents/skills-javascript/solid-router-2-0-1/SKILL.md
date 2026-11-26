---
name: solid-router-2-0-1
description: Universal router for SolidJS (@solidjs/router v2.0.1, Solid 2) with config-object routes, a typed paths proxy, plain-anchor link handling, opt-in link preloading, and data APIs (query, liveQuery, formAction) with single-flight mutations. Use when building or navigating routes in a SolidJS 2 app, typing URLs and route params, preloading routes, setting up SSR with the router server collector, or migrating from the 0.x component API.
license: MIT
compatibility: Requires the @solidjs/router npm package, solid-js ^2.0.0 and @solidjs/web ^2.0.0 peer dependencies; filesystem-routing >=0.4.0 is optional for file-system routes
metadata:
  tags:
    - javascript
    - frontend
    - routing
    - solidjs
---

# solid-router 2.0.1

## Overview

@solidjs/router (v2.0.1, MIT) is the universal router for SolidJS, targeting **Solid 2** (peers `solid-js ^2.0.0` and `@solidjs/web ^2.0.0` — the 1.x router line belongs to Solid 1). Routes are config objects — the single source of truth for matching _and_ types — and the router upgrades HTML's own verbs instead of wrapping them: `<a href>` and `<form action>` carry typed, URL-addressable values on real platform elements, intercepted by delegation, and keep working without JavaScript.

- **Typed routing** — URLs built through a `paths` proxy inferred from the route config (`paths.users(2).settings` typechecks against the tree)
- **Plain anchors** — no link component; `<a>` gets `aria-current` and `data-active` automatically, `data-pending` with the opt-in `pendingLinks` plugin
- **Universal rendering** — one factory for browser, hash, memory, and server; history adapters are imports, so unused ones never enter the bundle
- **Preload functions + opt-in link preloading** — render-as-you-fetch data, warm before the click
- **Data APIs** — `query`, `liveQuery`, `formAction` with dedupe, revalidation, single-flight mutations
- **Typed search params** — opt-in per-route Standard Schema validation (`search.page` is a `number`, not `"2"`)

Official docs: https://docs.solidjs.com/solid-router

## Usage

### Install

```bash
npm add @solidjs/router
```

### Getting started

Define routes as config objects and create the router outside JSX. The instance is the provider component, and `paths` is the typed URL builder inferred from the tree:

```tsx
// app/router.ts
import { lazy } from "solid-js";
import { createRouter } from "@solidjs/router";

export const Router = createRouter({
  routes: [
    { path: "/", component: lazy(() => import("./pages/Home")) },
    { path: "/about", component: lazy(() => import("./pages/About")) },
    {
      path: "/users/:id",
      component: lazy(() => import("./pages/User")),
      children: [
        { path: "/", component: lazy(() => import("./pages/UserOverview")) },
        { path: "/settings", component: lazy(() => import("./pages/UserSettings")) }
      ]
    },
    { path: "*404", component: lazy(() => import("./pages/NotFound")) }
  ]
});

export const { paths } = Router;
```

One module serves everything: the client renders the instance, and the server reads its location from the request. Mount it — the render-prop child is the root layout, always mounted, receiving the matched content as `props.children`:

```tsx
render(
  () => (
    <Router>
      {props => (
        <>
          <h1>My Site with lots of pages</h1>
          {props.children}
        </>
      )}
    </Router>
  ),
  document.getElementById("app")!
);
```

Trees composed across files should be wrapped in `defineRoutes` (preserves literal type inference); `defineRoute` also types a route's own `component`/`preload` params — see [02-routes](references/02-routes.md).

### Links

There is no link component — use plain `<a>`. The router intercepts same-origin clicks through delegation; behavior modifiers are attributes, so they work in client, server-rendered, and third-party markup:

| attribute  | effect                                                                                          |
| ---------- | ----------------------------------------------------------------------------------------------- |
| `replace`  | Replace the history entry instead of pushing                                                    |
| `noscroll` | Turn off scrolling to the top after navigation                                                  |
| `state`    | JSON string pushed onto the history stack                                                       |
| `preload`  | `"false"` opts out of all preloading; `"viewport"` / `"eager"` opts into that strategy          |
| `link`     | Marks a router link when `explicitLinks` is enabled                                             |
| `target`   | Any value (e.g. `_self`) opts the anchor out of router handling                                 |

Active/pending state is styled with CSS — `aria-current="page"` and `data-active` are automatic, `data-pending` is opt-in via the `pendingLinks` plugin. `useLinkState` is the programmatic counterpart for custom link components.

### Preloading

Nothing is preloaded unless you opt in (earlier versions preloaded on hover/focus/touch by default — that built-in is gone). Strategies, all client-only and importable individually: `intentPreload()` (pointer rest/focus/touch), `tapPreload()` (pointer down), `viewportPreload()` (in-viewport + idle), `eagerPreload()` (page loaded + idle). Pass an array to combine. Full options in [03-data-and-preloading](references/03-data-and-preloading.md).

### Router config

```tsx
createRouter(config);
```

| option          | description                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------------- |
| `routes`        | The route tree — inline arrays infer literally; wrap extracted trees in `defineRoutes`            |
| `base`          | Base url for matching; a path starting with `/` is a full path — `paths` is base-aware            |
| `preload`       | App-wide preload: once per mount/request, result reaches the root render-prop as `props.data`     |
| `history`       | History adapter; defaults to browser history on the client and the request URL on the server      |
| `singleFlight`  | Single-flight mutations, default `true`                                                           |
| `actionBase`    | Root url for server actions, default `/_server`                                                   |
| `preloadLinks`  | Link preload strategies, e.g. `intentPreload()`; none by default. A boolean is a type error       |
| `explicitLinks` | Require the `link` attribute for router handling instead of intercepting all anchors              |
| `links`         | Link claims plugin — `pendingLinks` adds `data-pending` to the in-flight navigation's target      |
| `transformUrl`  | Rewrite URLs before matching                                                                      |

The instance carries the static surface: `paths` (typed URL builder), `match(url)` (pure matching, no rendering context), `routes`, `config`. Hooks read the live session — see [01-hooks-and-paths](references/01-hooks-and-paths.md).

## Gotchas

- **v2 is Solid 2 only.** `@solidjs/router` 2.x peers `solid-js ^2.0.0` / `@solidjs/web ^2.0.0`. The Solid 1 router is the 1.x line (renumbered after 0.16 went stable as 1.0.0) — do not `^1`-range-track the `next` tag expecting Solid 2.
- **The component API is gone in 2.0.** `<Router>`, `<Route>`, `<A>`, `<Navigate>`, `<HashRouter>`, `<MemoryRouter>`, `<StaticRouter>` were removed — `createRouter` with config-object routes and plain `<a>` are the only setup and link primitives. Full mapping in [04-migration-0-x](references/04-migration-0-x.md).
- **`preloadLinks: true` is a type error.** Link preloading is opt-in via strategy functions; a boolean preloads nothing and warns in development.
- **Paths starting with `/` are full paths — the `base` is never added.** `navigate("/about")`, `href="/about"`, and `redirect("/x")` all bypass the base. Use `paths` nodes (or `${base}/…`) for base-relative links.
- **`formAction` only works with POST** — put `method="post"` on the form.
- **Wildcard `*` must be the last path segment** — `foo/*any/bar` creates no routes.
- **`redirect` and `reload` come from `@solidjs/web`**, not the router — they are protocol-level and work without the router. Same for `json` → `respond`.
- **`createAsync` / `createAsyncStore` are gone (Solid 2)** — read `query()` results with `createMemo`, `createProjection`, `createOptimistic(Store)`.
- **`useAction` is deprecated with no replacement** — outside a form, call the server function (or a core `action`) directly; the router applies its revalidation and redirect either way.
- **One router per app** — the tree is immutable; mounting a router inside another router is not supported and warns in development. Compose large apps by spreading `defineRoutes` subtrees into one config.
- **`query` cache timing in the browser** — a 5-second preload cache (link preload and route entry share one fetch) and a back/forward cache up to 5 minutes (user-initiated navigation bypasses it).
- **SPA deployments need index rewrites** — without SSR, deep URLs 404 unless the host rewrites to `index.html` (Netlify `_redirects`, Vercel `rewrites`).

## References

- [01-hooks-and-paths](references/01-hooks-and-paths.md) — instance members, the typed `paths` proxy, and all router hooks (`useParams` … `useBeforeLeave`)
- [02-routes](references/02-routes.md) — route definition keys, dynamic/optional/wildcard/multi-path routes, match filters, nested and lazy subtrees, typed route params
- [03-data-and-preloading](references/03-data-and-preloading.md) — preload strategies and functions, `query`, `liveQuery`, `formAction`, `useSubmissions`, typed search params
- [04-migration-0-x](references/04-migration-0-x.md) — mapping from the 0.x component API to `createRouter` + plain anchors
- [05-server-and-environments](references/05-server-and-environments.md) — server component routes (experimental), file-system routes, server integration, hash/memory history, no-Proxy runtimes, SPA rewrites

---
name: solid-router-2-0-0-next-35
description: Solid Router 2.0.0-next.35 — the official router for Solid.js 2 (next line, 2.0.0-rc runtime). Config-based routing through the createRouter factory — the component-based API is removed — with a typed path proxy, plain anchor links with link state, preload functions, data APIs (query, liveQuery, action, useSubmissions, revalidate), typed search params, hash and memory history adapters, single-flight SSR, file-system routes, and server component routes. Use when building Solid.js 2 apps with client-side routing, SPA navigation, data fetching with preload, or server-side rendering, or when migrating from Solid Router 0.x.
license: MIT
compatibility: Requires Solid.js 2.0.0-rc.13+ and @solidjs/web 2.0.0-rc.13+; optional filesystem-routing >=0.4.0 peer for file-system routes
metadata:
  tags:
    - javascript
    - typescript
    - solidjs
    - routing
    - frontend
    - spa
    - ssr
---

# solid-router-2-0-0-next-35

## Overview

Solid Router 2.x (next line) is the official router for Solid.js 2. The API is config-based — routes are config objects passed to a `createRouter` factory, and the returned instance is itself the provider component. The 0.x component API (`<Router>`, `<Route>`, `<A>`, `<Navigate>`) is removed; plain `<a>` elements are the only link primitive.

Routes are the single source of truth for matching *and* types — `paths` is a typed URL builder inferred from the route tree, and the router upgrades HTML's own verbs (`<a href>`, `<form action>`) instead of wrapping them in components.

Key features:
- **Config-based routing** — `createRouter({ routes })`; the instance is the provider component; one router per app, immutable tree
- **Typed paths** — `paths.users(2).settings` typechecks against the tree; param types from match filters, search types from per-route Standard Schema validators
- **Plain anchors** — no link component; the router intercepts same-origin clicks by delegation and manages `aria-current="page"`, `data-active`, and `data-pending`
- **Preload functions** — parallel data fetching on route render and link hover/focus
- **Data APIs** — `query` / `liveQuery` (experimental) for reads, `action` for mutations, with deduplication, revalidation, and single-flight responses
- **Universal rendering** — browser, hash, and memory history are plain imports (unused ones stay out of the bundle); on the server the request URL drives rendering

Install with `npm add @solidjs/router`. Import from `"@solidjs/router"`; sub-exports are `./server` (framework handler wiring) and `./fs` (file-system routes).

## Usage

### Basic setup

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

This one module serves everything — the client renders the instance, and on the server the same instance reads its location from the request (or the configured history when there is no request, e.g. SSG, tests). Mount it by rendering the instance; the render-prop child is the root layout and always stays mounted:

```tsx
// app/index.tsx
import { render } from "@solidjs/web";
import { Router } from "./router";

render(
  () => (
    <Router>
      {props => (
        <>
          <nav>
            <a href={paths()}>Home</a>
            <a href={paths.about}>About</a>
          </nav>
          {props.children}
        </>
      )}
    </Router>
  ),
  document.getElementById("app")!
);
```

Links are plain anchors — typed path nodes coerce to strings on the attribute, and the router intercepts clicks through delegation:

```tsx
<a href={paths.users(user.id).settings}>Settings</a>
```

### Mental model — instance vs hooks

The instance is shared — one module-level object serving every mount, request, and test — and deliberately non-stateful, so it carries only static routing vocabulary. Hooks read the live session from router context:

| Instance — facts about the app | Hooks — facts about the session |
| --- | --- |
| `paths` — how to spell URLs | `useLocation`, `useParams` — where am I |
| `match(url)`, `keysFor(url)` — pure matching | `useNavigate`, `usePreloadRoute` — move / warm |
| `routes`, `config` — what exists | `useIsRouting`, `useRouteMatches`, `useSearchParams` — live state |

They compose as noun and verb: `navigate(paths.users(2))`, `useParams(paths.users)`. Components that only read their session never import the router instance, which also avoids import cycles between component files and the router module.

### Data fetching and mutations

```tsx
import { query, action } from "@solidjs/router";
import { redirect } from "@solidjs/web";
import { paths } from "./router";

const getUser = query(async id => (await fetch(`/api/users/${id}`)).json(), "users");

const updateUser = action(async (form: FormData) => {
  await db.users.update(form.get("id"), form);
  throw redirect(paths.users(form.get("id"))); // typed paths work in redirects
}, "update-user");
```

```tsx
function User() {
  const params = useParams(paths.users); // typed from the tree
  const user = createMemo(() => getUser(params.id));
  return (
    <>
      <h1>{user().name}</h1>
      <form action={updateUser} method="post">
        <button>Save</button>
      </form>
    </>
  );
}
```

Forms bind actions directly with `method="post"`; single-flight mutations are on by default, so the mutation response carries refreshed route data in the same round trip.

## Gotchas

- **The component API is gone** — no `<Router>`, `<Route>`, `<A>`, `<Navigate>`, `<HashRouter>`, `<MemoryRouter>`, `<StaticRouter>` components, and no JSX route trees. `createRouter` is the only setup path; history modes are config values (`hashHistory()`, `memoryHistory(url)`).
- **Wrap extracted route arrays in `defineRoutes`** — a bare route array extracted into a module silently widens to `string` paths; `defineRoutes` is an identity function that preserves the literal types the `paths` proxy infers from.
- **One router per app, immutable tree** — mounting a router inside another router is not supported and warns in development; compose large apps by spreading subtrees into the config.
- **`redirect`, `reload`, `respond` come from `@solidjs/web`**, not from the router — they are protocol-level and work without the router. `revalidate` and the data APIs come from the router.
- **`createAsync` / `createAsyncStore` are gone** — read `query()` results with Solid 2 primitives: `createMemo`, `createProjection`, or the optimistic pair `createOptimistic` / `createOptimisticStore`.
- **`useSubmissions` is settled history, not in-flight state** — use optimistic primitives fed by `action(...).onSubmit(...)` for pending UI; select the latest settled submission with `.at(-1)`.
- **Actions are POST only** — put `method="post"` on the form. Actions that are not server functions need a stable name for SSR-serializable form attributes: `action(fn, "my-action")`.
- **Typed `paths` require `Proxy`** — the core router works on no-Proxy runtimes, but accessing `paths` there throws; swap in `paramsWrapper` / `queryWrapper` through the history adapter's `utils`.
- **The wildcard token must be the last path segment** — `foo/*any/bar` won't create routes; name it (`*any`) to expose the rest as a param.
- **Shared-path routes don't re-render on param change** — to force a re-render when params change within one pattern, use a keyed `<Show>` around the component.
- **SPA deployments need URL rewrites** — without SSR, deep links 404 on hard load; add Netlify `_redirects` or Vercel `rewrites` to `index.html`.
- **Typed paths promise spelling, not matching** — `matchFilters` means a well-typed URL can still fail to match at runtime; `match()` returning `[]` is a valid state.
- **`scrollRestoration` is opt-in for custom history adapters** — it defaults to `true` only with the default browser history; a custom `history` owns its session and must pass `scrollRestoration: true` explicitly.

## References

- [01-route-config](references/01-route-config.md) — createRouter factory, config options, instance members, route definitions, dynamic routes, match filters, nested and lazy subtrees, preload functions
- [02-typed-paths-links](references/02-typed-paths-links.md) — paths proxy mechanics, link attributes, current/active/pending rules, useLinkState
- [03-primitives](references/03-primitives.md) — useParams, useNavigate, useLocation, useSearchParams, useIsRouting, useMatch, useRouteMatches, usePreloadRoute, useBeforeLeave, useResolvedPath/useHref
- [04-data-apis](references/04-data-apis.md) — query, liveQuery, action, useAction, useSubmissions, revalidate, response helpers, optimistic UI patterns
- [05-server-fs](references/05-server-fs.md) — server integration and no-JS forms, server component routes, file-system routes, hash/memory history, no-Proxy runtimes, pure matching
- [06-migration-deployment](references/06-migration-deployment.md) — migrating from 0.x, removed and renamed APIs, SPA deployment

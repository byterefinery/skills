---
name: solid-router-1-0-0
description: Solid Router 1.0.0 — the official router for Solid.js. Covers Router/Route/A/Navigate components, dynamic routes with params and wildcards, nested routes via props.children, preload functions, data APIs (query, createAsync, createAsyncStore, action), response helpers (redirect, reload, json), router primitives (useParams, useNavigate, useLocation, useSearchParams, useIsRouting, useMatch, useBeforeLeave), HashRouter/MemoryRouter/StaticRouter, config-based routing, and SSR. Use when building Solid.js apps with client-side routing, SPA navigation, data fetching with preload, or server-side rendering.
license: MIT
compatibility: "Requires Solid.js 1.9+ and Node.js 18+. Browser support — ES2017+. JSX transform via babel-preset-solid or @babel/plugin-transform-react-jsx."
metadata:
  tags:
    - javascript
    - solidjs
    - routing
    - frontend
    - spa
    - ssr
---

# solid-router 1.0.0

## Overview

Solid Router is the official router for Solid.js, providing fine-grained reactive routing with declarative route definitions. Routes are defined as `<Route>` components inside a `<Router>`, with nested routes rendered via `props.children` (no `<Outlet>` or `<Routes>`). The router supports history, hash, memory, and static (SSR) modes.

Key features:
- **Declarative JSX routes** — define routes as component trees, or as config arrays
- **Dynamic segments** — `:param`, optional `:param?`, wildcard `*`, named wildcard `*name`
- **Match filters** — validate params with enums, regex, or functions
- **Preload functions** — parallel data fetching triggered on route load or link hover
- **Data APIs** — `query()` for cached/deduped fetching, `createAsync`/`createAsyncStore` for reactive async state, `action()` for mutations with revalidation
- **Response helpers** — `redirect()`, `reload()`, `json()` — thrown from queries/actions to control navigation
- **Router primitives** — `useParams()`, `useNavigate()`, `useLocation()`, `useSearchParams()`, `useIsRouting()`, `useMatch()`, `useBeforeLeave()`, `usePreloadRoute()`

Install with `npm add @solidjs/router`. Import from `"@solidjs/router"`.

## Usage

### Basic setup

```tsx
import { render } from "solid-js/web";
import { Router, Route } from "@solidjs/router";
import { lazy } from "solid-js";

const Home = lazy(() => import("./pages/Home"));
const Users = lazy(() => import("./pages/Users"));
const User = lazy(() => import("./pages/User"));

const App = (props) => (
  <>
    <nav>
      <a href="/">Home</a>
      <a href="/users">Users</a>
    </nav>
    {props.children}
  </>
);

render(
  () => (
    <Router root={App}>
      <Route path="/" component={Home} />
      <Route path="/users" component={Users} />
      <Route path="/users/:id" component={User} />
      <Route path="*" component={() => <h1>404 Not Found</h1>} />
    </Router>
  ),
  document.getElementById("app")
);
```

The `root` prop wraps every route — ideal for top-level layout, nav bars, and context providers. It receives `props.children` as the matched route content.

### Dynamic routes and params

```tsx
import { useParams } from "@solidjs/router";

function User() {
  const params = useParams();
  return <h1>User: {params.id}</h1>;
}
```

Access params reactively via `useParams()`. The params object is a reactive store — access properties to subscribe to changes.

### Nested routes

```tsx
function PageWrapper(props) {
  return (
    <div>
      <h1>Users Section</h1>
      {props.children}
    </div>
  );
}

<Route path="/users" component={PageWrapper}>
  <Route path="/" component={UsersList} />
  <Route path="/:id" component={User} />
</Route>
```

Nested routes render inside `props.children` of the parent component. Only leaf routes become their own URLs — parent routes without a leaf child render empty. Use `props.children` for outlets; there is no `<Outlet>` component.

### The `<A>` component

```tsx
import { A } from "@solidjs/router";

<A href="/users" activeClass="active" inactiveClass="inactive">Users</A>
<A href="/" activeClass="active" end>Home</A>
```

`<A>` resolves relative paths against the current route, applies `active`/`inactive` classes, and sets `aria-current="page"` on exact match. Use `end` to match exactly (without descendants) — essential for root `/` links.

### Programmatic navigation

```tsx
import { useNavigate } from "@solidjs/router";

function Login() {
  const navigate = useNavigate();

  const handleSubmit = async () => {
    await login();
    navigate("/dashboard", { replace: true });
  };
}
```

`navigate(path, options)` — `replace` omits history entry, `scroll` controls auto-scroll, `state` passes serializable data, `resolve` controls relative path resolution.

### Search params

```tsx
import { useSearchParams } from "@solidjs/router";

function Search() {
  const [params, setParams] = useSearchParams();

  return (
    <>
      <span>Page: {params.page}</span>
      <button onClick={() => setParams({ page: String(parseInt(params.page || "0") + 1) })}>
        Next
      </button>
    </>
  );
}
```

Returns `[params, setParams]`. Values are strings. Setting `""`, `undefined`, or `null` removes a key.

### Preload functions

```tsx
import { Route } from "@solidjs/router";

async function preloadUser({ params, location, intent }) {
  if (intent === "preload") return; // skip during hover-only preloads
  return fetch(`/api/users/${params.id}`).then(r => r.json());
}

<Route path="/users/:id" component={User} preload={preloadUser} />;
```

Preload functions receive `{ params, location, intent }`. The `intent` is `"initial"` (page load), `"navigate"` (router navigation), `"native"` (back/forward), or `"preload"` (hover/prefetch). The return value is passed as `props.data` to the component (for all intents except `"preload"`).

### Data APIs — query and createAsync

```tsx
import { query, createAsync } from "@solidjs/router";

const getUser = query(async (id) => {
  return (await fetch(`/api/users/${id}`)).json();
}, "users");

function User(props) {
  const user = createAsync(() => getUser(props.params.id));
  return <h1>{user()?.name}</h1>;
}
```

`query(fn, key)` deduplicates requests, caches results (5s preload, 3min back/forward), and supports revalidation by key. `createAsync()` wraps the call in a reactive signal that suspends while pending.

### Actions — mutations with revalidation

```tsx
import { action, redirect, revalidate } from "@solidjs/router";

const updateTodo = action(async (formData) => {
  const id = Number(formData.get("id"));
  await fetch(`/api/todos/${id}`, { method: "PUT", body: JSON.stringify({ done: true }) });
  throw redirect(`/todos/${id}`, { revalidate: getUser.keyFor(id) });
});

<form action={updateTodo} method="post">
  <input type="hidden" name="id" value={todo.id} />
  <button type="submit">Complete</button>
</form>
```

Actions work with `<form action={myAction} method="post">` or programmatically via `useAction(myAction)`. Throw `redirect()` or `reload()` to control post-mutation navigation. Use `action.fn.with(arg1, arg2)` to bind arguments instead of `FormData`.

## Gotchas

- **No `<Outlet>` or `<Routes>`** — nested routes render via `props.children` in the parent component. There is no `<Outlet>` component. The `<Router>` itself acts as the routes container.
- **`root` prop on `<Router>`, not a wrapper** — put your top-level layout (nav, context providers) in `root={App}`, not outside the `<Router>`. The root component receives `props.children` as route content.
- **Preload return value becomes `props.data`** — the preload function's return value is passed to the route component as `props.data`. It is available for all intents except `"preload"` (hover-only).
- **`<A>` vs `<a>`** — `<A>` resolves relative paths and adds active classes. Plain `<a>` tags are intercepted by default; set `target` (e.g., `target="_self"`) to disable interception for a specific link, or use `explicitLinks` on `<Router>` to require `<A>` everywhere.
- **`end` prop on root links** — `<A href="/">` matches every path. Use `end` to match only exact `/`: `<A href="/" end activeClass="active">Home</A>`.
- **`query` key is for revalidation** — the second argument to `query(fn, "key")` is the cache key prefix. Use `queryFn.key` to revalidate all entries or `queryFn.keyFor(arg)` for a specific entry.
- **`createAsync` suspends** — reading `createAsync()` before resolution triggers `<Suspense>`. Use `user.latest` for the most recent resolved value without suspending (will be removed in future).
- **Actions need `method="post"`** — form actions only work with POST. Always include `method="post"` on the `<form>`.
- **`useSearchParams` values are strings** — the reactive params object always has string values. Parse as needed: `parseInt(params.page)`.
- **Wildcard must be last** — `foo/*` matches `foo/a/b/c`, but `foo/*rest/bar` creates no routes. The wildcard segment must be the final path segment.
- **`useBeforeLeave` cleanup is automatic** — the subscription is cleaned up when the component unmounts. No manual disposal needed.
- **Multiple paths keep component mounted** — `<Route path={["login", "register"]} component={Auth}>` keeps the component alive when switching between the two paths.
- **Match filters prevent route matching** — if a `matchFilters` constraint fails, the route silently doesn't match. Use this for enum-like params or regex validation.
- **HashRouter uses `location.hash`** — switch to `<HashRouter>` when the server can't handle arbitrary paths. It uses the URL hash fragment for routing.
- **SSR: pass `url` prop on server** — `<Router url={isServer ? req.url : ""} />`. The router defaults to static mode on the server; pass the request URL for correct matching.

## References

- [01-routing-components](references/01-routing-components.md) — Router, Route, A, Navigate components and props
- [02-route-primitives](references/02-route-primitives.md) — useParams, useNavigate, useLocation, useSearchParams, useIsRouting, useMatch, useCurrentMatches, useBeforeLeave, usePreloadRoute
- [03-data-apis](references/03-data-apis.md) — query, createAsync, createAsyncStore, action, useAction, useSubmission
- [04-response-helpers](references/04-response-helpers.md) — redirect, reload, json, revalidate, cache control
- [05-advanced-patterns](references/05-advanced-patterns.md) — preload functions, config-based routing, SSR, alternative routers, match filters, SPA deployment

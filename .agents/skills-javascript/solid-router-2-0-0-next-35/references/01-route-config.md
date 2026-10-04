# Route Config

The `createRouter` factory is the only way to set up the router. Routes are config objects created outside JSX; the returned instance is the provider component.

## createRouter

```tsx
import { createRouter } from "@solidjs/router";

const Router = createRouter({ routes, base: "/app" });
// Router is a component: <Router>{props => <Layout>{props.children}</Layout>}</Router>
```

The render-prop child is the root layout — it always stays mounted, receives the matched content as `props.children`, and is the ideal place for top-level navigation and context providers. The factory-level `preload` option replaces the old `root` / `rootPreload` props.

## Config options

| option          | type                      | description                                                                                           |
| --------------- | ------------------------- | ----------------------------------------------------------------------------------------------------- |
| `routes`        | `RouteDefinition[]`       | The route tree — inline arrays infer literally; wrap extracted trees in `defineRoutes`               |
| `base`          | `string`                  | Base URL to use for matching routes                                                                   |
| `preload`       | `RoutePreloadFunc`        | App-wide preload: once per mount/request, result reaches the root render-prop as `props.data`         |
| `history`       | `RouterHistory`           | History adapter; defaults to browser history on the client and the request URL on the server          |
| `singleFlight`  | `boolean`                 | Single-flight mutations, default `true`                                                               |
| `actionBase`    | `string`                  | Root URL for server actions, default `/_server`                                                       |
| `preloadLinks`  | `boolean`                 | Preload route code/data on link hover and focus, default `true`                                       |
| `explicitLinks` | `boolean`                 | Require the `link` attribute for router handling instead of intercepting all anchors, default `false` |
| `scrollRestoration` | `boolean`             | Explicit scroll restoration for back/forward, default `true` with the default browser history; custom `history` adapters own their session and must opt in explicitly |
| `transformUrl`  | `(url: string) => string` | Rewrite URLs before matching                                                                            |

## Instance members

The returned instance is the provider component and carries the static surface:

| member      | description                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------------- |
| `paths`     | The typed path proxy — how to spell URLs                                                          |
| `match(url)`| Pure matching against an arbitrary URL — no rendering or request context; root→leaf, `[]` if none |
| `routes`    | The config tree                                                                                   |
| `config`    | The full config — lets server integrations consume the instance directly                          |
| `keysFor(url)` | The query keys of the server component routes a URL shows, root→leaf — what to name in `revalidate` to refetch exactly those routes; accepts a `paths` node; works in server actions since it is pure matching |

## Route definitions

A route definition supports:

| key            | type                                                         | description                                                                     |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `path`         | `string \| string[]`                                         | Path partial for this route segment                                             |
| `component`    | `Component`                                                  | Component rendered for the matched segment                                      |
| `children`     | `RouteDefinition \| RouteDefinition[] \| () => Promise<...>` | Nested route definitions, or a thunk for a lazy subtree                         |
| `preload`      | `RoutePreloadFunc`                                           | Called on preload intent (hover/focus) and navigation                           |
| `matchFilters` | `MatchFilters`                                               | Additional constraints for matching parameters                                  |
| `search`       | `StandardSchemaV1`                                           | Search-param validator; its types flow into `paths` and hooks                   |
| `info`         | `Record<string, any>`                                        | Arbitrary metadata, readable via `useRouteMatches`                              |

The tree is immutable and there is one router per app — that is what makes `paths` and the typed hooks truthful, and it lets matching compile once and be shared by every mount, request, and `match()` call. Compose large apps by spreading subtrees into the config.

## defineRoutes / defineRoute

Wrap extracted route arrays in `defineRoutes` — an identity function that preserves the literal types inference feeds on (a bare extracted array silently widens to `string` paths without it or `as const`) and type-checks the definitions where they are written:

```tsx
// features/admin/routes.ts
export const adminRoutes = defineRoutes([
  { path: "/admin", component: Admin, children: [/* ... */] }
]);

// app/router.ts
export const Router = createRouter({ routes: [...appRoutes, ...adminRoutes] });
```

Its single-route sibling `defineRoute` also types `params` inside the route's own `component` and `preload` from the route's own `path`, and checks those params against the pattern:

```tsx
import { defineRoute } from "@solidjs/router";

const story = defineRoute({
  path: "/stories/:id/:tab?",
  preload: ({ params }) => getStory(params.id), // params.id: string
  component: props => (
    <Story
      id={props.params.id} // string — the pattern guarantees it
      tab={props.params.tab} // string | undefined — optional param
    />
  )
});
```

`defineRoute` is an identity function at runtime — the route object drops into `routes` (or a parent's `children`) like any plain object, and `path`, `children`, `matchFilters`, and `search` still flow into `paths` and the typed hooks. Params inherited from parent routes stay accessible as `string | undefined`; nested `children` type their own params only if they use `defineRoute` themselves.

## Typed route params

By default `params` is an open record — every key is `string | undefined`, even when the pattern guarantees it. For components declared away from their route, `RouteProps` takes a path witness — the same `paths` node you navigate with (`import type` keeps the instance out of the runtime graph, so no cycle) — plus an optional data type:

```tsx
import type { RouteComponent, RouteProps } from "@solidjs/router";
import type { Router } from "./app/router";

function Story(props: RouteProps<typeof Router.paths.stories, StoryData>) {
  props.params.id; // string
}

// component-type form — props infer contextually
const Story: RouteComponent<typeof Router.paths.stories, StoryData> = props => (
  <h1>{props.params.id}</h1>
);

// or, anywhere under the route:
const params = useParams(paths.stories); // typed from the tree
```

When no instance is in scope at the definition site — most notably file-system route files, where the pattern lives in the filename — the witness can be the pattern string itself: `RouteProps<"/stories/:id">`.

## Dynamic routes

Treat part of the path as a parameter with a colon:

```tsx
const routes = defineRoutes([
  { path: "/users", component: Users },
  { path: "/users/:id", component: User }
]);
```

As long as the URL fits the pattern, the `User` component shows, and `id` is available via `useParams`.

Routes that share the same path match are treated as the same route — param changes do not re-render. To force a re-render, wrap the component in a keyed `<Show>`:

```tsx
<Show when={params.something} keyed>
  <MyComponent />
</Show>
```

## Match filters

Each parameter can be validated with a `MatchFilter` — an enum array, a regex, or a predicate. If validation fails, the route doesn't match:

```tsx
import { int, type MatchFilters } from "@solidjs/router";

const filters: MatchFilters = {
  parent: ["mom", "dad"], // enum values
  id: /^\d+$/, // only numbers
  withHtmlExtension: (v: string) => v.length > 5 && v.endsWith(".html")
};

const routes = defineRoutes([
  { path: "/users/:parent/:id/:withHtmlExtension", component: User, matchFilters: filters }
]);
```

So `/users/mom/123/contact.html` matches, while `/users/aunt/123/contact.html` (invalid `parent`) and `/users/mom/me/contact.html` (non-numeric `id`) don't.

The built-in `int` filter is typed: it constrains matching to integers at runtime and types the param as `number` at `paths` callsites:

```tsx
{ path: "/users/:id", matchFilters: { id: int }, component: User }

paths.users(123);   // ok
paths.users("abc"); // type error
```

## Optional parameters

Add a question mark to make a parameter optional:

```tsx
// Matches stories and stories/123 but not stories/123/comments
{ path: "/stories/:id?", component: Stories }
```

## Wildcard routes

Use `*` to match any remainder of the path, optionally naming it to expose it as a parameter:

```tsx
{ path: "foo/*", component: Foo }     // matches foo/, foo/a, foo/a/b/c
{ path: "foo/*any", component: Foo }  // rest of the path available as params.any
```

The wildcard token must be the last part of the path; `foo/*any/bar` won't create any routes.

## Multiple paths

An array of paths lets a route stay mounted (no re-render) when switching between locations it matches:

```tsx
// Navigating from login to register does not re-render Login
{ path: ["login", "register"], component: Login }
```

## Nested routes

Only leaf nodes become routes. A parent with a `component` wraps its children, which render where the parent places `props.children`:

```tsx
function PageWrapper(props) {
  return (
    <div>
      <h1>We love our users!</h1>
      {props.children}
      <a href={paths()}>Back Home</a>
    </div>
  );
}

const routes = defineRoutes([
  {
    path: "/users",
    component: PageWrapper,
    children: [
      { path: "/", component: Users },
      { path: "/:id", component: User }
    ]
  }
]);
```

Nesting is unlimited — children render inside the parent's `props.children` placement.

## Lazy route subtrees

`children` also accepts a thunk, so a whole section's route table (not just its components) stays out of the initial bundle:

```tsx
// admin/routes.ts
export default defineRoutes([
  { path: "/", component: lazy(() => import("./Dashboard")) },
  { path: "/users/:id", matchFilters: { id: int }, component: lazy(() => import("./User")) }
]);

// app.ts
const router = createRouter({
  routes: [
    { path: "/", component: Home },
    { path: "/admin", component: AdminShell, children: () => import("./admin/routes") }
  ]
});
```

The import only fires when something needs the subtree — hovering a link into it, navigating into it, or the server matching a URL beneath it. Until then the tree carries a placeholder that knows every URL under `/admin` belongs to the subtree without knowing its contents (static sibling routes still win without triggering the load). Everything folds in as if the routes were inline:

- **Types** — TypeScript never runs the thunk; inference flows through the import's promise type, so `paths.admin.users(2)` typechecks (match filters and search schemas included) before any of the subtree's code exists client-side. The module's `default` or `routes` export is used. Only tables genuinely built at runtime (typed as plain `RouteDefinition[]`) degrade to untyped.
- **Navigation** — the table load folds into the navigation transition; the old screen holds until the subtree (and its matched components) are ready, exactly like a `lazy()` route component.
- **Preloading** — hover intent kicks the table load, and when it lands the preload continues into the inner routes' components and `preload` functions — one cascading warm-up from the earliest possible moment.
- **Server** — SSR resolves matched boundaries during the render (use the streaming entry point — awaiting it resolves with the settled HTML — as with any async work), and the single-flight collector resolves them before its data pass.

Resolution is cached per thunk and append-only: the tree never changes shape after a subtree lands, it just gets more specific. Keep thunks deterministic — `() => import(...)` — rather than switching tables on runtime state.

## Preload functions

Even with smart caches, waterfalls happen when data fetching waits on view logic or lazy-loaded code. Preload functions start fetching data in parallel with loading the route — called when a route renders, and eagerly when links are hovered or focused.

```tsx
import { lazy } from "solid-js";

const User = lazy(() => import("./pages/users/[id].js"));

function preloadUser({ params, location }) {
  void getUser(params.id);
}

const routes = defineRoutes([{ path: "/users/:id", component: User, preload: preloadUser }]);
```

The preload function receives:

| key      | type                                               | description                                                                                                                                                       |
| -------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `params`   | object                                            | The route parameters (same value as `useParams()` inside the route component)                                                                                     |
| `location` | `{ pathname, search, hash, query, state, key }`    | Path information (corresponds to `useLocation()`)                                                                                                                |
| `intent`   | `"initial" \| "navigate" \| "native" \| "preload"` | Why this is being called: `initial` — first render; `navigate` — router navigation; `native` — browser back/forward; `preload` — link hover/focus, not navigating |

The factory-level `preload` option is the app-wide counterpart: it runs once per mount/request with the merged params of every match, and its result reaches the root render-prop as `props.data`.

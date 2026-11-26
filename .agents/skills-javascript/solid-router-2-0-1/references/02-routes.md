# Route definitions

A route is a config object — the single source of truth for matching _and_ types:

| key            | type                                                         | description                                                                     |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `path`         | `string \| string[]`                                         | Path partial for this route segment                                             |
| `component`    | `Component`                                                  | Component rendered for the matched segment                                      |
| `children`     | `RouteDefinition \| RouteDefinition[] \| () => Promise<...>` | Nested route definitions, or a thunk for a lazy subtree                         |
| `preload`      | `RoutePreloadFunc`                                           | Called on link preloading and navigation                                        |
| `matchFilters` | `MatchFilters`                                               | Additional constraints for matching parameters                                  |
| `search`       | `StandardSchemaV1`                                           | Search-param validator; its types flow into `paths` and hooks                   |
| `info`         | `Record<string, any>`                                        | Arbitrary metadata, readable via `useRouteMatches`                              |

The tree is **immutable, one router per app** — that's what makes `paths` and the typed hooks truthful and lets matching compile once, shared by every mount, request, and `match()` call. Mounting a router inside another router is not supported (warns in dev). Compose large apps by spreading `defineRoutes` subtrees into one config.

## Dynamic routes

Colon marks a parameter; the URL fits the pattern as long as the param does:

```tsx
const routes = defineRoutes([
  { path: "/users", component: Users },
  { path: "/users/:id", component: User }
]);
```

Params are decoded: on `/users/%E7%8C%AB` (`/users/猫`), `id` is `"猫"`, and `matchFilters` see the decoded value. Each segment is decoded after matching, so an encoded slash stays inside its param (`/users/a%2Fb` gives `id: "a/b"`); a malformed escape is left as-is. `paths` encodes params on the way out, so `paths.users("猫")` round-trips. When building a URL from a param by hand, encode it (`encodeURIComponent`) or use `paths`. `location.pathname` keeps the URL's own encoding.

Routes that share the same path match are treated as the same route — to force a re-render on param change, wrap the component in a keyed `<Show when={...} keyed>`.

## Typed route params

By default `params` is an open record — every key is `string | undefined`, even when the pattern guarantees it. `defineRoute` is an identity function at runtime that types the route's own `component` and `preload` from its `path`:

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

Params inherited from parent routes stay accessible as `string | undefined`; nested `children` type their own params only if they use `defineRoute` themselves.

For components declared away from their route, `RouteProps` / `RouteComponent` take a paths-node witness (an `import type` keeps the instance out of the runtime graph, so no cycle) plus an optional data type:

```tsx
import type { RouteComponent, RouteProps } from "@solidjs/router";
import type { Router } from "./app/router";

function Story(props: RouteProps<typeof Router.paths.stories, StoryData>) {
  props.params.id; // string
}
```

With no instance in scope (file-system route files), the witness can be the pattern string itself: `RouteProps<"/stories/:id">`.

## Match filters

Each parameter can be validated with a `MatchFilter` — an enum array, a regex, or a predicate. If validation fails, the route doesn't match:

```tsx
import { int, type MatchFilters } from "@solidjs/router";

const filters: MatchFilters = {
  parent: ["mom", "dad"], // enum values
  id: /^\d+$/, // only numbers
  withHtmlExtension: (v: string) => v.length > 5 && v.endsWith(".html")
};
```

`/users/mom/123/contact.html` matches; `/users/aunt/123/...` (invalid `parent`) and `/users/mom/me/...` (non-numeric `id`) don't.

The built-in `int` filter is _typed_ — it constrains matching to integers at runtime and types the param as `number` at `paths` callsites:

```tsx
{ path: "/users/:id", matchFilters: { id: int }, component: User }

paths.users(123);   // ok
paths.users("abc"); // type error
```

## Optional parameters

A question mark makes a parameter optional — matches with and without the segment:

```tsx
// Matches stories and stories/123 but not stories/123/comments
{ path: "/stories/:id?", component: Stories }
```

## Wildcard routes

`*` matches any remainder of the path, optionally named to expose it as a parameter. The wildcard token must be the last part of the path — `foo/*any/bar` creates no routes:

```tsx
{ path: "foo/*", component: Foo }     // matches foo/, foo/a, foo/a/b/c
{ path: "foo/*any", component: Foo }  // rest of the path available as params.any
```

## Multiple paths

An array of paths keeps a route mounted (no re-render) when switching between locations it matches:

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

Nesting is unlimited — each layer just places `props.children` inside its own markup.

## Lazy route subtrees

`children` accepts a thunk, so a whole section's route table (not just its components) stays out of the initial bundle:

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

The import fires only when something needs the subtree — preloading a link into it, navigating into it, or the server matching a URL beneath it. Until then the tree carries a placeholder that knows every URL under `/admin` belongs to the subtree (static sibling routes still win without triggering the load). Everything folds in as if inline:

- **Types** — inference flows through the import's promise type, so `paths.admin.users(2)` typechecks before any subtree code exists client-side. The module's `default` or `routes` export is used; tables genuinely built at runtime (plain `RouteDefinition[]`) degrade to untyped.
- **Navigation** — the table load folds into the navigation transition; the old screen holds until the subtree and its matched components are ready, like a `lazy()` route component.
- **Preloading** — a link preload kicks the table load, then continues into the inner routes' components and `preload` functions.
- **Server** — SSR resolves matched boundaries during render (use `renderToStream` for streaming); the single-flight collector resolves them before its data pass.

Resolution is cached per thunk and append-only — the tree never changes shape after a subtree lands. Keep thunks deterministic (`() => import(...)`) rather than switching tables on runtime state.

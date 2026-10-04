# Server, File-System, and Other Environments

## Server integration

Framework handler wiring lives in `@solidjs/router/server`. The integration accepts the router instance directly — its routes, base, and preload are the single source of truth:

```tsx
import { createFlightDataCollector } from "@solidjs/router/server";
import { Router } from "./app/router";

const collectFlightData = createFlightDataCollector(Router);
```

`createFlightDataCollector` produces the single-flight hook: after a mutation it reruns the route data the mutation invalidated for the page the client is on (or is redirected to), folding fresh data into the same response. This policy previously lived inside SolidStart; the router now owns it, so custom server setups get single-flight mutations without a framework. It accepts config objects, an array, a thunk, or a router instance — no JSX trees.

The no-JS form convention needs no wiring at all: the server function runtime answers form posts made without the client runtime by redirecting back with the outcome in a one-shot flash cookie, and the router's SSR reads it into submission state. To configure it (e.g. a base path), pass `createNoJSHandler(options)` from `@solidjs/web/server-functions/server` as the handler's `handleNoJS`.

On the server the request URL drives rendering automatically. Without a request event (SSG scripts, server-side tests), the configured history adapter provides the location, so `memoryHistory("/page")` renders that page isomorphically.

## Server component routes (experimental)

Solid's experimental server components are `"use server"` functions that return a component. `serverRouteComponent` takes a `query` over one and uses it as a route's `component` directly — the router owns the URL → call translation:

```tsx
// story.tsx — the source owns its key
import { query, type ServerRouteArgs } from "@solidjs/router";

export const getStory = query(async ({ params }: ServerRouteArgs<{ id: string }>) => {
  "use server";
  const story = await db.stories.get(params.id);
  return props => (
    <article>
      <h1>{story.title}</h1>
      {props.children}
    </article>
  );
}, "story");

// routes.ts
defineRoute({ path: "/stories/:id", component: serverRouteComponent(getStory) });
```

The source is called with **derived** arguments, not a live location — the call's `(function, arguments)` address keys both the query cache and the frame store, so the args name exactly what the route depends on:

- `params`: the params this route's pattern (and its ancestors') declares — never a child's, so a layout does not refetch when a leaf param changes. `defineRoute` checks them against the pattern.
- `search`: the validated output of the route's `search` schema, only when one is declared. Otherwise `undefined`, and the route never tracks the query string.

A route view is route-shaped on purpose — the address stays stable and `defineRoute` can check its params against the pattern — which means it is only callable as a route. When the same server component is also used elsewhere, keep it a plain (non-exported, non-endpoint) function and have the route view call it with `params.id`. The value `serverRouteComponent` returns is a component only so it fits the `component` field; mounting it any other way (through `lazy()`, or by hand) throws.

The router mounts the resolved component with the outlet as `children`, so a server component can be a layout, and it calls the same source under preload intent — link hover, `preloadRoute`, the single-flight collector — with the same derived args. What that call means is the source's: the router does not choose the cache strategy or own the key.

- `query(fn, key)`: link intent warms the entry the render reads, `revalidate("story")` and action responses refetch it, and the collector reproduces it so a mutation's response carries the route's fresh markup. Argument changes deliver into the mounted boundary — it morphs in place rather than remounting.
- `liveQuery(fn, key)`: the frame stream stays open and the channel owns it — hover connects it (held through the preload window, so a hovered link is an open stream), `revalidate(key)` reconnects, and the mutation sweep and the single-flight collector both leave it alone.

Anything else callable with the args works too; wrapping is what gives dedupe, preload, and revalidation.

Mutations reach these routes the way they reach any query, and the cost model is worth knowing: a swept server route is a server-side re-render plus its markup in the response, not a small data blob. From a server action, `redirect(url)` re-collects everything the target shows and a bare `reload()` everything the current page shows — server routes included, shell and layouts too. On a server-component-heavy page, name what a mutation actually changed instead. `Router.keysFor(url)` answers the query keys of the server routes a URL shows, root to leaf — the app's own keys, from pure matching, so it works in an action and never spells a key:

```ts
export const addComment = action(async (form: FormData) => {
  "use server";
  await db.comments.add(form);
  return reload({ revalidate: Router.keysFor(paths.stories(form.get("id"))) });
});
```

Route keys, not addresses: every story page is refetched, which is what prefix matching gives a hand-written `revalidate("story")` too.

An app shell is a pathless layout route whose `component` is a server component. With no pattern, its args are the constant `{ params: {}, search: undefined }` — one call, one address, persisting across every navigation — and as a route it gets preload, collection, and `revalidate` like any other. The `<Router>` root slot exists for client providers that need router context without following route rules; a server component has neither, so it does not go there:

```tsx
const routes = [{ component: serverRouteComponent(query(appShell, "shell")), children: pages }];
render(() => <Router routes={routes} />, document.body);
```

`children` is the only client position the router fills, and the helper's type says so: a server component that requires other props — event handlers, refs, named slots — is rejected. Those come from the client, so that route has a client half; write it as an ordinary route component around `dynamic()`. Interaction that lives on the server — form posts to server actions via `action={addTodo}` — needs no client component at all.

## File-system routes

The `@solidjs/router/fs` adapter turns a `file-routes` manifest into route definitions — the app imports the virtual module, the adapter maps it:

```tsx
import { pageRoutes } from "virtual:file-routes";
import { fileRoutes } from "@solidjs/router/fs";

export const Router = createRouter({ routes: fileRoutes(pageRoutes) });
```

Route files export their component as `default` and everything else as a `route` config export, which is spread into the definition. Inside a route file the pattern lives in the filename, so there's no `paths` node to witness with at the definition site — `defineFileRoute` takes the pattern string instead, types `preload`'s params from it, and validates `matchFilters` along the way. The config then doubles as the component's `RouteProps` witness, typing `params` from the pattern and `data` from the `preload`'s return type:

```tsx
// routes/blog/[id].tsx
import { int } from "@solidjs/router";
import { defineFileRoute } from "@solidjs/router/fs";

export const route = defineFileRoute("/blog/:id", {
  matchFilters: { id: int },
  preload: ({ params }) => getPost(params.id) // params.id: string
});

export default function Post(props: RouteProps<typeof route>) {
  props.params.id; // string
  props.data; // ReturnType of the preload above
}
```

The pattern string is a typing witness — at runtime the manifest's path (from the filename) is the source of truth. With the plugin's `types` option generating a literal declaration for the virtual module, the file paths flow into `paths` and the typed hooks like a hand-written tree — `paths.blog(42)` typechecks, filters and search schemas included, and `useParams(paths.blog)` works as usual anywhere under the route.

### Server pages

A route file's page can be a server component: make the default export a `"use server"` function of the route args. With `fileRoutes({ serverComponents: true })` on the `file-routes` plugin, the scanner flags such a file and the adapter builds the route the hand-written tree spells out — `serverRouteComponent(query(fn, key))` with the file's path as the key. No `query`, key, or wrapper in the route file. (That option turns on server component routes; server components themselves are Solid's plugin's `serverFunctions: { components: true }`, the same switch a hand-written server route needs.)

```tsx
// routes/stories/[id].tsx
import { defineFileRoute } from "@solidjs/router/fs";
import type { ServerRouteArgs } from "@solidjs/router";

export const route = defineFileRoute("/stories/:id", { search: storySearch });

export default async function Story({ params, search }: ServerRouteArgs<typeof route>) {
  "use server";
  const story = await db.stories.get(params.id);
  return props => <article>{story.title}{props.children}</article>;
}
```

`ServerRouteArgs<typeof route>` reads the config as a witness like `RouteProps` does: `params` from the pattern, `search` as the schema's output (`undefined` with no schema). The key is the file — `Router.keysFor(paths.stories(7))` answers `["src/routes/stories/[id].tsx"]` (plus any server layouts above it), so an action names the page without spelling a path; because keys match by prefix, `revalidate("src/routes/stories")` refetches every page under the directory (pathless layouts have no route path of their own, so the file is what tells them apart). The directive has to be the first statement of the inline default export — behind a wrapper call or a re-export the scanner cannot see it, the page is code-split like a client page, and in development the adapter throws a directed error when the chunk resolves.

A live page names its wrapper in the `route` config — `defineFileRoute("/feed", { query: liveQuery })` — and the adapter sources through that instead of `query`. The route file imports `liveQuery`, so only an app with a live page carries it.

Apps with no server page pay nothing for any of this. The plugin folds the scan into `filesystem-routing/flags`, and the adapter's only path to `serverRouteComponent` and `query` is a module gated on that constant, so the branch — and with it the frames runtime — tree-shakes away.

## Other environments

History adapters are plain imports, so unused ones never enter your bundle:

```tsx
import { createRouter, hashHistory, memoryHistory } from "@solidjs/router";

// hash mode
const Router = createRouter({ routes, history: hashHistory() });

// tests and non-browser environments
const Router = createRouter({ routes, history: memoryHistory("/users/1") });
```

`memoryHistory(initialPath?)` carries `go`/`back`/`forward`/`listen` for tests and tools (it replaces 0.x's `createMemoryHistory`).

### Environments without Proxy

On runtimes without `Proxy` support (some older smart TVs), the core router still works: typed `paths` are built lazily so they only require `Proxy` if you access them, and `params`/`location.query` can be swapped to a `Proxy`-free implementation through the history adapter's `paramsWrapper`/`queryWrapper` utils:

```tsx
const base = browserHistory();
const history = {
  ...base,
  // wrappers build objects with defined getters instead of a Proxy
  utils: { ...base.utils, paramsWrapper, queryWrapper }
};
const Router = createRouter({ routes, history });
```

## Pure matching

The instance matches arbitrary URLs anywhere — server middleware, sitemap generation, tests — with no rendering involved:

```tsx
import { Router } from "./app/router";

Router.match("/users/2/settings?tab=x");
// [
//   { path: "/users/:id", match: "/users/2", params: { id: "2" } },
//   { path: "/settings", match: "/users/2/settings", params: {} }
// ]
```

# Server, file-system routes, and other environments

## Server component routes (experimental)

Solid's experimental server components are `"use server"` functions that return a component. `serverRouteComponent` takes a `query` over one and uses it as a route's `component` directly — the router owns the URL → call translation a client wrapper used to spell out:

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

A route view is route-shaped on purpose — mounting it any other way (through `lazy()`, or by hand) throws. The router mounts the resolved component with the outlet as `children`, so a server component can be a layout, and it calls the same source under preload intent (link preloading, `usePreloadRoute`, the single-flight collector) with the same derived args.

- `query(fn, key)`: link intent warms the entry the render reads; `revalidate("story")` and action responses refetch it; argument changes deliver into the mounted boundary — it morphs in place rather than remounting.
- `liveQuery(fn, key)`: the frame stream stays open and the channel owns it — a link preload connects it, `revalidate(key)` reconnects, and the mutation sweep and collector leave it alone.

The cost model for mutations is worth knowing: a swept server route is a server-side re-render plus its markup in the response, not a small data blob. From a server action, `redirect(url)` re-collects everything the target shows and a bare `reload()` everything the current page shows — server routes included. On a server-component-heavy page, name what a mutation actually changed: `Router.keysFor(url)` answers the query keys of the server routes a URL shows, root to leaf — from pure matching, so it works in an action and never spells a key:

```ts
export const addComment = formAction(async (form: FormData) => {
  "use server";
  await db.comments.add(form);
  return reload({ revalidate: Router.keysFor(paths.stories(form.get("id"))) });
});
```

An app shell is a pathless layout route whose `component` is a server component — with no pattern, its args are the constant `{ params: {}, search: undefined }`, one call persisting across every navigation:

```tsx
const routes = [{ component: serverRouteComponent(query(appShell, "shell")), children: pages }];
```

`children` is the only client position the router fills: a server component that requires other props (event handlers, refs, named slots) is rejected — write that route as an ordinary component around `dynamicComponent()`.

## File-system routes

The `@solidjs/router/fs` adapter turns a `file-routes` manifest into route definitions (peer dependency `filesystem-routing >=0.4.0`, optional):

```tsx
import { pageRoutes } from "virtual:file-routes";
import { fileRoutes } from "@solidjs/router/fs";

export const Router = createRouter({ routes: fileRoutes(pageRoutes) });
```

Route files export their component as `default` and everything else as a `route` config export, which is spread into the definition. Inside a route file the pattern lives in the filename, so `defineFileRoute` takes the pattern string as the witness and types `preload`'s params from it:

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

The pattern string is a typing witness — at runtime the manifest's path (from the filename) is the source of truth. With the plugin's `types` option generating a literal declaration for the virtual module, file paths flow into `paths` and the typed hooks — `paths.blog(42)` typechecks, filters and search schemas included.

A route file's page can be a server component: make the default export a `"use server"` function of the route args, with `fileRoutes({ serverComponents: true })` on the plugin. No `query`, key, or wrapper in the route file — the adapter builds `serverRouteComponent(query(fn, key))` with the file's path as the key, so `Router.keysFor(paths.stories(7))` answers `["src/routes/stories/[id].tsx"]`. The `"use server"` directive has to be the first statement of the inline default export — behind a wrapper call or re-export the scanner cannot see it, the page code-splits like a client page, and in development the adapter throws a directed error when the chunk resolves. A live page names its wrapper in the config — `defineFileRoute("/feed", { query: liveQuery })`.

Apps with no server page pay nothing: the adapter's only path to `serverRouteComponent` and `query` is a module gated on a scan constant, so the branch tree-shakes away.

## Server integration

Framework handler wiring lives in `@solidjs/router/server`. The integration accepts the router instance directly — its routes, base, and preload are the single source of truth:

```tsx
import { createFlightDataCollector } from "@solidjs/router/server";
import { Router } from "./app/router";

const collectFlightData = createFlightDataCollector(Router);
```

`createFlightDataCollector` produces the single-flight hook: after a mutation it reruns the route data the mutation invalidated for the page the client is on (or is redirected to), folding fresh data into the same response. This policy previously lived inside SolidStart; the router now owns it, so custom server setups get single-flight mutations without a framework.

The no-JS form convention needs no wiring: the server function runtime answers form posts made without the client runtime by redirecting back with the outcome in a one-shot flash cookie, and the router's SSR reads it into submission state. To configure it (e.g. a base path), pass `createNoJSHandler(options)` from `@solidjs/web/server-functions/server` as the handler's `handleNoJS`.

## Other environments

History adapters are plain imports, so unused ones never enter your bundle:

```tsx
import { createRouter, hashHistory, memoryHistory } from "@solidjs/router";

// hash mode
const Router = createRouter({ routes, history: hashHistory() });

// tests and non-browser environments
const Router = createRouter({ routes, history: memoryHistory("/users/1") });
```

On the server the request URL drives rendering automatically. Without a request event (SSG scripts, server-side tests), the configured history adapter provides the location, so `memoryHistory("/page")` renders that page isomorphically.

On runtimes without `Proxy` support (some older smart TVs), the core router still works: typed `paths` are built lazily so they only require `Proxy` if you access them, and `params`/`location.query` can be swapped to `Proxy`-free implementations through the history adapter's `paramsWrapper`/`queryWrapper` utils:

```tsx
const base = browserHistory();
const history = {
  ...base,
  // wrappers build objects with defined getters instead of a Proxy
  utils: { ...base.utils, paramsWrapper, queryWrapper }
};
const Router = createRouter({ routes, history });
```

Under Vite's `base`, pass `import.meta.env.BASE_URL` as the router `base` and link with `paths`, so links, `navigate()`, and `redirect()` follow it.

## SPAs in deployed environments

When deploying a client-side-routed application without SSR, handle redirects to the index page so loading other URLs doesn't 404.

On Netlify, create a `_redirects` file:

```
/*   /index.html   200
```

On Vercel, add a rewrites section to `vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

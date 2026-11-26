# Migration from 0.x and Deployment

This guide maps from the stable 0.x releases (Solid 1). The 2.x line removes the component-based API — the `createRouter` factory is the only way to set up the router, and plain `<a>` elements are the only link primitive. It also targets Solid 2, so the async data patterns change alongside the router API.

## Router components → createRouter

```tsx
// 0.x
<Router root={App}>
  <Route path="/users" component={Users} />
  <Route path="/users/:id" component={User} />
</Router>;

// 1.0+
const Router = createRouter({
  routes: [
    { path: "/users", component: Users },
    { path: "/users/:id", component: User }
  ]
});

<Router>{props => <App {...props} />}</Router>;
```

- `<HashRouter>` → `createRouter({ routes, history: hashHistory() })`
- `<MemoryRouter>` / `createMemoryHistory` → `createRouter({ routes, history: memoryHistory("/initial") })`
- `<StaticRouter url>` / `<Router url>` for SSR → automatic from the request URL; without a request event, pass `memoryHistory(url)`
- `root` prop → the render-prop child; `rootPreload` → the factory's `preload` option

## JSX Route → config objects

Route props map 1:1 onto definition keys (`path`, `component`, `preload`, `matchFilters`, `info`); nesting becomes `children` arrays. Wrap extracted route trees in `defineRoutes` to get typed `paths`. File-based routing generates config.

## A → plain a

- `<A href replace noScroll state>` → `<a href replace noscroll state>` (attributes, all lowercase)
- `activeClass` / `inactiveClass` → CSS attribute selectors on `[data-active]` / `[aria-current="page"]`
- `end` → style exact matches with `[aria-current="page"]` (which also compares the query) instead of `[data-active]`; the root path already only matches exactly
- Route-relative hrefs → typed `paths`; `useResolvedPath` / `useHref` remain for manual resolution
- Custom link components → `useLinkState`

## Removed and renamed

- `<Navigate>` → call `useNavigate()` during component setup, or redirect from a preload
- `useCurrentMatches` → `useRouteMatches` (same behavior)
- `redirect` / `reload` → import from `@solidjs/web`; they're protocol-level and work without the router
- `json(data, init)` → `respond(data, init)` from `@solidjs/web`
- `cache` (deprecated alias) → `query`
- `createMemoryHistory` → the `memoryHistory(initialPath)` adapter
- Removed outright: `<Router>`, `<HashRouter>`, `<MemoryRouter>`, `<StaticRouter>`, `createRouterComponent`, JSX `<Route>` (and its props type), `<A>`, `Navigate`
- `usePreloadRoute` keeps its name and now also accepts typed path nodes alongside strings and URLs

## Data APIs (Solid 2)

- `createAsync` / `createAsyncStore` are gone — read `query()` results with Solid 2 primitives: `createMemo`, `createProjection`, `createOptimistic`, `createOptimisticStore`.

```tsx
// 0.x
const user = createAsync(() => getUser(params.id));

// 1.0+
const user = createMemo(() => getUser(params.id));
```

- `query()` stays the source of truth for cached reads and invalidation.
- `useSubmission` (singular) is gone, and submissions are now settled history rather than in-flight state. Pending/optimistic UI moves to Solid's optimistic primitives fed by the action's `.onSubmit(...)` hook; read settled results with `useSubmissions()` and select the latest with `.at(-1)`.

```tsx
// 0.x — read in-flight state off the submission
const submitting = useSubmission(addTodo);
<span>{submitting.pending && "Saving..."}</span>;

// 1.0+ — optimistic primitives own in-flight state
const [todos, setTodos] = createOptimisticStore(() => getTodos(), []);
const addTodo = action(saveTodo).onSubmit(todo =>
  setTodos(items => {
    items.push({ ...todo, pending: true });
  })
);
```

- Action lifecycle centers on instance methods: `.onSubmit(...)` for owner-scoped optimistic work, `.onSettled(...)` for observing completions. Returned values are the expected result channel; thrown errors land on `Submission.error`.

## SPAs in deployed environments

When deploying a client-side-routed application without server-side rendering, you need to handle redirects to your index page so that loading other URLs doesn't return a 404.

On Netlify, create a `_redirects` file:

```sh
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

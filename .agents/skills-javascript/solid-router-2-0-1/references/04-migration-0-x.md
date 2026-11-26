# Migration from 0.x

This maps from the stable 0.x releases (Solid 1). 2.0 removes the component-based API — the `createRouter` factory is the only way to set up the router, and plain `<a>` elements are the only link primitive. The 2.x line also targets Solid 2, so the async data patterns change alongside the router API.

## Router components → `createRouter`

```tsx
// 0.x
<Router root={App}>
  <Route path="/users" component={Users} />
  <Route path="/users/:id" component={User} />
</Router>;

// 2.x
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

## JSX `<Route>` → config objects

Route props map 1:1 onto definition keys (`path`, `component`, `preload`, `matchFilters`, `info`); nesting becomes `children` arrays. Wrap extracted route trees in `defineRoutes` to get typed `paths`. File-based routing generates config.

## `<A>` → plain `<a>`

- `<A href replace noScroll state>` → `<a href replace noscroll state>` (attributes, all lowercase)
- `activeClass` / `inactiveClass` → CSS attribute selectors on `[data-active]` / `[aria-current="page"]`
- `end` → style exact matches with `[aria-current="page"]` (which also compares the query) instead of `[data-active]`; the root path already only matches exactly
- Pending link styling → `[data-pending]`, opt-in with `createRouter({ routes, links: pendingLinks })`
- Route-relative hrefs → typed `paths`; `useResolvedPath` / `useHref` remain for manual resolution
- Custom link components → `useLinkState`
- Hover/focus preloading is opt-in → `createRouter({ routes, preloadLinks: intentPreload() })`; `preload="false"` on a link skips it entirely. `<A>` preloaded on hover by default

## Removed and renamed

- `<Navigate>` → call `useNavigate()` during component setup, or redirect from a preload
- `useCurrentMatches` → `useRouteMatches` (same behavior)
- `redirect` / `reload` → import from `@solidjs/web`; they're protocol-level and work without the router
- `json(data, init)` → `respond(data, init)` from `@solidjs/web`
- `cache` (deprecated alias) → `query`
- `action` → `formAction` (`Action` → `FormAction`); the old names remain as deprecated aliases with a dev warning — `action` is solid-js's own primitive
- `useAction` → deprecated with no replacement; call the server function or a core `action` directly
- `RouterContext`'s `isRouting` / `pendingTarget` → `useIsRouting()`; for the in-flight destination, use the `isPending`/`latest` recipe on the location (see [01-hooks-and-paths](01-hooks-and-paths.md))

## Data APIs (Solid 2)

`createAsync` / `createAsyncStore` are gone — read `query()` results with Solid 2 primitives: `createMemo`, `createProjection`, `createOptimistic`, `createOptimisticStore`.

```tsx
// 0.x
const user = createAsync(() => getUser(params.id));

// 2.x
const user = createMemo(() => getUser(params.id));
```

- `query()` stays the source of truth for cached reads and invalidation.
- `useSubmission` (singular) is gone; submissions are now settled history rather than in-flight state. Pending/optimistic UI moves to Solid's optimistic primitives fed by the action's `.onSubmit(...)` hook; read settled results with `useSubmissions()` and select the latest with `.at(-1)` (clear old records in `.onSubmit` when a form shows only its latest outcome).

```tsx
// 0.x — read in-flight state off the submission
const submitting = useSubmission(addTodo);
<span>{submitting.pending && "Saving..."}</span>;

// 2.x — optimistic primitives own in-flight state
const [todos, setTodos] = createOptimisticStore(() => getTodos(), []);
const addTodo = formAction(saveTodo).onSubmit(todo =>
  setTodos(items => {
    items.push({ ...todo, pending: true });
  })
);
```

Action lifecycle centers on instance methods: `.onSubmit(...)` for owner-scoped optimistic work, `.onSettled(...)` for observing completions. Returned values are the expected result channel; thrown errors land on `Submission.error`.

## Version numbering

The Solid 2 prerelease line was renumbered from `1.0.0-next.*` to `2.0.0-next.*`: the 0.16 line was declared stable as `1.0.0`, so the 1.x majors belong to the Solid 1 router and this line continues under 2.x, matching Solid 2's major. If you tracked the `next` tag with a `^1.0.0-next.*` range, update it to `2.0.0-next.*` — otherwise a stable `1.x` will eventually satisfy it and hand you the Solid 1 router.

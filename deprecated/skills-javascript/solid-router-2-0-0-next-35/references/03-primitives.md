# Router Primitives

Hooks read the live session off router context. They must be used inside a component rendered by the router.

## useParams

Retrieves a reactive, store-like object of the current route's path parameters. Pass a paths node for typing:

```tsx
const params = useParams(); // Params (strings)
const params = useParams(paths.users); // { id: string } — typed from the tree
```

Inside a route's own `component`/`preload`, `defineRoute` types `props.params` without a witness.

## useNavigate

Retrieves a method to navigate. Accepts a string or a typed path node, plus options:

- `resolve` (_boolean_, default `true`): resolve the path against the current route
- `replace` (_boolean_, default `false`): replace the history entry
- `scroll` (_boolean_, default `true`): scroll to top after navigation
- `state` (_any_): pass custom state to `location.state` (serialized with structured clone)

```tsx
const navigate = useNavigate();
navigate(paths.login, { replace: true });
```

For declarative redirects on render (the old `<Navigate>`), call it during component setup or redirect from a preload.

## useLocation

Retrieves the reactive `location` object:

```tsx
const location = useLocation();
const pathname = createMemo(() => parsePath(location.pathname));
```

## useSearchParams

See [typed search params](#typed-search-params) — a route's `search` schema (Standard Schema validator) types reads and writes:

```tsx
const [search, setSearch] = useSearchParams(paths.search);
search.page; // number (parsed, not "2")
setSearch({ page: search.page + 1 }); // typed setter
```

Without a schema, `useSearchParams()` behaves as before: raw string values, merge-on-set semantics (`''`, `undefined`, and `null` remove keys), navigation-like updates with auto-scrolling disabled. Reads are proxied — access properties to subscribe.

## useIsRouting

A signal indicating whether the router is processing a navigation — useful for pending UI while the next route and its data settle:

```tsx
const isRouting = useIsRouting();
return <div classList={{ "grey-out": isRouting() }}>...</div>;
```

In Solid's dev and observe builds the router also declares every navigation to the attribution engine (`solid-js/attribution`): holds and re-runs caused by a navigation are named after the route pattern, timed from the user event that started it, and redirect hops fold onto the navigation they belong to. Nothing of this exists in production builds.

## useMatch

Tests a path _pattern you supply_ against the current location; returns a memo of match information or `undefined`. It never consults the route tree — the pattern doesn't have to correspond to a defined route. The match's `params` are typed from the pattern, and a typed path node works too (a concrete URL — useful for "am I here" checks):

```tsx
const match = useMatch(() => "/admin/*rest");
match()?.params.rest; // string
return <Show when={match()}>...</Show>;

const here = useMatch(() => paths.users(2));
```

## useRouteMatches

Returns an accessor of the router's _resolved_ matches for the current location — the chain of route definitions producing the current render, outermost first. This is the counterpart to `useMatch`: one reflects the route tree, the other tests a pattern. Useful for reading `info` metadata:

```tsx
const matches = useRouteMatches();
const breadcrumbs = createMemo(() => matches().map(m => m.route.info?.breadcrumb));
```

`info` is freeform by default; augment `RouteInfo` to type it app-wide — declared keys are checked at route definitions and typed on reads:

```ts
declare module "@solidjs/router" {
  interface RouteInfo {
    breadcrumb?: string;
  }
}
```

(`useRouteMatches` is the 1.0 rename of `useCurrentMatches` — same behavior.)

## usePreloadRoute

Returns a function to preload a route manually — the same work link hover/focus triggers automatically. Accepts strings, URLs, and typed path nodes:

```tsx
const preload = usePreloadRoute();
preload(paths.users(2).settings, { preloadData: true });
```

## useBeforeLeave

Takes a function called before leaving a route. The blocking machinery is installed lazily on first use, so apps that never call `useBeforeLeave` don't pay for it in their bundle. The handler receives:

- `from` (_Location_): current location (before change)
- `to` (_string | number_): path passed to `navigate`
- `options` (_NavigateOptions_): options passed to `navigate`
- `preventDefault()`: call to block the route change
- `defaultPrevented` (_readonly boolean_): `true` if any previous handler called `preventDefault`
- `retry(force?)`: retry the navigation, e.g. after confirming with the user; pass `true` to skip re-running leave handlers

```tsx
useBeforeLeave((e: BeforeLeaveEventArgs) => {
  if (form.isDirty && !e.defaultPrevented) {
    e.preventDefault();
    setTimeout(() => {
      if (window.confirm("Discard unsaved changes - are you sure?")) {
        e.retry(true);
      }
    }, 100);
  }
});
```

## useResolvedPath / useHref

Remaining from 0.x for manual path resolution. Prefer typed `paths` for route-relative hrefs; use these when resolving a raw string against the current location without the route tree.

## RouterContext

`RouterContext` (exported from `@solidjs/router`) is the context object that hooks read — useful for building integrations that need the live router from outside a component.

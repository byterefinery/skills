# Hooks and typed paths

The router's two surfaces. **Instance** — shared, non-stateful, facts about the _app_ (`paths`, `match(url)`, `routes`, `config`). **Hooks** — facts about the _live session_, read from router context. The line: could two concurrent server requests give different answers? If yes, it's a hook.

```tsx
const navigate = useNavigate();
navigate(paths.users(2)); // verb(noun) — the instance supplies a typed URL, the hook acts

const params = useParams(paths.users); // hook, typed by the instance
```

Hooks are the default: a component that only reads its session (params, location, string-path navigation) never needs the router instance, so component files don't form import cycles with the router module.

## Instance members

| member   | description                                                                                       |
| -------- | ------------------------------------------------------------------------------------------------- |
| `paths`  | The typed path proxy — see below                                                                  |
| `match`  | Pure matching against an arbitrary URL — no rendering or request context; root→leaf, `[]` if none |
| `routes` | The config tree                                                                                   |
| `config` | The full config — lets server integrations consume the instance directly                          |

`Router.match(url)` works anywhere — server middleware, sitemap generation, tests:

```tsx
Router.match("/users/2/settings?tab=x");
// [
//   { path: "/users/:id", match: "/users/2", params: { id: "2" } },
//   { path: "/settings", match: "/users/2/settings", params: {} }
// ]
```

## Typed paths

`paths` is a proxy inferred from the route tree. Property access descends static segments, calls bind params, and it mirrors URL anatomy — params, then a search object, then a hash string:

```tsx
paths.users(123); // ok — matchFilters flow into the callsite
paths.users(2).settings; // chainable into children
paths.users(2, { tab: "x" }, "comments"); // "/users/2?tab=x#comments"
paths.about(); // zero-arg/search calls terminate to a plain string
paths(); // "/" — the root
```

- Every node coerces via `toString`, so nodes drop straight into `href`, `navigate()`, and `redirect()` without explicit termination.
- Nodes include the router's `base` — they are the portable way to link under one. A plain string starting with `/` is a full path everywhere; the base is never added to it.
- Accessing a segment that doesn't exist in the tree, or binding a param with the wrong type, is a compile error.

## useParams

Reactive, store-like object of the current route's path parameters. Pass a paths node for typing:

```tsx
const params = useParams(); // Params (strings)
const params = useParams(paths.users); // { id: string }
```

## useNavigate

Navigate method. Accepts a string or a typed path node, plus options:

- `resolve` (default `true`): resolve the path against the current route
- `replace` (default `false`): replace the history entry
- `scroll` (default `true`): scroll to top after navigation
- `state` (any): custom state for `location.state` (structured clone)

A string starting with `/` is a full path — under `base: "/app"`, `navigate("/about")` goes to `/about`, not `/app/about`. A full path outside the base is another document, so `navigate()` loads it. For declarative redirects on render (the old `<Navigate>`), call it during component setup or redirect from a preload.

## useLocation

Reactive `location` object (`pathname`, `search`, `hash`, `query`, `state`, `key`):

```tsx
const location = useLocation();
const pathname = createMemo(() => parsePath(location.pathname));
```

## useInRouter

Returns `true` under a router, `false` elsewhere. The other primitives throw outside a router, so a component that also renders outside one (an error fallback above the router) can check first. Reads from the reactive owner — call during component setup, not from an event handler:

```tsx
const location = useInRouter() ? useLocation() : undefined;
```

## useSearchParams

See typed search params in [03-data-and-preloading](03-data-and-preloading.md). Reads are proxied — access properties to subscribe.

## useIsRouting

Signal indicating whether the router is processing a navigation — pending UI while the next route and its data settle. It's the way to read routing state. The router doesn't expose where a navigation is heading; read it off the location with Solid's `isPending` and `latest` (covers back/forward too):

```tsx
import { isPending, latest } from "solid-js";

const location = useLocation();
const target = () =>
  isPending(() => location.pathname) ? latest(() => location.pathname) : undefined;
```

## useMatch

Tests a path _pattern you supply_ against the current location; returns a memo of match information or `undefined`. Never consults the route tree — the pattern doesn't have to correspond to a defined route. `params` are typed from the pattern; a typed path node works too (concrete-URL "am I here" checks):

```tsx
const match = useMatch(() => "/admin/*rest");
match()?.params.rest; // string

const here = useMatch(() => paths.users(2));
```

## useRouteMatches

Accessor of the router's _resolved_ matches for the current location — the chain of route definitions producing the current render, outermost first (renamed from 0.x `useCurrentMatches`). Useful for reading `info` metadata, which is freeform by default — augment `RouteInfo` to type it app-wide:

```ts
declare module "@solidjs/router" {
  interface RouteInfo {
    breadcrumb?: string;
  }
}
```

```tsx
const matches = useRouteMatches();
const breadcrumbs = createMemo(() => matches().map(m => m.route.info?.breadcrumb));
```

## usePreloadRoute

Preload a route manually — the same work link preloading triggers automatically. Accepts strings, URLs, and typed path nodes:

```tsx
const preload = usePreloadRoute();
preload(paths.users(2).settings, { preloadData: true });
```

## useLinkState

Reactive `active`/`current`/`pending` state for custom link components, matched by the same rule as plain anchors:

- `current()` — same path and same query, ignoring parameter order and the hash (what `aria-current="page"` reflects)
- `active()` — the location's path is the link's path or lives under it, query ignored (`data-active`); a root link (the router's `base`, or `/` without one) is exact-only
- `pending()` — the link's path is the target of an in-flight navigation, back/forward excluded (`data-pending`). Works without the `pendingLinks` plugin, which only adds the attribute to plain anchors

Pass `{ end: true }` to make `active` (and `pending`) exact-path for any link:

```tsx
import { useLinkState } from "@solidjs/router";

function TabLink(props: { href: string; children: JSX.Element }) {
  const link = useLinkState(() => props.href);
  return (
    <a href={props.href} class="tab" data-selected={link.active() || undefined}>
      {props.children}
    </a>
  );
}
```

## useBeforeLeave

Handler called before leaving a route. The blocking machinery is installed lazily on first use — apps that never call it don't ship it. The handler receives `from` (current location), `to` (path passed to `navigate`), `options` (NavigateOptions), `preventDefault()`, `defaultPrevented` (readonly), and `retry(force?)` (retry the navigation, e.g. after confirming — `true` skips re-running leave handlers):

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

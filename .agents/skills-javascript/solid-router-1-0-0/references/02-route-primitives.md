# Router Primitives

All primitives read from the Router/Route context and must be used inside a route component or the root layout.

## `useParams`

Returns a reactive store of path parameters.

```tsx
import { useParams } from "@solidjs/router";

function User() {
  const params = useParams();
  return <h1>User: {params.id}</h1>;
}
```

Access properties reactively: `params.id` creates a subscription. The store merges params from all matched route segments.

## `useNavigate`

Returns a navigation function.

```tsx
import { useNavigate } from "@solidjs/router";

const navigate = useNavigate();

// Absolute path
navigate("/dashboard");

// Relative to current route
navigate("../settings");

// With options
navigate("/login", { replace: true, scroll: true, state: { from: "/dashboard" } });

// Go back/forward
navigate(-1);
navigate(1);
```

Options:
- `resolve` (default `true`): resolve relative to current route
- `replace` (default `false`): replace history entry instead of pushing
- `scroll` (default `true`): scroll to top after navigation
- `state`: serializable value pushed to history (uses structured clone algorithm)

## `useLocation`

Returns the reactive location object.

```tsx
import { useLocation } from "@solidjs/router";

const location = useLocation();

const pathname = () => location.pathname;
const search = () => location.search;
const hash = () => location.hash;
const query = () => location.query;      // parsed query params
const state = () => location.state;       // history state
```

| Property | Type | Description |
|----------|------|-------------|
| `pathname` | `string` | URL path |
| `search` | `string` | Raw query string (includes `?`) |
| `hash` | `string` | URL hash (includes `#`) |
| `query` | `SearchParams` | Parsed query parameters |
| `state` | `unknown` | History state |
| `key` | `string` | Unique navigation key |

## `useSearchParams`

Returns a tuple of reactive search params and a setter.

```tsx
import { useSearchParams } from "@solidjs/router";

const [params, setParams] = useSearchParams();

// Read (values are always strings)
const page = parseInt(params.page || "1");

// Update (merges with existing params)
setParams({ page: String(page + 1), filter: "active" });

// Remove a key
setParams({ page: "" });
setParams({ page: null });
setParams({ page: undefined });

// With navigation options
setParams({ page: "2" }, { replace: true });
```

Values are always strings. Property names retain their casing. Setter accepts the same options as `navigate()` (minus `scroll` which defaults to `false` for param-only updates).

## `useIsRouting`

Returns a signal indicating whether a route transition is in progress.

```tsx
import { useIsRouting } from "@solidjs/router";

const isRouting = useIsRouting();

return (
  <div classList={{ "opacity-50": isRouting() }}>
    <Suspense fallback={<Spinner />}>
      <MyContent />
    </Suspense>
  </div>
);
```

Useful for showing loading states, grey-out effects, or disabling interactions during navigation.

## `useMatch`

Tests if a given path matches the current location.

```tsx
import { useMatch } from "@solidjs/router";

const match = useMatch(() => "/users/:id");

// Returns { params, path } or null
if (match()) {
  console.log(match().params.id);
}
```

Accepts match filters as a second argument:

```tsx
const match = useMatch(() => "/users/:id", { id: /^\d+$/ });
```

Useful for custom active state logic, conditional rendering, or analytics tracking.

## `useCurrentMatches`

Returns all matched route segments for the current location.

```tsx
import { useCurrentMatches } from "@solidjs/router";

const matches = useCurrentMatches();

// Build breadcrumbs from route info
const breadcrumbs = createMemo(() =>
  matches().map(m => m.route.info.breadcrumb)
);
```

Each match has `route` (the route definition with `info`), `params`, and `path`. Store custom data in `info` on `<Route info={{ breadcrumb: "Users" }}>` and retrieve it here.

## `useBeforeLeave`

Registers a handler called before leaving the current route.

```tsx
import { useBeforeLeave } from "@solidjs/router";

useBeforeLeave((e) => {
  if (form.isDirty && !e.defaultPrevented) {
    e.preventDefault(); // block immediately
    setTimeout(() => {
      if (window.confirm("Discard unsaved changes?")) {
        e.retry(true); // force navigate, skip handlers again
      }
    }, 100);
  }
});
```

Event args:
- `from`: current `Location` (before change)
- `to`: path passed to `navigate`
- `options`: navigation options
- `defaultPrevented`: `true` if any handler called `preventDefault()`
- `preventDefault()`: block the navigation
- `retry(force?)`: retry the navigation; pass `true` to skip handlers

Subscription auto-cleans on component unmount.

## `usePreloadRoute`

Returns a function for manual route preloading.

```tsx
import { usePreloadRoute } from "@solidjs/router";

const preload = usePreloadRoute();

// Preload route component and data
preload("/users/settings", { preloadData: true });

// Preload just the component
preload("/users/settings");
```

This is what happens automatically on link hover when `preload` is enabled. Exposed as an API for manual control.

## `useResolvedPath`

Resolves a path relative to the current route.

```tsx
import { useResolvedPath } from "@solidjs/router";

const resolved = useResolvedPath(() => "../settings");
// Returns a Memo with the absolute path
```

## `useHref`

Converts a resolved path to the final href (including base path).

```tsx
import { useHref, useResolvedPath } from "@solidjs/router";

const to = useResolvedPath(() => props.href);
const href = useHref(to);
// href() includes base path for correct <a> rendering
```

## `useRouter` / `useRoute`

Access the raw router or route context.

```tsx
import { useRouter, useRoute } from "@solidjs/router";

const router = useRouter(); // RouterContext — location, params, isRouting, etc.
const route = useRoute();   // RouteContext — pattern, path, outlet, resolvePath
```

Consider these opaque and internal — they may change. Use the named primitives above for stable APIs.

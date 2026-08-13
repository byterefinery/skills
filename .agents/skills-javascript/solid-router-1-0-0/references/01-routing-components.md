# Routing Components

## `<Router>`

The main router component. Wraps all route definitions.

```tsx
import { Router, Route } from "@solidjs/router";

<Router root={AppLayout} base="/app" preload={true}>
  <Route path="/" component={Home} />
  <Route path="/users" component={Users} />
</Router>
```

| Prop | Type | Description |
|------|------|-------------|
| `children` | `JSX.Element`, `RouteDefinition`, `RouteDefinition[]` | Route definitions as JSX or config objects |
| `root` | `Component<RouteSectionProps>` | Top-level layout wrapping all routes |
| `rootPreload` | `RoutePreloadFunc` | Preload function for the root layout |
| `base` | `string` | Base URL prefix for all routes |
| `actionBase` | `string` | Root URL for server actions (default: `/_server`) |
| `preload` | `boolean` | Enable/disable preloads globally (default: `true`) |
| `explicitLinks` | `boolean` | Require `<A>` for intercepted links (default: `false`) |
| `singleFlight` | `boolean` | Deduplicate concurrent requests (default: `true`) |
| `transformUrl` | `(url: string) => string` | Transform URL before matching |

SSR usage: `<Router url={isServer ? req.url : ""} />`.

## `<Route>`

Defines a single route segment.

```tsx
<Route path="/users/:id" component={User} preload={loadUser} />
```

| Prop | Type | Description |
|------|------|-------------|
| `path` | `string` or `string[]` | Path pattern(s). Array keeps component mounted across paths |
| `component` | `Component<RouteSectionProps>` | Component rendered when route matches |
| `preload` | `RoutePreloadFunc` | Function called during preload/navigation |
| `matchFilters` | `MatchFilters` | Validation constraints for path parameters |
| `children` | `JSX.Element` | Nested `<Route>` definitions |
| `info` | `Record<string, any>` | Arbitrary metadata accessible via `useCurrentMatches()` |

### Path patterns

- **Static**: `/about`, `/users/settings`
- **Dynamic**: `/users/:id` — matches any value, accessible via `useParams()`
- **Optional**: `/stories/:id?` — matches both `/stories` and `/stories/123`
- **Wildcard**: `foo/*` — matches `foo/`, `foo/a`, `foo/a/b/c`
- **Named wildcard**: `foo/*rest` — wildcard captured as `params.rest`
- **Multiple paths**: `path={["login", "register"]}` — same component, stays mounted

### Match filters

```tsx
import type { MatchFilters } from "@solidjs/router";

const filters: MatchFilters = {
  parent: ["mom", "dad"],           // enum values
  id: /^\d+$/,                       // regex
  ext: (v) => v.endsWith(".html"),   // function
};

<Route
  path="/users/:parent/:id/:ext"
  component={User}
  matchFilters={filters}
/>
```

If validation fails, the route doesn't match.

## `<A>`

Router-aware anchor with active state and relative path resolution.

```tsx
import { A } from "@solidjs/router";

<A href="/users" activeClass="active" inactiveClass="inactive">Users</A>
<A href="/" end activeClass="active">Home</A>
<A href="/users" replace noScroll>Users (no history)</A>
```

| Prop | Type | Description |
|------|------|-------------|
| `href` | `string` | Route path (resolved relative to current route; prefix `/` for absolute) |
| `activeClass` | `string` | Class when active (default: `"active"`) |
| `inactiveClass` | `string` | Class when inactive (default: `"inactive"`) |
| `end` | `boolean` | Match exactly (no descendants); essential for root `/` links |
| `replace` | `boolean` | Don't add history entry |
| `noScroll` | `boolean` | Skip auto-scroll to top |
| `state` | `unknown` | Push value to history stack |

`<A>` sets `aria-current="page"` on exact match. Regular `<a>` tags are intercepted by default unless `target` is set or `explicitLinks` is enabled on `<Router>`.

## `<Navigate>`

Immediately navigates when rendered.

```tsx
import { Navigate } from "@solidjs/router";

// Simple redirect
<Navigate href="/dashboard" />

// Dynamic redirect
<Navigate href={({ navigate, location }) => {
  return location.state?.from || "/";
}} />
```

| Prop | Type | Description |
|------|------|-------------|
| `href` | `string` or `({ navigate, location }) => string` | Path or function returning path |
| `state` | `unknown` | History state to push |

Useful for post-authentication redirects, conditional routing, or redirect components.

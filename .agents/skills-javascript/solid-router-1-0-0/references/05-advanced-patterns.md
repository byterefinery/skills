# Advanced Patterns

## Preload Functions

Preload functions start data fetching in parallel with route loading, following the render-as-you-fetch pattern.

```tsx
import { Route } from "@solidjs/router";

function preloadUser({ params, location, intent }) {
  // intent: "initial" | "navigate" | "native" | "preload"
  console.log("Preloading user", params.id, "intent:", intent);

  // Fetch data
  return fetch(`/api/users/${params.id}`).then(r => r.json());
}

<Route path="/users/:id" component={User} preload={preloadUser} />;
```

The preload function receives:

| Property | Type | Description |
|----------|------|-------------|
| `params` | `Params` | Route parameters (same as `useParams()`) |
| `location` | `Location` | Target location info (pathname, search, hash, query, state) |
| `intent` | `Intent` | `"initial"` (page load), `"navigate"` (router nav), `"native"` (back/forward), `"preload"` (hover) |

The return value is passed to the component as `props.data` for all intents except `"preload"`. During hover-only preloads, the data is fetched but not passed to the component.

### Dedicated data files

```tsx
// pages/users/[id].data.ts
import { query } from "@solidjs/router";

export const getUser = query(async (id) => {
  return (await fetch(`/api/users/${id}`)).json();
}, "users");

export default function preload({ params }) {
  void getUser(params.id);
}

// pages/users/[id].tsx
import preload from "./[id].data";
import { getUser } from "./[id].data";

export default function User(props) {
  const user = createAsync(() => getUser(props.params.id));
  return <h1>{user()?.name}</h1>;
}

// routes.tsx
<Route path="/users/:id" component={User} preload={preload} />;
```

Separate data logic into `.data.ts` files so they can be imported without loading the component.

## Config-Based Routing

Define routes as objects instead of JSX:

```tsx
import { lazy } from "solid-js";
import { Router } from "@solidjs/router";

const routes = [
  {
    path: "/",
    component: lazy(() => import("/pages/index.js")),
  },
  {
    path: "/users",
    component: lazy(() => import("/pages/users.js")),
    children: [
      {
        path: "/",
        component: lazy(() => import("/pages/users/index.js")),
      },
      {
        path: "/:id",
        component: lazy(() => import("/pages/users/[id].js")),
        children: [
          {
            path: "/settings",
            component: lazy(() => import("/pages/users/[id]/settings.js")),
          },
          {
            path: "/*all",
            component: lazy(() => import("/pages/users/[id]/[...all].js")),
          },
        ],
      },
    ],
  },
  {
    path: "/*all",
    component: lazy(() => import("/pages/[...all].js")),
  },
];

<Router>{routes}</Router>;
```

Route definition objects support:
- `path`: string or string[]
- `component`: route component
- `preload`: preload function
- `matchFilters`: param validation
- `children`: nested route definitions
- `info`: arbitrary metadata

Single route objects are also accepted: `<Router>{routeDef}</Router>`.

## Alternative Routers

### HashRouter

Uses `location.hash` for routing. Useful when the server cannot handle arbitrary paths.

```tsx
import { HashRouter, Route } from "@solidjs/router";

<HashRouter>
  <Route path="/" component={Home} />
  <Route path="/about" component={About} />
</HashRouter>
```

URLs look like `example.com/#/about`.

### MemoryRouter

Uses in-memory history. Useful for testing in non-browser environments.

```tsx
import { MemoryRouter, Route } from "@solidjs/router";

<MemoryRouter>
  <Route path="/" component={Home} />
</MemoryRouter>
```

### StaticRouter (SSR)

For server-side rendering. The `<Router>` defaults to static mode on the server.

```tsx
import { isServer } from "solid-js/web";
import { Router } from "@solidjs/router";

<Router url={isServer ? req.url : ""}>
  <Route path="/" component={Home} />
</Router>
```

Pass the request URL to the `url` prop for correct route matching on the server.

## Match Filters

Validate path parameters against constraints:

```tsx
import type { MatchFilters } from "@solidjs/router";

const filters: MatchFilters = {
  // Enum — only these values match
  role: ["admin", "user", "moderator"],

  // Regex — matches the pattern
  id: /^\d{4,}$/,

  // Function — custom validation
  slug: (value) => value.length > 3 && /^[a-z-]+$/.test(value),
};

<Route
  path="/admin/:role/:id/:slug"
  component={AdminPage}
  matchFilters={filters}
/>
```

If validation fails, the route silently doesn't match. The next route in priority order is tried.

## SPA Deployment

Client-side routers need the server to redirect all paths to `index.html`:

### Netlify

Create `_redirects`:
```
/*  /index.html  200
```

### Vercel

Add to `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Nginx

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

### Apache

In `.htaccess`:
```
FallbackResource /index.html
```

## Root Layout Preload

The `root` component can have its own preload function:

```tsx
<Router root={AppLayout} rootPreload={preloadAppData}>
  <Route path="/" component={Home} />
</Router>
```

`rootPreload` receives the same `{ params, location, intent }` args. Its return value is passed as `props.data` to the root layout component.

## Explicit Links Mode

By default, all `<a>` tags with internal hrefs are intercepted by the router. Enable `explicitLinks` to require `<A>` for client-side navigation:

```tsx
<Router explicitLinks={true}>
  <Route path="/" component={Home} />
</Router>
```

With `explicitLinks`, plain `<a>` tags do full page reloads. Only `<A>` uses client-side navigation.

To disable interception for a specific link without `explicitLinks`, set any `target` attribute:

```tsx
<a href="/external" target="_self">Full reload</a>
```

## Base Path

For apps served from a subdirectory:

```tsx
<Router base="/my-app">
  <Route path="/" component={Home} />
  <Route path="/about" component={About} />
</Router>
```

All routes are matched relative to `/my-app`. The `<A>` component automatically includes the base path in rendered hrefs.

## Single Flight

By default, concurrent requests to the same endpoint are deduplicated (`singleFlight: true`). Disable for independent requests:

```tsx
<Router singleFlight={false}>
  <Route path="/" component={Home} />
</Router>
```

## Transform URL

Custom URL transformation before matching:

```tsx
<Router transformUrl={(url) => url.replace(/^\/en\//, "")}>
  <Route path="/" component={Home} />
</Router>
```

Useful for i18n prefixes, locale stripping, or URL normalization.

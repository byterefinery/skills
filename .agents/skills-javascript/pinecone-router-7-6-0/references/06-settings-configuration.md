# Settings Configuration

## API

Settings are configured via the `PineconeRouter.settings()` function. It acts as both getter and setter:

```js
// Set settings
PineconeRouter.settings({ hash: true, basePath: '/app' })

// Read settings
const current = PineconeRouter.settings()
console.log(current.hash) // true

// In Alpine components
<div x-init="$router.settings({ targetID: 'app' })"></div>
```

## Settings Object

| Setting | Type | Default | Description |
|---|---|---|---|
| `hash` | `boolean` | `false` | Enable hash-based routing (`#/path` instead of `/path`) |
| `basePath` | `string` | `''` | Base path prefix for all routes and navigation |
| `targetID` | `string \| undefined` | `undefined` | Default element ID for rendering templates |
| `handleClicks` | `boolean` | `true` | Auto-intercept anchor link clicks |
| `globalHandlers` | `Handler[]` | `[]` | Handlers that run on every route |
| `preload` | `boolean` | `false` | Preload all external templates after first load |
| `fetchOptions` | `RequestInit` | `{}` | Options passed to `fetch()` for template requests |
| `pushState` | `boolean` | `true` | Call `history.pushState()` on navigation |

## hash

Enable hash routing for environments that don't support pushState or need hash-based URLs:

```js
PineconeRouter.settings({ hash: true })
```

With hash routing:
- Routes use `#/path` format in the URL
- `basePath` is only applied to template URLs, not to hash fragments
- The router reads from `location.hash` instead of `location.pathname`

## basePath

Automatically prefix all routes, navigation calls, and template URLs:

```js
PineconeRouter.settings({ basePath: '/blog' })
```

With `basePath: '/blog'`:
- `x-route="/about"` matches `/blog/about`
- `$router.navigate('/about')` navigates to `/blog/about`
- `x-template="/views/home.html"` fetches `/blog/views/home.html`
- `PineconeRouter.add('/about')` registers `/blog/about`

This eliminates the need to manually prefix every path.

## targetID

Set a default target element for all templates:

```js
PineconeRouter.settings({ targetID: 'app' })
```

All templates without an explicit `.target` modifier will render inside `<div id="app"></div>`. Individual routes can override with `.target.otherId`.

## handleClicks

Disable automatic link interception:

```js
PineconeRouter.settings({ handleClicks: false })
```

When disabled, only links with the `x-link` attribute are intercepted:

```html
<a href="/path">Reloads the page</a>
<a href="/path" x-link>Handled by router</a>
```

## globalHandlers

Register handlers that execute on every route change:

```js
PineconeRouter.settings({
  globalHandlers: [
    (context, controller) => {
      // Runs before every route-specific handler
      if (!isAuthenticated() && context.path !== '/login') {
        window.PineconeRouter.navigate('/login')
      }
    },
  ],
})
```

## preload

Fetch all external templates at low priority after the first page renders:

```js
PineconeRouter.settings({ preload: true })
```

This improves perceived performance on subsequent navigations. Individual routes can still use `.preload` even when global preload is off.

## fetchOptions

Pass custom options to `fetch()` when loading external templates:

```js
PineconeRouter.settings({
  fetchOptions: {
    headers: {
      'Authorization': 'Bearer ' + token,
    },
    credentials: 'include',
  },
})
```

The `priority` option is always set by the router (`high` for on-demand, `low` for preload) and cannot be overridden here.

## pushState

Disable browser history API calls:

```js
PineconeRouter.settings({ pushState: false })
```

The URL stays static but Pinecone Router's internal navigation history still tracks paths. Useful for embedded apps or custom history management.

## Configuration Timing

Settings should be configured before `Alpine.start()`:

```js
document.addEventListener('alpine:init', () => {
  PineconeRouter.settings({
    hash: false,
    basePath: '/app',
    targetID: 'app',
    preload: true,
  })
})
```

Settings can be changed at any time, but some changes (like `basePath`) only affect routes added after the change.

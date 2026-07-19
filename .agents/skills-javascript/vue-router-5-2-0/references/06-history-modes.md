# History Modes

## HTML5 History (`createWebHistory`)

Uses the HTML5 History API (`pushState` / `replaceState`). Produces clean URLs without `#`.

```js
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [/* ... */],
})
```

URLs: `https://example.com/users/42`

### Base path

Pass a base for apps hosted at a sub-path:

```js
// App served at https://example.com/my-app/
const router = createRouter({
  history: createWebHistory('/my-app/'),
  routes: [/* ... */],
})
// Routes resolve as: /my-app/, /my-app/users, etc.
```

The base is automatically read from `<base>` tag if present:

```html
<head>
  <base href="/my-app/">
</head>
```

### Server requirement

The server must return the `index.html` for all client-side routes. Configure a fallback:

**Nginx**:
```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

**Apache** (`.htaccess`):
```apache
FallbackResource /index.html
```

**Node.js (Express)**:
```js
app.use('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'))
})
```

**Vite dev server**: handled automatically.

## Hash History (`createWebHashHistory`)

Uses URL hash fragment. No server configuration needed.

```js
import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [/* ... */],
})
```

URLs: `https://example.com/#/users/42`

### Base path

```js
// At https://example.com/folder/
createWebHashHistory()           // https://example.com/folder#/
createWebHashHistory('/folder/') // https://example.com/folder/#/
```

### `file://` protocol

Hash history works with local files. The base parameter is ignored when there is no host:

```js
// file:///usr/etc/folder/index.html
createWebHashHistory('/ignored') // base is ignored, hash is always used
```

### When to use

- Cannot configure the server to handle HTML5 history
- Deploying to static hosting without rewrite rules
- Running from `file://` protocol

## Memory History (`createMemoryHistory`)

In-memory history with no URL changes. Used for SSR and testing.

```js
import { createRouter, createMemoryHistory } from 'vue-router'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [/* ... */],
})
```

### SSR usage

Create the router on the server, then navigate to the target URL:

```js
// Server
const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

// Navigate to the requested URL
await router.push(req.url)
await router.isReady()

// Render with the router
const html = await renderToString(createApp(App, { router }))
```

### Testing

```js
import { createRouter, createMemoryHistory } from 'vue-router'

const router = createRouter({
  history: createMemoryHistory('/initial-location'),
  routes,
})

// Navigate in tests without affecting the real URL
await router.push('/test-route')
expect(router.currentRoute.value.path).toBe('/test-route')
```

## History API

The history object exposed by each factory:

| Property/Method | Description |
|---|---|
| `base` | Base path string |
| `location` | Current history location string |
| `state` | Current `history.state` object |
| `push(location, state?)` | Push a new history entry |
| `replace(location, state?)` | Replace current history entry |
| `go(delta)` | Navigate by delta entries |
| `listen(callback)` | Listen for history changes (returns teardown) |
| `createHref(location)` | Generate an `href` string for a location |
| `destroy()` | Clean up event listeners |

## Safari pushState limit

Safari throws a `SecurityError` when `pushState` is called more than 100 times in 30 seconds. Vue Router handles this gracefully by falling back to direct URL assignment (`location.assign`), which resets the counter.

## Choosing a history mode

| Factor | HTML5 | Hash | Memory |
|---|---|---|---|
| Clean URLs | Yes | No (`#/`) | N/A |
| Server config | Required | None | N/A |
| Bookmarks | Clean | Hash in URL | N/A |
| `file://` support | No | Yes | Yes |
| SSR | Yes (with base) | Yes | Yes |
| Default recommendation | **Default** | Fallback | SSR/testing |

Use HTML5 history as the default. Switch to hash history only when server configuration is not possible.

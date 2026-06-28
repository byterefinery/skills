# Events & Link Handling

## Events

All events are dispatched on `document`.

| Event | Detail | When |
|---|---|---|
| `pinecone:start` | — | Loading starts (before handlers) |
| `pinecone:end` | — | Loading ends (after templates render) |
| `pinecone:fetch-error` | `{ error: string, url: string }` | External template fetch fails |
| `pinecone:handler-error` | `{ error, handler, ctx }` | Uncaught error in a handler |

### Alpine.js usage

```html
<div @pinecone:start.document="showLoader()"
     @pinecone:end.document="hideLoader()"></div>
```

### JavaScript usage

```js
document.addEventListener('pinecone:start', () => NProgress.start())
document.addEventListener('pinecone:end', () => NProgress.done())
document.addEventListener('pinecone:fetch-error', (event) => {
  console.error('Fetch error at', event.detail.url, ':', event.detail.error)
})
document.addEventListener('pinecone:handler-error', (event) => {
  console.error('Handler error:', event.detail.error)
})
```

### Loading state

Check `$router.loading` reactively:

```html
<div x-show="$router.loading" class="spinner">Loading...</div>
```

## Link Handling

### Automatic interception

By default, Pinecone Router intercepts clicks on all anchor elements with valid `href` attributes. It:

1. Ignores clicks with modifier keys (Ctrl, Meta, Alt, Shift)
2. Ignores non-primary button clicks
3. Ignores links with URL schemes (`http:`, `mailto:`, `tel:`, etc.)
4. Ignores links with `target="_blank"` or other non-self targets
5. Calls `preventDefault()` and `Router.navigate(href)` for internal links

### Bypassing interception

Add `native` or `data-native` attribute to skip router handling:

```html
<a href="/foo" native>Handled by browser (page reload)</a>
<a href="/foo" data-native>Also handled by browser</a>
```

### Disabling globally

```js
PineconeRouter.settings({ handleClicks: false })
```

When disabled, only links with the `x-link` attribute are intercepted:

```html
<a href="/path">Reloads the page</a>
<a href="/path" x-link>Handled by router (SPA navigation)</a>
```

## nProgress Integration

```js
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

document.addEventListener('pinecone:start', () => NProgress.start())
document.addEventListener('pinecone:end', () => NProgress.done())
```

## Custom Loading Indicator

```html
<div x-data="{ loading: false }"
     @pinecone:start.window="loading = true"
     @pinecone:end.window="loading = false">
  <div x-show="loading" x-transition class="overlay">Loading...</div>
</div>
```

Or use the reactive `$router.loading`:

```html
<div x-show="$router.loading" x-transition.opacity class="overlay">
  Loading...
</div>
```

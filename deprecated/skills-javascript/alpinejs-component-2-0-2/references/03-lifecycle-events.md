# Lifecycle Events Reference

## Overview

The host element dispatches custom events at key points in the component lifecycle. All events bubble and are composed (cross shadow boundary).

## Events

### `x-component:loading`

Dispatched when a URL fetch begins. Not dispatched for on-page templates.

**Payload:** `{ source }` — the resolved URL string.

```html
<div
  x-component.url="'/components/card.html'"
  x-on:x-component:loading="showSpinner = true"
></div>
```

### `x-component:loaded`

Dispatched when rendering completes successfully — after the shadow root is populated, styles are applied, and `Alpine.initTree()` has run.

**Payload:** `{ source }` — the resolved template id or URL.

```html
<div
  x-component="'card'"
  x-on:x-component:loaded="console.log('rendered', $event.detail.source)"
></div>
```

### `x-component:error`

Dispatched when any failure occurs:

- Expression evaluation throws
- URL fetch fails (network error, non-OK status)
- Cross-origin URL blocked
- Invalid URL protocol
- Template source resolved but no fragment returned

**Payload:** `{ source, error }` — the source value and the `Error` object.

For expression evaluation failures, `source` is the raw directive expression string.
For render/load failures, `source` is the resolved template id or URL.

```html
<div
  x-component.url="'/components/card.html'"
  x-on:x-component:error="console.error('failed', $event.detail.error)"
></div>
```

## Event properties

All events are created as:

```js
new CustomEvent(eventName, {
  bubbles: true,
  composed: true,
  detail: eventDetail,
})
```

- `bubbles: true` — events propagate up the DOM tree
- `composed: true` — events cross shadow DOM boundaries

## Lifecycle flow

### On-page template (`x-component`)

```
Expression evaluated
  → Template looked up (cached or from DOM)
  → Shadow root created/updated
  → Styles applied (if x-component-styles)
  → Alpine.initTree() called
  → x-component:loaded dispatched
```

No `x-component:loading` event for on-page templates.

### Remote template (`x-component.url`)

```
Expression evaluated
  → x-component:loading dispatched
  → Fetch (cached or network)
  → Shadow root created/updated
  → Styles applied (if x-component-styles)
  → Alpine.initTree() called
  → x-component:loaded dispatched
```

### Error path

```
Expression evaluated
  → [Evaluation throws]
  → x-component:error dispatched
  → Content cleared
```

or:

```
x-component:loading dispatched
  → [Fetch fails / template missing]
  → x-component:error dispatched
  → Content cleared (if previously mounted)
```

## Usage patterns

### Loading indicator

```html
<div x-data="{ loading: false, error: null }">
  <div
    x-component.url="'/components/dashboard.html'"
    x-on:x-component:loading="loading = true"
    x-on:x-component:loaded="loading = false"
    x-on:x-component:error="error = $event.detail.error.message; loading = false"
  ></div>

  <template x-if="loading">
    <div class="spinner">Loading...</div>
  </template>

  <template x-if="error">
    <div class="error" x-text="error"></div>
  </template>
</div>
```

### Retry on error

```html
<div x-data="{ url: '/card.html', retries: 0 }">
  <div
    x-component.url="url"
    x-on:x-component:error="retries++"
  ></div>

  <template x-if="retries > 0">
    <button x-on:click="retries = 0; url = url">Retry</button>
  </template>
</div>
```

Forcing a re-evaluation clears the failed cache entry and allows a fresh fetch.

## Gotchas

- **No loading event for on-page templates** — `x-component:loading` only fires for `.url` mode. On-page template lookups are synchronous.
- **Missing on-page templates do not emit error events** — if a template id doesn't exist, a console warning is logged but no `x-component:error` is dispatched. Only URL failures and expression errors emit the error event.
- **Expression errors clear content** — if the directive expression throws, any previously rendered content is destroyed and the shadow root is cleared.
- **Events fire per render cycle** — reactive changes that trigger re-renders will dispatch new lifecycle events.

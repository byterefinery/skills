# Lifecycle Events

The host element dispatches three bubbling, composed `CustomEvent`s:

- `x-component:loading` — when a URL load starts (URL mode only; never emitted for on-page templates)
- `x-component:loaded` — when rendering completes
- `x-component:error` — when loading or rendering fails

Event payloads (`event.detail`):

- `x-component:loading`: `{ source }`
- `x-component:loaded`: `{ source }`
- `x-component:error`: `{ source, error }`

`source` is the resolved template id or URL; `error` is the thrown `Error`.

## Attach listeners to an ancestor

`x-component:loading` is dispatched while the host's own directives are still being processed, so an `x-on` binding **on the host element itself can miss it**. The events bubble and are composed (they escape even if the host sits inside someone else's shadow root), so an ancestor always sees all three:

```html
<div
  x-on:x-component:loaded="console.log('component ready', $event.detail)"
  x-on:x-component:error="console.error('component failed', $event.detail)"
>
  <div x-component.url="'/public/person-card.html'"></div>
</div>
```

## What triggers `x-component:error`

- Missing on-page template id (a console warning is logged first)
- Failed URL fetch — non-2xx response, network error, invalid URL, non-`http(s)` protocol, or a blocked cross-origin URL
- A source that resolved but returned no fragment

Each error is also logged to the console.

## What does not trigger it

If the directive **expression itself** throws, Alpine reports the error through its own error handler, the source is treated as empty, and any mounted content is cleared — no `x-component:error` is emitted.

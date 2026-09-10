# `react-dom` (18.3.1)

The web renderer. Entry points and what to use where:

| Entry | Exports | Status |
|---|---|---|
| `react-dom/client` | `createRoot`, `hydrateRoot`, `flushSync` | **Use these** |
| `react-dom` | `render`, `hydrate`, `unmountComponentAtNode`, `findDOMNode`, `flushSync`, `unstable_batchedUpdates`, `createPortal`, `unstable_*` | Legacy — deprecated, runs app in React 17 mode |
| `react-dom/server` | string and streaming renderers | See 03-server-rendering |
| `react-dom/test-utils` | `Simulate`, legacy helpers, deprecated `act` | See 05-testing |

The main `react-dom` export also re-exports `createRoot`/`hydrateRoot` but warns "importing createRoot from react-dom is not supported" — always import from `react-dom/client`.

## Contents

- [Client roots](#client-roots)
- [Legacy API](#legacy-api)
- [Portal](#portal)
- [Batching and flushSync](#batching-and-flushsync)
- [Events](#events)
- [Refs](#refs)
- [DOM property handling](#dom-property-handling)

## Client roots

```js
import { createRoot, hydrateRoot } from 'react-dom/client';

const root = createRoot(container, options);
root.render(<App />);   // mount or update
root.unmount();         // tear down and remove DOM content

const root = hydrateRoot(container, <App />, options);
root.unmount();
root.unstable_scheduleHydration(node); // nudge hydration of a specific subtree
```

`createRoot` options (from the 18.3.1 source):

| Option | Purpose |
|---|---|
| `identifierPrefix` | Prefix for generated `useId` IDs — set it in both client and server to keep IDs stable across hydration |
| `onRecoverableError(error, errorInfo)` | Called when React recovers from a rendering or hydration error and retries (default: `reportError`/`console.error`) |
| `unstable_strictMode` | Strict Mode at the root without wrapping in `<StrictMode>` |
| `transitionCallbacks` | Internal hook used by React DevTools — do not use |

Passing a second argument to `root.render(...)` or a JSX element to `createRoot` are common mistakes React explicitly warns about (the errors suggest the correct call shape).

`hydrateRoot` takes the same container-options object and re-renders the same tree; mismatches fall back to client rendering at the nearest `<Suspense>` boundary (see 03).

## Legacy API

| Export | Behavior in 18 |
|---|---|
| `render(element, container, callback?)` | Dev error: "ReactDOM.render is no longer supported in React 18. Use createRoot instead." Runs in **legacy mode** — no concurrent features, no automatic batching |
| `hydrate(element, container, callback?, options?)` | Same deprecation; legacy hydration only |
| `unmountComponentAtNode(container)` | Deprecated — use `root.unmount()` |
| `renderSubtreeIntoContainer` | Unstable, warns on call |
| `findDOMNode(component)` | Deprecated; warns for function components and returns the first DOM child — avoid |
| `createPortal(children, container, key?)` | Still the portal API — but it lives in `react-dom`'s exports, not `react-dom/client` |

Mixing a modern root and legacy `render` on the same container is unsupported and produces dev errors.

## Portal

```js
import { createPortal } from 'react-dom';
createPortal(<Dialog />, document.body);
```

- The portal's children render into `container` (a DOM node) but stay part of the React tree where `createPortal` was called — context, refs, and events flow from the **parent** location, not the DOM location.
- `container` must be an existing DOM node when the portal renders; it is not created for you.
- A third `key` argument exists in the signature (usually passed `null`).

## Batching and flushSync

- 18 batches updates from event handlers, timeouts, promises, and native callbacks into a single render.
- `flushSync(() => setState(...))` forces the update to complete before the next line — use only when subsequent code reads the DOM (scroll position, measurements). It bypasses concurrent scheduling, so it is costly; calling it while React is already rendering emits a dev warning.

`unstable_batchedUpdates(callback)` is exported for library authors that need explicit batching inside native event handlers on non-React events; it is unstable.

## Events

React 18 attaches a small number of **delegated listeners per event type on the root container** (not `document`), and synthesizes a `SyntheticEvent` for each React prop handler (`onClick`, `onMouseEnter`, …). Consequences:

- Event handlers must be idempotent-ish and fast; they run during delegation from the root.
- **Passive listeners**: `touchstart`, `touchmove`, and `wheel` are registered `passive: true` at the root — `preventDefault()` inside those React handlers does nothing. To block scrolling, add your own `addEventListener('wheel', fn, { passive: false })` to the target element.
- Capture-phase handlers exist for every event: `onXxxCapture`.
- Synthetic events are not pooled in 18 (the 17 pooling warning is gone) — you can pass them around safely, but they are still not native events (no `nativeEvent`-level DOM API without `event.nativeEvent`).
- Supported additions in 18: `onResize` on `<video>`; `aria-description` recognized; `imageSizes`/`imageSrcSet` on `<img>`; non-string `<option>` children allowed when a `value` prop is provided.
- `onChange` works on text inputs/selects/checkboxes (React implements it with internal value tracking); `onInput` is available for raw input events. Composition events: `onCompositionStart/Update/End`.

## Refs

- `ref={callback}` or `ref={useRef(null)}` on DOM components gives the host node; on function components the ref is `null` unless the component uses `forwardRef` (and `useImperativeHandle` to shape what is exposed).
- Class components receive the instance; `findDOMNode`-style traversal is deprecated.
- Refs are set before `componentDidMount` and cleaned up to `null` on unmount; callback refs receive `null` on unmount.
- A component that forwards its own ref must re-export it via `forwardRef` — refs are just props in disguise.

## DOM property handling

- `style` is an object; CSS custom properties go in `cssText`-style keys (`{'--my-var': 'x'}`) or use `style={{ ['--my-var']: 'x' }}`. `dangerouslySetInnerHTML` replaces children (pass `{__html}`).
- Unknown props on built-in elements: React 18 passes through **unknown lowercase attributes** to the DOM (e.g., `data-*`, `aria-*`, custom-element attributes) instead of dropping them, and warns in dev for unknown **uppercase** props (likely typos) and for props with dashes in the wrong case.
- Custom elements (`<my-element attr="...">`) get all non-`on`/`style` props set as attributes, and `onXxx` handlers are attached via `addEventListener`.
- Dev-only validation: DOM nesting rules (e.g., `<div>` inside `<p>`), invalid `aria-*` values, `target="_blank"` without `rel="noopener"`, `http://` URLs in `src`/`href` (warns, does not block).
- SVG elements use their native property names; React handles camelCase → kebab-case for standard attributes.
- `suppressHydrationWarning` (per element) silences a one-node hydration mismatch warning in dev and prod (prod support landed in 18.1).

---
name: react-18-3-1
description: React 18.3.1 — JavaScript library for building user interfaces from components with hooks for state and effects, concurrent features (transitions, useDeferredValue, Suspense data fetching), automatic batching, and createRoot/hydrateRoot client rendering. Verified against the react/react monorepo at tag v18.3.1. Covers the react and react-dom packages (client, server streaming, test-utils), the Rules of Hooks, testing with act, and auxiliary packages (react-is, react-refresh, use-sync-external-store, scheduler, eslint-plugin-react-hooks). Use when writing, reviewing, debugging, or testing React 18 code, or doing SSR, hydration, or streaming with React 18.
license: MIT
compatibility: Runtime needs Promise, Symbol, and Object.assign (IE11 not supported). Node.js for renderToPipeableStream; modern edge runtimes for renderToReadableStream. Content verified against the react/react repository at tag v18.3.1.
metadata:
  tags:
    - javascript
    - frontend
    - framework
    - react
    - hooks
    - ssr
---

# react 18.3.1

React 18.3.1 (April 2024) is the final stable release of the React 18 line, verified against the `react/react` monorepo at tag `v18.3.1`. The canonical documentation for this API surface is reactjs.org (React 18 docs); for exact signatures consult the source or [references](#references) below. 18.3 is a patch-level release of 18.2 — its only public API change is exporting `act` from `react` itself (previously only from `react-dom/test-utils` and `react-test-renderer`), plus bug fixes (notably `useId` in streamed SSR and `useSyncExternalStore` with selectors).

## Overview

React builds UIs from components. The `react` package defines components and holds no DOM knowledge; `react-dom` is the web renderer. React 18's defining features:

- **Concurrent rendering** — rendering is interruptible and prioritized. New APIs separate *urgent* updates (typing) from *transitions* (background state changes) and *deferred* values.
- **Automatic batching** — state updates batched in event handlers, timeouts, promises, and native callbacks; one render per batch.
- **New client APIs** — `createRoot`/`hydrateRoot` from `react-dom/client`; the legacy `ReactDOM.render`/`hydrate` are deprecated and run the app in React 17 mode.
- **Streaming SSR** — `renderToPipeableStream` (Node) and `renderToReadableStream` (edge) stream `<Suspense>` fallbacks and swap in resolved content.
- **Hydration** — `hydrateRoot` with selective hydration and strict mismatch errors.
- **18.3** — `act` exported from `react`; `ReactDOMTestUtils.act` now warns as deprecated.

Package map (all verified in the monorepo):

| Package | Entry points | Purpose |
|---|---|---|
| `react` | `react`, `react/jsx-runtime`, `react/jsx-dev-runtime` | Components, hooks, elements, `Suspense`/`memo`/`lazy`/`forwardRef`/`createContext` |
| `react-dom` | `react-dom` (legacy) | `render`, `hydrate`, `findDOMNode` — deprecated, legacy mode |
| `react-dom` | `react-dom/client` | `createRoot`, `hydrateRoot`, `flushSync` |
| `react-dom` | `react-dom/server` (`.node` / `.browser` conditions) | `renderToString`, `renderToStaticMarkup`, `renderToPipeableStream`, `renderToReadableStream` |
| `react-dom` | `react-dom/test-utils` | `Simulate`, legacy `TestUtils` helpers, deprecated `act` |
| `react-is` | — | `typeOf`, `isValidElementType`, element-type predicates |
| `react-refresh` | `runtime`, `babel` | Fast Refresh runtime and Babel plugin (bundler integration) |
| `use-sync-external-store` | ``, `shim`, `shim/with-selector` | Backwards-compatible `useSyncExternalStore` shim |
| `scheduler` | ``, `unstable_post_task`, `unstable_mock` | Cooperative scheduler used by React internally |
| `eslint-plugin-react-hooks` | — | `rules-of-hooks` and `exhaustive-deps` lint rules |
| `react-server-dom-webpack` (experimental) | ``, `/plugin`, `/writer`, `/node-register` | RSC webpack integration, 0.1.0 |

The monorepo also contains `react-native-renderer` (the renderer behind React Native), `react-test-renderer`, `react-devtools*`, and internal packages (`react-reconciler`, `react-server`, `react-client`) that are not meant for direct use.

## Usage

Browser app — create a root, render, let React manage updates:

```jsx
import { useState } from 'react';
import { createRoot } from 'react-dom/client';

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <>
      <h1>{count}</h1>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </>
  );
}

const root = createRoot(document.getElementById('root'));
root.render(
  <StrictMode>
    <Counter />
  </StrictMode>,
);
```

SSR with streaming Suspense support:

```js
import { renderToPipeableStream } from 'react-dom/server';

function handleRequest(req, res) {
  const { pipe } = renderToPipeableStream(<App page={page} />, {
    bootstrapScripts: ['/main.js'],
    nonce: cspNonce,
    onShellReady() {
      res.setHeader('content-type', 'text/html');
      pipe(res); // shell sent — start hydrating on the client
    },
    onAllReady() {
      // every Suspense boundary resolved; safe to log TTFB metrics
    },
    onError(err) {
      return 'FATAL'; // digest, embedded in the stream for RSC
    },
  });
}
```

Marking an update as a non-urgent transition:

```jsx
const [isPending, startTransition] = useTransition();

function onFilter(value) {
  setQuery(value); // urgent — input reflects immediately
  startTransition(() => setResults(search(value))); // interruptible
}
```

See [04-concurrent-features](references/04-concurrent-features.md) for the full concurrent model and [03-server-rendering](references/03-server-rendering.md) for the complete SSR API.

## Gotchas

- **Use `createRoot` from `react-dom/client`, not `ReactDOM.render`.** In 18, `render`/`hydrate` from `react-dom` log a dev error and run the app in legacy (React 17) mode where concurrent features are off. All 18 features require the new root APIs.
- **Import `act` from `react` in 18.3.** `ReactDOMTestUtils.act` still works but warns "deprecated in favor of `React.act`". For pre-18.3 code, import from `react-test-renderer` or `react-dom/test-utils`.
- **Set `globalThis.IS_REACT_ACT_ENVIRONMENT = true`** in unit test setup. Without it, React 18 suppresses the "not wrapped in act" warnings entirely (opt-in design).
- **Strict Mode in 18 dev double-mounts components** (mount → unmount → remount, state preserved) to prepare for future state preservation. Effects that lack cleanup will run twice visibly; make effect setup idempotent.
- **Automatic batching is the default.** `setState` inside `setTimeout`, `Promise.then`, or native event handlers batches with others. Use `flushSync` only when code must read the DOM immediately after an update; never inside a transition callback.
- **Hydration text mismatches are errors in 18.** React stops trying to patch individual nodes; it re-renders the client tree from the closest `<Suspense>` boundary. `suppressHydrationWarning` (works in prod since 18.1) silences one element.
- **`renderToString` renders the `<Suspense>` fallback** and retries that content on the client. Use the streaming APIs (`renderToPipeableStream` / `renderToReadableStream`) for real Suspense support.
- **Profiler `onRender` takes 6 arguments in 18**: `(id, phase, actualDuration, baseDuration, startTime, commitDuration)`. There is no `onCommit` prop in stable 18 — it exists only behind feature flags in the source. Code written for 19's signature will misread the arguments.
- **`useMutableSource` is exported but unsupported** in stable 18 builds; it is only wired behind feature flags. Use `useSyncExternalStore` instead.
- **`useSyncExternalStore` needs `getServerSnapshot`** when the component can render on the server; without it SSR and hydration will tear.
- **Passive event listeners**: `touchstart`, `touchmove`, and `wheel` are registered passively at the root — `event.preventDefault()` in those handlers is a no-op. Attach your own non-passive listener to block scrolling.
- **`useId` must be called on both server and client** for stable matching IDs; generate IDs per-render or with `Math.random` and you will get hydration mismatches.
- **Don't mix root APIs on one container** — calling `ReactDOM.render` on a container already given to `createRoot` (or vice versa) is unsupported and warns.
- **18.3 RSC is experimental** — `react-server-dom-webpack` 0.1.0 and the `unstable_*` cache/context exports are not stable APIs; see [07-experimental-rsc](references/07-experimental-rsc.md) before touching them.

## References

- [01-core-api](references/01-core-api.md) — `react` package: elements, components, every stable hook, special elements, unstable exports
- [02-react-dom](references/02-react-dom.md) — client roots, legacy API, events, refs, DOM property handling
- [03-server-rendering](references/03-server-rendering.md) — `react-dom/server`: string and streaming renderers, options, hydration
- [04-concurrent-features](references/04-concurrent-features.md) — priorities, transitions, `useDeferredValue`, batching, Strict Mode, Suspense
- [05-testing](references/05-testing.md) — `act`, `IS_REACT_ACT_ENVIRONMENT`, `react-test-renderer`, `Simulate`, legacy helpers
- [06-ecosystem-packages](references/06-ecosystem-packages.md) — `react-is`, `react-refresh`, `use-sync-external-store`, `scheduler`, `eslint-plugin-react-hooks`
- [07-experimental-rsc](references/07-experimental-rsc.md) — React Server Components as of 18.3.1: Flight protocol packages, server context, cache APIs

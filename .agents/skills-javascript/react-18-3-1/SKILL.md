---
name: react-18-3-1
description: React 18.3.1 — JavaScript library for building declarative, component-based user interfaces. Covers function and class components, JSX, props, state, the complete hook API (useState, useReducer, useEffect, useLayoutEffect, useInsertionEffect, useRef, useMemo, useCallback, useContext, useId, useTransition, useDeferredValue, useSyncExternalStore, useImperativeHandle), refs, context, memo, concurrent rendering, Suspense and lazy, startTransition, automatic batching, createRoot and hydrateRoot, portals, flushSync, testing with React.act, streaming server rendering, and experimental React Server Components with the Flight protocol. Use when writing, debugging, or testing React 18 code, creating components or hooks, configuring SSR and hydration, or reasoning about React 18 concurrent features.
license: MIT
compatibility: Evergreen browsers at runtime; Node.js or an edge runtime for server rendering; JSX requires a build toolchain (Babel, Vite, Webpack, or TypeScript)
metadata:
  tags:
    - javascript
    - frontend
    - ui
    - library
    - react
    - components
    - hooks
    - concurrent
    - ssr
    - server-components
---

# react 18.3.1

## Overview

React 18.3.1 is a JavaScript library for building user interfaces. It is declarative — design simple views for each state of the application, and React efficiently updates and renders just the right components when data changes — and component-based — encapsulated components manage their own state and compose into complex UIs. React 18's headline feature is concurrent rendering: React can work on multiple things at once, interrupt and resume work, and interleave urgent with non-urgent updates.

Version highlights in the 18.3.x line (both 18.3.0 and 18.3.1 shipped April 2024; 18.3.1 is the last 18 release):

- **`React.act`** — the testing utility `act` is exported from the `react` package itself (18.3.1); `ReactDOMTestUtils.act` now warns in development.
- **Deprecation warnings** — `findDOMNode`, `unmountComponentAtNode`, `ReactDOMTestUtils`, and `ReactDOMServer.renderToStaticNodeStream` log deprecation warnings in development.
- **Better element warnings** — `createElement`/JSX now detect components that were not exported (default/named import mixups) and JSX literals accidentally passed as a component type.

What is **not** in 18.3.1 (all React 19): `use()`, `useActionState`, `useOptimistic`, refs as props, stable `cache()`, stable `batchedUpdates`, `useFormStatus`, `<Activity>`, `<ViewTransition>`, `useEffectEvent`. Also note `useSyncExternalStoreWithSelector` lives in the `use-sync-external-store/with-selector` package, not in `react`.

Packages — `react` (component definitions and hooks, no renderer), `react-dom` (browser and server renderers, portals, flushSync), `react-server` (experimental Server Component runtime), `react-server-dom-webpack` (experimental RSC Flight wire protocol), `scheduler` (ForkJoin scheduling), `react-is`, `react-refresh`, `use-sync-external-store`, `use-subscription`, `eslint-plugin-react-hooks`, `react-test-renderer`, plus tooling — `react-devtools`, `react-reconciler` (custom renderers), `react-native-renderer`.

## Usage

### Quick start

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
  </StrictMode>
);
```

### Entry points

- `react` — hooks, `createElement`, `createContext`, `forwardRef`, `memo`, `lazy`, `Fragment`, `StrictMode`, `Profiler`, `Suspense`, `SuspenseList`, `startTransition`, `act`, `version`
- `react-dom/client` — `createRoot(container, options)`, `hydrateRoot(container, children, options)`
- `react-dom` — `createPortal`, `flushSync`, `findDOMNode` (deprecated), `unstable_batchedUpdates`, legacy `render`/`hydrate`/`unmountComponentAtNode`
- `react-dom/server` — `renderToString`, `renderToStaticMarkup`, `renderToPipeableStream` (Node), `renderToReadableStream` (Node and edge runtimes), legacy `renderToNodeStream`
- `react-dom/test-utils` — deprecated in 18.3; import `act` from `react` instead
- `react/jsx-runtime` — automatic JSX transform (`jsx`, `jsxs`, `Fragment`)
- `react-server-dom-webpack` — experimental Flight client (`createFromFetch`, `createFromReadableStream`, `createFromXHR`) and writer (see 06)

### Project setup

- Vite (`npm create vite@latest -- --template react`) for client-only apps; Next.js (13.x/14.x) or Remix (2.x) when you want SSR/RSC on React 18
- Keep `react` and `react-dom` on the same minor (18.3.x)
- Use the automatic JSX runtime (`react/jsx-runtime`) — importing `React` just for JSX is only required by the legacy classic runtime
- Enable `eslint-plugin-react-hooks` (`react-hooks/rules-of-hooks`, `react-hooks/exhaustive-deps`)

### Where to look

- Component model, JSX, class components, composition → [01-components-and-jsx](references/01-components-and-jsx.md)
- Every hook with signatures and rules → [02-hooks](references/02-hooks.md)
- createRoot, hydrateRoot, portals, events, legacy APIs, testing → [03-react-dom-client](references/03-react-dom-client.md)
- Concurrent rendering, Suspense, transitions → [04-concurrent-and-suspense](references/04-concurrent-and-suspense.md)
- Server rendering and hydration → [05-server-rendering](references/05-server-rendering.md)
- Experimental Server Components and Flight → [06-server-components](references/06-server-components.md)
- Performance, memoization, Profiler, production build → [07-performance](references/07-performance.md)
- Context and refs in depth, unstable APIs, companion packages → [08-advanced-apis-and-packages](references/08-advanced-apis-and-packages.md)
- 18.3.0/18.3.1 changes, 17→18 migration, what's missing from 18 → [09-18-3-changes-and-migration](references/09-18-3-changes-and-migration.md)

## Gotchas

- **Use `createRoot`, not `ReactDOM.render`** — the legacy API still works but warns and runs your app in legacy (React 17) mode; concurrent features, client Suspense, and streaming hydration do not work with it.
- **`useId` IDs are colon-based** — e.g. `:r0:` on the client, `:R0:` when server-rendered and hydrated. Never parse or regenerate them; escape them if you use them in CSS selectors or HTML `id`/`for` pairs.
- **StrictMode double-invokes in development only** — components render twice, effects mount/cleanup/mount, ref callbacks run twice on mount. Side effects in render or missing effect cleanups surface here; the cost disappears in production.
- **Hydration mismatches are errors, not warnings** — React no longer patches up individual nodes; it reverts to client rendering up to the closest `<Suspense>` boundary. `suppressHydrationWarning` is the only opt-out (works in production since 18.1).
- **Automatic batching is the default** — multiple `setState` calls in the same event, timeout, promise, or XHR are batched into one render. If you need a synchronous flush (measuring the DOM right after an update), wrap in `flushSync`.
- **Event pooling is gone** — synthetic events are not recycled (since React 17); you can read event properties later or in async handlers without calling `persist()`.
- **Effects run after paint; layout effects run before** — use `useLayoutEffect` for DOM measurements, `useEffect` for subscriptions and async work; `useLayoutEffect` warns on the server.
- **`renderToString` does not stream** — for Suspense support on the server use `renderToPipeableStream` (Node) or `renderToReadableStream` (Node/edge); `renderToString` emits fallback HTML for any suspended boundary and retries client-side.
- **Server Components are experimental in 18** — the `react-server` export condition, `react-server-dom-webpack` Flight API, `createServerContext`, and `unstable_Cache` are all unstable. There is no stable RSC story on React 18; for production RSC use React 19 with a framework (Next.js App Router, Remix/React Router v7).
- **No built-in client data fetching** — React 18.3.1 ships no first-party client fetch library; combine `Suspense` + `lazy` with a third-party cache (React Query, SWR) or pass data from the server.
- **`act` comes from `react`** — `import { act } from 'react'` (18.3.1+); `react-dom/test-utils` is deprecated and its `act` warns. Test runners that do not set `globalThis.IS_REACT_ACT_ENVIRONMENT = true` will get "not wrapped in act" warnings.
- **`key` is not a prop** — it is consumed by the reconciler for list matching; never read `props.key` or pass it to another element manually.

## References

- [01-components-and-jsx](references/01-components-and-jsx.md) — Function and class components, JSX and the automatic runtime, props, children, lists and keys, composition, createElement/cloneElement, Children
- [02-hooks](references/02-hooks.md) — Complete hook API with signatures, calling rules, and per-hook notes
- [03-react-dom-client](references/03-react-dom-client.md) — createRoot/hydrateRoot and options, root API, flushSync, portals, event system, legacy APIs, testing with act
- [04-concurrent-and-suspense](references/04-concurrent-and-suspense.md) — Concurrent rendering model, automatic batching, transitions, Suspense, lazy, SuspenseList, offscreen
- [05-server-rendering](references/05-server-rendering.md) — renderToString, streaming renderers, pipeable/readable streams, hydration, suppressHydrationWarning
- [06-server-components](references/06-server-components.md) — Experimental RSC, "use client"/"use server", Flight protocol, react-server, cache internals, serialization rules
- [07-performance](references/07-performance.md) — Re-render triggers, memoization, keys, StrictMode cost, Profiler API, production build, DevTools
- [08-advanced-apis-and-packages](references/08-advanced-apis-and-packages.md) — Context and refs in depth, unstable API catalog, scheduler, react-is, react-refresh, use-subscription, use-sync-external-store, eslint plugin
- [09-18-3-changes-and-migration](references/09-18-3-changes-and-migration.md) — 18.3.0/18.3.1 changes, 17→18 migration, deprecations, what is not in 18

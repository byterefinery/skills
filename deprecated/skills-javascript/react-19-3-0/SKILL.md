---
name: react-19-3-0
description: React 19.3.0 — JavaScript library for building declarative, component-based user interfaces. Covers function components and JSX, props, state, events, the complete hook API (useState, useEffect, useActionState, useOptimistic, use, useEffectEvent), refs as props, context, memo, Suspense and concurrent rendering, Actions and forms, Server Components and Server Actions, ViewTransition and addTransitionType, performance, the React Compiler, and migrating from React 18. Use when writing or debugging React 19 code, creating components or hooks, migrating from React 18, configuring the React Compiler, or working with React Server Components.
license: MIT
compatibility: Evergreen browsers at runtime; Node.js for server rendering; React Compiler requires Babel 7 in the build pipeline.
metadata:
  tags:
    - javascript
    - frontend
    - ui
    - framework
    - components
    - hooks
    - server-components
    - compiler
---

# react 19.3.0

## Overview

React 19.3.0 is a JavaScript library for building user interfaces. It is declarative — design simple views for each state of the application, and React efficiently updates and renders just the right components when data changes — and component-based — encapsulated components manage their own state and compose into complex UIs. React renders to the browser (`react-dom`), to the server (React Server Components), and to other platforms.

Version highlights in 19.3.0:

- **`<ViewTransition>`** — built-in component that animates UI updates through the browser View Transitions API, driven by `startTransition`; **`addTransitionType()`** tags transitions so per-type CSS classes and callbacks can react to them.
- **`<Activity>`** (19.2) — hide and restore a subtree while keeping its state; **`useEffectEvent()`** (19.2) — extract non-reactive event logic for use in effects; **`cacheSignal()`** (19.2, RSC) — know when the `cache()` lifetime is over.
- React 19 core — Actions with `useActionState`/`useOptimistic`, `use()` for reading Promises and context in render, refs as props, `<form action>` and `useFormStatus`, document metadata hoisting, `<Context>` renderable as a provider, `useId` IDs now use underscores.

Packages — `react` (component definitions and hooks, no renderer), `react-dom` (browser and server renderers, portals, preloading), `react-server` (Server Component runtime), `react-server-dom-webpack|turbopack|parcel|esm|unbundled` (RSC wire protocols), `scheduler` (ForkJoin scheduling), `react-is`, plus tooling — `react-devtools`, `react-refresh`, `react-test-renderer` (deprecated, prefer Testing Library).

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

- `react-dom/client` — `createRoot(container)`, `hydrateRoot(container, html)`
- `react-dom/server` — `renderToPipeableStream`, `renderToReadableStream`, `prerender`, `prerenderToNodeStream`, and the 19.2 `resume*` APIs for partial pre-rendering
- `react-dom` — `createPortal`, `flushSync`, `preload`, `preconnect`, `prefetchDNS`, `preinit`, `preinitModule`, `useFormStatus`, `requestFormReset`
- `react` — hooks, `memo`, `lazy`, `Suspense`, `Activity`, `ViewTransition`, `startTransition`, `addTransitionType`, `cache`, `createContext`, `createElement`

### Project setup

Use a framework (Next.js, React Router v7, TanStack Start) when you want Server Components — they provide the RSC bundler integration. For client-only apps, Vite (`npm create vite@latest -- --template react`) is the standard choice. Keep `react` and `react-dom` on the same minor version (19.3.x).

### Where to look

- Component model, JSX, refs-as-props, composition → [01-components-and-jsx](references/01-components-and-jsx.md)
- Every hook with signatures and rules → [02-hooks](references/02-hooks.md)
- State design, events, forms and Actions → [03-state-and-events](references/03-state-and-events.md)
- Re-render triggers, reconciliation, keys, purity, StrictMode → [04-rendering-and-reconciliation](references/04-rendering-and-reconciliation.md)
- Suspense, `use()`, data fetching, transitions, `<Activity>` → [05-suspense-and-async](references/05-suspense-and-async.md)
- Server Components, Server Actions, RSC renderers → [06-server-components](references/06-server-components.md)
- `startTransition`, `addTransitionType`, `<ViewTransition>` (19.3.0) → [07-view-transitions](references/07-view-transitions.md)
- Profiling, memoization, prefetching, production build → [08-performance](references/08-performance.md)
- Enabling and reasoning about the React Compiler → [09-react-compiler](references/09-react-compiler.md)
- React 18 → 19.3 breaking changes and deprecations → [10-react-19-migration](references/10-react-19-migration.md)

## Gotchas

- **Ref is a prop in 19** — function components receive `ref` inside `props`; `forwardRef` is unnecessary (still supported). Reading `element.ref` is deprecated — use `element.props.ref`.
- **`use()` is not a hook** — it can be called conditionally in render, but it suspends the component when the Promise is pending; use a `Suspense` boundary around it.
- **Actions, not event handlers** — async functions passed to `startTransition` or a form's `action` prop run inside a Transition; use `useActionState` for pending state and error handling, and `useOptimistic` for instant feedback.
- **`<ViewTransition>` only animates inside `startTransition`** — mount/unmount updates outside a transition render without animation, and the browser needs the View Transitions API.
- **`useId` IDs changed in 19.2** — they are now underscore-based (e.g. `_r_1x`) instead of colon-based; never parse them, and escape them if used in CSS selectors.
- **Server components cannot use client features** — no event handlers, `useState`, `useEffect`, or refs without a `"use client"` boundary; props crossing the boundary must be serializable.
- **StrictMode double-invokes in development** — renders twice, effects mount/cleanup/mount, and ref callbacks run twice on mount; any side effect in render will surface here.
- **React Compiler needs the Rules of React** — mutating props/state during render or conditional hook calls break compiler optimizations and are reported by `eslint-plugin-react-compiler`.
- **No built-in client data fetching** — React ships no first-party client fetch library; use `use()` with server data or a third-party cache (React Query, SWR).

## References

- [01-components-and-jsx](references/01-components-and-jsx.md) — Function components, JSX rules, props, lists and keys, composition, refs as props, context
- [02-hooks](references/02-hooks.md) — Complete 19.3.0 hook API with signatures and calling rules
- [03-state-and-events](references/03-state-and-events.md) — State design patterns, synthetic events, forms, and Actions
- [04-rendering-and-reconciliation](references/04-rendering-and-reconciliation.md) — Re-render triggers, reconciliation, keys, memo, purity rules, StrictMode, error boundaries
- [05-suspense-and-async](references/05-suspense-and-async.md) — Suspense, lazy, use(), data fetching, useTransition, useDeferredValue, Activity, SuspenseList
- [06-server-components](references/06-server-components.md) — RSC directives, Server Actions, renderers, cache and cacheSignal, taint APIs
- [07-view-transitions](references/07-view-transitions.md) — startTransition, addTransitionType, and the ViewTransition component (new in 19.3.0)
- [08-performance](references/08-performance.md) — Profiling, avoiding re-renders, concurrent tools, resource preloading, production build
- [09-react-compiler](references/09-react-compiler.md) — Compiler goals, pipeline, enabling via Babel/ESLint, Rules of React, opt-out
- [10-react-19-migration](references/10-react-19-migration.md) — 18 → 19 breaking changes, deprecations, and the 19.1–19.3 feature timeline

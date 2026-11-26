# React 19.3.0 — Migration and Version Timeline

Contents

- [Preparing](#preparing)
- [Breaking changes (18 → 19)](#breaking-changes-18--19)
- [Deprecations](#deprecations)
- [New in 19.0](#new-in-190)
- [Notable 19.0 changes](#notable-190-changes)
- [TypeScript changes](#typescript-changes)
- [Codemods](#codemods)
- [19.1.x](#191x)
- [19.2.0](#1920)
- [19.3.0](#1930)

## Preparing

Upgrade to **React 18.3.1 first** — it is 18.2 plus warnings for everything React 19 deprecates, so you can find the problems before the breaking upgrade.

## Breaking changes (18 → 19)

- **New JSX transform required** — the automatic runtime is mandatory; the classic `import React` runtime was removed (and brings ref-as-prop support in JSX).
- **`propTypes` removed** — silently ignored; migrate to TypeScript or another type-checking solution.
- **`defaultProps` removed for function components** — use ES6 default parameters. (Class components keep `defaultProps`.)
- **`contextTypes` and `getChildContext` removed** — legacy context is gone; use `createContext` + `contextType`.
- **String refs removed** — migrate to ref callbacks.
- **Module pattern factory removed** — migrate to regular functions.
- **`React.createFactory` removed** — use JSX.
- **`react-test-renderer/shallow` removed** — use the third-party `react-shallow-renderer` or Testing Library.
- **`react-dom/test-utils` removed** — `act` moved to `react`; other utilities are gone.
- **`ReactDOM.render` / `ReactDOM.hydrate` removed** — use `createRoot` / `hydrateRoot` (the concurrent APIs).
- **`unmountComponentAtNode` removed** — use `root.unmount()`.
- **`ReactDOM.findDOMNode` removed** — use DOM refs.
- **Render errors no longer re-thrown** — uncaught errors in render are reported to `window.reportError` (caught ones to `console.error`); customize via `onUncaughtError` / `onCaughtError` options on `createRoot`/`hydrateRoot`.

## Deprecations

- **`element.ref`** — deprecated in favor of `element.props.ref` (accessing warns).
- **`react-test-renderer`** — logs a deprecation warning and switched to concurrent rendering; migrate to `@testing-library/react` (or `-react-native`).
- **`useFormState`** — deprecated alias of `useActionState` (keep importing from `react-dom` if you must).
- **`forwardRef`** — still exported and working, but unnecessary: refs are props on function components.

## New in 19.0

- **Actions** — `startTransition` accepts async functions; a transition waits for them, giving pending/error states and side effects (like `fetch`) inside transitions.
- **`useActionState(reducer, initialState, permalink?)`** — orders Actions inside a transition with access to action state and pending state; the third argument enables progressive-enhancement forms.
- **`useOptimistic(state, reducer)`** — optimistically update state while a transition is in flight.
- **`use(promiseOrContext)`** — read a Promise or Context in render; suspends while pending; callable conditionally.
- **Ref as a prop** — function components receive `ref` in `props`; no `forwardRef`.
- **Suspense sibling pre-warming** — when a component suspends, the nearest fallback commits immediately; suspended siblings pre-warm in the background.
- **Form Actions** — `<form action>` and `<button>/<input> formAction` with automatic reset for uncontrolled components; `useFormStatus`; `requestFormReset`.
- **Document metadata** — `<title>`, `<meta>`, `<link>` rendered in components are hoisted into `<head>` with deduplication.
- **Stylesheets in Suspense** — React inserts stylesheets into `<head>` before revealing the boundary that needs them.
- **Async scripts** — renderable anywhere, ordered and deduplicated by React.
- **Preloading** — `preinit`, `preload`, `prefetchDNS`, `preconnect` APIs.
- **`prerender` / `prerenderToNodeStream`** — static generation APIs that wait for data (streaming-friendly).
- **RSC stable** — directives, server components, and server functions are stable; the framework-facing `react-server` export condition is the supported path.

## Notable 19.0 changes

- **`<Context>` as a provider** — render `<Context value=...>` directly; `<Context.Provider>` still works.
- **Ref callbacks can return cleanup** — called on unmount.
- **`useDeferredValue(value, initialValue?)`** — first argument is the initial render's value.
- **Custom Elements** — React passes all Custom Elements Everywhere tests.
- **StrictMode** — `useMemo`/`useCallback` reuse the first render's result during the second render; ref callbacks double-invoke on initial mount.
- **UMD builds removed** — use an ESM CDN (e.g., esm.sh) for script-tag usage.
- **Hydration** — mismatch errors log a single diff; third-party DOM insertions trigger a client re-render to fix up.

## TypeScript changes

- Removed deprecated types: `ReactChild`, `ReactFragment`, `ReactNodeArray`, `ReactText`, `VoidFunctionComponent`, `VFC`; `Requireable`, `ValidationMap`, `Validator`, `WeakValidationMap` moved to `prop-types`; classic class types moved to `create-react-class`.
- **Refs may return cleanup** — implicit returns of non-functions now error.
- **`useRef` requires an initial argument.**
- **Ref objects are always mutable.**
- Strict `ReactElement` typing — props default to `unknown`, not `any`.
- **Global `JSX` namespace removed** — `import { JSX } from 'react'`.
- Better `useReducer` typings — no explicit `React.Reducer<...>` needed.

## Codemods

```sh
# JS/TS runtime changes (render → createRoot, etc.)
npx react-codemod@latest upgrade-to-react-19 .

# TypeScript-only changes
npx types-react-codemod@latest preset-19 ./path-to-react-ts-files
```

## 19.1.x

Patch line focused on **React Server Components hardening** — extra loop protection for Server Functions, cycle protection and `toString` patches on Server Functions, DoS mitigations, and a `react-server-dom-unbundled` package (moved from `react-server-dom-webpack/*.unbundled`).

## 19.2.0

- **`<Activity>`** — hide/restore a subtree with its state.
- **`useEffectEvent`** — stable, always-latest event functions for effects.
- **`cacheSignal`** (RSC) — abort signal for the `cache()` lifetime.
- **Resume APIs for partial pre-rendering** — `resume`, `resumeAndPrerender`, `resumeToPipeableStream`, `resumeAndPrerenderToNodeStream`; `prerender` now returns a resumable `postponed` state.
- **Node Web Streams** added to the SSR APIs.
- **`useId` now emits underscore-based IDs** (was colons) — escape them for CSS.
- React DOM batches Suspense boundary reveals in server rendering (notable with animated reveals).
- `nonce` on hoistable styles; ARIA 1.3 attributes no longer warn.
- **React Performance tracks** in browser dev tools (DevTools).

## 19.3.0

- **`<ViewTransition>`** — built-in component animating mount/unmount/update via the browser View Transitions API, driven by `startTransition`; per-phase class props and event callbacks (see [07-view-transitions](07-view-transitions.md)).
- **`addTransitionType(type)`** — tag the active transition inside `startTransition` for per-type styling and callbacks.
- Further **RSC/Server Actions hardening** carried across the 19.x line (cycle protections, DoS mitigations).

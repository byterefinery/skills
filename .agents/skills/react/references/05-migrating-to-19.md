# Migrating to React 19 (verified at tag v19.3.0)

From the 19.0.0 CHANGELOG entry. Upgrade path recommendation from React itself: go to `18.3.1` first (identical to 18.2 but adds deprecation warnings), fix what it flags, then move to 19.

## Removed in 19

**React core**

- `propTypes` — silently ignored; use TypeScript or another type-checking solution
- `defaultProps` on function components — use ES6 default parameters (class components keep `defaultProps`)
- `contextTypes` and `getChildContext` — legacy class context is gone; use `contextType` / `createContext`
- String refs — migrate to ref callbacks or object refs
- Module pattern factories and `React.createFactory` — migrate to regular functions and JSX
- `react-test-renderer/shallow` — use the standalone `react-shallow-renderer` or Testing Library
- `element.ref` access — deprecated in favor of `element.props.ref` (warnings in 19)

**react-dom**

- `react-dom/test-utils` — `act` moved to `react` (development builds only); other utilities removed
- `ReactDOM.render` / `ReactDOM.hydrate` — use `createRoot` / `hydrateRoot`
- `unmountComponentAtNode` — use `root.unmount()`
- `ReactDOM.findDOMNode` — use DOM refs
- UMD builds — load via an ESM CDN (e.g., esm.sh) instead

**Requirements**

- The new (automatic) JSX transform is required — the old classic transform is unsupported.

## Behavior changes to know

- **Uncaught render errors** — no longer re-thrown to the browser's `error` event by default; they go to `window.reportError`. Customize via `onCaughtError`/`onUncaughtError` options on `createRoot`/`hydrateRoot`.
- **`<Context>` as provider** — render `<Context value={...}>` directly instead of `<Context.Provider>`.
- **Ref cleanup** — a function returned from a ref callback runs as cleanup on unmount/re-attach.
- **`useDeferredValue` initial value** — pass an optional initial value to defer from the first render.
- **Custom Elements** — React 19 passes all Custom Elements Everywhere tests; use standard custom-element APIs freely.
- **StrictMode** — `useMemo`/`useCallback` now reuse the first render's memoized result during the double render, and ref callbacks are double-invoked on mount.
- **Hydration mismatches** — logged as a single error with a content diff; React force-renders client-side to fix up DOM modified by third-party scripts/extensions.
- **`useId` format** — changed from `:r123:` to `«r123»` in 19.1, then to underscores in 19.2; treat as opaque.
- **RSC is stable** — directives, server components, and server functions may target React 19 as a peer dependency via the `react-server` export condition. The low-level RSC framework APIs (bundler-level) do not follow semver and may break between 19.x minors.

## TypeScript

Run the official codemod for type changes (`ReactChild`, `ReactFragment`, `ReactNodeArray`, `ReactText`, `VoidFunctionComponent`/`VFC` removed; `Requireable`/`ValidationMap`/`Validator`/`WeakValidationMap` moved to `prop-types`):

```sh
npx types-react-codemod@latest preset-19 ./path-to-your-react-ts-files
```

## New features you can adopt on top of 19

- `use()`, `useActionState`, `useOptimistic`, `useFormStatus`, form `action`/`formAction`
- Document metadata and stylesheet hoisting, `preinit`/`preload`/`preconnect`/`prefetchDNS`
- `prerender` and the 19.2 `resume*` APIs
- 19.1: `captureOwnerStack` (dev-only Owner Stacks), `react-server-dom-parcel`
- 19.2: `<Activity>`, `useEffectEvent`, `cacheSignal`, batched suspense-boundary reveal
- 19.3 tree: `<ViewTransition>`, `addTransitionType`, `react-markup`

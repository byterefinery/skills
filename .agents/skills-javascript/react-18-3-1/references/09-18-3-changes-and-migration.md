# 18.3 changes and migration

What the 18.3.x line (18.3.0 and 18.3.1, both April 2024) changed, the 17→18 migration checklist, and what 18.3.1 deliberately does not include.

## What changed in 18.3.0

- **`React.unstable_act`** — the `act` testing utility moved into the `react` package (as `unstable_act`); `react-test-renderer` and `react-dom/test-utils` keep exporting it for compatibility.
- **`findDOMNode` deprecation warning** — development `console.error`: "findDOMNode is deprecated and will be removed in the next major release. Instead, add a ref directly to the element you want to reference."
- **`unmountComponentAtNode` deprecation warning** — development `console.error` pointing to the `createRoot` API.
- **`ReactDOMTestUtils` deprecation warnings** — the whole `react-dom/test-utils` module now warns in development ("deprecated ... Upgrade to a modern testing library, such as @testing-library/react"), and its `act` warns separately: "`ReactDOMTestUtils.act` is deprecated in favor of `React.act`. Import `act` from `react` instead."
- **`renderToStaticNodeStream` deprecation warning** — points to `renderToPipeableStream` + waiting for `onAllReady` before `pipe`.
- **Sharper `createElement`/JSX warnings** — element creation now detects:
  - `undefined` or `{}` passed as a type, with the hint "You likely forgot to export your component from the file it's defined in, or you might have mixed up default and named imports."
  - a JSX literal accidentally passed as a component type ("Did you accidentally export a JSX literal instead of a component?").
  - improved `key`-spread and invalid-type diagnostics in `ReactElementValidator`.

## What changed in 18.3.1

- **`act` is exported under its stable name** — `import { act } from 'react'` works; `unstable_act` remains as an alias. This is the functional delta of 18.3.1 (plus the version bump). 18.3.1 is the final 18.x release.

## React 17 → 18 migration checklist

The 18.0 release (March 2022) is the substantive breaking step; 18.1–18.3 are additive/bug-fix.

### Adopt the new roots (required for all 18 features)

```diff
- import ReactDOM from 'react-dom';
- ReactDOM.render(<App />, document.getElementById('root'));
+ import { createRoot } from 'react-dom/client';
+ const root = createRoot(document.getElementById('root'));
+ root.render(<App />);
```

- `ReactDOM.render` / `ReactDOM.hydrate` still work but warn and run the app in **legacy mode** — no concurrent rendering, no client Suspense, no streaming hydration.
- `unmountComponentAtNode(container)` → keep the `root` reference and call `root.unmount()`.
- Server: `renderToString` keeps working but is discouraged — move dynamic pages to `renderToPipeableStream` (Node) or `renderToReadableStream` (edge), and pair with `hydrateRoot` (see 05).
- `renderToNodeStream`/`renderToStaticNodeStream` are deprecated — use the streaming APIs.

### Fix StrictMode fallout (development-only)

React 18's StrictMode unmounts and **remounts** every component on initial mount (restoring state) to surface missing cleanups. Expected breakage and fixes:

- Effects without cleanup → add the cleanup (the double mount/cleanup/mount exposes every leak).
- Side effects in render (mutation, logging, random values) → move to effects or make pure.
- Third-party components that assume single mount → upgrade them or drop `<StrictMode>` for the affected subtree.

### Automatic batching

Updates from the same event, `setTimeout`, promise, or XHR now batch into one render (previously only React-synthesized events batched):

- Code that relied on an intermediate render (measure DOM between two `setState` calls) → wrap the first update in `flushSync` or restructure.
- Render counts drop; code that counts renders in tests may need updating.

### Stricter hydration

- Mismatched text/nodes are now **errors**: React reverts to client rendering up to the closest `<Suspense>` boundary instead of patching individual nodes.
- Audit server/client divergence (timestamps, user-specific content, `Math.random()`/`Date.now()` in render) and add `suppressHydrationWarning` only where the difference is intentional.
- `suppressHydrationWarning` works in production since 18.1.

### Other 18.0 behavior changes to know

- **`useEffect` timing** — effects triggered by discrete events (click/keydown) always flush synchronously now; previously inconsistent. Code that depended on the old timing needs `useLayoutEffect` or restructuring.
- **Components may render `undefined`** — no longer an error (keep a linter rule to catch missing returns).
- **No "setState on unmounted component" warning** — removed; use effect cleanups for subscription hygiene.
- **StrictMode no longer suppresses console logs** — the second render's logs show (DevTools greys them out).
- **`renderToString`/`renderToStaticMarkup` no longer throw on Suspense** — they emit the boundary's fallback HTML and the client retries.
- **New JS environment requirements** — `Promise`, `Symbol`, and `Object.assign` must exist; polyfill for legacy browsers.
- **`useId`** — for unique, hydration-safe IDs (a11y pairings in component libraries); the format is `:r…` (client) / `:R…` (server), colon-based.
- **Event system (from 17, for completeness)** — listeners attach to the root container, and event pooling is removed (no `persist()` needed).

### Testing

- `import { act } from 'react'` (18.3.1) instead of `ReactDOMTestUtils.act` / `react-test-renderer`'s copy.
- Migrate `react-dom/test-utils` (Simulate, renderIntoDocument, selectors) to `@testing-library/react` + user-event.
- If your runner does not set `globalThis.IS_REACT_ACT_ENVIRONMENT = true`, you will see act-environment warnings; Testing Library sets it.

## What 18.3.1 does NOT include

These arrived in **React 19** — do not assume them on 18, and do not write 18 code that requires them:

| 19 feature | 18-era alternative |
|---|---|
| `use()` (read promises/context in render) | Await in effects, or render behind `Suspense`; Flight client materializes promises in the decoded tree |
| `useActionState` / `useOptimistic` | Hand-rolled pending/error state in effects or event handlers |
| Refs as props on function components | `forwardRef` + `useImperativeHandle` |
| Stable `cache()` (RSC) | `unstable_getCacheForType` / `unstable_Cache` (experimental, see 06) |
| Stable `batchedUpdates` | `unstable_batchedUpdates` (batching is already the default in 18 anyway) |
| `useFormStatus`, `requestFormReset` | `useRef` + form events |
| Document metadata hoisting (`<title>`/`<meta>` from RSC) | Set `document.title` in an effect or via a framework |
| `<Context>` rendered as a provider | `<Context.Provider value={...}>` |
| `useEffectEvent`, `<Activity>`, `<ViewTransition>`, `addTransitionType` | Regular effects / conditional render / CSS transitions |
| `useSyncExternalStoreWithSelector` in `react` | `use-sync-external-store/with-selector` package |
| `taint*` APIs (RSC security) | No 18 equivalent |

## Upgrading to React 19

- 19 is largely a drop-in upgrade for most apps: `ReactDOM.render` and `ReactDOMTestUtils` are **removed** (if your app still uses them, finish the 18 migration first), and `ref` starts flowing to function components (usually a non-event; it breaks code that spreads props into `forwardRef`ed third-party components — audit `...props` spreads that include `ref`).
- Bump `react`, `react-dom`, and `@types/react` together to 19.x; update `react-test-renderer` expectations (deprecated in 19 — Testing Library preferred).
- Frameworks: Next.js 14+/15+ and React Router v7 (Remix) target React 19; on 18, use Next.js 13.x/14.x-era configs.
- If you are on 18.3.1 and not blocking on 19 features, staying on 18 is stable and supported — 18.3.1 is the final 18 release.

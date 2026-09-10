# Performance

Contents

- [Measure first](#measure-first)
- [Avoid unnecessary re-renders](#avoid-unnecessary-re-renders)
- [Use concurrent tools](#use-concurrent-tools)
- [Code splitting and prefetching](#code-splitting-and-prefetching)
- [Resource preloading APIs](#resource-preloading-apis)
- [Document metadata and stylesheets](#document-metadata-and-stylesheets)
- [Lists](#lists)
- [Production build](#production-build)
- [When to stop optimizing](#when-to-stop-optimizing)

## Measure first

- **React DevTools Profiler** — records re-renders with a flame chart of render durations; commit vs render phases are separated.
- **React Performance tracks** (19.2+) — appear on the browser Performance panel timeline, correlating React's scheduling with browser work.
- **`<Profiler onRender={fn} id="...">`** — programmatic: `fn(id, phase, actualDuration, baseDuration, startTime, commitTime)`; `phase` is `mount` or `update`.

Profile in a realistic scenario (real data volume, mid-tier hardware). Optimize the top offenders, not everything.

## Avoid unnecessary re-renders

1. **Memoize components** — `memo(Component)` skips re-renders when props are shallow-equal. Only helps when a component actually re-renders with unchanged props and its render is measurable.
2. **Keep props stable** — don't create inline objects, arrays, or functions in JSX for memoized children:

```jsx
// bad — new array and function every render defeats memo
<Filters options={all.filter(available)} onChange={v => setOption(v)} />

// good
const options = useMemo(() => all.filter(available), [all]);
const onChange = useCallback(v => setOption(v), []);
```

3. **Split context** — if one context holds both a rarely-changing value and a frequently-changing one, consumers of the rare value re-render on every frequent change. Split into two providers/contexts.
4. **Move state down** — keep frequently-changing state in the leaf that uses it so the subtree above doesn't re-render.
5. **Let the compiler do it** — with React Compiler (see [09-react-compiler](09-react-compiler.md)) manual `memo`/`useMemo`/`useCallback` become mostly unnecessary and can be removed.

## Use concurrent tools

- **`startTransition`** — wrap non-urgent updates (search, filters, navigation) so urgent input stays responsive.
- **`useDeferredValue`** — for expensive *derived* UI (filtering 10k rows, expanding a tree), so typing isn't blocked.
- **`useOptimistic`** — instant UI for long round-trips.
- **`lazy` + `Suspense`** — code-split routes and heavy components; see below.
- **`flushSync`** — the opt-out: force a synchronous render when imperative DOM integration requires it (rare).

Batching is automatic in 18+ — multiple `setState` calls in one event/timeout/Promise resolve commit once.

## Code splitting and prefetching

```jsx
const Settings = lazy(() => import('./Settings.js'));

// prefetch on hover/focus, render on click
<a href="/settings"
   onMouseEnter={() => import('./Settings.js')}
   onClick={() => navigate('/settings')}>
  Settings
</a>
```

Split at route boundaries and for optional features. Suspense fallbacks keep the rest of the page usable while chunks load.

## Resource preloading APIs

`react-dom` exports hoisting, deduplicating preload APIs — render them anywhere in the tree, React places them in `<head>`:

- **`preload(href, { as, ... })`** — `<link rel="preload">` for fonts, images, scripts.
- **`preconnect(href)`** — `<link rel="preconnect">` to establish connections early (CDNs, APIs).
- **`prefetchDNS(href)`** — `<link rel="dns-prefetch">`.
- **`preinit(href, { as, priority? })`** — loads and initializes a script/style with priority.
- **`preinitModule(href)`** — preinitializes a module script.

Use them to move discovery out of CSS (font preloads) and to prefetch resources for anticipated navigations.

## Document metadata and stylesheets

Since 19, React natively hoists document metadata rendered in components into `<head>` — `<title>`, `<meta>`, `<link>`, and `<script>` tags (deduplicated by attributes) can live anywhere:

```jsx
function Settings() {
  return (
    <>
      <title>Settings</title>
      <meta name="description" content="App settings" />
      <SettingsForm />
    </>
  );
}
```

`<link rel="stylesheet">` inside a Suspense boundary is revealed together with its content — React waits for the stylesheet before showing the boundary, preventing unstyled flashes.

## Lists

- Stable keys (IDs, not indices) — React reuses the right components and DOM.
- Keep list item components `memo`-friendly (stable props) and split the item so typing in one input doesn't re-render every row.
- Avoid re-creating the item array in render when the source data hasn't changed (`useMemo`).
- For very long lists, virtualize (third-party) — React does not virtualize natively.

## Production build

Development builds include extra warnings, checks, and slower paths. Build with `NODE_ENV=production` (Vite/Webpack do this by default in build mode) — never serve the dev bundle. UMD builds were removed in 19; for script-tag usage use an ESM CDN (e.g., esm.sh) with an import map.

## When to stop optimizing

- A render under ~16 ms is fine — the frame budget matters more than the render count.
- Premature memoization adds comparison cost, code size, and maintenance burden; the React Compiler exists precisely to make manual optimization obsolete for idiomatic code.
- Profile → fix the biggest offender → re-profile.

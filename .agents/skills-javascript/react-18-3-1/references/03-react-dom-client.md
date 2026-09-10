# react-dom client

Everything for mounting and interacting with the DOM: `createRoot`/`hydrateRoot`, root options, `flushSync`, portals, the event system, the legacy APIs, and testing.

## createRoot

```ts
// from 'react-dom/client'
createRoot(container: Element | Document | DocumentFragment, options?: CreateRootOptions): Root
```

- The only correct way to mount an app in React 18. Using `ReactDOM.render` instead warns and keeps your app in legacy (React 17) mode where concurrent features do not work.
- Calling `createRoot` on a container that already has a root throws; unmount first.
- `container` must be a valid DOM element — `createRoot(...): Target container is not a DOM element.` otherwise.

`Root` interface:

```ts
root.render(children: ReactNodeList): void   // may be called repeatedly to replace the tree
root.unmount(): void                          // removes the tree and releases resources
```

Options (`CreateRootOptions`):

```ts
{
  identifierPrefix?: string;       // prefix for useId (":prefix:r1:"); set the same value on
                                   // createRoot and on the server renderer for consistency
  onRecoverableError?: (error: unknown) => void;  // called when React recovers from an error
                                   // during render/hydration (default: reportError/console.error)
  unstable_strictMode?: boolean;   // wrap in <StrictMode> (usually you just render <StrictMode>)
  unstable_concurrentUpdatesByDefault?: boolean;  // start all updates as transitions (experimental)
}
```

`identifierPrefix` matters for component libraries that ship `useId`: a global prefix keeps client IDs distinct across multiple roots on one page.

## hydrateRoot

```ts
// from 'react-dom/client'
hydrateRoot(container: Element | Document, children: ReactNodeList, options?: HydrateRootOptions): Root
```

- Hydrates server-rendered HTML: React attaches listeners and adopts the server DOM instead of recreating it.
- Must be called before the server HTML goes stale in a way that breaks consistency; hydration mismatches revert the affected `<Suspense>` boundary to client rendering (see 05).
- `children` is required — `Must provide initial children as second argument to hydrateRoot.`
- Extra options beyond `CreateRootOptions`:

```ts
onHydrated?: (suspenseNode: Comment) => void;   // a Suspense boundary finished hydrating
onDeleted?: (suspenseNode: Comment) => void;    // a boundary's server content was deleted
hydratedSources?: Array<MutableSource<any, any>>; // legacy, pairs with createMutableSource
```

## Synchronous updates

```ts
// from 'react-dom'
flushSync(fn?: () => void): void
unstable_batchedUpdates(fn: () => void): void
```

- `flushSync` synchronously flushes any pending updates (and runs `fn` then flushes its updates) before yielding. Use it right before DOM measurements that must see the update, or when handing control to a library that mutates the DOM immediately. It blocks concurrent behavior and is a performance cost — the rare exception, not the default.
- `unstable_batchedUpdates` forces the React 18 batching behavior (in 18 batching is already the default everywhere; the escape hatch mainly exists for legacy mode and third-party code).

## Portals

```ts
// from 'react-dom'
createPortal(children: ReactNodeList, container: Element | DocumentFragment, key?: string | number): Portal
```

- Renders `children` into a different DOM node while keeping them in the React tree at the call site — state, context, events, and refs all behave as if the portal were inline.
- Classic use: modals, tooltips, and dropdowns that must escape `overflow: hidden` or stacking contexts, or content that must live at `document.body` for z-index purposes.
- The portal's DOM location is separate from its React location: a portal inside a `<Suspense>` boundary still participates in that boundary, and context providers above the portal apply to its children.

## Event system

- React attaches listeners for all synthetic events **to the root container** (since 17 — not `document`), so events from code that bypasses React inside that container are not seen by React.
- **No event pooling** (since 17): event objects are normal objects; reading properties in a `setTimeout` or async handler works, and `event.persist()` is gone (calling it warns).
- **Async handlers are fine** — `onClick={async () => {...}}` works; the event is not recycled, so there is nothing to persist.
- Events use camelCase props (`onClick`, `onMouseDown`, `onChange` on inputs) and bubble/capture like DOM events; add a `Capture` suffix for capture-phase props (`onFocusCapture`).
- `onChange` on `input`/`textarea`/`select` is React's normalized change event, not the DOM `change` — for `input` it fires like `input` (on every keystroke).
- Scroll listeners (`onScroll`) are registered **passive** — `e.preventDefault()` inside them is a no-op; prevent scrolling via CSS or other APIs.
- Keyboard, pointer, touch, drag-and-drop, and composition events follow DOM semantics with React's normalized names (`onDragEnter`, `onTouchStart`, `onCompositionEnd`, …).

## Legacy APIs (deprecated — do not use for new code)

From `react-dom` (all still functional in 18.3.1, all warn in development):

| API | Status |
|---|---|
| `render(element, container, callback?)` | Deprecated — runs the app in legacy mode (no concurrent features). Use `createRoot(container).render(element)`. |
| `hydrate(element, container, callback?)` | Deprecated. Use `hydrateRoot(container, element)`. |
| `unmountComponentAtNode(container)` | Deprecated since 18.3 (explicit console.error). Use `root.unmount()`. |
| `renderSubtreeIntoContainer` (`unstable_renderSubtreeIntoContainer`) | Deprecated; no direct replacement — lift state or use context. |
| `findDOMNode(componentOrElement)` | Deprecated since 18.3 (explicit console.error). Use refs. |

In 18, `render` and `hydrate` still work so existing apps keep functioning, but they keep your tree in legacy mode: no concurrent rendering, no client Suspense, no streaming hydration. Treat them as a migration stopgap (see 09).

`unstable_flushControlled` flushes controlled input updates synchronously (used by form libraries), and `unstable_createEventHandle` exposes a handle to the underlying native event system — both are internal-facing and should not be used from app code.

## Testing

- **`act`** — since 18.3.1, `import { act } from 'react'`. Wraps state-changing interactions so React flushes work and assertions see consistent state:

```jsx
import { act } from 'react';

await act(async () => {
  userEvent.click(screen.getByRole('button', { name: 'Submit' }));
});
expect(result).toBeInTheDocument();
```

  - Wrap async work: `await act(async () => { ... })` flushes pending effects, transitions, and microtasks.
  - Test runners must mark the environment — `globalThis.IS_REACT_ACT_ENVIRONMENT = true` — or React warns about act usage outside tests. `@testing-library/react` (and `react-test-renderer` in Jest setups) handle this for you; if you write a custom runner, set the flag.
  - `ReactDOMTestUtils.act` (from `react-dom/test-utils`) still exists in 18.3 but warns: "`ReactDOMTestUtils.act` is deprecated in favor of `React.act`."
- **`react-dom/test-utils` is deprecated** in 18.3 (the whole module warns: use a modern testing library such as `@testing-library/react`). `renderIntoDocument`, `Simulate`, and the `mockComponent`/selector helpers should all be replaced by Testing Library's queries and user-event.
- **`react-dom/unstable_testing`** exposes the internal selector engine (`findAllNodes`, `createRoleSelector`, `createTestNameSelector`, `createTextSelector`, `findBoundingRects`, …) — useful for building custom test utilities, not for ordinary component tests.
- **`react-test-renderer`** — the official non-DOM renderer, still supported in 18.3.1 (deprecated only later, in React 19):

```jsx
import TestRenderer, { act } from 'react-test-renderer';

let renderer;
act(() => {
  renderer = TestRenderer.create(<App />);
});
expect(renderer.toJSON()).toMatchSnapshot();

const instance = renderer.root.findByType(Button);   // TestInstance API
instance.props.onClick();                              // wrap in act when it updates state
renderer.unmount();
```

  `TestInstance` gives `type`, `props`, `children`, `findByType`, `findAllByType`, `findAll`, `findByProps`, and `toJSON()` (serializable tree). Use it for snapshot and structural tests; prefer Testing Library for behavior tests.
- In development React auto-injects DevTools hooks and, if the browser lacks DevTools, prints a download link — harmless console noise in tests, usually silenced by the test environment.

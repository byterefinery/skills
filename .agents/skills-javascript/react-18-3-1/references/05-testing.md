# Testing React 18 (18.3.1)

## Contents

- [act](#act)
- [Enabling act warnings](#enabling-act-warnings)
- [react-test-renderer](#react-test-renderer)
- [react-dom/test-utils](#react-domtest-utils)
- [Patterns](#patterns)

## act

`act` tells React a unit of work is happening: it flushes scheduled updates, effects, and (for async act) microtasks, so assertions observe a settled tree.

**Import from `react` on 18.3.** In 18.3.1, `ReactDOMTestUtils.act` is a thin wrapper that logs: "`ReactDOMTestUtils.act` is deprecated in favor of `React.act`. Import `act` from `react`...". On 18.0–18.2 import from `react-dom/test-utils` or `react-test-renderer`.

```js
import { act } from 'react';

// synchronous
act(() => {
  user.click(); // dispatch a React event
});

// async — await the whole flow, including effects and transitions
await act(async () => {
  fireEvent.submit(form);
  await waitFor(() => expect(screen.getByText('Saved')).toBeInTheDocument());
});
```

Semantics (18 implementation):

- Batches updates inside the callback (replicates `batchedUpdates` in legacy mode).
- Flushes the React work queue and passive effects before resolving; nested `act` scopes are supported.
- `act` is a **development-only** API — in production builds it throws.
- Wrap *effects that React schedules in response to* your action: state updates, `startTransition` callbacks, promise resolutions that call `setState`.

## Enabling act warnings

Since 18.0 the "An update to Component inside a test was not wrapped in act(...)" warnings are **opt-in**. Set in your test setup (e.g., `setupTests.js` / vitest setup):

```js
globalThis.IS_REACT_ACT_ENVIRONMENT = true;
```

Without it React stays silent about un-wrapped updates — a common source of confusing "stale DOM in test" bugs. End-to-end (Playwright/Cypress) environments should leave it off; unit tests should turn it on.

## react-test-renderer

A DOM-free renderer producing a pure JS tree — handy for snapshot-testing component logic without jsdom.

```js
import TestRenderer, { act } from 'react-test-renderer';

let renderer;
act(() => {
  renderer = TestRenderer.create(<Counter />);
});
expect(renderer.toJSON()).toMatchObject({ type: 'button', children: ['0'] });

act(() => { buttonRef.current.dispatchEvent(new Event('click')); });
renderer.unmount();
```

- `toJSON()` gives the rendered element tree (host components as `{ type, props, children }`, text as strings, `null` for empty).
- `testRenderer.root` walks the tree by type/props (`findByType`, `findAllByProps`, `findByProps`).
- Host instances expose the simulated DOM (attributes, children) without a browser.

## react-dom/test-utils

| Export | Status |
|---|---|
| `Simulate[eventName](node, eventData)` | Dispatches a synthetic event through React's event system on a real DOM node (jsdom). Supported: full `DOMPluginEventSystem` list — `click`, `change`, `submit`, `input`, `keydown`/`keyup`/`keypress`, `focus`/`blur`, `drag*`, `drop`, `copy`/`cut`/`paste`, `composition*`, pointer events, `touch*`, media events, `mouseEnter`/`mouseLeave`, `pointerEnter`/`pointerLeave`, `select`, `beforeInput`, etc. |
| `act` | **Deprecated in 18.3** — import from `react` |
| `renderIntoDocument`, `isElement`, `isElementOfType`, `isDOMComponent`, `isDOMComponentElement`, `isCompositeComponent`, `isCompositeComponentWithType`, `findAllInRenderedTree`, `scryRendered{DOMComponents}With{Class,Tag}`, `findRendered{Component,DOMComponent}With{Type,Class,Tag}`, `mockComponent`, `nativeTouchData` | Legacy (pre-16) helpers — avoid in new code; query the DOM (Testing Library) instead |

## Patterns

- **Render inside act, assert outside** — the render call itself schedules work:
  ```js
  let container;
  act(() => { container = render(<App />); });
  expect(container.querySelector('h1').textContent).toBe('Hi');
  ```
- **Transitions**: `await act(async () => { startTransition(() => setFilter('x')); });` — the awaited act flushes the transition's updates; check `isPending` inside if you want the in-flight state.
- **Suspense**: render with a stub that throws a pending promise; `await act(async () => { resolve(data); });` to resolve the boundary, then assert content.
- **Error boundaries**: `act(() => { trigger(); })` and assert the fallback rendered; React recovers to the boundary, not the app.
- **Timers/scheduler**: `jest.useFakeTimers()` to control scheduling; `scheduler`'s `unstable_mock` entry is for framework-level tests, not app tests.
- **Multiple React copies** break hooks ("Invalid hook call") — dedupe `react` in `jest.config` (`moduleNameMapper`) or the bundler; a test-only copy of `react` alongside the app's copy is the usual cause.

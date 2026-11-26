# View Transitions (19.3.0)

Contents

- [Background: the browser API](#background-the-browser-api)
- [The ViewTransition component](#the-viewtransition-component)
- [Props](#props)
- [Class props](#class-props)
- [Event callbacks](#event-callbacks)
- [Transition types with addTransitionType](#transition-types-with-addtransitiontype)
- [Combining with Suspense and Activity](#combining-with-suspense-and-activity)
- [Graceful degradation](#graceful-degradation)

## Background: the browser API

The View Transitions API (`document.startViewTransition`) captures the old and new DOM as snapshots and cross-fades (or custom-animates) between them, exposing CSS hooks: `::view-transition`, `::view-transition-old(name)`, `::view-transition-new(name)`, `::view-transition-group(name)`, and `::view-transition-image-pair(name)`. Elements opt in by sharing a `view-transition-name`. React 19.3.0 wraps this API so you can declare transitions in your component tree.

## The `ViewTransition` component

```jsx
import { ViewTransition, Suspense, useState } from 'react';

function App() {
  const [page, setPage] = useState('/home');
  return (
    <ViewTransition name="page">
      <Suspense fallback={<PageSkeleton />}>
        <Page url={page} onNavigate={setPage} />
      </Suspense>
    </ViewTransition>
  );
}
```

React applies the `name` to the subtree as a `view-transition-name` and drives `document.startViewTransition` when the subtree mounts, unmounts, or updates **inside `startTransition`**.

## Props

- **`name`** (`string`) — the `view-transition-name` for the subtree. Omit it (or pass `"auto"`) to have React generate a unique name per instance.
- **`children`** — the subtree to animate.

## Class props

Class props apply CSS classes to the transition's view-transition pseudo-elements for each phase:

- **`default`** — applies to the overall transition,
- **`enter`** — entering elements (mounts),
- **`exit`** — exiting elements (unmounts),
- **`update`** — elements that update in place,
- **`share`** — elements whose `view-transition-name` is shared between old and new snapshots,
- **`parentEnter`** / **`parentExit`** — applied to the parent group when this subtree enters/exits inside a larger transition.

Each accepts a class string, `'none'`, `'auto'`, or a **per-transition-type map**:

```jsx
<ViewTransition
  name="route"
  default="fade"
  enter={{ push: 'slide-in-from-right', pop: 'slide-in-from-left' }}
  exit="fade-out"
/>
```

The map is keyed by transition type (see below); `'auto'` picks React's default classes.

## Event callbacks

Callbacks receive the native `ViewTransition` instance and the transition's types, and may return a cleanup function:

- **`onEnter(instance, types)`** — subtree mounts,
- **`onExit(instance, types)`** — subtree unmounts,
- **`onUpdate(instance, types)`** — subtree updates,
- **`onShare(instance, types)`** — a shared name transitions,
- **`onParentEnter(instance, types)`** / **`onParentExit(instance, types)`** — nested inside a parent's enter/exit.

```jsx
<ViewTransition
  name="page"
  onEnter={vt => {
    vt.ready.then(() => { /* animate once the snapshot is ready */ });
    return () => { /* cleanup */ };
  }}
>
  {children}
</ViewTransition>
```

`instance` is the DOM `ViewTransition` object — use its `ready`/`updateComplete` promises to drive custom animation timing.

## Transition types with `addTransitionType`

`addTransitionType('push')` (from `react`) tags the **current transition** so per-type class maps and callback `types` can distinguish it. It must be called inside a `startTransition` (or `startGestureTransition`) callback — calling it outside an active transition warns:

```jsx
function navigate(url, type = 'push') {
  startTransition(() => {
    addTransitionType(type);
    setPage(url);
  });
}
```

Types stack — a single transition can carry several.

## Combining with Suspense and `Activity`

- **Suspense** — when a suspended boundary reveals inside a `ViewTransition`, the reveal participates in the transition (fallback → content cross-fades). This is the routing use case: navigation updates in a transition, Suspense streams content as data resolves.
- **`Activity`** — `<Activity hidden={...}>` hides/restores a subtree without unmounting it; drive `hidden` inside `startTransition` and wrap in `ViewTransition` for animated show/hide with preserved state.
- Multiple `ViewTransition` siblings can nest; React pairs entering/exit instances during commit so old and new snapshots animate together.

## Graceful degradation

If the browser lacks the View Transitions API (or `document.startViewTransition` is unavailable), content updates exactly as it would without a `ViewTransition` — no animation, no error. Write the transition as progressive enhancement, not as the primary loading indicator.

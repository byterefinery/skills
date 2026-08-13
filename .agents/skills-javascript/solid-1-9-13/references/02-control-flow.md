# Control Flow

Solid's control flow components are reactive — they track their inputs and only update the affected DOM branches. They are imported from `solid-js` (not a separate package).

## For — Keyed List

```tsx
import { For } from "solid-js";

<For each={items()} fallback={<p>No items</p>}>
  {(item, index) => (
    <li data-index={index()}>{item.name}</li>
  )}
</For>
```

- `each` — the list accessor (reactive)
- `children` — render function receiving `(item, indexAccessor)`
- `fallback` — rendered when `each` is empty/null/false
- Tracks items by identity — efficient DOM reuse when items move/add/remove
- Items must have stable identity (use objects, not regenerated primitives)

**When to use:** Lists where items have identity and can be reordered/added/removed.

**Gotchas:**
- If your items are recreated every render (e.g., `items.map(i => ({ ...i }))`), `<For>` will replace all DOM nodes. Use `<Index>` or ensure stable identities.
- `index` is an accessor — call it with `index()` inside reactive contexts.

## Index — Non-Keyed List

```tsx
import { Index } from "solid-js";

<Index each={items()} fallback={<p>No items</p>}>
  {(item, i) => <li>{i}: {item().name}</li>}
</Index>
```

- `children` receives `(itemAccessor, index)` — note: `item` is the accessor, `i` is a plain number
- Fixed positions — DOM nodes stay at their index, only values update
- No identity tracking — positions are stable, contents change

**When to use:** Lists with fixed positions but changing values (e.g., a fixed-size grid where cell values update).

**Gotchas:**
- `item` is an accessor function — call it with `item()`, not `item`.
- `i` is a plain number, not an accessor.

## Show — Conditional Rendering

```tsx
import { Show } from "solid-js";

// Simple form — children render regardless, visibility toggled
<Show when={condition()}>
  <Component />
</Show>

// With fallback
<Show when={condition()} fallback={<EmptyState />}>
  <Component />
</Show>

// Function children — deferred rendering (children only run when condition is true)
<Show when={user()}>
  {(user) => <div>{user.name}</div>}
</Show>

// Keyed mode — recreates children when value changes (not just truthiness)
<Show when={id()} keyed>
  <Component id={id()} />
</Show>
```

- `when` — condition accessor (reactive)
- `fallback` — rendered when condition is falsy
- `keyed` — when `true`, recreates children on every value change (not just truthy/falsy transitions)
- Function children receive the condition value (accessor in non-keyed, raw value in keyed mode)

**When to use:** Any conditional rendering. Prefer function children form when the child is expensive to create.

**Gotchas:**
- Without function children, the child component is created regardless of the condition (only visibility changes). Use the function form for true conditional creation.
- `<Show when={a()} keyed>` recreates on every `a` change. `<Show when={a()}>` only toggles on truthy/falsy boundary.

## Switch / Match — Multi-Way Branching

```tsx
import { Switch, Match } from "solid-js";

<Switch fallback={<Unknown />}>
  <Match when={state() === "loading"}>
    <LoadingSpinner />
  </Match>
  <Match when={state() === "error"}>
    <ErrorMessage error={error()} />
  </Match>
  <Match when={state() === "ready"}>
    <Content data={data()} />
  </Match>
</Switch>
```

- `<Switch>` wraps `<Match>` children
- First truthy `<Match>` wins (mutually exclusive)
- `fallback` — rendered when no match is truthy
- `keyed` on `<Match>` — same semantics as `<Show keyed>`

**When to use:** Multiple mutually exclusive conditions (replaces if/else chains).

**Gotchas:**
- Only one `<Match>` renders at a time — the first with a truthy `when`.
- `<Match>` must be a direct child of `<Switch>`.

## ErrorBoundary

```tsx
import { ErrorBoundary } from "solid-js";

// Static fallback
<ErrorBoundary fallback={<div>Something went wrong</div>}>
  <RiskyComponent />
</ErrorBoundary>

// Callback form — receives error and reset function
<ErrorBoundary
  fallback={(err, reset) => (
    <div>
      <p>Error: {err.message}</p>
      <button onClick={reset}>Retry</button>
    </div>
  )}
>
  <RiskyComponent />
</ErrorBoundary>
```

- Catches errors thrown in child components and their effects
- `fallback` — static JSX or callback `(error, reset) => JSX`
- `reset()` re-renders the children to attempt recovery
- Nested boundaries: errors re-thrown in the fallback bubble to the parent boundary
- `resetErrorBoundaries()` — programmatically reset all boundaries

**When to use:** Wrap components that might throw (API data rendering, third-party components, user-generated content).

**Gotchas:**
- Only catches synchronous errors and errors in effects. Promise rejections need `.catch()` or `try/catch` in the effect.
- The callback form `(err, reset) => JSX` requires the function to have parameters (`fn.length > 0`). A zero-parameter function is treated as static JSX.

## Dynamic Component

```tsx
import { Suspense } from "solid-js";

// Render different components based on a signal
const [page, setPage] = createSignal("home");

// Using JSX directly with a variable component type
<{ [key: string]: Component }>
const pages = { Home, About, Settings };

<.pages[page()] />

// Or with dynamic attribute
const Component = pages[page()];
<Component />
```

Solid doesn't have a `<Dynamic>` component like React's `<Component />`. Instead, use computed component types or conditional rendering with `<Switch>`.

## Index vs For — Decision Guide

| Scenario | Use |
|---|---|
| Items have IDs, can reorder/add/remove | `<For>` |
| Fixed-size list, values change in place | `<Index>` |
| Simple static list | Plain `map()` in JSX |
| Need index as a number (not accessor) | `<Index>` |
| Need stable DOM for animations | `<For>` |

## Pattern: Conditional Lists

```tsx
// Show loading, empty, or data states
<Switch>
  <Match when={loading()}>
    <Spinner />
  </Match>
  <Match when={items().length === 0}>
    <EmptyState />
  </Match>
  <Match when={items().length > 0}>
    <For each={items()}>
      {(item) => <ItemCard item={item} />}
    </For>
  </Match>
</Switch>
```

## Pattern: Nested Conditionals

```tsx
<Show when={user()}>
  {(user) => (
    <Show when={user.role === "admin"}>
      <AdminPanel />
    </Show>
  )}
</Show>
```

Function children form allows accessing the unwrapped value in nested conditionals.

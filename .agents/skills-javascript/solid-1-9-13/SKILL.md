---
name: solid-1-9-13
description: Solid.js 1.9.13 — reactive UI library with fine-grained reactivity via signals. Covers createSignal, createMemo, createEffect, createResource, context, control flow components (For, Show, Switch/Match, Index, Suspense, ErrorBoundary), lazy loading, SSR, splitProps/mergeProps, and the JSX-based component model. Use when building Solid.js apps, working with fine-grained reactive state, migrating from React/Vue, or debugging Solid reactivity patterns.
license: MIT
compatibility: Requires Node.js 18+ for build tooling. Browsers: ES2017+ (Chrome 62+, Firefox 58+, Safari 11.1+, Edge 79+). JSX transform via babel-preset-solid or @babel/plugin-transform-react-jsx.
allowed-tools: Bash(npm:*) Bash(npx:*) Bash(pnpm:*) Bash(yarn:*) Bash(bun:*) Read
metadata:
  tags:
    - javascript
    - frontend
    - ui
    - framework
    - reactive
    - signals
    - jsx
    - ssr
---

# solid 1.9.13

## Overview

Solid.js 1.9.13 is a declarative JavaScript framework for building user interfaces, using fine-grained reactive signals under the hood. Unlike React's Virtual DOM approach, Solid compiles JSX into real DOM nodes and wires reactivity directly — updates hit only the exact DOM nodes that changed, with no diffing overhead.

Solid shares JSX syntax with React but has a fundamentally different mental model:
- **Signals** (`createSignal`) are the primitive — getters/setter pairs, not state setters
- **Memo** (`createMemo`) derives computed values lazily
- **Effects** (`createEffect`) run side effects after render
- Components are called once; reactivity flows through signal reads inside them
- No `useState`, no `useEffect`, no Virtual DOM

The library ships three entry points: `solid-js` (client), `solid-js/web` (DOM rendering), and `solid-js/server` (SSR). JSX is transformed via `babel-preset-solid` or the native JSX transform into `solid-js/jsx-runtime`.

## Usage

### Project scaffolding

```bash
npx degit solidjs/templates/base my-app
cd my-app && npm install && npm run dev
```

Templates: `base` (Vite, TypeScript), `javascript` (Vite, JS), `lit` (Web Components), `tamagot` (Tamagui), `three` (Three.js integration), `tailwind-css` (Tailwind).

### Signals — the core primitive

```tsx
import { createSignal } from "solid-js";

function Counter() {
  const [count, setCount] = createSignal(0);

  return (
    <button onClick={() => setCount(count() + 1)}>
      Count: {count()}
    </button>
  );
}
```

Signals return a tuple `[getter, setter]`. The getter is a function — **always call it** with `()`. The setter accepts a new value or an updater function `(prev) => newValue`. Signal reads inside a reactive context (component render, memo, effect) automatically create tracking dependencies.

### Memos — derived state

```tsx
import { createMemo, createSignal } from "solid-js";

function Search() {
  const [query, setQuery] = createSignal("");
  const [items] = createSignal(allItems);

  const filtered = createMemo(() =>
    items().filter(i => i.name.includes(query()))
  );

  return (
    <>
      <input value={query()} onInput={e => setQuery(e.currentTarget.value)} />
      <For each={filtered()}>{item => <div>{item.name}</div>}</For>
    </>
  );
}
```

Memos are lazy — they only recompute when read after a dependency changes. Use them for expensive computations or to narrow dependency graphs.

### Effects — side effects

```tsx
import { createEffect, createSignal } from "solid-js";

function Logger() {
  const [count, setCount] = createSignal(0);

  createEffect(() => {
    console.log("count changed to", count());
  });

  return <button onClick={() => setCount(c => c + 1)}>Increment</button>;
}
```

Effects run after render. They track all signal reads inside their callback automatically. Use `on()` to make dependencies explicit and avoid tracking unwanted signals.

### Explicit dependencies with `on()`

```tsx
import { createEffect, on, createSignal } from "solid-js";

function Watch() {
  const [a, setA] = createSignal(0);
  const [b, setB] = createSignal(0);

  // Only tracks `a`, not `b`
  createEffect(on(a, v => console.log("a =", v, "b =", b())));

  return (
    <>
      <button onClick={() => setA(a => a + 1)}>A: {a()}</button>
      <button onClick={() => setB(b => b + 1)}>B: {b()}</button>
    </>
  );
}
```

`on(deps, fn)` tracks only `deps` reactively; reads inside `fn` are untracked. This prevents unnecessary re-runs.

### Control flow components

Solid provides reactive control flow as components — they track their conditions and only update the affected branches:

```tsx
import { For, Show, Switch, Match, Index } from "solid-js";

function List() {
  const [items, setItems] = createSignal([
    { id: 1, name: "Alice" },
    { id: 2, name: "Bob" },
  ]);
  const [status, setStatus] = createSignal<"loading" | "ready" | "error">("loading");

  return (
    <>
      {/* Keyed list — tracks by identity, efficient DOM updates */}
      <For each={items()} fallback={<p>No items</p>}>
        {(item, index) => (
          <li data-index={index()}>
            {item.name}
          </li>
        )}
      </For>

      {/* Non-keyed — fixed positions, changing values */}
      <Index each={items()}>
        {(item, i) => <li>{i}: {item().name}</li>}
      </Index>

      {/* Conditional rendering */}
      <Show when={items().length > 0} fallback={<p>Empty</p>}>
        <p>Has items</p>
      </Show>

      {/* Multi-way branching */}
      <Switch fallback={<div>Unknown</div>}>
        <Match when={status() === "loading"}>Loading...</Match>
        <Match when={status() === "error"}>Error!</Match>
        <Match when={status() === "ready"}>Ready</Match>
      </Switch>
    </>
  );
}
```

- `<For>` — keyed iteration (stable identity tracking, like `key` in React)
- `<Index>` — non-keyed iteration (fixed positions, values change)
- `<Show>` — conditional rendering with optional fallback
- `<Switch>` / `<Match>` — mutually exclusive conditionals (first truthy wins)

### Context — cross-cutting state

```tsx
import { createContext, useContext, createSignal } from "solid-js";

const ThemeContext = createContext<{
  theme: string;
  setTheme: (t: string) => void;
}>();

function App() {
  const [theme, setTheme] = createSignal("light");

  return (
    <ThemeContext.Provider value={{ theme: theme, setTheme }}>
      <Toolbar />
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  const ctx = useContext(ThemeContext);
  return <button onClick={() => ctx.setTheme("dark")}>
    Current: {ctx.theme()}
  </button>;
}
```

Context provides dependency injection through the component tree. `createContext(defaultValue?)` creates a context; `Context.Provider` supplies values; `useContext(Context)` reads them.

### Resources — async data

```tsx
import { createResource, Suspense } from "solid-js";

function UserPage({ id }: { id: string }) {
  const [user] = createResource(() => fetch(`/api/users/${id}`).then(r => r.json()));

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div>
        <h1>{user()?.name}</h1>
        <p>{user()?.email}</p>
      </div>
    </Suspense>
  );
}
```

Resources wrap async operations in reactive state. They expose `.state` (`"unresolved"`, `"pending"`, `"ready"`, `"refreshing"`, `"errored"`), `.loading`, `.error`, and `.latest`. Resources integrate with `<Suspense>` for automatic pending states.

Resource actions: `[resource, { mutate, refetch }] = createResource(...)`.

### Lazy components

```tsx
import { lazy, Suspense } from "solid-js";

const HeavyChart = lazy(() => import("./HeavyChart"));

function Dashboard() {
  return (
    <Suspense fallback={<div>Loading chart...</div>}>
      <HeavyChart data={chartData} />
    </Suspense>
  );
}
```

`lazy()` wraps dynamic `import()` and returns a component that suspends until loaded. Use `.preload()` for prefetching: `HeavyChart.preload()`.

### Error boundaries

```tsx
import { ErrorBoundary } from "solid-js";

function App() {
  return (
    <ErrorBoundary
      fallback={(err, reset) => (
        <div onClick={reset}>
          <p>Error: {err.message}</p>
          <button>Retry</button>
        </div>
      )}
    >
      <RiskyComponent />
    </ErrorBoundary>
  );
}
```

Catches errors in child scopes and renders a fallback. The callback form receives `(error, reset)` for recovery.

### Props handling — `splitProps` and `mergeProps`

```tsx
import { Component, splitProps, mergeProps } from "solid-js";

interface ButtonProps {
  variant?: "primary" | "secondary";
  size?: "sm" | "lg";
  onClick?: () => void;
  [key: string]: any;
}

const defaultProps = { variant: "primary" as const, size: "sm" as const };

const Button: Component<ButtonProps> = (props) => {
  const [local, others] = splitProps(
    mergeProps(defaultProps, props),
    "variant", "size", "onClick"
  );

  return (
    <button
      class={`btn btn-${local.variant} btn-${local.size}`}
      onClick={local.onClick}
      {...others}
    >
      {props.children}
    </button>
  );
};
```

- `splitProps(props, ...keys)` — partitions props into tracked subsets (preserves fine-grained reactivity)
- `mergeProps(...sources)` — merges defaults with passed props reactively

### Lifecycle hooks

```tsx
import { onMount, onCleanup } from "solid-js";

function Timer() {
  const [seconds, setSeconds] = createSignal(0);

  onMount(() => {
    const id = setInterval(() => setSeconds(s => s + 1), 1000);
    onCleanup(() => clearInterval(id));
  });

  return <span>{seconds()}s</span>;
}
```

- `onMount(fn)` — runs once after initial render
- `onCleanup(fn)` — runs when the component/scope is disposed

### `untrack()` and `batch()`

```tsx
import { createSignal, createEffect, untrack, batch } from "solid-js";

function Example() {
  const [a, setA] = createSignal(0);
  const [b, setB] = createSignal(0);

  // Read `a` reactively, `b` without tracking
  createEffect(() => {
    console.log(a(), untrack(() => b()));
  });

  // Group multiple updates — effects fire once after all changes
  const updateBoth = () => batch(() => {
    setA(a => a + 1);
    setB(b => b + 1);
  });
}
```

- `untrack(fn)` — executes `fn` outside the reactive tracking context
- `batch(fn)` — groups updates; dependent effects fire once after all changes

### Custom elements (Web Components)

```tsx
import { customElement, withSolid } from "solid-element";
import { createSignal } from "solid-js";
import { render } from "solid-js/web";

@customElement("my-counter")
class MyCounter extends withSolid(() => {
  const [count, setCount] = createSignal(0);
  return () => (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count()}
    </button>
  );
}) {}
```

`solid-element` provides `withSolid()` and `@customElement` decorator for creating Web Components from Solid functions.

### SSR

```tsx
// server.ts
import { renderToString } from "solid-js/web";
import { App } from "./App";

const html = renderToString(() => <App />);
```

SSR uses `solid-js/server` entry point. Hydration is enabled via `enableHydration()` in the client entry. Solid's SSR supports `<Suspense>` streaming with `deferStream` option on resources.

## Gotchas

- **Signals are functions, not values** — always call with `count()`, never `count`. Forgetting `()` is the most common mistake. In JSX expressions like `{count()}`, the parentheses are required.
- **Components render once** — unlike React, Solid components are called once. All reactivity comes from signal reads inside the component body. Re-rendering doesn't happen; signals push updates to dependent computations.
- **`splitProps` is essential for reactivity** — without it, accessing `props.someKey` inside effects/memos tracks the entire props object. Use `splitProps(props, "key1", "key2")` to get fine-grained tracking per prop subset.
- **`<For>` needs stable identities** — items in `<For>` should have consistent identity (objects, not primitives regenerated each render). If items are recreated every render, use `<Index>` instead.
- **`<Show>` with function children** — `<Show when={condition}>{() => <div>{value()}</div>}` defers rendering until the condition is truthy. Without the function form, the child renders regardless.
- **Memo narrows the dependency graph** — wrapping a computation in `createMemo` isolates its dependencies. Effects reading the memo only re-run when the memo's output changes, not when inner signals change.
- **`on()` for explicit deps** — when an effect reads many signals but should only track a few, use `on(signal, (v) => { /* reads here are untracked */ })`. This is the Solid equivalent of React's dependency array.
- **`equals` option prevents unnecessary updates** — `createSignal({}, { equals: false })` forces updates on every set. `createSignal(0, { equals: (a, b) => Math.abs(a - b) < 0.01 })` uses a custom comparator. Default is strict equality.
- **No `key` prop** — Solid doesn't use `key` like React. Use `<For>` for keyed lists and `<Index>` for non-keyed. The control flow components handle DOM reconciliation internally.
- **JSX transform is required** — Solid's JSX has different semantics than React's. Use `babel-preset-solid` or configure the JSX pragma to `solid-js/jsx-runtime`. The transform compiles JSX into efficient DOM operations, not `React.createElement`.
- **`createEffect` vs `createRenderEffect` vs `createComputed`** — `createEffect` runs after render (for side effects). `createRenderEffect` runs during render (for DOM-like updates). `createComputed` runs before render (for writing to other signals). Use `createEffect` for 95% of cases.
- **Resources auto-track the source** — `createResource(source, fetcher)` re-runs the fetcher when `source` changes. Pass `false`/`null`/`undefined` to the source to cancel. Use `refetch()` to re-run without source change.
- **`lazy()` returns a component, not a promise** — call it like `<LazyComponent />`, don't `await` it. Use `.preload()` for prefetching.

## References

- [01-reactivity-primitives](references/01-reactivity-primitives.md) — Signals, memos, effects, computed, reaction, deferred, selector
- [02-control-flow](references/02-control-flow.md) — For, Index, Show, Switch/Match, ErrorBoundary patterns
- [03-async-patterns](references/03-async-patterns.md) — Resources, Suspense, SuspenseList, transitions, lazy loading
- [04-component-patterns](references/04-component-patterns.md) — Props typing, splitProps, mergeProps, refs, dynamic components
- [05-context-and-state](references/05-context-and-state.md) — createContext, useContext, observable, from, state management patterns
- [06-ssr-and-hydration](references/06-ssr-and-hydration.md) — Server-side rendering, streaming, hydration, sharedConfig
- [07-jsx-and-transform](references/07-jsx-and-transform.md) — JSX runtime, babel-preset-solid, spread attributes, event handlers
- [08-web-components](references/08-web-components.md) — solid-element, custom elements, withSolid, shadow DOM

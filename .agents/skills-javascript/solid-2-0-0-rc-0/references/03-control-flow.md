# Control flow

One list primitive (`For`) with explicit keying, `Repeat` for ranges, renamed async/error boundaries (`Loading`/`Errored`), `Reveal` for coordinating boundaries, and the `dynamic` factory.

## For — keyed, non-keyed, custom key

The callback shape depends on the keying mode:

| Mode | `item` | `i` |
|---|---|---|
| default / `keyed={true}` (identity) | raw value | accessor (rows can move) |
| `keyed={false}` (replaces `Index`) | accessor | stable plain number |
| `keyed={(item) => key}` | accessor | accessor |

```jsx
<For each={todos()} fallback={<EmptyState />}>
  {(todo, i) => <TodoRow todo={todo} index={i()} />}
</For>

<For each={todos()} keyed={false}>
  {(todo, i) => <TodoRow todo={todo()} index={i} />}
</For>

<For each={todos()} keyed={(t) => t.id}>
  {(todo) => <TodoRow todo={todo()} />}
</For>
```

Prefer literal `keyed` modes with function children — a dynamic boolean `keyed={condition()}` makes the callback shape ambiguous.

## Repeat — range/count rendering (no diffing)

Children receive a **plain number** (the slot's index never changes). Built for store-backed lists where the store handles granular updates, plus skeletons and windowing:

```jsx
<Repeat count={store.items.length} fallback={<EmptyState />}>
  {(i) => <Row name={store.items[i].name} status={store.items[i].status} />}
</Repeat>

<Repeat count={10}>{i => <Skeleton key={i} />}</Repeat>
<Repeat count={visibleCount()} from={start()}>{i => <Row index={i} />}</Repeat>
```

## Show / Switch / Match

Function children receive a **narrowed accessor** (non-keyed) — call it. The `keyed` variant receives the raw narrowed value.

```jsx
<Show when={user()} fallback={<Login />}>
  {u => <Profile user={u()} />}
</Show>

<Show when={user()} keyed>{u => <Profile user={u} />}</Show>

<Switch fallback={<NotFound />}>
  <Match when={route() === "home"}><Home /></Match>
  <Match when={route() === "profile"}>{() => <Profile />}</Match>
</Switch>
```

## Loading — the async boundary (replaces Suspense)

Shows `fallback` while the subtree reads not-ready async values. Covers **branch readiness**: once content has rendered, revalidation keeps stale content visible by default.

```jsx
<Loading fallback={<Spinner />}>
  <UserProfile id={id()} />
</Loading>

// `on` prop: re-show fallback when this expression changes while async is pending
<Loading on={id()} fallback={<Spinner />}>
  <UserProfile id={id()} />
</Loading>
```

`renderToString` renders `fallback` for pending boundaries. Uncaught async outside any `Loading` holds the root mount until it settles (dev warns `ASYNC_OUTSIDE_LOADING_BOUNDARY`) — the permissive default, fine when you don't want fallback UI.

## Errored — the error boundary (replaces ErrorBoundary)

```jsx
<Errored
  fallback={(err, reset) => (
    <div>
      <p>Something went wrong.</p>
      <pre>{String(err())}</pre>
      <button onClick={reset}>Retry</button>
    </div>
  )}
>
  <Page />
</Errored>
```

`fallback` is an element or a callback receiving an **error accessor** and a **reset action**. Boundaries heal automatically when the retry succeeds — `resetErrorBoundaries` is gone.

## Reveal — coordinates sibling Loadings (replaces SuspenseList)

Props: `order` (`"sequential"` | `"together"` | `"natural"`, default `"sequential"`) and `collapsed` (sequential-only — boundaries past the frontier render nothing instead of their own fallback).

```jsx
<Reveal> {/* sequential: reveal in DOM order as each resolves */}
  <Loading fallback={<Skeleton />}><ProfileHeader /></Loading>
  <Loading fallback={<Skeleton />}><Posts /></Loading>
</Reveal>

<Reveal order="together"> {/* wait for the whole group, then reveal at once */}
  <Loading fallback={<Skeleton />}><A /></Loading>
  <Loading fallback={<Skeleton />}><B /></Loading>
</Reveal>

<Reveal collapsed> {/* only the frontier shows a fallback */}
  <Loading fallback={<S />}><A /></Loading>
  <Loading fallback={<S />}><B /></Loading>
</Reveal>
```

Nesting: a nested `<Reveal>` is one **composite slot** to its parent — held on fallbacks until the parent's frontier reaches it, then it resumes its own order locally. No opt-out: wrapping children in extra `<Loading>` doesn't escape a hold. Group membership is direct-children-only; a `<Loading>`/`<Errored>` inside a slot severs coordination for its subtree. `order="natural"` marks "one slot to my parent, children don't coordinate". SSR: `renderToString` supports sequential (without `collapsed`) and natural; `together`/`collapsed` require `renderToStream`.

## Dynamic components — dynamic factory and <Dynamic>

`createDynamic(source, props)` is reshaped into a `lazy`-style factory returning a **stable `Component<P>`** whose identity is driven reactively:

```jsx
import { dynamic, Dynamic } from "@solidjs/web";

const Active = dynamic(() => (isEditing() ? Editor : Viewer));
return <Active value={value()} />;

// Native tag swap
const Tag = dynamic(() => (multiline() ? "textarea" : "input"));

// JSX-wrapper convenience (unchanged from 1.x at the call site)
<Dynamic component={isEditing() ? Editor : Viewer} value={value()} />
```

The source may return a `Promise<Component | string | undefined>` — async sources compose with `Loading` through the normal not-ready flow (no `await` in user code). Source evaluation is shared across all mounted instances of the returned component.

## clientOnly — browser-only components (from @solidjs/web)

Wraps a dynamically imported component so the server renders `props.fallback` and **never starts the import**:

```jsx
import { clientOnly } from "@solidjs/web";

const Chart = clientOnly(() => import("./Chart.jsx"));

<Chart fallback={<div>Loading chart…</div>} data={data()} />;
```

Unlike `lazy()`, it avoids Suspense/`Loading` entirely and participates in no hydration asset manifest. The swap to the real component happens after the tree settles — hydration is mismatch-free by construction. `{ lazy: true }` defers the import to first render; the importer runs at most once regardless of instance count. The bundler injects the module URL for an early `modulepreload` hint. Use it for anything touching `window`, measuring the DOM, or simply unavailable on the server.

## Context — the context is the provider

```jsx
// Default-less — canonical form for reactive state.
// No Provider → ContextNotFoundError; useContext is typed T (not T | undefined).
type TodosCtx = readonly [Store<Todo[]>, TodoActions];
const TodosContext = createContext<TodosCtx>();

function App() {
  return (
    <TodosContext value={createTodos()}>
      <TodoList />
    </TodosContext>
  );
}

function TodoList() {
  const [todos, { addTodo }] = useContext(TodosContext);
}

// Default form — primitive fallbacks only (theme, locale, frozen config)
const Theme = createContext<"light" | "dark">("light");
```

`Context.Provider` is gone — the context value **is** the provider component. Drop the 1.x `useX`-with-throw wrapper hooks; the default-less form already throws. If you want truly app-wide state, don't use Context — a module-scope signal/store *is* a global.

## Children, lazy, component types

```tsx
import { children, lazy, type Component, type VoidComponent, type ParentComponent, type FlowComponent, type Element } from "solid-js";

const list = children(() => props.children);
list.toArray();

const Heavy = lazy(() => import("./Heavy")); // use .preload() to prefetch

type Basic = Component<P>;          // no implicit children
type Empty = VoidComponent<P>;       // forbids children
type WithChildren = ParentComponent<P>; // optional Element children
type Flow = FlowComponent<P, C>;     // requires children of type C
```

For renderer-neutral annotations use `Element` from `solid-js` — `JSX.Element` now comes from the renderer package (see [08-typescript-jsx-transform](08-typescript-jsx-transform.md)).

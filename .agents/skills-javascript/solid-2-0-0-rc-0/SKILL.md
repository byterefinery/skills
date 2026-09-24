---
name: solid-2-0-0-rc-0
description: SolidJS 2.0.0-rc.0 — fine-grained reactive UI library that compiles templates to real DOM updates. Covers the 2.0 public API (which differs from 1.x and React) — split-phase createEffect, microtask batching with flush, signals and writable memos, draft-first stores and projections, actions with optimistic updates, async-in-computations with Loading/Errored/Reveal boundaries, For/Repeat/Show/Switch control flow, context, @solidjs/web render/hydrate/Portal, streaming SSR, server functions — and the @solidjs/html tagged template literal (html) for build-less templating. Use when writing or migrating SolidJS 2.0 code, building reactive Solid apps, or using the html tagged template literal.
license: MIT
compatibility: Node.js 20+ for build tooling; Vite with babel-preset-solid recommended for JSX. Browsers — last 2 years of Chrome, Firefox, Safari, Edge. The html tagged template literal works with no build step. SSR targets Node, Deno, Cloudflare Workers.
metadata:
  tags:
    - javascript
    - frontend
    - ui
    - framework
    - reactive
    - signals
    - jsx
    - tagged-templates
    - ssr
---

# solid-2-0-0-rc-0

## Overview

Solid 2.0.0-rc.0 is a major rewrite of the SolidJS fine-grained reactive UI library. Templates compile to real DOM nodes; updates touch only the exact DOM positions that read a changed value — no virtual DOM, no diffing. Component functions run once; reactivity flows through signal reads.

**2.0 is not 1.x and not React.** Models trained on either pattern-match wrong: `createEffect` takes two arguments, `createResource`/`Suspense`/`Index`/`batch`/`onMount` are gone, reads don't update until the microtask flushes, and writes inside a reactive scope throw in dev. When in doubt, treat this skill's API as the source of truth, not 1.x examples.

### Packages

| Package | Role |
|---|---|
| `solid-js` | Core — signals, memos, effects, stores, control-flow components, context, actions |
| `@solidjs/web` | DOM runtime — `render`, `hydrate`, `Portal`, `Dynamic`, `dynamic`, `clientOnly`, SSR, server functions, `httpStatus`/`httpHeader` |
| `@solidjs/html` | `html` tagged template literal — write components with no build step (JSX alternative) |
| `@solidjs/h` | Hyperscript `h()` factory (also usable as a standard JSX transform factory) |
| `@solidjs/universal` | `createRenderer` for custom renderers (non-DOM platforms) |
| `@solidjs/signals` | The reactive core (embedded in `solid-js`, usable standalone) |
| `@solidjs/element` | Web Components wrapper |
| `babel-preset-solid` | Compiles JSX to fine-grained DOM operations |

1.x subpaths are gone: `solid-js/web` → `@solidjs/web`, `solid-js/store` → `solid-js` (store APIs moved into core), `solid-js/h` → `@solidjs/h`, `solid-js/html` → `@solidjs/html`, `solid-js/universal` → `@solidjs/universal`.

## Setup

```sh
npm i solid-js @solidjs/web
npm i -D babel-preset-solid
```

```json
{
  "compilerOptions": {
    "jsx": "preserve",
    "jsxImportSource": "@solidjs/web"
  }
}
```

Vite users use `@solidjs/vite-plugin`. 2.0 starter templates are tracked at solidjs/templates; the 1.x templates target 1.x. Without a build step, use the `html` tagged template literal instead of JSX.

## Core reactivity

```ts
import { createSignal, createMemo, createEffect, onSettled, flush } from "solid-js";
import { render } from "@solidjs/web";

function Counter() {
  const [count, setCount] = createSignal(0);
  const doubled = createMemo(() => count() * 2);

  // Split effect — the only form in 2.0. Compute tracks; apply does side effects.
  createEffect(
    () => count(),                     // compute (tracked; receives prev)
    (value, prev) => {                 // apply (untracked; may return cleanup)
      document.title = String(value);
      return () => { document.title = ""; };
    }
  );

  // onSettled replaces onMount — runs once after the settle, may return cleanup
  onSettled(() => {
    const id = setInterval(() => setCount(c => c + 1), 1000);
    return () => clearInterval(id);
  });

  setCount(1);   // queues — count() still returns 0 until the microtask flushes
  flush();       // now count() is 1 and DOM updates have applied

  return <button onClick={() => setCount(c => c + 1)}>{doubled()}</button>;
}

render(() => <Counter />, document.getElementById("app")!);
```

The core rules:

- Signals are `[getter, setter]` pairs; always call the getter with `()`.
- **Writes don't update reads until the microtask batch flushes** — `setX(v); x()` returns the previous value; `flush()` forces synchronous application (tests, imperative interop).
- **`createEffect` is two-argument** `(compute, apply)`; the 1.x single-arg form is an error. Compute receives `prev` (use a default parameter for first-run values); apply returns cleanup.
- **Writes inside an owned scope throw in dev** (memo, effect compute, component body). Move setters to event handlers, `onSettled`, or actions; `{ ownedWrite: true }` is a narrow opt-in for internal state only.
- **Top-level reactive reads in a component body warn** (including destructuring props) — read inside JSX, a memo, or `untrack`.
- **Props are values, not accessors** — pass `value={count()}` at the call site; read `props.value` in the child (the property access is what tracks). Never destructure props.

## html tagged template literal

For no-build environments, `@solidjs/html` provides the `html` tagged template literal as a JSX alternative. Templates are parsed at runtime by the `@dom-expressions/tagged-jsx` engine (AST-based, no `eval` — CSP-safe) and reactive bindings are installed against the resulting DOM.

```ts
import { render } from "@solidjs/web";
import html from "@solidjs/html";
import { createSignal } from "solid-js";

function Button(props) {
  return html`<button class="btn-primary" ...${props} />`;
}

function Counter() {
  const [count, setCount] = createSignal(0);
  const increment = (e) => setCount(c => c + 1);

  // Components close with <//>; expressions bind with ${...}
  return html`<${Button} type="button" onClick=${increment}>${count}<//>`;
}

render(() => <Counter />, document.getElementById("app")!);
```

- Zero-arg functions are auto-wrapped as getters — `${count}` and `${() => count()}` are both reactive; wrap manually for explicitness.
- Component props auto-wrap zero-arg functions, so event handlers passed to **components** must take an event argument — `onClick=${(e) => ...}`, not `onClick=${() => ...}`.
- `ref` is callback form only — `ref=${(el) => (myEl = el)}`.
- Multiple top-level elements are fine — the result is a single node or an array; normalize with `[result].flat()`.
- `html.define({ For, Show })` returns a new tag with those components registered by capitalized name; unregistered capitalized tag names throw at template construction.
- Spread is `...${props}`; force property vs. attribute with `prop:name=${v}` / `attr:name=${v}`.
- `html` is slightly less efficient than compiled JSX (larger non-treeshakeable runtime, no expression analysis) — prefer JSX in build-step projects; use `html` for no-build, script, or server-adjacent contexts.
- Full syntax, registry model, and caveats: [06-html-tagged-template](references/06-html-tagged-template.md).

## Gotchas

- **Distrust 1.x and React patterns** — `Suspense`, `createResource`, `Index`, `batch`, `createComputed`, `on()`, `splitProps`, `mergeProps`, `unwrap`, `onMount`, `ErrorBoundary`, `SuspenseList`, `startTransition` are all gone or renamed (see [09-migration-from-1x](references/09-migration-from-1x.md)).
- **`createEffect` takes two arguments** — `(compute, apply)`; cleanup belongs on the apply side, returned as a function.
- **Setters are batched by microtask** — reads return the previous value until flush; call `flush()` in tests before asserting and in imperative code that needs synchronous DOM.
- **No writes inside owned scope** — a setter call in a memo/effect compute/component body throws in dev. Derive with `createMemo`; write in event handlers, `onSettled`, actions, or `untrack`.
- **Don't destructure props** — `function Comp({ name })` unwraps once and kills reactivity; keep the `props` object and read `props.name`. Same rule for control-flow callback bodies — read through JSX expressions.
- **Call accessors at the JSX boundary** — `<X value={count()} />`, not `<X value={count} />`; the child would receive a function, not a number.
- **`<For>` callback shape depends on keying mode** — default/identity: raw item + index accessor; `keyed={false}` (replaces `Index`): item accessor + stable number; custom key function: both accessors.
- **`class` is the only class prop** — `classList` is gone; use object/array form (`class={["card", { active: isActive() }]}`), not string concatenation.
- **Refs are callback functions** — no ref objects; compose with arrays (`ref={[a, b]}`); `use:` directives are gone — use two-phase ref directive factories.
- **`html` templates auto-wrap zero-arg functions as getters** — pass `${() => Counter}` if you genuinely want to hand over a zero-arg function as a value.
- **`html` returns a node or an array** — multi-root templates return an array; normalize before appending or spreading.
- **Async lives in computations** — `createMemo(() => fetchUser(id()))` + `<Loading>` replaces `createResource`; a bare `refresh()` is silent (`isPending` stays false) — declare `affects(x)` when a reload should read as pending.
- **Errors have one path** — async errors propagate through the graph to `<Errored>` (or an effect's `error` option); no inline `.error` branching.
- **Primitives need an owner** — wrap test code in `createRoot(dispose => { ... })` or effects leak; `createRoot` is owned by its parent by default, `runWithOwner(null, ...)` is the explicit detach.

## References

- [01-reactivity-core](references/01-reactivity-core.md) — Signals, writable memos, split effects, flush/batching, onSettled, ownership, escape hatches, dev diagnostics
- [02-stores](references/02-stores.md) — Draft-first stores, storePath, reconcile, shallow stores, snapshot/deep, projections, merge/omit
- [03-control-flow](references/03-control-flow.md) — For keying modes, Repeat, Show, Switch/Match, Loading, Errored, Reveal, Dynamic/dynamic, clientOnly, context
- [04-async-and-actions](references/04-async-and-actions.md) — Async in computations, isPending/latest/refresh/affects, transitions, actions, optimistic updates, createResource migration, ssrSource
- [05-dom](references/05-dom.md) — render/hydrate, refs and directive factories, attributes, class, event delegation, Portal
- [06-html-tagged-template](references/06-html-tagged-template.md) — The @solidjs/html `html` tagged template literal — full syntax, component registry, reactivity rules, differences from JSX
- [07-ssr-and-server-functions](references/07-ssr-and-server-functions.md) — SSR entry points, streaming, request events, httpStatus/httpHeader, cookies, "use server" functions, server components (experimental)
- [08-typescript-jsx-transform](references/08-typescript-jsx-transform.md) — jsxImportSource, renderer-owned JSX types, babel-preset-solid, @solidjs/h hyperscript, @solidjs/universal renderers
- [09-migration-from-1x](references/09-migration-from-1x.md) — 1.x to 2.0 rename/removal map with before/after examples

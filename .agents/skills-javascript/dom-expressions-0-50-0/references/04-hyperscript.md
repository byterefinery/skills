# `@dom-expressions/hyperscript`

`createHyperScript(runtime)` returns a hyperscript `h` bound to a DOM-expressions runtime (`import * as r from "dom-expressions/src/client"`; Solid re-exports a pre-wired `solid-js/h`). Target: fine-grained reactive libraries that want a **no-build** authoring syntax and interop with React-style ecosystems.

> **Performance note**: of the three frontends, hyperscript is the **slowest** — every `h(...)` materializes a small tree at runtime, versus precompiled cloned templates (babel-plugin-jsx) or parse-once-then-clone caching (tagged-jsx). If you just want a no-tooling authoring syntax, prefer tagged-jsx. Hyperscript's niche is interop with existing `h(tag, props, …children)` tooling and pure-JS DSLs.

## The `h` contract — laziness

Every `h(...)` call returns a **zero-arity thunk** tagged with an internal symbol; the thunk materializes DOM (or invokes the component) under the *current reactive owner* when called. Laziness is what keeps per-row render effects inside `For`/`mapArray` rooted under their own owners rather than the parent `insert` effect.

```js
const tree = h("div", h(Counter)); // thunk
tree();                            // materializes DOM

// Mount: render invokes the thunk inside its root
render(h(App), document.getElementById("app"));
```

Inside `h(...)` composition is ceremony-free: nested `h(...)` children are invoked once at consumption, and user-supplied accessors (`() => expr`) route through `r.insert` so they stay reactive.

## Components, props, children

- **Props are uniform.** Zero-arity function props route through `dynamicProperty` — reading them invokes the accessor and returns the current value (the getter convention Solid's JSX compiler emits). Function props with arity ≥ 1 (render-callbacks, `mapArray` row callbacks, `onClick: e => …`) are wrapped so nested `h(...)` thunks in their return values materialize at the call site — matching what JSX-compiled call sites store. This keeps `For`/`Index`/`Show` consumers from re-running stable row components on list mutations, and works for any third-party JSX-compiled component that re-invokes a callback prop with arguments. Arity (`cb.length`), `this`-binding, and identity are preserved; the wrap is idempomatic across nested components.

  **Footgun (events on components):** because zero-arity function props are wrapped as getters, `onClick: () => doStuff()` is *invoked at render time* and its `undefined` return becomes the prop — the click never fires. Take the unused argument to mark it 1-arity: `onClick: e => doStuff()`. Same for any component prop you want passed by reference.

- **`props.children` mirrors the caller's input:**

  | call shape | `props.children` |
  |---|---|
  | `h(Comp)` | `undefined` |
  | `h(Comp, { children: v })` | `v` |
  | `h(Comp, null, a)` | `a` |
  | `h(Comp, null, a, b, c)` | `[a, b, c]` |

  Nested `h(...)` thunks flow through as-is and auto-invoke once when consumed.

- **Reactive consumption is explicit.** `h("p", props.children)` reads once at render time. For reactive re-reads wrap in an accessor: `h("p", () => props.children)` — `r.insert` tracks the read and re-runs on change (mirrors JSX `{props.children}` → `insert(el, () => props.children)`).

- **Fragments** are plain arrays (`[h(...), h(...)]`) or `h.Fragment`.

- **JSX-compiler interop (one-way).** Components compiled by `@dom-expressions/babel-plugin-jsx` can be invoked from inside `h(...)` — they see the same props shape (getters for dynamic props, `children` as value/function/array). The reverse — passing a hyperscript thunk to compiled call sites expecting an element — is **not** supported.

## Tag selectors and differences from JSX

- Refs are a function prop: `ref: el => { … }`.
- Reactivity is explicit: wrap tracked expressions in `() => expr`, including when forwarding props.
- Fragments are arrays (or `h.Fragment`).
- Tag strings understand selectors: `h("div#main.sel", …)`.

## Example

```js
import { createHyperScript } from "@dom-expressions/hyperscript";
import * as r from "dom-expressions/src/client";
import { createSignal, mapArray } from "@solidjs/signals";

const h = createHyperScript(r);
const For = props => mapArray(() => props.each, props.children);

const App = () => {
  const [rows, setRows] = createSignal([{ id: 1, label: "one" }, { id: 2, label: "two" }]);
  return h(
    "table.table",
    h("tbody", h(For, { each: rows }, row =>
      h("tr", h("td.col-md-1", () => row().id), h("td.col-md-4", () => row().label))
    )
  );
};

r.render(h(App), document.getElementById("main"));
```

Compatible libraries: Solid, ko-jsx, mobx-jsx.

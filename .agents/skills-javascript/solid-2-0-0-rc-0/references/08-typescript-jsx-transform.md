# TypeScript, JSX ownership, and transforms

## Renderer-owned JSX

In 2.0, `solid-js` no longer owns a JSX namespace or `jsx-runtime` type entries. **Renderer packages own JSX types**; the core owns renderer-neutral component and child types.

Web apps:

```json
{
  "compilerOptions": {
    "jsx": "preserve",
    "jsxImportSource": "@solidjs/web"
  }
}
```

```ts
// 1.x / old beta
import type { JSX, ComponentProps } from "solid-js";

// 2.0 — renderer types come from @solidjs/web
import type { JSX, ComponentProps } from "@solidjs/web";

type ButtonProps = ComponentProps<"button">;
type ClickHandler = JSX.EventHandler<HTMLButtonElement, MouseEvent>;

// Renderer-neutral: use Element from solid-js instead of JSX.Element
import type { Component, Element, ParentComponent } from "solid-js";
type Wrapper = Component<{ children?: Element }>;
```

`@solidjs/web/jsx-runtime` and `@solidjs/web/jsx-dev-runtime` provide the TypeScript JSX namespace for web projects; `solid-js/jsx-runtime` / `solid-js/jsx-dev-runtime` are removed. The `JSXElement` alias is gone — use `Element`.

Hyperscript projects:

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "@solidjs/h"
  }
}
```

Custom renderers expose their own `./jsx-runtime` and `./jsx-dev-runtime` type entries and define their own `JSX` namespace (see the `@solidjs/universal` README template).

## babel-preset-solid

Compiles Solid's JSX into fine-grained DOM operations. For build-step projects, add it to the Babel config or — simpler — use `@solidjs/vite-plugin` (which wires the transform, `delegateEvents` emission, and SSR entries):

```js
// Vite
import solidPlugin from "@solidjs/vite-plugin";
export default defineConfig({ plugins: [solidPlugin({ solid: { /* options */ } })] });
```

For a custom renderer:

```js
// Babel: point at your renderer module and universal generation
{
  "presets": [
    ["babel-preset-solid", { "moduleName": "solid-custom-dom", "generate": "universal" }]
  ]
}
```

The compiler contract is small — it compiles JSX, emits `delegateEvents([...])` declarations, and (for server functions) performs the `"use server"` directive pass. It does not recognize framework wrappers.

## @solidjs/h — hyperscript

The `h()` factory for non-compiled environments (or standard-JSX-transform environments):

```js
import h from "@solidjs/h";

h("button", { title: "My button" }, "Click Me");
h(Button, { title: "My button" }, "Click Me");
h("div", { title: "x" }, h("span", "1"), h("span", "2")); // children as array or spread args
```

Caveats (same family as the `html` tag):

1. Reactive expressions must be manually wrapped — `h("div", { id: () => props.id }, () => firstName() + lastName())`.
2. Merging spreads requires `merge` to keep reactivity — `h("div", merge({ class: selectedClass }, props))`.
3. Events on components require an explicit event argument (zero-arg functions are auto-wrapped as getters).
4. Refs are callback form only — `ref: el => (myEl = el)`.
5. Shorthand static id/class — `h("div#some-id.my-class")`.
6. Fragments are just arrays — `[h("span", "1"), h("span", "2")]`.

`h(...)` returns a **tagged zero-arity thunk**, not a DOM node — pass a function reference (or `() => h(App)`) to `render(...)` so the thunk is invoked inside the root. Nested `h(...)` thunks auto-invoke when consumed, so composition with `<For>`/`<Show>` works without extra wrapping.

## @solidjs/universal — custom renderers

`createRenderer(impl)` returns a renderer bundle (`render`, `effect`, `memo`, `createComponent`, `createElement`, `createTextNode`, `insertNode`, `insert`, `spread`, `setProp`, `mergeProps`, `applyRef`, `ref`) for non-DOM targets (native, canvas/WebGL, terminal). You implement the platform methods (`createElement`, `setProperty`, `insertNode`, …), export the results as named exports from a referenceable module, forward `solid-js` control flow, and point the build at the module (`moduleName` + `generate: "universal"`).

Note: the universal `render` schedules the top-level mount through the effect queue and drains it with a tail `flush()` — uncaught top-level async holds the initial commit on the active transition and attaches atomically once it settles (same deferred-mount semantics as `@solidjs/web`).

## Web Components

`@solidjs/element` wraps Solid functions as custom elements (the 1.x `solid-element` lineage). Compose with `withSolid`/`customElement` from the package; the web runtime's shadow-root-scoped event delegation makes hosted Solid roots behave well inside elements.

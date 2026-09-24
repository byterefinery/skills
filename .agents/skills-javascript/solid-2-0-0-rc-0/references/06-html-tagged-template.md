# The `html` tagged template literal (@solidjs/html)

The build-less way to write Solid components. `@solidjs/html` (package `solid-html` in the repo) exports the `html` tag for use as a **replacement for JSX** in non-compiled environments. Since Solid 2.0 it is backed by [`@dom-expressions/tagged-jsx`](https://www.npmjs.com/package/@dom-expressions/tagged-jsx) — an AST-based tagged-template runtime: templates are **parsed at runtime** (no `new Function`/`eval`, so it is CSP-safe) and reactive bindings are installed against the resulting DOM.

Table of contents: [quick start](#quick-start) · [syntax](#elements--components) · [component registry](#component-registry) · [return shape](#return-shape) · [reactivity](#reactivity) · [attributes](#attributes--spread) · [events](#events) · [text, whitespace, raw nodes](#text-whitespace--raw-nodes) · [differences from JSX](#differences-from-jsx) · [performance](#performance)

## Quick start

```ts
import { render } from "@solidjs/web";
import html from "@solidjs/html";
import { createSignal } from "solid-js";

function Button(props) {
  return html`<button class="btn-primary" ...${props} />`;
}

function Counter() {
  const [count, setCount] = createSignal(0);
  const increment = (e) => setCount((c) => c + 1);

  // Inline component via expression hole; components close with <//>
  return html`<${Button} type="button" onClick=${increment}>${count}<//>`;
}

render(() => <Counter />, document.getElementById("app")!);
```

`html` is wired to the Solid web runtime automatically (`insert`, `spread`, `createComponent`, `mergeProps`, `claimElement`, and the SVG/MathML/Void/RawText element sets). Any signals library can drive tagged JSX by implementing the `Runtime` interface and calling `createTaggedJSXRuntime(runtime)` from `@dom-expressions/tagged-jsx`.

## Elements & components

```
html`<div />`;                  // self-closing
html`<div></div>`;              // matched
html`<${MyComponent} />`;       // inline component via expression hole
html`<${MyComponent}>...<//>`;  // shorthand close for inline components
html`<MyComponent />`;          // registered component (capitalized tag name)
```

- Tag names start with `a-zA-Z$_` and may contain `a-zA-Z0-9$.:-_`.
- **Capitalized** tag names are looked up in the component registry; an unregistered capitalized name **throws at template-construction time** (concrete failure for tooling/codemods to key off).
- **Lowercase** tag names are HTML/SVG/MathML elements; the namespace is inferred from the element name and walked into nested children.

## Component registry

Inline expression holes (`<${Component} />`) work with zero setup. The **named registry** registers capitalized tag names:

```ts
import html from "@solidjs/html";
import { For, Show } from "solid-js";

const tpl = html.define({ For, Show });

function List(props) {
  return tpl`
    <Show when=${() => props.items.length > 0} fallback=${tpl`<p>No items</p>`}>
      <ul>
        <For each=${() => props.items}>
          ${item => tpl`<li>${item.name}</li>`}
        </For>
      </ul>
    </Show>
  `;
}
```

- `tag.define(components)` returns a **new** tag with the components merged in; the original tag is unchanged. Registries compose: `base.define({ For }).define({ Show })`.
- `tag.components` exposes the current registry as a plain object.
- `tag.jsx` is a self-reference — writing `withForAndShow.jsx\`...\`` gives codemods, highlighters, and formatters a stable tag name to recognize regardless of the local variable name.

## Return shape

A template resolves to a **single node** when it has one root, and an **array of nodes** when it has many. Normalize before appending, spreading, or iterating:

```ts
const result = html`<span class="a"></span><span class="b"></span>`; // array
const nodes = Array.isArray(result) ? result : [result];
// or: const nodes = [result].flat();
```

Multiple top-level elements need no fragments — just write them.

## Reactivity

Because there is no compiler, the runtime uses a zero-arity heuristic. A **function passed to a non-event, non-`ref` attribute is auto-wrapped as a getter if it takes zero arguments**. Both forms are reactive and equivalent:

```ts
const [count] = createSignal(0);

html`<button count=${() => count()} />`;  // explicit wrap — always works
html`<button count=${count} />`;          // the getter itself; auto-wrapped
```

Text holes follow the same rule — `${count}` updates when count changes. Manual wrapping (`${() => ...}`) remains the explicit, self-documenting form.

**Opting out:** if the value you want to pass *is itself* a zero-arg function, wrap it again to break the heuristic:

```ts
html`<Route component=${() => Counter} />`;  // pass the function, don't call it
```

**`on*` and `ref` props are never auto-wrapped** — passed as-is.

## Attributes & spread

```ts
html`<input value="hi" />`            // static string attribute
html`<input disabled />`              // static boolean attribute
html`<input value=${val} />`          // dynamic — attribute or property, chosen automatically
html`<input prop:value=${val} />`     // forced DOM property
html`<input attr:foo=${val} />`       // forced HTML attribute
html`<input ...${props} />`           // spread
html`<input ref=${el => (myEl = el)} />` // ref — callback form only, not reactive
html`<input onClick=${handler} />`    // delegated event (camelCase)
html`<input onclick=${handler} />`    // bound listener (legacy lowercase)
```

`children` as an attribute is honored **only when the element has no template children** (matching JSX).

## Events

- DOM elements: camelCase `onClick=${handler}` uses the runtime's delegated event path when supported; lowercase `onclick=${handler}` binds a direct listener.
- **Components:** because component props auto-wrap zero-arg functions as getters, an event handler handed to a component must take an event argument:

```ts
// good — the handler has an argument, so it is passed through
html`<${Button} onClick=${(e) => console.log("Hi")} />`;

// bad — zero-arg, so it is auto-wrapped as a getter (never invoked as a handler)
html`<${Button} onClick=${() => console.log("Hi")} />`;
```

The same applies to render props like `<For>`'s child function.

## Text, whitespace, raw nodes

- Text content is **HTML-decoded** (`&copy;` → `©`, `&gt;` → `>`).
- Pure-whitespace runs **between elements** are dropped from the AST.
- Leading/trailing whitespace **inside an element** is dropped when the element contains at least one expression hole.
- When in doubt, use an expression: `` html`<p>${" exact spaces "}</p>` ``.
- `<!-- ... -->` comments are stripped.
- `<style>` and `<script>` bodies are **raw text** — no `innerHTML` workaround needed.
- `claimElement` hooks into the element-claim contract: static `href` anchors in templates reach claim consumers (router link-state integration).

## Differences from JSX

| Feature | Solid JSX | `html` tagged template |
|---|---|---|
| Fragments | Required: `<>...</>` for multiple roots | None needed — returns a node or array of nodes |
| Spread | `<div {...props} />` | `<div ...${props} />` |
| Comments | `{/* ... */}` | `<!-- ... -->` (stripped) |
| Raw-text tags | `innerHTML` workaround | `<style>`/`<script>` bodies are raw text |
| Whitespace | JSX-style stripping | Trims between tags; preserves inside text |
| Reactivity | Signals auto-wrapped by the compiler | Zero-arg functions auto-wrapped (use `() =>` to opt out) |
| Component refs | Identifier in scope | Registered name (`<Foo />`) or expression hole (`<${Foo} />`) |
| Refs | Identifier or callback | Callback form only (`ref=${el => ...}`) |

## Performance

`html` is slightly **less efficient than compiled JSX**: it requires a larger runtime that isn't treeshakeable, and it cannot leverage expression analysis — hence the manual wrapping and auto-wrap heuristics. In build-step projects prefer JSX; use `html` for no-build contexts, scripts, REPLs, or when the environment can't run a transform.

## Tooling

The [Tagged JSX Tools VS Code extension](https://marketplace.visualstudio.com/items?itemName=DanielRKling.tagged-jsx-vscode) provides syntax highlighting, formatting, JSX↔tagged-template conversion commands, and TypeScript diagnostics for JSX inside tagged template literals.

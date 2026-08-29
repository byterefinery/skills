# `@dom-expressions/tagged-jsx` — deep-dive

A fine-grained tagged-template JSX runtime. Parses JSX-shaped templates **at runtime** and installs reactive bindings against the resulting DOM. Any signals library can hook in by implementing the `Runtime` adapter.

## Wiring a runtime

```ts
import { createTaggedJSXRuntime, type Runtime } from "@dom-expressions/tagged-jsx";

// @solidjs/web's namespace exports satisfy Runtime
import * as web from "@solidjs/web";
const html = createTaggedJSXRuntime(web).define({ For, Show });
```

The `Runtime` interface (from `src/types.ts`):

```ts
interface Runtime {
  insert(parent: MountableElement, accessor: any, marker?: Node | null, init?: any): any;
  spread<T>(node: Element, accessor: (() => T) | T, skipChildren?: boolean): void;
  createComponent(Comp: (props: any) => any, props: any): any;
  mergeProps(...sources: unknown[]): any;
  claimElement<T extends Element>(node: T): T;
  SVGElements: Set<string>;
  MathMLElements: Set<string>;
  VoidElements: Set<string>;
  RawTextElements: Set<string>;
}
```

`claimElement` was added in this line: static `a[href]`/`form[action]` are baked into the cached `<template>`, so they never pass through the runtime `setAttribute` recheck that claims dynamically-written `href`/`action` — the tag stamps such nodes as claim targets while static props are still visible, and every clone is claimed at render. The contract is a no-op null check until a consumer registers a handler.

## API

- `createTaggedJSXRuntime(runtime): TaggedJSXInstance<{}>` — binds the runtime, empty registry.
- `tag.define(components): TaggedJSXInstance<Prev & New>` — **new** tag with merged registry; the original is immutable.
- `tag.jsx` — self-reference (`tag === tag.jsx`); gives codemods/highlighters/formatters a stable tag name.
- `tag.components` — the registry as a plain object.

## Parser and whitespace rules

Tokenization (`src/tokenize.ts`) and parsing (`src/parse.ts`):

- **Tag names** start with `a-zA-Z$_`, continue with `a-zA-Z0-9$.:-_`.
- **Components**: capitalized names or expression holes (`<${Comp} />`). Unregistered capitalized names throw at render (`Component "X" not found in registry`). Inline components can use the shorthand close `<${Comp}>…<//>`.
- **Namespace inference**: element type (HTML/SVG/MathML) is decided from the name against the runtime's element sets; `template` gets special treatment — its children are appended to `elem.content`.
- **Raw text**: `RawTextElements` (minus `template`) — `<style>`, `<script>`, `<textarea>` bodies are consumed raw with a case-insensitive closing-tag regex, never tokenized as JSX.
- **Whitespace**: pure-whitespace text nodes *between* tags are dropped from the AST; leading/trailing whitespace inside an element containing expression holes is dropped at the template build. Text is HTML-entity decoded (via `<template>` round-trip) — `&copy;` → `©`.
- **Void elements**: children of void elements are discarded on close.
- **Mismatched close** throws (`Mismatched closing tag for <div>`).
- **Spreads** `...${expr}` must be followed by an expression; non-object values throw at render (`Can only spread objects`).
- **Attribute forms**: `name` (boolean), `name="str"` (static), `name=${expr}` (expression), `prop:value=${expr}` (forced DOM property — kept out of template baking even without spread), `attr:foo=${expr}` (forced attribute).

## Template caching and baking

`getCachedRoot` caches the parsed `RootNode` in a `WeakMap` keyed by `TemplateStringsArray` — each unique literal is parsed exactly once. On first parse, `buildTemplate` bakes a real `<template>` element:

- Static props (and booleans) are `setAttribute`-ed onto the template DOM **at build time** — clones never pay for them at runtime, and `prop:`-prefixed or spread-following props are kept for runtime application (spread-overrides order is preserved).
- Expression holes and component nodes become comment placeholders; static text nodes are entity-decoded.
- Per render, `renderChildren` clones `template.content.firstChild` and walks it in sync with the AST using a `TreeWalker`: expression/component placeholders are replaced via `runtime.insert(parent, value, placeholder)`; elements get `runtime.spread(elem, props, true)` only when they have dynamic/spread props, and `runtime.claimElement(elem)` when stamped.

## Props and reactivity

`gatherProps` builds the props object; `applyGetter` is the reactivity heuristic:

```ts
if (typeof value === "function" && value.length === 0 && name !== "ref" && !name.startsWith("on")) {
  // define an enumerable getter -> reactive
} else {
  props[name] = value; // pass by value
}
```

- Zero-arg functions on non-event, non-`ref` props → **getter** (reactive). `count=${count}` and `count=${() => count()}` are equivalent.
- To pass a zero-arg function *by value*, double-wrap: `component=${() => Counter}`.
- `on*` and `ref` are always passed by value.
- Component `children`: when a component node has template children, `props.children` is a lazy getter that re-renders the children on access.
- `children` as an attribute on an element is honored only when the element has no template children (JSX parity).

## JSX vs `html` comparison

| Feature | Solid JSX | `html` tagged template |
|---|---|---|
| Fragments | `<>...</>` required | none needed — returns node or array |
| Spread | `<div {...props} />` | `<div ...${props} />` |
| Comments | `{/* … */}` | `<!-- … -->` (stripped) |
| Raw-text tags | `innerHTML` workaround | `<style>`/`<script>` bodies are raw |
| Whitespace | JSX-style stripping | trims between tags; preserves inside text |
| Reactivity | signals auto-wrapped | zero-arg functions auto-wrapped (opt out with `() =>`) |
| Component refs | identifier in scope | registered name (`<Foo />`) or expression (`<${Foo} />`) |

Because `html` returns a `JSX.Element` (node **or** array), normalize for iteration/spreading: `const nodes = [result].flat()`.

## Tooling

The [Tagged JSX Tools VS Code extension](https://marketplace.visualstudio.com/items?itemName=DanielRKling.tagged-jsx-vscode) provides syntax highlighting, formatting, conversion commands, and TypeScript diagnostics for JSX inside tagged template literals. It keys on the `html` tag name / `tag.jsx` self-reference — wrap/rename freely, keep `.jsx` for tooling.

## Source map

`src/tokenize.ts` (character-level tokenizer with raw-text and comment handling) → `src/parse.ts` (token → AST with element/component/text/expression/spread node types) → `src/tagged-jsx.ts` (baking, caching, render walk) · `src/types.ts` (public types).

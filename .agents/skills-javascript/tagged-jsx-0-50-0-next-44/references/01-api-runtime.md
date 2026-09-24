# API and `Runtime` adapter

Public surface of `@dom-expressions/tagged-jsx@0.50.0-next.44` (all exports from the single entry point):

- `createTaggedJSXRuntime(runtime: Runtime): TaggedJSXInstance<{}>` — the only value export.
- Types: `TaggedJSXInstance<T>`, `Runtime`, `ComponentRegistry`, `FunctionComponent`.

## Package metadata

| Field | Value |
|---|---|
| Install | `npm install @dom-expressions/tagged-jsx` |
| Latest published | `0.50.0-next.44` (the `next` dist-tag lags at next.42 — pin explicitly) |
| Module format | ESM only — `exports["."]` maps `import` → `dist/index.mjs`, `types` → `dist/index.d.mts`; no `require`/CJS |
| Dependencies | **zero** runtime dependencies (dev-only: vitest, jsdom, tsdown, `@dom-expressions/runtime`) |
| `sideEffects` | `false` — bundlers can tree-shake unused exports |
| Types | Self-contained — `csstype` is inlined into `dist/index.d.mts`, so consumers never resolve a transitive JSX-type dependency |
| License / author | MIT / Daniel Kling |
| Source | `packages/tagged-jsx` in ryansolid/dom-expressions (published from the `next` branch) |

## `createTaggedJSXRuntime(runtime)`

Binds the runtime once and returns a tag with an **empty** component registry. Binding is where `document` is first required (a `TreeWalker` and a scratch `<template>` element are created). Returns `TaggedJSXInstance<{}>`.

```ts
import { createTaggedJSXRuntime } from "@dom-expressions/tagged-jsx";
import * as web from "@solidjs/web";
const html = createTaggedJSXRuntime(web);
```

## `TaggedJSXInstance<T>` — the tag

```ts
type TaggedJSXInstance<T extends ComponentRegistry> = {
  (strings: TemplateStringsArray, ...values: any[]): JSX.Element; // the tag call
  jsx: TaggedJSXInstance<T>;        // self-reference (tag === tag.jsx)
  define<TNew extends ComponentRegistry>(components: TNew): TaggedJSXInstance<T & TNew>;
  components: T;                    // the registry, as a plain object
};
```

- **Tag call** — parses (or fetches the cached AST for) the literal, clones the baked template, binds the holes, and returns real DOM: a single node for one root, an array for several, `[]` for empty templates. `JSX.Element` here is deliberately the scalar-or-array union.
- **`.define(components)`** — returns a **new** tag with `{ ...oldRegistry, ...newComponents }`; the original tag is unchanged. Newer keys override older ones.

  ```ts
  const base = createTaggedJSXRuntime(web);
  const withFor = base.define({ For });
  const withForAndShow = withFor.define({ Show });
  base.components;            // {}
  withForAndShow.components;  // { For, Show }
  ```
- **`.jsx`** — `tag.jsx === tag`. A stable tag name for codemods, highlighters, formatters, and TS tooling: name the local anything, call through `.jsx` if tooling needs a fixed anchor.
- **`.components`** — inspect the registry as a plain object.

## `Runtime` adapter contract

```ts
type MountableElement = Element | Document | ShadowRoot | DocumentFragment | Node;

interface Runtime {
  insert(parent: MountableElement, accessor: any, marker?: Node | null, init?: any): any;
  spread<T>(node: Element, accessor: (() => T) | T, skipChildren?: boolean): void;
  createComponent(Comp: (props: any) => any, props: any): any;
  mergeProps(...sources: unknown[]): any;
  claimElement<T extends Element>(node: T): T;   // required since 0.50.0-next.25
  SVGElements: Set<string>;
  MathMLElements: Set<string>;
  VoidElements: Set<string>;
  RawTextElements: Set<string>;
}
```

The exported `Runtime` type is the extension point: any signals library can be wired by implementing this shape against its own primitives.

| Member | How the tag uses it |
|---|---|
| `insert(parent, accessor, marker, init?)` | Replaces each `<!--+-->` expression placeholder and `<!--Name-->` component placeholder: the tag calls `r.insert(placeholder.parentNode, value, placeholder)` per hole, where `value` is the raw expression value (usually a signal/accessor) or the rendered component. |
| `spread(node, accessor, skipChildren?)` | Applies the gathered props object to an element. The tag always passes `skipChildren: true` because template children are walked separately. The runtime decides attribute-vs-property-vs-event and honors `prop:`/`attr:`-prefixed names and delegated `on*` events. |
| `createComponent(Comp, props)` | Instantiates a component (registry lookup or dynamic `<${Comp}>`). Typically `untrack(() => Comp(props))` in signals cores. `props.children` is a lazy getter when the component has template children. |
| `mergeProps(...sources)` | Merges the tag's own props with each `...${spread}` object in source order (later wins). |
| `claimElement(node)` | Element-claim contract (below). A no-op null check in the runtime until a consumer registers a handler via `registerElementClaim`. |
| `SVGElements` / `MathMLElements` | Element-name sets used to pick `createElementNS` vs `createElement` — namespace is inferred from the name, not the parent. |
| `VoidElements` | Names whose children are discarded at parse time on close. |
| `RawTextElements` | Names whose body is consumed raw. The tag **removes `template` from this set** before use, so `<template>` children are parsed as JSX and appended to `.content` (runtime default set: `style, script, noscript, template, textarea, title`). |

### `@solidjs/web` satisfies the shape

`import * as web from "@solidjs/web"` provides every member: `insert`, `spread`, `createComponent`, `mergeProps` (Solid's `merge`), the four element sets, and `claimElement` in versions current with this line. The repo's test core does the same wiring against `@dom-expressions/runtime`'s client entry plus `@solidjs/signals`:

```ts
// tests/core.ts (abridged) — the shape a custom core takes
import * as signals from "@solidjs/signals";
export const sharedConfig = {};
export function createComponent(Comp: any, props: any) {
  return signals.untrack(() => Comp(props)); // + class-component branch in the real file
}
export {
  createRoot as root, createRenderEffect as effect, createMemo as memo,
  getOwner, runWithOwner, untrack, merge as mergeProps, flatten, flush
} from "@solidjs/signals";
export { RawTextElements, VoidElements } from "../../runtime/src/constants";
// runtime client entry supplies insert/spread/claimElement + SVG/MathML sets
```

### Custom cores (Preact Signals, ko-signals, …)

Implement the eight members against the target core's primitives. The four element sets are data — reuse `@dom-expressions/runtime`'s constants or any equivalent list. If the core's web module predates 0.50.0-next.25 and lacks `claimElement`, shim it:

```ts
const html = createTaggedJSXRuntime({ ...web, claimElement: (el) => el });
```

## The element-claim contract (`a[href]` / `form[action]`)

Added in **0.50.0-next.25** (the only tagged-jsx source change between next.15 and next.44). The runtime uses *element claims* to track anchor/form navigation targets. Dynamic `href`/`action` writes are claimed by the runtime's `setAttribute` recheck. The gap this closes: **static** `href`/`action` are baked into the cached `<template>` at build time, so they never pass through that runtime recheck. The tag therefore:

1. Stamps `node.claim = true` at bake time when a static or boolean `a[href]` / `form[action]` prop is about to be baked (only when no spread precedes it — spread-carried attributes still flow through the runtime recheck).
2. Calls `r.claimElement(element)` for every clone of a stamped template at render.

Observable behavior (from the package's tests):

- `html`<a href="/about">About</a>` → the anchor is claimed once, at render, even though the href is static.
- `html`<a href=${href}>…` → claimed on the initial attribute write; **re-claimed on every href change** (the recheck fires again).
- `<a name="anchor">` without `href`, and non-claim elements, are never claimed.
- Each clone of a cached template is claimed independently — calling the same literal twice yields two distinct, independently claimed elements.

## Tooling

The [Tagged JSX Tools VS Code extension](https://marketplace.visualstudio.com/items?itemName=DanielRKling.tagged-jsx-vscode) provides syntax highlighting, formatting, conversion commands, and TypeScript diagnostics for JSX inside tagged template literals. It keys on the tag name — keep the variable named `html`, or route calls through the `.jsx` self-reference for a stable anchor after renames/wraps.

## Source map (package ships full `src/`)

- `src/index.ts` — the two-line export surface above.
- `src/types.ts` — `Runtime`, `TaggedJSXInstance`, `ComponentRegistry`, `FunctionComponent`.
- `src/tokenize.ts` — character-level tokenizer (tags, attributes, strings, raw text, comments, expression holes).
- `src/parse.ts` — token stream → AST (element/component/text/expression nodes; static/boolean/expression/spread props).
- `src/tagged-jsx.ts` — template baking, `WeakMap` caching, clone+`TreeWalker` render walk, props gathering, reactivity heuristic.
- `tests/` — vitest + jsdom integration tests against the runtime client entry (1800+ lines; excellent behavioral oracle).

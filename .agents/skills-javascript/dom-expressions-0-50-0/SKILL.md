---
name: dom-expressions-0-50-0
description: dom-expressions 0.50.0 (published prerelease 0.50.0-next.44) — fine-grained reactive DOM rendering runtime for signals libraries. Covers the four published packages — runtime (dom-expressions, client/ssr/universal entry points), babel-plugin-jsx (Babel JSX compiler), compiler (experimental AST-native Oxc/Rust compiler), tagged-jsx (runtime-parsed JSX via tagged template literals), hyperscript (lazy h() DSL) — plus the Solid 2.x server components / frame-streams architecture (docs/). Use when authoring or debugging fine-grained reactive UI libraries built on dom-expressions, configuring its JSX compilers, working with Solid 2 / SolidStart-style SSR and hydration, or understanding frame streams, server components, and behavior claims.
license: MIT
compatibility: Node.js with pnpm for the monorepo; @dom-expressions/compiler ships per-platform native bindings plus a WASI fallback. Requires a reactive core (e.g. @solidjs/signals) via the rxcore rename-import mechanism.
metadata:
  tags:
    - javascript
    - frontend
    - reactive
    - signals
    - jsx
    - dom
    - ssr
    - solid
---

# dom-expressions 0.50.0

## Overview

dom-expressions is a rendering runtime for fine-grained reactive libraries. Instead of a Virtual DOM and lifecycle, it renders pure DOM expressions and lets the reactive core (signals, memos, effects) manage updates. It is the render backend of Solid 2.x, and it powers ko-jsx, mobx-jsx, and s-jsx.

This skill covers the `next` line: **0.50.0 targeting Solid 2.x**, currently published in prerelease as **0.50.0-next.44**. All four published packages are version-locked in lockstep via Changesets `fixed` groups:

- **`dom-expressions`** (packages/runtime) — the runtime itself: client (`dom-expressions/src/client`), server (`src/server`), and universal (`src/universal`) entry points.
- **`@dom-expressions/babel-plugin-jsx`** — the mature JSX→DOM Babel compiler.
- **`@dom-expressions/compiler`** — experimental AST-native Oxc/Rust compiler (23–355x faster than Babel).
- **`@dom-expressions/tagged-jsx`** — JSX-in-tagged-templates runtime API (no build step).
- **`@dom-expressions/hyperscript`** — lazy `h(...)` DSL (lowest performance, highest interop flexibility).

Version ranges (see repo `VERSIONING.md`): `0.40.x` is the Solid 1.x maintenance line; `0.41.0`–`0.49.x` is **reserved** and must not be published; `0.50.0+` is active development for Solid 2.x; `1.0.0` is deferred until the runtime contract (including Server Components / Resumability) is semver-stable. During the prerelease window every changeset must be `patch`.

## Packages

### Runtime (`dom-expressions`)

Most developers never import it directly — the reactive library re-exports a generated runtime. The runtime core is injected via `babel-plugin-transform-rename-import` mapping the virtual module `rxcore` to your reactive core (which exports `root`, `effect`, `memo`, `untrack`, `getOwner`, `createComponent`, `mergeProps`, and optionally the `waitAsset`, `driveList`, `patchableRaw`, `registerPatch` seams — optional seams degrade gracefully when absent).

Client entry (`dom-expressions/src/client`) key APIs: `render`, `hydrate`, `template`, `insert`, `assign`, `spread`, `delegateEvents`, `registerDelegatedRoot/Container`, `setAttribute`, `className`, `style`, `addEvent`, `ref`/`applyRef`, `dynamicProperty`, `getHydrationKey`, `useHead`, `acquireAsset`/`warmAsset`, `registerElementClaim`/`claimElement`/`claimElementTree`, `rowProof`, `patchDriver`, plus the element-set constants (`DOMElements`, `SVGElements`, `MathMLElements`, `VoidElements`, `RawTextElements`, `Namespaces`, `DelegatedEvents`).

Server entry (`dom-expressions/src/server`): `renderToString`, `renderToStream`, `HydrationScript`, `generateHydrationScript`, `useHead`, `createSSRResponse`, `getRequestEvent`, `createRequestEvent`, `commitEventResponse`, `ssrGroup`, `createLiveHoles`, `composeMiddleware`, `ssr`/`ssrElement`/`ssrAttribute`/`ssrClassName`/`ssrStyle`, `getExpectedRedirectStatus`, `scriptNonce`/`styleNonce`.

Universal entry (`dom-expressions/src/universal`): `createRenderer(...)` — builds a renderer bound to any node backend (createElement/insertNode/setProperty/… primitives), used by `generate: "universal"` and `"dynamic"` compilation.

### Tagged JSX (`@dom-expressions/tagged-jsx`) — the focus

A tagged-template runtime that parses JSX-shaped templates at runtime and installs reactive bindings against the resulting DOM. Any signals library can hook in by implementing the `Runtime` adapter interface:

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

(`@solidjs/web` exports satisfy this shape; `import * as web from "@solidjs/web"` is the standard wiring.)

Core API:

- `createTaggedJSXRuntime(runtime)` — returns a tag with an empty component registry.
- `tag.define({ For, Show })` — returns a **new** tag with merged registry; the original tag is immutable.
- `tag.jsx` — self-reference (`tag === tag.jsx`), giving codemods/highlighters a stable tag name.
- `tag.components` — the registry as a plain object.

Templates:

```ts
const html = createTaggedJSXRuntime(web).define({ For, Show });

const Counter = () => {
  const [count, setCount] = createSignal(0);
  return html`
    <button onClick=${() => setCount(c => c + 1)}>Count: ${count}</button>
    <For each=${list()}><li>…</li></For>
  `;
};
```

Syntax rules (from `packages/tagged-jsx/src/parse.ts` + README):

- **Components**: capitalized tag names are looked up in the registry; unregistered capitalized names **throw**. Inline components use expression holes: `<${MyComponent} />` and shorthand close `<${MyComponent}>…<//>`.
- **Elements**: lowercase names, namespace (SVG/MathML/HTML) inferred from name and walked into nested children. Tag names start with `a-zA-Z$_`, contain `a-zA-Z0-9$.:-_`.
- **Attributes**: static strings, boolean (bare) props, expression props `=${val}`, forced DOM property `prop:value=${val}`, forced attribute `attr:foo=${val}`, spread `...${props}` (must be an object — throws otherwise), `ref=${fn}` (never reactive), camelCase `onClick=${h}` (delegated when the runtime supports it) and legacy lowercase `onclick=${h}` (bound listener).
- **Whitespace**: pure-whitespace runs between elements are dropped; leading/trailing whitespace inside an element is dropped when it contains at least one expression hole; text is HTML-decoded (`&copy;` → `©`).
- **Raw-text tags**: `<style>`/`<script>`/`<textarea>` bodies are raw text (never tokenized as JSX).
- **Reactivity**: zero-arity functions passed to non-event, non-`ref` attributes are auto-wrapped as getters; `on*` and `ref` are never wrapped. To pass a zero-arg function by value, double-wrap: `component=${() => Counter}`.
- **`children`**: honored as an attribute only when the element has no template children; on component nodes it becomes a lazy getter that re-renders on access.
- **Multiple roots**: `html` returns a single node or an array — normalize with `[result].flat()`.

Internals: templates are tokenized/parsed once per `TemplateStringsArray` (cached in a `WeakMap`), baked into a `<template>` element (static attributes set at build so they skip runtime `setAttribute`), then cloned per render and walked in sync with the AST via `TreeWalker`. Expressions and components become comment placeholders replaced through `runtime.insert`.

### Babel Plugin (`@dom-expressions/babel-plugin-jsx`)

The production workhorse. Pre-compiles JSX into `template(html, flag)` + `cloneNode(true)` + minimal traversal + `insert`/`effect`/`className` calls; delegates camelCase events via `delegateEvents(["click"])`. Details (all plugin options, special bindings, compile output anatomy) in [02-babel-plugin-jsx](references/02-babel-plugin-jsx.md).

### Compiler (`@dom-expressions/compiler`)

Experimental AST-native Oxc/Rust implementation of the same transform — parse once, mutate the AST, codegen once. Exposes `transform(source, options)` / `transformAsync(...)` / `transformDirectives(code, options)` (the `"use server"` directive pass, interoperable with SolidStart's Babel manifest format via `xxhash32(path)-count` IDs). Adds `generate: "universal"` and `"dynamic"` (universal fallback + per-tag DOM routing) beyond Babel's `dom`/`ssr`. Defaults `contextToCustomElements: true` to match Solid. It is a backend API, **not** a Vite/Rollup/Babel plugin. Details in [03-compiler](references/03-compiler.md).

### HyperScript (`@dom-expressions/hyperscript`)

`createHyperScript(runtime)` returns a **lazy** `h(...)` — every call returns a zero-arity thunk that materializes DOM (or invokes the component) under the current reactive owner. Mount with `r.render(h(App), el)`. The slowest frontend of the three (no parse-once caching, no precompiled templates); its niche is interop with React-style transforms and pure-JS DSLs. Zero-arity function props are wrapped as getters — so `onClick: () => doStuff()` on a component is invoked at render and the click never fires; write `onClick: e => doStuff()`. Details in [04-hyperscript](references/04-hyperscript.md).

## Server Components and Frame Streams

The `next` line is where Solid 2.x server components live. The architecture (repo `docs/server-components.md`):

- **A server component is a function returned from a `"use server"` function.** The server function's *arguments* are the server inputs (drive fetching); the returned component's *props* are **client positions** — holes the client fills — and never travel to the server.
- **Props are positions, not data.** `{props.children}` emits a marked range in HTML; the client decides what lives there and it survives every server update.
- **A boundary is a call.** Server content renders into a frame addressed by the call that produced it (function + args, like a query-cache key). Re-fetching the same call *morphs* in place — client state inside (focus, inputs, video) survives; different args are a different boundary.
- **`$key`** names an occurrence by entity for live reordering lists — only meaningful on slot calls (`<props.comment $key={c.id}>`), and keyed occurrences must be siblings.
- The wire format is **frame streams** (docs: `frame-streams-rfc.md`, `frame-seams-decision.md`): the client claims server markup by `pl-` markers, streams async holes as raw seroval streams (buffered values replay synchronously to keep the synchronous hydration claim walk correct), and "behavior claims" (`_bnd` markers) wire refs and delegated events onto morphed subtrees.

Details in [06-server-components](references/06-server-components.md).

## Gotchas

- **`next` ≠ stable**: 0.50.0-next.* is prerelease; the Rust compiler API is explicitly unstable pre-1.0 (pin exact revisions when embedding). The Node `transform()` contract is the supported interface.
- **Never publish into 0.41–0.49** — reserved for the Solid 1.x maintenance line.
- **`html` throws on unregistered components** — every capitalized tag must be in the `.define({...})` chain (or an expression hole). Registry is immutable per tag; `define` returns a new tag.
- **`...${props}` must be an object** — tagged-jsx throws "Can only spread objects" on non-objects.
- **Zero-arg function props are getters, not values** — in tagged-jsx and hyperscript alike. Event handlers written `onClick: () => doStuff()` fire at render time, not on click; take the argument: `e => doStuff()`.
- **`ref` and `on*` are never auto-wrapped** in tagged-jsx; everything else zero-arg is.
- **Static attributes baked into the `<template>` bypass runtime `setAttribute`** — including the `a[href]`/`form[action]` behavior-claim recheck, which is why tagged-jsx stamps claim targets at build time and claims clones via `claimElement`.
- **Whitespace is aggressive** in tagged-jsx — text between elements that is pure whitespace vanishes; use `${" exact  spaces "}` when literal spacing matters.
- **Multiple roots return an array** — `html` tags are `JSX.Element` (node or array); normalize with `[result].flat()` before spreading or iterating.
- **Hyperscript `h` is a thunk** — passing the raw tree without calling it (or via `r.render`, which invokes it in its root) means nothing renders; and a hyperscript thunk cannot be passed to a compiled JSX call site expecting an element (interop is one-way).
- **Babel vs Rust compiler parity is tracked but not complete** — the Rust compiler intentionally *rejects* unsupported input (e.g. DOM `namespaceElements` the Oxc parser chokes on, unknown namespaced attributes outside `xlink`) instead of silently miscompiling.
- **SSR escaping**: `innerHTML`-style inserts bypass dom-expressions' automatic escaping; `<noscript>` contents are outside its purview entirely — sanitize there and keep a strict CSP.
- **`children` attribute vs template children** — honored only when the element has no template children (matches JSX semantics); component `props.children` is a lazy getter, not a value.

## References

- [01-runtime](references/01-runtime.md) — rxcore contract, client/server/universal entry points, render/hydrate, insert semantics, event delegation, head and asset management, behavior claims
- [02-babel-plugin-jsx](references/02-babel-plugin-jsx.md) — full option reference, compile-output anatomy, special bindings (ref, events, spreads), components and fragments
- [03-compiler](references/03-compiler.md) — @dom-expressions/compiler transform API, native/WASI bindings, generate modes, source maps, `"use server"` directives, performance
- [04-hyperscript](references/04-hyperscript.md) — the `h` contract, props/children rules, event footgun, JSX-compiler interop, tag selectors
- [05-tagged-jsx](references/05-tagged-jsx.md) — Runtime adapter deep-dive, parser/whitespace/attribute rules, caching and template-baking internals, JSX-vs-html comparison
- [06-server-components](references/06-server-components.md) — frame streams, boundaries as calls, `$key`, hydration and live holes, behavior claims, SSR response utilities

---
name: tagged-jsx-0-50-0-next-44
description: "@dom-expressions/tagged-jsx 0.50.0-next.44 (latest) — fine-grained reactive JSX runtime written as tagged template literals for signals libraries, from the dom-expressions 0.50.0-next line. No build step and no runtime code generation (CSP-safe); parses JSX-shaped templates at runtime, bakes static markup into cached template elements, and binds expression holes through a pluggable Runtime adapter (@solidjs/web satisfies it). Covers the tag API (createTaggedJSXRuntime, define, jsx self-reference, components), full template syntax (spreads, prop/attr namespaced attributes, raw-text style/script/noscript/textarea/title bodies, line and block comments in tags, shorthand close for dynamic components, whitespace and entity-decoding rules), zero-arg-function getter reactivity, scalar-or-array return values, and the anchor-href / form-action element-claim contract. Use when writing reactive DOM UI without a JSX transform, wiring any signals library to tagged-template markup, or debugging parsed template output."
license: MIT
compatibility: Browser or DOM environment required — createTaggedJSXRuntime and every tag call touch document, though the module import itself is DOM-agnostic. ESM only (single import export, no CJS). Zero runtime dependencies. No SSR entry point.
metadata:
  tags:
    - javascript
    - frontend
    - reactive
    - signals
    - jsx
    - tagged-templates
    - dom
    - solid
    - dom-expressions
---

# tagged-jsx-0-50-0-next-44

## Overview

`@dom-expressions/tagged-jsx` (version **0.50.0-next.44**, the latest published version) is the no-build-step member of the dom-expressions 0.50.0-next line. It renders JSX-shaped markup through a **tagged template literal** — `` html`<div>Hi ${name}</div>` `` — for any fine-grained reactive signals library:

- **No build step, no code generation** — templates are parsed at runtime into an AST, static markup is baked once into a cached `<template>` element, and later calls re-render by cloning that template and binding only the expression holes. No `new Function`/eval, so it is CSP-safe. It supersedes the old `lit-dom-expressions` package, which compiled templates into code strings at runtime.
- **Any signals library** — the package has zero runtime dependencies; the reactive core is injected through a `Runtime` adapter interface. `@solidjs/web`'s namespace exports satisfy it out of the box; `createTaggedJSXRuntime` also accepts a hand-rolled adapter (Preact Signals, etc.).
- **One call site, one cache** — parsed AST + baked template are cached in a `WeakMap` keyed by the literal's `TemplateStringsArray`, so repeated calls with the same template literal parse and bake exactly once.
- **Client only** — `createTaggedJSXRuntime` and tag calls require `document`. There is no SSR entry; server rendering belongs to the `dom-expressions` runtime and its Babel compiler.

Positioning in the line (all packages version-locked at 0.50.0-next.44): the `dom-expressions` runtime is the backend; `@dom-expressions/babel-plugin-jsx` and `@dom-expressions/compiler` are the compile-time JSX paths; `@dom-expressions/hyperscript` is the lazy `h()` path. **tagged-jsx is the runtime-parsed path** — largest in size/memory, but the only one that needs no transform. The sibling skill `dom-expressions-0-50-0` covers the runtime, compilers, and hyperscript; this skill goes deep on this package.

## Usage

### Wiring

```ts
import { createTaggedJSXRuntime } from "@dom-expressions/tagged-jsx";
import * as web from "@solidjs/web"; // namespace exports satisfy Runtime
import { For, Show, createSignal } from "solid-js";
import { render } from "@solidjs/web";

// Bind the runtime once; register components for PascalCase tag names.
const html = createTaggedJSXRuntime(web).define({ For, Show });

function Counter() {
  const [count, setCount] = createSignal(0);
  return html`
    <button onClick=${() => setCount(c => c + 1)}>Count: ${count}</button>
  `;
}

render(Counter, document.body);
```

Call the tag inside a reactive owner (component body or `createRoot`) so the runtime's `insert`/`spread` track signals. The tag call is **eager** — it returns real DOM, not a render function.

### Return value — scalar or array

The tag returns a **single node** when the template resolves to one root, an **array** of nodes when it resolves to several, `[]` for an empty template, and a plain string for whitespace-only templates. Normalize before iterating:

```ts
const nodes = [result].flat(); // always an array of nodes
```

### Template quick reference

- **Elements** — `` html`<div class="a">Hi ${name}</div>` ``; self-closing `/>` and matched closing tags both work; tag names start with `a-zA-Z$_` and continue with `a-zA-Z0-9$.:-_` (custom elements with dashes, dots, colons work). SVG/MathML namespaces are inferred from the element name.
- **Components** — capitalized names are looked up in the registry set via `.define({ ... })`; an unregistered name throws at render. Inline dynamic components use an expression hole: `` html`<${Comp} />` ``, closed with a matching `` </${Comp}> `` or the shorthand `<//>` (dynamic components only).
- **Attributes** — `name="static"` (string, either quote), `name` (boolean), `name=${expr}` (dynamic), `...${props}` (spread, objects only), `prop:value=${expr}` (force DOM property), `attr:foo=${expr}` (force attribute). Later attributes override earlier ones, including across spreads.
- **Raw text** — `style`, `script`, `noscript`, `textarea`, `title` bodies are consumed raw (no JSX parsed inside); `template` is parsed normally and its children land in `.content`.
- **Comments** — `<!-- … -->` in text, plus `//` line and `/* … */` block comments **inside tag blocks**; all stripped. Expressions inside HTML comments are dead code (never evaluated).
- **Whitespace** — pure-whitespace runs between tags are dropped; spaces inside a text run are preserved. Text is HTML-entity decoded (`&copy;` → `©`). When exact spacing matters, pass it as an expression.
- **Reactivity** — a zero-argument function on a non-`on*`, non-`ref` attribute is auto-wrapped into a reactive getter: `x=${fn}` and `x=${() => fn()}` are equivalent. Double-wrap (`x=${() => fn}`) to pass a zero-arg function by value. `on*` and `ref` are always passed by value.
- **Events / refs** — `onClick=${handler}` (delegated when the runtime supports it), `onclick=${handler}` (direct listener), `ref=${fn}` (not reactive).

### Tooling

The [Tagged JSX Tools VS Code extension](https://marketplace.visualstudio.com/items?itemName=DanielRKling.tagged-jsx-vscode) provides syntax highlighting, formatting, conversion commands, and TypeScript diagnostics for JSX inside tagged template literals. It keys on the tag name — name the tag `html` (the default tooling configuration) or use the `tag.jsx` self-reference (`` tag.jsx`...` `` gives tooling a stable name no matter what the local variable is called).

## Gotchas

- **The shorthand `<//>` closes only dynamic components** — `` html`<${Comp}>…<//>` `` works; `html`<RegisteredComp>…<//>` `` throws "Mismatched closing tag". A `//` that is not immediately followed by `>` (ignoring whitespace) is a **line comment** inside a tag block, not a close.
- **`claimElement` is required in `Runtime`** — added in 0.50.0-next.25 as part of the anchor-href / form-action claim contract. The published README's `Runtime` interface **omits it** — trust `src/types.ts` over the README. Adapters predating next.25 (e.g. an older `@solidjs/web`) can shim it: `{ ...web, claimElement: (el) => el }`.
- **No SSR** — importing the module in Node is safe, but `createTaggedJSXRuntime` reads `document` at bind time, so server-side rendering throws. Use the Babel-compiler / runtime SSR entries for server output.
- **The tag is eager, and the result is scalar-or-array** — the DOM is built at call time; reactivity comes from tracking in the surrounding owner, not from a returned function. Iterate with `[result].flat()`.
- **`.define` is immutable** — `tag.define({ X })` returns a **new** tag with the merged registry; the original keeps its old registry. Newer registrations override same-named older ones.
- **Spread must be an object** — `...${42}` throws "Can only spread objects" at render; `...` not followed by an expression is a parse error. Override order is source order across statics and spreads.
- **Void elements swallow children** — `<input>x</input>` parses, but the children are discarded when the void element closes.
- **Component `children` is overridden** — when a component node has template children, `props.children` becomes a lazy getter and silently replaces any `children` value passed in the same tag. On elements, a `children` attribute is honored only when the element has no template children.
- **`<${expr}>` must resolve to a function** — a dynamic tag name whose value is not a function throws "not found in registry" at render, same message as an unregistered capitalized name.
- **Install pin** — the `next` dist-tag on npm lags (points at next.42); `0.50.0-next.44` is the latest published. Pin the explicit version, and note the repo's only git tag is `@dom-expressions/tagged-jsx@0.50.0-next.15` — later versions publish from the `next` branch without tags.
- **Whitespace-only templates return a string, not a node** — `` html`   ` `` returns the literal `"   "` string scalar. Spreading it (`...[result].flat()`) explodes into individual characters; guard or avoid templates that may render to whitespace only.
- **Whitespace is not JSX whitespace** — only pure-whitespace *runs* between tags are dropped; the space in `<i> ${name}</i>` survives only because it trails a non-whitespace text run. Do not depend on indentation surviving.

## References

- [01-api-runtime](references/01-api-runtime.md) — full API surface, the `Runtime` adapter contract, Solid and custom-core wiring, the element-claim contract, package metadata
- [02-template-syntax](references/02-template-syntax.md) — complete template syntax: elements, components, attributes, spreads, comments, raw text, namespaces, whitespace, entities, error messages
- [03-internals](references/03-internals.md) — tokenize → parse → bake → cache → clone/walk pipeline, reactivity heuristic, return-value semantics, performance and CSP notes
- [04-version-history](references/04-version-history.md) — package lineage (`sld-dom-expressions` → `@dom-expressions/tagged-jsx`), per-release changesets through 0.50.0-next.44, repo/tag provenance

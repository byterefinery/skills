# Internals

How a tagged-template call becomes DOM, per `src/tokenize.ts` → `src/parse.ts` → `src/tagged-jsx.ts`. Understanding this explains the caching, the whitespace rules, and where each error comes from.

## Pipeline

```
tag(strings, ...values)
  └─ getCachedRoot(strings)                 # WeakMap keyed by TemplateStringsArray
       ├─ tokenize(strings, rawTextElements) # flat token stream, holes as EXPRESSION_TOKEN
       ├─ parse(tokens, voidElements)        # AST: root → element/component/text/expression nodes
       └─ buildTemplate(root)                # bakes <template> elements + stamps claims (once)
  └─ renderChildren(root, values, components)
       ├─ clone template.content.firstChild (cloneNode(true))   # per top-level element / component child
       ├─ TreeWalker (SHOW_ELEMENT|SHOW_COMMENT, 129) walks clone in sync with AST
       │    ├─ expression/component hole → r.insert(parent, value, markerComment)
       │    ├─ element with surviving props → r.spread(el, props, true)
       │    └─ stamped element → r.claimElement(el)
       └─ flat(children)                     # 1 → scalar, n → array, 0 → []
```

### Tokenize (`src/tokenize.ts`)

Character-level state machine over each string chunk, five states:

- **TEXT** — scans to the next `<`; `<!--` switches to COMMENT; else emits `OPEN_TAG_TOKEN` and enters TAG.
- **TAG** — identifiers (start `a-zA-Z$_`, continue `a-zA-Z0-9$.:-_`), `=`, quoted strings (either quote, unterminated → error), `...` spread, `>`, `/` (self-closing, line comment `//`, block comment `/*`, or the `<//>` shorthand), `//` line comments to EOL, `/*` block comments to `*/`. Whitespace is skipped, including between attribute name and `=`.
- **RAW_TEXT** — after a non-self-closing open of a raw-text element; regex-scans the chunk for the case-sensitive `</name>` (whitespace around slash/name tolerated) and emits one TEXT token up to it.
- **COMMENT / LINE_COMMENT / BLOCK_COMMENT** — consume to the terminator; may span chunks.
- **Expression holes** — at the end of chunk `i` (when `i < strings.length - 1`), an `EXPRESSION_TOKEN { value: i }` is pushed **iff** the current state is TEXT, TAG, or RAW_TEXT. Holes inside comments are swallowed — no token, the value is never used, later hole indices stay aligned.

### Parse (`src/parse.ts`)

Stack machine over tokens producing:

- Nodes: `ROOT`, `ELEMENT`, `COMPONENT` (capitalized name **or** expression index), `TEXT`, `EXPRESSION` (hole index).
- Props: `BOOLEAN`, `STATIC` (string value + quote char), `EXPRESSION` (hole index), `SPREAD` (hole index).
- Whitespace-only text runs between tags are dropped here (prev token `>` or next token `<`).
- Closing a **void element** clears its children; mismatched close throws; unclosed root throws.
- `<//>` shorthand: the close branch accepts a second `SLASH_TOKEN` only when the current parent's name is an expression index.

### Bake (`buildTemplate` / `buildNodes`, once per literal)

- Every **top-level element** (root child) and every **element child of a component** gets its own `<template>`: the element subtree is built with `document.createElement`/`createElementNS`, static and boolean props are `setAttribute`-ed onto it, expression/component children become comment placeholders (`<!--+-->` / `<!--Name-->`), text nodes are entity-decoded via a scratch `<template>` innerHTML round-trip.
- **Props that survive baking** (kept for runtime application): `prop:`-prefixed statics (always), and any static/boolean that appears **after a spread** (so source-order overrides hold). This is also where the claim stamp is set — a static `a[href]`/`form[action]` baked without a preceding spread marks `node.claim = true`, because once baked it can never be seen by the runtime's attribute-write recheck again.
- Top-level text and component-child text are entity-decoded in place (`node.value` replaced).

### Render (per tag call)

- `renderChildren` on an element with a template: `node.template.content.firstChild.cloneNode(true)`, then a shared `TreeWalker` (flag 129 = `SHOW_ELEMENT | SHOW_COMMENT`, created once at `createTaggedJSXRuntime`) walks the clone in lockstep with the AST. Holes are replaced via `r.insert(domNode.parentNode, value, marker)` and the walker is repositioned past the marker. Nested `<template>` elements get a fresh walker over their `.content`.
- Element nodes with surviving props get `r.spread(el, gatherProps(...), true)`; stamped nodes get `r.claimElement(el)`.
- `gatherProps` builds the props object in source order: booleans → `true`, statics → string, expressions → `applyGetter`, spreads → `r.mergeProps(props, spread)`. Component nodes with children get a `children` getter that re-renders the children lazily on access.
- Components render through `r.createComponent(comp, props)`; the result is inserted into the hole like any other value.

## Reactivity heuristic (`applyGetter`)

```ts
if (typeof value === "function" && value.length === 0 && name !== "ref" && !name.startsWith("on")) {
  Object.defineProperty(props, name, { get() { return value(); }, enumerable: true });
} else {
  props[name] = value;
}
```

Zero-arg functions on non-event, non-ref attributes become getters the runtime reads inside effects — that is the entire auto-reactivity story at the tag level. Everything reactive below it (which attributes become properties, which events are delegated) is the runtime adapter's job.

## Caching and performance

- **Cache key is the `TemplateStringsArray` object itself** (`WeakMap`). Each distinct literal *site* in source has its own strings array, so parsing+baking happens once per site, ever. Re-invocations of the same literal (e.g. inside a component body re-run) clone the template and rebind holes only.
- `cloneNode(true)` on a prebuilt template is dramatically cheaper than `createElement` per node — the same trick the Babel-compiler path uses with `_`$template(`...`)`.
- **CSP-safe**: no code generation anywhere — unlike `lit-dom-expressions` (which this package supersedes), nothing is compiled to a string and evaled, so strict CSPs work.
- **Memory**: one cached `<template>` per literal site plus per-render clones; the cache is weakly referenced and dies with the literal's strings array (e.g. on module reload).
- **No invalidation needed** — the baked template is static by construction; only holes and surviving props are dynamic.

## Return-value semantics

`flat(arr) = arr.length === 1 ? arr[0] : arr` applied to the rendered root children: single root → scalar node, multiple → array, empty → `[]`, whitespace-only literal → the raw whitespace string (a plain string scalar, which is why `` html`   ` `` returns `"   "`). The declared type is `JSX.Element` (the runtime's scalar-or-array union) — normalize with `[result].flat()` before iterating or spreading, and beware that spreading a string scalar splits it into characters.

## Environment constraints

- `createTaggedJSXRuntime` requires `document` at bind time (creates the shared `TreeWalker` and scratch `<template>`). The **module import** itself is DOM-agnostic (no top-level `document` access), so bundling for SSR is safe as long as the runtime is never constructed server-side.
- No SSR rendering path exists in the package — server HTML is the Babel-compiler/runtime SSR entries' job; hydration on the client uses the runtime's `hydrate`, not this tag.
- ESM-only consumption; `sideEffects: false` enables tree-shaking of the type-only exports.

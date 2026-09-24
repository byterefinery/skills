# Template syntax

Everything that can be written inside an `html` tagged template, per `src/tokenize.ts` + `src/parse.ts` and the package tests. Tag blocks are parsed with a state machine (text / tag / raw-text / comment states) over the literal's string chunks, with `${}` holes marking chunk boundaries.

## Elements

```ts
html`<div />`;              // self-closing
html`<div></div>`;          // matched pair
html`<input value="hi" />`; // void element, self-closing
```

- **Tag names** start with `a-zA-Z$_` and continue with `a-zA-Z0-9$.:-_` — custom elements (`<my-widget>`), dotted (`<ns.thing>`), and coloned names all tokenize.
- **Void elements** (runtime `VoidElements` set) discard their children when closed: `<input>x</input>` parses but `x` is dropped.
- **Mismatched closing tags throw** at parse time: `Mismatched closing tag for <div>`. Unclosed tags throw at template end: `Unclosed tag for <div>`.
- **Namespaces are inferred from the element name**, not the parent: a name in `SVGElements` → `createElementNS(svg)`, in `MathMLElements` → `createElementNS(math)`, otherwise HTML. So `<circle>` is SVG even if written outside an `<svg>` in the template, and nested dynamic SVG paths keep their namespace.
- **`<template>` is special** — its children are parsed as JSX (expressions work inside) and appended to the element's `.content` DocumentFragment; the render walk re-enters a fresh `TreeWalker` over `.content`. (The runtime's `RawTextElements` includes `template`, but the tag removes it before use.)

## Components

```ts
html`<MyComponent />`;           // registry lookup by capitalized name
html`<${MyComponent} />`;        // inline component via expression hole
html`<${MyComponent}>…</${MyComponent}>`;  // matched close for inline component
html`<${MyComponent}>…<//>`;     // shorthand close (dynamic components only)
```

- **Capitalized names** are looked up in the registry (`.define({ ... })`). An unregistered name throws at render: `Component "MyComponent" not found in registry`.
- **Expression tag names** take the value from the hole; it must be a function at render, otherwise the same `not found in registry` error. The value may itself be computed: `` html`<${items.length ? RowA : RowB}>` ``.
- **Shorthand close `<//>`** — inside a tag block, `//` is normally the start of a line comment. It becomes a close when it is immediately followed by `>` (whitespace between the two slashes' `//` and `>` is tolerated) *and* the open tag was an expression tag. The parser only accepts it when the open node's name is the expression index — i.e. **it works for `<${Comp}>` and throws for registered `<Comp>`**. The package's own test for the registered-component form is commented out.
- Component children become `props.children` — a **lazy getter** that re-renders the children on access (see Attributes below).

## Attributes

```ts
html`<input value="hi" />`           // static string (single or double quotes)
html`<input disabled />`             // boolean attribute
html`<input value=${val} />`         // dynamic expression
html`<input prop:value=${val} />`    // forced DOM property (always set as a property)
html`<input attr:foo=${val} />`      // forced HTML attribute
html`<input ...${props} />`          // spread (object only)
html`<input ref=${el => ...} />`     // ref — passed by value, never reactive-wrapped
html`<input onClick=${handler} />`   // event — delegated when the runtime supports it
html`<input onclick=${handler} />`   // legacy lowercase — direct listener
```

- **`name=value`** requires a string or an expression; anything else is a parse error (`Attribute value for "name" in <tag> must be an expression or a string`). A bare identifier before `=` with no value is a **boolean** attribute.
- **Static string values** keep inner newlines and JSON-like content: `uniforms='{ "iTime": { "value": 0 } }'` round-trips verbatim. An unterminated string throws `Unterminated string at <chunk>:<offset>`.
- **`prop:` / `attr:` prefixes** survive into the runtime props object (they are *not* baked into the template even without a spread) — the runtime applies them as a forced property/attribute respectively.
- **Spread ordering is source order** — later attributes override earlier ones across statics and spreads alike:

  ```ts
  html`<div id="static" class="red" ...${props} />`;   // spread wins: id="spread"
  html`<div ...${props} id="static" class="red" />`;   // statics after spread win: id="static"
  ```

  Mechanics: static props are `setAttribute`-baked at build time *unless* a spread precedes them; those that survive (post-spread, or `prop:`-prefixed) are re-applied at render through the runtime `spread`, preserving override order.
- **`...${expr}`** must be an expression at parse time; at render the value must be a non-null object or it throws `Can only spread objects`. Multiple spreads merge left-to-right through `runtime.mergeProps`.
- **`children`** — as an attribute on an element, honored only when the element has no template children (JSX parity). On a component with template children, `props.children` becomes a lazy getter that **overwrites any `children` passed in the same tag**.

## Reactivity of attribute values

`applyGetter` wraps a zero-argument function on a non-`ref`, non-`on*` expression attribute as an **enumerable getter** — the runtime then reads it inside an effect, making it reactive:

```ts
const [count] = createSignal(0);
html`<button count=${() => count()} />`;  // getter → reactive
html`<button count=${count} />`;          // signal accessor, also reactive
```

- To pass a zero-arg function **by value**, wrap it once more: `component=${() => Counter}` — the getter returns `Counter` itself, not the result of calling it.
- `on*` and `ref` values are always passed by value, even when zero-arg.
- Boolean/numeric/string expression values are passed by value (e.g. `hidden=${!visible}`) — reactivity there comes from the runtime re-running the effect when the surrounding owner tracks the signal.

## Raw-text elements

`style`, `script`, `noscript`, `textarea`, `title` (runtime `RawTextElements` minus `template`). After a non-self-closing open tag for one of these, the body is consumed **verbatim** until the case-sensitive closing tag — with whitespace tolerated around the slash and name, so `< / textarea >` still closes. Inside raw text:

- No JSX tokenization — `<`, `&`, `{}` are literal.
- `${}` holes still work: a hole boundary ends the raw scan, the value is inserted, and the raw scan resumes in the next chunk.
- A self-closing raw tag (`<style />`) is *not* raw text — it is a normal element.

```ts
const el = html`
  <style>
    #div { color: ${() => "red"}; background-color: blue; }
  </style>`;
// style.textContent === "#div { color: red; background-color: blue; }"
```

## Comments

- **HTML comments** `<!-- … -->` in text are stripped; they may span chunks. **Expressions inside them are dead** — a `<!-- c ${fn()} -->` swallows the hole, pushes no token, and `fn` is never called; later holes keep correct indices.
- **Line comments** `// …` inside **tag blocks** (between attributes, even before the tag name) run to end of line.
- **Block comments** `/* … */` inside tag blocks, including multi-line, with attributes continuing right after `*/`.

```ts
html`<button
  disabled // keep out for now
  /* class=${cls} */
  class="btn"
/>`;
```

Note the `//` vs `<//>` collision: a `//` in a tag block is a line comment unless it is the shorthand close (two slashes immediately followed by `>`, closing an expression-tag component).

## Whitespace and entities

- **Dropped**: pure-whitespace text runs *between tags* (a whitespace-only text node whose preceding token is a closing `>` or whose following token is an opening `<`). Indentation of a multi-line template therefore never appears in the DOM.
- **Kept**: whitespace *inside* a non-whitespace text run (e.g. the trailing space of `Hello, my name is: `), and all text inside raw-text bodies.
- **Entities are decoded** via a `<template>` innerHTML round-trip: `&copy;` → `©`, `&gt;` → `>`, numeric entities included. Decoding happens at bake time for top-level/component-child text and per text node for baked content.
- When exact spacing is required, pass it as an expression: `` html`<p>${" exact  spaces   "}</p>` ``.

## Result shape by template

| Template | Returned value |
|---|---|
| `` html`<div />` `` | the `div` element (scalar) |
| `` html`\n<div /> <span />\n` `` | `[div, span]` (array) |
| `` html`` `` | `[]` (empty array) |
| `` html`   ` `` | `"   "` (the whitespace string — a scalar text value) |
| `` html`${a} ${b}` `` | `[a, b]` (top-level expression holes are nodes too) |

Top-level expressions are first-class children: `` html`<div></div>${() => count()}` `` renders the element plus a live expression sibling. Normalize with `const nodes = [result].flat();`.

## Error messages (exact, for grep-able debugging)

| Message | Trigger |
|---|---|
| `Component "X" not found in registry` | capitalized name not registered, **or** dynamic `<${expr}>` whose value is not a function |
| `Can only spread objects` | `...${expr}` with nullish/non-object value at render |
| `Spread operator in <tag> must be followed by an expression` | `...` in a tag not followed by `${}` |
| `Mismatched closing tag for <tag>` | close name ≠ open name; `<//>` used to close a registered component |
| `Unclosed tag for <tag>` | missing closing tag at template end |
| `Unexpected token: … after <tag>` | malformed attribute or stray token |
| `Attribute value for "name" in <tag> must be an expression or a string` | `name=` with an invalid value |
| `Invalid attribute in <tag>` | attribute position not starting with an identifier or `...` |
| `Unterminated string at i:cursor` | unquoted attribute string |
| `Unexpected Character: c at i:cursor` | illegal character inside a tag block |

Parse errors fire at **first bake** of a literal (tag call); registry/spread/component-function errors fire at **render** (tag call). Both surface synchronously from the tagged-template evaluation.

## JSX vs `html` comparison

| Feature | Solid JSX | `html` tagged template |
|---|---|---|
| Fragments | `<>…</>` required for multiple roots | none needed — returns node or array |
| Spread | `<div {...props} />` | `<div ...${props} />` |
| Comments | `{/* … */}` | `<!-- … -->` in text; `//` and `/* */` inside tags |
| Raw-text tags | `innerHTML` workaround | `style`/`script`/`noscript`/`textarea`/`title` bodies are raw |
| Whitespace | JSX-style stripping | pure-whitespace runs between tags dropped; inside-text spaces kept |
| Reactivity | signals auto-wrapped | zero-arg functions auto-wrapped (double-wrap to opt out) |
| Component refs | identifier in scope | registered name or `<${Comp} />` expression hole |
| Build step | Babel plugin / Oxc compiler | none — parsed at runtime |

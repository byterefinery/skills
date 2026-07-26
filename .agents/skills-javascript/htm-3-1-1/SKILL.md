---
name: htm-3-1-1
description: >-
  HTM (Hyperscript Tagged Markup) 3.1.1 — JSX-like syntax via JavaScript tagged
  templates, no transpiler needed. Use when writing JSX-style markup in plain JS
  (React, Preact, or custom hyperscript functions), avoiding build-step JSX
  transforms, or developing directly in the browser. Covers binding, syntax rules,
  prebuilt integrations (htm/preact, htm/react, htm/preact/standalone), htm/mini,
  caching internals, spread props, babel-plugin-htm compilation, and
  babel-plugin-transform-jsx-to-htm migration.
license: Apache-2.0
compatibility: Node.js or modern browser with ES module support and tagged template literals
metadata:
  tags:
    - javascript
    - jsx
    - virtual-dom
    - preact
    - react
    - tagged-template
    - babel
---

# htm 3.1.1

## Overview

HTM parses JavaScript tagged template literals into calls to a hyperscript `h(type, props, ...children)` function, producing JSX-like markup with zero transpiler. It uses a character-by-character state machine to compile templates into cached operation lists, then evaluates them by driving `h()` calls.

Core API is a single default export — bind it to any hyperscript-compatible function:

```js
import htm from 'htm';
const html = htm.bind(h);
const result = html`<div id=${id}>Hello</div>`;
```

Prebuilt bindings: `htm/preact` (re-exports `h`, `Component`, `render`), `htm/react` (exports `html` only), `htm/preact/standalone` (Preact + HTM + hooks in one import, ~3.5 KB gzipped). `htm/mini` drops caching (~450 bytes). `babel-plugin-htm` compiles HTM away at build time for zero runtime cost.

## Usage

### Binding to a custom hyperscript function

```js
import htm from 'htm';

function h(type, props, ...children) {
  return { type, props, children };
}

const html = htm.bind(h);

html`<h1 id=hello>Hello world!</h1>`;
// { type: 'h1', props: { id: 'hello' }, children: ['Hello world!'] }
```

### Prebuilt Preact integration

```js
import { html, render, h, Component } from 'htm/preact';

render(html`<a href="/">Hello!</a>`, document.body);
```

### Prebuilt React integration

```js
import ReactDOM from 'react-dom';
import { html } from 'htm/react';

ReactDOM.render(html`<a href="/">Hello!</a>`, document.body);
```

### Standalone Preact (single import, no dependencies)

```js
import {
  html, render, h, Component,
  useState, useEffect, useRef, useMemo, useCallback, useContext
} from 'htm/preact/standalone';
```

Or direct from CDN:

```js
import { html, render } from 'https://unpkg.com/htm/preact/standalone.module.js';
```

### Component syntax

Components are JS values — use `<${...}>` (not `<Foo />`):

```js
const Header = ({ name }) => html`<h1>${name}</h1>`;

html`<${Header} name="App" />`;        // self-closing
html`<${Header} name="App"><//>`;      // auto-closing end tag
html`<${Header} name="App">body</${Header}>`;  // explicit end tag
```

### Spread props

```js
const props = { id: 'main', class: 'container' };
html`<div ...${props}>content</div>`;
```

Multiple spreads merge left-to-right via `Object.assign()`. The original spread object is never mutated.

```js
html`<a ...${base} ...${extra} href="/override" />`;
```

### Dynamic interpolation

```js
html`<span>Hello ${name}!</span>`;
html`<a href="/user/${id}/edit" />`;   // values concatenate as strings
```

### Boolean attributes

Bare names (no `=`) always produce `true`:

```js
html`<input disabled checked />`;      // { disabled: true, checked: true }
```

### Optional quotes

Values without whitespace or special chars need no quotes:

```js
html`<div class=foo id=bar />`;        // { class: 'foo', id: 'bar' }
```

### HTML comments (fully stripped)

```js
html`<div><!-- comment --><span /></div>`;
```

### Fragments (multiple roots)

```js
html`<div /><span />`;  // [h('div'), h('span')]
```

Single root returns the element directly. Empty template returns `undefined`.

### htm/mini — no caching, smaller

```js
import htm from 'htm/mini';
const html = htm.bind(h);
```

Disables template caching. Uses flat arrays instead of operation lists internally.

### Babel compilation — zero runtime cost

```json
{
  "plugins": [
    ["htm", { "pragma": "React.createElement" }]
  ]
}
```

Transforms `html`<div>Hello</div>` into `React.createElement("div", null, "Hello")` — the `htm` runtime becomes unnecessary and tree-shakes away.

Key options:

- `pragma` — target function (default `"h"`, `"React.createElement"`, or `false` for plain objects)
- `tag` — tagged template name to process (default `"html"`)
- `import` — auto-import the pragma module (string or `{module, export}` object)
- `useBuiltIns` — use native `Object.assign` for spreads (default `false`, uses Babel `_extends`)
- `useNativeSpread` — use `{ ...b }` spread syntax (takes precedence over `useBuiltIns`)
- `variableArity` — `false` for fixed 3-arg `h(type, props, children[])` (default `true`, variable args)
- `pragma=false` — output plain `{ tag, props, children }` objects
- `monomorphic` — all nodes share uniform object shape with `type` discriminator

## Gotchas

- **`htm` never inspects `h()` return values** — it only drives the call signature. Result shape is entirely your `h()` function's responsibility.
- **Caching is per-bound-function** — `htm.bind(h1)` and `htm.bind(h2)` maintain separate caches. `htm/mini` disables caching entirely. To disable caching in default build, add `this[0] = 3;` at the start of your `h()` function.
- **`<${Foo}>`, not `<Foo />`** — component references must be JS expressions inside `<${...}>`. Plain `<Foo />` would parse `Foo` as a literal tag name string.
- **Spread is `...${...}`, not `{...}`** — unlike JSX `{...props}`, HTM uses `...${props}` without curly braces around the spread.
- **`<//>` auto-closes the nearest open tag** — essential when the component is a variable: `<${Comp}><//>`.
- **Slash in tag/prop names triggers self-close** — `<ab/ba>` parses as self-closing `<ab>`. `<a pr/op=v>` treats `pr` as boolean prop, self-closes.
- **Slash in property values** — preserved unless followed by `>`: `<a href=val/ue>` keeps the slash; `<a href=value/>` self-closes with `href: 'value'`.
- **Empty template returns `undefined`** — `html`` is `undefined`, not `''` or `[]`.
- **Non-element roots** — `html`foo` returns `'foo'`. `html`a${1}b` returns `['a', 1, 'b']`.
- **`htm/preact` re-exports Preact core** — `h`, `Component`, `render` come from Preact. No separate import needed.
- **`htm/preact/standalone` re-exports hooks** — `useState`, `useEffect`, `useRef`, `useMemo`, `useCallback`, `useContext`, `useReducer`, `useLayoutEffect`, `useImperativeHandle`, `useDebugValue`, `useErrorBoundary`, plus `createContext`.
- **`htm/react` exports only `html`** — import `render`, `Component`, hooks from `react` / `react-dom` directly.
- **`babel-plugin-htm` processes only `html` tag by default** — use `tag` option for custom names. Tag name can be a regex pattern (e.g., `"/^html$/"`).
- **First evaluation is slower** — `evaluate()` rewrites the operation list in-place after first run, replacing `CHILD_RECURSE` with `CHILD_APPEND` for static children. Subsequent calls skip recursion.
- **`htm` is framework-agnostic** — bind it to `vhtml` for string HTML, `jsxobj` for config objects, or any custom `h()` function.
- **NUL characters are preserved** — in attribute values and text content, `\0` passes through without special handling.

## References

- [01-syntax-reference](references/01-syntax-reference.md) — Full syntax rules, tag modes, attribute parsing, edge cases
- [02-internal-architecture](references/02-internal-architecture.md) — Operation list format, caching, `build()` / `evaluate()` pipeline, `treeify()`
- [03-integrations](references/03-integrations.md) — Preact, React, vhtml, jsxobj bindings, standalone bundles, CDN imports
- [04-babel-plugins](references/04-babel-plugins.md) — `babel-plugin-htm` options, `babel-plugin-transform-jsx-to-htm`, compilation patterns

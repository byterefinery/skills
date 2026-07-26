# HTM 3.1.1 — Babel Plugins

## babel-plugin-htm

Compiles HTM tagged templates to hyperscript calls at build time, eliminating the runtime parser entirely.

### Installation

```bash
npm install --save-dev babel-plugin-htm
# or
npm install --save-dev htm  # included in the main package
```

### Basic configuration

```json
{
  "plugins": [
    ["htm", {
      "pragma": "React.createElement"
    }]
  ]
}
```

### Transformation

```js
// Input:
html`<div id="foo">hello ${you}</div>`

// Output:
React.createElement("div", { id: "foo" }, "hello ", you)
```

### How it works

The plugin uses `build()` and `treeify()` from htm's source to parse the template at compile time, then generates equivalent `h()` calls. This means the same parsing logic runs at build time instead of runtime.

```js
// Inside babel-plugin-htm:
import { build, treeify } from '../../src/build.mjs';

// For each html`...` expression:
const statics = path.node.quasi.quasis.map(e => e.value.raw);
const expr = path.node.quasi.expressions;
const tree = treeify(build(statics), expr);
// tree → { tag, props, children } → transformed to h() call
```

### Options

#### `pragma` (default: `"h"`)

The target hyperscript function. Accepts dotted paths like `"React.createElement"`.

```json
["htm", { "pragma": "h" }]              // h("div", { id: "foo" }, "hello ", you)
["htm", { "pragma": "React.createElement" }]
["htm", { "pragma": "Preact.h" }]
["htm", { "pragma": false }]            // plain objects
```

When `pragma` is `false`, output is plain `{ tag, props, children }` objects instead of function calls.

#### `tag` (default: `"html"`)

The tagged template name to process. Can be a string or regex pattern.

```json
["htm", { "tag": "myTag" }]
["htm", { "tag": "/^html$/" }]          // regex pattern
```

```js
// With tag: "myTag"
myTag`<div />`;  // transformed
html`<div />`;   // left alone
```

#### `import` (default: `false`)

Auto-import the pragma function. Only adds import if HTM templates are actually used in the file.

**String form** — imports pragma from module:

```json
["htm", {
  "tag": "$$html",
  "import": "preact"
}]
```

Produces:

```js
import { h } from 'preact';
// $$html`<div />` → h("div", null)
```

**Object form** — full control over import:

```json
["htm", {
  "pragma": "React.createElement",
  "tag": "$$html",
  "import": {
    "module": "react",
    "export": "default"
  }
}]
```

Produces:

```js
import React from 'react';
// $$html`<div />` → React.createElement("div", null)
```

Export values:
- `"default"` — `import React from 'react'`
- `"*"` — `import * as Preact from 'preact'`
- `"h"` — `import { h } from 'preact'`
- `null` or omitted — `import { h } from 'module'` (uses pragma name)

#### `useBuiltIns` (default: `false`)

Use native `Object.assign()` for prop spreads instead of Babel's `_extends` helper.

```js
// Default (Babel _extends helper):
_extends({}, a, { x: 'y' })

// With useBuiltIns: true
Object.assign({}, a, { x: 'y' })
```

#### `useNativeSpread` (default: `false`)

Use ES2018 object spread syntax `{ ...b }` for prop spreads. Takes precedence over `useBuiltIns`.

```js
// With useNativeSpread: true
{ ...a, x: 'y' }
```

#### `variableArity` (default: `true`)

Controls how children are passed to `h()`.

**`true` (default)** — variable arguments, matches JSX output:

```js
html`<div />`           // h("div", null)
html`<div a />`         // h("div", { a: true })
html`<div>b</div>`      // h("div", null, "b")
html`<div a>b</div>`    // h("div", { a: true }, "b")
```

**`false`** — always exactly 3 arguments:

```js
html`<div />`           // h("div", null, [])
html`<div a />`         // h("div", { a: true }, [])
html`<div>b</div>`      // h("div", null, ["b"])
html`<div a>b</div>`    // h("div", { a: true }, ["b"])
```

Use `false` when your `h()` function expects a fixed signature `h(type, props, children[])`.

#### `pragma=false` — plain object output

```json
["htm", { "pragma": false }]
```

```js
// Input:
html`<div id="foo">hello ${you}</div>`

// Output:
{ tag: "div", props: { id: "foo" }, children: ["hello ", you] }
```

Useful for creating static data structures without any runtime function calls.

#### `monomorphic` — uniform object shapes

Like `pragma=false` but all nodes (including text) share the same object shape with a `type` discriminator:

```json
["htm", { "monomorphic": true }]
```

```js
// Input:
html`<div id="foo">hello ${you}</div>`

// Output:
{
  type: 1,
  tag: "div",
  props: { id: "foo" },
  text: null,
  children: [
    { type: 3, tag: null, props: null, text: "hello ", children: null },
    you
  ]
}
```

Type discriminators: `1` = element, `3` = text node. All nodes have the same shape, which can improve JIT optimization in V8.

### Spread transformation

How prop spreads are compiled depends on options:

```js
html`<a ...${foo}></a>`;
// → h("a", foo)  (single spread collapses to just the variable)

html`<a ...${foo} ...${bar}></a>`;
// useBuiltIns: true  → h("a", Object.assign({}, foo, bar))
// useNativeSpread: true → h("a", { ...foo, ...bar })
// default → h("a", _extends({}, foo, bar))

html`<a b="1" ...${foo}></a>`;
// useBuiltIns: true → h("a", Object.assign({b:"1"}, foo))
// useNativeSpread: true → h("a", {b:"1", ...foo})

html`<a ...${foo} b="1"></a>`;
// useBuiltIns: true → h("a", Object.assign({}, foo, {b:"1"}))
// useNativeSpread: true → h("a", { ...foo, b: "1" })
```

### String coercion

When mixing static and dynamic values in props, the plugin coerces to strings:

```js
html`<a b=${1}${2}></a>`;
// → h("a", { b: "" + 1 + 2 })

html`<a b="1${2}${3}"></a>`;
// → h("a", { b: "1" + 2 + 3 })
```

The leading `"" +` ensures numeric values are stringified when concatenated.

---

## babel-plugin-transform-jsx-to-htm

Converts JSX syntax to HTM tagged templates. Useful for migrating from JSX to HTM or for environments where JSX transforms aren't available but tagged templates are.

### Installation

```bash
npm install --save-dev babel-plugin-transform-jsx-to-htm
# or
npm install --save-dev htm  # included in the main package
```

### Configuration

```json
{
  "plugins": [
    "babel-plugin-transform-jsx-to-htm",
    "htm"
  ]
}
```

Use both plugins in sequence: `transform-jsx-to-htm` first (JSX → HTM), then `htm` (HTM → hyperscript calls).

### Transformation

```js
// Input (JSX):
const Foo = () => <h1>Hello</h1>

// After transform-jsx-to-htm:
const Foo = () => html`<h1>Hello</h1>`

// After babel-plugin-htm:
const Foo = () => h("h1", null, "Hello")
```

### Options

#### `tag` (default: `"html"`)

The tagged template function name to produce.

```json
["babel-plugin-transform-jsx-to-htm", { "tag": "$$html" }]
```

```js
// Output:
$$html`<h1>Hello</h1>`
```

#### `terse` (default: `false`)

Use `<//>` for closing component tags instead of `</${Comp}>`.

```js
// terse: false
html`<${Comp}>content</${Comp}>`

// terse: true
html`<${Comp}>content<//>`
```

#### `import` (default: `false`)

Auto-import the tag function.

```json
["babel-plugin-transform-jsx-to-htm", {
  "tag": "$$html",
  "import": {
    "module": "htm/preact",
    "export": "html"
  }
}]
```

Produces:

```js
import { html as $$html } from 'htm/preact';
export default $$html`<h1>hello</h1>`
```

### JSX to HTM mapping

| JSX | HTM |
|---|---|
| `<div />` | `<div />` |
| `<div>text</div>` | `<div>text</div>` |
| `<div>{expr}</div>` | `<div>${expr}</div>` |
| `<div prop={val} />` | `<div prop=${val} />` |
| `<div prop="str" />` | `<div prop="str" />` or `<div prop=str />` |
| `<div {...spread} />` | `<div ...${spread} />` |
| `<Comp />` | `<${Comp} />` |
| `<Comp>child</Comp>` | `<${Comp}>child<//>` or `<${Comp}>child</${Comp}>` |
| `<React.Fragment>...</React.Fragment>` | handled as fragment |
| `<>...</>` | handled as fragment |

### Text escaping

Text content containing `<` is escaped by converting to an expression:

```js
// JSX:
<div>a &lt;b&gt; c</div>

// HTM:
html`<div>${"a <b> c"}</div>`
```

### Attribute escaping

Attribute values are quoted optimistically — uses unquoted form when safe, double quotes when value contains `'`, single quotes when value contains `"`.

---

## Production strategy

Recommended setup: compile HTM away entirely for production.

```json
{
  "plugins": [
    ["htm", {
      "pragma": "React.createElement",
      "tag": "html",
      "useBuiltIns": true
    }]
  ]
}
```

Benefits:
- `htm` runtime tree-shakes away (no imports needed in production)
- Output identical to JSX transpilation
- Zero runtime parsing overhead
- Works with React DevTools (same `React.createElement` calls)
- Smaller bundle size (no HTM parser in output)

Development workflow: use `htm` at runtime for fast iteration (no rebuild). Production: compile with Babel plugin.

### Migrating from JSX

1. Add `babel-plugin-transform-jsx-to-htm` to convert JSX → HTM
2. Add `babel-plugin-htm` to compile HTM → hyperscript calls
3. Remove JSX transform from your Babel config
4. Optionally remove `babel-plugin-transform-jsx-to-htm` once source is rewritten to use HTM syntax directly

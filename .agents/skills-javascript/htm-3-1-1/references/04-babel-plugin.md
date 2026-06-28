# babel-plugin-htm

## Overview

`babel-plugin-htm` compiles htm tagged templates to hyperscript calls at build time,
eliminating the runtime parsing cost. The output is identical to what htm produces at runtime.

## Installation

```sh
npm i -D babel-plugin-htm
```

## Configuration

```js
// .babelrc or babel.config.js
{
  "plugins": [
    ["babel-plugin-htm", {
      "pragma": "h",
      "tag": "html"
    }]
  ]
}
```

## Input / Output

```js
// Input
html`<div id="foo">hello ${you}</div>`

// Output
h("div", { id: "foo" }, "hello ", you)
```

## Options

### `pragma` (default: `"h"`)

The hyperscript function to compile to:

```js
// With pragma: "React.createElement"
html`<div />`
// → React.createElement("div", null)

// With pragma: "h" (default)
html`<div />`
// → h("div", null)
```

Set to `false` for plain object output:

```js
// pragma: false
html`<div id="foo">hello</div>`
// → { tag: "div", props: { id: "foo" }, children: ["hello"] }
```

### `tag` (default: `"html"`)

The tagged template tag function name to process:

```js
{
  "plugins": [["babel-plugin-htm", { "tag": "myTag" }]]
}

// Only myTag`...` is processed, not html`...`
myTag`<div />`;
```

Supports regex patterns:

```js
{ "tag": "/^html$/" }
```

### `import` (default: `false`)

Auto-import the pragma function:

```js
// String form
{ "import": "preact" }
// Adds: import { h } from 'preact';

// Object form
{
  "import": {
    "module": "react",
    "export": "default"
  }
}
// Adds: import React from 'react';
```

### `variableArity` (default: `true`)

When `true` (default), children are spread as individual arguments:

```js
html`<div>a<b /></div>`
// h("div", null, "a", h("b", null))
```

When `false`, children are always an array (always exactly 3 arguments):

```js
html`<div>a<b /></div>`
// h("div", null, ["a", h("b", null, [])])
```

### `useBuiltIns` (default: `false`)

Use native `Object.assign()` instead of Babel's `_extends` helper for spread props:

```js
// useBuiltIns: true
html`<div ...${props} />`
// h("div", Object.assign({}, props))

// useBuiltIns: false (default)
html`<div ...${props} />`
// h("div", _extends({}, props))
```

### `useNativeSpread` (default: `false`)

Use native object spread `{ ...a, ...b }` instead of `Object.assign()`:

```js
html`<div ...${a} ...${b} />`
// h("div", { ...a, ...b })
```

Takes precedence over `useBuiltIns`.

### `monomorphic` (default: `false`)

Output monomorphic inline objects — all nodes (including text) use the same object shape:

```js
html`<div>hello</div>`
// {
//   type: 1,
//   tag: "div",
//   props: null,
//   text: null,
//   children: [
//     { type: 3, tag: null, props: null, text: "hello", children: null }
//   ]
// }
```

## babel-plugin-transform-jsx-to-htm

A separate plugin that converts JSX syntax into htm tagged templates:

```js
// Input (JSX)
const Foo = () => <h1>Hello</h1>

// Output (htm)
const Foo = () => html`<h1>Hello</h1>`
```

### Installation

```sh
npm i -D babel-plugin-transform-jsx-to-htm
```

### Configuration

```js
{
  "plugins": [
    ["babel-plugin-transform-jsx-to-htm", {
      "tag": "html",
      "import": false
    }]
  ]
}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `tag` | String | `"html"` | Tag function name for output |
| `import` | false\|String\|Object | `false` | Auto-import the tag function |

### Auto-import example

```js
{
  "plugins": [
    ["babel-plugin-transform-jsx-to-htm", {
      "tag": "$$html",
      "import": {
        "module": "htm/preact",
        "export": "html"
      }
    }]
  ]
}
```

Produces:

```js
import { html as $$html } from 'htm/preact';
const Foo = () => $$html`<h1>Hello</h1>`;
```

## Workflow: JSX → htm → hyperscript

You can chain both plugins to write JSX and get hyperscript output:

1. `babel-plugin-transform-jsx-to-htm` converts JSX → htm tagged templates
2. `babel-plugin-htm` compiles htm → hyperscript calls

Order matters — jsx-to-htm must run first:

```js
{
  "plugins": [
    "babel-plugin-transform-jsx-to-htm",
    "babel-plugin-htm"
  ]
}
```

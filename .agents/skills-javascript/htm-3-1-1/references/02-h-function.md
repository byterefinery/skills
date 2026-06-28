# The h() Function Contract

## Signature

htm calls your `h()` function with this signature:

```js
h(type, props, ...children)
```

- **`type`** — string tag name (e.g., `'div'`) or a component function/reference
- **`props`** — object with attributes/properties, or `null` if none
- **`...children`** — zero or more children (strings, nested h() results, arrays, primitives)

## Minimal implementation

```js
function h(type, props, ...children) {
  return { type, props, children };
}

const html = htm.bind(h);
```

## Binding

Create the tagged template by binding htm to your h function:

```js
import htm from 'htm';
const html = htm.bind(h);
```

Each bind creates a separate template cache. The bound function is the tagged template:

```js
html`<div>hello</div>`
```

## Multiple bindings

You can bind htm to different h functions:

```js
const html1 = htm.bind(h1);
const html2 = htm.bind(h2);

// Each has its own template cache
html1`<div>a</div>`;
html2`<div>a</div>`;
```

## Using with Preact

```js
import { h } from 'preact';
import htm from 'htm';
const html = htm.bind(h);
```

Or use the prebuilt binding:

```js
import { html } from 'htm/preact';
```

## Using with React

```js
import { createElement } from 'react';
import htm from 'htm';
const html = htm.bind(createElement);
```

Or use the prebuilt binding:

```js
import { html } from 'htm/react';
```

## Using with vhtml (string output)

```js
import htm from 'htm';
import vhtml from 'vhtml';
const html = htm.bind(vhtml);

html`<h1>Hello</h1>`;  // '<h1>Hello</h1>'
```

## Using with lit-html

```js
import htm from 'htm';
import { html as litHtml } from 'lit-html';
const html = htm.bind(litHtml);
```

## The `this` context

When htm calls your `h()` function, `this` is set to the operation list (an array).
The first element `this[0]` contains staticness bits (see Caching reference).

You can use `this` to access or modify the operation list:

```js
function h(type, props, ...children) {
  // this is the operation list array
  // this[0] contains staticness bits
  return { type, props, children };
}
```

## Disabling caching via `this[0]`

Setting `this[0] = 3` at the start of your `h` function disables caching for all elements:

```js
function h(type, props, ...children) {
  this[0] = 3;  // mark everything as dynamic
  return { type, props, children };
}
```

## Variable arity

htm passes children as spread arguments, not as an array:

```js
// htm calls:
h('div', null, 'hello', h('span', null, 'world'))

// NOT:
h('div', null, ['hello', h('span', null, ['world'])])
```

If you need exactly 3 arguments, use `babel-plugin-htm` with `{ variableArity: false }`.

## Return value

htm never inspects the return value of `h()`. Return whatever your rendering system expects:
- Virtual DOM nodes (Preact, React)
- Plain objects (custom renderers)
- Strings (vhtml)
- Template results (lit-html)

## Props handling

htm passes props as a plain object. Be aware of:

- Boolean attributes become `true` values: `<input disabled>` → `{ disabled: true }`
- Empty string values: `<input value="">` → `{ value: '' }`
- Spread props are merged via `Object.assign()`
- Prop values are always strings for static values, but preserve type for dynamic `${}` values

```js
html`<a href="/path" count=${42} />`
// props: { href: '/path', count: 42 }
// href is string (static), count is number (dynamic)
```

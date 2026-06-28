---
name: htm-3-1-1
description: >
  htm 3.1.1 — JSX-like syntax in plain JavaScript via Tagged Templates, no transpiler required.
  Use when the project uses htm (not JSX/TSX), including htm/preact, htm/react, or
  htm.bind(h) with custom hyperscript functions. Covers the $-braced component
  syntax, auto-closing tags, spread props, babel-plugin-htm compilation, and htm/mini.
metadata:
  tags:
    - javascript
    - templating
    - virtual-dom
    - preact
    - react
---

# htm 3.1.1

htm (Hyperscript Tagged Markup) is a library that lets you write JSX-like markup inside
plain JavaScript tagged template literals — no transpiler needed. It parses the template
and calls a hyperscript function `h(type, props, ...children)` for each element.

## Overview

htm works by binding a tagged template function to a hyperscript `h()` function. The
tagged template parses HTML-like syntax and translates it into `h()` calls. It is
framework-agnostic: works with Preact, React, lit-html, vhtml, or any custom `h()` function.

**Core difference from JSX**: htm uses JavaScript tagged templates at runtime (or compiles
via `babel-plugin-htm`), while JSX requires a compile step. The syntax is close to JSX but
has distinct differences in how components, expressions, and spreads are written.

## Usage

### Basic binding

```js
import htm from 'htm';

function h(type, props, ...children) {
  return { type, props, children };
}

const html = htm.bind(h);

html`<h1 id=hello>Hello world!</h1>`
// { type: 'h1', props: { id: 'hello' }, children: ['Hello world!'] }
```

### Preact

```js
import { html, render } from 'htm/preact';

const App = () => html`<h1>Hello</h1>`;
render(html`<${App} />`, document.body);
```

### React

```js
import ReactDOM from 'react-dom';
import { html } from 'htm/react';

const App = () => html`<h1>Hello</h1>`;
ReactDOM.render(html`<${App} />`, document.body);
```

### Standalone Preact (single import, no build tool)

```js
import { html, Component, render } from 'https://unpkg.com/htm/preact/standalone.module.js';
```

### Dynamic values

Use `${}` (template literal interpolation) for expressions — not JSX-style `{}`:

```js
const name = 'world';
html`<h1>Hello ${name}!</h1>`;
html`<a href=${url} onClick=${handler}>Click</a>`;
```

### Props

```js
// Static string values — quotes optional
html`<div class=foo id=bar></div>`;
html`<div class="foo bar"></div>`;

// Boolean attributes
html`<input disabled />`;
html`<input draggable />`;

// Dynamic values
html`<a href=${url} />`;

// Spread props — use ...${}, not {...}
html`<div ...${props}></div>`;
html`<div class=wrapper ...${extraProps}></div>`;

// Concatenated prop values
html`<a href="/path/${id}" />`;  // "/path/42"
```

### Children

```js
// Text children
html`<p>Hello world</p>`;

// Dynamic children
html`<p>${greeting}</p>`;

// Element children
html`<div><span>nested</span></div>`;

// Mixed children
html`<div>before <span>middle</span> after</div>`;

// Arrays and conditionals
html`<ul>
  ${items.map(item => html`<li key=${item.id}>${item.name}</li>`)}
</ul>`;
```

### Multiple root elements (fragments)

htm supports multiple roots natively — returns an array:

```js
html`<div /><div />`
// [{ tag: 'div', ... }, { tag: 'div', ... }]
```

### HTML comments

```js
html`<div><!-- this is a comment --></div>`;
```

### htm/mini

Smaller build (~450 bytes) with no template caching:

```js
import htm from 'htm/mini';
const html = htm.bind(h);
```

### babel-plugin-htm

Compile htm at build time for zero runtime cost:

```js
// .babelrc
{
  "plugins": [
    ["babel-plugin-htm", {
      "pragma": "h",
      "tag": "html"
    }]
  ]
}
```

## Gotchas

### Component opening syntax: `<${Foo}>` not `<Foo>`

This is the biggest difference from JSX. Components must be opened with `<${ComponentName}>`:

```js
// htm — correct
html`<${Foo} />`
html`<${Foo} name=${name}>content</${Foo}>`

// JSX — does NOT work in htm
html`<Foo />`        // parsed as literal tag name "Foo"
html`<Foo>content</Foo>`  // same — literal tag name "Foo"
```

The `<${}>` wrapper tells htm to evaluate the JavaScript expression as the component
reference. Without it, the tag name is treated as a plain string.

### Component closing: three options

Components have three closing styles:

1. **Self-closing** — `<${Foo} />` or `<${Foo}/>`. No children.
2. **Explicit end tag** — `<${Foo}>content</${Foo}>`. The closing tag must match with `<${...}>` syntax.
3. **Auto-closing** — `<${Foo}>content<//>`. The `<//>` shorthand closes the most recent open tag.

```js
// All three are valid
html`<${Foo} />`
html`<${Foo}>content</${Foo}>`
html`<${Foo}>content<//>`

// Nested with auto-close
html`<${Outer}><${Inner}><//>more<//>`
```

### Mixing component closing styles in nesting

With `<//>`, the auto-close always closes the **most recently opened** tag. Be careful with nesting:

```js
// Correct nesting with <//>
html`<${A}><${B}><//>text after B<//>`

// This works too — explicit closing mixed with auto
html`<${A}><${B}></${B}>text<//>`
```

### `<//>` works for any tag, not just components

The auto-close `<//>` closes any open tag — HTML elements and components alike:

```js
html`<div>content<//>`           // same as <div>content</div>
html`<${Foo}>content<//>`        // same as <${Foo}>content</${Foo}>
```

### Expressions use `${}`, not `{}`

JSX uses `{expression}` everywhere. htm uses `${expression}` (template literal interpolation):

```js
// htm
html`<div class=${cls}>${text}</div>`

// JSX equivalent
<div className={cls}>{text}</div>
```

Inside the tag name position, use `<${expr}>` for dynamic tags/components.

### Spread props use `...${}`, not `{...}`

```js
// htm
html`<div ...${props}></div>`

// JSX equivalent
<div {...props}></div>
```

### Slash in tag names and prop names self-closes

A `/` character in the middle of a tag name or prop name acts as a self-close:

```js
html`<ab/ba>`     // parsed as self-closing <ab> — "ba" is ignored
html`<a pr/op>`   // parsed as <a pr> — self-closing, "op" ignored
```

However, `/` inside a **prop value** does NOT self-close unless immediately followed by `>`:

```js
html`<a href=val/ue></a>`    // props: { href: 'val/ue' }, NOT self-closed
html`<a href=value/>`        // props: { href: 'value' }, self-closed (the /> ends the tag)
html`<a href=value/ ></a>`   // props: { href: 'value/' }, NOT self-closed (space before >)
```

### Unquoted attribute values

htm supports HTML-style unquoted values, but only for simple tokens (no spaces):

```js
html`<div class=foo></div>`     // { class: 'foo' }
html`<div class="foo bar"></div>` // { class: 'foo bar' }
// html`<div class=foo bar></div>` — "bar" is a separate boolean attribute
```

### Empty templates return `undefined`

```js
html``  // undefined
```

Non-element text returns the text directly (or an array for mixed content):

```js
html`hello`       // "hello"
html`${1}`        // 1
html`a${1}b`      // ["a", 1, "b"]
```

### Caching: static subtrees are reused

htm caches parsed template structures. Identical static templates return the **same object reference**:

```js
const a = html`<div>static</div>`;
const b = html`<div>static</div>`;
a === b;  // true — same cached object
```

This is an optimization, not a bug. If your `h()` function mutates returned objects, cache reuse will cause issues. Use `htm/mini` or set `this[0] = 3` in your `h` function to disable caching.

### `this[0]` staticness bits in `h()`

When htm calls your `h()` function, `this` is the operation list and `this[0]` contains staticness bits:

- `0` — fully static subtree (no dynamic values)
- `1` — dynamic props, static children
- `2` — static props, some dynamic children
- `3` — dynamic props and dynamic children

You can modify `this[0]` to force a subtree to be treated as static (enabling caching):

```js
function h(type, props, ...children) {
  if (props['@static']) {
    this[0] &= ~3;  // force static
  }
  return { type, props, children };
}
```

### Spread objects are not mutated

htm does not mutate the spread source objects:

```js
const obj = {};
html`<div ...${obj} foo=bar></div>`;
obj;  // still {}
```

### Dynamic tag names

Use `<${expr}>` for dynamic tag names (works for both HTML tags and components):

```js
const tag = 'h1';
html`<${tag}>Hello</${tag}>`;

const Component = SomeComponent;
html`<${Component} />`;
```

### Case-sensitive prop names

htm preserves case in prop names, which matters for React's camelCase props:

```js
html`<div onClick=${handler} />`  // { onClick: handler }
html`<div onclick=${handler} />`  // { onclick: handler }
```

### The `html` tag name is a convention

The variable name `html` is just a convention. You can name it anything:

```js
const htm_ = htm.bind(h);
htm_`<div>hello</div>`;
```

For `babel-plugin-htm`, configure the tag name with the `tag` option.

## References

- [01-component-syntax](references/01-component-syntax.md) — Component opening, closing, and nesting patterns
- [02-h-function](references/02-h-function.md) — Custom hyperscript functions, binding, and the h() contract
- [03-caching](references/03-caching.md) — Template caching internals, staticness bits, and htm/mini
- [04-babel-plugin](references/04-babel-plugin.md) — babel-plugin-htm and babel-plugin-transform-jsx-to-htm
- [05-integrations](references/05-integrations.md) — htm/preact, htm/react, and standalone builds

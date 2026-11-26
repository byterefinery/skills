# Template Engine

## Table of Contents

- [html & svg](#html--svg)
- [Attributes & properties](#attributes--properties)
- [Event listeners](#event-listeners)
- [Form elements & html.set](#form-elements--htmlset)
- [Content values](#content-values)
- [Promises](#promises)
- [Conditions](#conditions)
- [Iteration & keys](#iteration--keys)
- [Nested templates](#nested-templates)
- [Styling](#styling)
- [Plugins & .use](#plugins--use)
- [html.resolve](#htmlresolve)
- [html.transition](#htmltransition)
- [Limitations](#limitations)

---

## html & svg

`html` and `svg` are tagged template literal functions (same interface; `svg` uses the SVG namespace) returning an update function that takes `host` and `target` (a text node position marker). Static content is untouched on updates; only expressions are resolved.

```js
import { html, svg } from "hybrids";

const update = ({ value }) => html`
  <div>${value}</div>
`;
```

The `<svg>` container element must be created with `html`; use `svg` only for the internal structure:

```js
const update = ({ radius }) => html`
  <svg viewBox="0 0 300 100">${
    svg`<circle cx="50" cy="50" r="${radius}" />`
  }</svg>
`;
```

## Attributes & properties

```js
html`<my-element propertyName="${value}" other-property="${value}"></my-element>`;
```

An attribute expression sets the matching existing case-sensitive property, the camelCased property, or **falls back to the attribute value** when the property is not found or is read-only (e.g., `form` or `list` on `<input>`). This maximizes compatibility with custom elements created outside the library.

**Mixed values** — if the attribute contains extra characters or multiple expressions, the attribute is always used with the concatenated string (precedence over the special cases below):

```js
html`<div id="el" class="button ${buttonType} ${buttonColor}"></div>`
```

### class

The `class` expression adds/removes class names via `classList`. Accepts a string, an array of strings, or a map of name → boolean:

```js
const name = "one two";
const array = ["one", "two"];
const map = { one: true, two: false };

html`<div class="${name || array || map}"></div>`;
```

### style

The `style` expression must be an object (dashed or camelCase keys), applied via the `CSSStyleDeclaration` API:

```js
const styles = {
  backgroundColor: "red",
  "font-face": "Arial",
};

html`<div style="${styles}"></div>`;
```

For actual styling, prefer the [styling](#styling) helpers.

## Event listeners

An `on*` attribute expression sets an event listener via `host.addEventListener(eventType, callback, false)`; the event type is the exact characters after `on`. The callback's first argument is the host element (the event target is at `event.target`), so callbacks can be defined as pure functions:

```js
function send(host, event) {
  event.preventDefault();
  sendData("api.com/create", { value: host.value });
}

define({
  tag: "my-element",
  value: 42,
  render: () => html`
    <form onsubmit="${send}">...</form>
  `,
});
```

**Options** — pass custom `addEventListener` options via the function's `.options` property (boolean or options object):

```js
function onScroll(host) { /* ... */ }
onScroll.options = { passive: true };

html`<div class="container" onscroll="${onScroll}">...</div>`;
```

## Form elements & html.set

Manual binding works with a callback:

```js
function updateName(host, event) {
  host.name = event.target.value;
}

html`<input type="text" defaultValue="${name}" oninput="${updateName}" />`;
```

`html.set()` generates the callback for you:

### Host property

```js
html.set(propertyName: string, value?: any): Function
```

Per-element behavior:

- `<input type="radio">` / `<input type="checkbox">` — uses `checked`
- `<input type="file">` — uses `event.target.files`
- Everything else — `event.detail.value` if defined, otherwise `event.target.value`

```js
html`
  <input type="checkbox" checked="${option}" onchange="${html.set("option")}" />
  <my-date-picker value="${date}" onchange="${html.set("date")}"></my-date-picker>
  <paper-toggle-button onchecked-changed="${html.set("option")}"></paper-toggle-button>
`;
```

The second argument overrides the value entirely (useful inside loops):

```js
${items.map((item) => html`
  <button onclick="${html.set("selected", item)}">select item!</button>
`)}
```

### Store model

```js
html.set(model: object, propertyPath: string | null): Function
```

`propertyPath` is a single name or dot path (`"address.street"`); `null` deletes the model:

```js
define({
  tag: "my-element",
  user: store(User, { id: "userId", draft: true }),
  render: ({ user }) => html`
    <input value="${user.firstName}" oninput="${html.set(user, "firstName")}"/>
    <input value="${user.address.street}" oninput="${html.set(user, "address.street")}"/>
    <button onclick="${html.set(user, null)}">Delete user</button>
  `,
});
```

## Content values

- Non-function, non-Promise, non-Node values resolve to `textContent`
- Falsy values **except the number `0`** render nothing (empty string) — same rules apply inside arrays
- HTML content via `innerHTML` is possible but an XSS risk — use with caution
- **Node instances** attach to the DOM — useful for canvas or other elements that need a reference (create once in a no-dependency property)
- **Functions** resolve to nested templates
- **Promises** resolve to their [result](#promises)

## Promises

Supported directly as content expressions since 9.2:

- The previous content stays in place until the promise resolves
- The resolved value is rendered by the normal content rules (nested template, array, Node, or primitive)
- If the expression updates before the promise resolves, the pending promise's result is ignored
- **Rejected promises are not handled** — chain `.catch()` to render an error state

```js
html`
  <div>
    ${asyncApi()
      .then((value) => html`<div>${value}</div>`)}
  </div>
`;
```

For a placeholder while pending, use [`html.resolve`](#htmlresolve).

## Conditions

Return falsy values (except `0`) to clear previously rendered content:

```js
html`<div>${isValid && html`<p>Valid</p>`}</div>`;
```

## Iteration & keys

Expressions may return arrays; items can be primitives, nested templates, or nested arrays. By default the array index identifies items for re-rendering. Use `.key(id)` for identity-based efficient reordering (existing template is updated instead of recreated when a key is found):

```js
html`
  <todo-list>
    ${names.map((name) => `Name: ${name}`)}

    ${items.map(({ id, name }) =>
      html`<todo-item>${name}</todo-item>`.key(id),
    )}
  </todo-list>
`;
```

## Nested templates

Expressions may return a function taking `(host, target)` — the update function from `html` is compatible. The child template propagates the parent's element instance context, so callbacks used in nested templates receive the same host:

```js
const submit = (fn) => html`
  <button type="submit" onclick="${fn}">Submit</button>
`;

html`
  <form>
    ${submit(myCallback)}
  </form>
`;
```

## Styling

### .css (preferred)

```js
html`...`.css`div { color: ${value}; }`
```

CSS in a tagged template literal (interpolatable). Most performant: when Constructable Stylesheets are supported, the generated CSS is shared between all elements with the same style.

### .style

For CSS content generated outside the template:

```js
html`...`.style(globals, styles, inlineStyles);
```

Accepts a list of CSS strings or `CSSStyleSheet` instances. Constructable Stylesheets are created and adopted when supported and:

- the CSS content contains no `@import`
- `.style()` is called on the **root template** of the custom element (nested templates fall back to a `<style>` element)

String input creates one `CSSStyleSheet` instance shared across all element instances. Passing `CSSStyleSheet` instances yourself works only in that mode — avoid it when targeting browsers without support.

### <style> element

A `<style>` element directly in the (Shadow DOM) template body also works.

## Plugins & .use

The template functions return an update function `(host, target) => void`. Wrap it for custom update control:

```js
function myPlugin(fn) {
  return (host, target) => {
    // custom logic before the update
    fn(host, target);
  };
}

render: () => myPlugin(html`<div>...</div>`),
```

Simpler syntax via `.use()` (chainable — plugins apply in order):

```js
render: () => html`<div>...</div>`.use(myPlugin);
```

## html.resolve

```js
html.resolve(promise: Promise, placeholder: Function, delay = 200): Function
```

Renders `placeholder` (an update function) until the promise resolves or rejects; `delay` is the ms threshold before the placeholder appears.

```js
html`
  <div>
    ${html.resolve(
      promise.then((value) => html`<div>${value}</div>`),
      html`Loading...`,
    )}
  </div>
`;
```

## html.transition

A built-in plugin using the View Transitions API. Works best with whole-viewport transitions (app-style navigation). Attach to a single, always-connected element (the app root):

```js
render: ({ stack }) => html`
  <header>...</header>
  <main>${stack}</main>
`.use(html.transition);
```

Triggers only when the element using `html.transition` updates (e.g., when `stack` changes) — internal changes inside `stack` do not trigger it. Customizable via CSS `::view-transition-*` selectors; the layout engine's `view` rule sets `view-transition-name` (e.g., `layout="view:card"`).

## Limitations

### Table family elements

`<table>`, `<caption>`, `<thead>`, `<tbody>`, `<tfoot>`, `<tr>`, `<th>`, `<td>`, `<colgroup>` with expressions must not contain additional non-whitespace text:

```js
// Breaks template
html`<tr>${cellOne} ${cellTwo} some text</tr>`;

// Works fine
html`<tr>${cellOne} ${cellTwo}</tr>`;
```

### template element

Expressions inside a `<template>` element are not supported — keep its content static:

```js
html`
  <custom-element>
    <template>
      <div class="my-static-class"></div>
    </template>
    <div>${content}</div>
  </custom-element>
`;
```

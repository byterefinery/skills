# Template Engine

## Table of Contents

- [html Tagged Template](#html-tagged-template)
- [svg Tagged Template](#svg-tagged-template)
- [Template Methods](#template-methods)
- [Template Helpers](#template-helpers)
- [Expression Resolution](#expression-resolution)
- [Caching and Compilation](#caching-and-compilation)
- [Style Handling](#style-handling)
- [Localization in Templates](#localization-in-templates)

---

## html Tagged Template

The primary way to create templates in Hybrids:

```js
import { html } from "hybrids";

html`
  <div class="${active ? 'active' : ''}">
    <h1>${title}</h1>
    <p>${description}</p>
    <button onclick="${handler}">Click</button>
  </div>
`;
```

### How It Works

1. Template literal parts are joined into a unique ID (string signature)
2. On first use, the template is compiled into a DOM fragment with marker nodes
3. Each expression position is tracked; only changed expressions update on re-render
4. The compiled update function is cached by ID

### Expression Types

Expressions (values inside `${}`) are resolved differently based on type:

| Type | Behavior |
|---|---|
| `string` / `number` / `boolean` | Text content or attribute value |
| `null` / `undefined` | Empty string (attributes removed) |
| `HTMLElement` / `DocumentFragment` | Inserted as DOM nodes |
| `UpdateFunction` (from `html\`...\``) | Nested template, called with `(host, target)` |
| `Function` | Used as event handler (bound to the attribute) |
| `Array` | Flattened — each item resolved recursively |

### Property vs Attribute

For element bindings, Hybrids auto-detects whether to use a property or attribute:

```js
html`<input value="${text}"/>`
// → input.value = text  (property, because 'value' is a known property)

html`<div data-id="${id}"/>`
// → div.setAttribute('data-id', id)  (attribute)
```

In SVG context, all bindings use `setAttribute` (SVG elements don't have standard DOM properties).

---

## svg Tagged Template

Create SVG content:

```js
import { svg } from "hybrids";

svg`
  <svg viewBox="0 0 100 100">
    <circle cx="${cx}" cy="${cy}" r="${radius}" fill="${color}"/>
  </svg>
`;
```

- All attribute bindings use `setAttribute` (no property detection)
- Namespace is correctly set to SVG
- Mixed with HTML via `html` templates:

```js
html`
  <div>
    ${svg`<svg>...</svg>`}
  </div>
`;
```

---

## Template Methods

Chain methods on template results to attach metadata:

### .key(id)

Provide a stable key for list items. Helps the template engine track items across re-renders:

```js
items.map(item => html`
  <li>${item.name}</li>
`.key(item.id))
```

### .style(...styles)

Attach CSS styles to the template. Styles are applied via `adoptedStyleSheets` (Shadow DOM) or a `<style>` element (light DOM):

```js
html`<div class="item">...</div>`.style(`
  .item { color: red; }
`)

// Multiple styles
html`...`.style(css1, css2, css3)

// CSSStyleSheet instances
html`...`.style(new CSSStyleSheet())
```

Styles are deduplicated — identical style strings are not re-applied.

### .css`...`

Template literal version of `.style()` — supports interpolation:

```js
html`<div>...</div>`.css`
  .item { padding: ${padding}px; margin: ${margin}px; }
`
```

### .use(plugin)

Apply a plugin function that wraps the update function:

```js
function loggingPlugin(updateFn) {
  return function(host, target) {
    console.log('rendering');
    return updateFn(host, target);
  };
}

html`<div>...</div>`.use(loggingPlugin)
```

Plugins are composable — multiple `.use()` calls chain:

```js
html`...`.use(pluginA).use(pluginB)
// → pluginB(pluginA(originalUpdateFn))
```

---

## Template Helpers

### html.set(property, valueOrPath)

Create event handlers that bind form input values to host properties:

```js
// Bind to host property
html`<input oninput="${html.set('name')}"/>`

// Set a fixed value
html`<button onclick="${html.set('status', 'clicked')}">Click</button>`

// Bind to store model property
html`<input oninput="${html.set(user, 'firstName')}"/>`

// Clear store model
html`<button onclick="${html.set(user, null)}">Reset</button>`
```

Handles different input types:

| Input Type | Value Extracted |
|---|---|
| text, password, email, etc. | `event.target.value` |
| checkbox, radio | `event.target.checked && event.target.value` |
| file | `event.target.files` |
| custom event with `detail.value` | `event.detail.value` |

### html.resolve(promise, placeholder, delay)

Render a placeholder while a promise resolves:

```js
html.resolve(
  fetchUser(id),
  html`<span>Loading...</span>`,  // placeholder template
  200                              // delay (ms) before showing placeholder
)
```

- If the promise resolves within the delay, the placeholder is never shown
- After resolution, the result replaces the placeholder
- The placeholder is shown immediately if the delay elapses

### html.transition(template)

Wrap a template update in the View Transitions API (`document.startViewTransition()`):

```js
html.transition(html`<div>${content}</div>`)
```

- Only active in browsers that support `document.startViewTransition`
- If a transition is already in progress, the update is queued
- Sets `router-transition` attribute on `<html>` during navigation transitions

---

## Expression Resolution

### Text Nodes

In text contexts, expressions become text content:

```js
html`Hello ${name}!`  // → text node with "Hello John!"
```

### Attributes

In attribute contexts, expressions set the attribute value:

```js
html`<div title="${tooltip}"/>`  // → div.setAttribute('title', tooltip)
```

Multiple expressions in one attribute are concatenated:

```js
html`<div class="${base} ${modifier}"/>`
// → div.className = `${base} ${modifier}`
```

### Event Handlers

Function expressions on event attributes are used as handlers:

```js
html`<button onclick="${() => doSomething()}">Click</button>`
```

### DOM Insertion

Elements and fragments are inserted directly:

```js
html`<div>${childElement}</div>`
```

---

## Caching and Compilation

Templates are compiled once and cached:

1. **Compilation** — the template literal is parsed into a DOM fragment with comment/text markers at expression positions
2. **Caching** — the compiled update function is stored in a `Map` keyed by the template string signature
3. **Re-use** — identical template strings share the same compiled function
4. **Update** — on re-render, only changed expression positions are updated

The compilation process:

1. Create a `<template>` element with the HTML content
2. Walk the fragment, replacing expression placeholders with marker nodes
3. Record the position and resolver function for each marker
4. Return an update function that applies values to markers

---

## Style Handling

### Shadow DOM (adoptedStyleSheets)

When the template uses Shadow DOM, styles are applied via `adoptedStyleSheets`:

```js
html`<div>...</div>`.style(`.item { color: red; }`)
// → shadowRoot.adoptedStyleSheets = [CSSStyleSheet]
```

- `CSSStyleSheet` instances are cached and reused
- Existing styles from the shadow root are preserved

### Light DOM (<style> element)

In light DOM, a `<style>` element is created and appended:

```js
html`<div>...</div>`.style(`.item { color: red; }`)
// → <style>.item { color: red; }</style> appended to the host
```

- The style element is reused across re-renders
- Styles are joined with `/*------*/` separator

### Style Deduplication

Identical style strings are not re-applied — the engine tracks previous styles and skips no-op updates.

---

## Localization in Templates

When `localize()` is configured, text content in templates is automatically translated:

```js
localize("pl", {
  "Hello ${0}!": { message: "Witaj ${0}!" },
});

html`<div>Hello ${name}!</div>`
// → In Polish: <div>Witaj John!</div>
```

### How It Works

1. Text nodes are normalized (whitespace trimmed, multiple spaces collapsed)
2. The text is used as a lookup key in the translation dictionary
3. If a translation is found, it replaces the text
4. Expression placeholders (`${0}`, `${1}`) are preserved and re-inserted

### Context Hints

Use HTML comments for disambiguation:

```html
<!-- | button label -->
Submit
```

The comment `<!-- | context -->` before text provides a context hint for translation lookups.

### Disabling Translation

Use `translate="no"` on an element to skip translation for it and its children:

```js
html`<div translate="no"><code>const x = 1;</code></div>`
```

Script and style elements are automatically excluded from translation.

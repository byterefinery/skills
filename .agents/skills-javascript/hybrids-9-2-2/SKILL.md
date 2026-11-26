---
name: hybrids-9-2-2
description: Hybrids 9.2.2 — a JavaScript framework for building web applications, UI component libraries, and single Web Components with a mixed declarative and functional architecture. Use when defining components as plain objects compiled to custom elements, building reactive UIs with html/svg tagged templates (promises are supported directly in content expressions), managing global state with store (models, external storage, offline caching, relations, drafts, validation, store.observe), configuring graph-based app routing with router (views, stacks, dialogs, guards, nested routers, programmatic router.navigate), applying inline CSS layouts with the layout engine, or localizing templates with localize/msg. Covers define/from/compile, mount, parent/children factories, html.set/resolve/transition helpers, template methods (key/style/css/use), and the hybrids CLI message extractor.
license: MIT
---

# hybrids 9.2.2

## Overview

Hybrids is a JavaScript framework for creating web applications, UI component libraries, and single Web Components. It uses a **mixed declarative and functional architecture** — components are defined as plain objects with pure functions, but compile to native Web Components (Custom Elements) under the hood.

Unlike class-based frameworks, Hybrids components are **plain objects** where each property is a descriptor: a primitive/function value, or a full descriptor with `value`, `connect` (lifecycle), `observe` (reactive callback), and `reflect` (attribute mirroring). The `render` property returns an update function that drives the template engine.

The framework ships with five integrated subsystems:

1. **Component Model** — plain-object definitions compiled to Custom Elements
2. **Template Engine** — `html`/`svg` tagged template literals with compiled caching
3. **Store** — declarative global state with external storage, offline caching, relations, drafts, and validation
4. **Router** — graph-based view routing with stacks, dialogs, guards, nested routers, and programmatic `router.navigate()`
5. **Layout Engine** — inline CSS layout rules in templates (flexbox, grid, spacing, alignment, responsive breakpoints)

Plus **localization** (`localize`/`msg`) and utility factories (`parent`, `children`, `mount`, `dispatch`).

### Architecture Highlights

- **Reactive caching** — property values are recalculated only when accessed and a dependency changed; changes propagate via the cache/emitter mechanism
- **Immutable data** — the cache compares values with strict equality (`nextValue !== lastValue`), so models and state should use immutable updates
- **No virtual DOM** — templates compile to DOM fragments; updates target only changed expressions
- **Shadow DOM optional** — auto-created when the root template contains `<style>`, `<link rel="stylesheet">`, `css`/`style` helpers, or `<slot>`; force with the `shadow` option
- **Zero build step** — ESM imports work directly in all modern browsers without transpilation

## Usage

### Installation

```bash
npm i hybrids
```

Or without a bundler via CDN (`https://esm.sh/hybrids@^9`, skypack, or unpkg) inside `<script type="module">`. Hot Module Replacement works out of the box — opt your entry module in with `if (import.meta.hot) import.meta.hot.accept();`.

### Defining Components

Components are plain objects with a required `tag` (dashed custom element name) and a `render` property:

```js
import { define } from "hybrids";

export default define({
  tag: "simple-counter",
  count: 0,
  increaseCount: (host) => { host.count += 1; },
  render: ({ count, increaseCount }) => html`
    <button onclick="${increaseCount}">Count: ${count}</button>
  `,
});
```

`define()` returns the passed definition, so the short export form above lets other modules import it (testing, references). For many components, `define.from(components, { prefix?, root? })` injects tag names from file paths (Vite `import.meta.glob`), letting modules export bare definitions without `tag`. `define.compile(component)` returns an unregistered constructor for libraries where the consumer chooses the tag.

Use as `<simple-counter count="42"></simple-counter>`; attributes provide initial values only (attribute changes are not watched).

### Property Descriptors

Properties can be shorthand values or full descriptors:

```js
define({
  tag: "my-element",

  // Shorthand — primitives are writable, typed from the default
  name: "",
  age: 0,
  active: false,

  // Computed — 1-arg function is read-only
  greeting: ({ name }) => `Hello, ${name}!`,

  // Writable computed — 2-arg function (getter only; value cached until access)
  data: (host, value) => (value ? JSON.parse(value) : null),

  // Full descriptor
  status: {
    value: "idle",
    reflect: true, // mirror to dash-cased attribute (or a transform fn)
    connect(host, key, invalidate) {
      // runs when the element connects; return a cleanup fn
      const t = setInterval(invalidate, 1000);
      return () => clearInterval(t);
    },
    observe(host, value, lastValue) {
      // side effects on change; called async first time when connected
    },
  },
});
```

Notes:

- Object defaults require the full descriptor: `data: { value: ["a", "b"] }` (the default object is frozen at compile time)
- `fn.length` detects the setter — default/rest parameters break writable detection
- `connect` runs on connect, returned fn on disconnect; `invalidate` forces recalculation (for external libraries/async sources)

### Render and Shadow DOM

```js
// Light DOM by default; auto Shadow DOM if the root template has styles or <slot>
render: ({ name }) => html`<h1>Hello ${name}!</h1>`,

// Explicit control
render: {
  value: (host) => html`...`,
  shadow: { mode: "open", delegatesFocus: true }, // or true / false
},
```

- Only the **root** template decides implicit Shadow DOM; nested templates with styles do not — force `shadow: true` in those cases
- `render` can be referenced by other properties to access the element's internals: `input: ({ render }) => render().querySelector("#input")`

### Template Engine

`html` and `svg` are tagged template literals returning update functions (cached by signature):

```js
import { html, svg } from "hybrids";

html`
  <div class="${active ? "active" : ""}">
    <h1>${title}</h1>
    <button onclick="${handler}">Click</button>
  </div>
`;

// The <svg> container itself must be created with html; svg`...` is for inner structure
html`<svg viewBox="0 0 300 100">${svg`<circle cx="50" cy="50" r="${radius}" />`}</svg>`;
```

Attribute expressions set the matching property, the camelCased property, or fall back to the raw attribute (useful for read-only DOM properties like `form`/`list`); mixed values concatenate into a string. `class` accepts a string/array/boolean map; `style` must be an object. Event listeners: `on*` attributes add the listener with the host as first callback argument; custom options go on the function's `.options` property.

**Promises in content (new in 9.2):** an expression may return a Promise directly — previous content stays in place until resolution, the resolved value renders by normal content rules, and rejections are not handled (chain `.catch()`). Use `html.resolve(promise, placeholder, delay = 200)` for a pending placeholder.

Content rules: primitives → `textContent` (falsy except `0` renders nothing), functions → nested templates, Node instances attach, arrays iterate. Use `.key(id)` on array items for identity-based reordering.

### Template Methods

```js
html`<li>${item}</li>`
  .key(item.id)                    // identity for list reordering
  .css`div { color: ${color}; }`   // CSS in tagged literal (interpolatable)
  .style(stringsOrSheets)          // CSS strings or CSSStyleSheet instances
  .use(pluginFn)                   // wrap the update function (chainable)
```

`.css`/`.style` use Constructable Stylesheets when supported (shared across instances); otherwise `<style>` elements.

### Template Helpers

```js
// Bind form inputs to host properties
html`<input oninput="${html.set("name")}"/>`

// Custom value (second argument overrides event.target.value)
html`<button onclick="${html.set("selected", item)}">select</button>`

// Store model instance + dot-path; null deletes the model
html`<input value="${user.firstName}" oninput="${html.set(user, "firstName")}"/>`
html`<button onclick="${html.set(user, null)}">Delete</button>`

// Placeholder while a promise is pending (delay defaults to 200ms)
html`<div>${html.resolve(promise, html`Loading...`)}</div>`

// View Transitions API — attach once, ideally on the app root element
render: ({ stack }) => html`...`.use(html.transition)
```

`html.set` for form elements: checkboxes/radios use `checked`, file inputs use `files`, otherwise `event.detail.value` if defined, else `target.value` (see references for full API).

### Parent & Children

```js
import { define, html, parent, children } from "hybrids";

define({
  tag: "my-element",
  ref: parent(MyParent),                    // nearest matching ancestor (crosses Shadow DOM)
  items: children(TabItem),                 // direct light-DOM children
  all: children(TabItem, { deep: true }),   // recursive; nested: true adds matched children' children
});
```

Both accept a component definition or a predicate function `(component, host) => boolean` for complex/self-reference conditions. Relations update reactively on connect/disconnect and subtree changes; parent property changes invalidate dependent child properties.

### Mount

Attach a definition to an existing element without registering a custom element — the typical full-page setup:

```js
import { mount, html, router } from "hybrids";

mount(document.body, {
  stack: router(Home),
  render: ({ stack }) => html`<template layout="column">${stack}</template>`,
});
```

### Dispatch

```js
import { html, dispatch } from "hybrids";

function increaseCount(host) {
  host.value += 1;
  dispatch(host, "custom-change", { detail: host.value }); // bubbles/cancelable/composed all default false
}
```

### Debug Mode

```js
import { debug } from "hybrids";

if (import.meta.env.DEV) debug(); // run before any other code; enables logging (router, store errors)
```

## Gotchas

- **Attributes set initial values only** — attribute changes are not watched; update via the property (`el.firstName = "George"`). Boolean attributes follow the HTML standard: attribute present (even empty) is `true`, so default such properties to `false`
- **One-arg functions are read-only properties** — `fn(host)` has no setter; `fn(host, value)` is writable but runs only on access (getter semantics). Default/rest parameters break the `fn.length` writable detection
- **Object defaults need the full descriptor** — object-instance defaults must be `data: { value: [...] }`, and the default object is frozen at compile time
- **Only the root template decides Shadow DOM implicitly** — styles or `<slot>` in a nested template do not create a Shadow DOM; set `shadow: true` explicitly (`shadow: false` disables it even with styles/slots present)
- **Promises in content reject silently** — the engine does not handle rejected promises; chain `.catch()` and render an error state. In 9.2 a Promise is a valid content expression directly, but a pending promise keeps the previous content in place
- **Table family elements** (`<tr>`, `<td>`, `<table>`, …) with expressions must contain only whitespace between expressions — extra text breaks the template; expressions are not supported inside `<template>` elements
- **`store.get()` is synchronous, `store.set()` is async, both always return an object** — instance, placeholder, or promise; guard async models with `store.ready()`/`pending()`/`error()` before reading properties
- **`store.set(model, null)` deletes** — resolves with an errored placeholder, not `undefined`; partial values merge (no full-instance resends)
- **Draft mode is memory-based and ephemeral** — `store(User, { draft: true })` returns a copy deleted when the component disconnects; commit with `store.submit(draft, extraValues?)`
- **`store.sync()` bypasses storage** — use only for server-pushed updates (WebSocket, extension messages)
- **Guard functions must be synchronous** — no `host` argument; for async setup (session fetch), conditionally render the app element only after the data is ready
- **Only one root router may be connected** — a second root router in the document throws; use nested `router()` inside views for complex layouts
- **`router.url()` returns `""` for unconnected views** (no throw); `router.navigate()` **throws** if the root router is not connected, the view is not part of the router, or it is called while a `navigate` event dispatches — reserve `navigate` for non-user-initiated navigation; user actions stay accessible via `href`/`action`
- **`submit` events do not cross the Shadow DOM boundary** — render app root templates in light DOM if the router should intercept form submissions; `router.resolve(event, promise)` navigates only on resolution (URL still comes from the event target)
- **`replace: true` reloads the view from scratch** — default in-stack navigation reuses the instance and updates parameters
- **Listing cache is not invalidated by nested model changes by default** — set `{ loose: true }` on nested model arrays (or storage `loose`) when list results depend on item state
- **Layout attributes accept no expressions** — resolved at compile time; use compound selectors (`layout[disabled]`, `layout.show`, pseudo-classes) for conditional rules
- **Template translation is compile-time** — `localize()` must run before the first render of a template; template text does not support dynamic language switching, plural forms, or HTML content (use `msg`/`msg.html` for those); avoid `msg` for static text (re-translated every update) and `msg.html`/`msg.svg` sanitize nothing (XSS vector)
- **`store.observe()` fires only on updates after registration** — not for already-existing instances

## References

- [01-component-model](references/01-component-model.md) — define/from/compile, mount, property descriptors, attributes, render/shadow, factories, parent/children, dispatch
- [02-template-engine](references/02-template-engine.md) — html/svg templates, attributes & events, values, promises, iteration, styling, plugins, html.set/resolve/transition, limitations
- [03-store](references/03-store.md) — model definitions, validation, nested structures, storage configuration, factory, direct methods, drafts, guards
- [04-router](references/04-router.md) — factory & options, view configuration (stack/url/dialog/multiple/replace/guard), URL methods, navigate/resolve/active, nested routers
- [05-layout-engine](references/05-layout-engine.md) — layout attributes, compound selectors, media queries, dimensions, CSS variables, full rule tables
- [06-localization](references/06-localization.md) — template translation, keys & context, msg/msg.html, localize formats, chrome.i18n, CLI extraction

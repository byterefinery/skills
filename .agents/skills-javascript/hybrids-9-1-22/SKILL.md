---
name: hybrids-9-1-22
description: Hybrids 9.1.22 — a JavaScript framework for building web applications and custom elements with a unique mixed declarative and functional architecture. Use when creating Web Components via plain objects and pure functions, building reactive UIs with html/svg template literals, managing global state with store (models, external storage, offline caching, relations, drafts, validation), configuring app-like graph-based routing with router (views, stacks, dialogs, guards, nested routers, URL params), applying inline CSS layouts with the layout engine (flexbox, grid, spacing, alignment, responsive breakpoints), or localizing content with localize/msg (translation dictionaries, plural forms, dynamic messages, chrome.i18n format). Covers define, mount, parent/children factories, html helpers (set, resolve, transition), template methods (key, style, css, use), and the hybrids CLI for message extraction.
---

# hybrids 9.1.22

## Overview

Hybrids is a JavaScript framework for creating web applications, UI component libraries, and single Web Components. It uses a unique **mixed declarative and functional architecture** — components are defined as plain objects with pure functions, but compile to native Web Components (Custom Elements) under the hood.

Unlike class-based frameworks, Hybrids components are **plain objects** where each property is a descriptor with a `value` (default or factory function), optional `connect` (lifecycle subscription), `observe` (reactive callback), and `reflect` (attribute mirroring). The `render` property returns an update function that drives the template engine.

The framework ships with five integrated subsystems:

1. **Component Model** — plain-object definitions compiled to Custom Elements
2. **Template Engine** — `html`/`svg` tagged template literals with compiled caching
3. **Store** — declarative global state with external storage, offline caching, relations, drafts, and validation
4. **Router** — graph-based view routing with stacks, dialogs, guards, and nested routers
5. **Layout Engine** — inline CSS layout rules in templates (flexbox, grid, spacing, alignment)

Plus **localization** (`localize`/`msg`) and utility factories (`parent`, `children`, `mount`, `dispatch`).

### Architecture Highlights

- **Reactive caching** — computed values are memoized with dependency tracking; changes propagate automatically via the emitter queue (microtask-based)
- **No virtual DOM** — templates compile to DOM fragments with marker nodes; updates target only changed expressions
- **Shadow DOM optional** — `render` descriptor's `shadow` option controls encapsulation; light DOM is the default
- **Zero build step** — works with ESM imports directly; no transpilation needed

## Usage

### Installation

```js
import { define, html, store, router, localize } from "hybrids";
```

Via CDN:

```html
<script type="module">
import { define, html } from "https://cdn.jsdelivr.net/gh/hybridsjs/hybrids@v9.1.22/src/index.js";
</script>
```

### Defining Components

Components are plain objects with a required `tag` (dashed custom element name) and optional properties:

```js
const Counter = define({
  tag: "simple-counter",
  count: 0,                    // writable property, default 0
  step: 1,                     // readable-only (no setter, pure default)

  // Function properties are computed (reactive)
  doubled: ({ count }) => count * 2,

  // Event handler (pure function, receives host)
  increase: (host) => { host.count += host.step; },

  // Render returns an update function
  render: ({ count, increase }) => html`
    <button onclick="${increase}">Count: ${count}</button>
  `,
});
```

Use as `<simple-counter count="42"></simple-counter>`. Attributes auto-coerce to the property's type (string, number, boolean).

### Property Descriptors

Properties can be simple values or full descriptors:

```js
define({
  tag: "my-element",

  // Simple defaults (auto-typed from value)
  name: "",           // string
  age: 0,             // number
  active: false,      // boolean

  // Full descriptor
  status: {
    value: "idle",
    reflect: true,                    // mirror to attribute
    connect(host, key, invalidate) {  // lifecycle
      const interval = setInterval(() => invalidate(), 1000);
      return () => clearInterval(interval);
    },
    observe(host, value, lastValue) { // reactive callback
      console.log(`${lastValue} → ${value}`);
    },
  },

  // Computed (function = read-only)
  greeting: ({ name }) => `Hello, ${name}!`,
});
```

- `reflect: true` mirrors property changes to the HTML attribute (camelCase → kebab-case)
- `reflect: fn` transforms the value before reflecting
- `connect` runs when the element connects to DOM; return a cleanup function
- `observe` fires on every property change (after recomputation)

### Render and Shadow DOM

The `render` property controls how content is rendered:

```js
define({
  tag: "my-element",

  // Light DOM (default)
  render: (host) => html`<p>Light DOM content</p>`,

  // Shadow DOM with options
  render: {
    value: (host) => html`<p>Shadow DOM content</p>`,
    shadow: { mode: "open", delegatesFocus: true },
  },

  // Explicit light DOM (no auto Shadow DOM)
  render: {
    value: (host) => html`<p>No shadow</p>`,
    shadow: false,
  },
});
```

Shadow DOM is auto-created when templates contain `<style>`, `<slot>`, or `<link rel="stylesheet">`.

### Template Engine

`html` and `svg` are tagged template literals that compile to cached update functions:

```js
import { html, svg } from "hybrids";

// HTML template
html`
  <div class="${active ? 'active' : ''}">
    <h1>${title}</h1>
    <button onclick="${handler}">Click</button>
  </div>
`;

// SVG template
svg`
  <circle cx="${cx}" cy="${cy}" r="${radius}" fill="${color}"/>
`;
```

Templates are compiled once and cached by their string signature. Expressions are resolved only when dependencies change.

### Template Methods

Attach metadata to templates via chained methods:

```js
// Stable key for list reordering
html`<li>${item}</li>`.key(item.id)

// Inline styles (adoptedStyleSheets or <style> element)
html`<div>...</div>`.style(`li { color: red; }`)

// CSS template literal (interpolated)
html`<div>...</div>`.css`
  .item { padding: ${padding}px; }
`

// Plugin (transform the update function)
html`<div>...</div>`.use(pluginFn)
```

### Template Helpers

#### `html.set`

Bind form input values to host properties:

```js
html`
  <input oninput="${html.set('name')}"/>
  <input type="checkbox" onchange="${html.set('active')}"/>
`
```

With store model instances and dot-path:

```js
html`
  <input oninput="${html.set(user, 'firstName')}"/>
`
```

#### `html.resolve`

Render a placeholder while a promise resolves:

```js
html.resolve(
  fetchData(),
  html`<span>Loading...</span>`,  // placeholder
  200                              // delay before showing placeholder (ms)
)
```

#### `html.transition`

Wrap a template in `document.startViewTransition()`:

```js
html.transition(html`<div>${content}</div>`)
```

### Parent and Children Factories

Access related components in the DOM tree:

```js
import { define, html, parent, children } from "hybrids";

const Card = define({ tag: "card-item", title: "", render: ({ title }) => html`<div>${title}</div>` });
const List = define({ tag: "card-list",

  // Find closest parent component
  app: parent(AppComponent),

  // Find child components (hybrids definition or predicate function)
  items: children(Card, { deep: true, nested: false }),

  render: ({ items }) => html`<ul>${items.map(item => html`<li>${item.title}</li>`)}</ul>`,
});
```

- `parent(Component)` — finds the nearest ancestor matching the component definition
- `parent(fn)` — uses a predicate function on component definitions
- `children(Component, options)` — returns array of matching descendants
- `options.deep` — search recursively through DOM tree
- `options.nested` — also recurse into found children

Both use `MutationObserver` for reactive updates when DOM changes.

### Mount

Mount a component definition onto an existing DOM element (without defining a custom element):

```js
import { mount, html } from "hybrids";

const el = document.getElementById("root");
const cleanup = mount(el, {
  count: 0,
  render: ({ count }) => html`<button onclick="${() => el.count++}">${count}</button>`,
});

// Later: cleanup() to disconnect
```

### Dispatch

Fire custom events:

```js
import { dispatch } from "hybrids";

dispatch(host, "item-selected", { bubbles: true, detail: { id: 1 } });
```

### Debug Mode

Enable debug logging for router navigation:

```js
import { debug } from "hybrids";
debug();
```

## Gotchas

- **`tag` is required and must be dashed** — `define()` throws if `tag` is missing or not kebab-case (e.g., `"my-element"`, not `"myElement"`)
- **Tag names must be unique** — defining the same tag twice throws. Hybrids supports HMR by reusing the custom element constructor when the tag already exists
- **Function properties are read-only** — a property defined as a function (e.g., `computed: (host) => ...`) has no setter. Only primitive defaults (string/number/boolean) and object/function values with explicit setters are writable
- **`reflect` is not supported on `render`** — the render descriptor cannot use the `reflect` option
- **`<slot>` requires explicit Shadow DOM** — using `<slot>` in a template without `shadow` option throws an error
- **Store model access in pending state throws** — accessing properties of a model instance before it's loaded throws. Always guard with `store.pending()`, `store.error()`, or `store.ready()`
- **`store.connect` is a Symbol** — use `store.connect` (the exported symbol) as the key for storage configuration, not a string
- **Layout attributes cannot contain expressions** — `layout="column gap:2"` works; `layout="column gap:\${size}"` throws
- **`html.set` with store models requires the second argument** — `html.set(modelInstance, 'propertyPath')` — omitting the path throws
- **Router views must be `define()`d first** — a component must pass through `define()` before being used in `router()` factory
- **Nested routers: at most one per view** — a view can have at most one property that is a nested router
- **Dialog views cannot have `url` or `stack` options** — dialogs are modal overlays; routing configuration is incompatible
- **`localize` function argument for remote translation** — pass a function (not a string) when integrating with external translation services like `chrome.i18n`

## References

- [01-component-model](references/01-component-model.md) — define, property descriptors, render, mount, parent/children
- [02-template-engine](references/02-template-engine.md) — html/svg tagged templates, methods (key/style/css/use), helpers (set/resolve/transition)
- [03-store](references/03-store.md) — model definitions, storage, guards, drafts, validation, relations, offline caching
- [04-router](references/04-router.md) — view routing, stacks, dialogs, guards, URL params, nested routers, transition
- [05-layout-engine](references/05-layout-engine.md) — inline CSS layout rules, flexbox, grid, spacing, alignment, responsive queries
- [06-localization](references/06-localization.md) — localize, msg, plural forms, chrome.i18n format, CLI extraction

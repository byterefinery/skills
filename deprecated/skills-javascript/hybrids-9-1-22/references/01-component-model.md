# Component Model

## Table of Contents

- [define()](#define)
- [Property Descriptors](#property-descriptors)
- [Render Descriptor](#render-descriptor)
- [define.compile()](#definecompile)
- [define.from()](#definefrom)
- [mount()](#mount)
- [parent()](#parent)
- [children()](#children)
- [dispatch()](#dispatch)
- [debug()](#debug)
- [Lifecycle](#lifecycle)

---

## define()

The core function for creating Hybrids components. Takes a plain object and compiles it into a native Custom Element.

```js
import { define } from "hybrids";

const MyComponent = define({
  tag: "my-component",
  // properties...
  render: (host) => html`...`,
});

// Returns the same object (frozen), registered as a custom element
```

### Requirements

- `tag` is mandatory — must be a valid dashed custom element name (e.g., `"my-element"`)
- Tag must be unique across the document — defining the same tag twice throws `TypeError`
- During HMR, re-defining the same tag updates all existing instances

### Property Types

Properties in the definition object can be:

| Form | Writable | Behavior |
|---|---|---|
| Primitive (`""`, `0`, `false`) | Yes | Auto-typed from default value |
| Object/array | Yes | Direct value, frozen default |
| Function `(host) => value` | No (read-only) | Computed, reactive |
| Descriptor `{ value, ... }` | Depends | Full control |

### Attribute Binding

HTML attributes automatically coerce to the property type:

```html
<my-component count="42" active></my-component>
```

- `count="42"` → `Number` (because default is `0`)
- `active` (boolean attribute, empty string) → `true` (because default is `false`)
- Attribute names are camelCased (`my-count` → `myCount`)

---

## Property Descriptors

Full descriptor objects provide lifecycle hooks and reflection:

```js
{
  value: defaultValue | (host, value) => computedValue,
  connect?(host, key, invalidate): void | (() => void),
  observe?(host, value, lastValue): void,
  reflect?: boolean | ((value) => string),
}
```

### value

- **Primitive** — sets the default and type coercion
- **Function** — computed value; receives `(host, assertedValue)`. If the function takes only one argument, it's read-only (no setter)

```js
// Read-only computed
fullName: ({ firstName, lastName }) => `${firstName} ${lastName}`,

// Writable with factory
items: () => [],  // each instance gets its own array
```

### connect

Runs when the element's `connectedCallback` fires. Receives:

- `host` — the element instance
- `key` — the property name (as a string)
- `invalidate` — function to trigger re-computation

Return a cleanup function called on `disconnectedCallback`.

```js
connect(host, key, invalidate) {
  const subscription = api.subscribe(() => invalidate());
  return () => subscription.unsubscribe();
}
```

### observe

Called after every property change (including initial). Receives `(host, value, lastValue)`. Use for side effects that depend on the property value.

```js
observe(host, value, lastValue) {
  if (value !== lastValue) {
    console.log(`${lastValue} → ${value}`);
  }
}
```

### reflect

Mirrors property changes back to the HTML attribute (camelCase → kebab-case):

```js
// Boolean reflect
active: { value: true, reflect: true },

// Custom transform
status: { value: "idle", reflect: (v) => v.toUpperCase() },
```

---

## Render Descriptor

The `render` property is special — it controls how the component renders its content:

```js
render: (host) => html`<p>Content</p>`,
```

Or as a full descriptor:

```js
render: {
  value: (host) => html`<p>Content</p>`,
  shadow: true | false | { mode: "open" | "closed", delegatesFocus: boolean },
  connect: ...,
  observe: ...,
}
```

### shadow Option

| Value | Behavior |
|---|---|
| `undefined` (default) | Auto — creates shadow root if template uses `<style>`, `<slot>`, or `<link rel="stylesheet">` |
| `true` | Always use Shadow DOM (`{ mode: "open" }`) |
| `{ mode, delegatesFocus }` | Explicit ShadowRootInit options |
| `false` | Never use Shadow DOM (light DOM only) |

### Render Target

The update function receives `(host, target)`:

- **Light DOM**: `target` is the host element itself
- **Shadow DOM**: `target` is the shadow root

---

## define.compile()

Compile a component definition without registering it as a custom element. Returns the `HybridElement` constructor class:

```js
import { define } from "hybrids";

const Constructor = define.compile({
  tag: "my-element",
  render: () => html`<p>Hello</p>`,
});

// Manually register or use with mount()
customElements.define("my-element", Constructor);
```

### define.from()

Batch-register components from an import map or module glob:

```js
import { define } from "hybrids";

define.from(
  {
    "./components/button": Button,
    "./components/input": Input,
  },
  {
    prefix: "app",      // → app-button, app-input
    root: "./components",
  }
);
```

Tags are auto-generated from file paths when not explicitly set.

---

## mount()

Mount a component definition onto an existing DOM element without defining a custom element:

```js
import { mount, html } from "hybrids";

const el = document.getElementById("app");

const cleanup = mount(el, {
  count: 0,
  render: () => html`<button onclick="${() => el.count++}">${el.count}</button>`,
});

// Later:
cleanup();
```

- The target element becomes the component host
- Returns a cleanup function that calls `disconnectedCallback` and removes descriptors
- Re-mounting with a new definition updates the element in place

---

## parent()

Find the nearest ancestor component:

```js
import { parent } from "hybrids";

define({
  tag: "child-element",
  app: parent(AppComponent),       // by component definition
  wrapper: parent((h) => h.tag.startsWith("wrapper")),  // by predicate
  render: ({ app, wrapper }) => html`...`,
});
```

- Walks up the DOM tree (including across shadow boundaries)
- Returns the element or `null`
- Reactively updates when the parent changes (via DOM mutations)

---

## children()

Find descendant components:

```js
import { children } from "hybrids";

define({
  tag: "parent-element",
  items: children(ItemComponent),
  deepItems: children(ItemComponent, { deep: true }),
  allItems: children(ItemComponent, { deep: true, nested: true }),
  render: ({ items }) => html`<ul>${items.map(item => html`<li>${item.name}</li>`)}</ul>`,
});
```

### Options

| Option | Default | Description |
|---|---|---|
| `deep` | `false` | Search recursively through the DOM tree |
| `nested` | `false` | Also recurse into found children (for nested component trees) |

- Uses `MutationObserver` for reactive updates
- Returns a plain array of element instances

---

## dispatch()

Fire a custom event from an element:

```js
import { dispatch } from "hybrids";

dispatch(host, "item-selected", {
  bubbles: true,
  detail: { id: 1, name: "test" },
});
```

Default: `bubbles: false`. Pass any `CustomEventInit` options.

---

## debug()

Enable debug mode for router navigation logging:

```js
import { debug } from "hybrids";
debug();
```

When enabled, the router logs navigation entries to the console with parameters. Each navigation is also accessible via `$$1`, `$$2`, etc. global variables.

---

## Lifecycle

### connectedCallback

1. All writable properties are initialized from attributes or defaults
2. All `connect` functions are queued via the emitter
3. Connect cleanup functions are tracked for disconnection

### disconnectedCallback

1. All connect cleanup functions are called
2. All cache entries for the instance are invalidated

### Property Change

1. `cache.assert()` marks the property as dirty
2. Dependent computed properties are queued for re-computation
3. The emitter runs all queued functions in a microtask
4. `observe` callbacks fire with `(host, newValue, lastValue)`

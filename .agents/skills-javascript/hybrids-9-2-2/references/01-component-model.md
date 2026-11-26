# Component Model

## Table of Contents

- [define](#define)
- [define.from](#definefrom)
- [define.compile](#definecompile)
- [Constructor access](#constructor-access)
- [Mount](#mount)
- [Cache & change detection](#cache--change-detection)
- [Attributes](#attributes)
- [Property descriptor](#property-descriptor)
- [Render](#render)
- [Factories](#factories)
- [Parent & children](#parent--children)
- [dispatch](#dispatch)

---

## define

```js
define(component: object & { tag: string }): component
```

- `component` — a map of property descriptors plus the `tag` property
- Returns the passed definition object unchanged

Recommended file structure — `define()` returns the definition, so modules can export it directly for testing/references:

```js
import { define } from "hybrids";

export default define({
  tag: "my-element",
  // ...
});
```

## define.from

```js
define.from(components: object, options?: { prefix?: string; root?: string | string[] }): components
```

Targets app setup with a bundler (e.g., Vite). Keys are tag names or file paths (slashes → dashes, extension removed, camelCase → dash-case). The `tag` key is injected dynamically when not set, so component modules can skip `tag` and export the bare definition.

```js
// ./components/HelloWorld.js
import { html } from "hybrids";

export default {
  render: () => html`<div>Hello World!</div>`,
};

// ./app.js (entry point)
import { define } from "hybrids";

define.from(
  import.meta.glob("./components/*.js", { eager: true, import: "default" }),
  { root: "components" },
);
```

Options:

- `prefix` — prefix added to tag names
- `root` — string or list of strings removed from tag names

## define.compile

```js
define.compile(component: object): HTMLElement
```

Produces the custom element **constructor without registering it** (component definition without `tag`). Useful for component libraries where the consumer chooses the tag:

```js
// Package
export default define.compile({
  name: "",
  render: ({ name }) => html`<div>Hello ${name}!</div>`,
});

// Consumer
import { MyElement } from "components-library";

customElements.define("my-super-element", MyElement);
```

## Constructor access

Once defined, get the constructor from the Custom Elements registry:

```js
import component from "./my-element.js";

const MyElement = customElements.get(component.tag);
const el = new MyElement();
```

## Mount

```js
mount(target: HTMLElement, component: object): void
```

Attaches a definition to an existing DOM element instead of defining a custom element — the typical full-page setup where a root custom element is not wanted. All framework features (router, layout engine, store) work with mounted components:

```js
import { mount, html, router } from "hybrids";

import Home from "./views/home.js";

mount(document.body, {
  stack: router(Home),
  render: ({ stack }) => html`
    <template layout="column">
      ${stack}
    </template>
  `,
});
```

## Cache & change detection

- The cache tracks dependencies between properties (even across different custom elements) and notifies about changes
- A property is recalculated **only when accessed and a dependency changed**; a property with no dependencies is computed once and the cached value is always returned
- A property is accessed automatically only if it is observed (descriptor `observe`) or is a dependency of an observed property
- Equality is a strict check (`nextValue !== lastValue`) — **use immutable data**
- If synchronous updates compensate and the final value equals the previous one, `observe` is not called

## Attributes

Writable properties read their initial value from the corresponding dash-cased attribute at creation time:

```html
<my-element first-name="Mark" last-name="Twain"></my-element>
```

- **Attribute changes are not watched** — set the property instead:

```js
const el = document.getElementsByTagName("my-element")[0];
el.firstName = "George"; // then el.getAttribute("first-name") reflects it
```

- **Booleans follow the HTML standard** — an existing attribute (even empty) is `true`; to allow `false`, do not set the attribute at all. For on/off switches, default the property to `false`:

```html
<my-element on></my-element>  <!-- on: true -->
```

- Templates can set `false` explicitly via expression regardless of the default:

```js
html`<my-element mySwitch="${false}"></my-element>`;
```

## Property descriptor

Reserved keys: `tag` (tag name string) and `render` (render function).

Shorthand values are translated to `{ value: ... }` descriptors.

```js
{
  property: {
    value:
      | string | boolean | number
      | object | undefined | null
      | (host) => { ... }
      | (host, value) => { ... };
    connect?: (host, key, invalidate) => () => { ... };
    observe?: (host, value, lastValue) => { ... };
    reflect?: boolean | (value) => string;
  },
}
```

### value

**Primitives & objects** — creates a writable property with the default value. For primitives, the type is protected with conversion on set. Object-instance defaults require the full descriptor:

```js
define({
  tag: "my-element",
  data: { value: ["a", "b", "c"] },
});
```

The default object is **frozen** during compilation; use a computed function returning a new object if external libraries need mutable objects.

**Functions** — creates a getter, plus a setter only when the function has two arguments:

```js
// Read-only (1 arg)
fullName: ({ firstName, lastName }) => `${firstName} ${lastName}`,

// Writable (2 args) — getter only semantics; assigned value is kept in cache until next access
data: (host, value) => (value ? JSON.parse(value) : null),
```

`fn.length` is used to detect the argument count, so default and rest parameters break writable detection:

```js
// won't work (fn.length === 1)
data: (host, value = "[]") => JSON.parse(value);

// will work
data: (host, value) => {
  value = value ?? "[]";
  return JSON.parse(value);
},
```

### connect

```js
connect: (host, key, invalidate) => () => { ... }
```

Called on `connectedCallback`; the returned function is the disconnect cleanup called on `disconnectedCallback` (element insert, remove, or relocate in the DOM). Use `invalidate` to tell the cache that the property value should be recalculated (e.g., when an external library or async source changes):

```js
name: {
  value: () => api.get("some-external-value"),
  connect(host, key, invalidate) {
    const value = host[key];
    const subscription = api.subscribe(invalidate);
    return () => subscription.unsubscribe();
  },
},
```

### observe

```js
observe: (host, value, lastValue) => { ... }
```

Side effects on property change. Called asynchronously the first time when the element is connected, then on every change. Skipped when compensating synchronous updates leave the value unchanged.

### reflect

```js
reflect: boolean | (value) => string
```

Mirrors the property value back to the dash-cased attribute (or passes it through a transform). Useful for CSS selectors like `:host([is-admin])` in the Shadow DOM:

```js
isAdmin: { value: false, reflect: true },
render: () => html`...`.css`:host([is-admin]) { background: yellow; }`,
```

## Render

`render` is reserved for the element's structure. `value` must be a function returning a template result. It follows the `observe` pattern (called automatically when dependencies change) and can be invoked manually via `el.render()`.

**Rendering mode** — without the `shadow` option, the mode is determined from the **root template structure only**: styles (`<style>`, `<link rel="stylesheet">`, `css`/`style` helpers) or `<slot>` elements force Shadow DOM. Nested templates never influence this — use `shadow: true` explicitly:

```js
// Disable Shadow DOM even with styles/slots
render: { value: (host) => html`...`.css`...`, shadow: false },

// Force Shadow DOM
render: { value: (host) => html`...`, shadow: true },

// Pass attachShadow options
render: { value: () => html`<div>...</div>`, shadow: { mode: "closed", delegatesFocus: true } },
```

**Reference internals** — DOM updates are asynchronous; use the property as a reference to avoid timing issues. A property depending on `render` that is read before the first update triggers the update manually:

```js
define({
  tag: "my-element",
  input: ({ render }) => render().querySelector("#input"),
  render: () => html`<input id="input" />`,
});
```

**connect & observe on render** — use the full descriptor with `value` to hook element connect/disconnect and re-render side effects.

## Factories

A factory is a function producing a property descriptor — hides implementation details and parameterizes shared behavior:

```js
function myCustomProperty(multiplier) {
  return {
    value: (host, value = 0) => value * multiplier,
  };
}

define({
  tag: "my-element",
  count: myCustomProperty(2),
});
```

Built-in factories: `parent`, `children`, `store`, `router`.

## Parent & children

Relations work only between custom elements defined by the library (not built-in or foreign custom elements).

### parent

```js
parent(componentOrFn: Object | (component, host) => boolean): descriptor
```

Resolves to `null` or the nearest ancestor element instance up to `document.body`, crossing Shadow DOM boundaries. Updates on connect/disconnect. Parent property changes invalidate dependent properties in the child:

```js
define({
  tag: "my-element",
  ref: parent(MyParent),
  render: ({ ref }) => html`count: ${ref.count}`,
});
```

### children

```js
children(componentOrFn, [options: { deep?: boolean; nested?: boolean }]): descriptor
```

Resolves to an array of light-DOM child elements. Without options: direct children only. `deep: true` traverses the subtree; `nested: true` (requires `deep`) adds matched elements' own matched children. Invalidates when the subtree changes:

```js
define({
  tag: "tab-group",
  tabs: children(TabItem),
  active: ({ tabs }) => tabs.find((tab) => tab.active),
});
```

### Complex conditions

Pass a predicate function for self-references or structural checks:

```js
const MyElement = define({
  tag: "my-element",
  parent: parent((component) => component === MyElement),
  items: children((component) => component.hasOwnProperty("value")),
});
```

## dispatch

```js
dispatch(host: Element, eventType: string, [options]): boolean
```

Creates and dispatches a `CustomEvent` on the host element. Options: `bubbles`, `cancelable`, `composed` (all default `false`) and `detail`. Returns `false` when the event is cancelable and a handler called `preventDefault()`.

```js
function increaseCount(host) {
  host.value += 1;
  dispatch(host, "custom-change", { detail: host.value });
}
```

Consumers listen with `oncustom-change="${callback}"` in templates or `addEventListener` on the element instance.

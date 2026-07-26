# Slots Reference

## Overview

The plugin supports default and named slots through `x-slot` on child `<template>` elements inside the host element. Slot content is projected into the shadow root where matching `<slot>` elements exist in the component template.

## How it works

1. The plugin scans the host element for direct children matching `template[x-slot]`
2. For each slot template, it clones `template.content` (a `DocumentFragment`)
3. For named slots, each element child gets `slot="<name>"` attribute set
4. The fragment is inserted after the `<template>` element (inside the host, before shadow rendering)
5. `Alpine.initTree()` is called on projected elements so Alpine directives work
6. On re-render or cleanup, projected nodes are destroyed and removed

## Default slot

Use `x-slot` without a value for the default (unnamed) slot:

```html
<div x-component="'card'">
  <template x-slot>
    <p>This goes into <slot></slot> in the template</p>
  </template>
</div>

<template id="card">
  <article>
    <slot></slot>
  </article>
</template>
```

## Named slots

Use `x-slot="name"` to target a named `<slot name="name">`:

```html
<div x-component="'card'">
  <template x-slot="header">
    <h2>Card Title</h2>
  </template>

  <template x-slot>
    <p>Default content</p>
  </template>

  <template x-slot="actions">
    <button>Edit</button>
    <button>Delete</button>
  </template>
</div>

<template id="card">
  <article>
    <header><slot name="header"></slot></header>
    <div><slot></slot></div>
    <footer><slot name="actions"></slot></footer>
  </article>
</template>
```

## Multiple slot templates

Multiple `<template x-slot>` elements with the same name are all projected. Their content is appended in document order:

```html
<div x-component="'list'">
  <template x-slot>
    <li>Item 1</li>
  </template>
  <template x-slot>
    <li>Item 2</li>
  </template>
</div>
```

## Alpine directives in slot content

Projected slot content is initialized with `Alpine.initTree()`, so Alpine directives work inside slots:

```html
<div x-data="{ open: false }">
  <div x-component="'dropdown'">
    <template x-slot>
      <button x-on:click="open = !open">Toggle</button>
      <div x-show="open">Dropdown content</div>
    </template>
  </div>
</div>
```

The slot content accesses the host element's Alpine scope (and ancestors).

## Dynamic slots with `x-for`

Generate slot content from loops:

```html
<div x-data="{ items: ['A', 'B', 'C'] }">
  <div x-component="'list'">
    <template x-for="item in items" :key="item">
      <template x-slot>
        <li x-text="item"></li>
      </template>
    </template>
  </div>
</div>
```

## Slot projection mechanics

The projection process:

1. `clearProjectedSlots()` — destroys and removes previously projected nodes
2. Query `:scope > template[x-slot]` — finds direct child templates
3. For each template:
   - Read `x-slot` attribute value (empty string = default slot)
   - Clone `template.content`
   - If named slot, set `slot="<name>"` on each element child
   - Insert fragment after the template element via `template.after(fragment)`
4. Call `Alpine.initTree()` on each projected element
5. Store references in `hostElement._x_componentSlots` for later cleanup

### Cleanup

On re-render or component destruction:
- Each projected node is checked: if it's an element, `Alpine.destroyTree()` is called
- The node is removed from the DOM
- `_x_componentSlots` is reset to an empty array

## Gotchas

- **`x-slot` must be on `<template>` elements** — plain elements with `x-slot` are ignored. The plugin queries specifically for `template[x-slot]`.
- **Slot content is inserted as direct children** — the projected nodes sit as direct children of the host element (between the host's start tag and the shadow root). They are not inside the shadow DOM.
- **Named slots set `slot` attribute on elements** — only element nodes get the `slot` attribute. Text nodes inside slot templates are projected but won't match named slots; wrap content in elements for named slots.
- **Slot templates are consumed, not preserved** — the original `<template x-slot>` elements remain in the DOM, but their content is cloned and inserted. The templates act as declarations.

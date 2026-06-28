---
name: alpinejs-3-15-12
description: Alpine.js 3.15.12 — a minimal, directive-based reactive UI framework for HTML. Use when building interactive components with x-data, x-bind, x-on, x-model, x-for, x-show, x-transition, x-if, x-teleport, and related directives. Covers all official plugins (mask, intersect, resize, persist, focus, collapse, anchor, morph, sort), the UI plugin (dialog, menu, tabs, listbox, combobox, popover, switch, radio, disclosure), CSP build, reactivity model, and extension APIs (custom directives, magics, Alpine.data, Alpine.store).
---

# alpinejs 3.15.12

## Overview

Alpine.js is a rugged, minimal tool for composing JavaScript behavior directly in HTML markup using declarative directives. It uses Vue's reactivity engine under the hood but exposes only a small surface area: directives (`x-*`), magic properties (`$*`), and the `Alpine.*` global API.

Core philosophy: keep logic close to markup, avoid build steps, and compose small reactive components without a virtual DOM. Alpine is not a full SPA framework — it augments existing HTML/server-rendered pages with interactivity.

### Key Concepts

Alpine is a collection of **15 attributes**, **6 properties**, and **2 methods**. There are no build steps, no virtual DOM, no component files — just HTML with reactive behavior.

Reactivity is powered by `@vue/reactivity` under the hood (`Alpine.reactive()` and `Alpine.effect()`).

### 15 Attributes

| Attribute | Description |
|---|---|
| `x-data` | Declare a new Alpine component and its reactive data scope |
| `x-bind` | Dynamically set HTML attributes (`:` shorthand) |
| `x-on` | Listen for browser events (`@` shorthand) |
| `x-text` | Set the text content of an element |
| `x-html` | Set the inner HTML of an element (trusted content only) |
| `x-model` | Two-way bind data to form inputs |
| `x-show` | Toggle element visibility (`display: none`) |
| `x-transition` | Animate elements in/out with CSS transitions (requires `x-show`) |
| `x-for` | Repeat a block of HTML over a data set (on `<template>`) |
| `x-if` | Conditionally add/remove elements from DOM (on `<template>`) |
| `x-init` | Run code when an element is initialized |
| `x-effect` | Re-run code when any referenced reactive dependency changes |
| `x-ref` | Register element reference accessible via `$refs` |
| `x-cloak` | Hide element until Alpine finishes initializing (requires CSS) |
| `x-ignore` | Prevent Alpine from initializing an element and its children |

Additional directives: `x-modelable` (expose property for parent `x-model`), `x-teleport` (move content to another DOM location), `x-id` (scoped ID groups for `$id()`).

### 6 Properties (Magics)

| Property | Description |
|---|---|
| `$store` | Access global stores registered via `Alpine.store()` |
| `$el` | Reference the current DOM element |
| `$dispatch` | Dispatch a custom browser event from the current element |
| `$watch` | Watch a data property and run a callback on change |
| `$refs` | Reference elements by key (set with `x-ref`) |
| `$nextTick` | Wait until after Alpine's reactive DOM updates to run code |

Additional magics: `$root` (closest `x-data` ancestor), `$data` (current scope as plain object), `$id` (generate unique IDs).

### 2 Methods

| Method | Description |
|---|---|
| `Alpine.data()` | Register reusable component definitions, referenced via `x-data="name"` |
| `Alpine.store()` | Declare global reactive data accessible from any component via `$store` |

Additional globals: `Alpine.bind()` (reusable directive objects), `Alpine.directive()` / `Alpine.magic()` (extension APIs), `Alpine.plugin()` (register plugins), `Alpine.morph()` (patch DOM preserving state).

## Usage

### Installation

Via CDN (simplest):

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.12/dist/cdn.min.js"></script>
```

Via NPM:

```js
import Alpine from 'alpinejs'
window.Alpine = Alpine
Alpine.start()
```

### Minimal Component

```html
<div x-data="{ count: 0 }">
  <button @click="count++">Increment</button>
  <span x-text="count"></span>
</div>
```

### Reusable Component

```js
document.addEventListener('alpine:init', () => {
  Alpine.data('dropdown', () => ({
    open: false,
    toggle() { this.open = !this.open }
  }))
})
```

```html
<div x-data="dropdown">
  <button @click="toggle">Toggle</button>
  <div x-show="open" x-transition>Content</div>
</div>
```

### Plugin Registration

Plugins must load BEFORE Alpine core (CDN) or register before `Alpine.start()` (NPM):

```js
import Alpine from 'alpinejs'
import collapse from '@alpinejs/collapse'
import focus from '@alpinejs/focus'
import anchor from '@alpinejs/anchor'

Alpine.plugin(collapse)
Alpine.plugin(focus)
Alpine.plugin(anchor)
Alpine.start()
```

## Gotchas

- **`defer` is required** on the `<script>` tag — Alpine must initialize after the DOM is parsed. Without `defer`, directives won't work.
- **`x-data` is required** as an ancestor for most directives. Directives without a parent `x-data` won't evaluate. Use bare `x-data` (no expression) for data-less components.
- **`x-for` and `x-if` must be on `<template>` elements**, not directly on the target element. The template must contain exactly one root child.
- **`x-show` uses `display: none`** — if CSS `!important` overrides it, use `x-show.important`.
- **`x-transition` only works with `x-show`**, not `x-if`. Use `x-show` + `x-transition` instead of `x-if` when animations are needed.
- **`$el` is the current element**, not the component root. Use `$root` for the closest `x-data` element.
- **`x-ref` values are static only** — dynamic `:x-ref="expr"` does not work in V3.
- **`x-init` auto-calls `init()`** methods on `x-data` objects. Don't manually call `init()` in `x-init`.
- **`$persist` with `Alpine.data` requires a regular function** (not arrow function) so `this` context is available.
- **`x-cloak` requires CSS**: `[x-cloak] { display: none !important; }` — without it, the directive does nothing.
- **Plugin script order matters** for CDN: plugins must load BEFORE Alpine core.
- **`Alpine.start()` must be called exactly once** when using NPM imports. Calling it multiple times creates duplicate Alpine instances.
- **CSP build** (`@alpinejs/csp`) does not support arrow functions, template literals, spread operator, destructuring, or global variable access in inline expressions. Extract complex logic into `Alpine.data()` components.
- **`x-model` on checkboxes bound to arrays** auto-manages push/pop. Single checkboxes bind to booleans by default.
- **`x-trap` (Focus plugin)** was previously called "Trap" — the directive name is `x-trap`, not `x-focus`.
- **`x-anchor` applies `position: absolute` by default**. Use `.fixed` modifier for fixed positioning, but be aware that transformed ancestors create new containing blocks.
- **`Alpine.morph()` preserves Alpine state** during DOM updates — it does not destroy/recreate components. Use `key` attributes on list items to preserve them across morphs.
- **`x-sort` uses SortableJS internally** — overwriting `handle`, `group`, `filter`, `onSort`, `onStart`, or `onEnd` in `x-sort:config` may break functionality.
- **UI plugin components use `x-bind` internally** via `Alpine.bind()` — they compose directives programmatically. The `x-modelable` pattern enables parent-child state binding.
- **`$dispatch` events bubble** — use `.window` modifier on listeners to catch events from sibling components.
- **`x-teleport` forwards events** registered on the `<template>` element itself, not on teleported children.

## References

- [01-essentials](references/01-essentials.md) — Installation, state management, events, lifecycle hooks
- [02-directives](references/02-directives.md) — All directives: x-data, x-init, x-show, x-bind, x-on, x-text, x-html, x-model, x-modelable, x-for, x-transition, x-effect, x-ignore, x-ref, x-cloak, x-teleport, x-if, x-id
- [03-magics](references/03-magics.md) — Magic properties: $el, $refs, $store, $watch, $dispatch, $nextTick, $root, $data, $id
- [04-globals](references/04-globals.md) — Alpine.data(), Alpine.store(), Alpine.bind(), global lifecycle events
- [05-plugins](references/05-plugins.md) — Official plugins: mask, intersect, resize, persist, focus, collapse, anchor, morph, sort
- [06-ui-plugin](references/06-ui-plugin.md) — UI plugin: dialog, menu, tabs, listbox, combobox, popover, switch, radio, disclosure
- [07-advanced](references/07-advanced.md) — CSP build, reactivity model, extending Alpine, async support, V2 migration

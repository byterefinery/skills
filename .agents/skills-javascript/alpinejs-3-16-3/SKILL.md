---
name: alpinejs-3-16-3
description: >
  Alpine.js 3.16.3 — rugged, minimal JavaScript framework for building reactive components directly in HTML with no build step. Covers core directives (x-data, x-on, x-model, x-bind, x-for, x-if, x-show, x-teleport, x-transition), $-magics, Alpine.data/store/bind globals, custom directives and magics, and all official plugins — anchor, collapse, csp, focus, history, intersect, mask, morph, navigate, persist, resize, sort, ui. Use when adding interactivity to server-rendered pages, building dropdowns, modals, forms, input masks, or sortable lists, or when working with @alpinejs packages or Livewire-style morphing.
license: MIT
compatibility: >
  Modern browsers (IntersectionObserver, ResizeObserver, Proxy). No build step required; optional npm/ESM integration.
  Official plugins ship as separate @alpinejs/* packages.
metadata:
  tags:
    - javascript
    - frontend
    - framework
    - reactivity
    - alpinejs
---

# alpinejs 3.16.3

## Overview

Alpine.js is a rugged, minimal JavaScript framework: instead of a JS compiler or component system, you sprinkle reactive directives (`x-*`), magics (`$*`), and a handful of global APIs directly into HTML. It is built on Vue's reactivity engine (`@vue/reactivity`) but needs no build step — a single `<script defer>` tag is a full app. Alpine 3 targets "server-rendered HTML plus just enough JS" (Rails, Laravel, Livewire, static sites).

The core package is `alpinejs`; the official plugins are separate `@alpinejs/*` packages from the same monorepo: `anchor`, `collapse`, `csp`, `focus`, `history`, `intersect`, `mask`, `morph`, `navigate`, `persist`, `resize`, `sort`, and `ui` (headless UI components).

### API surface at a glance

- **Directives** — `x-data`, `x-on`/`@`, `x-bind`/`:`, `x-model`, `x-for`, `x-if`, `x-show`, `x-text`, `x-html`, `x-transition`, `x-teleport`, `x-modelable`, `x-effect`, `x-init`, `x-id`, `x-ref`, `x-ignore`, `x-cloak`
- **Magics** — `$el`, `$root`, `$data`, `$refs`, `$id`, `$store`, `$watch`, `$dispatch`, `$nextTick`
- **Globals** — `Alpine.data()`, `Alpine.store()`, `Alpine.bind()`, `Alpine.directive()`, `Alpine.magic()`, `Alpine.plugin()`, `Alpine.start()`, `Alpine.version`, `Alpine.reactive()`, `Alpine.effect()`, `Alpine.walk()`, `Alpine.entangle()`

## Usage

### Installation

**CDN** — pin the version for production stability; `defer` is required:

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.16.3/dist/cdn.min.js"></script>
```

**Module** — register extensions between import and `Alpine.start()`, and call `start()` exactly once:

```js
import Alpine from 'alpinejs'
import morph from '@alpinejs/morph'

Alpine.plugin(morph)          // plugins, Alpine.data/store/bind go here
window.Alpine = Alpine        // optional, handy for devtools
Alpine.start()
```

CDN plugin scripts load **before** the core (both `defer`), or inside an `alpine:init` listener. Details in [01-installation](references/01-installation.md).

### Minimal component

```html
<div x-data="{ open: false, count: 0 }">
    <button @click="open = ! open">Toggle</button>
    <div x-show="open" x-transition>Content...</div>
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

`x-data` is the component root and is required (even bare `x-data`) for most other directives to work. Child `x-data` inherits parent scope; nested same-named properties shadow outward. Inside `x-data` object literals, reference siblings with `this.`; in directive expressions, bare names.

### Reusable data and global state

```js
// script tag: inside alpine:init; module: before Alpine.start()
Alpine.data('dropdown', () => ({
    open: false,
    toggle() { this.open = ! this.open },
    init() { /* auto-called on component init */ }
}))
// markup: x-data="dropdown" or with params: x-data="dropdown(true)"

Alpine.store('cart', { items: [], add(i) { this.items.push(i) } })
// any scope: $store.cart.items, $store.cart.add(item)
// single values work too: Alpine.store('open', false) + $store.open = true
```

`Alpine.bind('name', () => ({ ':class': ..., '@click'() {...} }))` reuses whole `x-bind` objects: `x-bind="name"`. Full details in [03-magics-and-globals](references/03-magics-and-globals.md).

### Directives cheat sheet

| Directive | Purpose |
|---|---|
| `x-data="{...}"` | Reactive component root; also methods, getters, `init()` |
| `x-on:evt` / `@evt` | Event listeners; modifiers `.prevent .stop .self .once .window .document .outside .debounce .throttle .passive .capture .camel .dot`, keys `.enter .shift .ctrl .meta .cmd .alt .tab .escape .up .down .left .right`, mouse-modifier keys on click-family events |
| `x-bind:attr` / `:attr` | Bind attributes; `:class` supports object syntax and short-circuit; class bindings preserve existing classes |
| `x-model` | Two-way binding for text/textarea/checkbox/radio/select; modifiers `.lazy .change .blur .enter .number .boolean .debounce .throttle .fill .unintrusive` |
| `x-for` | Loops on `<template>` only; `item in list`, `(item, index) in list`, `i in 5`, `:key` required for reorder safety |
| `x-if` | Add/remove from DOM, on `<template>` only |
| `x-show` | Show/hide via `display: none` (element stays in DOM); `.important` forces CSS |
| `x-text` / `x-html` | Text content / innerHTML (XSS — trusted content only) |
| `x-transition` | Fade+scale on `x-show`; helpers `.duration .delay .scale.80 .origin.top .opacity` or class syntax `x-transition:enter(-start/-end)`, `:leave(-start/-end)` |
| `x-teleport="sel"` | Move a `<template>`'s content to a CSS selector target; forwards events registered on the template |
| `x-modelable` | Two-way bridge for custom inputs (JSON-safe values) |
| `x-effect` | Re-run expression when any data it reads changes |
| `x-init` | Run code on element init; works standalone outside `x-data` |
| `x-id` + `$id` | Namespaced unique IDs for repeatable components |
| `x-ref` + `$refs` | Named element handles (static only in v3) |
| `x-ignore` | Skip subtree during Alpine init |
| `x-cloak` | Hide until Alpine boots (needs `[x-cloak] { display: none !important; }` CSS) |

Modifier syntax details, examples, and `x-transition` class patterns are in [02-directives](references/02-directives.md).

### Lifecycle

- `x-init="code"` — runs when the element initializes (before first DOM update); supports `await`.
- `init()` method on `x-data` / `Alpine.data` objects — auto-called at component init.
- `alpine:init` event — fire point to register `Alpine.data/store/bind/directive/magic` **before** the core initializes.
- `alpine:initialized` event — fire point **after** init completes.
- `$watch('a.b', (val, oldVal) => ...)` and `x-effect` for reacting to state changes.

### Extending

```js
document.addEventListener('alpine:init', () => {
    Alpine.directive('uppercase', (el, { value, expression, modifiers },
        { Alpine, effect, cleanup, evaluate }) => { /* ... */ })
    Alpine.magic('now', () => () => Date.now())
})
```

`Alpine.plugin(fn)` (or an array of fns) is how every official plugin installs. Custom directive/magic patterns and the reactivity primitives (`Alpine.reactive`, `Alpine.effect`, `Alpine.transaction`) are in [04-advanced](references/04-advanced.md).

## Plugins

All plugins follow the same install pattern — CDN `<script defer>` **before** the core, or `Alpine.plugin(name)` before `Alpine.start()`:

- **`@alpinejs/anchor`** — `x-anchor="$refs.trigger"` positions elements with Floating UI (dropdowns, popovers, tooltips); `.top/.bottom/.left/.right` + `-start/-end`, `.offset.8`, `.fixed`
- **`@alpinejs/collapse`** — `x-collapse` animates height of `x-show` elements; `.duration.750ms`, `.min.100px`
- **`@alpinejs/csp`** — drop-in core build that does not violate `unsafe-eval` CSP; most inline expressions work
- **`@alpinejs/focus`** — `x-trap.noscroll="open"` traps Tab focus inside modals/dialogs (uses Tabbable)
- **`@alpinejs/history`** — binds `x-data` props to URL query strings (alpha, developed in the Livewire repo)
- **`@alpinejs/intersect`** — `x-intersect` / `:enter` / `:leave` on viewport intersection; `.once .half .full .threshold.N .margin`
- **`@alpinejs/mask`** — `x-mask="999-999"` literal masks; `x-mask:dynamic` with `$input`; `$money($input, '.', ',', 2)`
- **`@alpinejs/morph`** — `Alpine.morph(el, html, options)` patches DOM while preserving Alpine state, focus, and input values (Livewire/LiveView pattern); `Alpine.morphBetween(start, end, html)`
- **`@alpinejs/navigate`** — SPA-like navigation with history support (developed in the Livewire repo)
- **`@alpinejs/persist`** — `$persist(0)` wraps `x-data` values into localStorage; `.as('key')`, `.using(sessionStorage)`
- **`@alpinejs/resize`** — `x-resize="w = $width; h = $height"` via ResizeObserver; `.document`
- **`@alpinejs/sort`** — `x-sort` + `x-sort:item` drag-to-reorder (SortableJS); `x-sort:group`, `x-sort:handle`, `x-sort:ignore`, `$item`/`$position` handler
- **`@alpinejs/ui`** — headless UI kit: combobox, dialog, disclosure, listbox, menu, popover, radio, switch, tabs

Per-plugin directives, modifiers, and worked examples: [05-plugins](references/05-plugins.md) and [06-plugins-ui](references/06-plugins-ui.md).

## Gotchas

- **`x-data` is the component boundary** — most directives silently do nothing without an `x-data` ancestor (including bare `x-data` on the element itself).
- **`x-for` and `x-if` require `<template>`** — put them on the `<template>` tag, never on the repeated element. A `<template x-for>` must contain exactly **one** root element.
- **Always set `:key` on `x-for`** when items can be reordered, added, or removed — without keys Alpine mismatches DOM nodes and state leaks between iterations.
- **`x-transition` only works with `x-show`**, never with `x-if` (element removal has no transition).
- **`x-cloak` needs the CSS rule** `[x-cloak] { display: none !important; }` or it does nothing.
- **`$refs` only see statically-rendered elements** — `x-ref="item.name"` in a loop stores the literal string `'item.name'`, not the value (a v2→v3 regression). Use `$el`/query APIs or `x-model` for dynamic children.
- **Event names are lowercase** (HTML attributes are case-insensitive) — for camelCase custom events use `@my-event.camel`; for dotted event names use `@my-event.dot`.
- **`.outside` fires only while the element is visible** — clicking the toggle that opened it won't immediately close it via the same handler.
- **`$dispatch` bubbles** — sibling components can't see it unless they listen with `.window`. `$dispatch` returns whether the event was not canceled, enabling guard patterns.
- **`$watch` callback must not mutate the watched property** — you will create an infinite loop.
- **`x-model` ignores the input's `value` attribute** by default (the bound property wins); use `x-model.fill` to seed an empty property from the attribute.
- **`x-modelable` clones values as JSON** — `File`, `FileList`, `Date`, `Map`, `Set`, class instances, DOM nodes do not cross the boundary. For custom file inputs, dispatch instead: `@change="$dispatch('input', Array.from($event.target.files))"`.
- **`$persist` type changes stick** — localStorage keys are namespaced `_x_<prop>`; if a persisted property changes type (e.g. number → object), clear localStorage or rename the key or you'll get corruption on the next load.
- **`x-anchor` `.fixed` breaks under transformed ancestors** — any ancestor with `transform`, `filter`, `perspective`, `backdrop-filter`, `will-change`, or `contain` makes `position: fixed` behave like `absolute` relative to it.
- **`x-bind:class` object syntax drops original classes** — only the object's keys are kept (this is the trick for toggling classes set before Alpine loads); string/short-circuit syntax preserves existing classes.
- **Call `Alpine.start()` exactly once** — a second call boots a parallel Alpine instance.
- **Extension registration order matters** — `Alpine.data/store/bind/directive/magic` must be registered before init (`alpine:init` with CDN; between import and `start()` with modules).
- **`x-show` keeps the element in the DOM** (display:none); use `x-if` when hidden content must not exist (lazy content, unmounted state, avoiding tab order).
- **Morph preserves inputs by matching nodes** — keep stable structure and use the `key` attribute (or `options.key`) on repeated nodes, or inputs will lose focus/value across morphs.
- **CSP build rejects eval-style syntax** — no function construction via `Function()`; extract complex logic into methods and keep inline expressions simple (see [04-advanced](references/04-advanced.md)).
- **`x-ignore` is a full subtree skip** — anything inside it is invisible to Alpine, including nested `x-data`.

## References

- [01-installation](references/01-installation.md) — CDN vs module install, version pinning, script order with plugins, CSP build
- [02-directives](references/02-directives.md) — every core directive with modifiers, examples, and transition patterns
- [03-magics-and-globals](references/03-magics-and-globals.md) — `$` magics, `Alpine.data/store/bind`, lifecycle events
- [04-advanced](references/04-advanced.md) — reactivity primitives, async/await in expressions, custom directives and magics
- [05-plugins](references/05-plugins.md) — anchor, collapse, focus, intersect, mask, morph, persist, resize, sort, csp, navigate, history
- [06-plugins-ui](references/06-plugins-ui.md) — `@alpinejs/ui` headless components (combobox, dialog, disclosure, listbox, menu, popover, radio, switch, tabs)

---
name: alpinejs-3-17-5
description: >
  Alpine.js 3.17.5 — rugged, minimal JavaScript framework for building reactive components
  directly in HTML with no build step. Covers core directives (x-data, x-on, x-bind, x-model,
  x-for, x-if, x-show, x-teleport, x-transition, x-modelable, x-ignore), $-magics,
  Alpine.data/store/bind globals, custom directives and magics, the CSP build, and official
  plugins — anchor, collapse, csp, focus, intersect, mask, morph, persist, resize, sort — plus
  the ui, history, and navigate packages. Use when adding interactivity to server-rendered
  pages, building dropdowns, modals, forms, input masks, or sortable lists, or when working
  with @alpinejs packages or Livewire-style morphing.
license: MIT
compatibility: >
  Modern browsers (IntersectionObserver, ResizeObserver, Proxy). No build step required;
  optional npm/ESM integration. Official plugins ship as separate @alpinejs/* packages.
metadata:
  tags:
    - javascript
    - frontend
    - framework
    - reactivity
    - alpinejs
---

# alpinejs 3.17.5

## Overview

Alpine.js is a rugged, minimal JavaScript framework: instead of a JS compiler or component system, you sprinkle reactive directives (`x-*`), magics (`$*`), and a handful of global APIs directly into HTML. It is built on Vue's reactivity engine (`Alpine.reactive` / `Alpine.effect` wrap `@vue/reactivity`) but needs no build step — a single `<script defer>` tag is a full app. It targets "server-rendered HTML plus just enough JS" (Rails, Laravel, Livewire, static sites).

The core package is `alpinejs`; official plugins are separate `@alpinejs/*` packages from the same monorepo, all at 3.17.5 (except `navigate` at 3.10.2 and `history` at 3.0.0-alpha.0).

### API surface at a glance

- **Directives** — `x-data`, `x-on`/`@`, `x-bind`/`:`, `x-model`, `x-for`, `x-if`, `x-show`, `x-text`, `x-html`, `x-transition`, `x-teleport`, `x-modelable`, `x-effect`, `x-init`, `x-id`, `x-ref`, `x-ignore`, `x-cloak`
- **Magics** — `$el`, `$root`, `$data`, `$refs`, `$id`, `$store`, `$watch`, `$dispatch`, `$nextTick`, `$event` (plus plugin-provided `$focus`, `$anchor`, `$input`, `$money`, `$width`, `$height`, `$item`, `$position`, `$persist`)
- **Globals** — `Alpine.data()`, `Alpine.store()`, `Alpine.bind()`, `Alpine.directive()`, `Alpine.magic()`, `Alpine.plugin()`, `Alpine.start()`, `Alpine.reactive()`, `Alpine.effect()`, `Alpine.morph()`, `Alpine.$persist`

## Usage

### Installation

**CDN** — `defer` is required; pin the version in production:

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.17.5/dist/cdn.min.js"></script>
```

**Module** — register plugins and extensions between import and `Alpine.start()`, and call `start()` exactly once per page:

```js
import Alpine from 'alpinejs'
import morph from '@alpinejs/morph'

Alpine.plugin(morph)          // plugins, Alpine.data/store/bind go here
window.Alpine = Alpine        // optional, handy for devtools
Alpine.start()
```

CDN plugin scripts load **before** the core (both `defer`), or register inside an `alpine:init` listener. Details in [01-installation](references/01-installation.md).

### Minimal component

```html
<div x-data="{ open: false, count: 0 }">
    <button @click="open = ! open">Toggle</button>
    <div x-show="open" x-transition>Content...</div>
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

`x-data` is the component root and is required (even bare `x-data`) for most other directives to work. Child `x-data` inherits the parent scope; a same-named child property shadows the parent. Inside the `x-data` object literal, reference sibling properties with `this.`; in directive expressions, use bare names. Methods and getters work in `x-data`; an `init()` method is auto-called.

### Reusable data and global state

```js
// script tag: inside alpine:init; module: before Alpine.start()
Alpine.data('dropdown', () => ({
    open: false,
    toggle() { this.open = ! this.open },
    init() { /* auto-called on component init */ },
    destroy() { /* auto-called before cleanup (e.g. inside x-if) */ }
}))
// markup: x-data="dropdown" or with params: x-data="dropdown(true)"

Alpine.store('cart', { items: [], add(i) { this.items.push(i) } })
// any scope: $store.cart.items, $store.cart.add(item)
// single values work too: Alpine.store('open', false) + $store.open = true
```

`Alpine.bind('name', () => ({ ':class'() {...}, '@click'() {...} }))` reuses whole `x-bind` objects: `x-bind="name"`. Full details in [03-magics-and-globals](references/03-magics-and-globals.md).

### Directives cheat sheet

| Directive | Purpose |
|---|---|
| `x-data="{...}"` | Reactive component root; also methods, getters, `init()`; bare `x-data` ok |
| `x-on:evt` / `@evt` | Event listeners; modifiers `.prevent .stop .self .once .window .document .outside .debounce[.Nms] .throttle[.Nms] .passive .passive.false .capture .camel .dot`, key modifiers `.enter .shift .ctrl .meta .cmd .alt .tab .escape .up .down .left .right .page-down ...` (any `KeyboardEvent.key` in kebab-case), mouse modifiers on click-family events |
| `x-bind:attr` / `:attr` | Bind attributes; `:class` supports object syntax and short-circuit; string/class bindings preserve existing classes |
| `x-model` | Two-way binding for text/textarea/checkbox/radio/select/range; modifiers `.lazy .change .blur .enter .number .boolean .debounce[.Nms] .throttle[.Nms] .fill`; event modifiers combine (e.g. `.blur.enter`) |
| `x-for` | Loops, on `<template>` only; `item in list`, `(item, index) in list`, `i in 5`; `:key` for reorder safety |
| `x-if` | Add/remove from DOM, on `<template>` only; no transitions |
| `x-show` | Show/hide via `display: none` (element stays in DOM); `.important` beats `!important` CSS |
| `x-text` / `x-html` | Text content / innerHTML (XSS — trusted content only) |
| `x-transition` | Fade+scale on `x-show`; helpers `.duration.Nms .delay.Nms .opacity .scale.N .origin.top...` or class syntax `x-transition:enter(-start/-end)`, `:leave(-start/-end)` |
| `x-teleport="sel"` | Move a `<template>`'s content to a CSS selector target; forwards events registered on the template |
| `x-modelable` | Expose component state to a parent's `x-model` (JSON-safe values only) |
| `x-effect` | Re-run expression when any data it reads changes |
| `x-init` | Run code on element init; works standalone outside `x-data`; supports `await` |
| `x-id` + `$id` | Namespaced unique IDs for repeatable components; `$id('name', key)` for keyed IDs |
| `x-ref` + `$refs` | Named element handles (static refs only in v3) |
| `x-ignore` | Skip an entire subtree during Alpine init |
| `x-cloak` | Hide until Alpine boots (needs `[x-cloak] { display: none !important; }` CSS) |

Modifier syntax, examples, and `x-transition` class patterns are in [02-directives](references/02-directives.md).

### Lifecycle

- `x-init="code"` — runs when the element initializes; `x-data`'s `init()` method runs **before** `x-init` when both are present.
- `init()` / `destroy()` methods on `x-data` / `Alpine.data` objects — auto-called at component init / cleanup.
- `alpine:init` event — register `Alpine.data/store/bind/directive/magic/plugin` **before** the core initializes (CDN usage).
- `alpine:initialized` event — code to run **after** init completes.
- `$watch('a.b', (val, oldVal) => ...)` and `x-effect` for reacting to state changes.

### Extending

```js
document.addEventListener('alpine:init', () => {
    Alpine.directive('uppercase', (el, { value, expression, modifiers },
        { Alpine, effect, cleanup, evaluate }) => { /* ... */ })
    Alpine.magic('now', () => () => Date.now())
})
```

`Alpine.plugin(fn)` (or an array of fns) is how every official plugin installs. Custom directive/magic signatures and the reactivity primitives are in [04-advanced](references/04-advanced.md).

## Plugins

All plugins follow the same install pattern — CDN `<script defer>` **before** the core, or `Alpine.plugin(name)` before `Alpine.start()`:

- **`@alpinejs/anchor`** — `x-anchor="$refs.trigger"` positions elements with Floating UI (dropdowns, popovers, tooltips); `.top/.bottom/.left/.right` + `-start/-end`, `.offset.N`, `.fixed`, `.noflip`, `.no-style` + `$anchor` magic
- **`@alpinejs/collapse`** — `x-collapse` on an `x-show` element animates height on toggle; `.duration.Nms`, `.min.Npx`
- **`@alpinejs/csp`** — drop-in core build that does not violate `unsafe-eval` CSP; most inline expressions work, globals/advanced syntax do not
- **`@alpinejs/focus`** — `x-trap.inert.noscroll="open"` traps Tab focus inside modals (uses Tabbable); `.inert .noscroll .noreturn .noautofocus`; `$focus` magic chain (`.wrap().next()`, `.within(el).first()`, ...)
- **`@alpinejs/intersect`** — `x-intersect` / `:enter` / `:leave` on viewport intersection; `.once .half .full .threshold.N .margin ... .dwell[.Nms] .parent`
- **`@alpinejs/mask`** — `x-mask="99/99/9999"` literal masks (`* a 9` wildcards); `x-mask:dynamic` with `$input`; `$money($input, '.', ',', 4)`
- **`@alpinejs/morph`** — `Alpine.morph(el, html, options)` patches DOM while preserving Alpine state (Livewire/LiveView pattern); lifecycle hooks, `key(el)`, `lookahead`; `Alpine.morphBetween(start, end, html)`
- **`@alpinejs/persist`** — `$persist(0)` wraps `x-data` values into localStorage (key `_x_<prop>`); `.as('key')`, `.using(sessionStorage)`; `Alpine.$persist` global
- **`@alpinejs/resize`** — `x-resize="w = $width; h = $height"` via ResizeObserver; `.document`, `.viewport`
- **`@alpinejs/sort`** — `x-sort` + `x-sort:item` drag-to-reorder (SortableJS); `x-sort:group`, `x-sort:handle`, `x-sort:ignore`, `x-sort.ghost`, `x-sort:config`; `$item`/`$position` handler
- **`@alpinejs/ui`** — headless UI components with ARIA wiring, no styling of its own: combobox, dialog, disclosure, listbox, menu, popover, radio, switch, tabs; per-component directives, parts, and magics in [06-plugins-ui](references/06-plugins-ui.md)
- **`@alpinejs/navigate` / `@alpinejs/history`** — SPA-like navigation and query-string state (alpha; versions 3.10.2 / 3.0.0-alpha.0 in this tag)

Per-plugin directives, modifiers, and worked examples: [05-plugins](references/05-plugins.md).

## Gotchas

- **`x-data` is the component boundary** — most directives silently do nothing without an `x-data` ancestor (bare `x-data` on the element itself works).
- **`x-for` and `x-if` require `<template>`** — put them on the `<template>` tag, never on the repeated element. A `<template x-for>` must contain exactly **one** root element.
- **Set `:key` on `x-for`** when items can be reordered, added, or removed — without keys Alpine mismatches DOM nodes and state leaks between iterations.
- **`x-transition` only works with `x-show`**, never with `x-if` (element removal has no transition).
- **`x-cloak` needs the CSS rule** `[x-cloak] { display: none !important; }` or it does nothing.
- **`$refs` only see statically-rendered elements** — `x-ref="item.name"` in a loop stores the literal string `'item.name'`, not the value (v2→v3 change).
- **Event names are lowercase** (HTML attributes are case-insensitive) — camelCase custom events need `@my-event.camel`; dotted event names need `@my-event.dot`.
- **`.outside` fires only while the element is visible** — the click that opened the dropdown does not immediately close it via the same handler.
- **`$dispatch` bubbles** — sibling components can't see it unless they listen with `.window`. It returns whether the event was **not** canceled (guard pattern), and a third argument overrides options (e.g. `{ bubbles: false }`).
- **`$watch` callback must not mutate the watched property** — you will create an infinite loop. `$watch` fires lazily (no initial call) and receives `(value, oldValue)`; `x-effect` runs immediately and re-runs on any read dependency.
- **`x-model` ignores the input's `value` attribute** by default (the bound property wins); use `x-model.fill` to seed an empty property from the attribute. `.enter` does not prevent form submission.
- **`x-modelable` clones values as JSON** — `File`, `FileList`, `Date`, `Map`, `Set`, class instances, DOM nodes do not cross the boundary. For custom file inputs, dispatch instead: `@change="$dispatch('input', Array.from($event.target.files))"`.
- **`$persist` type changes stick** — keys are namespaced `_x_<prop>`; if a persisted property changes type (number → object), clear localStorage or rename the key.
- **`x-bind:class` object syntax does not preserve original classes** — only the object's keys are kept (that is the trick for toggling a class set before Alpine loads); string/short-circuit syntax preserves existing classes.
- **Call `Alpine.start()` exactly once per page** — a second call boots a parallel Alpine instance.
- **Extension registration order matters** — `Alpine.data/store/bind/directive/magic/plugin` must be registered before init (`alpine:init` listener with CDN; between import and `start()` with modules). CDN plugin scripts must appear **before** the core script.
- **`x-show` keeps the element in the DOM** (display:none); use `x-if` when hidden content must not exist (tab order, lazy state).
- **Morph preserves nodes by matching** — keep stable structure and use the `key` attribute (or `options.key`) on repeated nodes, or inputs lose focus/value across morphs.
- **CSP build rejects advanced inline syntax** — no arrow functions, template literals, destructuring, spread, or global references (`console`, `document`, `Math`, `parseInt`...); extract logic into methods or `Alpine.data` components.
- **`x-ignore` is a full subtree skip** — everything inside is invisible to Alpine, including nested `x-data`.
- **`x-anchor` `.fixed` breaks under transformed ancestors** — `transform`, `filter`, `perspective`, `backdrop-filter`, `will-change`, or `contain` on any ancestor makes `position: fixed` behave like `absolute` relative to it.
- **`Alpine.data` + `$persist` needs a standard function, not an arrow** — `Alpine.data('x', function () { return { open: this.$persist(false) } })`.
- **`x-init` order** — `x-data`'s `init()` method runs before the `x-init` directive on the same element.

## References

- [01-installation](references/01-installation.md) — CDN vs module install, version pinning, script order with plugins, CSP build
- [02-directives](references/02-directives.md) — every core directive with modifiers, examples, and transition patterns
- [03-magics-and-globals](references/03-magics-and-globals.md) — `$` magics, `Alpine.data/store/bind`, lifecycle events
- [04-advanced](references/04-advanced.md) — reactivity primitives, async/await in expressions, custom directives and magics, CSP build limits
- [05-plugins](references/05-plugins.md) — anchor, collapse, focus, intersect, mask, morph, persist, resize, sort
- [06-plugins-ui](references/06-plugins-ui.md) — `@alpinejs/ui` headless components (combobox, dialog, disclosure, listbox, menu, popover, radio, switch, tabs)

# Alpine.js 3.16.3 — Magics and Globals

## Magics

Magics are `$`-prefixed helpers available in every Alpine expression.

### `$el`

The current DOM node the expression is evaluated on:

```html
<button @click="$el.classList.add('active')">Toggle</button>
```

### `$root`

The nearest ancestor (or self) carrying `x-data` — the component root:

```html
<div x-data="{ open: false }">
    <span @click="$root.open = true">Open root's panel</span>
</div>
```

### `$data`

The live data object of the current scope (what `x-data` created), useful for passing scope to plain functions:

```html
<button @click="sayHello($data)">Say Hello</button>
<script>
function sayHello({ greeting, name }) { alert(greeting + ' ' + name) }
</script>
```

### `$refs`

Elements in the component marked with `x-ref="name"`. Static only in v3 — see `x-ref`.

### `$id`

Generate collision-free element IDs: `$id('text-input')` → `text-input-1`, next → `text-input-2`. Pair with `x-id` for grouped namespaces (labels + inputs).

### `$store`

Access global stores registered with `Alpine.store()`:

```html
<button x-data @click="$store.darkMode.toggle()">Toggle</button>
<span :class="$store.darkMode && 'dark'"></span>
```

Single-value stores work: `Alpine.store('open', false)` then `$store.open = ! $store.open`.

### `$watch`

Watch a property (dot notation allowed) for changes:

```html
<div x-data="{ open: false }" x-init="$watch('open', (value, oldValue) => console.log(value, oldValue))">
```

- Fires on every change, deep-watched automatically.
- Callback gets `(newValue, oldValue)`.
- Deep changes report the whole watched object (not the changed sub-property).
- **Never mutate the watched property from the callback** — infinite loop.

### `$dispatch`

Fire a (custom) DOM event, with optional payload in `event.detail`:

```html
<button @click="$dispatch('notify', { message: 'Hello' })">Notify</button>
<div x-data @notify="console.log($event.detail.message)">
```

- Wraps `el.dispatchEvent(new CustomEvent(...))`.
- **Returns a boolean**: `true` if the event was *not* canceled by any `preventDefault()` handler — enables guards: `@click="if ($dispatch('open-modal')) { open = true }"`.
- Third parameter overrides event options (e.g. `{ bubbles: false }`).
- Because events bubble to `window`, **sibling** components must listen with `.window`: `@notify.window="..."`. A parent listening for a child's event works normally.
- `$dispatch('input', value)` is the mechanism custom components use to feed `x-model` parents (see `x-modelable`).

### `$nextTick`

Run a callback after Alpine has flushed DOM updates from the current change:

```html
<button x-data @click="
    title = 'Hello World!';
    $nextTick(() => console.log($el.innerText));  // logs 'Hello World!'
" x-text="title"></button>
```

Also returns a promise — `await $nextTick()` inside async handlers.

## Globals

The `Alpine` global (CDN: automatic; module: `window.Alpine = Alpine`).

### `Alpine.data(name, callback)`

Register a reusable `x-data` provider. `callback` receives initial parameters and returns the data object:

```js
document.addEventListener('alpine:init', () => {
    Alpine.data('dropdown', (initialOpen = false) => ({
        open: initialOpen,
        toggle() { this.open = ! this.open },
        init() { /* auto-called */ }
    }))
})
```

```html
<div x-data="dropdown"></div>
<div x-data="dropdown(true)"></div>
```

### `Alpine.store(name, data)`

Global state available anywhere via `$store.name`:

```js
Alpine.store('darkMode', {
    init() { this.on = window.matchMedia('(prefers-color-scheme: dark)').matches },
    on: false,
    toggle() { this.on = ! this.on },
})
```

- `init()` runs right after registration.
- Read or write from any component: `$store.darkMode.on = true`.
- Externally: `Alpine.store('darkMode').toggle()` (omit the second argument to fetch a registered store).
- Any value is a valid store (booleans, arrays, objects).

### `Alpine.bind(name, callback)`

Register a reusable `x-bind` object:

```js
Alpine.bind('SomeButton', () => ({
    type: 'button',
    '@click'() { this.doSomething() },
    ':disabled'() { return this.shouldDisable },
}))
```

```html
<button x-bind="SomeButton"></button>
```

### `Alpine.plugin(fn)`

Install a plugin — `fn(Alpine)` is called with the global. Accepts a function or an array:

```js
Alpine.plugin(morph)
Alpine.plugin([collapse, focus, mask])
```

### Other globals

| API | Purpose |
|---|---|
| `Alpine.version` | Version string (`3.16.3`) |
| `Alpine.start()` | Boot Alpine (module installs only; call once) |
| `Alpine.reactive(obj)` / `Alpine.effect(fn)` / `Alpine.transaction(fn)` | Vue reactivity primitives (see advanced) |
| `Alpine.walk(el, cb)` | Walk an element tree (used by plugins) |
| `Alpine.evaluate(el, expr)` / `Alpine.evaluateLater(el, expr)` | Evaluate an expression in an element's scope (sync / thenable) |
| `Alpine.entangle(inner, outer)` | Two-way sync between two reactive values across components |
| `Alpine.addRootSelector(sel)` | Treat extra selectors as component roots |
| `Alpine.morph` / `Alpine.morphBetween` | Added by `@alpinejs/morph` |

## Lifecycle events

| Event / hook | When |
|---|---|
| `alpine:init` (document event) | After the script loads, **before** Alpine scans the page — the only window to register extensions in CDN usage |
| `alpine:initialized` (document event) | After the initial page scan completes |
| `x-init` directive | Element initialization |
| `init()` on data objects | Component data initialization |
| `$watch` / `x-effect` | After any state change |

Registration timing summary:

```js
// CDN — extensions must wait for alpine:init
document.addEventListener('alpine:init', () => {
    Alpine.data('dropdown', () => ({ /* ... */ }))
    Alpine.store('cart', { /* ... */ })
    Alpine.directive('custom', (el, { expression }, { evaluate }) => { /* ... */ })
})

// Module — extensions go between import and start
import Alpine from 'alpinejs'
Alpine.data('dropdown', () => ({ /* ... */ }))
Alpine.start()
```

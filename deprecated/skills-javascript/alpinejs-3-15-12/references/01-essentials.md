# Essentials

## Installation

### CDN

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.12/dist/cdn.min.js"></script>
```

The `defer` attribute is mandatory — Alpine initializes after DOM parsing. For production, pin the exact version.

### NPM

```bash
npm install alpinejs
```

```js
import Alpine from 'alpinejs'
window.Alpine = Alpine  // optional, useful for devtools
Alpine.start()
```

Extensions (plugins, custom directives, Alpine.data) must be registered between the import and `Alpine.start()`. Call `Alpine.start()` exactly once.

### CSP Build

For environments with strict Content Security Policy (no `unsafe-eval`):

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.15.12/dist/cdn.min.js"></script>
```

Or via NPM: `import Alpine from '@alpinejs/csp'`. See [07-advanced](07-advanced.md) for CSP limitations.

## State

### Local State (`x-data`)

```html
<div x-data="{ open: false, count: 0 }">
  <span x-text="count"></span>
</div>
```

`x-data` accepts a JS object expression. Properties are reactive — changes automatically update dependent expressions.

### Methods and Getters

```html
<div x-data="{
  open: false,
  toggle() { this.open = !this.open },
  get isOpen() { return this.open }
}">
```

- Methods use `this.` to access own properties (inside the object literal)
- Getters act as computed properties (not cached — re-evaluated on each access)
- In template expressions, access properties directly without `this.`

### Nesting / Scope

Data cascades to children. Child `x-data` can access parent properties. Same-name properties in child override parent.

```html
<div x-data="{ foo: 'parent' }">
  <div x-data="{ bar: 'child' }">
    <span x-text="foo"></span>  <!-- "parent" — inherited -->
    <span x-text="bar"></span>  <!-- "child" — local -->
  </div>
</div>
```

### Data-less Components

```html
<button x-data @click="alert('clicked')">Click</button>
```

Bare `x-data` (no expression) creates an Alpine component with empty scope.

### Global State (`Alpine.store`)

```js
document.addEventListener('alpine:init', () => {
  Alpine.store('theme', {
    dark: false,
    toggle() { this.dark = !this.dark }
  })
})
```

```html
<button @click="$store.theme.toggle()">Toggle</button>
<div :class="$store.theme.dark && 'bg-black'">...</div>
```

Stores are reactive and accessible from any component via `$store.<name>`.

## Events

### Listening

```html
<button @click="handleClick">Click</button>
<input @keyup.enter="submit">
<form @submit.prevent="handleSubmit">
```

- `@` is shorthand for `x-on:`
- Any DOM event name works: `@click`, `@mouseenter`, `@keyup`, `@scroll`, etc.
- `$event` gives access to the native event object

### Event Modifiers

| Modifier | Description |
|---|---|
| `.prevent` | `event.preventDefault()` |
| `.stop` | `event.stopPropagation()` |
| `.self` | Only fire if event target is the element itself |
| `.once` | Fire only once |
| `.capture` | Listen in capture phase |
| `.window` | Listen on `window` |
| `.document` | Listen on `document` |
| `.passive` | Add `{ passive: true }` |
| `.passive.false` | Add `{ passive: false }` |
| `.debounce` / `.debounce.500ms` | Debounce (default 250ms) |
| `.throttle` / `.throttle.500ms` | Throttle (default 250ms) |
| `.outside` | Fire when click originates outside element |
| `.camel` | CamelCase the event name |
| `.dot` | Convert dashes to dots in event name |

### Keyboard Modifiers

`.enter`, `.space`, `.delete`, `.esc`, `.tab`, `.up`, `.down`, `.left`, `.right`, `.ctrl`, `.shift`, `.alt`, `.meta`, `.caps-lock`, `.page-down`, `.equal`, `.period`, `.comma`, `.slash`

Chainable: `@keyup.shift.enter`

### Mouse Modifiers

`.shift`, `.ctrl`, `.meta`, `.alt` — on click, auxclick, context, dblclick, mouseover, mousemove, mouseenter, mouseleave, mouseout, mouseup, mousedown

### Custom Events

```html
<div @foo="handleFoo">
  <button @click="$dispatch('foo')">Dispatch</button>
</div>
```

`$dispatch(eventName, detail?, options?)` creates a bubbling CustomEvent.

## Lifecycle

### `x-init`

Executes when Alpine initializes the element. Can be placed anywhere inside or outside `x-data`.

```html
<div x-data="{ items: [] }" x-init="items = await fetch('/api').then(r => r.json())">
```

The `init()` method on `x-data` objects is called automatically before `x-init` directives.

### `$nextTick`

Execute after Alpine's reactive DOM updates complete:

```html
<div x-init="$nextTick(() => { /* DOM is fully updated */ })">
```

Returns a Promise — usable with `await`:

```js
await $nextTick()
console.log($el.innerText)  // reflects latest data
```

### Global Events

```js
document.addEventListener('alpine:init', () => {
  // Before Alpine initializes the page
  Alpine.data('...', () => ({ ... }))
})

document.addEventListener('alpine:initialized', () => {
  // After Alpine has initialized everything
})
```

Use `alpine:init` to register extensions. Use `alpine:initialized` for post-init work.

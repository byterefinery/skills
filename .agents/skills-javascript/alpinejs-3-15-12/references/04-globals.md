# Globals

## Alpine.data()

Register reusable component definitions. Accessed via `x-data="name"` or `x-data="name(params)"`.

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
  <div x-show="open">Content</div>
</div>
```

### With Parameters

```html
<div x-data="dropdown(true)">
```

```js
Alpine.data('dropdown', (initialOpen = false) => ({
  open: initialOpen,
  toggle() { this.open = !this.open }
}))
```

### Lifecycle Methods

- `init()` — called automatically before Alpine renders the component
- `destroy()` — called before component cleanup (e.g., when removed by `x-if`)

```js
Alpine.data('timer', () => ({
  timer: null,
  counter: 0,
  init() {
    this.timer = setInterval(() => { this.counter++ }, 1000)
  },
  destroy() {
    clearInterval(this.timer)
  }
}))
```

### Using Magics in Components

Access magics via `this` inside component methods:

```js
Alpine.data('component', () => ({
  init() {
    this.$watch('open', value => console.log(value))
  }
}))
```

### With $persist

Use a regular function (not arrow) so `this` context is available:

```js
Alpine.data('component', function() {
  return {
    open: this.$persist(false)
  }
})
```

### NPM Module Registration

```js
import Alpine from 'alpinejs'
import dropdown from './dropdown.js'

Alpine.data('dropdown', dropdown)
Alpine.start()
```

```js
// dropdown.js
export default () => ({
  open: false,
  toggle() { this.open = !this.open }
})
```

## Alpine.store()

Register global reactive stores. Accessible from any component via `$store`.

```js
// Script tag
document.addEventListener('alpine:init', () => {
  Alpine.store('theme', {
    dark: false,
    toggle() { this.dark = !this.dark }
  })
})

// NPM module (before Alpine.start())
import Alpine from 'alpinejs'
Alpine.store('theme', { dark: false, toggle() { this.dark = !this.dark } })
Alpine.start()
```

```html
<button @click="$store.theme.toggle()">Toggle</button>
<div :class="$store.theme.dark && 'bg-black'">
```

### Accessing Stores Externally

```js
Alpine.store('theme').toggle()
```

### init() in Stores

```js
Alpine.store('theme', {
  init() {
    this.dark = window.matchMedia('(prefers-color-scheme: dark)').matches
  },
  dark: false,
  toggle() { this.dark = !this.dark }
})
```

### Single-Value Stores

```js
Alpine.store('darkMode', false)
```

```html
<button @click="$store.darkMode = !$store.darkMode">Toggle</button>
<div :class="$store.darkMode && 'bg-black'">
```

## Alpine.bind()

Register reusable directive binding objects. Applied via `x-bind="name"`.

```js
document.addEventListener('alpine:init', () => {
  Alpine.bind('button-attrs', () => ({
    type: 'button',
    ['@click']() { this.doSomething() },
    [':disabled']() { return this.shouldDisable },
  }))
})
```

```html
<button x-bind="button-attrs">Click</button>
```

## Global Lifecycle Events

```js
document.addEventListener('alpine:init', () => {
  // Before Alpine initializes — register extensions here
  Alpine.data('...', () => ({ ... }))
  Alpine.store('...', { ... })
  Alpine.directive('custom', ...)
  Alpine.magic('custom', ...)
})

document.addEventListener('alpine:initialized', () => {
  // After Alpine has initialized everything on the page
})
```

For NPM modules, register between import and `Alpine.start()`:

```js
import Alpine from 'alpinejs'

Alpine.data('...', () => ({ ... }))
Alpine.store('...', { ... })

Alpine.start()
```

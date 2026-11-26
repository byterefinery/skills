# Magics and Globals (Alpine.js 3.17.5)

Magics are `$`-prefixed helpers available inside Alpine expressions. Globals live on the `Alpine` object.

## Magics

### $el

The current DOM node.

```html
<button @click="$el.innerHTML = 'Hello World!'">Replace me</button>
```

### $root

The closest ancestor element (up the DOM tree) that contains `x-data` — the component root.

```html
<div x-data data-message="Hello World!">
    <button @click="alert($root.dataset.message)">Say Hi</button>
</div>
```

### $data

The current Alpine data scope as an actual object — useful for passing the whole scope to a function.

```html
<div x-data="{ greeting: 'Hello' }">
    <div x-data="{ name: 'Caleb' }">
        <button @click="sayHello($data)">Say Hello</button>
    </div>
</div>

<script>
    function sayHello({ greeting, name }) {
        alert(greeting + ' ' + name + '!')
    }
</script>
```

### $refs

DOM elements marked with `x-ref` inside the component (see directives). Static refs only in v3 — a dynamic `x-ref="item.name"` stores the literal string.

### $id

Generates page-unique IDs; pair with `x-id` scopes. `$id('text-input')` → `text-input-1`, `text-input-2`, ... on repeated components. Second optional parameter adds a key suffix for loops: `$id('list-item', item.id)`.

### $store

Access to global stores registered with `Alpine.store(...)`:

```html
<button x-data @click="$store.darkMode.toggle()">Toggle Dark Mode</button>
<div x-data :class="$store.darkMode.on && 'bg-black'">...</div>
```

Stores can be objects **or single values** (`Alpine.store('open', false)` + `$store.open = true`).

### $watch

Watch a property (dot notation supported) for changes:

```html
<div x-data="{ foo: { bar: 'baz' } }" x-init="$watch('foo.bar', (value, oldValue) => ...)">
```

- Callback receives `(new value, old value)`.
- Lazy — does not run until the first change (contrast with `x-effect`, which runs immediately).
- Deep watching: watching `foo` also fires for `foo.bar` changes, but the callback gets the whole `foo` value, not the changed subproperty.
- **Do not mutate the watched property inside the callback** — infinite loop.

### $dispatch

Shortcut for `element.dispatchEvent(new CustomEvent(...))`:

```html
<div @notify="alert($event.detail.message)">
    <button @click="$dispatch('notify', { message: 'Hello World!' })">Notify</button>
</div>
```

- Data passed as the second argument is available on `$event.detail`.
- **Bubbling** — dispatched events bubble through the DOM; sibling components can't hear them unless they listen with `.window`.
- **Cancelable** — `$dispatch` returns whether the event was **not** prevented, enabling guards:

  ```html
  <div x-data x-on:open="$event.preventDefault()">
      <button @click="if ($dispatch('open')) { open = true }">Click me</button>
  </div>
  ```

- **Options** — a third argument overwrites event options, e.g. `$dispatch('update-title', 'Hi', { bubbles: false })`.
- **Dispatching to `x-model`** — dispatching an `input` event on an element updates its bound property: `@click="$dispatch('input', 'Hello World!')"`. This is how custom input components feed `x-model`.

### $nextTick

Run code after Alpine has finished its reactive DOM updates; returns a Promise so it can be awaited.

```html
<button
    @click="
        title = 'Hello World!';
        await $nextTick();
        console.log($el.innerText)   // 'Hello World!'
    "
    x-text="title"
></button>
```

### $event

The native event object inside `x-on` expressions (also passed as first argument to methods called without parens).

## Globals

### Alpine.data()

Register a re-usable `x-data` context:

```js
Alpine.data('dropdown', () => ({
    open: false,
    toggle() { this.open = ! this.open }
}))
// markup: x-data="dropdown"
```

- **Initial parameters** — reference as a function to pass args: `x-data="dropdown(true)"` with `Alpine.data('dropdown', (initialOpen = false) => ({ open: initialOpen }))`.
- **`init()` / `destroy()`** — auto-called on component init / cleanup (e.g. clear intervals; destruction happens when the element is removed, like inside `x-if`).
- **Magics via `this`** — component objects can use magics through the `this` context (`this.$watch(...)` in `init()`).
- **With `$persist`** — use a standard function, not an arrow function, so `this` binds: `Alpine.data('dropdown', function () { return { open: this.$persist(false) } })`.
- **Encapsulating directives** — store `x-bind` objects on the data to reuse whole directive bundles (see `x-bind` in directives).

### Alpine.store()

Global state available from any component via `$store`:

```js
// CDN: inside alpine:init. Module: before Alpine.start().
Alpine.store('darkMode', {
    on: false,
    toggle() { this.on = ! this.on }
})
```

- Stores may have an `init()` method, run right after registration (e.g. read `window.matchMedia('(prefers-color-scheme: dark)').matches`).
- Single values are valid stores.
- Read/write from plain JS too: `Alpine.store('darkMode').toggle()`.

### Alpine.bind()

Register a re-usable `x-bind` object:

```js
Alpine.bind('SomeButton', () => ({
    type: 'button',
    '@click'() { this.doSomething() },
    ':disabled'() { return this.shouldDisable }
}))
// markup: <button x-bind="SomeButton">
```

## Lifecycle events

| Event | When | Use for |
|---|---|---|
| `alpine:init` (on `document`) | After Alpine loads, **before** it initializes the page | Register `Alpine.data/store/bind/directive/magic/plugin` (CDN usage) |
| `alpine:initialized` (on `document`) | After initialization completes | Any code that needs the page already set up |

```js
document.addEventListener('alpine:init', () => {
    Alpine.data(...)
})
document.addEventListener('alpine:initialized', () => {
    //
})
```

## Reactivity primitives

- `Alpine.reactive(object)` — returns a reactive proxy of the object (Vue reactivity under the hood).
- `Alpine.effect(callback)` — runs the callback, tracks every reactive read inside it, re-runs when any tracked value changes (re-collecting dependencies each run; reads inside `setTimeout` are not tracked by the original effect).

```js
let data = Alpine.reactive({ count: 1 })
Alpine.effect(() => {
    span.textContent = data.count
})
button.addEventListener('click', () => { data.count++ })
```

## Async / await

Alpine supports `async`/`await` in most expression contexts:

```html
<span x-text="await getLabel()"></span>
```

where `getLabel` is an async function. Methods referenced without parens are also detected and awaited automatically.

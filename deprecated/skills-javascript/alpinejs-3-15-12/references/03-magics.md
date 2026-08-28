# Magic Properties

Magic properties are `\$`-prefixed helpers available in all Alpine expressions.

## $el

The current DOM element where the expression is evaluated.

```html
<button @click="$el.innerHTML = 'Hello'">Click</button>
<button @click="$el.classList.add('active')">Click</button>
```

In V3, `$el` is always the element the expression runs on (not the component root). Use `$root` for the component root.

## $refs

Object mapping `x-ref` names to DOM elements within the component.

```html
<div x-data>
  <span x-ref="text">Hello</span>
  <button @click="$refs.text.textContent = 'Changed'">Change</button>
</div>
```

Refs are static only — dynamic `:x-ref` does not work in V3.

## $store

Access global stores registered via `Alpine.store()`.

```html
<button @click="$store.theme.toggle()">Toggle</button>
<div :class="$store.theme.dark && 'bg-black'">
<button @click="$store.darkMode = !$store.darkMode">Toggle boolean store</button>
```

```js
Alpine.store('theme', { dark: false, toggle() { this.dark = !this.dark } })
Alpine.store('darkMode', false)  // single-value store
```

## $watch

Watch a property for changes. Callback receives `(newValue, oldValue)`.

```html
<div x-data="{ open: false }" x-init="$watch('open', (value, old) => console.log(value, old))">
```

Dot notation for nested properties:

```html
<div x-data="{ user: { name: 'John' } }" x-init="$watch('user.name', value => console.log(value))">
```

Deep watching — watching `user` fires when any nested property changes, but returns the entire `user` object.

Warning: mutating a watched property inside its own callback causes an infinite loop.

## $dispatch

Dispatch custom DOM events. Returns whether the event was prevented.

```html
<div @notify="handleNotify()">
  <button @click="$dispatch('notify')">Dispatch</button>
</div>

<!-- With detail data -->
<button @click="$dispatch('notify', { message: 'Hello' })">
<div @notify="console.log($event.detail.message)">

<!-- Check if prevented -->
<button @click="if ($dispatch('open')) { open = true }">

<!-- Non-bubbling -->
<button @click="$dispatch('event', data, { bubbles: false })">
```

For cross-component communication, use `.window` modifier on listeners since events bubble up, not across siblings.

## $nextTick

Execute callback after Alpine's reactive DOM updates complete. Returns a Promise.

```html
<button @click="
  title = 'Hello World';
  $nextTick(() => { console.log($el.textContent) })
">
```

With async/await:

```html
<button @click="
  title = 'Hello World';
  await $nextTick();
  console.log($el.textContent);
">
```

## $root

The closest ancestor element with `x-data` — the component root.

```html
<div x-data data-message="Hello">
  <button @click="alert($root.dataset.message)">Alert</button>
</div>
```

## $data

The current Alpine data scope as a plain object. Merges all ancestor `x-data` scopes.

```html
<div x-data="{ greeting: 'Hello' }">
  <div x-data="{ name: 'World' }">
    <button @click="externalFunc($data)">Pass scope</button>
  </div>
</div>

<script>
function externalFunc({ greeting, name }) {
  alert(greeting + ' ' + name)
}
</script>
```

## $id

Generate unique IDs. Use with `x-id` for scoped ID groups.

```html
<!-- Basic: auto-incrementing suffix -->
<input :id="$id('text-input')">  <!-- id="text-input-1" -->
<input :id="$id('text-input')">  <!-- id="text-input-2" -->

<!-- Scoped: same ID within x-id group -->
<div x-id="['text-input']">
  <label :for="$id('text-input')">  <!-- "text-input-1" -->
  <input :id="$id('text-input')">   <!-- "text-input-1" -->
</div>

<!-- Keyed: unique within loop -->
<div x-id="['list-item']">
  <ul :aria-activedescendant="$id('list-item', activeId)">
    <template x-for="item in items" :key="item.id">
      <li :id="$id('list-item', item.id)">
    </template>
  </ul>
</div>
```

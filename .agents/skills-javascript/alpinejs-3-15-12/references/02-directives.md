# Directives

All directives require a parent `x-data` (can be bare `x-data` with no expression).

## x-data

Declares a reactive component scope. Accepts a JS object expression or nothing (data-less).

```html
<div x-data="{ count: 0 }">
<div x-data>  <!-- data-less -->
<div x-data="dropdown">  <!-- registered via Alpine.data() -->
<div x-data="dropdown(true)">  <!-- with initial parameters -->
```

Properties cascade to children. Nested `x-data` can access parent scope. Methods use `this.` inside the object. Getters provide computed-like behavior.

## x-init

Runs on element initialization. Auto-evaluates `init()` methods on `x-data` objects before `x-init` directives.

```html
<div x-init="console.log('initialized')">
<div x-data="{ init() { /* auto-called */ } }">
<div x-init="$nextTick(() => { /* after DOM updates */ })">
```

## x-show

Toggles `display: none` inline style based on expression truthiness.

```html
<div x-show="open">Content</div>
<div x-show.important="open">Content</div>  <!-- adds !important -->
```

Use with `x-transition` for animated toggles. Not compatible with `x-if`.

## x-bind

Binds HTML attributes to expressions. Shorthand: `:`.

```html
<input :placeholder="placeholderText">
<button :disabled="shouldDisable">Click</button>
<img :src="imageUrl" :alt="imageAlt">
```

### Class Binding

```html
<div :class="open ? '' : 'hidden'">
<div :class="open || 'hidden'">
<div :class="{ 'hidden': !open }">  <!-- object syntax: preserves existing classes -->
```

Object syntax for `:class` preserves original classes on the element and toggles only the specified ones.

### Style Binding

```html
<div :style="{ color: 'red', display: 'flex' }">
<div :style="stylesObject">
<div style="padding: 1rem" :style="{ color: 'red' }">  <!-- merges -->
```

### Directive Binding (Spread)

Apply multiple directives from an object:

```html
<button x-bind="trigger">
<div x-bind="dialogue">
```

```js
Alpine.data('dropdown', () => ({
  open: false,
  trigger: {
    ['@click']() { this.open = !this.open },
    ['x-ref']: 'trigger',
  },
  dialogue: {
    ['x-show']() { return this.open },
    ['@click.outside']() { this.open = false },
  },
}))
```

For `x-for` in bind objects, return a string: `['x-for']() { return 'item in items' }`

## x-on

Listens for DOM events. Shorthand: `@`.

```html
<button @click="handleClick">Click</button>
<input @keyup.enter="submit">
<form @submit.prevent="handleSubmit">
<div @click.outside="open = false">
<div @scroll.window.throttle="handleScroll">
```

Event modifiers: `.prevent`, `.stop`, `.self`, `.once`, `.capture`, `.window`, `.document`, `.outside`, `.passive`, `.passive.false`, `.debounce`, `.throttle`, `.camel`, `.dot`, plus keyboard and mouse key modifiers.

See [01-essentials](01-essentials.md) for full modifier reference.

## x-text

Sets `textContent` to expression result. Auto-updates on reactive changes.

```html
<span x-text="username">
<span x-text="count * 2">
```

## x-html

Sets `innerHTML`. Only use with trusted content — XSS risk with user input.

```html
<div x-html="trustedHtml">
```

## x-model

Two-way binding between form inputs and data properties.

```html
<input type="text" x-model="message">
<textarea x-model="message"></textarea>
<input type="checkbox" x-model="show">  <!-- boolean -->
<input type="checkbox" value="red" x-model="colors">  <!-- array push/pop -->
<input type="radio" value="yes" x-model="answer">
<select x-model="color"><option>Red</option></select>
<select x-model="colors" multiple><option>Red</option></select>
<input type="range" x-model="range" min="0" max="1" step="0.1">
```

### Modifiers

| Modifier | Description |
|---|---|
| `.lazy` | Sync on blur (not every keystroke) |
| `.change` | Sync on native `change` event |
| `.blur` | Sync on blur regardless of change |
| `.enter` | Sync on Enter key |
| `.number` | Coerce to number |
| `.boolean` | Coerce to boolean |
| `.debounce` / `.debounce.500ms` | Debounce updates |
| `.throttle` / `.throttle.500ms` | Throttle updates |
| `.fill` | Use input's `value` attribute if bound property is empty |

Modifiers can be combined: `x-model.blur.enter="search"`

### Programmatic Access

```html
<div x-ref="div" x-model="username">
<button @click="$refs.div._x_model.set('new')">Set</button>
<span x-text="$refs.div._x_model.get()">
```

## x-modelable

Exposes a component's internal property for `x-model` binding from a parent. Enables custom input components.

```html
<div x-data="{ number: 5 }">
  <div x-data="{ count: 0 }" x-modelable="count" x-model="number">
    <button @click="count++">Increment</button>
  </div>
  Number: <span x-text="number"></span>
</div>
```

## x-for

Iterates over arrays, objects, or ranges. Must be on `<template>` with one root child.

```html
<template x-for="item in items" :key="item.id">
  <li x-text="item.name"></li>
</template>

<template x-for="(value, key) in object">
  <li><span x-text="key"></span>: <span x-text="value"></span></li>
</template>

<template x-for="(item, index) in items">
  <li><span x-text="index"></span>: <span x-text="item"></span></li>
</template>

<template x-for="i in 10">  <!-- range: 1 to 10 -->
  <li x-text="i"></li>
</template>
```

Keys (`:key`) are essential for reordering, adding, or removing items — they tell Alpine which DOM nodes to preserve, move, or destroy.

## x-transition

Animates elements toggled by `x-show`. Works only with `x-show`, not `x-if`.

### Helper Modifiers

```html
<div x-show="open" x-transition>
<div x-show="open" x-transition.duration.500ms>
<div x-show="open" x-transition.opacity>
<div x-show="open" x-transition.scale.80>
<div x-show="open" x-transition.scale.origin.top>
<div x-show="open" x-transition.delay.50ms>
```

Separate enter/leave:

```html
<div x-show="open"
  x-transition:enter.duration.500ms
  x-transition:leave.duration.400ms>
```

### CSS Class Syntax

```html
<div x-show="open"
  x-transition:enter="transition ease-out duration-300"
  x-transition:enter-start="opacity-0 scale-90"
  x-transition:enter-end="opacity-100 scale-100"
  x-transition:leave="transition ease-in duration-300"
  x-transition:leave-start="opacity-100 scale-100"
  x-transition:leave-end="opacity-0 scale-90">
```

| Phase | Description |
|---|---|
| `:enter` | Entire entering phase |
| `:enter-start` | Before insert, removed one frame after |
| `:enter-end` | One frame after insert, removed when done |
| `:leave` | Entire leaving phase |
| `:leave-start` | Immediately on leave, removed after one frame |
| `:leave-end` | One frame after leave starts, removed when done |

## x-effect

Re-evaluates expression when any referenced reactive property changes. Runs immediately on init.

```html
<div x-data="{ label: 'Hello' }" x-effect="console.log(label)">
```

Unlike `$watch`, `x-effect` auto-detects dependencies and runs eagerly (not lazy). No access to previous value.

## x-if

Conditionally adds/removes elements from DOM. Must be on `<template>` with one root child. No transition support.

```html
<template x-if="open">
  <div>Content</div>
</template>
```

Use `x-show` + `x-transition` instead when animations are needed.

## x-ref

Registers a DOM element reference accessible via `$refs`.

```html
<span x-ref="text">Hello</span>
<button @click="$refs.text.remove()">Remove</button>
```

Refs are static only — `:x-ref="dynamic"` does not work in V3.

## x-cloak

Hides element until Alpine initializes. Requires CSS:

```css
[x-cloak] { display: none !important; }
```

```html
<span x-cloak x-show="false">Won't flicker</span>
<span x-cloak x-text="message">Hidden until data loads</span>
```

## x-ignore

Prevents Alpine from initializing the element and its children.

```html
<div x-data="{ label: 'Alpine' }">
  <div x-ignore>
    <span x-text="label"></span>  <!-- not evaluated -->
  </div>
</div>
```

## x-teleport

Moves template content to another DOM location. Useful for modals to escape z-index stacking contexts.

```html
<div x-data="{ open: false }">
  <button @click="open = !open">Toggle</button>
  <template x-teleport="body" @click="open = false">
    <div x-show="open">Modal content</div>
  </template>
</div>
```

- Selector accepts any CSS selector string (`body`, `#id`, `.class`)
- Events registered on `<template x-teleport>` are forwarded from teleported content
- Teleported content retains Alpine scope, `$refs`, `$root` access
- Nesting teleports works for nested modals

## x-id

Declares an ID scope for `$id()` calls. Accepts array of ID names.

```html
<div x-id="['text-input']">
  <label :for="$id('text-input')">Username</label>
  <input :id="$id('text-input')">
  <!-- Both resolve to "text-input-1" -->
</div>
```

`$id('name', key)` accepts optional second parameter for keyed IDs within loops.

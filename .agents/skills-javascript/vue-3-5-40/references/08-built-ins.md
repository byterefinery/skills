# Built-in Components & Directives

Vue's built-in components and special directives available without registration.

## Table of Contents

- [Built-in Components](#built-in-components)
- [Built-in Directives](#built-in-directives)
- [Special Attributes](#special-attributes)
- [Special Elements](#special-elements)

## Built-in Components

### `<KeepAlive>`

Caches inactive component instances instead of destroying them. Wrap dynamic components.

```vue
<KeepAlive>
  <component :is="currentTab" />
</KeepAlive>

<!-- With max cache size -->
<KeepAlive :max="10">
  <component :is="currentTab" />
</KeepAlive>

<!-- Include/exclude by component name -->
<KeepAlive :include="['a', 'b']" :exclude="['c']">
  <component :is="currentTab" />
</KeepAlive>
```

- `include` / `exclude`: string, regex, or comma-separated list of component names
- `max`: maximum number of cached instances
- Triggers `onActivated` / `onDeactivated` lifecycle hooks

### `<Transition>`

Applies enter/leave animations to a single element or component.

```vue
<Transition name="fade">
  <div v-if="show">Hello</div>
</Transition>

<!-- CSS classes applied: -->
<!-- .fade-enter-active, .fade-enter-from, .fade-enter-to -->
<!-- .fade-leave-active, .fade-leave-from, .fade-leave-to -->
```

Props:
- `name`: shorthand for class prefix (auto-generates class names)
- `css`: disable CSS transitions (default `true`)
- `duration`: custom duration in ms
- `type`: specify transition type (`'transition'` or `'animation'`)
- `mode`: `'in-out'` (default) or `'out-in'` for element transitions

JavaScript hooks:
- `@before-enter`, `@enter`, `@after-enter`, `@enter-cancelled`
- `@before-leave`, `@leave`, `@after-leave`, `@leave-cancelled`

```vue
<Transition @enter="onEnter" @leave="onLeave">
  <div v-if="show">Hello</div>
</Transition>
```

### `<TransitionGroup>`

Applies animations to items in a `v-for` list. Renders a wrapper element (default `<span>`, configurable via `tag`).

```vue
<TransitionGroup name="list" tag="ul">
  <li v-for="item in items" :key="item.id">
    {{ item.name }}
  </li>
</TransitionGroup>
```

Uses same CSS classes as `<Transition>` plus `.v-move` for list reordering animations. Each item must have a unique `:key`.

### `<Teleport>`

Renders its slot content to a different part of the DOM.

```vue
<Teleport to="body">
  <div class="modal">
    <p>Modal content</p>
    <button @click="open = false">Close</button>
  </div>
</Teleport>

<!-- Dynamic target -->
<Teleport :to="targetContainer">
  <div>Content</div>
</Teleport>

<!-- Disabled (renders in place) -->
<Teleport to="body" :disabled="isMobile">
  <div>Content</div>
</Teleport>
```

- `to`: CSS selector string or actual DOM element
- `disabled`: if true, content renders in place instead of teleporting
- Content is still part of the Vue component tree (reactivity, events, lifecycle work normally)

### `<Suspense>`

Coordinates loading of async dependency trees.

```vue
<Suspense>
  <template #default>
    <AsyncComponent />
  </template>
  <template #fallback>
    <p>Loading...</p>
  </template>
</Suspense>
```

- `#default`: shown when all async dependencies are resolved
- `#fallback`: shown while waiting for async dependencies
- `timeout`: ms to wait before showing fallback

## Built-in Directives

### v-model

Two-way binding on form inputs and components. See [04-template-syntax](04-template-syntax.md#v-model).

### v-bind (`:`)

Dynamic attribute binding. See [04-template-syntax](04-template-syntax.md#attribute-bindings).

### v-on (`@`)

Event listener. See [04-template-syntax](04-template-syntax.md#v-on-event-handling).

### v-if / v-else-if / v-else

Conditional rendering. Destroys and recreates elements. See [04-template-syntax](04-template-syntax.md#v-if-v-else-if-v-else).

### v-for

List rendering. See [04-template-syntax](04-template-syntax.md#v-for).

### v-show

Toggles `display` CSS property. Element always rendered.

```vue-html
<h1 v-show="visible">Toggle me</h1>
```

### v-text

Sets `textContent`. Overwrites all existing content.

```vue-html
<span v-text="msg"></span>
<!-- equivalent to -->
<span>{{ msg }}</span>
```

### v-html

Sets `innerHTML`. Security risk — only use on trusted content.

```vue-html
<div v-html="trustedHtml"></div>
```

### v-pre

Skips compilation of element and children. Render raw mustaches as-is.

```vue-html
<span v-pre>{{ this is not compiled }}</span>
```

### v-once

Renders once and skips future updates.

```vue-html
<span v-once>{{ this will never change }}</span>
<!-- With v-for (3.2+) -->
<option v-for="option in options" :key="option.value" :value="option.value" v-once>
```

### v-memo (3.2+)

Memoizes a subtree. Only updates if any value in the array changes.

```vue-html
<div v-memo="[list.length, sortBy]">
  <Item v-for="item in sortedList" :item="item" />
</div>
```

Use for performance optimization on large lists where most items don't change.

### v-cloak

Keeps element hidden until the associated instance finishes compilation. Useful to prevent flickering of uncompiled mustaches.

```vue-html
<div v-cloak>{{ message }}</div>
```

```css
[v-cloak] { display: none; }
```

## Special Attributes

### key

Special attribute for Vue's virtual DOM diffing algorithm. Required on `v-for` items. Helps Vue identify which nodes to reuse/move.

```vue-html
<li v-for="item in items" :key="item.id">{{ item.name }}</li>
```

### ref

Template ref for accessing DOM elements or component instances.

```vue-html
<!-- DOM element -->
<div ref="myDiv"></div>

<!-- Component instance -->
<ChildComponent ref="child" />
```

```vue
<script setup>
import { ref, onMounted } from 'vue'

const myDiv = ref(null)
const child = ref(null)

onMounted(() => {
  console.log(myDiv.value) // HTMLDivElement
  console.log(child.value) // Component instance (if not defineExpose)
})
</script>
```

Use `useTemplateRef()` (3.5+) for typed template refs:

```ts
const myDiv = useTemplateRef<HTMLDivElement>('myDiv')
```

### is

Used for dynamic components.

```vue-html
<component :is="currentComponent" />
```

Also used to force Vue to treat a native HTML element as a Vue component (for elements like `<select>`, `<template>` that have special behavior).

## Special Elements

### `<template>`

Placeholder element for grouping content. Not rendered in the DOM. Used with:
- `v-if` / `v-for` for conditional/list blocks
- Named slots: `<template #header>`
- Fragment-like multi-root content

### `<component>`

Meta-component for rendering dynamic components via `:is`.

```vue-html
<component :is="currentTab" />
```

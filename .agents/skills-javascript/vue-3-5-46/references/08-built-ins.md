# Built-in components, directives, SSR, custom elements

Source: `packages/runtime-core/src/index.ts` + `components/`, `packages/runtime-dom/src/index.ts` + `components/` + `directives/`, `packages/server-renderer/src/index.ts` in the v3.5.46 tree.

## Built-in components

| Component | Package | Purpose |
|---|---|---|
| `Teleport` | runtime-core (`components/Teleport`) | move DOM to another location (`to` target); `TeleportProps` type |
| `Suspense` | runtime-core (`components/Suspense`) | suspense boundary for async setup/components; `SuspenseProps` type |
| `KeepAlive` | runtime-core (`components/KeepAlive`) | cache component instances; exports `onActivated`/`onDeactivated` |
| `Transition` | runtime-dom (`components/Transition`) | enter/leave transitions; `TransitionProps` type |
| `TransitionGroup` | runtime-dom (`components/TransitionGroup`) | list transitions; `TransitionGroupProps` type |

`Transition` and `TransitionGroup` are also registered as global components via the `GlobalComponents` module augmentation (runtime-dom index), so they work in templates without imports.

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

## Built-in directives

- **`v-model`** — runtime-dom `directives/vModel.ts`: `vModelText`, `vModelCheckbox`, `vModelRadio`, `vModelSelect`, `vModelDynamic`. SSR variants initialized via `initVModelForSSR`.
- **`v-show`** — `directives/vShow.ts` (`vShow` export; `initVShowForSSR` for SSR).
- **`v-on` helpers** — `withModifiers`, `withKeys` (exported for custom directive composition).
- Compiler-time: `v-if`, `v-for`, `v-once`, `v-memo`, `v-bind`, `v-slot` (see 04-template-syntax).

Directive registration: app-level via `app.directive` (Application API); programmatic directive VNodes via `withDirectives` (runtime-core).

## SSR (server-renderer + client hydration)

- **Server** — from `@vue/server-renderer` (deep import `vue/server-renderer`): `renderToString`, `renderToSimpleStream`, `renderToNodeStream`, `renderToWebStream`, `pipeToNodeWritable`, `pipeToWebWritable`; `renderToStream` is **deprecated**. Types: `SSRContext`, `SimpleReadable`.
- **App creation** — `createSSRApp()` (runtime-dom) for both server and client entry; client hydrates with the hydration renderer (`hydrate` is exported from runtime-dom).
- **Helpers** — `useSSRContext()` (+ `ssrContextKey`), `onServerPrefetch()` (see 07-lifecycle), `defineSSRCustomElement()`.

## Custom elements

From runtime-dom (`apiCustomElement.ts`): `defineCustomElement`, `defineSSRCustomElement`, `useShadowRoot`, `useHost`, the `VueElement` base class, and types `VueElementConstructor`, `CustomElementOptions`.
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

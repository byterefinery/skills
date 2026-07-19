---
name: vue-3-5-40
description: Vue.js 3.5.40 — progressive JavaScript framework for building UIs with reactive components. Covers Composition API with script-setup, reactivity (ref, reactive, computed, watch), SFCs, build-less CDN usage, composables, directives, transitions, and the full component model. Use when working with Vue 3 codebases, creating Vue components, debugging reactivity, or scaffolding Vue projects.
license: MIT
compatibility: Requires Node.js ^22.18.0 || >=24.12.0 for build setups. Browser: ES modules + import maps support (Safari 16.4+).
allowed-tools: Bash(npm:*) Bash(npx:*) Bash(pnpm:*) Bash(yarn:*) Bash(bun:*) Read
metadata:
  tags:
    - javascript
    - frontend
    - ui
    - framework
    - reactive
    - components
    - sfc
---

# vue 3.5.40

## Overview

Vue.js 3.5.40 is a progressive JavaScript framework for building user interfaces. It uses a declarative, component-based model built on reactive state. Two API styles exist: **Composition API** (recommended, used with `<script setup>`) and **Options API** (object-based, beginner-friendly). Vue supports multiple deployment modes: Single-File Components with Vite, build-less CDN usage with ES modules, SSR via Nuxt, and Web Components.

The reactivity system uses JavaScript Proxies and `ref()` wrappers to track state changes and efficiently update the DOM. Templates are pre-compiled into optimized render functions with compile-time optimizations.

## Usage

### Build-less (CDN / no build step)

```html
<script type="importmap">
  {
    "imports": {
      "vue": "https://unpkg.com/vue@3.5.40/dist/vue.esm-browser.js"
    }
  }
</script>

<div id="app">{{ message }}</div>

<script type="module">
  import { createApp, ref } from 'vue'

  createApp({
    setup() {
      const message = ref('Hello Vue!')
      return { message }
    }
  }).mount('#app')
</script>
```

Use `<script type="module">` with an import map pointing to the ESM browser build. All top-level APIs are also available on the global `Vue` object when using `vue.global.js`. Split JS into separate `.js` files served over `http://` (not `file://`). See [00-build-less](references/00-build-less.md) for full details.

### SFC with Vite (recommended for full apps)

```bash
npm create vue@latest
cd my-app && npm install && npm run dev
```

```vue
<script setup>
import { ref } from 'vue'
const count = ref(0)
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>

<style scoped>
button { font-weight: bold; }
</style>
```

### Reactivity

```js
import { ref, reactive, computed, watch } from 'vue'

const count = ref(0)                    // .value access in JS, auto-unwrapped in templates
const state = reactive({ count: 0 })    // deep proxy, direct property access
const double = computed(() => count.value * 2)
watch(count, (val) => console.log(val))
```

### Components

```vue
<!-- Parent.vue -->
<script setup>
import Child from './Child.vue'
const msg = ref('hello')
</script>

<template>
  <Child :title="msg" @update="msg = $event" />
</template>

<!-- Child.vue -->
<script setup>
const props = defineProps({ title: String })
const emit = defineEmits(['update'])
</script>
```

## Gotchas

- **`ref().value` required in JS, not in templates** — refs auto-unwrap inside template expressions but require `.value` in JavaScript code. Forgetting `.value` is the most common bug.
- **`reactive()` only works on objects** — cannot hold primitives. Use `ref()` for strings, numbers, booleans. Destructuring a reactive object loses reactivity connection.
- **`<script setup>` executes per-instance** — unlike normal `<script>` which runs once on import, `<script setup>` runs for every component instance. Side effects at top level will run per instance.
- **`v-model` on components uses `modelValue`/`update:modelValue` by default** — in 3.4+, use `defineModel()` macro for cleaner syntax. On native inputs, `v-model` ignores initial `value`/`checked`/`selected` HTML attributes.
- **Template expressions are sandboxed** — only a restricted list of globals (`Math`, `Date`) is available. No access to `window`, `document`, or user-defined globals unless explicitly added via `app.config.globalProperties`.
- **`v-if` has higher priority than `v-for`** — never put both on the same element. Wrap with `<template v-for>` and put `v-if` on an inner element, or use a computed filter.
- **Lifecycle hooks must be called synchronously during setup** — `onMounted()`, `onUnmounted()`, etc. must be called in the synchronous call stack of `setup()` or `<script setup>`. Calling them inside `setTimeout` or async callbacks won't work.
- **Reactive proxy !== original object** — `reactive(obj) === obj` is `false`. Always use the proxy, never the original. Same applies to `ref` — the original object assigned is left intact.
- **Build-less requires HTTP server** — ES modules don't work over `file://` protocol. Use `npx serve` or any static server. Import maps need Safari 16.4+.
- **`watch` is lazy, `watchEffect` runs immediately** — `watch()` only fires on source changes; `watchEffect()` runs once right away and tracks all accessed dependencies automatically.
- **`nextTick()` for DOM access after state changes** — DOM updates are batched asynchronously. Use `await nextTick()` before reading DOM state after mutating reactive data.

## References

- [01-build-less](references/01-build-less.md) — CDN usage, global build, ES module build, import maps, splitting modules, production deployment without build tools
- [02-reactivity](references/02-reactivity.md) — ref, reactive, computed, watch, watchEffect, reactivity system internals, shallow APIs, readonly
- [03-components](references/03-components.md) — component definition, props, emits, slots, provide/inject, defineProps/defineEmits/defineModel macros
- [04-template-syntax](references/04-template-syntax.md) — mustaches, directives (v-bind, v-on, v-if, v-for, v-model, v-show), event modifiers, dynamic arguments
- [05-sfc](references/05-sfc.md) — Single-File Component format, script-setup, template, style-scoped, pre-processors, src imports
- [06-composables](references/06-composables.md) — composable pattern, convention (useXxx), nested composables, side-effect cleanup
- [07-lifecycle](references/07-lifecycle.md) — onMounted, onUpdated, onUnmounted, async component lifecycle, Suspense
- [08-built-ins](references/08-built-ins.md) — Transition, TransitionGroup, Teleport, KeepAlive, Suspense, v-model, v-show, v-memo, v-once
- [09-api-reference](references/09-api-reference.md) — Application API, Reactivity API, Composition API, general utilities, type references

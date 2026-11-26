---
name: vue-3-5-46
description: Vue.js 3.5.46 — progressive JavaScript framework for building UIs with reactive components. Covers Composition API with script setup, reactive props destructure, reactivity (ref, reactive, computed, watch), SFC compilation, build-less CDN usage, SSR, composables, directives, transitions, and the full component model. Use when working with Vue 3 codebases, creating Vue components, debugging reactivity, or scaffolding Vue projects.
license: MIT
compatibility: Modern browser with ES module support for build-less usage. Core repo development needs pnpm and Node >=20.0.0.
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

# vue 3.5.46

## Overview

Vue.js 3.5.46 is a progressive JavaScript framework for building user interfaces with a declarative, component-based model. The repo (vuejs/core) contains the framework packages — `vue` (main entry, "full build" = runtime + compiler), `@vue/reactivity`, `@vue/runtime-core`, `@vue/runtime-dom`, `@vue/compiler-core` / `compiler-dom` / `compiler-sfc` / `compiler-ssr`, `@vue/server-renderer`, and `@vue/compat` (Vue 2 migration build) — plus runnable demos in `packages/vue/examples` (classic and composition variants of commits, grid, markdown, svg, todomvc, tree, plus transition demos) and in-browser tools in `packages-private` (SFC Playground, Template Explorer).

Two API styles coexist: **Options API** (object-based) and **Composition API** (`setup()` / `<script setup>`). The Composition API is built on the Proxy-based reactivity system (`ref()`, `reactive()`, `computed()`, `watch()`), and templates compile to optimized render functions with static hoisting.

## Usage

### Build-less (CDN / no build step)

The official examples (`packages/vue/examples/`) load `dist/vue.global.js` and use in-DOM templates:

```html
<script src="../../dist/vue.global.js"></script>

<script type="text/x-template" id="grid-template">
  <table v-if="filteredData.length">
    <tr v-for="entry in filteredData">
      <td v-for="key in columns">{{ entry[key] }}</td>
    </tr>
  </table>
  <p v-else>No matches found.</p>
</script>

<script>
  const { reactive, computed } = Vue
  const DemoGrid = {
    template: '#grid-template',
    props: { data: Array, columns: Array, filterKey: String },
    setup(props) {
      const state = reactive({ sortKey: '', sortOrders: {} })
      const filteredData = computed(() => props.data)
      return { state, filteredData }
    }
  }
</script>
```

The `vue.global.js` full build includes the runtime compiler, so `template: '#id'` in-DOM templates work; the runtime-only builds require pre-compiled templates. All APIs are on the global `Vue` object (IIFE build). See [01-build-less](references/01-build-less.md) for the dist file matrix.

### SFC (bundler, via vue/compiler-sfc)

Since 3.2.13+ `@vue/compiler-sfc` ships as a dependency of `vue` — use the deep import `vue/compiler-sfc` (no separate install or version matching). Bundler plugins (Vite, vue-loader) compile SFCs by parsing into a descriptor and transforming script / template / style blocks separately:

```js
// what a compiled SFC facade looks like (compiler-sfc README)
import script from '/project/foo.vue?vue&type=script'
import { render } from '/project/foo.vue?vue&type=template&id=xxxxxx'
import '/project/foo.vue?vue&type=style&index=0&id=xxxxxx'
script.render = render
script.__scopeId = 'xxxxxx'
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

const count = ref(0)                    // .value in JS, auto-unwrapped in templates
const state = reactive({ count: 0 })    // deep proxy
const double = computed(() => count.value * 2)
watch(count, (val) => console.log(val))
```

3.5-era additions present in this version: `watchPostEffect()` / `watchSyncEffect()` (flush-timed variants of `watchEffect`), `onWatcherCleanup()`, `getCurrentWatcher()`, `toValue()`, `triggerRef()`, `useId()`, `useTemplateRef()`, `useModel()`, and reactive props destructure in `<script setup>`.

### Components

```vue
<script setup>
const props = defineProps({ title: String })
const emit = defineEmits(['update'])
</script>

<template>
  <button @click="emit('update', true)">{{ props.title }}</button>
</template>
```

Component API: `defineComponent()`, `defineAsyncComponent()`, `provide()` / `inject()` / `hasInjectionContext()`, `useAttrs()`, `useSlots()`, `useModel()`, `useTemplateRef()`, `useId()`, plus `<script setup>` compiler macros: `defineProps` (with `withDefaults()` and reactive destructure), `defineEmits`, `defineExpose`, `defineSlots`, `defineModel`, `defineOptions`.

### SSR

```js
import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'

const html = await renderToString(app)
```

`vue/server-renderer` deep import exposes `renderToString`, `renderToSimpleStream`, `renderToNodeStream`, `renderToWebStream`, and pipe helpers. On the client, `createSSRApp()` + `hydrate()` for hydration; `useSSRContext()` and `onServerPrefetch()` for SSR-side work.

## Gotchas

- **`vue.global.js` is an IIFE, not UMD** — inlines all internal packages; import everything from this single file to avoid duplicate instances. Use pre-minified `*.prod.js` files for production.
- **Full vs runtime builds** — `vue.runtime.*` builds have no template compiler; `template: '#id'` in-DOM templates (as the examples use) only work with the full build (`vue.global.js`, `vue.esm-browser.js`, or aliasing `vue` to `vue.esm-bundler.js`).
- **esm-bundler builds need bundler config** — prod/dev branches are guarded by `process.env.NODE_ENV` (the bundler must replace it). Feature flags `__VUE_OPTIONS_API__` (default true), `__VUE_PROD_DEVTOOLS__` (default false), `__VUE_PROD_HYDRATION_MISMATCH_DETAILS__` (default false) should be configured for proper tree-shaking.
- **Props destructure vs `withDefaults`** — reactive props destructure is disabled when `withDefaults()` is used; destructured props are readonly, no nested patterns, no computed keys.
- **Reactivity caveats** — built-in objects are not observed except `Array`, `Map`, `WeakMap`, `Set`, `WeakSet` (reactivity README). `reactive()` takes objects only; `ref()` for primitives.
- **`app.config.compilerOptions` is dev-warning-only in runtime-only builds** — in a runtime-only build it must be passed to `@vue/compiler-dom` in the build setup instead (Vite plugin options / vue-loader).
- **`@vue/runtime-core` is not for applications** — published for typing and custom renderers; apps import `vue` (which re-exports `@vue/runtime-dom` → `@vue/runtime-core`).
- **`@vue/reactivity` standalone vs inlined** — the standalone package must not be mixed with a pre-bundled renderer build; they use different internal storage for reactivity connections.
- **Vue 2 migration** — `@vue/compat` runs in Vue 2 mode by default (MODE 2) with runtime warnings; opt to Vue 3 behavior globally via `configureCompat({ MODE: 3 })` or per-component `compatConfig`. Transition class renames have no runtime warning — search for `.*-enter` / `.*-leave` manually.

## References

- [01-build-less](references/01-build-less.md) — dist file matrix (global / esm-browser / esm-bundler / cjs), prod builds, feature flags, in-DOM templates
- [02-reactivity](references/02-reactivity.md) — full reactivity API, refs, proxies, computed, effects, scopes, watch family, caveats
- [03-components](references/03-components.md) — component model, props/emits/slots, provide/inject, script setup macros, destructure, compat build
- [04-template-syntax](references/04-template-syntax.md) — directives and their compiler transforms, in-DOM templates, examples patterns
- [05-sfc](references/05-sfc.md) — SFC structure, compiler-sfc API, facade module workflow, styles, CSS vars, playground
- [06-composables](references/06-composables.md) — reusable stateful logic with the Composition API, scopes and cleanup
- [07-lifecycle](references/07-lifecycle.md) — all lifecycle hooks incl. SSR prefetch, debug hooks, error capture, KeepAlive activation
- [08-built-ins](references/08-built-ins.md) — Teleport, Suspense, KeepAlive, Transition/Group, v-model/v-show/v-once/v-memo, SSR APIs, custom elements
- [09-api-reference](references/09-api-reference.md) — complete export surface per package, vue subpath exports, examples and demos index

# Component model

Source: `packages/runtime-core/src/` (apiDefineComponent, apiAsyncComponent, apiInject, apiSetupHelpers, helpers/useModel, helpers/useTemplateRef, helpers/useId), `packages/compiler-sfc/src/script/` (macros), `packages/vue/examples/` in the v3.5.46 tree.

## Two API styles

- **Options API** — `data()`, `props:`, methods on `this` (the classic examples use this).
- **Composition API** — `setup()` or `<script setup>`; state via `ref`/`reactive`, logic grouped in plain functions.

## Core component APIs

- `defineComponent()` — typed component definition (option-object or setup-based).
- `defineAsyncComponent()` — async component definition (the Vue 3 replacement for the Vue 2 async component API; see the compat feature reference).
- **Provide / inject** — `provide()`, `inject()`, `hasInjectionContext()` (runtime-core `apiInject.ts`).
- **Setup helpers** — `useAttrs()` and `useSlots()` (must be called in `setup()`), `useModel()` (runtime equivalent of the `defineModel()` macro), `useTemplateRef()` (reactive template refs; types `TemplateRef`), `useId()` (unique id for a component instance).
- **Render utilities** — `h()`, `createVNode()`, `cloneVNode()`, `mergeProps()`, `isVNode()`, `Fragment`, `Text`, `Comment`, `Static`, `renderList()`, `renderSlot()`, `toHandlers()`, `createSlots()`, `withMemo()`, `isMemoSame()`.
- `getCurrentInstance()` — internal instance access (escape hatch; prefer setup APIs).

## `<script setup>` compiler macros

Defined in `packages/compiler-sfc/src/script/`:

- **`defineProps`** — runtime declaration (object or array) or type-only declaration (inferred from TypeScript). Supports reactive **props destructure** (3.5): `const { title } = defineProps({ ... })`. Restrictions from the compiler: no nested patterns, no computed keys, destructured props are readonly ("Cannot assign to destructured props as they are readonly"), and reactive destructure is disabled when `withDefaults()` is used.
- **`withDefaults`** — default values for props (pairs with `defineProps`; disables reactive destructure).
- **`defineEmits`** — runtime array or type-only declaration of emitted events.
- **`defineExpose`** — expose bindings to the parent (everything in `<script setup>` is private by default).
- **`defineSlots`** — type-only slot declarations (type-checking only, no runtime value).
- **`defineModel`** — two-way binding prop/emit pair (`modelValue` + `update:modelValue` by default, or named models).
- **`defineOptions`** — runtime options (`name`, `inheritAttrs`, ...) for `<script setup>` components.

## Patterns from the official examples

- **classic/** examples: plain options objects — `template: '#id'`, `props:`, `data()`, template references via `ref="..."` attributes.
- **composition/** examples: `setup(props)` returning reactive bindings (e.g. `grid.html` builds `state = reactive({...})` from `props.columns` and a `filteredData = computed(...)`).
- Components are registered locally (`components: { DemoGrid }`) or via imports; the examples show both in-DOM templates and component nesting (grid of components in `commits.html`).

## Prop Validation Types

- `String`, `Number`, `Boolean`, `Array`, `Object`, `Date`, `Function`, `Symbol`
- Custom constructor: `type: MyClass`
- Multiple types: `type: [String, Number]`
- Options: `default`, `required`, `validator(value) => boolean`

## One-Way Data Flow

Props flow one-way from parent to child. Never mutate a prop directly in the child. If you need to transform a prop, use a computed property. If you need to modify and sync back, use `v-model` or emit an update event.

## Slots

### Basic Slots

```vue
<!-- Child.vue -->
<template>
  <div>
    <slot>Default content</slot>
  </div>
</div>
</template>

<!-- Parent.vue -->
<template>
  <Child>
    <p>Replaced content</p>
  </Child>
</template>
```

### Named Slots

```vue
<!-- Child.vue -->
<template>
  <header><slot name="header" /></header>
  <main><slot /></main>
  <footer><slot name="footer" /></footer>
</template>

<!-- Parent.vue -->
<template>
  <Child>
    <template #header>
      <h1>Title</h1>
    </template>
    <template #default>
      <p>Main content</p>
    </template>
    <template #footer>
      <p>Footer</p>
    </template>
  </Child>
</template>
```

### Scoped Slots

```vue
<!-- Child.vue -->
<script setup>
const items = ref(['a', 'b', 'c'])
</script>

<template>
  <slot name="item" v-for="item in items" :item="item">
    {{ item }}
  </slot>
</template>

<!-- Parent.vue -->
<template>
  <Child>
    <template #item="{ item }">
      <strong>{{ item }}</strong>
    </template>
  </Child>
</template>
```

### useSlots() / useAttrs()

Access slots and attrs outside `<script setup>`:

```js
import { useSlots, useAttrs } from 'vue'

const slots = useSlots()
const attrs = useAttrs()

// Check if default slot exists
if (slots.default) {
  // render slots.default()
}
```

## Component Registration

### Local Registration (SFC + <script setup>)

Imports are automatically available in the template:

```vue
<script setup>
import MyComponent from './MyComponent.vue'
</script>

<template>
  <MyComponent />
</template>
```

### Global Registration

```js
import { createApp } from 'vue'
import MyComponent from './MyComponent.vue'

const app = createApp(App)
app.component('MyComponent', MyComponent)
app.mount('#app')
```

### Options API Local Registration

```js
import MyComponent from './MyComponent.vue'

export default {
  components: { MyComponent }
}
```

## Async Components

```js
import { defineAsyncComponent } from 'vue'

const AsyncComp = defineAsyncComponent(() =>
  import('./MyComponent.vue')
)

// With loading/error states
const AsyncComp = defineAsyncComponent({
  loader: () => import('./MyComponent.vue'),
  loadingComponent: LoadingComponent,
  errorComponent: ErrorComponent,
  delay: 200,        // ms before showing loading component
  timeout: 3000,     // ms before showing error component
  onError(error) { /* retry logic */ }
})
```

## Dynamic Components

```vue
<script setup>
import Foo from './Foo.vue'
import Bar from './Bar.vue'

const currentComponent = ref(Foo)
</script>

<template>
  <component :is="currentComponent" />
  <component :is="condition ? Foo : Bar" />
</template>
```

## Recursive Components

An SFC can reference itself by filename. A file named `TreeNode.vue` can use `<TreeNode />` in its template. Imported components take priority — alias imports that conflict with the inferred name.

```vue
<!-- TreeNode.vue -->
<script setup>
import { ref } from 'vue'
const props = defineProps({ node: Object })
</script>

<template>
  <li>
    {{ node.name }}
    <ul v-if="node.children">
      <TreeNode v-for="child in node.children" :node="child" />
    </ul>
  </li>
</template>
```
## Vue 2 migration build (`@vue/compat`)

Per `packages/vue-compat/README.md`:

- A build of Vue 3 with configurable Vue 2 compatibility behavior; **runs in Vue 2 mode by default** (MODE 2) and emits runtime warnings for changed/deprecated APIs. Per-component opt-in via the `compatConfig` component option; global config via `configureCompat()` from `vue`.
- Typical workflow: alias `vue` → `@vue/compat` in the build, fix compiler warnings (e.g. filters), update `<transition>` class names (the one breaking change **without** a runtime warning — search for `.*-enter` / `.*-leave`), switch to the `createApp()` mounting API, upgrade to vuex v4 / vue-router v4, then remove the compat build.
- Known limitations: dependencies on Vue 2 private APIs (e.g. VNode private properties), no IE11 (Vue 3 dropped IE11), SSR migration is involved (`vue-server-renderer` → `@vue/server-renderer`).
- The README's feature table marks features ✔ fully compatible, ◐ partially compatible, ⨂ incompatible (warning only), ⭘ compat-only (no warning) — e.g. `GLOBAL_MOUNT_CONTAINER` (⨂), `COMPILER_V_IF_V_FOR_PRECEDENCE` (⨂), `TRANSITION_CLASSES` (⭘).

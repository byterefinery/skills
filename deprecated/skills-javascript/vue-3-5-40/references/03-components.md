# Components

Component definition, props, emits, slots, provide/inject, and `<script setup>` macros.

## Table of Contents

- [Component Definition](#component-definition)
- [Props](#props)
- [Emits](#emits)
- [Slots](#slots)
- [defineModel (3.4+)](#definemodel-34)
- [provide / inject](#provide--inject)
- [Component Registration](#component-registration)
- [Async Components](#async-components)
- [Dynamic Components](#dynamic-components)
- [Recursive Components](#recursive-components)

## Component Definition

### SFC (Single-File Component)

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

### JavaScript Object (build-less)

```js
import { ref } from 'vue'

export default {
  setup() {
    const count = ref(0)
    return { count }
  },
  template: `<button @click="count++">{{ count }}</button>`
}
```

### defineComponent (TypeScript)

```ts
import { defineComponent, ref } from 'vue'

export default defineComponent({
  props: {
    initial: { type: Number, default: 0 }
  },
  setup(props) {
    const count = ref(props.initial)
    return { count }
  }
})
```

## Props

### declareProps with <script setup>

```vue
<script setup>
// Runtime declaration
const props = defineProps({
  title: String,
  count: { type: Number, default: 0 },
  tags: Array,
  callback: Function
})

// TypeScript declaration
defineProps<{
  title?: string
  count?: number
  tags?: string[]
  callback?: () => void
}>()
</script>
```

### withDefaults (TypeScript)

```vue
<script setup>
withDefaults(defineProps<{
  title?: string
  count?: number
  tags?: string[]
}>(), {
  title: 'Hello',
  count: 0,
  tags: () => ['default']
})
</script>
```

### Options API

```js
export default {
  props: {
    title: { type: String, required: true },
    count: { type: Number, default: 0 }
  }
}
```

### Prop Validation Types

- `String`, `Number`, `Boolean`, `Array`, `Object`, `Date`, `Function`, `Symbol`
- Custom constructor: `type: MyClass`
- Multiple types: `type: [String, Number]`
- Options: `default`, `required`, `validator(value) => boolean`

### One-Way Data Flow

Props flow one-way from parent to child. Never mutate a prop directly in the child. If you need to transform a prop, use a computed property. If you need to modify and sync back, use `v-model` or emit an update event.

## Emits

### defineEmits with <script setup>

```vue
<script setup>
// Runtime declaration
const emit = defineEmits(['update', 'delete'])

emit('update', newValue)

// TypeScript declaration
const emit = defineEmits<{
  update: [value: string]
  delete: [id: number]
}>()

// Runtime with type inference
const emit = defineEmits({
  update: (value) => typeof value === 'string',
  delete: (id) => typeof id === 'number'
})
</script>

<template>
  <button @click="emit('update', 'hello')">Update</button>
</template>
```

### Options API

```js
export default {
  emits: ['update', 'delete'],
  methods: {
    submit() {
      this.$emit('update', newValue)
    }
  }
}
```

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

## defineModel (3.4+)

Simplifies two-way binding between parent and child.

```vue
<!-- Child.vue -->
<script setup>
const model = defineModel() // default: binds to modelValue / update:modelValue

// With options
const count = defineModel({
  default: 0,
  transformer: {
    toValue: (v) => parseInt(v),
    fromValue: (v) => String(v)
  }
})

// Multiple models
const title = defineModel('title')
const count = defineModel('count')
</script>

<template>
  <input v-model="model" />
  <input v-model="count" />
</template>

<!-- Parent.vue -->
<template>
  <Child v-model="text" v-model:count="num" />
</template>
```

TypeScript:

```ts
const model = defineModel<string>()
const count = defineModel<number>({ default: 0 })
```

## provide / inject

Pass data down the component tree without prop drilling.

```vue
<!-- Ancestor.vue -->
<script setup>
import { provide, ref } from 'vue'

const count = ref(0)
provide('count', count)
provide('multiplier', 2)
</script>

<!-- Descendant.vue -->
<script setup>
import { inject } from 'vue'

const count = inject('count')
const multiplier = inject('multiplier', 1) // default value
</script>

<template>
  <span>{{ count }} * {{ multiplier }}</span>
</template>
```

Inject reactive values to preserve reactivity. For non-reactive primitives, use `ref()` when providing.

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

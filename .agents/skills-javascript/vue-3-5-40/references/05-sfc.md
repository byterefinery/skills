# Single-File Components (SFC)

The `*.vue` file format, `<script setup>`, compile-time macros, and style features.

## Table of Contents

- [SFC Structure](#sfc-structure)
- [<script setup>](#script-setup)
- [defineProps / defineEmits](#defineprops--defineemits)
- [defineModel (3.4+)](#definemodel-34)
- [defineExpose](#defineexpose)
- [defineOptions (3.3+)](#defineoptions-33)
- [defineSlots (3.5+)](#defineslots-35)
- [useSlots / useAttrs](#useslots--useattrs)
- [<style> Features](#style-features)
- [Pre-processors](#pre-processors)
- [Src Imports](#src-imports)
- [Custom Blocks](#custom-blocks)
- [How SFC Compilation Works](#how-sfc-compilation-works)

## SFC Structure

```vue
<template>
  <div class="example">{{ msg }}</div>
</template>

<script setup>
import { ref } from 'vue'
const msg = ref('Hello')
</script>

<style scoped>
.example {
  color: red;
}
</style>
```

- At most one `<template>` block
- At most one `<script>` and one `<script setup>` block
- Multiple `<style>` tags allowed
- Optional custom blocks (e.g., `<i18n>`, `<gql>`)

## <script setup>

Compile-time syntactic sugar for Composition API in SFCs. Code inside is compiled as the component's `setup()` function — executes **per instance**.

### Advantages

- Less boilerplate — no need to manually return state
- Top-level bindings automatically exposed to template
- Better runtime performance (no intermediate proxy)
- Better IDE type inference

### Basic Usage

```vue
<script setup>
import { ref, computed } from 'vue'

const count = ref(0)
const double = computed(() => count.value * 2)

function increment() {
  count.value++
}
</script>

<template>
  <button @click="increment">{{ count }} (x2 = {{ double }})</button>
</template>
```

All top-level variables, functions, and imports are directly usable in the template.

### Using Components

```vue
<script setup>
import MyComponent from './MyComponent.vue'
import * as Form from './form-components'
</script>

<template>
  <MyComponent />
  <Form.Input />  <!-- namespaced components -->
</template>
```

### Dynamic Components

```vue
<script setup>
import Foo from './Foo.vue'
import Bar from './Bar.vue'
</script>

<template>
  <component :is="Foo" />
  <component :is="condition ? Foo : Bar" />
</template>
```

### Normal <script> alongside <script setup>

Use normal `<script>` for things that run once at module level (not per instance):

```vue
<script>
// Runs once on import
export const customProps = {}
</script>

<script setup>
// Runs per instance
const count = ref(0)
</script>
```

## defineProps / defineEmits

Compile-time macros available only in `<script setup>`. No `import` needed.

### defineProps

```vue
<script setup>
// Runtime declaration
const props = defineProps({
  title: String,
  count: { type: Number, default: 0 },
  callback: Function
})

// TypeScript declaration
defineProps<{
  title?: string
  count?: number
  callback?: () => void
}>()
</script>
```

### withDefaults

```vue
<script setup>
withDefaults(
  defineProps<{
    title?: string
    count?: number
    items?: string[]
  }>(),
  {
    title: 'Hello',
    count: 0,
    items: () => ['default']
  }
)
</script>
```

### defineEmits

```vue
<script setup>
// Runtime
const emit = defineEmits(['change', 'delete'])
emit('change', newValue)

// TypeScript
const emit = defineEmits<{
  change: [value: string]
  delete: [id: number]
}>()

// Runtime with validation
const emit = defineEmits({
  change: (value) => typeof value === 'string',
  delete: (id) => typeof id === 'number'
})
</script>
```

## defineModel (3.4+)

Simplifies two-way binding. Replaces manual prop + emit pattern.

```vue
<script setup>
// Default model (modelValue / update:modelValue)
const model = defineModel()

// With default value
const count = defineModel({ default: 0 })

// TypeScript
const title = defineModel<string>()
const count = defineModel<number>({ default: 0 })

// Multiple models
const title = defineModel('title')
const count = defineModel('count', { default: 0 })

// With transformer
const model = defineModel({
  transformer: {
    toValue: (v) => parseInt(v),
    fromValue: (v) => String(v)
  }
})
</script>

<template>
  <input v-model="model" />
</template>
```

Parent usage:

```vue
<Child v-model="text" />
<Child v-model:title="title" v-model:count="count" />
```

## defineExpose

By default, `<script setup>` components are fully opaque to parent template refs. Use `defineExpose` to selectively expose properties.

```vue
<!-- Child.vue -->
<script setup>
import { ref } from 'vue'

const internal = ref('secret')
const publicData = ref('hello')

defineExpose({
  publicData
  // internal is NOT exposed
})
</script>

<!-- Parent.vue -->
<script setup>
import { ref } from 'vue'
import Child from './Child.vue'

const childRef = ref()
// childRef.value.publicData works
// childRef.value.internal is undefined
</script>
```

## defineOptions (3.3+)

Set component options directly in `<script setup>` without normal `<script>`:

```vue
<script setup>
defineOptions({
  inheritAttrs: false,
  name: 'MyComponent'
})
</script>
```

## defineSlots (3.5+)

Type-check slots in `<script setup>`:

```vue
<script setup>
defineSlots<{
  default(props: { item: string }): any
  header(props: { title: string }): any
}>()
</script>
```

## useSlots / useAttrs

Access slots and attrs programmatically (works outside `<script setup>` too):

```js
import { useSlots, useAttrs } from 'vue'

const slots = useSlots()
const attrs = useAttrs()

// Check if a slot exists
if (slots.header) {
  // slots.header({ title: 'Hello' })
}
```

## <style> Features

### scoped

Adds a unique data attribute to elements and scopes CSS to them:

```vue
<style scoped>
.example {
  color: red;
}
</style>

<!-- Compiled to: -->
<!-- .example[data-v-xxxx] { color: red; } -->
```

- Child component root elements are affected by both parent and child scoped styles
- Deep selectors: `:deep(.child)` targets nested elements in child components
- Slotted content: `:slotted(.header)` targets content passed via slots
- Global override: `:global(.class)` applies globally

### CSS Modules

```vue
<style module>
.red {
  color: red;
}
</style>

<script setup>
// Classes exposed as $style
console.log($style.red) // hashed class name
</script>

<template>
  <div :class="$style.red">Hello</div>
</template>
```

Custom injection name:

```vue
<style module="styles">
</style>

<!-- Access via $styles instead of $style -->
```

### Multiple Style Blocks

```vue
<style>
/* Global styles */
</style>

<style scoped>
/* Scoped styles */
</style>

<style module>
/* CSS modules */
</style>
```

## Pre-processors

Use `lang` attribute on any block:

```vue
<template lang="pug">
p {{ msg }}
</template>

<script lang="ts" setup>
import { ref } from 'vue'
const msg = ref('Hello')
</script>

<style lang="scss">
$primary: #333;
body { color: $primary; }
</style>
```

## Src Imports

Externalize blocks into separate files:

```vue
<template src="./template.html"></template>
<script src="./script.js"></script>
<style src="./style.css"></style>
```

## Custom Blocks

Project-specific blocks handled by tooling:

```vue
<i18n>
{
  "en": { "message": "Hello" },
  "ja": { "message": "こんにちは" }
}
</i18n>

<gql>
query { user { name } }
</gql>
```

## How SFC Compilation Works

1. `@vue/compiler-sfc` parses the `.vue` file into its blocks
2. `<template>` is pre-compiled into a JavaScript render function (with compile-time optimizations)
3. `<script setup>` is transformed into a `setup()` function
4. `<style>` tags are either injected as `<style>` tags (dev) or extracted into CSS (prod)
5. The compiled result is a standard ES module — importable like any `.js` file

Play with SFC compilation at [Vue SFC Playground](https://play.vuejs.org/).

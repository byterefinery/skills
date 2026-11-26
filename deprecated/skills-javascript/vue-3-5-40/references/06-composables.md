# Composables

The composable pattern for encapsulating and reusing stateful logic with the Composition API.

## Table of Contents

- [What is a Composable](#what-is-a-composable)
- [Basic Composable](#basic-composable)
- [Composable with Parameters](#composable-with-parameters)
- [Nested Composables](#nested-composables)
- [Side-Effect Cleanup](#side-effect-cleanup)
- [Convention and Naming](#convention-and-naming)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## What is a Composable

A composable is a function that leverages Vue's Composition API to encapsulate and reuse **stateful logic**. Unlike stateless utility functions (which take input and return output), composables manage state that changes over time and can hook into the component lifecycle.

## Basic Composable

```js // useMouse.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  function update(event) {
    x.value = event.pageX
    y.value = event.pageY
  }

  onMounted(() => window.addEventListener('mousemove', update))
  onUnmounted(() => window.removeEventListener('mousemove', update))

  return { x, y }
}
```

Usage in a component:

```vue
<script setup>
import { useMouse } from './useMouse.js'

const { x, y } = useMouse()
</script>

<template>
  <p>Mouse: {{ x }}, {{ y }}</p>
</template>
```

## Composable with Parameters

```js // useFetch.js
import { ref, watchEffect } from 'vue'

export function useFetch(url) {
  const data = ref(null)
  const error = ref(null)
  const loading = ref(true)

  watchEffect(async () => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(url.value)
      data.value = await response.json()
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  })

  return { data, error, loading }
}
```

Usage:

```vue
<script setup>
import { ref } from 'vue'
import { useFetch } from './useFetch.js'

const url = ref('https://api.example.com/data')
const { data, error, loading } = useFetch(url)
</script>
```

## Nested Composables

Composables can call other composables, enabling composition of complex logic from small units:

```js // useEventListener.js
import { onMounted, onUnmounted } from 'vue'

export function useEventListener(target, event, callback) {
  onMounted(() => target.addEventListener(event, callback))
  onUnmounted(() => target.removeEventListener(event, callback))
}
```

```js // useMouse.js (refactored)
import { ref } from 'vue'
import { useEventListener } from './useEventListener'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)

  useEventListener(window, 'mousemove', (event) => {
    x.value = event.pageX
    y.value = event.pageY
  })

  return { x, y }
}
```

## Side-Effect Cleanup

### Using onWatcherCleanup (3.5+)

```js
import { watch, onWatcherCleanup } from 'vue'

export function useAsyncData(id) {
  const data = ref(null)

  watch(id, (newId) => {
    const { response, cancel } = doAsyncWork(newId)
    onWatcherCleanup(cancel)
    data.value = await response
  })

  return { data }
}
```

### Using onCleanup callback parameter

```js
watch(id, async (newId, oldId, onCleanup) => {
  const { response, cancel } = doAsyncWork(newId)
  onCleanup(cancel)
  data.value = await response
})
```

### Using watchEffect

```js
watchEffect(async (onCleanup) => {
  const { response, cancel } = doAsyncWork(id.value)
  onCleanup(cancel)
  data.value = await response
})
```

## Convention and Naming

- Composable function names start with `use` (e.g., `useMouse`, `useFetch`, `useFormValidation`)
- This convention makes composables identifiable and aligns with Vue's own `use*` helpers (`useSlots`, `useAttrs`, `useTemplateRef`, `useId`)
- Place composables in a `composables/` or `use/` directory

## Best Practices

- **Call lifecycle hooks inside composables** — `onMounted()`, `onUnmounted()` etc. automatically associate with the current active component instance
- **Call composables synchronously** — must be called during the synchronous execution of `setup()` or `<script setup>`. Not inside `setTimeout`, async callbacks, or conditional blocks that may not execute during setup
- **Return refs, not raw values** — this preserves reactivity when the consumer destructures the return value
- **One responsibility per composable** — keep composables focused. Compose complex behavior from smaller composables
- **Document parameters and return values** — especially for shared composables

## Common Patterns

### State with Reset

```js
export function useResettableState(initial) {
  const state = ref(initial)

  function reset() {
    state.value = typeof initial === 'function' ? initial() : initial
  }

  return { state, reset }
}
```

### Debounced Ref

```js
import { ref, watch } from 'vue'

export function useDebounce(value, delay = 300) {
  const debounced = ref(value.value)
  const timer = ref(null)

  watch(value, (newVal) => {
    if (timer.value) clearTimeout(timer.value)
    timer.value = setTimeout(() => {
      debounced.value = newVal
    }, delay)
  })

  return debounced
}
```

### Toggle

```js
import { ref, computed } from 'vue'

export function useToggle(initial = false) {
  const value = ref(initial)

  function toggle() {
    value.value = !value.value
  }

  function set(val) {
    value.value = val
  }

  return { value: computed({ get: () => value.value, set }), toggle, set }
}
```

### Element Size Observer

```js
import { ref, onMounted, onUnmounted } from 'vue'

export function useElementSize(targetRef) {
  const width = ref(0)
  const height = ref(0)

  let observer

  onMounted(() => {
    observer = new ResizeObserver(([entry]) => {
      width.value = entry.contentRect.width
      height.value = entry.contentRect.height
    })
    observer.observe(targetRef.value)
  })

  onUnmounted(() => observer?.disconnect())

  return { width, height }
}
```

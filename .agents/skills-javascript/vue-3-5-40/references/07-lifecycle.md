# Lifecycle Hooks

Component lifecycle hooks for both Composition API and Options API.

## Table of Contents

- [Lifecycle Diagram](#lifecycle-diagram)
- [Composition API Hooks](#composition-api-hooks)
- [Options API Hooks](#options-api-hooks)
- [Setup Phase Rules](#setup-phase-rules)
- [Async Component Lifecycle](#async-component-lifecycle)
- [Suspense Lifecycle](#suspense-lifecycle)

## Lifecycle Diagram

```
                  ┌─ onBeforeMount / beforeMount
                  │
                  ├─ onMounted / mounted ◄── DOM created & inserted
                  │
                  ├─ onBeforeUpdate / beforeUpdate
                  │
                  ├─ onUpdated / updated ◄── DOM re-rendered & patched
                  │
                  ├─ onBeforeUnmount / beforeUnmount
                  │
                  └─ onUnmounted / unmounted ◄── component destroyed
```

Additional hooks: `onActivated`/`onDeactivated` (for `<KeepAlive>`), `onRenderTracked`/`onRenderTriggered` (debugging), `onErrorCaptured`, `onServerPrefetch`.

## Composition API Hooks

All hooks must be called **synchronously** during the `setup()` phase.

### onMounted

Called after the component and its synchronous children are mounted and their DOM trees are in the document.

```vue
<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('Component is mounted, DOM is ready')
  // Safe to access DOM elements here
})
</script>
```

Not called during server-side rendering.

### onUpdated

Called after the component's DOM has been updated due to a reactive state change. Multiple state changes in one tick are batched — this hook fires once after all updates.

```vue
<script setup>
import { onUpdated } from 'vue'

onUpdated(() => {
  console.log('DOM has been updated')
})
</script>
```

**Do not mutate state in `onUpdated`** — this leads to infinite update loops.

### onUnmounted

Called after the component is fully unmounted and all its child components are unmounted. Use for cleanup:

```vue
<script setup>
import { onUnmounted } from 'vue'

onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('resize', handler)
})
</script>
```

### onBeforeMount

Called right before the component performs the initial DOM insertion and creates its DOM tree.

### onBeforeUpdate

Called right before the DOM is about to be patched due to a reactive change. Use to access current DOM state before Vue updates it.

### onBeforeUnmount

Called right before a component instance is unmounted. The instance is still fully functional at this point.

### onActivated / onDeactivated

Called when a component wrapped in `<KeepAlive>` is inserted or removed.

```vue
<script setup>
import { onActivated, onDeactivated } from 'vue'

onActivated(() => {
  console.log('Component activated (visible)')
})

onDeactivated(() => {
  console.log('Component deactivated (cached)')
})
</script>
```

### onRenderTracked / onRenderTriggered

Debugging hooks for inspecting reactivity. Called when a reactive dependency is tracked or triggers a re-render.

```vue
<script setup>
import { onRenderTracked } from 'vue'

onRenderTracked((e) => {
  console.log({
    key: e.key,
    oldValue: e.oldValue,
    newValue: e.newValue,
    target: e.target,
    type: e.type,
    effect: e.effect
  })
})
</script>
```

### onErrorCaptured

Called when an error from a descendant component is captured. Returns `false` to prevent the error from propagating further.

```vue
<script setup>
import { onErrorCaptured } from 'vue'

onErrorCaptured((err, instance, info) => {
  console.error(`Error in ${info}:`, err)
  return false // prevent propagation
})
</script>
```

### onServerPrefetch

Called on the server before the mounted component is resolved and rendered. Use for async data fetching during SSR.

```vue
<script setup>
import { onServerPrefetch } from 'vue'

onServerPrefetch(async () => {
  // Fetch data on the server before rendering
  data.value = await fetch('/api/data')
})
</script>
```

## Options API Hooks

```js
export default {
  beforeMount() {
    // Before initial DOM creation
  },
  mounted() {
    // DOM created and inserted
  },
  beforeUpdate() {
    // Before DOM re-render
  },
  updated() {
    // After DOM re-render
  },
  beforeUnmount() {
    // Before unmount
  },
  unmounted() {
    // After unmount
  },
  activated() {
    // KeepAlive activated
  },
  deactivated() {
    // KeepAlive deactivated
  },
  errorCaptured(err, instance, info) {
    // Error from descendant
  }
}
```

Arrow functions should be avoided in Options API hooks — they don't have access to `this`.

## Setup Phase Rules

Composition API lifecycle hooks must be called during the synchronous execution of `setup()`:

```js
// ✅ Correct — called synchronously during setup
onMounted(() => { /* ... */ })

// ❌ Wrong — called asynchronously, no active instance
setTimeout(() => {
  onMounted(() => { /* won't work */ })
}, 100)

// ✅ Correct — called in an external function, but invoked synchronously from setup
function setupLogic() {
  onMounted(() => { /* ... */ })
}
setupLogic()
```

The hook doesn't need to be lexically inside `setup()` or `<script setup>` — it just needs to be in the synchronous call stack originating from setup.

## Async Component Lifecycle

Async components defined with `defineAsyncComponent()` have their own loading states:

```js
import { defineAsyncComponent } from 'vue'

const AsyncComp = defineAsyncComponent({
  loader: () => import('./MyComponent.vue'),
  loadingComponent: LoadingComponent,  // shown during loading
  errorComponent: ErrorComponent,      // shown on error
  delay: 200,                          // ms before showing loading component
  timeout: 3000,                       // ms before showing error
  onError(error) {
    // Retry logic
  }
})
```

## Suspense Lifecycle

Components inside `<Suspense>` have additional async handling:

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

- `onMounted` is called when the component is mounted in the `#default` slot (after all async dependencies are resolved)
- Use `onServerPrefetch` for server-side data fetching before the component renders

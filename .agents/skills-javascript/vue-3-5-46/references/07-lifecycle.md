# Lifecycle hooks

Source: `packages/runtime-core/src/apiLifecycle.ts` (v3.5.46). Every hook below is exported there.

## Component hooks

| Hook | When it runs |
|---|---|
| `onBeforeMount` | before the mounted DOM is patched |
| `onMounted` | after the component is mounted |
| `onBeforeUpdate` | before the re-render caused by state changes |
| `onUpdated` | after the re-render / DOM patch |
| `onBeforeUnmount` | before unmount |
| `onUnmounted` | after unmount (cleanup listeners, intervals, etc.) |
| `onServerPrefetch` | SSR only — prefetch data on the server before rendering |
| `onActivated` / `onDeactivated` | KeepAlive activation/deactivation (exported from `components/KeepAlive.ts`) |

## Error capture

- `onErrorCaptured(hook, target?)` — hook receives `(err, instance, info)`; return `false` to stop propagation (per the `ErrorCapturedHook` type in apiLifecycle.ts).

## Debug hooks

- `onRenderTriggered` / `onRenderTracked` — `DebuggerHook` callbacks receiving `DebuggerEvent` (used by devtools/profiling; types `DebuggerOptions`, `DebuggerEventExtraInfo` come from the reactivity effect API).

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
## Notes from the implementation

- Hooks are created by a `createHook(lifecycle)` factory that injects into `currentInstance` — call them **synchronously** in `setup()` / `<script setup>` top level. The dev warning for async setup says hooks before the first `await` are fine ("hooks before the first await statement"), so top-level-of-setup registration is the requirement, not "no awaits at all".
- Post-create hooks are no-ops during SSR except `onServerPrefetch` (`isInSSRComponentSetup` check in apiLifecycle.ts).
- `injectHook(lifecycle, hook, target?)` is exported for custom renderers to add their own lifecycle points.

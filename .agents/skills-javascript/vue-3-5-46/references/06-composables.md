# Composables

Source: `packages/vue/examples/composition/` (state logic in `setup()`), reactivity effect-scope APIs in `packages/reactivity/src/index.ts`, lifecycle hooks in `packages/runtime-core/src/apiLifecycle.ts`, in the v3.5.46 tree.

A composable is a plain function that packages reusable **stateful** logic built on the Composition API — refs, reactive state, computed values, watchers, event listeners, and cleanup — and returns the pieces the component needs. The composition examples (`grid.html`, `commits.html`, `markdown.html`) demonstrate the pattern inline inside `setup()`; extracting that logic into a named function is the composable idiom.

## Shape

```js
import { ref, computed, onMounted, onUnmounted } from 'vue'

function useCounter(initial = 0) {
  const count = ref(initial)
  const double = computed(() => count.value * 2)
  function increment() { count.value++ }
  onMounted(() => { /* start interval, bind listeners */ })
  onUnmounted(() => { /* clear interval, remove listeners */ })
  return { count, double, increment }
}
```

Rules that follow from how the runtime works:

- Call composables **inside `setup()`** (or inside another composable) so `getCurrentInstance()`-dependent APIs (`onMounted`, `provide/inject`, `useModel`, `useTemplateRef`, `useId`) resolve to the calling component.
- Hooks must be registered synchronously during setup (not in async callbacks) — the lifecycle hook factories (`createHook` in apiLifecycle.ts) bind to `currentInstance`.
- Return reactive bindings (`ref`/`reactive`/`computed`) rather than plain values when the consumer needs reactivity; refs auto-unwrap in templates.
- Pair every side effect with cleanup: `onUnmounted` for component lifetime, or `onScopeDispose` / `onWatcherCleanup` / `onEffectCleanup` for scope- and effect-level cleanup.

## Scopes (from the reactivity API)

- `effectScope()` — run reactive effects in a scope and dispose them all at once; `EffectScope` type, `getCurrentScope()`, `onScopeDispose()`.
- `onWatcherCleanup()` — register cleanup for a watcher's runner (3.5-era API, exported in this version).
- `pauseTracking()` / `resetTracking()` / `enableTracking()` — temporarily suspend and restore dependency tracking around imperative code.

## The examples' own patterns

- **`grid.html` (composition)** — `setup(props)` derives initial `sortOrders` from `props.columns`, keeps UI state in `reactive({ sortKey, sortOrders })`, exposes `filteredData = computed(...)`; returns everything for template binding.
- **`markdown.html` (composition)** — `ref('# hello')` input, `computed` output, and a debounced `update` function (lodash `_.debounce`) as the side-effect glue.
- **`commits.html` (composition)** — fetches data in `setup()`, stores results in refs, demonstrates async setup logic.
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

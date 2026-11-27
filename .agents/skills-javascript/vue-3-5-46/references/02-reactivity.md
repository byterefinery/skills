# Reactivity API

Source: `packages/reactivity/src/index.ts` and `packages/reactivity/README.md` in the v3.5.46 tree.

## API surface (complete)

- **Refs** — `ref`, `shallowRef`, `isRef`, `toRef`, `toValue`, `toRefs`, `unref`, `proxyRefs`, `customRef`, `triggerRef`; types `Ref`, `MaybeRef`, `MaybeRefOrGetter`, `ToRef`, `ToRefs`, `UnwrapRef`, `ShallowRef`, `ShallowUnwrapRef`, `RefUnwrapBailTypes`, `CustomRefFactory`.
- **Reactive / readonly** — `reactive`, `readonly`, `isReactive`, `isReadonly`, `isShallow`, `isProxy`, `shallowReactive`, `shallowReadonly`, `markRaw`, `toRaw`, `toReactive`, `toReadonly`; types `Raw`, `DeepReadonly`, `ShallowReactive`, `UnwrapNestedRefs`, `Reactive`, `ReactiveMarker`.
- **Computed** — `computed` (getter, or getter+setter options for a writable computed); types `ComputedRef`, `WritableComputedRef`, `WritableComputedOptions`, `ComputedGetter`, `ComputedSetter`, `ComputedRefImpl`.
- **Effects** — `effect`, `stop`, `enableTracking`, `pauseTracking`, `resetTracking`, `onEffectCleanup`, `ReactiveEffect`, `EffectFlags`; types `ReactiveEffectRunner`, `ReactiveEffectOptions`, `EffectScheduler`, `DebuggerOptions`, `DebuggerEvent`, `DebuggerEventExtraInfo`.
- **Tracking internals** — `trigger`, `track`, `ITERATE_KEY`, `ARRAY_ITERATE_KEY`, `MAP_KEY_ITERATE_KEY`.
- **Scopes** — `effectScope`, `EffectScope`, `getCurrentScope`, `onScopeDispose`.
- **Watch** — `watch`, `getCurrentWatcher`, `traverse`, `onWatcherCleanup`, `WatchErrorCodes`; types `WatchOptions`, `WatchScheduler`, `WatchStopHandle`, `WatchHandle`, `WatchEffect`, `WatchSource`, `WatchCallback`, `OnCleanup`. (`watchEffect`, `watchPostEffect`, `watchSyncEffect` are exported by `@vue/runtime-core` from `apiWatch.ts`.)
- **Constants** — `TrackOpTypes`, `TriggerOpTypes`, `ReactiveFlags`; array instrumentation helpers `reactiveReadArray`, `shallowReadArray`.

## Usage notes

- Implementation is Proxy-based; the README credits Meteor Tracker, nx-js/observer-util, and salesforce/observable-membrane as prior art.
- The package is inlined into the global and browser-ESM builds of the user-facing renderers (`@vue/runtime-dom`), and is also published standalone. **Do not** use the standalone build alongside a pre-bundled renderer build — internal storage for reactivity connections differs. A user-facing renderer re-exports all APIs from this package.

## watch() and watchEffect()

### watchEffect()

Runs immediately, tracks all accessed reactive dependencies, re-runs when they change.

```js
import { watchEffect } from 'vue'

watchEffect(() => {
  console.log(count.value) // runs immediately, re-runs on count changes
})
```

Return value is a handle with `stop()`, `pause()`, `resume()`:

```js
const { stop, pause, resume } = watchEffect(() => {})
pause() // temporarily pause
resume() // resume
stop() // stop permanently
```

Side-effect cleanup:

```js
import { onWatcherCleanup } from 'vue'

watchEffect(async () => {
  const { response, cancel } = doAsyncWork(id.value)
  onWatcherCleanup(cancel)
  data.value = await response
})
```

### watch()

Lazy — callback only fires when watched source changes. Accesses both new and old values.

```js
import { watch } from 'vue'

// Watch a ref
watch(count, (newVal, oldVal) => {
  console.log(`count changed from ${oldVal} to ${newVal}`)
})

// Watch a getter
watch(() => state.count, (newVal, oldVal) => { /* ... */ })

// Watch multiple sources
watch([fooRef, barRef], ([newFoo, newBar], [oldFoo, oldBar]) => { /* ... */ })
```

Options:

```js
watch(source, callback, {
  immediate: true,   // trigger on creation
  deep: true,        // deep traversal (3.5+: can be a number for max depth)
  flush: 'post',     // 'pre' (default), 'post', or 'sync'
  once: true         // run only once (3.4+)
})
```

`flush: 'pre'` (default): runs before component rendering. `flush: 'post'`: runs after. `flush: 'sync'`: triggers immediately on every change (use with caution).

### watch vs watchEffect

| | watch | watchEffect |
|---|---|---|
| Lazy | Yes — only on source change | No — runs immediately |
| Specific source | Yes — explicit source | No — auto-tracks all accessed deps |
| Old value | Yes | No |

## Shallow APIs

Opt out of deep reactivity for performance or external state management.

- **`shallowRef()`** — only `.value` access is tracked, inner object not made reactive
- **`shallowReactive()`** — only root-level properties are reactive, nested objects not converted
- **`shallowReadonly()`** — only root-level is readonly

```js
import { shallowRef } from 'vue'

const bigData = shallowRef(largeObject)
bigData.value = newObject // tracked
bigData.value.nested.prop = 1 // NOT tracked
```

Use for large immutable structures, or when inner state is managed by an external library.

## readonly() and toRaw()

### readonly()

Returns a deep readonly proxy. Reads are tracked for reactivity, writes fail with a warning.

```js
import { readonly, reactive } from 'vue'

const original = reactive({ count: 0 })
const copy = readonly(original)

watchEffect(() => console.log(copy.count)) // tracks changes
original.count++ // triggers watcher
copy.count++ // warning!
```

### toRaw()

Returns the original object from a reactive/readonly proxy. Use sparingly — bypasses reactivity.

```js
import { reactive, toRaw } from 'vue'

const state = reactive({ count: 0 })
const raw = toRaw(state)
```

### markRaw()

Marks an object as never reactive. `reactive(markRaw(obj))` returns the original object.

```js
import { markRaw, reactive } from 'vue'

const nonReactive = markRaw({ count: 0 })
console.log(reactive(nonReactive) === nonReactive) // true
```

Use for objects that should never be proxied: third-party class instances, Vue component objects, etc.

## Caveats

- Built-in objects are **not** observed, except `Array`, `Map`, `WeakMap`, `Set`, `WeakSet` (package README).
- `reactive()` takes objects; use `ref()` for primitives (strings, numbers, booleans).
- Destructuring a reactive object loses the reactive connection — use `toRefs()`.
- Refs auto-unwrap in templates but require `.value` in JavaScript code.
## Utility Functions

| Function | Description |
|---|---|
| `isRef()` | Check if a value is a ref |
| `unref()` | Return `.value` if ref, else the value itself |
| `toRef(obj, key)` | Create a ref from an object property, keeping reactivity connection |
| `toRefs(obj)` | Convert a reactive object to a plain object where all properties are refs |
| `toValue()` | (3.3+) Normalize ref/getter/value to a value |
| `triggerRef()` | Force trigger effects tracking a shallow ref |
| `proxyRefs()` | Proxy an object where refs are auto-unwrapped (for destructuring reactive objects) |

```js
import { toRefs } from 'vue'

const state = reactive({ count: 0, status: 'idle' })
const { count, status } = toRefs(state) // refs, still connected to state
```

## Reactivity Internals

Vue's reactivity uses a dependency-tracking system:

1. **Track**: When a reactive property is read during an effect (render, computed, watch), the effect is recorded as a dependency
2. **Trigger**: When a reactive property is mutated, all effects tracking that property are re-run

Refs use getter/setter on `.value` for interception. Reactive objects use JavaScript Proxies to intercept all property access/mutation.

## DOM Update Timing

DOM updates are batched asynchronously. Use `nextTick()` to wait for DOM updates:

```js
import { nextTick } from 'vue'

async function increment() {
  count.value++
  await nextTick()
  // DOM is now updated
  console.log(document.getElementById('count').textContent)
}
```

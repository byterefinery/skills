# Reactivity System

Vue's dependency-tracking reactivity system using `ref()`, `reactive()`, `computed()`, `watch()`, and `watchEffect()`.

## Table of Contents

- [ref()](#ref)
- [reactive()](#reactive)
- [computed()](#computed)
- [watch() and watchEffect()](#watch-and-watcheffect)
- [Shallow APIs](#shallow-apis)
- [readonly() and toRaw()](#readonly-and-toraw)
- [Utility Functions](#utility-functions)
- [Reactivity Internals](#reactivity-internals)
- [DOM Update Timing](#dom-update-timing)

## ref()

Creates a reactive mutable ref object with a `.value` property. Primary API for declaring reactive state.

```js
import { ref } from 'vue'

const count = ref(0)
console.log(count.value) // 0
count.value++
console.log(count.value) // 1
```

- Auto-unwrapped in templates: `{{ count }}` (no `.value` needed)
- Object values are made deeply reactive internally via `reactive()`
- Nested refs inside objects are deeply unwrapped
- Can hold any type including primitives

```js
const count = ref(0)
const state = reactive({ count })
console.log(state.count) // 0 (auto-unwrapped as reactive property)
state.count = 1
console.log(count.value) // 1 (stays in sync)
```

### Caveats

- **Arrays/collections**: refs inside reactive arrays or Maps are NOT auto-unwrapped — use `.value`
- **Template unwrapping**: only applies to top-level properties in render context. `object.id` where `id` is a ref won't auto-unwrap in expressions like `{{ object.id + 1 }}`

## reactive()

Returns a reactive proxy of an object. Deep conversion — all nested objects become reactive when accessed.

```js
import { reactive } from 'vue'

const state = reactive({ count: 0 })
state.count++
```

- Works only on object types (objects, arrays, Map, Set)
- Returns a Proxy — `reactive(obj) === obj` is `false`
- Always use the proxy, never the original

### Limitations

1. Cannot hold primitive types (string, number, boolean)
2. Cannot replace entire object — reactivity connection is lost:
   ```js
   let state = reactive({ count: 0 })
   state = reactive({ count: 1 }) // lost connection to first proxy
   ```
3. Destructuring loses reactivity:
   ```js
   const state = reactive({ count: 0 })
   let { count } = state // disconnected from state.count
   count++ // does not affect original state
   ```

Due to these limitations, prefer `ref()` as the primary reactive state API.

## computed()

Creates a readonly reactive ref derived from other reactive values. Cached based on dependencies — only re-evaluates when dependencies change.

```js
import { ref, computed } from 'vue'

const count = ref(0)
const double = computed(() => count.value * 2)

console.log(double.value) // 0
count.value++
console.log(double.value) // 2
```

### Writable Computed

```js
const fullName = computed({
  get() {
    return firstName.value + ' ' + lastName.value
  },
  set(newValue) {
    [firstName.value, lastName.value] = newValue.split(' ')
  }
})
```

### Previous Value (3.4+)

```js
const alwaysSmall = computed((previous) => {
  if (count.value <= 3) return count.value
  return previous
})
```

### Best Practices

- Getters should be pure — no side effects, no async, no DOM mutations
- Treat computed return values as read-only snapshots
- Use methods instead of computed when you don't want caching

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

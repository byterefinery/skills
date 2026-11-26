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

## Caveats

- Built-in objects are **not** observed, except `Array`, `Map`, `WeakMap`, `Set`, `WeakSet` (package README).
- `reactive()` takes objects; use `ref()` for primitives (strings, numbers, booleans).
- Destructuring a reactive object loses the reactive connection — use `toRefs()`.
- Refs auto-unwrap in templates but require `.value` in JavaScript code.

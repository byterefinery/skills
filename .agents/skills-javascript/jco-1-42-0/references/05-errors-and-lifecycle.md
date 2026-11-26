# Errors, traps, and instance lifecycle

Source material: jco book chapters *Transpiling* (generated utilities, instantiation), *WIT Type representations* (results), *Advanced: Detecting traps, Stopping running instances, Tracking individual calls* (docs at tag jco-v1.42.0).

## Error wrapping (ComponentError)

- Jco CLI and `@bytecodealliance/jco` wrap a top-level `result::err` in a generated `ComponentError` by default (an `Error` with a `payload` property holding the lifted error value). Pass `--no-component-error-wrapping` (CLI) or `noComponentErrorWrapping: true` (jco-transpile) to throw the payload directly. `@bytecodealliance/jco-transpile` throws the payload directly by default; `noComponentErrorWrapping: false` requests the wrapper.
- When wrapping is enabled, bindings expose `_util.isComponentError(value)`:
  - For default ESM output: `import { _util } from './component.js'`.
  - For explicit instantiation: `instance._util.isComponentError(value)`.
  - Uses `instanceof` against a private constructor, so it only recognizes errors from the same module/instance; returns `false` for host exceptions, errors from other instances, and plain objects with a `payload` property. Absent when bindings do not use wrapping. In TypeScript it narrows to `Error & { readonly payload: unknown }`.

```js
try {
  await fallible.f(42);
} catch (error) {
  if (_util.isComponentError(error)) {
    console.error('Declared WIT error:', error.payload);
  } else {
    throw error;
  }
}
```

- With `typedErrorClasses`/`--typed-error-classes` enabled (requires wrapping), each named error type of a function gets an exported class named after the type with an `Error` suffix (e.g. `fallible.ErrorCodeError`), which also satisfies `isComponentError`. No class is generated for anonymous error types, name-colliding types, or functions the world exports directly — those throw the wrapper itself. Generated declarations state what each function throws in a `@throws` tag.

## Traps

- **Traps are not `ComponentError` instances.** They are `WebAssembly.RuntimeError`, and `isComponentError()` returns `false` for them. Handle them separately.
- With explicit instantiation, pass `options.onTrap` to receive traps: called once per trap as soon as it happens, including background traps after starting calls have returned and deadlocks. It runs mid-unwinding — it may call `_util.stop()` but should not otherwise use the instance; an exception it throws is left uncaught.
- A host import throwing something other than `WebAssembly.RuntimeError` is not a trap and is not reported (the host knows it threw).

## Stopping instances

- `instance._util.stop()` (instantiation mode) or the exported `_util.stop()` (default ESM) permanently stops the instantiation, including background guest work, and disposes guest-owned host resources.
- `instance._util.whenIdle()` waits for guest task exit, including background work after an export returns; it also resolves when the instance stops or traps. Use it for orderly shutdown before `stop()`.

## Call tracking

`jco transpile --call-tracking` emits optional invocation handles: `_util.calls.start(fn, ...args)` returns a handle with a separate `finished` promise for the selected guest execution.

## Host-side idiomatic errors

Host implementations of `result`-returning imports can throw real `Error` objects: jco extracts a `payload` property from thrown `Error`s as the result error type, so `Object.assign(new Error('...'), { payload: 1111 })` maps to the WIT error value.

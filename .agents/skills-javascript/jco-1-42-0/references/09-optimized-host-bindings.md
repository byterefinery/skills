# Optimized host bindings

Source material: jco book chapter *Host Bindings* (docs at tag jco-v1.42.0).

Default host bindings in Jco are high-level JS bindgen: every import is a normal JS function, so hosts can `import { getRandomBytes } from 'wasi:random/random'` and provide custom or virtual implementations using the same conventions. For performance-sensitive hosts, Jco also supports optimized (low-level) bindgen that bypasses the component-model lowering layer.

## Import bindings modes

`jco transpile --import-bindings [mode]` (same control via `--jco-import-bindings` for `jco run`/`jco serve`):

| Mode | Behavior |
|---|---|
| `js` (default) | High-level JS bindings for all imports |
| `hybrid` | High-level bindgen for all imports, but check each function for `Symbol.for('cabiLower')` and use the optimized bindgen when available |
| `optimized` | Omit the high-level JS bindgen for imports; use the low-level bindgen directly, assuming `Symbol.for('cabiLower')` is defined on all imports |
| `direct-optimized` | Assume the imports themselves are low-level functions (no `Symbol.for('cabiLower')` lookup); useful in instantiation mode |

This scheme implies instantiation mode to supply the host bindings, or a host that provides imports as ESM imports.

## `fn[Symbol.for('cabiLower')](canonOpts) -> coreFn`

A function with a native optimized implementation exposes it through `Symbol.for('cabiLower')`, taking a `canonOpts` object with these fields, as needed:

- `memory` — the component's `WebAssembly.Memory`
- `realloc` — the component's realloc function, per component model canonical-definition semantics
- `postReturn` — the post-return function for the call
- `stringEncoding` — default `'utf8'`
- `resourceTables` — ordered list of the resource tables (`ResourceTable[]`) in which the function's resource parameters and results uniquely appear

The returned `coreFn` is an optimized native function to provide as a direct core-function import to `WebAssembly.instantiate` of the component's core binary — a host-native binding with no intermediate component-model lowering.

```js
function hostFn(/* high-level JS binding */) {}
hostFn[Symbol.for('cabiLower')] = function (canonOpts) {
  // return the optimized core function
};
```

## `ResourceTable: number[]`

Resource handles are tracked in handle tables — shared slab data structures relating handles to resource representations (reps); each resource usually has a unique table per component. Optimized bindgen mutates these tables (e.g., resource creation writes an own handle into the *caller's* table), so full component model semantics must be followed.

Implementation: a JS array of integers (not typed arrays, for resizability without reserving a large buffer). Each entry is a pair of JS numbers, either a free-list entry or a data entry. Ownership is stored above the 32-bit rep as an offset of `T_OWN = 2 ** 32`; bit 30 (`T_FLAG = 1 << 30`) is used only in the scope slot to mark free entries.

- **Free-list entries** — bit 30 set on the first value. The pair at indices 0,1 is the free-list head, initially `1 << 30, 0`; clearing the flag gives 0, the end of the free list.
- **Data entries** — first value is a u30 scope (ref count for own handles, scope id for borrow handles; bit 30 never set); second value is the unsigned rep plus `T_OWN` for own handles. An entry is owned when the second value is at least `T_OWN`; its rep is the value modulo `T_OWN`.

Free-list numbering and handle numbering are the same, indexed by pair: handle `n` is at indices `n * 2` (scope) and `n * 2 + 1` (rep + ownership). A scope with bit 30 set means an invalid handle (throw). A zero rep is valid; only handle index 0 is reserved. Reps are normalized to unsigned 32-bit values (including capture-table keys), so a signed i32 and the corresponding u32 identify the same rep.

## Resource symbols

- **`resourceInstance[Symbol.for('cabiRep')]`** — normally imported resource classes need no special symbols (reps are assigned when passed in). But with `hybrid`/`optimized` bindgen, any high-level resource instance that crosses into low-level bindgen MUST define `Symbol.for('cabiRep')`:

  ```js
  class MyResource {
    constructor(rep) {
      this[Symbol.for('cabiRep')] = rep;
    }
  }
  ```

- **`ResourceClass[Symbol.for('cabiDispose')](rep)`** — optional static destructor on imported resource classes for low-level bindgen (the low-level analogue of `Symbol.dispose`). Unlike the other low-level functions it is called directly, unbound, taking the rep.

Externally created resources passed into high-level functions are always explicitly *captured*, even when they define `cabiRep`; in capture cases `resourceInstance[Symbol.dispose]()` is called instead of `cabiDispose` (even if `Symbol.dispose` is not defined), so custom GC hooks still apply.

## When to use

- **`js`** — default; easiest to reason about, works everywhere
- **`hybrid`** — best balance: high-level by default, optimized when available
- **`optimized`** — maximum performance; every import must implement `cabiLower`
- **`direct-optimized`** — instantiation mode where imports are already low-level functions

## Gotchas

- **Full component model semantics required** — optimized bindgen must follow the component model exactly when mutating shared handle tables
- **Resource tables are shared mutable state** — great care needed when operating on them
- **`cabiRep` needed for cross-boundary resources** — high-level resources passed to low-level functions must define the symbol
- **Externally created resources are captured** — they use `Symbol.dispose` even with `cabiRep` defined

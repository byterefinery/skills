# Optimized Host Bindings

## Overview

Default host bindings use high-level JS bindgen — all imports are normal JS functions. For performance-sensitive applications, jco supports optimized (low-level) bindgen that bypasses the component model lowering layer.

## Import Bindings Modes

Control with `--import-bindings` during transpilation:

| Mode | Description |
|---|---|
| `js` (default) | High-level JS bindings for all imports |
| `hybrid` | High-level with `Symbol.for('cabiLower')` fallback per function |
| `optimized` | Low-level only; assumes `cabiLower` on all imports |
| `direct-optimized` | Imports are assumed to be low-level functions directly (instantiation mode) |

```bash
jco transpile component.wasm --import-bindings hybrid -o out-dir
```

## cabiLower Protocol

Functions with native optimized implementations expose `Symbol.for('cabiLower')`:

```js
function hostFn(canonOpts) {
  // Returns an optimized core function for direct WebAssembly.instantiate
}
hostFn[Symbol.for('cabiLower')] = function(canonOpts) {
  // Return optimized core function
};
```

### canonOpts

```ts
interface CanonOpts {
  memory?: WebAssembly.Memory;
  realloc?: (ptr: number, oldLen: number, align: number, newLen: number) => number;
  postReturn?: () => void;
  stringEncoding?: 'utf8';  // default
  resourceTables?: number[][];
}
```

## ResourceTable

Resource handles are tracked in shared slab data structures (JS arrays of integers):

- Each entry is a pair of u32s (free list entry or data entry)
- Lowest 29 bits for data, flag bit at 1 << 30
- Highest bit avoided to prevent SMI deoptimization

### Free List Entries

High bit set on first value indicates free list. Entry at indices 0,1 is the head.

### Data Entries

- First value: scope (ref count for own handles, scope id for borrow handles)
- Second value: rep (resource representation), high bit indicates own handle

Access handle `n` at indices `n * 2` and `n * 2 + 1`.

## Resource Symbols

### cabiRep

High-level resource instances must define `Symbol.for('cabiRep')` to interact with low-level bindgen:

```js
class MyResource {
  constructor(rep) {
    this[Symbol.for('cabiRep')] = rep;
  }
}
```

### cabiDispose

Optional destructor as static method on resource class:

```js
class MyResource {
  static[Symbol.for('cabiDispose')](rep) {
    // Clean up internal state for rep
  }
}
```

Unlike `Symbol.dispose`, `cabiDispose` takes the rep directly and is called by low-level bindgen.

## When to Use

- **`js`** — default, easiest to reason about, works everywhere
- **`hybrid`** — best balance; high-level by default, optimized when available
- **`optimized`** — maximum performance; requires all imports to implement `cabiLower`
- **`direct-optimized`** — for instantiation mode where imports are already low-level

## Gotchas

- **Full component model semantics required** — optimized bindgen must follow component model exactly
- **Resource tables are shared state** — great care needed when mutating handle tables
- **`cabiRep` needed for cross-boundary resources** — high-level resources passed to low-level functions must define the symbol
- **External resources are captured** — externally created resources use `Symbol.dispose` even with `cabiRep`

# JavaScript SDK

## Installation

```sh
npm install usearch
```

Supports Node.js (native addon) and WASM environments.

## Quickstart

```js
const assert = require('node:assert');
const usearch = require('usearch');

const index = new usearch.Index({
  metric: 'l2sq',
  connectivity: 16,
  dimensions: 3,
});

// Keys are BigInt (note the 'n' suffix)
index.add(42n, new Float32Array([0.2, 0.6, 0.4]));

const results = index.search(new Float32Array([0.2, 0.6, 0.4]), 10);

assert(index.size() === 1);
assert.deepEqual(results.keys, new BigUint64Array([42n]));
assert.deepEqual(results.distances, new Float32Array([0]));

index.remove(42n);
```

> **Keys are always `BigInt`** — use `42n`, not `42`. This is the most common source of errors.

## Advanced Configuration

```js
const index = new usearch.Index({
  dimensions: 128,
  metric: 'ip',
  quantization: 'f32',     // 'bf16', 'f16', 'e5m2', 'e4m3', 'e3m2', 'e2m3', 'u8', 'i8', 'b1'
  connectivity: 10,
  expansion_add: 5,
  expansion_search: 3,
  multi: true,              // Multiple vectors per key
});
```

## Batch Operations

Use flattened `TypedArray` (not array of arrays) for performance:

```js
const keys = new BigUint64Array([15n, 16n]);
const vectors = new Float32Array([10, 20, 10, 25]);  // 2 vectors of dim 2

index.add(keys, vectors);

// Batch search
const batchResults = index.search(vectors, 2);
const firstMatch = batchResults.get(0);

// Multi-threaded batch ops (0 = auto-detect)
const threads = 0;
index.add(keys, vectors, threads);
const results = index.search(vectors, 2, threads);
```

## Serialization

```js
index.save('index.usearch');   // Save to file
index.load('index.usearch');   // Load into memory (writable)
index.view('index.usearch');   // Memory-map (read-only)
```

## Index Introspection

```js
const dimensions = index.dimensions();
const size = index.size();
const capacity = index.capacity();
const containsKey = index.contains(42n);
const count = index.count(42n);  // Number of vectors for a key (multi-vector indexes)
```

## Gotchas

- **BigInt keys** — always use `42n` syntax. Regular numbers will fail.
- **TypedArrays only** — vectors must be `Float32Array`, `Float64Array`, `Int8Array`, etc. Plain arrays are not accepted.
- **Flattened batch data** — batch vectors are a single flat `TypedArray`, not nested arrays. For 3 vectors of dim 4: `new Float32Array([v1a, v1b, v1c, v1d, v2a, ...])`.
- **WASM vs native** — the npm package ships native addons for Node.js. For browser/WASM usage, check the repository for the WASM build.

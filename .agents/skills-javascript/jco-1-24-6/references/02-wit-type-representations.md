# WIT Type Representations

## Basic Types

| WIT type | JS Type |
|---|---|
| `u8` | `number` |
| `u16` | `number` |
| `u32` | `number` |
| `u64` | `BigInt` |
| `s8` | `number` |
| `s16` | `number` |
| `s32` | `number` |
| `s64` | `BigInt` |
| `f32` | `number` |
| `f64` | `number` |
| `bool` | `boolean` |
| `char` | `string` |
| `string` | `string` |

## Variants

Variants are represented as objects with a `tag` and optional `val`:

```wit
variant filter {
    all,
    none,
    some(list<string>),
}
```

JS representation:

```js
// all — no val
{ tag: 'all' }

// none — no val
{ tag: 'none' }

// some — with val
{ tag: 'some', val: ['a', 'b', 'c'] }
```

> Variants can only hold one piece of data per alternative. Use a `tuple` or `record` as the contained type for multiple values.

## Records

Records become plain JS objects:

```wit
record person {
    name: string,
    age: u32,
    favorite-color: option<string>,
}
```

```ts
interface Person {
  name: string;
  age: number;
  favoriteColor?: string;
}
```

## Options

Single-level `option<T>` maps to `T | undefined`:

```wit
option<u32>
```

```ts
number | undefined
```

In function arguments/returns, omit the parameter or pass `undefined`:

```wit
interface optional {
    f: func(n: option<u32>) -> string;
}
```

```ts
function f(n?: number): string {
  if (n === undefined) return 'no n';
  return 'n provided';
}
```

In records, options become optional properties (`prop?: T`).

### Nested options

`option<option<T>>` uses the tagged form to distinguish missing from empty:

```ts
{ tag: 'some', val: { tag: 'some', val: 42 } }  // Some(Some(42))
{ tag: 'some', val: { tag: 'none' } }            // Some(None)
{ tag: 'none' }                                   // None
```

## Results

### As function return values

When `result` is a direct return, throw for error:

```wit
add-overflow: func(lhs: u32, rhs: u32) -> result<u32, string>;
```

```js
function addOverflow(lhs, rhs) {
  let sum = lhs + rhs;
  if (sum > 4294967295) throw 'u32 overflow';
  return sum;
}
```

### In container types

When `result` is inside a record, tuple, or function parameter, use tagged form:

```ts
type Result<T, E> = { tag: 'ok', val: T } | { tag: 'err', val: E };

function handle(input: Result<string, string>): string {
  switch (input.tag) {
    case 'ok': return `SUCCESS: ${input.val}`;
    case 'err': return `ERROR: ${input.val}`;
  }
}
```

### Idiomatic JS errors in host functions

When implementing host functions that throw, use `Error` with a `payload` property:

```js
function justThrow() {
  const err = new Error('Error for JS users');
  err.payload = 1111;  // This becomes the result error value
  throw err;
}
```

jco extracts `payload` from thrown `Error` objects as the result error type.

## Tuples

Tuples become JS arrays:

```wit
tuple<u32, u32>
tuple<string, u32>
```

```ts
[number, number]
[string, number]
```

## Lists

```wit
list<u8>
list<string>
list<u32>
```

| WIT | JS |
|---|---|
| `list<u8>` | `Uint8Array` |
| `list<T>` | `T[]` |

> `list<u8>` specifically maps to `Uint8Array`, not `number[]`. All other lists use native arrays.

## Resources

Resources represent objects that cannot be trivially serialized. They are exposed as classes with methods:

```wit
resource blob {
    constructor(init: list<u8>);
    write: func(bytes: list<u8>);
    read: func(n: u32) -> list<u8>;
    merge: static func(lhs: borrow<blob>, rhs: borrow<blob>) -> blob;
}
```

JS representation:

```ts
class Blob {
  constructor(init: Uint8Array);
  write(bytes: Uint8Array): void;
  read(n: number): Uint8Array;
  static merge(lhs: Blob, rhs: Blob): Blob;
}
```

### Resource disposal

Generated types include `[Symbol.dispose]()` for automatic cleanup:

```ts
using blob = new Blob(new Uint8Array([1, 2, 3]));
blob.write(new Uint8Array([4, 5]));
// blob.dispose() called automatically at end of scope
```

Or manual disposal:

```js
const blob = new Blob(new Uint8Array([1, 2, 3]));
try {
  blob.write(new Uint8Array([4, 5]));
} finally {
  blob[Symbol.dispose]();
}
```

### Borrowed resources

`borrow<T>` in WIT means the function takes a reference without taking ownership. In JS, pass the resource instance directly.

### Resource flags

- `own<T>` — the function takes ownership; the caller should not use the resource after passing it
- `borrow<T>` — the function borrows the resource; the caller retains ownership

## Flags

WIT flags become a JS object with boolean properties:

```wit
flags colors {
    red,
    green,
    blue
}
```

```ts
{ red: boolean, green: boolean, blue: boolean }
```

## Enums

WIT enums map to string literals:

```wit
enum cows {
    default,
    owl
}
```

```ts
'default' | 'owl'
```

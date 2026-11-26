# WIT type representations

Source material: jco book chapter *WIT Type representations* (docs at tag jco-v1.42.0).

## Basic types

| WIT | JS |
|---|---|
| `u8`, `u16`, `u32`, `s8`, `s16`, `s32` | `number` |
| `u64`, `s64` | `BigInt` (use `42n` / `BigInt(...)`) |
| `f32`, `f64` | `number` |
| `bool` | `boolean` |
| `char`, `string` | `string` |

## Enums

A WIT enum is a union of string literals preserving the WIT case names:

```wit
enum status { request-pending, request-complete }
```
```ts
export type Status = 'request-pending' | 'request-complete';
```

`--enum-values-screaming-snake-case` switches values to `SCREAMING_SNAKE_CASE` on both sides of the boundary. WIT enums/variants are TS *types* by default (no runtime values); `--use-namespace-objects` additionally generates frozen namespace objects (`api.Direction.North`, `api.Permissions.Read | api.Permissions.Write` — flag values are bit masks, so it implies `--flags-as-bigint`).

## Variants

Represented as objects with a `tag` and optional `val`:

```wit
variant filter { all, none, some(list<string>) }
```
```ts
type Filter = { tag: 'all' } | { tag: 'none' } | { tag: 'some'; val: string[] };
```

A variant case holds at most one value; use a tuple or record inside the case for multiple fields. By default each case gets a named interface in the declarations; `--variants-inline-cases` inlines the cases in the union (avoids case-name collisions with record names).

## Records

Records become JS objects with camelCase property names:

```wit
record person { name: string, age: u32, favorite-color: option<string> }
```
```ts
interface Person { name: string; age: number; favoriteColor?: string; }
```

## Options

- Single-level `option<T>`: `T | undefined`.
- Doubly-nested `option<option<T>>`: tagged object `{ tag: 'some' | 'none', val: T }` — needed to distinguish missing from contained-empty.
- In records: optional properties (`prop?: T`). In function parameters: optional arguments.

## Results

- **As a function return/parameter:** JS exceptions. Implementing `f: func(n: u32) -> result<string, string>` means `throw 'not correct'` / `return 'ok'`. When wrapping is enabled, the host sees an `Error` with a `payload` property; `Error` objects thrown by host implementations have their `payload` extracted as the result error type.
- **Inside a container** (record field, tuple, variant payload): tagged object `{ tag: 'ok', val: T } | { tag: 'err', val: E }`. An arm without a payload is typed `void`.

Jco CLI and `@bytecodealliance/jco` wrap top-level `result::err` in a generated `ComponentError` by default; `@bytecodealliance/jco-transpile` throws the lifted payload directly by default (opt in with `noComponentErrorWrapping: false`). Error wrapping, typed error classes, and `isComponentError` are covered in [05-errors-and-lifecycle](05-errors-and-lifecycle.md).

## Tuples

Fixed-size arrays: `tuple<u32, u32>` → `[number, number]`.

## Lists

`list<u8>` → `Uint8Array`; all other `list<T>` → `T[]`.

## Resources

Resources are non-copyable handles to state owned by the provider. Jco represents them as classes (kebab-case WIT names become PascalCase classes, camelCase methods); the generated declarations are the source of truth.

```wit
resource blob {
  constructor(init: list<u8>);
  write: func(bytes: list<u8>);
  read: func() -> list<u8>;
  merge: static func(lhs: borrow<blob>, rhs: borrow<blob>) -> blob;
}
```
```ts
class Blob implements Disposable {
  constructor(init: Uint8Array) {}
  write(bytes: Uint8Array): void {}
  read(): Uint8Array {}
  static merge(lhs: Blob, rhs: Blob): Blob {}
  [Symbol.dispose](): void {}
}
```

### Provider/consumer direction (guest perspective)

| WIT world item | Provider | Consumer |
|---|---|---|
| `import blobs` | Host | Guest component |
| `export blobs` | Guest component | Host |

- **Guest imports a resource:** the host implements the class and passes it in the imports object under the WIT interface name, e.g. `instantiate(loader, { 'docs:resources/blobs': { Blob: HostBlob } })`. Property names match generated JS names (`blob` → `Blob`). Jco invokes methods with the original resource object as `this`, so private state works.
- **Guest exports a resource:** the guest exports the class inside an object named after the WIT interface (`export const blobs = { Blob: GuestBlob }`); the host receives `{ blobs }` from `instantiate()` and uses `blobs.Blob` like a normal class.

### Ownership

- `own<blob>` transfers ownership; the receiver must eventually drop it.
- `borrow<blob>` is temporary; the caller keeps ownership.
- Resource methods implicitly borrow `self`.
- Release deterministically with `using` declarations (TS) or try/finally `blob[Symbol.dispose]()` (JS). Do not use a resource after disposing it or passing it as `own<T>`.

### Declaration compatibility options

All default to `false` in jco (the first four are enabled by default in the lower-level `jco-transpile` package):

| API option | CLI flag | Effect when enabled |
|---|---|---|
| `nominalResources` | `--nominal-resources` | Resource consumers require the generated resource identity; structural mocks fail type-checking |
| `asyncImportsMayReturnSync` | `--async-imports-may-return-sync` | Host async imports return `Promise<T> \| T` |
| `typedErrorClasses` | `--typed-error-classes` | Named result errors get exported error classes |
| `separateInterfaceTypes` | `--separate-interface-types` | Import/export declarations split into separate files (exports under `interfaces/exports/`) |
| `optionalResultPayloads` | `--optional-result-payloads` | Payload-less result arms allow omitted `val` |

The first three imply `separateInterfaceTypes`. Use the same options when generating declarations and transpiling.

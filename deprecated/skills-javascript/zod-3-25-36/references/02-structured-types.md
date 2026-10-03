# Structured types (object, array, tuple, record, map, set)

## Contents

- [Object](#object)
- [Unknown keys](#unknown-keys)
- [Shape manipulation](#shape-manipulation)
- [Optional and required masks](#optional-and-required-masks)
- [Recursive objects](#recursive-objects)
- [Array](#array)
- [Tuple](#tuple)
- [Record](#record)
- [Map](#map)
- [Set](#set)

## Object

```ts
const schema = z.object({
  id: z.string().uuid(),
  name: z.string(),
});
```

- `schema.shape` — map of key → schema (`schema.shape.name`).
- Output/input types: each required field appears in both; fields wrapped in `.optional()`/`.default()`/`.nullable()` get `?` in the input (and, for nullable/optional, `| null`/`| undefined` in both).
- Accepts create params (`z.object(shape, { message, errorMap, description, ... })`).

## Unknown keys

`z.object()` defaults to `strip` — unknown keys are silently removed from the output.

| Mode | Behavior |
|---|---|
| `.strip()` (default; what `z.object()` produces) | unknown keys removed, no error |
| `.strict()` / `z.strictObject(shape)` | unknown keys → `unrecognized_keys` issue (lists the keys) |
| `.strict(msg)` | same, with a custom message for the `unrecognized_keys` issue |
| `.passthrough()` | unknown keys kept, unvalidated; the output type gains `[k: string]: unknown` |
| `.catchall(valueSchema)` | unknown keys validated against `valueSchema`; overrides strip/strict/catchall behavior |

`nonstrict` is a deprecated alias of `passthrough`. Note that `strip` and `passthrough` differ at the *type* level too: only `passthrough` widens the output type.

## Shape manipulation

```ts
schema.extend({ extra: z.number() })   // add or override fields (`augment` is deprecated)
schema.merge(other)                    // combine shapes; the merged schema takes `other`'s unknownKeys and catchall
schema.setKey("id", z.number())        // add/override one key (sugar over extend)
schema.pick({ id: true, name: true })  // keep only listed keys
schema.omit({ name: true })            // drop listed keys
schema.keyof()                         // z.enum of the shape's keys
```

`pick`/`omit` masks are `{ [key]: true }` objects; keys not listed are untouched. `extend` keeps existing unknown-keys mode; `merge` adopts the incoming schema's mode.

## Optional and required masks

```ts
schema.partial()                 // every field optional
schema.partial({ id: true })     // only listed fields become optional
schema.required()                // every field required (unwraps .optional())
schema.required({ name: true })  // only listed fields become required
schema.deepPartial()             // recursively optional (deprecated in v4; fine here)
```

`required` only removes `.optional()` wrappers — a field that was never optional stays as-is. `deepPartial` recurses through objects, arrays, tuples, and optional/nullable wrappers.

## Recursive objects

```ts
interface Category { name: string; sub: Category[] }
const Category: z.ZodType<Category> = z.object({
  name: z.string(),
  sub: z.array(z.lazy(() => Category)),
});

// lazily-built shape (deferred, for mutually recursive structures)
const shape: () => z.ZodRawShape = () => ({ name: z.string() });
const Lazy = z.late.object(shape);
```

`z.lazy(() => S)` (see 03-composition) is the workhorse; `z.late.object` defers only the shape construction.

## Array

```ts
const list = z.array(z.string());
list.min(1); list.max(10); list.length(5); list.nonempty();
list.element   // the element schema
```

- Issues: `too_small` / `too_big` with `type: "array"`.
- `.nonempty()` changes the inferred type to a non-empty tuple form `[T, ...T[]]` (cardinality `atleastone`).
- Element paths in issues are numeric indices.

## Tuple

```ts
z.tuple([z.string(), z.number()])                    // exact length
z.tuple([z.string(), z.number()]).rest(z.boolean())  // extra items validated as boolean
z.tuple([])                                           // empty tuple
```

- Shorter input → `too_small` (aborts the parse of that branch); longer input without `.rest()` → `too_big`.
- `z.tuple` items may be any schemas (objects included); `.items` getter returns the array of item schemas.

## Record

```ts
z.record(z.string())                          // Record<string, string> — single arg is the VALUE schema
z.record(z.number(), z.boolean())             // Record<number, boolean>
z.record(z.enum(["a", "b"]), z.number())      // { a?: number; b?: number } (partial type in v3)
z.record(z.union([z.literal("a"), z.number()]), z.boolean())
```

- Key schema (`KeySchema`): any schema whose output is `string | number | symbol` — commonly `z.string()`, `z.number()`, `z.enum(...)`.
- With an enum/union-of-literals key, v3 infers a *partial* record type (all keys optional); v4 changed this to exhaustive (see 07-v4-subpath).
- Getters: `.keySchema`, `.valueSchema`.
- Plain objects only (`invalid_type` otherwise); keys are iterated in insertion order, values parsed.

## Map

```ts
const m = z.map(z.string(), z.number());  // Map<string, number>
m.keySchema; m.valueSchema;
```

- Input must be an actual `Map` (plain objects fail with `invalid_type`).
- Every entry is parsed; the result is a new `Map` (key and value can be transformed by coercion/effects).
- Entry paths are `[index, "key" | "value"]`.

## Set

```ts
const s = z.set(z.string());
s.min(2); s.max(10); s.size(5); s.nonempty();
```

- Input must be an actual `Set`; the result is a new `Set` of parsed values.
- `.size(n)` ≡ exact length (`too_small`/`too_big`, `type: "set"`).

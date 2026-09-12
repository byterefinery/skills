---
name: zod-3-25-36
description: Zod 3.25.36 — TypeScript-first runtime schema validation with static type inference (classic v3 API). Use for defining, validating, and transforming data shapes in TypeScript or JavaScript, parsing untrusted input, building object, array, union, discriminated-union, enum, and record schemas, handling validation errors, and extracting types with z.infer. Covers the full v3.25.36 API at the zod package root, plus the bundled zod/v4 and zod/v4-mini subpaths.
license: MIT
compatibility: Runs in Node.js and all modern browsers with zero runtime dependencies. TypeScript required for static type inference; plain JavaScript works.
metadata:
  tags:
    - typescript
    - javascript
    - validation
    - schema
---

# zod 3.25.36

## Overview

Zod 3.25.36 is the final release line of the classic Zod API (v3): a TypeScript-first validation library in which every schema is simultaneously a runtime validator and a static type. Define a schema, parse data, and the result is both validated and typed.

Key properties:
- **Two-way typing** — `z.infer<typeof S>` gives the validated output type, `z.input<typeof S>` the accepted input type
- **Immutable API** — every method (`.min()`, `.strict()`, `.partial()`, …) returns a new schema; chains must be assigned
- **Chainable composition** — instance methods (`.optional()`, `.or()`, `.transform()`, `.pipe()`) plus constructors (`z.object()`, `z.union()`, `z.discriminatedUnion()`)
- **Standard Schema v1** — every schema exposes `~standard`, so it plugs into React Hook Form, TanStack Form, and similar interop layers
- **Bundled v4** — `zod@3.25.x` also ships Zod 4 (stable) at `zod/v4` and `zod/v4-mini` (core-only build); `import { z } from "zod"` (or `zod/v3`) remains the classic v3 API documented here

```ts
import { z } from "zod";

const User = z.object({
  name: z.string().min(2),
  age: z.number().int().nonnegative(),
  email: z.string().email(),
});

const data = User.parse(untrusted); // throws ZodError when invalid
// data: { name: string; age: number; email: string }
```

## Usage

```ts
import { z } from "zod";

// Primitives and checks
z.string().min(5).max(10).toLowerCase()
z.number().int().positive().multipleOf(2)
z.date().min(new Date("2024-01-01"))
z.coerce.number()                 // Number(input) before validating
z.enum(["prod", "dev"])
z.nativeEnum(MyTsEnum)

// Structured types
const Config = z.object({
  host: z.string().ip(),
  port: z.coerce.number().int().gte(0).lte(65535),
  tags: z.array(z.string()).nonempty(),
  kind: z.enum(["prod", "dev"]),
}).strict();

Config.shape.port                 // per-field schema
Config.pick({ port: true })       // subset; .omit() is the inverse
Config.partial()                  // all fields optional
Config.deepPartial()              // recursively optional

// Composition
z.union([z.string(), z.number()])
z.discriminatedUnion("type", [
  z.object({ type: z.literal("cat"), meows: z.boolean() }),
  z.object({ type: z.literal("dog"), barks: z.boolean() }),
])
z.tuple([z.string(), z.number()]).rest(z.number())
z.record(z.string())                             // Record<string, string>
z.record(z.enum(["a", "b"]), z.number())         // { a?: number; b?: number }
z.map(z.string(), z.number())
z.set(z.string()).nonempty()
z.instanceof(Date, { message: "Not a Date" })

// Recursive types
interface Category { name: string; sub: Category[] }
const Category: z.ZodType<Category> = z.object({
  name: z.string(),
  sub: z.array(z.lazy(() => Category)),
});

// Transformations
const upper = z.string().transform((s) => s.toUpperCase())
const port = z.coerce.number().pipe(z.number().int().gte(0).lte(65535))
const wrapped = z.preprocess((v) => (typeof v === "string" ? v.trim() : v), z.string())
const even = z.number().refine((n) => n % 2 === 0, "Must be even")
const crossField = Config.superRefine((val, ctx) => {
  if (val.port === 80 && val.kind !== "prod") {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ["port"],
      message: "port 80 is only allowed in prod",
    });
  }
});

// Parsing
schema.parse(data)                 // throws ZodError
schema.safeParse(data)             // { success: true, data } | { success: false, error }
await schema.parseAsync(data)      // for async refinements/transforms
const result = schema.safeParse(untrusted);
if (!result.success) {
  result.error.issues;             // ZodIssue[] — each has path, code, message
  result.error.flatten();          // { formErrors, fieldErrors }
  result.error.format();           // nested tree with _errors arrays
}

// Function schemas
const Add = z
  .function()
  .args(z.tuple([z.number(), z.number()]))
  .returns(z.number());
const add = Add.implement((a, b) => a + b); // validated wrapper, throws ZodError

// Type extraction
type UserOut = z.infer<typeof User>;   // output
type UserIn = z.input<typeof User>;    // input (differs after transforms/defaults)
```

## Gotchas

- **`import { z } from "zod"` is the v3 (classic) API in 3.25.x** — v4 lives at `zod/v4` (mini at `zod/v4-mini`). Never mix v3 and v4 schemas in one composition; they are separate class hierarchies. v4-only features (`.check()`, `z.check.*`, `z.templateLiteral`, `z.file()`, `z.email()`, `z.iso.*`) do not exist on v3 schemas.
- **Methods never mutate** — `const s = z.string(); s.min(3);` silently discards the new schema. Reassign or chain in a single expression.
- **`z.object()` strips unknown keys by default.** Use `.strict()` to reject extras, `.passthrough()` to keep them unvalidated, `.catchall(schema)` to validate them.
- **Plain `z.union` reports only "Invalid input"** (code `invalid_union`) when every option fails. Use `z.discriminatedUnion("field", [...])` when options are objects sharing a `z.literal`/`z.enum`/`z.nativeEnum` discriminator — faster (single lookup) and precise per-option errors.
- **Discriminated unions are strict** — duplicate discriminator values across options throw at creation, and the discriminator field's value must be statically extractable (`.optional()`, `.nullable()`, `.default()`, `.brand()`, `.readonly()`, `.catch()`, `.lazy()`, and effect wrappers are allowed).
- **`errorMap` cannot be combined with `invalid_type_error` or `required_error`** in create params — throws.
- **`z.coerce.boolean()` is JS truthiness** — `Boolean("false")` is `true`, `Boolean(0)` is `false`. Parse real "true"/"false" strings with `z.enum(["true", "false"]).transform(...)`.
- **`.transform()` and `z.preprocess()` change the input type** — after either, `z.input` is the pre-transform type (`unknown` for preprocess) and `z.output` is the transformed type. Use `.pipe()` when you want input/output types to stay distinct without an effects wrapper.
- **Async effects require `parseAsync`/`safeParseAsync`** — a sync `parse` on a schema with an async refine/transform/preprocess throws ("Synchronous parse encountered promise").
- **`ZodError.message` is `JSON.stringify(issues)`** — not a human-facing message. Render from `error.issues` (path + code + message per issue), `error.flatten()`, or `error.format()`.
- **`error.flatten()` uses only `issue.path[0]`** — nested errors lose their depth (all reported under the first key); use `format()` for nested shapes.
- **`z.date()` requires a valid `Date`** — rejects `new Date("nope")` (NaN) with `invalid_date`; `z.instanceof(Date)` does not check for NaN. Use `z.coerce.date()` for string/number input.
- **`z.map()` and `z.set()` require actual `Map`/`Set` instances** — plain objects fail with `invalid_type`.
- **`z.record()` defaults to string keys** — `z.record(z.number(), V)` for numeric keys, `z.record(z.enum(...), V)` for a fixed key set (v3 infers a *partial* record type for enum keys).
- **`z.enum()` takes a string-literal tuple** — TS numeric/string enums need `z.nativeEnum(MyEnum)` (accepts the enum's values, not the reverse-mapped names).
- **`.default(undefined)` is disallowed** — the param is typed `noUndefined`. `.default(v)` makes the field optional in the input and drops `undefined` from the output.
- **`z.intersection` merges both parsed halves recursively** — objects merge key by key, arrays must have equal length, conflicting values fail with `invalid_intersection_types`.
- **`z.custom()` is fatal by default** — pass `{ fatal: false }` in params to keep collecting other issues.
- **`z.readonly()` and `z.brand()` are type-level only** — no runtime validation; `.unwrap()` (or `.removeDefault()`/`.removeCatch()`) strips these wrappers.
- **No `z.templateLiteral` in v3** — that is Zod 4. Emulate with `z.enum()`, a union of `z.literal()`, or `.regex()`.
- **Deprecated in v3** — `augment` (use `extend`), `nonstrict` (use `passthrough`), `z.transformer` (alias of `z.effect`), the third `fatal` argument to `z.custom` (put `fatal` in the params object).

## References

- [01-primitives](references/01-primitives.md) — string/number/bigint/boolean/date/NaN/symbol/undefined/null/any/unknown/never/void, every string and number check, `z.coerce`, create params
- [02-structured-types](references/02-structured-types.md) — object (unknown keys, pick/omit/partial/required/deepPartial, catchall, extend/merge/setKey, keyof, `z.late.object`), array, tuple, record, map, set
- [03-composition](references/03-composition.md) — union, discriminated union, intersection, literal, enum, nativeEnum, lazy, instanceof, recursive patterns, template-literal emulation
- [04-transformations](references/04-transformations.md) — transform, pipe, preprocess, refine/refinement/superRefine, custom, function, promise, low-level effects API
- [05-error-handling](references/05-error-handling.md) — parse API, ZodError, issue codes, error maps, custom messages, adding issues, handling patterns
- [06-type-inference](references/06-type-inference.md) — z.infer/z.input/z.output, wrapper unwrapping, Standard Schema, utility types and helpers
- [07-v4-subpath](references/07-v4-subpath.md) — what `zod/v4` and `zod/v4-mini` contain in 3.25.x, key v3→v4 differences, when to use which

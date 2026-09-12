# Type inference, wrappers, and utilities

## Contents

- [Core type helpers](#core-type-helpers)
- [When input and output diverge](#when-input-and-output-diverge)
- [Wrappers and unwrapping](#wrappers-and-unwrapping)
- [Standard Schema](#standard-schema)
- [Utility types and helpers](#utility-types-and-helpers)

## Core type helpers

```ts
import { z } from "zod";

type Out  = z.infer<typeof schema>;     // = z.TypeOf<typeof schema> = T["_output"]
type In   = z.input<typeof schema>;     // T["_input"]
type Out2 = z.output<typeof schema>;    // same as z.infer
```

- `z.infer` is an alias of `z.TypeOf`; all three read the schema's phantom type parameters.
- For most schemas input and output are identical — `z.infer` is enough.

## When input and output diverge

| Wrapper | `z.input` | `z.infer` (output) |
|---|---|---|
| `.optional()` | `T \| undefined` | `T \| undefined` |
| `.nullable()` | `T \| null` | `T \| null` |
| `.nullish()` | `T \| null \| undefined` | `T \| null \| undefined` |
| `.default(v)` | `T \| undefined` (field becomes optional in objects) | `T` (no `undefined`) |
| `.catch(v)` | `unknown` (accepts anything) | `T` |
| `z.preprocess(fn, S)` | `unknown` | S's output |
| `.transform(fn)` | inner schema's input | transform's return type |
| `.pipe(B)` | A's input | B's output |
| `z.coerce.*` | same as the plain primitive | same (coercion is type-transparent) |

Typical split: form prefill / request bodies use `z.input`, trusted internal state uses `z.infer`.

## Wrappers and unwrapping

| Wrapper class | unwrap method |
|---|---|
| `ZodOptional` / `ZodNullable` | `.unwrap()` |
| `ZodBranded` | `.unwrap()` |
| `ZodReadonly` | `.unwrap()` |
| `ZodPromise` | `.unwrap()` |
| `ZodDefault` | `.removeDefault()` |
| `ZodCatch` | `.removeCatch()` |
| `ZodEffects` | `.innerType()` |

- `.brand<T>()` / `.brand()` — phantom brand: the output becomes `T & { [z.BRAND]: { [k in B]: true } }`, a distinct type with zero runtime effect. `z.BRAND` is the symbol; use it to keep, say, `Id = z.string().brand<"User">()` from being passed where a plain string is expected.
- `.readonly()` — output wrapped in `MakeReadonly`: plain objects → `Readonly<T>`, arrays → `ReadonlyArray`, tuples → readonly tuples, `Map`/`Set` → `ReadonlyMap`/`ReadonlySet`, built-ins (Date, Promise, …) unchanged. No runtime effect.
- Probes (computed by actually parsing): `schema.isOptional()` (accepts `undefined`), `schema.isNullable()` (accepts `null`).
- `schema.description` — getter for the `.describe()` metadata.

## Standard Schema

Every schema implements Standard Schema v1:

```ts
schema["~standard"];     // { version: 1, vendor: "zod", validate, types? }
schema["~validate"](x); // { value } on success | { issues } on failure (sync or async)
```

This is the interop surface used by React Hook Form (`@hookform/resolvers/zod`), TanStack Form, GLAM, Hono validators, and friends. `~validate` falls back to async internally when the schema uses async effects.

## Utility types and helpers

Named exports of the package (on the `z` namespace or importable directly):

- `z.ZodTypeAny` — `ZodType<any, any, any>`, the "any schema" type
- `z.Schema`, `z.ZodSchema` — aliases of `ZodType`
- `z.ZodFirstPartyTypeKind` — string enum of all 32 first-party type names (`"ZodString"`, `"ZodObject"`, …)
- `z.objectOutputType<Shape, Catchall, UnknownKeys>` / `z.objectInputType<...>` — compute object output/input types from a raw shape
- `z.arrayOutputType<T, Cardinality>` — array output incl. the `atleastone` cardinality form
- `z.partialUtil.DeepPartial<T>` — the type produced by `.deepPartial()`
- `z.errorUtil.errToObj(message)` — normalize `string | { message? } | undefined` into `{ message? }`
- `z.util` — re-exported internals: `ZodParsedType` (20 runtime type tags: `string`, `nan`, `number`, `integer`, `float`, `boolean`, `date`, `bigint`, `symbol`, `function`, `undefined`, `null`, `array`, `object`, `unknown`, `promise`, `void`, `never`, `map`, `set`), `getParsedType(value)`, `objectKeys`, `objectValues`, `joinValues`, `getValidEnumValues`, `arrayToEnum`, `jsonStringifyReplacer`, `clone`, `Omit`, `OmitKeys`, `Exactly`, `assertNever`
- `z.quotelessJson(obj)` — `JSON.stringify` with unquoted keys (used in default error text)
- `z.datetimeRegex({ precision, offset, local })` — the regex behind `z.string().datetime()`
- `z.NEVER` — the internal `INVALID` parse sentinel, typed as `never`
- `z.StandardSchemaV1` — the Standard Schema type definitions
- `z.Primitive` / `z.Scalars` — `string | number | symbol | bigint | boolean | null | undefined` (and array form)
- `z.setErrorMap`, `z.getErrorMap`, `z.defaultErrorMap` — global error-map control
- `z.ZodError`, `z.ZodIssueCode`, `z.IssueData`, `z.ZodIssue`, `z.ZodErrorMap`, `z.SafeParseReturnType` — error-side types

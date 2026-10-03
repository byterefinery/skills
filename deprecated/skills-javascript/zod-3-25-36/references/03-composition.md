# Composition — union, discriminated union, intersection, enum, literal, lazy, instanceof

## Contents

- [Union](#union)
- [Discriminated union](#discriminated-union)
- [Intersection](#intersection)
- [Literal](#literal)
- [Enum](#enum)
- [Native enum](#native-enum)
- [Lazy](#lazy)
- [Instanceof](#instanceof)
- [Template-literal emulation](#template-literal-emulation)

## Union

```ts
const sn = z.union([z.string(), z.number()]);
const alt = z.string().or(z.number());
```

- Options are tried in order; the first fully valid parse wins. A "dirty" result (right type, failed checks) in an earlier option does not stop later options from being tried.
- If every option fails, the result is a single `invalid_union` issue carrying `unionErrors` — the per-option `ZodError`s. Its default message is just `"Invalid input"`.
- Inferred type is the union of the option outputs.

## Discriminated union

```ts
const Animal = z.discriminatedUnion("type", [
  z.object({ type: z.literal("cat"), meows: z.boolean() }),
  z.object({ type: z.literal("dog"), barks: z.boolean() }),
  z.object({ type: z.enum(["fish", "shark"]), gills: z.boolean() }),
]);
```

- All options must be **object schemas** sharing a `discriminator` property.
- The discriminator field must be `z.literal`, `z.enum`, or `z.nativeEnum`, optionally wrapped in `.optional()`, `.nullable()`, `.default()`, `.brand()`, `.readonly()`, `.catch()`, `.lazy()`, or any effect (`.transform()`, `.refine()`, `z.preprocess`) — the extractor peels these wrappers.
- Discriminator values must be **unique across options** — duplicates throw at schema creation.
- Parsing reads `data[discriminator]` and looks the option up in a map: one pass, much faster than `z.union` for object unions, and errors pinpoint the option.
- Unknown discriminator value → `invalid_union_discriminator` issue with `path: [discriminator]` and the list of expected values.
- Getters: `.discriminator`, `.options`, `.optionsMap`.

## Intersection

```ts
const A = z.object({ a: z.string() });
const B = z.object({ b: z.number() });
const AB = z.intersection(A, B);  // or A.and(B)
```

- Both sides parse the **same input**; the two parsed results are merged recursively:
  - object + object → merged object (shared keys are merged recursively and must agree)
  - array + array → element-wise merge, **equal length required**
  - date + date → must have equal timestamps
  - anything else that differs → `invalid_intersection_types` issue (aborts)
- Inferred type is `A & B`. Intersections are best for overlaying optional properties on a base type (`Base.and(z.object({ extra: z.string().optional() }))`).

## Literal

```ts
z.literal("hello")
z.literal(42)
z.literal(true)
z.literal(1n)
z.literal(null)
z.literal(undefined)
z.literal(Symbol.for("x"))
```

- Strict `!==` comparison → `invalid_literal` issue carrying `expected`/`received`.
- Accepted values are `string | number | bigint | boolean | null | undefined | symbol` (`Primitive`).
- For a *set* of string values prefer `z.enum()` — its error message lists the allowed options.
- Getter: `.value`.

## Enum

```ts
const Role = z.enum(["admin", "user", "guest"]);
Role.options   // ["admin", "user", "guest"]
Role.enum      // { admin: "admin", user: "user", guest: "guest" } (also .Enum and .Values)

// derived subsets
const AdminOnly = Role.extract(["admin"]);
const NoGuest   = Role.exclude(["guest"]);
```

- Argument: string-literal tuple or a `const`-asserted array.
- Invalid value → `invalid_enum_value` issue listing `options` and `received`.
- Create params (`message`) customize the default message; `message` also overrides `invalid_enum_value` (see 01-primitives, Create params).

## Native enum

```ts
enum Fruit { Apple = 0, Banana = 1 }
const FruitSchema = z.nativeEnum(Fruit);  // accepts 0 and 1
```

- For numeric TS enums only the **numeric values** are accepted (reverse-mapped string keys are filtered out); string TS enums accept their string values.
- Getter: `.enum` returns the original enum object.
- Deprecated in v4 in favor of `z.enum(Color)` (which gained enum-like input support).

## Lazy

```ts
interface Node { name: string; children: Node[] }
const Node: z.ZodType<Node> = z.object({
  name: z.string(),
  children: z.array(z.lazy(() => Node)),
});
```

- `z.lazy(fn)` defers schema evaluation until parse time — the standard escape hatch for recursive and mutually recursive types.
- The `.schema` property exposes the resolved inner schema (evaluated).

## Instanceof

```ts
z.instanceof(Date)
z.instanceof(Date, { message: "Not a Date" })   // default: "Input not instance of Date"
```

- Pure `instanceof` check — no further validation (invalid `Date`s pass).
- Built on `z.custom` over `z.any()`; the accepted type is `InstanceType<T>`.

## Template-literal emulation

v3 has no `z.templateLiteral` (that is Zod 4). Common v3 stand-ins:

```ts
// fixed set of results
const Path = z.enum(["/a", "/b", "/c"]);

// pattern
const Slug = z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/);

// composed from validated parts
const Ref = z
  .tuple([z.enum(["user", "post"]), z.string().regex(/^\d+$/)])
  .transform(([kind, id]) => `/${kind}/${id}`);
```

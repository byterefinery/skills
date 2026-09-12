# Transformations and effects

## Contents

- [Transform](#transform)
- [Pipe](#pipe)
- [Preprocess](#preprocess)
- [Refine](#refine)
- [Refinement](#refinement)
- [SuperRefine](#superrefine)
- [Custom](#custom)
- [Function schemas](#function-schemas)
- [Promise schemas](#promise-schemas)
- [Low-level effects API](#low-level-effects-api)

## Transform

```ts
const upper = z.string().transform((s) => s.toUpperCase());
// input: string, output: string — the two types are distinct to the compiler

const toHex = z.string().transform((s) => parseInt(s, 16).toString(16));

// async
const checked = z.string().transform(async (s) => await validate(s));
// must be parsed with parseAsync / safeParseAsync
```

- Wraps the schema in `ZodEffects` (alias export `ZodTransformer`). The transform receives the inner schema's validated value plus a `RefinementCtx`.
- A sync `parse` on an async transform throws — switch to `parseAsync`.
- `.innerType()` returns the wrapped schema.
- Effects change the input/output typing — see 06-type-inference.

## Pipe

```ts
const port = z.coerce.number().pipe(z.number().int().gte(0).lte(65535));
const lowerEmail = z.string().email().pipe(z.string().toLowerCase());
```

- `ZodPipeline` (also `z.pipeline(A, B)`): input is validated by A, A's output is validated by B.
- Input type = A's input, output type = B's output — no effects wrapper, so types stay clean. Prefer pipe over stacked `.transform()` calls when each stage is itself a full schema (coerce → validate, parse → normalize).

## Preprocess

```ts
const trimmed = z.preprocess((v) => (typeof v === "string" ? v.trim() : v), z.string());
const dateStr = z.preprocess((v) => (typeof v === "string" ? new Date(v) : v), z.date());
```

- `z.preprocess(transform, schema)` — runs `transform` on the **raw** input, then validates the result.
- Inferred input type becomes `unknown` (the preprocessor may accept anything); output = the inner schema's output.
- A preprocessor that returns bad data surfaces the inner schema's issues (type mismatch included).

## Refine

```ts
const even = z.number().refine((n) => n % 2 === 0, "Must be even");
const min2 = z.string().refine((s) => s.length >= 2, { message: "Too short" });
const dynamic = z.number().refine((n) => n > 0, (n) => `Expected positive, got ${n}`);

// type predicate — narrows the output type (v3 behavior; v4 drops this)
const big = z.number().refine((n): n is 100 => n === 100);  // output: 100
```

- Message forms: `string`, `{ message, path?, fatal?, ... }` (`CustomErrorParams`), or `(value) => string | CustomErrorParams`.
- The check may be async (then `parseAsync` is required).
- The check runs **after** the inner schema validates; it fails with a `custom` issue.

## Refinement

```ts
z.string().refinement((s) => s.length <= 5, {
  code: z.ZodIssueCode.too_big,
  maximum: 5,
  type: "string",
  inclusive: true,
});
```

- Lower-level than `.refine()`: the second argument is a full `IssueData` (any issue code) or a function `(value, ctx) => IssueData`.
- Use it when you need a specific issue code (e.g. `too_big`) rather than `custom`.

## SuperRefine

```ts
const Password = z.object({
  pw: z.string(),
  confirm: z.string(),
}).superRefine((val, ctx) => {
  if (val.pw !== val.confirm) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ["confirm"],
      message: "Passwords do not match",
    });
  }
});
```

- Signature `(value, ctx: RefinementCtx) => void | Promise<void>`; call `ctx.addIssue(...)` once per problem — multiple issues are collected.
- `ctx.path` is the starting path; push segments to nest sub-issues (e.g. `ctx.path.push("nested")`).
- The canonical tool for cross-field validation.

## Custom

```ts
// standalone schema
const NonEmptyStrOrNull = z.custom<string | null>(
  (v) => v === null || (typeof v === "string" && v.length > 0),
  { message: "Non-empty string or null" }
);

// non-fatal: keep collecting other issues
const soft = z.custom<unknown>((v) => typeof v !== "number", { fatal: false, message: "no numbers" });
```

- `z.custom<T>(check?, params?, fatal?)` — the third `fatal` argument is deprecated; put `fatal` in `params`.
- `check` may return truthy/falsy or a promise thereof; falsy → `custom` issue.
- `params`: `string` (message), `CustomErrorParams` (`{ message?, path?, fatal?, ... }` — extras land in `issue.params`), or a function of the input value.
- Default `fatal: true` — the parse stops after the issue; `fatal: false` lets other validations continue.
- `z.custom<T>()` with no check is a pass-through type assertion.
- v3 has no `.custom()` method on schemas — custom checks go through `z.custom`, `.refine()`, or `.superRefine()`.

## Function schemas

```ts
type Add = (a: number, b: number) => number;
const Add: z.ZodType<Add> = z
  .function()
  .args(z.tuple([z.number(), z.number()]))
  .returns(z.number());

const add = Add.implement((a, b) => a + b);  // wrapped, validated function
add(1, 2);    // 3
add("x", 2);  // throws ZodError (invalid_arguments)
```

- `z.function()` alone (no args/returns) accepts any function; `.args(tuple)`, `.returns(schema)` define validation. Positional form also works: `z.function(z.tuple([...]), z.number())`.
- `.implement(fn)` (alias `.validate`) returns a wrapper that validates arguments **and** the return value on every call; the returned function is typed per the schemas.
- `.strictImplement(fn)` returns the raw function with the schema-derived type, no runtime validation.
- Getters: `.parameters()` (args tuple schema), `.returnType()`.
- Bad arguments → `ZodError` with an `invalid_arguments` issue wrapping the argument issues; bad return → `invalid_return_type`.
- Function schemas parse the *function itself* (`schema.parse(fn)` validates that `fn` is callable), and `implement` is the ergonomic path.

## Promise schemas

```ts
const p = z.promise(z.string());   // or schema.promise()
await p.parseAsync(Promise.resolve("ok"));
```

- The value must be a `Promise` (else `invalid_type`); the **resolved** value is validated by the inner schema — so use `parseAsync`.
- A sync `parse` only checks that the value is a promise.

## Low-level effects API

```ts
// z.effect / z.transformer — ZodEffects.create(schema, effect)
const t = z.effect(z.string(), { type: "transform", transform: (s) => s.length });
// effect object kinds:
//   { type: "transform", transform }
//   { type: "refinement", refinement }
//   { type: "preprocess", transform }
```

- `z.effect` and `z.transformer` are both aliases of `ZodEffects.create(schema, effect, params?)`.
- Prefer the fluent methods (`.transform`, `.refine`, `z.preprocess`); this is only for programmatic effect construction.

# Error handling — parse API, ZodError, issue codes, error maps

## Contents

- [Parse API](#parse-api)
- [ZodError](#zoderror)
- [Issue codes](#issue-codes)
- [Customizing messages](#customizing-messages)
- [Error maps](#error-maps)
- [Adding issues from refinements](#adding-issues-from-refinements)
- [Handling patterns](#handling-patterns)

## Parse API

```ts
schema.parse(data)                    // returns parsed value | throws ZodError
schema.safeParse(data)                // { success: true, data } | { success: false, error: ZodError }
await schema.parseAsync(data)         // async-aware (async refinements/transforms)
await schema.safeParseAsync(data)     // `.spa` is an alias
```

- All four accept an optional params object `{ path?: (string|number)[], errorMap?: ZodErrorMap, async?: boolean }` — a contextual error map applies only to that parse.
- "Dirty" vs "aborted": a failed check marks the value *dirty* (parsing continues, more issues are collected); a failed type check *aborts* that branch. `safeParse` returns every issue collected either way.
- `parse` returns the parsed (possibly transformed, stripped, coerced, defaulted) value — not the input object.

## ZodError

```ts
e.issues;                    // ZodIssue[] — the primary API
e.errors;                    // alias of issues
e.message;                   // JSON.stringify(issues, null, 2) — machine-oriented, not human-facing
e.isEmpty;                   // issues.length === 0
e.addIssue(iss);             // immutable append (returns updated issues)
e.addIssues([iss]);
e.flatten();                 // { formErrors: string[], fieldErrors: { [key]: string[] } }
e.flatten((i) => i.code);    // mapper overload
e.formErrors;                // getter — formErrors half of flatten()
e.format();                  // nested { _errors: string[] } tree mirroring the data shape
e.format((i) => i.code);     // mapper overload
ZodError.create(issues);     // construct from raw issues
ZodError.assert(value);      // type guard — throws "Not a ZodError" if it isn't
```

- Top-level issues (empty `path`) go to `formErrors`; field issues are keyed by **`path[0]` only** — nested depth is lost in `flatten()`.
- `format()` recurses into `invalid_union`/`invalid_arguments`/`invalid_return_type` sub-errors and places each issue at its full path.

## Issue codes

`z.ZodIssueCode` is a string enum of 16 codes. Every `ZodIssue` has `path`, `message`, `code`, plus code-specific fields:

| code | extra fields | raised when |
|---|---|---|
| `invalid_type` | `expected`, `received` | wrong parsed type; missing (undefined) input → message "Required" |
| `invalid_literal` | `expected`, `received` | `z.literal` mismatch |
| `invalid_enum_value` | `options`, `received` | `z.enum`/`z.nativeEnum` mismatch |
| `invalid_string` | `validation` | a string check failed (`"email"`, `"uuid"`, `"datetime"`, `{ includes, position? }`, `{ startsWith }`, `{ endsWith }`, `"regex"`, …) |
| `invalid_date` | — | invalid (NaN) date |
| `too_small` | `minimum`, `inclusive`, `exact?`, `type` | below min (string/number/array/date/set/bigint) |
| `too_big` | `maximum`, `inclusive`, `exact?`, `type` | above max |
| `not_multiple_of` | `multipleOf` | divisibility |
| `not_finite` | — | `z.number().finite()` |
| `unrecognized_keys` | `keys` | `.strict()` object with unknown keys |
| `invalid_union` | `unionErrors: ZodError[]` | no union option matched |
| `invalid_union_discriminator` | `options` | unknown discriminator value |
| `invalid_arguments` | `argumentsError: ZodError` | `z.function` bad arguments |
| `invalid_return_type` | `returnTypeError: ZodError` | `z.function` bad return |
| `invalid_intersection_types` | — | intersection merge conflict |
| `custom` | `params?` | `refine`/`superRefine`/`z.custom` |

## Customizing messages

Per call — any check or validator method:

```ts
z.string().min(5, "Too short")
z.string().min(5, { message: "Too short" })
z.string().email("Bad email")
```

At schema creation — every constructor:

```ts
z.string({ message: "Not a string" })
z.string({ required_error: "Name is required" })
z.string({ invalid_type_error: "Must be a string" })
z.string({ errorMap: (issue, ctx) => ({ message: "Custom: " + issue.code }) })
z.string({ description: "The user's name" })  // metadata only, via .describe() equivalent
```

- `message` is a blanket override for `invalid_type` (including required) and for `invalid_enum_value` on enums.
- `errorMap` may **not** be combined with `invalid_type_error`/`required_error` — throws at creation.

Global (all schemas, until changed):

```ts
import { setErrorMap, getErrorMap } from "zod";
setErrorMap((issue, ctx) => ({ message: `bad ${issue.code}` }));  // replaces the default map
getErrorMap();          // current map
z.defaultErrorMap;      // the built-in English map (locales/en)
```

## Error maps

Signature: `(issue: ZodIssueOptionalMessage, ctx: { defaultError: string; data: any }) => { message: string }`.

Resolution order per issue: **contextual map** (from `parse({ errorMap })`) → **schema map** (`_def.errorMap`) → **global map** (`setErrorMap`) → built-in default. `ctx.defaultError` is the message the next level in the chain would produce, so a custom map can fall back by returning it.

## Adding issues from refinements

- `ctx.addIssue({ code, path?, message?, ...issueFields })` inside `.superRefine()` and `z.custom()` — `path` is relative to the current schema position.
- `.refinement(check, issueData | (value, ctx) => issueData)` adds exactly one issue, with a code of your choice.
- `.refine(check, message)` adds a `custom` issue with the given message.

## Handling patterns

```ts
// discriminated result (most common at API boundaries)
const result = schema.safeParse(input);
if (!result.success) {
  const { formErrors, fieldErrors } = result.error.flatten();
  // formErrors: top-level messages; fieldErrors: per top-level key
}

// throw + catch
try {
  schema.parse(input);
} catch (e) {
  if (e instanceof ZodError) {
    e.issues.forEach((i) => console.error(i.path.join("."), i.message));
  } else {
    throw e; // not a validation error — rethrow
  }
}

// per-parse contextual error map
schema.parse(input, { errorMap: (iss) => ({ message: `bad ${iss.code}` }) });
```

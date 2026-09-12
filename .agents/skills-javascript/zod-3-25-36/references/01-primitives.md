# Primitives and z.coerce

## Contents

- [Primitive constructors](#primitive-constructors)
- [String checks](#string-checks)
- [Number checks](#number-checks)
- [BigInt checks](#bigint-checks)
- [Date checks](#date-checks)
- [Coercion](#coercion)
- [Create params](#create-params)

## Primitive constructors

| Constructor | Parsed type | Notes |
|---|---|---|
| `z.string()` | `string` | chainable checks below |
| `z.number()` | `number` | `NaN` fails type check (use `z.nan()`); ±Infinity pass unless `.finite()` |
| `z.bigint()` | `bigint` | |
| `z.boolean()` | `boolean` | no runtime check methods |
| `z.date()` | `Date` | rejects invalid (NaN) dates with `invalid_date` |
| `z.nan()` | `number` | accepts only `NaN` |
| `z.symbol()` | `symbol` | |
| `z.undefined()` | `undefined` | |
| `z.null()` | `null` | |
| `z.any()` | `any` | accepts anything, typed `any` |
| `z.unknown()` | `unknown` | accepts anything, typed `unknown` |
| `z.never()` | `never` | always fails validation |
| `z.void()` | `void` | accepts only `undefined` |

Optional shortcuts (v3-only, dropped in v4): `z.ostring()`, `z.onumber()`, `z.oboolean()` — each equals the primitive's `.optional()`.

## String checks

Validation checks (failure → `invalid_string` issue, or `too_small`/`too_big` for lengths):

| Method | Accepts |
|---|---|
| `.min(n)` / `.max(n)` / `.length(n)` / `.nonempty()` | string length (`.nonempty()` ≡ `.min(1)`) |
| `.email()` | practical email address (no local-part dots-only, no `..`, TLD ≥ 2 chars) |
| `.url()` | anything `new URL()` accepts |
| `.uuid()` / `.nanoid()` / `.cuid()` / `.cuid2()` / `.ulid()` | ID formats (canonical lengths) |
| `.emoji()` | one or more emoji characters |
| `.base64()` / `.base64url()` | encodings (base64url accepts optional padding) |
| `.jwt({ alg? })` | three-segment JWT; header must decode (base64url → JSON) with an `alg`; if `alg` is given it must match, and `typ` (if present) must be `"JWT"` |
| `.ip("v4" \| "v6" \| { version?, message? })` / `.cidr(...)` | IPv4/IPv6, optionally with `/prefix` (cidr) |
| `.datetime({ precision?, offset?, local? })` | ISO 8601 datetime; `precision` null = any, `offset: true` allows `+02:00`, `local: true` allows omitting the zone (default requires `Z`) |
| `.date()` / `.time({ precision? })` / `.duration()` | `YYYY-MM-DD` (leap-year aware), `HH:MM[:SS[.fff]]`, ISO 8601 duration (`P…T…`) |
| `.regex(re)` / `.includes(v, { position?, message? })` / `.startsWith(v)` / `.endsWith(v)` | pattern and containment checks |

Options objects may be a bare string (treated as the message): `.datetime("bad date")` ≡ `.datetime({ message: "bad date" })`.

Transforming checks (always pass, mutate the output value):

- `.trim()`, `.toLowerCase()`, `.toUpperCase()`

Introspection getters: `.minLength`, `.maxLength`, and one boolean per format — `.isEmail`, `.isURL`, `.isUUID`, `.isNANOID`, `.isCUID`, `.isCUID2`, `.isULID`, `.isEmoji`, `.isDatetime`, `.isDate`, `.isTime`, `.isDuration`, `.isIP`, `.isCIDR`, `.isBase64`, `.isBase64url`.

Every check accepts a custom error: `.email("Bad email")` or `.email({ message: "Bad email" })`.

## Number checks

| Method | Accepts |
|---|---|
| `.min(n)` / `.gte(n)`, `.max(n)` / `.lte(n)` | inclusive bounds |
| `.gt(n)` / `.lt(n)` | exclusive bounds |
| `.int()` | integers (issue `invalid_type` with `expected: "integer"`) |
| `.positive()` / `.negative()` / `.nonnegative()` / `.nonpositive()` | sign (strict and inclusive zero) |
| `.multipleOf(n)` / `.step(n)` | divisibility (float-safe remainder) |
| `.finite()` | rejects ±Infinity (`not_finite`) |
| `.safe()` | safe integer range — sugar for `.min(Number.MIN_SAFE_INTEGER).max(Number.MAX_SAFE_INTEGER)` (`too_small`/`too_big`) |

`.min`/`.max` are property aliases of `.gte`/`.lte` (bound checks use `too_small`/`too_big` issues).

## BigInt checks

`.min()`/`.gte()`, `.max()`/`.lte()`, `.gt()`, `.lt()`, `.multipleOf()`, `.positive()`, `.negative()`, `.nonnegative()`, `.nonpositive()`; getters `.minValue` / `.maxValue`. No `.int()` (bigints are always integral), no `.finite()`/`.safe()`.

## Date checks

`.min(Date)` / `.max(Date)`; getters `.minDate` / `.maxDate` (undefined until set). An invalid date (NaN) fails with `invalid_date` before any check runs.

## Coercion

`z.coerce.string()`, `z.coerce.number()`, `z.coerce.boolean()`, `z.coerce.bigint()`, `z.coerce.date()` run `String()`, `Number()`, `Boolean()`, `BigInt()`, `new Date()` on the input before validating.

- Accept the same create params as the plain primitives: `z.coerce.number({ message: "Not a number" })`.
- `z.coerce.number()`: `""` → `0`, `null` → `0` (both pass); `"abc"` → `NaN` (fails).
- `z.coerce.boolean()`: pure JS truthiness — `"false"` and `"0"` become `true`.
- `z.coerce.date()`: wraps `new Date(input)`; a garbage string then fails with `invalid_date`.
- No coercion for `enum`, `object`, or collection types.

## Create params

Every constructor (and every static `.create()`) accepts `RawCreateParams`:

```ts
{
  errorMap?: (issue, ctx) => ({ message: string });
  invalid_type_error?: string;  // message for invalid_type issues
  required_error?: string;      // message when the input is undefined
  message?: string;             // blanket override for invalid_type/required, plus invalid_enum_value on enums
  description?: string;         // metadata, equivalent to .describe()
}
```

Constraints:

- `errorMap` may not be used together with `invalid_type_error` or `required_error` — throws at creation.
- `message` takes priority over `invalid_type_error`/`required_error` when both are given.
- `.describe()` is a method equivalent to the `description` param.

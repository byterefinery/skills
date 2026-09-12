# The bundled v4 subpaths (zod/v4, zod/v4-mini)

`zod@3.25.36` ships three APIs in one package:

| Import | API |
|---|---|
| `import { z } from "zod"` | classic v3 (default — the rest of this skill) |
| `import { z } from "zod/v3"` | identical to the root |
| `import { z } from "zod/v4"` | Zod 4 — stable, the "flagship" line |
| `import { z } from "zod/v4-mini"` | Zod 4 core-only build (slimmer, no classic-compat layer) |

Zod 4 was released inside the 3.25 line so the ecosystem could migrate on its own schedule; when `zod@4.0.0` ships on npm, v4 moves to the package root and `zod/v4` remains.

## Rules of engagement

- **Never mix v3 and v4 schemas in one composition** — different class hierarchies and parse internals; there is no compatibility layer between them.
- If a project is on `zod@3.25.x`, new code may use either line, but keep each module on one.
- This skill documents v3 (the package root). v4's own docs are authoritative for v4 specifics.

## Key v3 → v4 differences (from the repo's migration guide)

### Error customization

- v4 standardizes everything on a single `error` param; `message` is deprecated, `invalid_type_error`/`required_error`/`errorMap` are **dropped**.
- `z.setErrorMap` is gone; customize per schema with `error`.
- `ZodError.message` becomes a human-readable string (first issue) instead of JSON.
- `ZodError.format()`, `.flatten()`, `.formErrors` are deprecated or dropped — iterate `.issues`; `.addIssue()`/`.addIssues()` deprecated.

### Primitives

- `z.number()`: infinite values are rejected outright; `.int()` accepts **safe integers only**; `.safe()` behaves like `.int()`.
- `z.string()`: format methods moved to the top level — `z.email()`, `z.uuid()`, `z.url()`, `z.emoji()`, `z.base64()`, `z.base64url()`, `z.nanoid()`, `z.cuid()`, `z.cuid2()`, `z.ulid()`, `z.ipv4()`, `z.ipv6()`, `z.cidrv4()`, `z.cidrv6()`, `z.iso.date()`, `z.iso.time()`, `z.iso.datetime()`, `z.iso.duration()`. The `.string().email()`-style methods are deprecated. `.ip()` and `.cidr()` dropped (use v4/v6 variants); `.base64url()` no longer accepts padding; IPv6 validation now uses `new URL()`.
- `z.coerce`: coerced boolean input type is `unknown` (v3: `string`).
- `z.literal()` drops `symbol` support.
- `z.templateLiteral()` exists only in v4.

### Objects

- `.strict()`/`.passthrough()` deprecated in favor of `z.strictObject()`/`z.looseObject()` (methods kept for back-compat); `.strip()` deprecated; `.nonstrict()` and `.deepPartial()` dropped (v4: `.partial({ deep: true })`).
- `z.unknown()`/`z.any()` fields are no longer optional in inferred types.
- `z.nativeEnum()` deprecated — `z.enum(Color)` now accepts enum-like input directly.
- `z.array().nonempty()` no longer changes the inferred type (v3: `[T, ...T[]]`).

### Records, intersections, functions

- `z.record()` requires both arguments: `z.record(z.string(), z.string())` — the single-arg form is dropped; enum keys become **exhaustive** (all keys required).
- `z.intersection` merge conflicts throw a plain `Error` instead of a `ZodError` with `invalid_intersection_types`.
- `z.function()` is no longer a schema — it's a function factory taking `{ input, output }` upfront, with `.implement()`/`.implementAsync()`.

### Refinements

- `.refine()` ignores type predicates (no output-type narrowing) and drops the function-as-message overload; `ctx.path` is removed from `RefinementCtx`.

### Misc

- `z.ostring()`/`z.onumber()`/`z.oboolean()` dropped; `z.promise()` deprecated (just `await` first); static `.create()` factories dropped (`z.string()` is the factory).

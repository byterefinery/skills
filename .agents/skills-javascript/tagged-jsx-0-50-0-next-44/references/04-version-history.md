# Version history and provenance

## Package lineage

| Release | Event |
|---|---|
| 0.50.0-next.3 | **Added as `sld-dom-expressions`** — "an AST-based tagged-template runtime that avoids runtime code generation (CSP-safe) and supports a named component registry for tooling-friendly templates". Same release: `createSLDRuntime(runtime)` returns a ready tag directly (no factory double-call, components via `.define({...})`); single-node results flattened to scalars (tag return type `JSX.Element`); `Runtime`/`ComponentRegistry`/`FunctionComponent` exported; `sideEffects: false`; `Runtime.spread`'s `skipChildren` type fixed from `Boolean` to `boolean`. |
| 0.50.0-next.6 | `<template>` rendering fixed so dynamic expressions are inserted into inert template content; `csstype` inlined into the published type declarations (no transitive JSX-type dependency for consumers). |
| 0.50.0-next.9 | Line (`//`) and block (`/* */`) comments supported inside tag blocks. |
| 0.50.0-next.11 | `on:` namespace event support removed across compiler, runtime, JSX types, and renderer packages — events are `on*` (delegated) or `on*` lowercase (direct) only. |
| 0.50.0-next.12 | Top-level element siblings each get their own cached template, so adjacent top-level expressions update and clean up correctly. |
| 0.50.0-next.15 | **Renamed** `sld-dom-expressions` → `tagged-jsx-dom-expressions` with the public API names still in use today: `createTaggedJSXRuntime`, `TaggedJSXInstance`, `.jsx` self-reference tag. Same release moved all packages into the `@dom-expressions` npm scope: `tagged-jsx-dom-expressions` → **`@dom-expressions/tagged-jsx`** (sibling packages: `dom-expressions` → `@dom-expressions/runtime`, `babel-plugin-jsx-dom-expressions` → `@dom-expressions/babel-plugin-jsx`, `jsx-dom-expressions-compiler` → `@dom-expressions/jsx-compiler`, `hyper-dom-expressions` → `@dom-expressions/hyperscript`). The old unscoped names remain only on the Solid 1.x maintenance line (`main` branch, 0.40.x). `lit-dom-expressions` was dropped from the prerelease line — superseded by this package. |
| 0.50.0-next.25 | **Element-claim contract**: static `a[href]` / `form[action]` in tagged templates are stamped at bake time and every clone is claimed via `claimElement` at render (static attributes are baked into the cached template and would otherwise bypass the runtime's attribute-write recheck). The `Runtime` interface gains a **required** `claimElement` member — a no-op null check until a consumer registers a handler. |
| 0.50.0-next.44 | **Latest published** (2026-08-24). No tagged-jsx-specific changesets since next.25 — the package source has been stable across next.16–next.44, all of whose changesets touched sibling packages (runtime, compiler, hyperscript). |

## next.15 → next.44 source diff (verified)

The repo's only git tag for this package is `@dom-expressions/tagged-jsx@0.50.0-next.15`; diffing that tag's `packages/tagged-jsx/src` against the published 0.50.0-next.44 npm tarball's `src/` shows **exactly one logical change** — the next.25 claim contract:

- `src/types.ts` — `Runtime` gains `claimElement<T extends Element>(node: T): T;`
- `src/parse.ts` — `ElementNode` gains an optional `claim?: boolean` stamp
- `src/tagged-jsx.ts` — bake-time stamping of `a`/`form` nodes with static `href`/`action` (only when no spread precedes) and `r.claimElement(...)` calls on stamped clones in both render paths
- `src/tokenize.ts`, `src/index.ts` — unchanged

So the tree at the `@dom-expressions/tagged-jsx@0.50.0-next.15` tag URL is next.44 *minus* the claim contract; everything else (API, syntax, reactivity, caching) is identical.

## Repo and registry provenance

- **Repo**: `github.com/ryansolid/dom-expressions`, package at `packages/tagged-jsx`. The `main` branch is the **0.40.x Solid 1.x maintenance line** (unscoped package names); the **`next` branch** carries the 0.50.0-next line. Versions from next.16 onward publish from `next` **without git tags** (the release commits are `Version packages for 0.50.0-next.N`).
- **npm tarball ships the full source** — `src/`, `tests/`, `README.md`, `CHANGELOG.md`, plus `dist/` — so the tarball is a complete study artifact: `curl -sL https://registry.npmjs.org/@dom-expressions/tagged-jsx/-/tagged-jsx-0.50.0-next.44.tgz`.
- **Registry**: `latest` dist-tag = `0.50.0-next.44`; the `next` dist-tag lags at `0.50.0-next.42`. Pin `0.50.0-next.44` explicitly.
- All five line packages are version-locked in lockstep via Changesets `fixed` groups — a `dom-expressions` 0.50.0-next.N npm release always ships a matching tagged-jsx build.

# `@dom-expressions/compiler`

Experimental AST-native JSX→DOM Expressions compiler implemented with **Oxc** (Rust, via NAPI). Parse once, mutate the AST (`VisitMut`), build replacements (`AstBuilder`), codegen once. It is a **backend API** — not a Vite/Rollup/Babel plugin; integrations call `transform()` once per source module.

## Install and bindings

Prebuilt native binaries ship as per-platform optional-dependency packages: `@dom-expressions/compiler-{darwin-arm64, darwin-x64, linux-x64-gnu, linux-arm64-gnu, win32-x64-msvc}`. A WASI fallback (`-wasm32-wasi`) covers StackBlitz WebContainers and similar environments where Node reports a native platform but can't load `.node` addons; the entry point prefers native and falls back automatically. `NAPI_RS_FORCE_WASI=error` forces the WASI binding for testing. Other platforms: build from source in `packages/compiler` (needs a Rust toolchain).

## API

```js
const { transform, transformAsync, transformDirectives } = require("@dom-expressions/compiler");

const result = transform(`const view = <div>Hello</div>;`, {
  filename: "App.jsx",
  moduleName: "dom",
  generate: "dom"
});
// result.code, result.map (when sourceMap: true)
```

`transformAsync(source, options)` returns the same shape as a promise.

### Rust core

The crate exposes a host-independent `compile(src, &CompileOptions)` for embedding without Node-API (build with `--no-default-features`). **Unstable pre-1.0**: options, output, and error types may change in any release — pin an exact revision. The Node `transform()` is the supported public contract.

## Generate modes

- `"dom"` — standard client output.
- `"ssr"` — string output (pair with `moduleName: "dom/server"`).
- `"universal"` — targets the `dom-expressions/src/universal` `createRenderer` primitives (custom backends).
- `"dynamic"` — universal fallback with a configured set of native tags routed to the DOM renderer:

```js
transform(source, {
  filename: "hybrid.jsx", moduleName: "renderer", generate: "dynamic",
  renderers: [{ name: "dom", moduleName: "dom", elements: ["div", "span", "button", "input"] }]
});
```

### Presets

- **Solid-style DOM**: `generate: "dom"`, `hydratable: true`, `builtIns: ["For", "Show"]` — the compiler defaults `contextToCustomElements: true` to match Solid. Add `dev: true` with `hydratable: true` for dev hydration-walk validation helpers (`getFirstChild`/`getNextSibling`).
- **SSR**: `moduleName: "dom/server"`, `generate: "ssr"`, `hydratable: true`.
- **Source maps**: `sourceMap: true` → JSON string in `result.map`.

### Options

Mirror the Babel plugin where implemented: `filename`, `moduleName`, `generate`, `hydratable`, `dev`, `sourceMap`, `contextToCustomElements`, `delegateEvents`, `delegatedEvents` (explicit list), `omitQuotes`, `omitAttributeSpacing`, `inlineStyles`, `effectWrapper` (string or `false` to disable), `memoWrapper` (string or `false`), `wrapConditionals`, `staticMarker`, `validate`, `omitNestedClosingTags`, `omitLastClosingTag`, `builtIns`, `requireImportSource`, `renderers`.

## `"use server"` directives (experimental)

`transformDirectives(code, options)` is an independent second pass ported from SolidStart's Babel transform — works on plain `.js`/`.ts` as well as JSX/TSX.

```js
const result = transformDirectives(source, { filename: "/project/src/api.ts", root: "/project", mode: "server" /* or "client" */ });
result.valid;     // false when no directive matched — keep the original module
result.code;      // registerServerReference / createServerReference output
result.functions; // [{ id, name, exports }] for manifest building
```

Server mode registers extracted functions via `registerServerReference(id, fn)`; client mode replaces them with `createServerReference(id)` proxies and strips server-only code (DCE). Function IDs use the frozen `xxhash32(root-relative path)-<count>` format (name-suffixed in development), interchangeable with the Babel implementation's manifests. Runtime module defaults to `@solidjs/web/server-functions` (`register`/`create` options override). Ported: module-level directives with exports in both modes, function-level directives on expressions/arrows (declarations bubble to `const` first), client DCE, metadata. **Not yet ported**: server functions nested inside other extracted server functions, object/class method directives, sourcemap fidelity through client DCE.

## Performance

vs `@dom-expressions/babel-plugin-jsx` on identical sources (Apple M5, release build, median of 7):

| Workload | Babel | Rust | Speedup |
|---|---|---|---|
| Fixture corpus (88 files, 175 KB, all modes) | 440 ms | 19 ms | 23x |
| 129 KB single module | 545 ms | 9.4 ms | 58x |
| 1 MB single module | 24,975 ms | 70 ms | 355x |

Native throughput stays flat at ~9–14 MB/s; Babel's cost grows super-linearly. Reproduce with `pnpm bench` in the package.

## Scope and intentional rejections

Checked fixture coverage: DOM, hydratable DOM, dev hydratable DOM, SSR, hydratable SSR, universal, dynamic, no-inline-styles, and wrapperless renderer paths — native elements, components, fragments, refs, spreads, dynamic text, events, attribute handling. A single `Classify` authority owns dynamic classification/child counting/static-marker handling across all generates (mirrors Babel's shared architecture), guarded by a cross-mode fixture-union parity ratchet.

The compiler **rejects** rather than fakes:

- DOM `namespaceElements` sections the Oxc parser rejects (e.g. hyphenated JSX member segments).
- Arbitrary custom renderer names beyond dynamic DOM override + universal fallback.
- Unknown/custom namespaced DOM attributes outside known runtime namespaces such as `xlink`.

## Architecture (for contributors)

`src/lib.rs` (NAPI entrypoint) · `src/config.rs` (options/result) · `src/shared/ast.rs` (AST construction helpers) · `src/shared/transform.rs` (traversal + target dispatch) · `src/shared/component.rs` · `src/shared/constants.rs` · `src/dom/{element,template,attrs,events}.rs` · `src/ssr/{mod,transform}.rs` · `src/universal/{mod,transform}.rs`. The older string-splice research backend lives on local branch `research/oxc-string-backend`. See repo `packages/compiler/AST_REWRITE.md` for the milestone tracking doc.

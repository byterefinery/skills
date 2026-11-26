# Build-less usage and dist files

Source: `packages/vue/README.md`, `packages/vue/examples/` in the v3.5.46 tree.

## Which dist file to use

### From CDN or without a Bundler

- **`vue(.runtime).global(.prod).js`** — for direct use via `<script src="...">` in the browser. Exposes the `Vue` global.
  - Not UMD — built as IIFEs, only for direct `<script src>` use.
  - **`vue.global.js`** is the "full" build: compiler + runtime, supports compiling templates on the fly (in-DOM templates, `template` option).
  - **`vue.runtime.global.js`** is runtime only; templates must be pre-compiled during a build step.
  - Inlines all Vue core internal packages — a single file with no dependencies. **Must** import everything from this file and this file only, to get one instance of the code.
  - Hard-coded prod/dev branches; the prod build is pre-minified. Use the `*.prod.js` files for production.

- **`vue(.runtime).esm-browser(.prod).js`** — for native ES modules imports (`<script type="module">`). Same runtime-compilation, dependency-inlining, and hard-coded prod/dev behavior as the global builds.

### With a Bundler

- **`vue(.runtime).esm-bundler.js`** — for webpack, rollup, parcel, etc.
  - Leaves prod/dev branches with `process.env.NODE_ENV` guards (the bundler must replace them).
  - Not shipped minified (minify with the rest of the code after bundling).
  - Imports dependencies (`@vue/runtime-core`, `@vue/compiler-core`, ...) as separate `esm-bundler` builds. They may be installed/imported individually, but must all resolve to the **same version**.
  - **`vue.runtime.esm-bundler.js` (default)** is runtime only — the default entry via the `module` field — because bundler setups pre-compile templates (e.g. `.vue` files).
  - **`vue.esm-bundler.js`** includes the runtime compiler — alias `vue` to it when using a bundler but still wanting runtime template compilation (in-DOM templates or templates as inline JS strings).

### Bundler Build Feature Flags

`esm-bundler` builds expose compile-time overridable global flags:

| Flag | Default | Effect |
|---|---|---|
| `__VUE_OPTIONS_API__` | `true` | Enable / disable Options API support |
| `__VUE_PROD_DEVTOOLS__` | `false` | Enable / disable devtools support in production |
| `__VUE_PROD_HYDRATION_MISMATCH_DETAILS__` | `false` | Enable / disable detailed hydration-mismatch warnings in production |

The build works without configuring these, but configuring them is **strongly recommended** for proper tree-shaking.

### For Server-Side Rendering

- **`vue.cjs(.prod).js`** — for Node.js SSR via `require()` (e.g. webpack `target: 'node'` with `vue` externalized). Dev/prod files are pre-built; the right one is picked by `process.env.NODE_ENV`.

## Patterns from the official examples

`packages/vue/examples/` ships six demos in **classic** (Options API) and **composition** (Composition API) variants: `commits`, `grid`, `markdown`, `svg`, `todomvc`, `tree`, plus `transition/list` and `transition/modal`. All of them:

1. Load the local full build: `<script src="../../dist/vue.global.js"></script>`.
2. Keep templates in an in-DOM `<script type="text/x-template" id="...">` block and reference it via `template: '#id'` (the full build compiles it at runtime).
3. Pull APIs from the global `Vue` object (`const { reactive, computed } = Vue`).

The composition variants use `setup(props)` with `reactive` / `computed` state and return it for template access; the classic variants use `data()` and `this`.

## Caveats

- ES modules do not run over `file://` — serve build-less apps over http (any static server).
- In-DOM templates are compiled from `innerHTML`, so the content must be trusted (the runtime marks the path `__UNSAFE__`).
- `app.config.compilerOptions` is only respected by builds that include the runtime compiler; in runtime-only builds pass options to `@vue/compiler-dom` in the build setup instead (the dev warning says so).

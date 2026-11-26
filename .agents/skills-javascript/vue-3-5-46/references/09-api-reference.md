# API reference (v3.5.46 export surface)

Source: package entry files in the v3.5.46 tree — `packages/vue/package.json` + `packages/vue/src/index.ts`, `packages/reactivity/src/index.ts`, `packages/runtime-core/src/index.ts`, `packages/runtime-dom/src/index.ts`, `packages/server-renderer/src/index.ts`, `packages/compiler-sfc/src/index.ts`.

## `vue` package

- Entry is the **full build**: runtime + compiler. `src/index.ts` registers a runtime compiler (`compileToFunction`) that compiles the `template` option (string or in-DOM `#selector`) with `hoistStatic: true`, caches results, and defaults `isCustomElement` to `customElements.get` when no compiler option is set. Exports `compile` (as `compileToFunction`) and re-exports everything from `@vue/runtime-dom`.
- **Subpath exports** (package.json `exports`): `. (`vue`), `./server-renderer`, `./compiler-sfc`, `./jsx-runtime`, `./jsx-dev-runtime`, `./jsx` (types), `./dist/*`, `./package.json`.
- Main/module/types: `index.js` / `dist/vue.runtime.esm-bundler.js` / `dist/vue.d.ts`. The bundler default is **runtime-only** (`vue.runtime.esm-bundler.js`).
- Root monorepo `package.json`: version `3.5.46`, `"engines": { "node": ">=20.0.0" }`.

## `@vue/reactivity`

Full list in [02-reactivity](02-reactivity.md). Highlights: `ref`, `reactive`, `computed`, `watch`, `effectScope`, `onScopeDispose`, `toValue`, `onWatcherCleanup`, `getCurrentWatcher`, `traverse`.

## `@vue/runtime-core`

> Published only for typing and building custom renderers — **not** for applications (README).

- Version: `version` export (=== `__VERSION__`).
- Reactivity re-exports: `computed` (apiComputed), `watch`/`watchEffect`/`watchPostEffect`/`watchSyncEffect` (apiWatch).
- App: `createApp`, `createRenderer`, `createHydrationRenderer` (custom renderer entry point), `defineComponent`, `defineAsyncComponent`.
- Injection: `provide`, `inject`, `hasInjectionContext`, `InjectionKey` type.
- Scheduling: `nextTick`, `queuePostFlushCb`.
- Setup helpers: `useAttrs`, `useSlots`, `useModel`, `useTemplateRef` (`TemplateRef`), `useId`, `getCurrentInstance`.
- VNodes: `h`, `createVNode`, `cloneVNode`, `mergeProps`, `isVNode`, `Fragment`, `Text`, `Comment`, `Static`, `VNodeRef` type, `transformVNodeArgs` (global vnode hook for HMR/profiling).
- Render helpers: `renderList`, `renderSlot`, `createSlots`, `toHandlers`, `withMemo`, `isMemoSame`.
- Components: `Teleport`, `Suspense`, `KeepAlive` (+ props types).
- Directives: `withDirectives`.
- SSR: `useSSRContext`, `ssrContextKey`, `ssrUtils`.
- Compiler: `registerRuntimeCompiler`, `isRuntimeOnly`.
- Misc: `warn` (NOOP in prod), `assertNumber`, `ErrorTypeStrings`, `devtools`/`setDevtoolsHook` (`__VUE_PROD_DEVTOOLS__`), re-exported `TrackOpTypes`/`TriggerOpTypes`, HMRRuntime type, Slot/Slots/SlotsType types.
- Compat (only in `__COMPAT__` builds): `compatUtils`, `DeprecationTypes`, `resolveFilter`, `CompatVue`/`LegacyConfig` types.

## `@vue/runtime-dom`

- DOM renderer over runtime-core: `render`, `hydrate`, `createApp`, `createSSRApp` (`nodeOps` + `patchProp` renderer options; lazy renderer creation so reactivity-only imports stay tree-shakable).
- `createApp.mount`: accepts element/shadow-root/selector, uses container innerHTML as template when the component has none, clears content, removes `v-cloak`, sets `data-v-app`; dev warns on closed-mode ShadowRoot mounts.
- DOM components: `Transition`, `TransitionGroup`.
- DOM directives: `vShow`, `vModelText/Checkbox/Radio/Select/Dynamic`, `withModifiers`, `withKeys`.
- Custom elements: `defineCustomElement`, `defineSSRCustomElement`, `useShadowRoot`, `useHost`, `VueElement`.
- SFC CSS helpers: `useCssModule`, `useCssVars`.
- JSX: `ClassValue`, `StyleValue` types (`./jsx`).
- Re-exports all of runtime-core (which re-exports reactivity).

## `@vue/server-renderer`

`renderToString`, `renderToSimpleStream`, `renderToNodeStream`, `renderToWebStream`, `pipeToNodeWritable`, `pipeToWebWritable`, deprecated `renderToStream`; types `SSRContext`, `SimpleReadable`; internal runtime helpers re-exported via `./internal`.

## `@vue/compiler-sfc`

See [05-sfc](05-sfc.md): `parse`, `compileScript`, `compileTemplate`, `compileStyle`/`compileStyleAsync`, `rewriteDefault`/`rewriteDefaultAST`, `resolveTypeElements`, `inferRuntimeType`, `babelParse`, `MagicString`, `walk`, `parseCache`, `errorMessages`, `invalidateTypeCache`, `registerTS`, `extractRuntimeProps`, `extractRuntimeEmits`.

## Compiler feature flags (compile-time, esm-bundler)

`__VUE_OPTIONS_API__` (true), `__VUE_PROD_DEVTOOLS__` (false), `__VUE_PROD_HYDRATION_MISMATCH_DETAILS__` (false) — see [01-build-less](01-build-less.md).

## Examples and demos index

- **`packages/vue/examples/classic/`** — `commits.html`, `grid.html`, `markdown.html`, `svg.html`, `todomvc.html`, `tree.html` (Options API).
- **`packages/vue/examples/composition/`** — same six (Composition API / `setup()`).
- **`packages/vue/examples/transition/`** — `list.html`, `modal.html` (`Transition`/`TransitionGroup` demos).
- **`packages-private/sfc-playground`** — in-browser SFC editor; deployed at play.vuejs.org; `pnpm dev-sfc` / `pnpm build-sfc-playground`.
- **`packages-private/template-explorer`** — live template compilation explorer; deployed at template-explorer.vuejs.org; `npm run dev-compiler` then `npm run open`.

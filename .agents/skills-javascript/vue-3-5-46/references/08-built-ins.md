# Built-in components, directives, SSR, custom elements

Source: `packages/runtime-core/src/index.ts` + `components/`, `packages/runtime-dom/src/index.ts` + `components/` + `directives/`, `packages/server-renderer/src/index.ts` in the v3.5.46 tree.

## Built-in components

| Component | Package | Purpose |
|---|---|---|
| `Teleport` | runtime-core (`components/Teleport`) | move DOM to another location (`to` target); `TeleportProps` type |
| `Suspense` | runtime-core (`components/Suspense`) | suspense boundary for async setup/components; `SuspenseProps` type |
| `KeepAlive` | runtime-core (`components/KeepAlive`) | cache component instances; exports `onActivated`/`onDeactivated` |
| `Transition` | runtime-dom (`components/Transition`) | enter/leave transitions; `TransitionProps` type |
| `TransitionGroup` | runtime-dom (`components/TransitionGroup`) | list transitions; `TransitionGroupProps` type |

`Transition` and `TransitionGroup` are also registered as global components via the `GlobalComponents` module augmentation (runtime-dom index), so they work in templates without imports.

## Built-in directives

- **`v-model`** — runtime-dom `directives/vModel.ts`: `vModelText`, `vModelCheckbox`, `vModelRadio`, `vModelSelect`, `vModelDynamic`. SSR variants initialized via `initVModelForSSR`.
- **`v-show`** — `directives/vShow.ts` (`vShow` export; `initVShowForSSR` for SSR).
- **`v-on` helpers** — `withModifiers`, `withKeys` (exported for custom directive composition).
- Compiler-time: `v-if`, `v-for`, `v-once`, `v-memo`, `v-bind`, `v-slot` (see 04-template-syntax).

Directive registration: app-level via `app.directive` (Application API); programmatic directive VNodes via `withDirectives` (runtime-core).

## SSR (server-renderer + client hydration)

- **Server** — from `@vue/server-renderer` (deep import `vue/server-renderer`): `renderToString`, `renderToSimpleStream`, `renderToNodeStream`, `renderToWebStream`, `pipeToNodeWritable`, `pipeToWebWritable`; `renderToStream` is **deprecated**. Types: `SSRContext`, `SimpleReadable`.
- **App creation** — `createSSRApp()` (runtime-dom) for both server and client entry; client hydrates with the hydration renderer (`hydrate` is exported from runtime-dom).
- **Helpers** — `useSSRContext()` (+ `ssrContextKey`), `onServerPrefetch()` (see 07-lifecycle), `defineSSRCustomElement()`.

## Custom elements

From runtime-dom (`apiCustomElement.ts`): `defineCustomElement`, `defineSSRCustomElement`, `useShadowRoot`, `useHost`, the `VueElement` base class, and types `VueElementConstructor`, `CustomElementOptions`.

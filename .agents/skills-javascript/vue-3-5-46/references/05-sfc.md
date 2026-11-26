# Single-File Components and compiler-sfc

Source: `packages/compiler-sfc/README.md` and `packages/compiler-sfc/src/index.ts` in the v3.5.46 tree.

## Availability

Since 3.2.13+, `@vue/compiler-sfc` is a dependency of the main `vue` package — use the deep import **`vue/compiler-sfc`** instead of installing the package separately (guarantees matching versions). It is what `vue-loader` and `@vitejs/plugin-vue` use under the hood.

## API surface (from `src/index.ts`)

- **`parse`** — parse SFC source into a descriptor (`script`, `template`, `styles`, `customBlocks`, `errors`, `queries`, `filename`, `source`, `map`). `parseCache` is exported as a plain Map.
- **`compileScript`** — compile the script block; handles `<script setup>`, the `defineXxx` macros, and CSS variable injection (`SFCScriptCompileOptions`).
- **`compileTemplate`** — compile the raw template into render function code.
- **`compileStyle` / `compileStyleAsync`** — compile styles; handles `<style scoped>`, `<style module>`, and CSS variable injection.
- **`rewriteDefault` / `rewriteDefaultAST`** — rewrite `export default` to a temp variable so options can be attached (used when inlining blocks instead of the facade pattern).
- **Type utilities** — `resolveTypeElements`, `inferRuntimeType`, `invalidateTypeCache`, `registerTS` (custom TS registration), `extractRuntimeProps`, `extractRuntimeEmits`.
- **AST / source tools** — `babelParse` (`@babel/parser`), `MagicString`, `walk` (`estree-walker`), `errorMessages` (SFC error code table).

## Compiled output shape (facade module)

The README's general idea: a facade module imports the individual blocks as "virtual" modules with query strings, then attaches the compiled render function to the script:

```js
// main script
import script from '/project/foo.vue?vue&type=script'
// template compiled to render function
import { render } from '/project/foo.vue?vue&type=template&id=xxxxxx'
// css
import '/project/foo.vue?vue&type=style&index=0&id=xxxxxx'

// attach render function to script
script.render = render

// attach additional metadata
script.__file = 'example.vue'
script.__scopeId = 'xxxxxx'

// additional tooling-specific HMR handling code
// using __VUE_HMR_API__ global

export default script
```

High-level workflow per the README:

1. Facade transform: `parse` the source, generate the facade code.
2. Script transform: `compileScript` (script setup, CSS variable injection) — or inline with `rewriteDefault`.
3. Template transform: `compileTemplate` into render function code.
4. Style transform: `compileStyle` for scoped styles, CSS modules, CSS variables.

Options can be passed via the query string. For real usage examples the README points to `@vitejs/plugin-vue` and `vue-loader`.

## SFC features

- **`<script setup>`** — the recommended script block: top-level bindings are exposed to the template; macros available: `defineProps`, `withDefaults`, `defineEmits`, `defineExpose`, `defineSlots`, `defineModel`, `defineOptions` (see 03-components).
- **Styles** — `<style scoped>` (scope-id based), `<style module>` (CSS modules, consumed via `useCssModule()` from `vue`), plain global styles.
- **CSS variables** — `useCssVars()` (from `vue`) maps reactive state to CSS custom properties; `compileScript` handles the injection.
- **Pre-processors** — plugin-based via the build system (e.g. `<style lang="scss">` handled by the corresponding loader).
- **HMR** — separate HMR for script, template and styles so template updates do not reset component state and style updates do not re-render (README motivation for the facade design).

## In-browser SFC demo

`packages-private/sfc-playground` (deployed at play.vuejs.org) compiles SFCs in the browser; run locally with `pnpm dev-sfc`, build with `pnpm build-sfc-playground` (README). Its `src/` includes dev/prod runtime proxies (`vue-dev-proxy.ts`, `vue-dev-proxy-prod.ts`) and an SSR preview proxy (`vue-server-renderer-dev-proxy.ts`).

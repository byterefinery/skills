# Template syntax and directives

Source: `packages/compiler-core/src/transforms/` (the transform modules are the authoritative list), `packages/runtime-dom/src/directives/`, and the official examples, in the v3.5.46 tree.

## Directive transforms (compiler-core)

Each of these is a transform module in `packages/compiler-core/src/transforms/`:

| Directive | Transform file | Notes from examples |
|---|---|---|
| `v-bind` / `:attr` shorthand | `vBind.ts` + `transformVBindShorthand.ts` | `:class`, `:style` bindings; `v-bind="object"` is order-sensitive (compat feature reference) |
| `v-on` / `@event` | `vOn.ts` | `@click="sortBy(key)"`; key and modifier handling lives in runtime-dom `withKeys`/`withModifiers` |
| `v-if` / `v-else-if` / `v-else` | `vIf.ts` | `v-if="filteredData.length"` with `v-else` fallback in grid.html |
| `v-for` | `vFor.ts` | `v-for="entry in filteredData"`, `v-for="key in columns"` (string/number/array iteration) |
| `v-model` | `vModel.ts` | two-way binding on form controls; runtime implementation in `packages/runtime-dom/src/directives/vModel.ts` (`vModelText`, `vModelCheckbox`, `vModelRadio`, `vModelSelect`, `vModelDynamic`) |
| `v-once` | `vOnce.ts` | render once, ignore future updates |
| `v-memo` | `vMemo.ts` | conditional re-render with dependency comparison |
| `v-slot` | `vSlot.ts` | slot props destructuring (`transformSlotOutlet.ts` handles `<slot>` outlets) |
| expressions | `transformExpression.ts` | `{{ mustache }}` interpolation plus all inline expressions |
| static hoisting | `cacheStatic.ts` | static vnodes hoisted out of the render function |
| no-op directives | `noopDirectiveTransform.ts` | `v-pre`, `v-once`-adjacent no-op directives handled here |

Element handling: `transformElement.ts` (props/attrs normalization, namespace). Text: `transformText.ts` (whitespace condensation).

## In-DOM templates (build-less)

The examples keep markup in hidden script blocks:

```html
<script type="text/x-template" id="grid-template">
  <table v-if="filteredData.length">...</table>
  <p v-else>No matches found.</p>
</script>
```

and reference it with `template: '#grid-template'`. The full build (`vue.global.js`) resolves the `#id` via `document.querySelector` and compiles the `innerHTML` at runtime — hence the `__UNSAFE__` trust warning for in-DOM template content.

## Mustaches and expressions

- `{{ message }}` — text interpolation; expressions are JS expressions evaluated in the component scope.
- Template expressions are sandboxed: no access to `window`/`document` or user globals (only a restricted global whitelist), except what `app.config.globalProperties` adds.

## Example-derived patterns

- `v-if` + `v-else` for empty states (grid.html).
- Nested `v-for` for table cells (grid.html: rows × columns).
- Event handler with argument: `@click="sortBy(key)"`.
- Conditional class object: `:class="{ active: state.sortKey == key }"`.
- Transition demos (`transition/list.html`, `transition/modal.html`) pair `v-if`/`v-for` with `<transition>` / `<transition-group>`.

## Caveats

- `v-if` and `v-for` on the same element: in Vue 3, `v-if` has higher precedence (per the compat feature reference `COMPILER_V_IF_V_FOR_PRECEDENCE`) — don't rely on Vue 2 behavior; wrap with `<template v-for>` and filter with a computed.
- `v-model` on native inputs ignores initial `value`/`checked`/`selected` HTML attributes.
- In a runtime-only build, template options are ignored — templates must be compiled at build time (see 01-build-less).

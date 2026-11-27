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

## Text Interpolation

Mustache syntax for data binding:

```vue-html
<span>Message: {{ msg }}</span>
<span>{{ count + 1 }}</span>
<span>{{ ok ? 'YES' : 'NO' }}</span>
```

Double mustaches interpret data as plain text, not HTML.

## Raw HTML

Use `v-html` to render raw HTML:

```vue-html
<div v-html="rawHtml"></div>
```

**Security warning**: Only use `v-html` on trusted content. Never on user-provided content — it leads to XSS vulnerabilities.

## Attribute Bindings

```vue-html
<div v-bind:id="dynamicId"></div>
<!-- shorthand -->
<div :id="dynamicId"></div>
```

- If bound value is `null` or `undefined`, the attribute is removed
- **Same-name shorthand (3.4+)**: `<div :id></div>` is equivalent to `<div :id="id"></div>`

### Boolean Attributes

```vue-html
<button :disabled="isDisabled">Button</button>
```

Included if truthy or empty string. Omitted for other falsy values.

### Binding Multiple Attributes

```vue-html
<div v-bind="objectOfAttrs"></div>
<!-- or -->
<div :="objectOfAttrs"></div>
```

## JavaScript Expressions

Full JS expressions are supported in bindings:

```vue-html
{{ number + 1 }}
{{ ok ? 'YES' : 'NO' }}
{{ message.split('').reverse().join('') }}
<div :id="`list-${id}`"></div>
```

**Constraints**:
- Only one single expression per binding (no statements, no flow control)
- Sandboxed — only restricted globals (`Math`, `Date`) are accessible
- Functions called in expressions run on every update — no side effects

## v-if, v-else-if, v-else

Conditional rendering. Elements are destroyed and recreated when toggled.

```vue-html
<p v-if="type === 'A'">Type A</p>
<p v-else-if="type === 'B'">Type B</p>
<p v-else>Other</p>
```

Use on `<template>` for multi-element conditional blocks:

```vue-html
<template v-if="ok">
  <h1>Title</h1>
  <p>Content</p>
</template>
```

## v-for

List rendering. Use `key` attribute for efficient DOM diffing.

```vue-html
<li v-for="item in items" :key="item.id">{{ item.name }}</li>

<!-- With index -->
<li v-for="(item, index) in items" :key="item.id">{{ index }}: {{ item.name }}</li>

<!-- Range -->
<span v-for="n in 10">{{ n }}</span>

<!-- On template -->
<template v-for="item in items">
  <li :key="item.id">{{ item.name }}</li>
  <li :key="'desc-' + item.id">{{ item.desc }}</li>
</template>
```

### v-for with v-if

`v-if` has higher priority than `v-for`. Never put both on the same element.

```vue-html
<!-- Wrong -->
<li v-for="user in users" v-if="user.active" :key="user.id">

<!-- Correct: wrap v-for in template -->
<template v-for="user in users" :key="user.id">
  <li v-if="user.active">{{ user.name }}</li>
</template>

<!-- Or use computed filter -->
<li v-for="user in activeUsers" :key="user.id">
```

## v-on (Event Handling)

```vue-html
<button @click="increment">Click</button>
<button @click="handle('hello', $event)">Click</button>
```

### Event Modifiers

| Modifier | Meaning |
|---|---|
| `.stop` | `event.stopPropagation()` |
| `.prevent` | `event.preventDefault()` |
| `.self` | Only trigger if event from this element |
| `.capture` | Capture mode |
| `.once` | Trigger at most once |
| `.passive` | `{ passive: true }` |

```vue-html
<a @click.stop.prevent="doThis">Link</a>
<form @submit.prevent="onSubmit">...</form>
<div @scroll.passive="onScroll">...</div>
```

### Key Modifiers

```vue-html
<input @keyup.enter="submit" />
<input @keyup.delete="delete" />
<input @keydown.ctrl.enter="submit" />
```

Special aliases: `.enter`, `.tab`, `.delete`, `.esc`, `.space`, `.up`, `.down`, `.left`, `.right`, `.ctrl`, `.alt`, `.shift`, `.meta`.

## v-model

Two-way binding on form inputs. Expands to `:value` + `@input` internally (varies by element type).

```vue-html
<input v-model="message" placeholder="edit me" />
<textarea v-model="message"></textarea>

<!-- Checkbox -->
<input type="checkbox" v-model="checked" />

<!-- Radio -->
<input type="radio" v-model="picked" value="A" />

<!-- Select -->
<select v-model="selected">
  <option value="A">A</option>
  <option value="B">B</option>
</select>
```

### v-model Modifiers

| Modifier | Purpose |
|---|---|
| `.lazy` | Sync on `change` instead of `input` |
| `.number` | Cast to number |
| `.trim` | Trim whitespace |

```vue-html
<input v-model.lazy="msg" />
<input v-model.number="age" type="number" />
<input v-model.trim="name" />
```

### v-model on Components

Default prop/event names: `modelValue` and `update:modelValue`. Use `defineModel()` (3.4+) for cleaner syntax.

```vue
<!-- Child -->
<script setup>
const model = defineModel()
</script>
<template>
  <input v-model="model" />
</template>

<!-- Parent -->
<Child v-model="text" />
```

## v-show

Toggles `display` CSS property. Unlike `v-if`, element is always rendered — only visibility changes. No conditional block support (cannot use on `<template>`).

```vue-html
<h1 v-show="visible">Toggle me</h1>
```

Use `v-show` for frequent toggling, `v-if` for conditions that rarely change.

## Class and Style Bindings

### Class Binding

```vue-html
<!-- Object syntax -->
<div :class="{ active: isActive, 'text-danger': hasError }"></div>

<!-- Array syntax -->
<div :class="[activeClass, errorClass]"></div>

<!-- Combined with static class -->
<div class="static" :class="{ active: isActive }"></div>
```

### Style Binding

```vue-html
<!-- Object syntax -->
<div :style="{ color: activeColor, fontSize: fontSize + 'px' }"></div>

<!-- Array syntax -->
<div :style="[baseStyles, overridingStyles]"></div>

<!-- Auto-prefixing -->
<div :style="{ display: '-webkit-box' }"></div>
```

## Dynamic Arguments

```vue-html
<a :[attributeName]="url">Link</a>
<a @[eventName]="handler">Link</a>
```

- Argument must evaluate to a string or `null`
- No spaces or quotes in dynamic argument expressions
- In-DOM templates: browsers coerce attribute names to lowercase

## Modifiers

Directive postfixes with `.` that indicate special binding behavior:

```vue-html
<!-- Event modifiers -->
<form @submit.prevent="onSubmit">

<!-- v-bind modifiers -->
<div :bind.camel="obj">  <!-- camelCase the prop name -->

<!-- v-model modifiers -->
<input v-model.trim="name">
```
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

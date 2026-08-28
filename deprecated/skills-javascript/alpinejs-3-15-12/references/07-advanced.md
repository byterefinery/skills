# Advanced

## CSP Build (`@alpinejs/csp`)

Alternate build that complies with strict Content Security Policy (no `unsafe-eval`). Uses a custom expression parser instead of `Function()` constructor.

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.15.12/dist/cdn.min.js"></script>
```

```js
import Alpine from '@alpinejs/csp'
window.Alpine = Alpine
Alpine.start()
```

### Supported

```html
<!-- Object/array literals -->
<div x-data="{ user: { name: 'John' }, items: [1, 2, 3] }">
  <span x-text="user.name"></span>
  <span x-text="items[0]"></span>
</div>

<!-- Basic operations -->
<span x-text="count + 10"></span>
<span x-text="count > 3"></span>
<span x-text="count === 5 ? 'Yes' : 'No'"></span>
<div x-show="!loading && count > 0"></div>

<!-- Assignments and method calls -->
<button @click="count++">
<button @click="items.push('c')">
<input x-model="user.name">
```

### Not Supported

```html
<!-- ❌ Property dot-assignment -->
<button @click="user.name = 'John'">

<!-- ❌ Arrow functions -->
<button @click="() => console.log('hi')">

<!-- ❌ Destructuring -->
<div x-text="{ name } = user">

<!-- ❌ Template literals -->
<div x-text="`Hello ${name}`">

<!-- ❌ Spread operator -->
<div x-data="{ ...defaults }">

<!-- ❌ Global variables/functions -->
<button @click="console.log('hi')">
<span x-text="document.title">
<span x-text="Math.max(a, b)">
<span x-text="JSON.stringify(obj)">

<!-- ❌ HTML injection -->
<span x-html="message">
```

### Strategy

Extract complex logic into `Alpine.data()` components or named functions:

```html
<div x-data="userManager" x-show="hasActiveAdmins">
```

```js
Alpine.data('userManager', () => ({
  users: [],
  get hasActiveAdmins() {
    return this.users.filter(u => u.active && u.role === 'admin').length > 0
  }
}))
```

### CSP Header Example

```
Content-Security-Policy: default-src 'self'; script-src 'nonce-[random]' 'strict-dynamic';
```

---

## Reactivity Model

Alpine uses `@vue/reactivity` under the hood. Two core functions power all reactivity:

### Alpine.reactive()

Wraps a plain object in a Proxy that intercepts get/set operations:

```js
let data = Alpine.reactive({ count: 1 })
console.log(data.count)  // 1
data.count = 2
console.log(data.count)  // 2
```

The proxy tracks all access, enabling Alpine to know which properties are read and when they change.

### Alpine.effect()

Runs a callback and tracks reactive dependencies. Re-runs when dependencies change:

```js
let data = Alpine.reactive({ count: 1 })

Alpine.effect(() => {
  console.log(data.count)  // logs on every change to data.count
})
```

### Building Reactive UI Without Directives

```js
let data = Alpine.reactive({ count: 1 })

Alpine.effect(() => {
  span.textContent = data.count
})

button.addEventListener('click', () => {
  data.count++
})
```

### Alpine.transaction()

Batch multiple reactive changes into a single notification cycle:

```js
Alpine.transaction(() => {
  data.a = 1
  data.b = 2
  data.c = 3
})  // effects fire once, not three times
```

---

## Extending Alpine

All extensions must register before Alpine initializes the page.

### Via Script Tag

```html
<script src="/js/extensions.js" defer></script>
<script src="/js/alpine.js" defer></script>
```

```js
// extensions.js
document.addEventListener('alpine:init', () => {
  Alpine.directive('foo', ...)
  Alpine.magic('bar', ...)
})
```

### Via NPM

```js
import Alpine from 'alpinejs'

Alpine.directive('foo', ...)
Alpine.magic('bar', ...)

Alpine.start()
```

### Custom Directives

```js
Alpine.directive('name', (el, { value, modifiers, expression }, { evaluate, evaluateLater, effect, cleanup, Alpine }) => {
  // value: part after colon (e.g., 'bar' from x-foo:bar)
  // modifiers: array of dot-separated modifiers
  // expression: the attribute value string
})
```

#### Simple Directive

```js
Alpine.directive('uppercase', el => {
  el.textContent = el.textContent.toUpperCase()
})
```

```html
<span x-uppercase>Hello World!</span>
```

#### Evaluating Expressions

```js
Alpine.directive('log', (el, { expression }, { evaluate }) => {
  console.log(evaluate(expression))
})
```

```html
<div x-log="message">
```

#### Reactive Directive

```js
Alpine.directive('log', (el, { expression }, { evaluateLater, effect }) => {
  let getter = evaluateLater(expression)

  effect(() => {
    getter(value => console.log(value))
  })
})
```

`evaluateLater()` compiles the expression string into a reusable function. Pass a callback receiver to support async expressions.

The `effect` from the directive context auto-cleans when the directive is removed from the DOM.

#### Cleanup

```js
Alpine.directive('listen', (el, {}, { cleanup }) => {
  let handler = () => { /* ... */ }
  window.addEventListener('resize', handler)
  cleanup(() => window.removeEventListener('resize', handler))
})
```

#### Custom Order

```js
Alpine.directive('foo', (el, { value, modifiers, expression }) => {
  Alpine.addScopeToNode(el, { foo: 'bar' })
}).before('bind')  // run before x-bind
```

### Custom Magics

```js
Alpine.magic('name', (el, { Alpine }) => {
  // Return a value (property) or a function
})
```

#### Magic Property

```js
Alpine.magic('now', () => (new Date).toLocaleTimeString())
```

```html
<span x-text="$now"></span>
```

#### Magic Function

```js
Alpine.magic('clipboard', () => subject => {
  navigator.clipboard.writeText(subject)
})
```

```html
<button @click="$clipboard('hello')">Copy</button>
```

### Writing Plugins

#### Script Tag Plugin

```js
// plugin.js (load before Alpine)
document.addEventListener('alpine:init', () => {
  window.Alpine.directive('foo', ...)
  window.Alpine.magic('bar', ...)
})
```

#### NPM Module Plugin

```js
// plugin.js
export default function(Alpine) {
  Alpine.directive('foo', ...)
  Alpine.magic('bar', ...)
}
```

```js
// app.js
import Alpine from 'alpinejs'
import plugin from './plugin.js'
Alpine.plugin(plugin)
Alpine.start()
```

`Alpine.plugin()` invokes the function with `Alpine` as the argument.

---

## Async Support

Alpine supports `await` in most expression contexts:

```html
<span x-text="await fetchLabel()"></span>
```

```js
async function fetchLabel() {
  let response = await fetch('/api/label')
  return await response.text()
}
```

Methods can be called without parentheses — Alpine detects async and handles it:

```html
<span x-text="fetchLabel"></span>
```

`x-init` supports async expressions:

```html
<div x-data="{ items: [] }" x-init="items = await (await fetch('/api')).json()">
```

`$nextTick` returns a Promise:

```html
<button @click="
  title = 'Hello';
  await $nextTick();
  console.log($el.textContent);
">
```

---

## V2 to V3 Migration

### Breaking Changes

| V2 | V3 |
|---|---|
| `$el` = component root | `$el` = current element; use `$root` for root |
| Manual `x-init="init()"` | `init()` called automatically |
| `import 'alpinejs'` auto-starts | Must call `Alpine.start()` |
| `x-show.transition="open"` | `x-show="open" x-transition` |
| `x-if.transition` supported | `x-if` has no transitions; use `x-show` + `x-transition` |
| Nested `x-data` blocks scope | Scope cascades through nested `x-data` |
| `x-init="() => { callback }"` | `x-init="$nextTick(() => { callback })"` |
| `return false` prevents default | Use `.prevent` modifier explicitly |
| `x-spread="obj"` | `x-bind="obj"` |
| `:x-ref="dynamic"` | Static `x-ref` only |
| `deferLoadingAlpine` | `alpine:init` / `alpine:initialized` events |
| IE11 supported | IE11 dropped |

### Deprecated

- `.away` modifier → use `.outside`
- Global function data providers → use `Alpine.data()`

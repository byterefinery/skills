# Alpine.js 3.16.3 — Advanced

## Reactivity primitives

Alpine is built on `@vue/reactivity`. The two core functions:

```js
let data = Alpine.reactive({ count: 1 })   // proxy-wrapped: reads and writes are tracked

Alpine.effect(() => {
    console.log(data.count)                // runs now, re-runs whenever data.count changes
})
```

- `Alpine.reactive(obj)` returns a proxy; mutating the original object and the proxy stay in sync.
- `Alpine.effect(fn)` runs `fn` immediately, tracks every reactive read inside it, and re-runs on change.
- `Alpine.transaction(fn)` batches mutations so dependent effects flush once instead of per-write.

This combination (plus DOM binding code) is all Alpine does — you can build components without any `x-*` syntax if you want.

## Async expressions

Anywhere Alpine evaluates an expression, `async`/`await` work:

```html
<span x-text="await getLabel()"></span>
<div x-data="{ posts: [] }" x-init="posts = await (await fetch('/posts')).json()">
```

- Async methods are also detected when referenced without parens: `x-text="getLabel"` with `async function getLabel() {...}`.
- `$nextTick()` returns a promise for sequencing after DOM flush.

## Extending Alpine

Extension APIs must be registered **after** the Alpine script is available but **before** init — `alpine:init` listener (CDN) or between import and `Alpine.start()` (module). Every built-in directive and magic uses these same APIs.

### `Alpine.directive(name, handler)`

```js
Alpine.directive('[name]', (el, { value, expression, modifiers },
    { Alpine, effect, cleanup, evaluate, evaluateLater }) => {})
```

| Piece | Meaning |
|---|---|
| `name` | `foo` is consumed as `x-foo` |
| `el` | The DOM element carrying the directive |
| `value` | Part after the colon: `'bar'` in `x-foo:bar` (undefined if absent) |
| `expression` | The attribute value: `'law'` in `x-foo="law"` |
| `modifiers` | Array from dot syntax: `['baz', 'lob']` in `x-foo.baz.lob` |
| `Alpine` | The global |
| `effect` | Reactive effect that **auto-cleans up** when the element leaves the DOM (prefer over `Alpine.effect`) |
| `cleanup` | Register callbacks to run when the directive is removed |
| `evaluate` | Evaluate a string expression in the element's scope (sync result) |
| `evaluateLater` | Compile a string into a function; call with a receiver callback (supports async) |

Examples:

```js
Alpine.directive('uppercase', el => {
    el.textContent = el.textContent.toUpperCase()
})

Alpine.directive('log', (el, { expression }, { evaluate }) => {
    console.log(evaluate(expression))
})

// Reactive: log now and on every change
Alpine.directive('log', (el, { expression }, { evaluateLater, effect }) => {
    let getThingToLog = evaluateLater(expression)   // compile once, reuse
    effect(() => {
        getThingToLog(thingToLog => console.log(thingToLog))
    })
})
```

Compile expressions with `evaluateLater` rather than calling `evaluate` repeatedly — string→function interpretation is expensive. Receiver-callback form (`getThing(value => ...)`) is what lets directives support `await` expressions.

### `Alpine.magic(name, handler)`

```js
Alpine.magic('[name]', (el, { Alpine }) => {})
```

Returns a value that becomes `$name` in expressions:

```js
// Magic "property" (evaluated getter)
Alpine.magic('now', () => (new Date).toLocaleTimeString())

// Magic "function" (return a function)
Alpine.magic('clipboard', () => subject => navigator.clipboard.writeText(subject))
```

```html
<span x-text="$now"></span>
<button @click="$clipboard('hello world')">Copy</button>
```

### Plugin shape

A plugin is just `function(Alpine)` that registers what it needs — this is how all official plugins install:

```js
export default function (Alpine) {
    Alpine.directive('collapse', (el, { modifiers }, { effect, cleanup }) => { /* ... */ })
    Alpine.magic('persist', el => (value, key) => { /* ... */ })
}
// Alpine.plugin(myPlugin) or Alpine.plugin([a, b, c])
```

## CSP build details

`@alpinejs/csp` swaps the `Function`-based evaluator for a restricted parser (no `unsafe-eval`). Supported: literals (objects/arrays), arithmetic, comparison, member access, assignment/`++`/`--`, method calls, ternaries, template-literal-free string building, simple `&&`/`||`. Not supported: `new`, arrow-function definitions inline, global references outside the Alpine scope, complex expression chains. Rule of thumb: if the inline expression grows beyond a simple call, move the logic into a data-object method.

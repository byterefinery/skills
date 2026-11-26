# Advanced (Alpine.js 3.17.5)

Reactivity primitives, async expressions, custom directives/magics, and the CSP build.

## Reactivity

Alpine's reactivity rests on two functions (Vue's reactivity engine under the hood):

- `Alpine.reactive(object)` — wraps the object in a JS Proxy; gets/sets behave as normal but Alpine tracks them.
- `Alpine.effect(callback)` — runs the callback, registers every reactive property read during that run as a dependency, and re-runs the callback when any dependency changes (re-collecting per run).

```js
let data = Alpine.reactive({ count: 1 })

Alpine.effect(() => {
    console.log(data.count)   // logs 1, then again on every change
})
```

Dependency collection happens only while the callback runs — reads inside `setTimeout` etc. are not tracked by the original effect.

## Async / await

Any place Alpine evaluates a standard function also supports async:

```js
async function getLabel() {
    let response = await fetch('/api/label')
    return await response.text()
}
```

```html
<span x-text="await getLabel()"></span>
```

A method referenced **without** parens (`x-text="getLabel"`) is also detected as async and handled accordingly. `x-init` supports `await` too (fetch data before the component renders).

## Custom directives

```js
Alpine.directive('[name]', (el, { value, modifiers, expression }, { Alpine, effect, cleanup, evaluate }) => {})
```

| Parameter | Meaning |
|---|---|
| name | Consumed as `x-<name>` |
| el | The DOM element the directive is on |
| value | Part after a colon (`x-foo:bar` → `'bar'`) |
| modifiers | Array of dot-separated additions (`x-foo.baz.lob` → `['baz','lob']`) |
| expression | The attribute value string |
| Alpine | The Alpine global |
| effect | Create reactive effects that auto-cleanup when the directive is removed |
| cleanup | Register callbacks that run when the directive is removed |

Simple example:

```js
Alpine.directive('uppercase', el => {
    el.textContent = el.textContent.toUpperCase()
})
```

**Evaluating expressions** — use `evaluate(expression)` for one-shot evaluation in the element's component scope. For repeated evaluation, prefer `evaluateLater(expression)`: it compiles the expression into a function once (string→function interpretation is expensive) and is async-capable — you pass it a callback receiver:

```js
Alpine.directive('log', (el, { expression }, { evaluateLater, effect }) => {
    let getThingToLog = evaluateLater(expression)

    effect(() => {
        getThingToLog(thingToLog => {
            console.log(thingToLog)
        })
    })
})
```

The directive-scoped `effect()` (not `Alpine.effect()`) auto-cleans up when the directive is removed. For listeners, use `cleanup(fn)`:

```js
Alpine.directive('...', (el, {}, { cleanup }) => {
    let handler = () => {}
    window.addEventListener('click', handler)
    cleanup(() => window.removeEventListener('click', handler))
})
```

**Custom order** — chain `.before()` to run before a given directive (name without `x-`):

```js
Alpine.directive('foo', (el, { value, modifiers, expression }) => {
    Alpine.addScopeToNode(el, { foo: 'bar' })
}).before('bind')
```

By default custom directives run after most standard ones (except `x-teleport`).

## Custom magics

```js
Alpine.magic('[name]', (el, { Alpine }) => {})
```

- Name is consumed as `$<name>`; `el` is the element the magic was triggered from.
- Return a value → magic **property** (evaluated on each access):

  ```js
  Alpine.magic('now', () => (new Date).toLocaleTimeString())
  // <span x-text="$now">
  ```

- Return a function → magic **function** (double-arrow shorthand supported):

  ```js
  Alpine.magic('clipboard', subject => navigator.clipboard.writeText(subject))
  // <button @click="$clipboard('hello world')">
  ```

## Writing and sharing plugins

A plugin is a function (or array of functions) installed via `Alpine.plugin(...)`. The official "plugin-blueprint" package scaffolds one (`npm install && npm run build`).

## CSP build

The standard build evaluates inline expressions via `Function` declarations, which violate `unsafe-eval` CSP. The `@alpinejs/csp` build (CDN or `import Alpine from '@alpinejs/csp'`) avoids that and supports most inline expression syntax — but with limits.

**Supported:** object/array literals, basic operations and comparisons, ternaries, string concatenation, assignments/updates (`count++`, `count = 0`, `x-model="user.name"`), method calls (`items.push('c')`).

**Not supported:**

- Property assignment expressions like `user.name = 'John'` in event handlers (use a method)
- Arrow functions, destructuring, template literals, spread
- Global variables and functions: `console.log(...)`, `document.title`, `window.innerWidth`, `Math.max(...)`, `parseInt(...)`, `JSON.stringify(...)`
- HTML injection: `x-html`, `$el.insertAdjacentHTML(...)`

**Recommended pattern** — extract anything non-trivial into named functions or `Alpine.data()` components:

```html
<div x-data="userManager" x-show="hasActiveAdmins">
<script nonce="...">
    Alpine.data('userManager', () => ({
        users: [],
        get hasActiveAdmins() {
            return this.users.filter(u => u.active && u.role === 'admin').length > 0
        }
    }))
</script>
```

A CSP header that works with the build (drop `'unsafe-eval'`, use nonce-based scripts):

```
Content-Security-Policy: default-src 'self'; script-src 'nonce-[random]' 'strict-dynamic';
```

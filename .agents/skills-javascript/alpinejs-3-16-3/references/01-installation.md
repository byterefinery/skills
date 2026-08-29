# Alpine.js 3.16.3 — Installation

## From a script tag (CDN)

The simplest path. Include the **deferred** script in `<head>`; pin the version for production stability:

```html
<html>
    <head>
        <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.16.3/dist/cdn.min.js"></script>
    </head>
    <body>
        <h1 x-data="{ message: 'I ❤️ Alpine' }" x-text="message"></h1>
    </body>
</html>
```

- The `defer` attribute is required — Alpine initializes after DOM parse.
- `@3.x.x` pulls the latest 3.x; for stable production pin a full version like `@3.16.3`.
- Even with the core loaded, you still need at least one `x-data` on the page for directives to take effect.

### Script order with plugins

Plugin CDN builds register themselves via `document.addEventListener('alpine:init', ...)` when loaded before the core, so put **plugins first, core second** — all with `defer`:

```html
<head>
    <!-- Alpine Plugins -->
    <script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.16.3/dist/cdn.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.16.3/dist/cdn.min.js"></script>

    <!-- Alpine Core -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.16.3/dist/cdn.min.js"></script>
</head>
```

Alternative: load any script **after** the core and register inside the `alpine:init` event it fires:

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.16.3/dist/cdn.min.js"></script>
<script defer src="/my-extensions.js"></script>
```

```js
// my-extensions.js
document.addEventListener('alpine:init', () => {
    Alpine.data('myComponent', () => ({ /* ... */ }))
})
```

## As an npm module

```bash
npm install alpinejs @alpinejs/collapse @alpinejs/focus
```

```js
import Alpine from 'alpinejs'
import collapse from '@alpinejs/collapse'
import focus from '@alpinejs/focus'

Alpine.plugin(collapse)   // or Alpine.plugin([collapse, focus])
Alpine.data('dropdown', () => ({ /* ... */ }))
Alpine.store('cart', { /* ... */ })

window.Alpine = Alpine    // optional — handy for devtools

Alpine.start()
```

Rules:

- Register **all** extensions (plugins, `Alpine.data`, `Alpine.store`, `Alpine.bind`, custom directives/magics) **between** importing `Alpine` and calling `Alpine.start()`.
- Call `Alpine.start()` **exactly once per page** — a second call boots a parallel instance.

## Versioning

- `Alpine.version` exposes the runtime version string (`3.16.3`).
- Core and every stable plugin in the monorepo share the same version (3.16.3); exceptions in this tag: `@alpinejs/navigate` (3.10.2) and `@alpinejs/history` (3.0.0-alpha.0) — both have moved to the Livewire repo.

## CSP build (`@alpinejs/csp`)

Standard Alpine evaluates attribute expressions by constructing `Function` objects, which violates `unsafe-eval` Content-Security-Policy. The CSP build replaces the evaluator with a restricted one that supports most practical inline expressions.

```html
<!-- CSP-friendly core -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.16.3/dist/cdn.min.js"></script>
```

```bash
npm install @alpinejs/csp
```

```js
import Alpine from '@alpinejs/csp'
window.Alpine = Alpine
Alpine.start()
```

Supported: object/array literals, basic arithmetic and comparisons, property access, assignments and updates (`count++`), method calls, string concatenation, ternaries, simple member expressions.

Not supported: `new` expressions, `Function` construction, global variable/function references not in Alpine scope, complex arrow functions and template literals. When an expression gets too complex, extract it into a method on `x-data`/`Alpine.data` and call the method from the attribute.

Use the CSP build whenever the host page sets `script-src` without `'unsafe-eval'`.

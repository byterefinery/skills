# Installation (Alpine.js 3.17.5)

Two supported ways to include Alpine: a `<script>` tag, or importing it as a module. Either is valid.

## From a script tag (CDN)

Include the CDN build in the `<head>`:

```html
<html>
    <head>
        ...
        <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.17.5/dist/cdn.min.js"></script>
    </head>
    ...
</html>
```

- The `defer` attribute is required.
- `@3.x.x` floats the latest 3.x; for production stability pin the exact version (e.g. `@3.17.5`).
- Alpine directives only work once a component with `x-data` exists — the script alone is not enough for bare `x-*` attributes outside a component.

## As a module (npm)

```shell
npm install alpinejs
```

```js
import Alpine from 'alpinejs'

window.Alpine = Alpine   // optional; handy for devtools

Alpine.start()
```

- `window.Alpine = Alpine` is optional but useful for tinkering in devtools.
- Any extension code (plugins, `Alpine.data`, `Alpine.store`, `Alpine.bind`, custom directives/magics) must be registered **between** importing the `Alpine` global and calling `Alpine.start()`.
- `Alpine.start()` must be called **exactly once per page**; multiple calls create parallel Alpine instances.

## Loading plugins

Each official plugin has its own CDN build and npm package (`@alpinejs/<name>`).

**CDN** — plugin scripts go **before** the core script, both with `defer`:

```html
<!-- Alpine Plugins -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/morph@3.x.x/dist/cdn.min.js"></script>

<!-- Alpine Core -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

**npm** — import and register before `Alpine.start()`:

```js
import Alpine from 'alpinejs'
import morph from '@alpinejs/morph'

window.Alpine = Alpine
Alpine.plugin(morph)

// ...later...
Alpine.start()
```

`Alpine.plugin()` accepts a function or an array of functions. Every official plugin installs through it.

## Registering reusable data before init

With a CDN script tag, custom `Alpine.data`/`Alpine.store`/`Alpine.bind` registrations must happen after Alpine is downloaded but before it initializes the page — use the `alpine:init` event:

```html
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('dropdown', () => ({
            open: false,
            toggle() { this.open = ! this.open }
        }))
    })
</script>
```

If the registration code lives in an external file, that file's `<script>` tag must appear **before** Alpine's:

```html
<script src="/js/foo.js" defer></script>
<script src="/js/alpine.js" defer></script>
```

From a bundle, the equivalent is simply registering before `Alpine.start()` (see above).

## Building from the monorepo (development)

The source monorepo builds all packages with `npm run build` (ESBuild via `scripts/build.js`); outputs land in each `packages/<name>/dist/`. A "cdn" build is self-initializing and meant for a `<script defer src="...">` tag; `module.esm.js` / `module.cjs.js` are for module imports. Manual testing happens in `./index.html` at the repo root.

## CSP build

For Content-Security-Policy setups that forbid `unsafe-eval`, use the dedicated `@alpinejs/csp` build instead of the core:

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.x.x/dist/cdn.min.js"></script>
```

or

```js
import Alpine from '@alpinejs/csp'

window.Alpine = Alpine
Alpine.start()
```

It supports most inline expressions but not all — see [04-advanced](04-advanced.md#csp-build).

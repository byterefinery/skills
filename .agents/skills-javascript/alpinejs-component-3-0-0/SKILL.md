---
name: alpinejs-component-3-0-0
description: >
  Directive-based Alpine.js components with slots and cached template rendering, mounted in the light DOM
  (alpinejs-component v3.0.0). Use when building reusable HTML components in Alpine.js projects — on-page
  templates, remote URL templates, default and named slots, lifecycle events, or upgrading a v2 Shadow DOM
  setup to light DOM.
license: MIT
compatibility: >
  Requires Alpine.js 3.x. Modern browsers with template.content and Element.replaceChildren support.
metadata:
  tags:
    - alpinejs
    - web-components
    - light-dom
    - template-rendering
---

# alpinejs-component 3.0.0

## Overview

`alpinejs-component` v3 is an Alpine.js plugin that renders components from the `x-component` directive. It supports on-page `<template id="...">` references, remote URL fetching, default and named slots, lifecycle events, and bounded in-memory caches.

The defining v3 change: content mounts in the **light DOM**, not a Shadow DOM root. Page CSS applies to component content as-is, and `x-component-styles` no longer exists. When you want isolation, scope your CSS yourself (`@scope` or a class convention).

Components inherit the host element's Alpine scope, so reactive data from the host or any ancestor `x-data` is available inside the template.

### Core capabilities

- **On-page templates** — `x-component="'template-id'"` renders a `<template id="...">` from the page
- **Remote templates** — `x-component.url="'/path.html'"` fetches and renders HTML from a URL
- **Cross-origin** — `x-component.url.external` allows cross-origin HTTP(S) URLs
- **Slots** — `<slot>` and `<slot name="...">` in the template, filled by `x-slot` templates on the host
- **Light DOM** — `$refs`, `$root`, `label[for]`, `<form>` submission, and `document.querySelector` all reach component content
- **Lifecycle events** — `x-component:loading`, `x-component:loaded`, `x-component:error` on the host
- **Bounded caches** — template fragments (200) and remote fetch promises (200), LRU eviction

## Usage

### Installation

**CDN** — load the plugin before Alpine.js, pinning an exact version:

```html
<script defer src="https://unpkg.com/alpinejs-component@3.0.0/dist/component.min.js"></script>
<script defer src="https://unpkg.com/alpinejs@3.15.12/dist/cdn.min.js"></script>
```

Pin an exact version rather than `@latest` — a pinned URL is immutable, so you can add a Subresource Integrity hash. Don't combine `integrity` with a floating tag like `@latest` or `@3`; the file changes and the hash blocks the script entirely.

**Package manager** — install and register:

```bash
npm install alpinejs-component
```

```js
import Alpine from 'alpinejs'
import component from 'alpinejs-component'

Alpine.plugin(component)
Alpine.start()
```

### Basic patterns

**On-page template** — reference a `<template>` by its id; the template sees the host's Alpine scope:

```html
<div x-data="{ item: person }">
  <div x-component="'person-card'"></div>
</div>

<template id="person-card">
  <article>
    <h2 x-text="item.name"></h2>
    <p x-text="item.age"></p>
  </article>
</template>
```

**Remote template** — fetch HTML from a same-origin URL:

```html
<div x-component.url="'/public/person-card.html'"></div>
```

**Dynamic template selection** — the expression re-evaluates reactively:

```html
<div x-data="{ view: 'person-card' }">
  <section x-component="view"></section>
  <button x-on:click="view = 'summary'">Switch</button>
</div>
```

**Conditional rendering** — `null`, `undefined`, and empty strings unmount and clear the component:

```html
<div x-component="showCard ? 'card' : ''"></div>
```

**Slots** — fill `<slot>` elements with host-side `<template x-slot>` content:

```html
<div x-component="'card'">
  <template x-slot>
    <p>Default slot content</p>
  </template>
  <template x-slot="actions">
    <button>Save</button>
  </template>
</div>

<template id="card">
  <article>
    <slot></slot>
    <footer><slot name="actions"></slot></footer>
  </article>
</template>
```

**Styles** — no setup needed; page stylesheets apply to component content directly. For per-component scoping use `@scope (.person-card) { ... }` or a class convention.

## Gotchas

- **Light DOM means no style isolation** — page CSS applies to component content by default. v2's `x-component-styles` and `styles` are removed; if you relied on Shadow DOM to keep page styles *out* of a component, scope your CSS with `@scope` or a class convention instead.
- **Slot content inside `x-for`/`x-if` loses host scope** — a `<slot>` nested in an `x-for` or `x-if` template is still filled and repeated per iteration, but its content evaluates against the *component's* scope, not the host's. Alpine clones those templates and the host-scope binding does not survive the clone (documented known bug). Keep slots out of `x-for`/`x-if` if they need host data.
- **Slot templates must be direct children of the host** — only `:scope > template[x-slot]` is captured as slot content, and the templates are removed from the host up front. Non-slot host children are discarded when the component mounts. Multiple `x-slot` templates with the same name are merged, not replaced.
- **`x-component:loading` can be missed by the host's own listeners** — it is dispatched while the host's directives are still being processed, so an `x-on` on the host element itself can miss it. The events bubble (and are composed), so attach listeners to an ancestor.
- **A throwing expression is not `x-component:error`** — if the directive expression itself throws, Alpine's own error handler reports it and mounted content is cleared; no `x-component:error` is emitted.
- **Missing templates and failed fetches do emit `x-component:error`** — a nonexistent `<template id>` or a failed URL request emits the error event (plus a console warning/error). In v2, missing on-page templates only warned in the console.
- **`.url` is same-origin by default** — only `http(s)` protocols are accepted (`file:`, `data:`, … throw). Add `.external` to allow cross-origin `http(s)` URLs.
- **Stale async renders are discarded** — a slow URL response that lands after a newer render started is dropped, so rapid expression changes don't repaint with stale content.
- **No sanitization — trusted sources only** — template HTML is rendered verbatim through `innerHTML`. Don't put user input directly in `x-component` or `x-component.url`; validate and sanitize any dynamic template selection yourself.
- **CSP** — Alpine's default build compiles expressions with `new Function`, so the CSP must allow `'unsafe-eval'` (or switch Alpine to its CSP build, `@alpinejs/csp`; the plugin works with it unchanged).
- **Trusted Types needs two pieces** — under `require-trusted-types-for 'script'`, allow the pass-through policy name `alpinejs-component` in `trusted-types` *and* use Alpine's CSP build. The policy does not sanitize.
- **Pin CDN versions** — floating tags (`@latest`, `@3`) change the file; `integrity` hashes only make sense on pinned versions.

## References

- [01-directives](references/01-directives.md) — Full directive reference: `x-component`, `x-component.url`, `x-component.url.external`, expression normalization, dynamic values
- [02-slots](references/02-slots.md) — Slot system: default and named slots, fallback content, host-scope evaluation, the `x-for`/`x-if` limitation
- [03-lifecycle-events](references/03-lifecycle-events.md) — `x-component:loading`/`loaded`/`error`, payloads, why listeners belong on ancestors, what does and doesn't trigger errors
- [04-caching](references/04-caching.md) — Bounded LRU caches: template fragments, remote fetch promises, eviction and failure behavior
- [05-security](references/05-security.md) — Trust model, URL validation, CSP and Trusted Types setup, browser support
- [06-migration](references/06-migration.md) — Migrating from v2 (Shadow DOM to light DOM) and v1 (custom elements to directive)

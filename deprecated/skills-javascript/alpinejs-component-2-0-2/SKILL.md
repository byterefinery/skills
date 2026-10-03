---
name: alpinejs-component-2-0-2
description: >
  Directive-based Alpine.js components with Shadow DOM encapsulation, slots, and cached template rendering (alpinejs-component v2.0.2).
  Use when building reusable HTML components in Alpine.js projects — on-page templates, remote URL templates,
  style isolation via Shadow DOM, slot composition, lifecycle events, or migrating from v1 custom elements.
license: MIT
compatibility: >
  Requires Alpine.js 3.x. Modern browsers with Shadow DOM, adoptedStyleSheets, CSSStyleSheet, and template.content support.
  Node.js for ESM builds.
metadata:
  tags:
    - alpinejs
    - web-components
    - shadow-dom
    - template-rendering
---

# alpinejs-component 2.0.2

## Overview

`alpinejs-component` is an Alpine.js plugin that provides directive-based component rendering into Shadow DOM. It replaces the v1 custom-element approach with the `x-component` directive, supporting on-page `<template>` references, remote URL fetching, named/default slots, style encapsulation via `adoptedStyleSheets`, lifecycle events, and bounded in-memory caches.

The plugin mounts component content inside a Shadow DOM root on the host element, giving full style isolation. Templates inherit the host's Alpine scope, so reactive data from parent `x-data` is accessible inside the component.

### Core capabilities

- **On-page templates** — `x-component="'template-id'"` renders from a `<template id="...">` on the page
- **Remote templates** — `x-component.url="'/path.html'"` fetches and renders HTML from a URL
- **Cross-origin** — `x-component.url.external` allows cross-origin HTTP(S) URLs
- **Shadow DOM isolation** — all content renders into an open shadow root
- **Style injection** — `x-component-styles="title"` injects matching document stylesheets via `adoptedStyleSheets`
- **Slots** — `x-slot` on child `<template>` elements projects default and named slot content
- **Lifecycle events** — `x-component:loading`, `x-component:loaded`, `x-component:error`
- **Bounded caches** — templates (200), remote responses (200), stylesheets (100)

## Usage

### Installation

**CDN** — load the plugin before Alpine.js CDN, or after with `alpine:init`:

```html
<script defer src="https://unpkg.com/alpinejs-component@2.0.2/dist/component.min.js"></script>
<script defer src="https://unpkg.com/alpinejs@latest/dist/cdn.min.js"></script>
```

The CDN build auto-registers via `document.addEventListener('alpine:init', ...)`.

**Package manager** — install and register as an Alpine plugin:

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

**On-page template** — reference a `<template>` by its `id`:

```html
<div x-data="{ person: { name: 'Jane', age: 30 } }">
  <div x-component="'person-card'"></div>
</div>

<template id="person-card">
  <article>
    <h2 x-text="person.name"></h2>
    <p x-text="person.age"></p>
  </article>
</template>
```

The template accesses `person` from the host's Alpine scope.

**Remote template** — fetch HTML from a URL:

```html
<div x-component.url="'/components/person-card.html'"></div>
```

**Dynamic template selection** — use reactive expressions:

```html
<div x-data="{ view: 'person-card' }">
  <section x-component="view"></section>
  <button x-on:click="view = 'summary'">Switch</button>
</div>
```

**Slots** — project content into component templates:

```html
<div x-component="'card'">
  <template x-slot>
    <p>Default slot content</p>
  </template>
  <template x-slot="footer">
    <button>Save</button>
  </template>
</div>
```

**Styles** — inject document stylesheets into the shadow root:

```html
<style title="card">
  article { border: 1px solid #ddd; }
</style>

<div x-component="'card'" x-component-styles="card"></div>
```

## Gotchas

- **Shadow DOM scope isolation** — component content lives in a shadow root. Global CSS (e.g., `body { font-family }`) does not apply. Use `x-component-styles` or `styles="global"` to inject document styles. Without it, components render unstyled.
- **Template scope inheritance** — the component template accesses the *host element's* Alpine scope, not a new isolated scope. This means `x-data` on the host or any ancestor is available inside the template. Do not assume template isolation.
- **`x-slot` requires `<template>` wrappers** — slot content must be inside `<template x-slot>` or `<template x-slot="name">`, not plain elements. The plugin clones `template.content` and inserts it as slot children.
- **`:key` on `x-for` templates** — when iterating components inside `x-for`, use `<template x-for="..." :key="...">` wrapping the component host element. Without `:key`, Alpine may reuse DOM nodes incorrectly.
- **Expression normalization** — `null`, `undefined`, and empty strings clear the component (destroy shadow root content). Numbers and booleans are `String()`-converted. Use this for conditional rendering: `x-component="showCard ? 'card' : ''"`.
- **`.url` is same-origin by default** — `x-component.url` blocks cross-origin URLs. Add `.external` modifier to allow cross-origin HTTP(S). Non-HTTP(S) protocols (e.g., `file:`, `data:`) are always rejected.
- **`adoptedStyleSheets` strips `:root` rules** — when injecting stylesheets, `:root` CSS custom property rules are dropped to avoid conflicts. Define custom properties on `:host` or specific selectors instead.
- **`@import` rules are resolved recursively** — imported stylesheets are inlined, but CORS-restricted imports silently produce empty text. External stylesheet `@import`s may not appear in the shadow root.
- **Cleanup on reactive changes** — when the directive expression changes reactively, the old shadow root tree is destroyed (`Alpine.destroyTree`) before the new one mounts. Interval/timer side effects inside components are torn down.
- **CDN build auto-registers** — the CDN bundle listens for `alpine:init` and calls `Alpine.plugin()` automatically. Do not manually register when using the CDN build.
- **Missing templates produce console warnings** — if a template ID doesn't exist, the plugin logs a warning and renders nothing. No error event is dispatched for missing on-page templates (only for URL failures and expression errors).
- **Failed URL fetches are evicted from cache** — if a remote template fetch fails, the entry is removed so retries can succeed. Successful fetches stay cached.

## References

- [01-directives](references/01-directives.md) — Full directive reference: `x-component`, `x-component.url`, `x-component.url.external`, `x-component-styles`, modifiers
- [02-slots](references/02-slots.md) — Slot system: default slots, named slots, `x-slot` syntax, slot projection mechanics
- [03-lifecycle-events](references/03-lifecycle-events.md) — Custom events: `x-component:loading`, `x-component:loaded`, `x-component:error`, event payloads
- [04-styles](references/04-styles.md) — Shadow DOM styling: `adoptedStyleSheets`, `x-component-styles`, `styles` alias, `global` keyword, `:root` stripping
- [05-caching](references/05-caching.md) — Bounded caches: template fragments, remote responses, adopted stylesheets, eviction, cache limits
- [06-security](references/06-security.md) — Security model: no sanitization, origin checks, cross-origin blocking, CSP, trusted sources
- [07-migration](references/07-migration.md) — Migrating from v1: custom element to directive, API changes, removed features

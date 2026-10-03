# Migration from v1

## Overview

v1 used custom HTML elements (`<x-component>`) with registration-based naming. v2 uses the `x-component` Alpine directive, eliminating the need for custom element registration.

## API changes

### Custom element → Directive

**v1:**
```html
<x-component template="person"></x-component>
<x-component url="/public/person.html"></x-component>
```

**v2:**
```html
<div x-component="'person'"></div>
<div x-component.url="'/public/person.html'"></div>
```

### Registration removed

**v1** allowed renaming the custom element:
```js
window.xComponent.name = 'my-component'
// <my-component template="person"></my-component>
```

**v2** has no registration step. The directive is registered automatically when the plugin is loaded. There is no equivalent of `window.xComponent.name`.

### CDN auto-registration

**v1:** Manual plugin registration required.

**v2 CDN:** The CDN build (`component.min.js`) auto-registers via `alpine:init`:
```js
document.addEventListener('alpine:init', () => window.Alpine.plugin(component))
```

Do not manually register when using the CDN build.

## Feature mapping

| v1 Feature | v2 Equivalent |
|---|---|
| `<x-component template="id">` | `<div x-component="'id'"></div>` |
| `<x-component url="/path.html">` | `<div x-component.url="'/path.html'"></div>` |
| `window.xComponent.name` | Removed — no registration needed |
| Custom element slots | `x-slot` on `<template>` children |
| Style encapsulation | Shadow DOM (same as v1) |

## Migration steps

### 1. Replace custom elements with directives

Find all `<x-component>` (or renamed) elements and convert:

```diff
- <x-component template="card"></x-component>
+ <div x-component="'card'"></div>
```

```diff
- <x-component url="/components/card.html"></x-component>
+ <div x-component.url="'/components/card.html'"></div>
```

### 2. Update slot syntax

v1 used native slot projection inside the custom element. v2 uses `x-slot` on `<template>` children:

```diff
  <div x-component="'card'">
-   <span slot="header">Title</span>
+   <template x-slot="header">
+     <span>Title</span>
+   </template>
  </div>
```

### 3. Update style references

If using stylesheet injection, update to `x-component-styles`:

```diff
- <x-component template="card" styles="card-styles">
+ <div x-component="'card'" x-component-styles="card-styles"></div>
```

The `styles` attribute alias is also available in v2.

### 4. Remove registration code

Remove any `window.xComponent.name` assignments or custom registration logic:

```diff
- window.xComponent.name = 'app-component'
```

### 5. Update event handlers

Lifecycle events use the same names in v2:
- `x-component:loading`
- `x-component:loaded`
- `x-component:error`

Event handler syntax is the same, but attached to the host element:

```html
<div
  x-component.url="'/card.html'"
  x-on:x-component:loaded="onLoaded($event)"
  x-on:x-component:error="onError($event)"
></div>
```

## New features in v2

Features added in v2 that have no v1 equivalent:

- **Dynamic expressions** — template id/URL can be any Alpine expression
- **`.external` modifier** — explicit opt-in for cross-origin URLs
- **`styles` alias** — shorthand for `x-component-styles`
- **Bounded caches** — explicit cache limits with FIFO eviction
- **Expression error handling** — `x-component:error` for evaluation failures
- **Reactive re-rendering** — Alpine's `effect()` system handles reactive updates automatically

## Gotchas during migration

- **Directive expressions need quotes** — `x-component="'card'"` (string literal in Alpine expression), not `x-component="card"` (which would look for a JavaScript variable named `card`)
- **Host element is now any element** — v1 required `<x-component>`. v2 works with any element (`<div>`, `<section>`, `<article>`, etc.)
- **Slots require `<template>` wrappers** — plain child elements with `slot` attributes are not processed. Use `<template x-slot>` or `<template x-slot="name">`
- **No custom element lifecycle** — v1 custom elements had `connectedCallback`/`disconnectedCallback`. v2 uses Alpine's directive lifecycle (`effect`/`cleanup`)
- **CDN load order** — the CDN build of alpinejs-component must load before Alpine.js CDN (or Alpine must not have started yet), so that `alpine:init` fires after the plugin registers its listener

# Migration

## From v2 (Shadow DOM to light DOM)

v3 renders into the light DOM instead of a Shadow DOM root.

Remove `x-component-styles` and `styles`. They no longer exist, because document styles now reach component content on their own:

```html
<!-- v2 -->
<div x-component="'person-card'" x-component-styles="person-card"></div>

<!-- v3 -->
<div x-component="'person-card'"></div>
```

If you relied on Shadow DOM to keep page styles **out** of a component, scope your CSS with `@scope` or a class convention instead.

Templates, `.url`, `.external`, `x-slot`, and the lifecycle events carry over unchanged.

What you gain by dropping the shadow boundary:

- Page styles apply to component content with no configuration
- `$refs` and `$root` resolve across the host boundary
- `label[for]`, `aria-describedby`, and friends can reference component content
- Form controls inside a component submit with an ancestor `<form>`
- `document.querySelector` finds component content

Behavior notes for the upgrade:

- **Missing on-page templates now emit `x-component:error`** — in v2 they only produced a console warning.
- **Stylesheets are no longer injected or cached** — v2's `adoptedStyleSheets` pipeline (with its `:root` stripping and `@import` inlining) is gone along with Shadow DOM.

## From v1 (custom elements to directive)

v1 used custom elements:

```html
<x-component template="person"></x-component>
<x-component url="/public/person.html"></x-component>
```

v2 and v3 use the directive:

```html
<div x-component="'person'"></div>
<div x-component.url="'/public/person.html'"></div>
```

`window.xComponent.name` custom-element renaming is no longer used, because v2 and v3 are directive-based.

# Directives Reference

## `x-component="expression"`

Renders content from an on-page `<template>` element identified by its `id` attribute.

### Syntax

```html
<div x-component="'template-id'"></div>
```

### Expression evaluation

The expression is evaluated through Alpine's expression system. Supported value types:

| Value | Behavior |
|---|---|
| Non-empty string | Trimmed, used as template `id` |
| Number / boolean | Converted via `String()`, used as template `id` |
| `null` / `undefined` | Treated as empty — component is cleared |
| Empty string (`""`) | Component is cleared (shadow root content destroyed) |

### Dynamic expressions

```html
<div x-data="{ currentView: 'person-card' }">
  <div x-component="currentView"></div>
  <button x-on:click="currentView = 'summary'">Switch View</button>
</div>
```

When the reactive value changes, the component re-renders: the old shadow root is destroyed and the new template is mounted.

### Reactive clearing

Set the expression to `null`, `undefined`, or `""` to unmount the component:

```html
<div x-data="{ show: true }">
  <div x-component="show ? 'card' : ''"></div>
  <button x-on:click="show = !show">Toggle</button>
</div>
```

### Missing templates

If no `<template id="...">` matches the resolved id, a console warning is logged and nothing renders. No lifecycle error event is dispatched.

---

## `x-component.url="expression"`

Fetches HTML from a URL and renders it into the shadow root.

### Syntax

```html
<div x-component.url="'/components/card.html'"></div>
```

### URL resolution

The expression value is resolved as a URL relative to `window.location.href`. Only `http:` and `https:` protocols are accepted.

### Same-origin enforcement

By default, only URLs on the same origin as the page are allowed. Cross-origin URLs throw an error:

```
Cross-origin URL blocked for x-component.url: https://other-domain.com/template.html
```

### Expression behavior

Same value normalization as `x-component`: strings are trimmed, primitives are `String()`-converted, null/undefined/empty clear the component.

### Error handling

- Invalid URLs throw: `Invalid URL for x-component.url: <value>`
- Non-HTTP(S) protocols throw: `Unsupported URL protocol for x-component.url: <protocol>`
- Failed fetches (non-OK status) throw: `Request failed (<status>) for <url>`
- Failed fetches are evicted from the remote cache, allowing retries

---

## `x-component.url.external="expression"`

Allows cross-origin HTTP(S) URLs. Same behavior as `.url` but without the origin check.

### Syntax

```html
<div x-component.url.external="'https://cdn.example.com/templates/card.html'"></div>
```

### Security note

Cross-origin content is rendered without sanitization. Only use with trusted sources. See [06-security](06-security.md) for details.

---

## `x-component-styles="targets"`

Injects document stylesheets into the component's shadow root via `adoptedStyleSheets`.

### Syntax

```html
<div x-component="'card'" x-component-styles="card-styles,utility"></div>
```

### Target matching

Values are comma-separated stylesheet `title` attributes:

```html
<style title="card-styles">
  article { border: 1px solid #ccc; }
</style>

<style title="utility">
  .text-sm { font-size: 0.875rem; }
</style>
```

Only stylesheets whose `title` matches one of the targets are included.

### `global` keyword

Use `global` to include all local (same-origin) stylesheets:

```html
<div x-component="'card'" x-component-styles="global"></div>
```

### `styles` alias

`styles="..."` is shorthand for `x-component-styles="..."`:

```html
<div x-component="'card'" styles="card-styles"></div>
```

### Style processing details

- Only same-origin stylesheets are included (external `@import` hrefs are skipped)
- `:root` rules are stripped to avoid conflicts with the shadow root context
- `@import` rules are resolved recursively (CORS-restricted imports produce empty text)
- The combined CSS is compiled into a single `CSSStyleSheet` instance and cached
- See [04-styles](04-styles.md) for full details

---

## Modifiers summary

| Modifier | Directive | Effect |
|---|---|---|
| (none) | `x-component` | Render from on-page `<template>` by id |
| `.url` | `x-component.url` | Fetch and render from a same-origin URL |
| `.url.external` | `x-component.url.external` | Fetch and render from any HTTP(S) URL |

Modifiers are checked via `modifiers.includes('url')` and `modifiers.includes('external')` in the directive handler.

---

## Expression evaluation errors

If the directive expression itself throws during evaluation (e.g., referencing an undefined variable):

1. `x-component:error` is dispatched with `{ source: expression, error: evaluationError }`
2. The component source is treated as empty
3. Any currently mounted content is cleared

```html
<div x-component="undefinedVariable">
  <!-- Throws → emits error event, clears content -->
</div>
```

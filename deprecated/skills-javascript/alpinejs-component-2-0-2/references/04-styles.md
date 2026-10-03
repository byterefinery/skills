# Styles Reference

## Overview

Component content renders inside a Shadow DOM root, which provides full style encapsulation. Global CSS (from `<style>` tags, linked stylesheets, or browser defaults) does not penetrate the shadow boundary.

The plugin provides `x-component-styles` (alias: `styles`) to inject selected document stylesheets into the shadow root via the `adoptedStyleSheets` API.

## Shadow DOM style isolation

```html
<style>
  /* This does NOT apply inside the component */
  article { border: 1px solid #ddd; }
  h2 { color: blue; }
</style>

<div x-component="'card'"></div>
<!-- Content in shadow root — global CSS has no effect -->
```

Without `x-component-styles`, components render with no inherited styles (except browser user-agent defaults for the shadow root).

## `x-component-styles` directive

Select document `<style>` elements by their `title` attribute:

```html
<style title="card">
  article {
    border: 1px solid #ddd;
    padding: 1rem;
    border-radius: 4px;
  }
  h2 {
    color: #333;
    margin-bottom: 0.5rem;
  }
</style>

<div x-component="'card'" x-component-styles="card"></div>
```

### Multiple stylesheets

Comma-separated list of titles:

```html
<div x-component="'card'" x-component-styles="card,typography,utilities"></div>
```

### `styles` alias

```html
<div x-component="'card'" styles="card"></div>
```

Equivalent to `x-component-styles="card"`.

### `global` keyword

Include all same-origin stylesheets on the page:

```html
<div x-component="'card'" x-component-styles="global"></div>
```

This collects every `<style>` and `<link rel="stylesheet">` on the page (same-origin only), combines their CSS text, and adopts it.

## How style injection works

### Collection

1. If `global` is in the target list, all `document.styleSheets` are collected
2. Otherwise, only stylesheets whose `title` matches a target are included
3. External stylesheets (different origin `href`) are filtered out

### Processing

For each included stylesheet:

1. CSS rules are iterated via `stylesheet.cssRules`
2. `@import` rules are resolved recursively — the imported stylesheet's rules are inlined
3. `:root` rules are stripped (replaced with empty string) to avoid conflicts
4. All other rules are collected as CSS text

Accessing `cssRules` on CORS-restricted stylesheets throws — these silently produce empty text.

### Adoption

1. Combined CSS text is compiled into a `CSSStyleSheet` instance via `replaceSync()`
2. The stylesheet is assigned to `shadowRoot.adoptedStyleSheets`
3. The stylesheet instance is cached by the sorted target list string

### Caching

The adopted stylesheet is cached by a normalized key (sorted targets joined by `,`). Repeated renders with the same style targets reuse the cached `CSSStyleSheet`. Cache limit: 100 entries.

## `:root` rule stripping

`:root` CSS rules are removed during style processing:

```css
/* This rule is stripped */
:root {
  --primary: #3498db;
  --spacing: 1rem;
}

/* These rules are kept */
.card { padding: var(--spacing); }
h2 { color: var(--primary); }
```

**Reason:** `:root` matches the document root (`<html>`), not the shadow root. Custom properties defined on `:root` are still accessible inside shadow DOM (they cascade from the light DOM), so stripping the rule body avoids redundant definitions.

**Workaround for shadow-root-local custom properties:** use `:host` instead:

```html
<style title="card">
  :host {
    --card-bg: #fff;
    --card-border: #eee;
  }

  article {
    background: var(--card-bg);
    border-color: var(--card-border);
  }
</style>
```

## `@import` handling

CSS `@import` rules are resolved recursively:

```css
@import url('base.css');

.card { /* ... */ }
```

The imported stylesheet's rules are extracted and inlined. However:

- CORS-restricted imports (cross-origin stylesheets) throw when accessing `cssRules` — these produce empty text
- Only same-origin stylesheets are processed (external `href` stylesheets are filtered at collection time)

## Browser requirements

- `CSSStyleSheet` constructor — for creating new stylesheet instances
- `CSSStyleSheet.replaceSync()` — for populating stylesheet content
- `ShadowRoot.adoptedStyleSheets` — for adopting stylesheets into the shadow root
- `CSSRule` iteration — for extracting rules from document stylesheets

These APIs are supported in all modern browsers (Chrome 73+, Firefox 72+, Safari 13.1+, Edge 79+).

## Gotchas

- **No automatic style inheritance** — unlike light DOM, shadow DOM does not inherit global CSS. Always use `x-component-styles` or `styles="global"` to apply styles.
- **`@media` queries work** — media queries inside adopted stylesheets function normally within the shadow root.
- **`::part` and `::slotted`** — for styling from outside the shadow root, use `::part` (on elements with `part` attribute) or `::slotted()` selectors. The plugin does not add these automatically; they must be in the template or external CSS.
- **Style recalculation cost** — `adoptedStyleSheets` triggers a style recalculation. The caching system minimizes repeated adoption of the same stylesheet set.
- **Empty style target list** — if `x-component-styles` resolves to empty (e.g., all values are whitespace), no styles are injected. This is silent, not an error.

---
name: oat-0-7-1
description: Oat UI v0.7.1 — ultra-lightweight (~10KB), zero-dependency, semantic HTML/CSS/JS component library. Use when building web UIs with native HTML elements styled contextually without class pollution. Covers 30+ components — buttons, forms, dialogs, dropdowns, tabs, toasts, sidebar layouts, grids, tables, badges, avatars, tooltips, file uploads, tag inputs, and more. Supports automatic dark mode via light-dark(). No framework or build step required.
license: MIT
compatibility: Modern browsers with CSS @layer, light-dark(), popover API, and Web Components support (Chrome 114+, Firefox 122+, Safari 17.2+)
metadata:
  tags:
    - ui
    - css
    - components
    - frontend
---

# oat 0.7.1

## Overview

Oat is a semantic-first UI component library that styles native HTML elements automatically — no class pollution, no framework, no build step. It uses CSS `@layer` cascade, `light-dark()` for automatic dark mode, and native browser APIs (popover, `<dialog>`, `<details>`) to minimize JavaScript. Dynamic components are built as Web Components (`<ot-dropdown>`, `<ot-tabs>`, `<ot-taginput>`, `<ot-upload>`). The library exposes a small `window.ot` global for toasts.

Core design principles:

- **Semantic HTML** — `<button>`, `<dialog>`, `<details>`, `<progress>`, `<meter>` are styled out of the box
- **Zero class boilerplate** — contextual styling via attributes (`data-variant`, `role`, `aria-*`)
- **Automatic dark mode** — `light-dark()` follows OS preference; override with `[data-theme="dark"]`
- **Tiny footprint** — ~10KB minified CSS + JS combined
- **Progressive enhancement** — CSS-only components work without JS; JS adds interactivity on top

## Usage

### Quick start

Include via CDN:

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

Or via npm:

```bash
npm install @knadh/oat
```

```js
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

### Semantic styling — no classes needed

Most elements are styled automatically:

```html
<h1>Hello World</h1>
<p>Paragraphs, buttons, inputs, tables — all styled by default.</p>
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger" class="outline">Danger</button>
```

### CSS-only components

Many components need zero JavaScript:

- `<details>` / `<summary>` — accordions
- `<dialog>` with `commandfor` — modal dialogs
- `<progress>`, `<meter>` — progress bars and gauges
- `<input role="switch">` — toggle switches
- `[data-tooltip]` — tooltips from `title` attributes

### JS Web Components

Dynamic components registered as custom elements:

- `<ot-dropdown>` — positioned dropdown menus with keyboard nav
- `<ot-tabs>` — tabbed interfaces with deep-linking
- `<ot-taginput>` — tag input with autocomplete
- `<ot-upload>` — drag-and-drop file uploader

### Toast API

```js
ot.toast('Saved!', 'Success', { variant: 'success' });
ot.toast('Error', 'Oops', { variant: 'danger', placement: 'top-left' });
ot.toast.el(document.querySelector('#template'), { duration: 8000 });
ot.toast.clear();
```

## Gotchas

- **`light-dark()` browser support** — automatic dark mode requires Chrome 119+, Firefox 122+, Safari 17.4+. On older browsers, colors fall back to the first (light) value. Test dark mode explicitly on target browsers.
- **Popover API required** — `<ot-dropdown>` and toast containers use the native popover API. Safari needs 17.2+ or a polyfill. Without it, dropdowns and toasts will not display.
- **`command`/`commandfor` Safari gap** — Oat includes a polyfill for `command`/`commandfor` on buttons, but only for `<dialog>` targets. If using these attributes on other elements, provide your own handler.
- **CSS `@layer` is mandatory** — Oat uses `@layer theme, base, components, animations, utilities`. Custom overrides must either redefine variables in a later stylesheet or use `@layer` explicitly. Without `@layer`, cascade specificity can cause unexpected overrides.
- **`[data-field]` wraps form fields** — use `data-field` on a container (not the input itself) to get hint text styling and validation error display via `aria-invalid="true"`.
- **`ot-tabs` deep-linking needs IDs** — `data-anchor="key"` only works if tabs have `id` attributes. Without IDs, the hash won't sync.
- **`ot-taginput` value is array-based** — `.value` returns an array of tags (strings or objects). Setting `.value` replaces all tags. Use `el.add(tag)` to append individually.
- **`ot-upload` wraps a hidden file input** — the `<input type="file">` must be inside `<ot-upload>` and marked `hidden`. The component handles click-through and drag-and-drop. Listen to `change` on the component, not the input.
- **Dialog `closedby` attribute** — use `closedby="any"` to allow backdrop clicks to close. Without it, only Escape or explicit close commands work.
- **Sidebar mobile breakpoint is hardcoded** — the sidebar collapse at 768px is a fixed media query in CSS, not a CSS variable. Changing it requires overriding the stylesheet.
- **Grid stacks on mobile** — at `max-width: 768px`, the grid collapses to 4 columns and all `col-*` classes span full width. Offsets are ignored on mobile.
- **Individual file imports need base files first** — when importing component CSS files individually, always include `00-base.css` and `01-theme.css` first. Component files assume those layers exist.
- **`[data-variant]` is the primary semantic attribute** — use `data-variant="success|warning|danger|secondary"` on buttons, badges, alerts, and toasts. Class names like `.outline`, `.ghost`, `.small`, `.large` are visual modifiers layered on top.
- **Toast placement containers are auto-created** — toast containers are created dynamically with `popover="manual"`. They persist until `ot.toast.clear()` is called. Memory leaks are unlikely but clear on page unload if long-running.
- **Toasts pause on hover** — the auto-dismiss timer pauses when the user hovers a toast. Set `duration: 0` for persistent toasts that never auto-dismiss.

## References

- [01-installation](references/01-installation.md) — CDN, npm, download methods and build setup
- [02-layout](references/02-layout.md) — Grid system, sidebar layout, topnav, responsive behavior
- [03-typography](references/03-typography.md) — Headings, paragraphs, lists, code, blockquotes, base text elements
- [04-forms](references/04-forms.md) — Inputs, selects, textareas, checkboxes, radios, switches, fieldsets, validation
- [05-components-css](references/05-components-css.md) — CSS-only components: accordion, alert, avatar, badge, breadcrumb, button, card, dialog, meter, pagination, progress, skeleton, spinner, switch, table, tooltip
- [06-components-js](references/06-components-js.md) — JS Web Components: dropdown, tabs, taginput, toast, upload
- [07-utilities](references/07-utilities.md) — Utility classes, flex helpers, spacing, text alignment
- [08-customizing](references/08-customizing.md) — CSS variables, theming, dark mode, overrides, selective imports
- [09-recipes](references/09-recipes.md) — Composable patterns: split buttons, radio cards, form cards, empty states, stats dashboards
- [10-extensions](references/10-extensions.md) — Community extensions: oat-chips, oat-animate, oat-table, oat-upload

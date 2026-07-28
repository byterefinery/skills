---
name: oat-0-7-0
description: >
  Oat UI 0.7.0 is an ultra-lightweight, zero-dependency semantic HTML/CSS/JS UI component library (~10KB).
  No framework, no build tools, no class pollution — semantic tags styled contextually. Dynamic components
  use native Web Components. Use when building lightweight web apps, dashboards, admin panels, forms, or
  any UI needing buttons, cards, tables, dialogs, tabs, dropdowns, toasts, tooltips, file uploads, tag inputs,
  sidebars, grids, progress bars, badges, avatars, skeletons, spinners, alerts, or accordion/details panels.
  Also triggers on mentions of oat ui, oat.ink, @knadh/oat, semantic CSS, zero-dependency UI, or lightweight
  component libraries.
license: MIT
compatibility: Modern browsers with CSS @layer, light-dark(), color-mix(), and CSS nesting support. Requires CSS container queries for grid responsiveness.
metadata:
  tags:
    - ui
    - components
    - css
    - web-components
    - javascript
---

# oat 0.7.0

## Overview

Oat is a semantic, minimal, zero-dependency UI library. It styles standard HTML elements by default — no classes needed for basic elements like `<button>`, `<input>`, `<table>`, `<dialog>`, `<details>`. A handful of dynamic components use custom Web Components (`<ot-tabs>`, `<ot-dropdown>`, `<ot-taginput>`, `<ot-upload>`) with minimal JavaScript.

The library uses CSS `@layer` for cascade management, `light-dark()` for automatic dark mode, and `color-mix()` for derived colors. All theming is done via CSS custom properties defined in `01-theme.css`. Override them in your own stylesheet loaded after Oat's CSS.

### Design Philosophy

- **Semantic first** — `<button>`, `<input>`, `<table>`, `<dialog>`, `<details>` all styled without classes
- **Progressive enhancement** — works with HTML alone; JS adds interactivity for tabs, dropdowns, toasts, etc.
- **Zero dependencies** — no framework, no build step, no runtime besides browser
- **Automatic dark mode** — via `light-dark()` and `color-scheme: light dark`
- **Web Components** — dynamic parts use `<ot-tabs>`, `<ot-dropdown>`, `<ot-taginput>`, `<ot-upload>`
- **CSS `@layer`** — explicit cascade layers: `theme`, `base`, `components`, `animations`, `utilities`

### Web Components

| Element | Purpose |
|---|---|
| `<ot-tabs>` | Tabbed interface with keyboard nav, ARIA, deep-linking via `data-anchor` |
| `<ot-dropdown>` | Dropdown/popover with auto-positioning, keyboard nav, flip on overflow |
| `<ot-taginput>` | Tag input with Enter/comma to add, Backspace to remove, optional `<datalist>` autocomplete |
| `<ot-upload>` | Drag-and-drop file upload with removable file badges |

### Global API

| API | Purpose |
|---|---|
| `ot.toast(message, title?, options?)` | Show a text toast notification |
| `ot.toast.el(element, options?)` | Show a toast with custom HTML content |
| `ot.toast.clear(placement?)` | Clear all toasts or those at a specific placement |

## Usage

### Installation

**CDN** (quickest start):
```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat@0.7.0/oat.min.css">
<script src="https://unpkg.com/@knadh/oat@0.7.0/oat.min.js" defer></script>
```

**npm**:
```bash
npm install @knadh/oat
```
```js
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

### Basic HTML Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
  <link rel="stylesheet" href="oat.min.css">
  <script src="oat.min.js" defer></script>
</head>
<body>
  <div class="container">
    <h1>Hello World</h1>
    <p>This paragraph is styled automatically — no classes needed.</p>
    <button>Click me</button>
  </div>
</body>
</html>
```

### Theming

Override CSS variables in your own stylesheet loaded after Oat:

```css
:root {
  --primary: #2563eb;
  --primary-foreground: #fff;
  --background: #f8fafc;
  --foreground: #0f172a;
}
```

### Selective Inclusion

When including components individually, always include `00-base.css` and `01-theme.css` first, then pick component CSS files as needed. For JS, include `base.js` first, then component scripts.

## Gotchas

- **`light-dark()` and `color-mix()` are required** — Oat uses these modern CSS functions extensively. Browsers without support (Safari < 17.4 for `light-dark()`, Safari < 17.4 for `color-mix()`) will not render correctly. Polyfills or fallbacks needed for older browsers.
- **`defer` on the script tag** — always use `defer` on `oat.min.js` so Web Components register after DOM parsing. Without `defer`, custom elements may not be recognized.
- **Dialog uses native `<dialog>`** — no JS needed. Use `commandfor="dialog-id"` and `command="show-modal"` on buttons to open. Use `command="close"` to close. Safari needs the `commandfor` polyfill (bundled in oat.min.js).
- **Dropdown uses native `popover` API** — the `<menu popover>` element and `popovertarget` attribute are core to `<ot-dropdown>`. Positioning is calculated manually because popover positioning is fixed relative to the viewport.
- **Tabs deep-linking requires `id` on tabs** — `data-anchor="key"` on `<ot-tabs>` only works when the target `role="tab"` has an explicit `id`. Tabs without ids get auto-generated ids and won't deep-link.
- **Switch is a checkbox with `role="switch"`** — not a separate element. Use `<input type="checkbox" role="switch">` for toggle switches.
- **Accordion is native `<details>`/`<summary>`** — no JS, no custom element. Styled automatically. Adjacent `<details>` elements stack with shared borders.
- **TagInput emits `input` event** — not `change`. Listen for `input` to react to tag additions/removals. The `detail` property contains the current tag array.
- **Upload fires native `change`** — the `<ot-upload>` component dispatches the native `change` event on the inner `<input type="file">`. Access files via `input.files`.
- **Toast auto-dismisses** — default duration is 4000ms. Hover pauses dismissal. Use `duration: 0` for persistent toasts.
- **Grid stacks on mobile** — at `max-width: 768px`, all columns span full width (4 of 4 mobile columns). Offsets are ignored on mobile.
- **Sidebar breakpoint is 768px** — below this, sidebar becomes a slide-out overlay. Use `data-sidebar-layout="always"` to keep toggle visible on all sizes.
- **Skeleton requires `role="status"`** — the shimmer animation only applies to elements with both `role="status"` and class `skeleton`.
- **Spinner requires `aria-busy="true"`** — the spinner appears as a `::before` pseudo-element on any element with `aria-busy="true"`. Use `data-spinner="small|large|overlay"` for size variants.
- **`fieldset.group` for input groups** — use `class="group"` on `<fieldset>` to combine inputs with buttons or legend labels into connected input groups.
- **`data-field` for validation** — wrap form fields in `[data-field]` containers. Set `aria-invalid="true"` to reveal `.error` messages.
- **Tooltip auto-converts `title`** — Oat's JS automatically converts `title` attributes to `data-tooltip` for custom-styled tooltips. Use `data-tooltip-placement="bottom|left|right"` to control position.

## References

- [01-installation-usage](references/01-installation-usage.md) — CDN, npm, download, basic page structure, selective inclusion
- [02-theme-variables](references/02-theme-variables.md) — CSS custom properties, color tokens, spacing, typography, shadows, transitions, dark mode
- [03-typography](references/03-typography.md) — headings, paragraphs, links, code, blockquote, lists, mark, hr
- [04-layout](references/04-layout.md) — grid system (container, row, col, offset), sidebar layout, topnav
- [05-buttons](references/05-buttons.md) — button variants, sizes, outline, ghost, icon, button groups
- [06-forms](references/06-forms.md) — inputs, selects, textareas, checkboxes, radios, switches, ranges, file, date, fieldset, input groups, validation
- [07-data-display](references/07-data-display.md) — table, card, badge, skeleton, spinner, progress, meter
- [08-feedback](references/08-feedback.md) — alert, toast (ot.toast API), tooltip
- [09-navigation](references/09-navigation.md) — tabs (ot-tabs), dropdown (ot-dropdown), sidebar layout
- [10-interactive](references/10-interactive.md) — dialog, accordion (details/summary), taginput (ot-taginput), upload (ot-upload)
- [11-media](references/11-media.md) — avatar (single and grouped)
- [12-utilities](references/12-utilities.md) — utility classes, flex helpers, spacing, alignment, unstyled

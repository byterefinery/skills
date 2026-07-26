---
title: Installation and Usage
---

# Installation and Usage

## CDN

Include CSS and JS directly from unpkg or jsdelivr:

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat@0.7.0/oat.min.css">
<script src="https://unpkg.com/@knadh/oat@0.7.0/oat.min.js" defer></script>
```

Always use `defer` on the script tag so Web Components register after DOM parsing.

## npm

```bash
npm install @knadh/oat
```

Import in your project:

```js
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

Or import individual files from `@knadh/oat/css` and `@knadh/oat/js` for selective inclusion.

## Download

```shell
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

Include in your HTML:

```html
<link rel="stylesheet" href="./oat.min.css">
<script src="./oat.min.js" defer></script>
```

## Basic Page Structure

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
    <p>This paragraph is styled automatically.</p>
    <button>Click me</button>
  </div>
</body>
</html>
```

## Selective Inclusion

When including components individually rather than the full bundle, follow this order:

### Must include (always)
- `00-base.css` — CSS reset, box-sizing, base element styles
- `01-theme.css` — CSS custom properties (colors, spacing, typography, etc.)
- `base.js` — `OtBase` class, `commandfor` polyfill, dialog touch shim

### Then include as needed

**CSS files:**
- `animations.css` — reduced-motion media query, dialog backdrop animation
- `avatar.css` — avatar figure styling
- `button.css` — button variants, sizes, groups
- `form.css` — inputs, selects, textareas, checkboxes, radios, switches, ranges, fieldsets
- `table.css` — table styling
- `progress.css` — progress and meter bars
- `spinner.css` — spinner pseudo-element
- `grid.css` — 12-column grid system
- `card.css` — card container
- `alert.css` — alert banners
- `badge.css` — badge pills
- `accordion.css` — details/summary styling
- `tabs.css` — tab list and panels
- `dialog.css` — dialog modal styling
- `dropdown.css` — ot-dropdown popover styling
- `toast.css` — toast notifications
- `sidebar.css` — sidebar layout
- `taginput.css` — ot-taginput styling
- `skeleton.css` — skeleton loading placeholders
- `tooltip.css` — tooltip pseudo-elements
- `upload.css` — ot-upload styling
- `utilities.css` — utility classes

**JS files:**
- `tabs.js` — `<ot-tabs>` Web Component
- `dropdown.js` — `<ot-dropdown>` Web Component
- `upload.js` — `<ot-upload>` Web Component
- `tooltip.js` — title-to-data-tooltip converter
- `sidebar.js` — sidebar toggle handler
- `taginput.js` — `<ot-taginput>` Web Component
- `toast.js` — `ot.toast()` API

## Build from Source

Requires `esbuild` for bundling and minifying:

```bash
make dist    # Build CSS and JS to dist/
make css     # Concatenate and minify CSS
make js      # Bundle and minify JS
make clean   # Remove dist/
make size    # Show bundle sizes
```

## Browser Support

Oat requires modern CSS features:
- **CSS `@layer`** — cascade layer management
- **CSS nesting** — nested selectors (e.g., `&:hover`)
- **`light-dark()`** — automatic light/dark color switching
- **`color-mix()`** — color interpolation for derived colors
- **CSS `rgb(from ...)`** — color channel extraction
- **`@starting-style`** — entry animations for dialogs

Minimum browsers: Chrome 119+, Firefox 121+, Safari 17.4+, Edge 119+.

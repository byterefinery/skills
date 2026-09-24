# Installation and Setup

## CDN

Include CSS and JS directly:

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

Use `defer` on the script to ensure CSS is parsed first, avoiding flash of unstyled content.

## npm

```bash
npm install @knadh/oat
```

Import in a bundler project:

```js
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

Or import individual component files from `@knadh/oat/css` and `@knadh/oat/js` directories for selective bundling.

## Direct download

```shell
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

Then include locally:

```html
<link rel="stylesheet" href="./oat.min.css">
<script src="./oat.min.js" defer></script>
```

## Build system (for contributors)

Requirements:
- [esbuild](https://esbuild.github.io/) — bundles and minifies CSS/JS
- [zola](https://github.com/getzola/zola/releases) — static site generator for docs/demo

```bash
make dist    # Build CSS + JS bundles
make css     # Concatenate and minify CSS
make js      # Bundle and minify JS
make size    # Show bundle sizes
make clean   # Remove dist/
```

The `Makefile` concatenates individual CSS files in layer order into `dist/oat.css`, then minifies to `dist/oat.min.css`. JS is bundled via esbuild in IIFE format.

## Minimal HTML template

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
  <h1>Hello World</h1>
  <p>This paragraph is styled automatically.</p>
  <button>Click me</button>
</body>
</html>
```

## Browser requirements

- CSS `@layer` — Chrome 99+, Firefox 95+, Safari 15+
- `light-dark()` — Chrome 119+, Firefox 122+, Safari 17.4+
- Popover API — Chrome 114+, Firefox 122+, Safari 17.2+
- Web Components (Custom Elements v1) — all modern browsers
- `@starting-style` — Chrome 111+, Safari 16.4+ (used for dialog/toast animations)

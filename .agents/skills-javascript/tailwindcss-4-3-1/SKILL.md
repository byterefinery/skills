---
name: tailwindcss-4-3-1
description: Tailwind CSS v4.3.1 — utility-first CSS framework. Use when working with Tailwind CSS v4 projects, configuring @theme, writing utility classes, using @apply, @utility, @variant directives, setting up build tools (Vite, PostCSS, CLI), or customizing the design system with CSS variables. Covers the new CSS-native configuration approach, arbitrary values, color opacity modifiers, and the plugin API.
metadata:
  tags:
    - css
    - frontend
    - styling
    - design-system
---

# tailwindcss 4.3.1

Tailwind CSS v4 is a rewrite that replaces JS config with CSS-native `@theme` blocks, uses a Rust engine for speed, and introduces `@utility`/`@variant` directives for custom utilities and variants. No `tailwind.config.js` needed by default.

## Overview

- **CSS-native config** — define theme values in `@theme` blocks instead of `tailwind.config.js`
- **No build config required** — works with Vite, PostCSS, CLI, and webpack out of the box
- **Arbitrary values** — use `[...]` syntax for any value: `w-[200px]`, `text-[#bada55]`
- **Color opacity modifiers** — `bg-red-500/50` applies 50% opacity via `color-mix`
- **New directives** — `@utility`, `@variant`, `@theme`, `@source`, `@import` with Tailwind functions
- **oklch colors** — default palette uses oklch for better perceptual uniformity
- **`@layer` system** — `theme`, `base`, `components`, `utilities` layers

## Usage

### Installation

```bash
npm install tailwindcss @tailwindcss/vite  # Vite
npm install tailwindcss @tailwindcss/postcss  # PostCSS
npm install tailwindcss @tailwindcss/cli  # CLI
```

### CSS Entry Point

```css
@import "tailwindcss";
```

Or import specific parts:

```css
@import "tailwindcss/theme";
@import "tailwindcss/utilities";
```

### Customizing Theme

Define theme values in a `@theme` block in your CSS:

```css
@theme {
  --color-brand: oklch(0.7 0.15 145);
  --color-brand-foreground: oklch(0.2 0.02 145);
  --font-heading: "Inter", sans-serif;
  --breakpoint-3xl: 120rem;
  --radius-xl: 1rem;
}
```

Theme values map directly to utility classes: `bg-brand`, `font-heading`, `3xl:text-lg`, `rounded-xl`.

### Using Utilities

```html
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h1 class="text-2xl font-bold text-gray-900">Hello</h1>
  <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Click
  </button>
</div>
```

### Arbitrary Values

```html
<div class="w-[200px] h-[100vh] text-[#bada55] bg-[url('/img.png')]">
  <span class="m-[10px] p-[2%] border-[3px]">Arbitrary</span>
</div>
```

### Responsive Design

```html
<div class="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl">
  Responsive text
</div>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  Responsive grid
</div>
```

Default breakpoints: `sm` (40rem), `md` (48rem), `lg` (64rem), `xl` (80rem), `2xl` (96rem).

### Dark Mode

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Dark mode content
</div>
```

Uses `@media (prefers-color-scheme: dark)` by default.

### Common Patterns

**Card component:**
```html
<div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
  <h2 class="text-lg font-semibold text-gray-900">Title</h2>
  <p class="mt-2 text-sm text-gray-600">Description</p>
</div>
```

**Button variants:**
```html
<button class="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors hover:bg-gray-100">
  Default
</button>
<button class="inline-flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-600">
  Primary
</button>
```

**Navigation:**
```html
<nav class="flex items-center gap-6 border-b border-gray-200 px-4 py-3">
  <a class="text-sm font-medium text-gray-900 hover:text-blue-500">Home</a>
  <a class="text-sm font-medium text-gray-500 hover:text-blue-500">About</a>
</nav>
```

## Gotchas

- **`@theme` values must start with `--`** — they are CSS custom properties. Use `--color-*` for colors, `--font-*` for fonts, `--breakpoint-*` for breakpoints, etc.
- **`@theme` overrides default values** — when you define `--color-brand`, it adds to the theme. To remove a default color, set `--color-red-*: initial;` (namespace clear).
- **No `tailwind.config.js` by default** — v4 uses CSS-native config. The JS config is available via `@config` directive or the compat plugin API for migration.
- **`@apply` only works with utilities** — you cannot `@apply` arbitrary values or variant-modified classes. Use `@apply` inside `@layer components` or regular CSS rules.
- **Variant order matters** — `hover:focus:bg-red-500` and `focus:hover:bg-red-500` may produce different CSS specificity. Tailwind sorts variants deterministically.
- **`group-*` and `peer-*` auto-compound** — in v4, `group-hover`, `peer-focus`, etc. work automatically without special setup. Use `group` class on parent, `peer` on sibling.
- **Color opacity uses `color-mix`** — `bg-red-500/50` compiles to `color-mix(in oklab, <color> 50%, transparent)`, not `rgba()`. This gives better perceptual results.
- **Spacing scale is `0.25rem` base** — `p-4` = `1rem` (4 × 0.25rem). Use fractional values: `p-1.5` = `0.375rem`.
- **`@utility` requires `-*` suffix for functional utilities** — `@utility tab-* { tab-size: --value(integer); }` creates `tab-4`, `tab-8`, etc.
- **Dark mode is media-query based by default** — unlike v3's class strategy, v4 uses `prefers-color-scheme`. Use `@variant dark` to customize.
- **`container` utility is responsive** — it automatically sets `max-width` at each breakpoint. No need for `max-w-*` alongside it.

## References

- [01-theme-system](references/01-theme-system.md) — @theme blocks, CSS variable namespaces, customization patterns
- [02-layout-utilities](references/02-layout-utilities.md) — Display, positioning, flexbox, grid, sizing, spacing
- [03-colors-backgrounds](references/03-colors-backgrounds.md) — Color utilities, backgrounds, gradients, opacity
- [04-typography](references/04-typography.md) — Text utilities, font sizes, weights, line height, decoration
- [05-borders-shadows](references/05-borders-shadows.md) — Border radius, shadows, rings, outlines
- [06-transforms-transitions](references/06-transforms-transitions.md) — Transforms, transitions, animations, will-change
- [07-filters-blurs](references/07-filters-blurs.md) — Filters, backdrop filters, blurs, brightness, contrast
- [08-variants](references/08-variants.md) — Responsive, hover, focus, dark mode, compound variants, state
- [09-at-directives](references/09-at-directives.md) — @apply, @utility, @variant, @theme, @layer, @source
- [10-plugin-api](references/10-plugin-api.md) — Plugin API, addUtilities, addVariant, matchUtilities, createPlugin
- [11-build-tools](references/11-build-tools.md) — Vite, PostCSS, CLI, webpack, migration from v3
- [12-arbitrary-values](references/12-arbitrary-values.md) — Arbitrary values, modifiers, data types, patterns

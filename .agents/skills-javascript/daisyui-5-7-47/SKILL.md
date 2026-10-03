---
name: daisyui-5-7-47
description: daisyUI 5.7.47 — component library for Tailwind CSS 4. Use when building UI with daisyUI components (btn, modal, drawer, menu, card, table, tab, toast, etc.), daisyUI semantic colors and themes (primary, base-100, data-theme), or configuring the daisyUI plugin with Tailwind CSS. Covers all 63 daisyUI 5 components, 33 built-in themes, custom themes, prefixes, and CDN usage.
license: MIT
compatibility: Requires Tailwind CSS 4 (daisyUI 5 does not support Tailwind CSS 3)
metadata:
  tags:
    - css
    - frontend
    - styling
    - design-system
    - tailwindcss
---

# daisyui 5.7.47

daisyUI 5 is a CSS-only component library for Tailwind CSS 4. It supplies class names for 63 UI components, semantic colors, and 33 built-in themes. It is added as a Tailwind CSS `@plugin` in your CSS — there is no JS runtime and no `tailwind.config.js`. Components are plain HTML: add daisyUI classes to standard elements, and compose state with CSS-only toggles (checkbox, radio, `dialog`, `popover`) plus Tailwind utilities.

## Overview

- **Tailwind CSS 4 only** — daisyUI 5 requires Tailwind 4; the v3 config file is not used
- **CSS-only components** — no JavaScript in the library; interactivity comes from `:checked`, `:hover`, `<dialog>`, and `<div popover>`
- **Semantic colors** — `primary`, `base-100`, `error`, etc. resolve to theme CSS variables, so colors follow `data-theme` automatically
- **33 built-in themes** — `light` and `dark` are enabled by default; enable more with `themes:` in the plugin config
- **Custom themes** — defined with `@plugin "daisyui/theme" { ... }` blocks
- **Per-project options** — `themes`, `root`, `include`, `exclude`, `prefix`, `logs`
- **CDN available** — precompiled CSS with no build step

## Usage

### Installation

```bash
npm i -D daisyui
```

CSS entry file (daisyUI loads through a Tailwind CSS 4 `@plugin`):

```css
@import "tailwindcss";
@plugin "daisyui";
```

Configuration is written in the same CSS file; full options in [03-configuration](references/03-configuration.md).

CDN (no install; precompiled daisyUI CSS + Tailwind browser build):

```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

The main CDN file includes the `light` and `dark` themes. For all built-in themes use `https://cdn.jsdelivr.net/npm/daisyui@5/themes.css`. CDN files do not include the `is-drawer-open:` and `is-drawer-close:` variants.

Framework install guides (Next.js, Vite, SvelteKit, Vue, Nuxt, Rails, Astro, HTMX, …): https://daisyui.com/docs/install/

### Writing components

Add the component class to a standard HTML element, plus applicable part, modifier, and style classes:

```html
<button class="btn btn-primary">Submit</button>
<div class="card">
  <div class="card-body">
    <h2 class="card-title">Card title</h2>
  </div>
</div>
```

Class name categories (reference only — do not use them in code): `component`, `part`, `style`, `behavior`, `color`, `size`, `placement`, `direction`, `modifier`, `variant`.

Overriding with Tailwind utilities: if a daisyUI style blocks a change, use a utility class, and the `!` suffix only when specificity still wins (`btn bg-red-500!`). If daisyUI lacks a component or variant, build it with Tailwind utilities. To change a component globally, use the Tailwind `@utility` directive:

```css
@utility btn {
  @apply rounded-full;
}
```

### Choosing a component

Match the requested function, not the words: read the category in [01-components](references/01-components.md) that fits the task, then the component section (and its examples) before writing markup. When a choice is not clear, compare the candidates' structure and rules — several components overlap (e.g., `collapse` vs `accordion` behavior, `menu` inside `drawer`, `join` with any input). Obey the structural rules exactly: several components require specific element types, child parts, or hidden inputs with matching `id`/`for` pairs.

Component files and the official per-component docs (https://daisyui.com/components/<name>/) are the source of truth for class names — do not invent class names.

### Colors and themes

Use daisyUI semantic color names in Tailwind color utilities (`bg-primary`, `border-base-300`, `text-base-content/60`). Never combine the `dark:` variant with daisyUI color names — the theme already handles dark mode. Prefer `base-*` colors for most of the page; use `primary` once, for the single most important element. Switch themes with `data-theme="NAME"` on `<html>` or any nested element (nesting is unlimited); `theme-controller` inputs do the same when checked. Full rules and a custom-theme template in [02-colors-themes](references/02-colors-themes.md).

## Gotchas

- **daisyUI 5 requires Tailwind CSS 4** — `tailwind.config.js` is deprecated in Tailwind 4; configure daisyUI in CSS via `@plugin "daisyui" { ... }`, not a JS config file.
- **`<dialog>` is preferred over checkbox modals** — the `modal-toggle` checkbox and anchor-link modals are legacy. Use `<dialog class="modal">` + `<form method="dialog">`, or the popover API (`<div class="modal" popover>` + `popovertarget`) when keyboard focus must not be trapped.
- **Hidden-input components need unique `id`/`for` pairs** — `drawer` (`drawer-toggle` input + `drawer-button` label), `modal` (legacy checkbox), `swap`, `collapse` variants: the label's `for` must match the input's `id`, or the toggle silently does nothing.
- **Do not use `dark:` with daisyUI colors** — semantic colors already adapt per theme; `dark:bg-primary` double-applies.
- **The `is-drawer-open:` / `is-drawer-close:` variants are missing from CDN files** — they work only in a local build; in CDN setups toggle drawer state with `drawer-open` class or `lg:drawer-open` instead.
- **One `primary` per page** — reserve `primary` for the single most important element; everything else uses `base-*`, `secondary`, or `neutral`.
- **CDN themes are limited** — the main CDN file ships only `light` and `dark`; use `themes.css` for the full set.
- **State is CSS-only** — drawer, modal, collapse, filter, and swap are driven by hidden checkboxes/radios or the `dialog`/`popover` APIs. Do not add JavaScript to toggle them; add `tabindex="-1" role="button" aria-disabled="true"` when disabling a `btn` with a class.
- **`btn` class name categories do not stack within a category** — one color, one style, one size, one modifier; e.g., `btn btn-primary btn-ghost` is invalid.
- **`prefix` applies to daisyUI classes only** — `prefix: daisy-` produces `daisy-btn`, not `daisy-flex`; Tailwind utilities are untouched.
- **Base modules are included by default** — `properties`, `rootcolor`, `scrollbar`, `rootscrolllock`, `rootscrollgutter`, `svg`; exclude specific ones in the plugin config if they interfere (e.g., `exclude: rootscrollgutter`).

## References

- [01-components](references/01-components.md) — all 63 components by category, with class names, syntax, and rules
- [02-colors-themes](references/02-colors-themes.md) — semantic colors, built-in themes, custom themes, theme-controller
- [03-configuration](references/03-configuration.md) — @plugin options, base modules, @utility overrides, CDN variants

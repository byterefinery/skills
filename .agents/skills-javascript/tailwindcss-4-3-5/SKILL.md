---
name: tailwindcss-4-3-5
description: Tailwind CSS 4.3.5 — utility-first CSS framework with CSS-first configuration. Use when working with Tailwind CSS v4 projects — writing utility classes, configuring the design system with @theme, defining custom utilities (@utility) or variants (@custom-variant, @variant), using @apply, @source, @reference, @plugin, @config, setting up build integrations (Vite, PostCSS, CLI, Turbopack, webpack, browser), upgrading from v3 with @tailwindcss/upgrade, or writing JS plugins (matchUtilities, matchVariant, addVariant, theme, config). Covers the default theme namespaces, the spacing multiplier, opacity modifiers, important placement, built-in variants, and v3 compatibility.
license: MIT
compatibility: Tailwind CSS 4.3.5 packages (tailwindcss, @tailwindcss/vite, @tailwindcss/postcss, @tailwindcss/cli, @tailwindcss/turbopack, @tailwindcss/webpack, @tailwindcss/browser, @tailwindcss/upgrade). Native file scanner from @tailwindcss/oxide with WASM fallback on platforms without native bindings.
metadata:
  tags:
    - css
    - styling
    - frontend
---

# tailwindcss 4.3.5

## Overview

Tailwind CSS 4.3.5 is a utility-first CSS framework. The v4 architecture is CSS-first — no JS config file is required:

- One entry — `@import "tailwindcss";` pulls in the theme (`theme.css`), preflight (`preflight.css`), and utilities (`utilities.css`) in the `theme, base, components, utilities` layers.
- Design system in CSS — tokens live in `@theme { … }` custom-property blocks; namespaces map to utility families (e.g. `--color-primary` → `bg-primary`, `--breakpoint-md` → `md:*`).
- On-demand generation — a native scanner (`@tailwindcss/oxide`) extracts candidate classes from source files and only the utilities that are used are compiled. Automatic source detection respects `.gitignore` (including negation patterns).
- Customization directives — `@utility` (custom utilities), `@custom-variant` / `@variant` (custom variants), `@apply`, `@source`, `@reference`, plus a v3 compatibility layer (`@config`, `@plugin`, JS plugin API via `tailwindcss/plugin`).
- Importable entry points — `tailwindcss`, `tailwindcss/preflight`, `tailwindcss/theme`, `tailwindcss/utilities` are separate CSS exports for custom setups.

## Usage

Vite (the setup used by the repo's own playground):

```ts
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

```css
/* src/index.css */
@import 'tailwindcss';
```

PostCSS (the setup used by the repo's Next.js playground):

```js
// postcss.config.js
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

Standalone CLI (build a stylesheet from an input file):

```bash
npx @tailwindcss/cli build --input ./src/input.css --output ./dist/output.css --watch
```

Then use utility classes directly in markup:

```html
<button class="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 md:px-6">Save</button>
```

A minimal CSS file can define its own design system before using it:

```css
@theme {
  --color-primary: oklch(0.6 0.2 250);
  --breakpoint-lg: 64rem;
}

@utility card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}
```

## Gotchas

- **Important is a trailing `!` in v4** — write `mx-4!`, not `!mx-4`. The leading v3-style form still parses as important for compatibility.
- **`@tailwind base` and `@tailwind components` do not exist in v4** — only `@tailwind utilities` is processed (and only once). Preflight is part of the main import; component classes are plain CSS (optionally in `@layer components`).
- **`@theme` blocks may only contain custom properties or `@keyframes`** — a nested selector like `.foo { --x: red }` inside `@theme` is a hard error.
- **`@source` paths must be quoted** — `@source "./src/**/*.{ts,tsx}";`. Use `@source not "…"` to exclude, `@source inline("…")` to force-include candidates that no scanned file contains.
- **`hover:` only applies on devices that support hover** — the variant compiles to `@media (hover: hover) { …:hover }`, so hover styles are intentionally absent on touch devices.
- **`dark:` follows `prefers-color-scheme` by default** — for class-based dark mode, override it with `@custom-variant dark (&:where(.dark, .dark *));`
- **`@utility` must be top-level, non-empty, and named properly** — no nesting, no empty bodies, lowercase-alphabetic names, and functional utilities must end in `-*` (e.g. `@utility push-*`), with the dynamic `-*` appearing exactly once at the end.
- **`@custom-variant` takes either a selector list or a body with `@slot` — never both**, and it cannot be nested.
- **`@plugin` options are flat CSS declarations only** — strings, numbers, booleans, and comma-separated value lists work; object values are rejected ("currently only supported in JavaScript configuration files").
- **`@config` and `@plugin` are v3 compatibility shims** — new v4 code should use `@theme` / `@utility` / `@custom-variant`. Use `npx @tailwindcss/upgrade` to migrate a v3 project (requires a clean git tree or `--force`).
- **Spacing utilities are multipliers, not fixed values** — `p-4` is `calc(var(--spacing) * 4)` with `--spacing: 0.25rem` by default; changing `--spacing` rescales the whole scale.
- **Width/height resolve from several namespaces** — `w-*` looks up `--width-*`, then `--spacing` (multiplier), then `--container-*`; custom values go in the matching namespace.

## References

- [01-setup](references/01-setup.md) — build integrations (Vite, PostCSS, CLI, Turbopack, webpack, browser), package entry points, @tailwindcss/upgrade
- [02-theme-and-sources](references/02-theme-and-sources.md) — @theme options and default namespaces, @source, @reference, v3 @config/@plugin, JS plugin API
- [03-directives](references/03-directives.md) — @utility, @custom-variant, @variant, @apply, @scope, @tailwind utilities
- [04-utilities-and-variants](references/04-utilities-and-variants.md) — candidate syntax, important/opacity/arbitrary values, spacing, built-in variant families

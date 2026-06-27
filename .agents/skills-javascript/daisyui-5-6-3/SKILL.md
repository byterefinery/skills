---
name: daisyui-5-6-3
description: daisyUI 5 component library for Tailwind CSS 4. Provides class names for UI components, semantic color system, and built-in themes. Use when generating HTML/JSX, building UIs with Tailwind CSS, creating dashboards, forms, navigation, modals, tables, cards, buttons, or any frontend UI work. Also triggers on mentions of daisyUI, component libraries, Tailwind plugins, CSS components, or theme customization.
---

# daisyui 5.6.3

## Overview

daisyUI 5 is a CSS component library for Tailwind CSS 4. It provides class names for common UI components, semantic color names, and built-in themes — all without writing custom CSS. Instead of long utility class strings, you write `<button class="btn btn-primary">` and get a fully styled, theme-aware button.

daisyUI 5 requires Tailwind CSS 4. Configuration uses `@plugin "daisyui"` in CSS (no `tailwind.config.js`).

## Usage

### Installation

**npm dependency** (recommended):
```css
@import "tailwindcss";
@plugin "daisyui";
```

**CDN** (prototyping only):
```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

### Config

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark;
  root: ":root";
  include: ;
  exclude: ;
  prefix: ;
  logs: true;
}
```

### Class Name Categories

Each component has class names in these categories:
- `component` — required base class
- `part` — child elements
- `style` — visual variant (outline, soft, ghost, etc.)
- `color` — semantic color (primary, success, error, etc.)
- `size` — xs, sm, md, lg, xl
- `placement` / `direction` — positioning modifiers
- `modifier` — behavioral or structural changes

### Component Discovery Protocol

Before writing daisyUI code:
1. Read the request intent, behavior, and shape — match on meaning, not literal words
2. Shortlist candidates from the reference files
3. Compare at least 3 candidates when ambiguous
4. Select the best component and apply its constraints exactly

## Gotchas

- **No `tailwind.config.js`** — Tailwind CSS v4 deprecated it. Use `@plugin "daisyui"` in your CSS file instead.
- **Always use daisyUI color names** (`bg-primary`, `text-base-content`) instead of Tailwind colors (`bg-red-500`, `text-gray-800`). Tailwind colors don't change with themes, so `text-gray-800` on a dark theme's `bg-base-100` becomes unreadable.
- **No `dark:` prefix needed** — daisyUI color names automatically adapt to the active theme.
- **Use `primary` sparingly** — reserve it for the single most important element on the page. Use `base-*` colors for everything else.
- **Override with `!` only as last resort** — if Tailwind utilities don't override daisyUI styles due to specificity, use `btn bg-red-500!` sparingly.
- **Don't add `bg-base-100 text-base-content` to body** unless necessary — these are defaults.
- **Drawer wraps everything** — when using drawer, navbar, footer, and all page content must be inside `drawer-content`, not outside the `drawer` div.
- **Modal IDs must be unique** — each modal needs its own ID for checkbox/anchor toggling or dialog element targeting.
- **Accordion uses radio inputs** — all radios sharing a `name` form one accordion group (only one open at a time). Use different names for separate groups.
- **hover-3d requires exactly 9 children** — the first is content, the remaining 8 are empty `<div>` hover zones. Put non-interactive content only inside it.
- **OTP span count must match maxlength** — 4 spans means `maxlength="4"` and `pattern="[0-9]{4}"`.
- **Custom themes require all CSS variables** — every `--color-*`, `--radius-*`, `--size-*`, `--border`, `--depth`, and `--noise` variable is mandatory.

## References

- [01-install-config](references/01-install-config.md) — Installation methods, config options, Tailwind CSS 4 integration
- [02-colors-themes](references/02-colors-themes.md) — Semantic color names, color rules, built-in themes, custom theme creation
- [03-layout-components](references/03-layout-components.md) — divider, join, stack, hero, indicator
- [04-typography](references/04-typography.md) — link, kbd, text-rotate, loading
- [05-form-elements](references/05-form-elements.md) — input, textarea, select, checkbox, radio, toggle, range, file-input, label, fieldset, otp, validator
- [06-navigation](references/06-navigation.md) — navbar, breadcrumbs, menu, megamenu, tab, drawer, dock, pagination
- [07-feedback](references/07-feedback.md) — alert, toast, modal, tooltip, skeleton, progress, radial-progress, countdown, swap, status
- [08-media](references/08-media.md) — avatar, chat, carousel, mockup-browser, mockup-code, mockup-phone, mockup-window
- [09-data-display](references/09-data-display.md) — table, stats, list, timeline, steps, badge
- [10-interactive](references/10-interactive.md) — button, dropdown, fab, collapse, accordion, filter, card
- [11-utilities](references/11-utilities.md) — mask, indicator, diff, aura, hover-3d, hover-gallery

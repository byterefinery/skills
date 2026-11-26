# Oat Usage and Theming Reference

## Contents

- [Installation](#installation)
- [Package contents](#package-contents)
- [Selective component bundling](#selective-component-bundling)
- [CSS layers](#css-layers)
- [Theming](#theming)
- [Color variables](#color-variables)
- [Design token variables](#design-token-variables)
- [Dark mode](#dark-mode)
- [Library development setup](#library-development-setup)

## Installation

### CDN

Include the CSS and JS files directly in your HTML:

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
<script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
```

### npm

```bash
npm install @knadh/oat
```

Then import in your project:

```js
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

Or import individual component files from `@knadh/oat/css` and `@knadh/oat/js` (see [Selective component bundling](#selective-component-bundling)).

### Download

```shell
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

Then include them in your project:

```html
<link rel="stylesheet" href="./oat.min.css">
<script src="./oat.min.js" defer></script>
```

## Package contents

- `oat.min.css`, `oat.min.js` — full minified bundles.
- `css/` — per-component source CSS files (`00-base.css`, `01-theme.css`, `button.css`, `form.css`, …, `utilities.css`).
- `js/` — per-component source JS modules (`base.js`, `index.js`, `toast.js`, `tabs.js`, …).

## Selective component bundling

Oat is small enough to bundle in full, but you can include only the components you use. **Must include:**

- `00-base.css` — reset, typography, and base styling of buttons and form controls.
- `01-theme.css` — all CSS variables plus the `data-variant` → color mappings.
- `base.js` — the `OtBase` lifecycle class, the `keyNav` helper, the `command`/`commandfor` polyfill (Safari), and the dialog touch shim.

After those, include the CSS and JS files of the components you actually use. For example, a page that only needs dialogs: `00-base.css`, `01-theme.css`, `dialog.css`, `base.js`.

## CSS layers

`00-base.css` declares the layer order: `@layer theme, base, components, animations, utilities;`

- `theme` — `:root` variables and the `data-variant` → `--_variant-color` mappings.
- `base` — reset, typography, buttons, form controls.
- `components` — component CSS (cards, tables, dialogs, toasts, sidebar, …).
- `animations` — keyframes and animation helpers.
- `utilities` — `.hstack`, `.vstack`, `.gap-*`, margins, `.unstyled`, alignment, …

Unlayered styles (typical hand-written CSS) beat every Oat layer, so theme overrides and ad-hoc fixes usually need no `!important`.

## Theming

Pretty much all Oat properties are defined as CSS variables. To override, redefine them in a CSS file in your project and **include it after** the library's CSS files. See `src/css/01-theme.css` in the repo for the full canonical variable list.

```css
:root {
  --primary: #3b5bdb;
  --primary-foreground: #fff;
  --ring: #3b5bdb;
  --radius-medium: 0.5rem;
  --font-sans: Inter, system-ui, sans-serif;
}
```

## Color variables

These control the colour profile:

| Variable | Role |
|---|---|
| `--background` / `--foreground` | Page background / primary text |
| `--card` / `--card-foreground` | Card (and dialog) background / text |
| `--primary` / `--primary-foreground` | Primary buttons and links / text on them |
| `--secondary` / `--secondary-foreground` | Secondary button background / text on them |
| `--muted` / `--muted-foreground` | Muted (lighter) background / text |
| `--faint` / `--faint-foreground` | Subtler than muted background / text |
| `--accent` | Hover background (outline/ghost buttons) |
| `--danger` / `--danger-foreground` | Error/danger colour / text on it |
| `--success` / `--success-foreground` | Success colour / text on it |
| `--warning` / `--warning-foreground` | Warning colour / text on it |
| `--border` | Border colour (boxes) |
| `--input` | Input borders |
| `--ring` | Focus ring colour |

The `data-variant` attribute maps onto these (shared by alert, badge, button, toast): `success` → `--success`, `warning` → `--warning`, `danger` **or `error`** → `--danger`; `secondary` uses `--secondary` directly.

## Design token variables

- **Spacing scale** — `--space-1` … `--space-18` (0.25rem → 4.5rem). The scale is not contiguous: `--space-1,2,3,4,5,6,8,10,12,14,16,18` exist (no `--space-7`, `--space-9`, …).
- **Radius** — `--radius-small` (0.125rem), `--radius-medium` (0.375rem), `--radius-large` (0.75rem), `--radius-full` (9999px).
- **Text scale** — `--text-1` … `--text-8`; `--text-1`–`--text-4` are fluid `clamp()` values, `--text-regular` = `--text-6` = 1rem.
- **Fonts** — `--font-sans` (system-ui), `--font-mono` (ui-monospace); weights `--font-normal` (400), `--font-medium` (500), `--font-semibold`/`--font-bold` (600).
- **Shadows** — `--shadow-small`, `--shadow-medium`, `--shadow-large`.
- **Transitions** — `--transition-fast` (120ms), `--transition` (200ms).
- **Bars** — `--bar-height` (0.5rem, progress/meter bar thickness).
- **Leading** — `--leading-normal` (1.5).
- **Z-index** — `--z-dropdown` (50), `--z-modal` (200).
- **Grid** — `--grid-cols` (12), `--grid-gap` (1.5rem), `--container-max` (1280px), `--container-pad` (1rem).
- **Sidebar** — `--sidebar-width`.

## Dark mode

Dark mode is applied automatically: colors use `light-dark(<light>, <dark>)` and `:root` sets `color-scheme: light dark`, following the OS system preference.

- To customize the dark theme, redefine the theme variables scoped inside a `[data-theme="dark"]` selector in your own CSS.
- To forcibly set a theme regardless of OS preference, `document.body.style.colorScheme = 'dark'` (or `'light'`).

## Library development setup

For developing Oat itself (docs/demo site):

1. Install [zola](https://github.com/getzola/zola/releases) (static site generator) and [esbuild](https://esbuild.github.io/).
2. Clone the repo, then `cd docs` and run `zola serve` — docs/demo site at http://localhost:1111.
3. After changing any CSS or JS file, run `make dist` (esbuild bundles + minifies, copies into `docs/static/`); the demo site auto-updates.

`make publish` builds, writes the git tag version into package.json, and publishes `@knadh/oat` to npm.

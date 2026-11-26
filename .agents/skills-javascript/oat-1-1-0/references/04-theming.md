# Oat Theming

Customizing Oat via CSS variables, dark mode behavior, selective file inclusion, and community extensions.

## Table of Contents

- [Theming with CSS variables](#theming-with-css-variables)
- [Key variables](#key-variables)
- [Dark mode](#dark-mode)
- [Picking and choosing files](#picking-and-choosing-files)
- [Community extensions](#community-extensions)

---

## Theming with CSS variables

Pretty much all Oat properties are CSS variables. To theme, redefine the variables in your own CSS file **included after** the library's CSS files (order matters — later rules win). See `src/css/01-theme.css` in the repo for the full variable list.

```css
:root {
  --primary: light-dark(#1d2b4f, #c7d3f0);
  --primary-foreground: light-dark(#fafafa, #18181b);
}
```

`data-variant` colors are centralized: `success`, `warning`, and `danger`/`error` each map to a `--_variant-color` consumed by alert, badge, toast, and other components.

## Key variables

From `01-theme.css` (values use `light-dark(light, dark)`):

- **Color surfaces**: `--background`, `--foreground`, `--card`, `--card-foreground`, `--muted`, `--muted-foreground`, `--faint`, `--faint-foreground`, `--accent`
- **Roles**: `--primary`/`--primary-foreground`, `--secondary`/`--secondary-foreground`, `--danger`/`--danger-foreground`, `--success`/`--success-foreground`, `--warning`/`--warning-foreground`, `--border`, `--input`, `--ring`
- **Spacing scale**: `--space-1` … `--space-18` (0.25rem, 0.5rem, 0.75rem, 1rem, 1.25rem, 1.5rem, 2rem, 2.5rem, 3rem, 3.5rem, 4rem, 4.5rem)
- **Radii**: `--radius-small`, `--radius-medium`, `--radius-large`, `--radius-full`
- **Typography**: `--font-sans`, `--font-mono`, `--text-1` … `--text-8` (fluid `clamp()` sizes for 1–4), `--text-regular`, `--leading-normal`, `--font-normal/medium/semibold/bold`
- **Shadows**: `--shadow-small`, `--shadow-medium`, `--shadow-large`
- **Motion**: `--transition-fast` (120ms), `--transition` (300ms)
- **Z-index**: `--z-dropdown` (50), `--z-modal` (200)
- **Misc**: `--bar-height`, `--sidebar-width` (sidebar layout)

## Dark mode

Dark mode is applied automatically via `light-dark()` and `color-scheme: light dark`, following the OS system preference — no opt-in.

- To customize the dark theme specifically, redefine theme variables scoped inside a `[data-theme="dark"]` selector in your own CSS.
- To force a theme regardless of the OS, set `document.body.style.colorScheme = 'dark'` or `'light'`.

## Picking and choosing files

Bundling all of Oat is fine given its size, but you can include components selectively. If you do, these are **must-include**:

- `00-base.css`
- `01-theme.css`
- `base.js`
- (then your component files after this)

Per-component files live in `src/css/` (e.g. `button.css`, `form.css`, `grid.css`, `utilities.css`) and `src/js/` (e.g. `dropdown.js`, `tabs.js`, `toast.js`).

## Community extensions

Third-party extensions that work with Oat (from the docs):

- **oat-chips** — chip/tag component with dismissible filters, colors, toggle selection (~1KB gzipped)
- **oat-animate** — lightweight animation extension with declarative `ot-animate` triggers (`on-load`, `hover`, `in-view`) and reduced-motion support
- **oat-table** — semantic table enhancement: sort, filter, select rows without turning tables into a framework widget
- **oat-upload** — dropzone, file previews, validation, removal, and progress for native `<input type="file">`

The docs site is at https://oat.ink; the library is MIT licensed.

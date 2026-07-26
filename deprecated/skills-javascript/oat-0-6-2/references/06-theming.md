# Theming

Oat uses CSS custom properties for complete theme customization. All variables are defined in `:root` and can be overridden.

## CSS Layers

Oat uses `@layer` for clean cascade management:

```css
@layer theme, base, components, animations, utilities;
```

- `theme` — CSS custom property definitions
- `base` — Reset, typography, element defaults
- `components` — Component-specific styles
- `animations` — Keyframes, transitions, `prefers-reduced-motion`
- `utilities` — Utility classes

Custom styles should use `@layer` or be placed after Oat's CSS.

## Color Tokens

### Backgrounds

| Variable | Purpose |
|---|---|
| `--background` | Page background |
| `--foreground` | Primary text color |
| `--card` | Card/surface background |
| `--card-foreground` | Text on cards |
| `--secondary` | Secondary surface |
| `--secondary-foreground` | Text on secondary |
| `--muted` | Muted/lighter surface |
| `--muted-foreground` | Muted text |
| `--faint` | Subtlest surface |
| `--faint-foreground` | Subtlest text |
| `--accent` | Accent hover surface |

### Semantic Colors

| Variable | Purpose |
|---|---|
| `--primary` | Primary buttons, links |
| `--primary-foreground` | Text on primary |
| `--danger` | Error/danger color |
| `--danger-foreground` | Text on danger |
| `--success` | Success color |
| `--success-foreground` | Text on success |
| `--warning` | Warning color |
| `--warning-foreground` | Text on warning |

### UI Colors

| Variable | Purpose |
|---|---|
| `--border` | Border color |
| `--input` | Input border color |
| `--ring` | Focus ring color |

## Spacing Scale

| Variable | Value |
|---|---|
| `--space-1` | 0.25rem |
| `--space-2` | 0.5rem |
| `--space-3` | 0.75rem |
| `--space-4` | 1rem |
| `--space-5` | 1.25rem |
| `--space-6` | 1.5rem |
| `--space-8` | 2rem |
| `--space-10` | 2.5rem |
| `--space-12` | 3rem |
| `--space-14` | 3.5rem |
| `--space-16` | 4rem |
| `--space-18` | 4.5rem |

## Border Radius

| Variable | Value |
|---|---|
| `--radius-small` | 0.125rem |
| `--radius-medium` | 0.375rem |
| `--radius-large` | 0.75rem |
| `--radius-full` | 9999px |

## Typography

| Variable | Value |
|---|---|
| `--font-sans` | `system-ui, sans-serif` |
| `--font-mono` | `ui-monospace, Consolas, monospace` |
| `--text-1` | `clamp(1.75rem, 1.5rem + 1.1vw, 2.25rem)` |
| `--text-2` | `clamp(1.5rem, 1.3rem + 0.8vw, 1.875rem)` |
| `--text-3` | `clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem)` |
| `--text-4` | `clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem)` |
| `--text-5` | 1.125rem |
| `--text-6` | 1rem |
| `--text-7` | 0.875rem |
| `--text-8` | 0.75rem |
| `--text-regular` | `var(--text-6)` |
| `--leading-normal` | 1.5 |
| `--font-normal` | 400 |
| `--font-medium` | 500 |
| `--font-semibold` | 600 |
| `--font-bold` | 600 |

## Shadows

| Variable | Value |
|---|---|
| `--shadow-small` | `0 1px 2px 0 rgb(0 0 0 / 0.05)` |
| `--shadow-medium` | `0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)` |
| `--shadow-large` | `0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` |

## Transitions

| Variable | Value |
|---|---|
| `--transition-fast` | `120ms cubic-bezier(0.4, 0, 0.2, 1)` |
| `--transition` | `200ms cubic-bezier(0.4, 0, 0.2, 1)` |

## Z-Index

| Variable | Value |
|---|---|
| `--z-dropdown` | 50 |
| `--z-modal` | 200 |

## Other

| Variable | Value |
|---|---|
| `--bar-height` | 0.5rem (progress/meter/range height) |

---

## Dark Mode

### Automatic (light-dark)

Oat uses `light-dark()` for automatic system preference detection:

```css
--background: light-dark(#fff, #09090b);
--foreground: light-dark(#09090b, #fafafa);
```

Supported in Chrome 123+, Edge 123+, Safari 18+.

### Manual (data-theme)

Add `data-theme="dark"` to `<body>` and scope dark variables:

```css
[data-theme="dark"] {
  --background: #09090b;
  --foreground: #fafafa;
  --card: #18181b;
  --primary: #fafafa;
  /* ... other overrides ... */
}
```

### color-scheme

`:root` sets `color-scheme: light dark` for native scrollbar and UI styling.

---

## Custom Theme Example

```css
:root {
  --primary: #3b82f6;
  --primary-foreground: #ffffff;
  --secondary: #e5e7eb;
  --secondary-foreground: #1f2937;
  --danger: #ef4444;
  --success: #22c55e;
  --warning: #f59e0b;
  --background: #ffffff;
  --foreground: #111827;
  --border: #d1d5db;
  --ring: #3b82f6;
  --radius-medium: 0.5rem;
  --font-sans: 'Inter', system-ui, sans-serif;
}
```

Override file must be loaded after `oat.min.css`.

---

## Selective Loading

For minimal bundles, include only needed files:

### Required
- `00-base.css` — Reset and base styles
- `01-theme.css` — CSS variables

### Optional (after required)
- Individual component CSS files from `css/`
- `base.js` — OtBase class and polyfills
- Individual component JS files from `js/`

Full bundle: `oat.min.css` + `oat.min.js`.

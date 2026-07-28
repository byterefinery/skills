---
title: Theme Variables
---

# Theme Variables

All visual properties are CSS custom properties defined in `01-theme.css`. Override them in your own stylesheet loaded after Oat's CSS.

## Color Tokens

### Base Colors

| Variable | Light | Dark | Purpose |
|---|---|---|---|
| `--background` | `#fff` | `#09090b` | Page background |
| `--foreground` | `#09090b` | `#fafafa` | Primary text |
| `--card` | `#fff` | `#18181b` | Card background |
| `--card-foreground` | `#09090b` | `#fafafa` | Card text |
| `--secondary` | `#f4f4f5` | `#27272a` | Secondary surfaces |
| `--secondary-foreground` | `#574747` | `#fafafa` | Text on secondary |
| `--muted` | `#f4f4f5` | `#27272a` | Muted background |
| `--muted-foreground` | `#71717a` | `#a1a1aa` | Muted text |
| `--faint` | `#fafafa` | `#1e1e21` | Subtle background |
| `--faint-foreground` | `#a1a1aa` | `#71717a` | Subtle text |
| `--accent` | `#f4f4f5` | `#27272a` | Hover/active surfaces |

### Semantic Colors

| Variable | Light | Dark | Purpose |
|---|---|---|---|
| `--primary` | `#574747` | `#fafafa` | Primary buttons, links |
| `--primary-foreground` | `#fafafa` | `#18181b` | Text on primary |
| `--danger` | `#d32f2f` | `#f4807b` | Error/danger states |
| `--danger-foreground` | `#fafafa` | `#18181b` | Text on danger |
| `--success` | `#008032` | `#6cc070` | Success states |
| `--success-foreground` | `#fafafa` | `#18181b` | Text on success |
| `--warning` | `#a65b00` | `#f0a030` | Warning states |
| `--warning-foreground` | `#09090b` | `#09090b` | Text on warning |

### Border and Focus

| Variable | Light | Dark | Purpose |
|---|---|---|---|
| `--border` | `#d4d4d8` | `#52525b` | Box borders |
| `--input` | `#d4d4d8` | `#52525b` | Input borders |
| `--ring` | `#574747` | `#d4d4d8` | Focus ring |

## Spacing Scale

| Variable | Value |
|---|---|
| `--space-1` | `0.25rem` |
| `--space-2` | `0.5rem` |
| `--space-3` | `0.75rem` |
| `--space-4` | `1rem` |
| `--space-5` | `1.25rem` |
| `--space-6` | `1.5rem` |
| `--space-8` | `2rem` |
| `--space-10` | `2.5rem` |
| `--space-12` | `3rem` |
| `--space-14` | `3.5rem` |
| `--space-16` | `4rem` |
| `--space-18` | `4.5rem` |

## Border Radius

| Variable | Value |
|---|---|
| `--radius-small` | `0.125rem` |
| `--radius-medium` | `0.375rem` |
| `--radius-large` | `0.75rem` |
| `--radius-full` | `9999px` |

## Typography

| Variable | Value |
|---|---|
| `--font-sans` | `system-ui, sans-serif` |
| `--font-mono` | `ui-monospace, Consolas, monospace` |
| `--text-1` (h1) | `clamp(1.75rem, 1.5rem + 1.1vw, 2.25rem)` |
| `--text-2` (h2) | `clamp(1.5rem, 1.3rem + 0.8vw, 1.875rem)` |
| `--text-3` (h3) | `clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem)` |
| `--text-4` (h4) | `clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem)` |
| `--text-5` (h5) | `1.125rem` |
| `--text-6` | `1rem` |
| `--text-7` | `0.875rem` |
| `--text-8` | `0.75rem` |
| `--text-regular` | `var(--text-6)` |
| `--leading-normal` | `1.5` |
| `--font-normal` | `400` |
| `--font-medium` | `500` |
| `--font-semibold` | `600` |
| `--font-bold` | `600` |

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
| `--z-dropdown` | `50` |
| `--z-modal` | `200` |

## Other

| Variable | Value |
|---|---|
| `--bar-height` | `0.5rem` |
| `--sidebar-width` | `15rem` |
| `--grid-cols` | `12` |
| `--grid-gap` | `1.5rem` |
| `--container-max` | `1280px` |
| `--container-pad` | `1rem` |

## Variant Color Map

The `[data-variant]` attribute maps to internal `--_variant-color`:

```css
[data-variant="success"] { --_variant-color: var(--success); }
[data-variant="warning"] { --_variant-color: var(--warning); }
:is([data-variant="danger"], [data-variant="error"]) { --_variant-color: var(--danger); }
```

Used by: alert, badge, toast.

## Dark Mode

Dark mode is automatic via `light-dark()` and `color-scheme: light dark`, following OS preference.

To customize dark mode manually, redefine variables scoped to `[data-theme="dark"]` and set `data-theme="dark"` on `<body>`:

```css
[data-theme="dark"] {
  --background: #000;
  --foreground: #fff;
  --primary: #3b82f6;
  /* ... other overrides ... */
}
```

## Custom Theme Example

```css
:root {
  --primary: #2563eb;
  --primary-foreground: #fff;
  --background: #f8fafc;
  --foreground: #0f172a;
  --card: #fff;
  --card-foreground: #0f172a;
  --secondary: #e2e8f0;
  --secondary-foreground: #1e293b;
  --muted: #f1f5f9;
  --muted-foreground: #64748b;
  --border: #cbd5e1;
  --input: #cbd5e1;
  --ring: #2563eb;
  --danger: #dc2626;
  --success: #16a34a;
  --warning: #d97706;
}
```

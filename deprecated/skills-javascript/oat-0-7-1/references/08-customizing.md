# Customizing

All properties are CSS variables that can be overridden. Include your overrides in a stylesheet loaded **after** Oat's CSS.

## Theme variables

```css
:root {
  /* Backgrounds */
  --background: light-dark(#fff, #09090b);
  --card: light-dark(#fff, #18181b);
  --secondary: light-dark(#f4f4f5, #27272a);
  --muted: light-dark(#f4f4f5, #27272a);
  --faint: light-dark(#fafafa, #1e1e21);
  --accent: light-dark(#f4f4f5, #27272a);

  /* Text colors */
  --foreground: light-dark(#09090b, #fafafa);
  --card-foreground: light-dark(#09090b, #fafafa);
  --primary-foreground: light-dark(#fafafa, #18181b);
  --secondary-foreground: light-dark(#574747, #fafafa);
  --muted-foreground: light-dark(#71717a, #a1a1aa);
  --faint-foreground: light-dark(#a1a1aa, #71717a);

  /* Semantic colors */
  --primary: light-dark(#574747, #fafafa);
  --danger: light-dark(#d32f2f, #f4807b);
  --danger-foreground: light-dark(#fafafa, #18181b);
  --success: light-dark(#008032, #6cc070);
  --success-foreground: light-dark(#fafafa, #18181b);
  --warning: light-dark(#a65b00, #f0a030);
  --warning-foreground: #09090b;

  /* Borders */
  --border: light-dark(#d4d4d8, #52525b);
  --input: light-dark(#d4d4d8, #52525b);
  --ring: light-dark(#574747, #d4d4d8);
}
```

## Changing primary color

```css
:root {
  --primary: #2563eb;
  --primary-foreground: #fff;
  --ring: #2563eb;
}
```

## Dark mode customization

Dark mode is automatic via `light-dark()`. To customize dark theme values:

```css
[data-theme="dark"] {
  --background: #111;
  --foreground: #eee;
  --primary: #3b82f6;
  /* ... other variables ... */
}
```

Then set `data-theme="dark"` on `<body>` to activate manually.

## Force dark mode

```css
:root {
  color-scheme: dark;
}
```

Or set individual variables without `light-dark()`:

```css
:root {
  --background: #09090b;
  --foreground: #fafafa;
  --card: #18181b;
  /* ... */
}
```

## Selective imports

Include only the components you need. Always include base files first:

```html
<!-- Must include -->
<link rel="stylesheet" href="css/00-base.css">
<link rel="stylesheet" href="css/01-theme.css">

<!-- Then pick components -->
<link rel="stylesheet" href="css/button.css">
<link rel="stylesheet" href="css/form.css">
<link rel="stylesheet" href="css/card.css">
<link rel="stylesheet" href="css/table.css">
```

### Available CSS files

| File | Components |
|---|---|
| `00-base.css` | Reset, typography, links, code, lists (mandatory) |
| `01-theme.css` | CSS variables, color scheme (mandatory) |
| `animations.css` | `prefers-reduced-motion`, dialog backdrop |
| `accordion.css` | `<details>` / `<summary>` |
| `alert.css` | `[role="alert"]` |
| `avatar.css` | `[data-variant="avatar"]` |
| `badge.css` | `.badge` |
| `button.css` | `<button>`, `menu.buttons` |
| `card.css` | `.card` |
| `dialog.css` | `<dialog>` |
| `dropdown.css` | `<ot-dropdown>` |
| `form.css` | inputs, selects, textareas, checkboxes, radios, switches, fieldsets |
| `grid.css` | `.container`, `.row`, `.col-*` |
| `progress.css` | `<progress>`, `<meter>` |
| `sidebar.css` | `[data-sidebar-layout]`, `[data-sidebar]`, `[data-topnav]` |
| `skeleton.css` | `.skeleton` |
| `spinner.css` | `[aria-busy]` |
| `tabs.css` | `[role="tablist"]`, `[role="tab"]`, `[role="tabpanel"]` |
| `taginput.css` | `<ot-taginput>` |
| `toast.css` | `.toast-container`, `.toast` |
| `tooltip.css` | `[data-tooltip]` |
| `table.css` | `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>` |
| `upload.css` | `<ot-upload>` |
| `utilities.css` | Flex, gap, margin, padding, text helpers |

### Available JS files

| File | Components |
|---|---|
| `base.js` | OtBase class (mandatory if using any JS component) |
| `dropdown.js` | `<ot-dropdown>` |
| `tabs.js` | `<ot-tabs>` |
| `taginput.js` | `<ot-taginput>` |
| `toast.js` | `window.ot.toast` |
| `tooltip.js` | title → data-tooltip converter |
| `upload.js` | `<ot-upload>` |
| `sidebar.js` | Sidebar toggle handler |

## CSS layers

Oat uses `@layer` cascade:

```css
@layer theme, base, components, animations, utilities;
```

Override order: `theme` < `base` < `components` < `animations` < `utilities` < author styles (no layer).

To override a component, either:
1. Redefine CSS variables (recommended)
2. Use `@layer components { ... }` or `@layer utilities { ... }`
3. Include your stylesheet after Oat's (no `@layer` — highest specificity)

## Variant system

`[data-variant]` maps to semantic colors shared across components:

```css
[data-variant="success"] { --_variant-color: var(--success); }
[data-variant="warning"] { --_variant-color: var(--warning); }
[data-variant="danger"], [data-variant="error"] { --_variant-color: var(--danger); }
```

Components that use variants: buttons, badges, alerts, toasts.

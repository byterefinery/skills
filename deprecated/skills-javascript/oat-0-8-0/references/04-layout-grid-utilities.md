# Oat Layout, Grid, and Utilities Reference

## Contents

- [Grid](#grid)
- [Sidebar layout](#sidebar-layout)
- [Utility classes](#utility-classes)

## Grid

A 12-column grid system using CSS grid. Use `.container`, `.row`, and `.col-{n}` (n = 1–12). Below 768px, rows collapse to 4 columns and everything stacks full-width (offsets reset to 0).

```html
<div class="container">
  <div class="row">
    <div class="col-4">col-4</div>
    <div class="col-4">col-4</div>
    <div class="col-4">col-4</div>
  </div>
  <div class="row">
    <div class="col-3">col-3</div>
    <div class="col-6">col-6</div>
    <div class="col-3">col-3</div>
  </div>
  <div class="row">
    <div class="col-4 offset-2">col-4 offset-2</div>
    <div class="col-4">col-4</div>
  </div>
  <div class="row">
    <div class="col-3">col-3</div>
    <div class="col-4 col-end">col-4 col-end</div>
  </div>
</div>
```

- `.col` (no number) spans all columns; `.col-1` … `.col-12` set the span.
- `.offset-1` … `.offset-6` push a column to the right.
- `.col-end` pins a column to the end of the row (useful after a flexible column).
- Tuning variables: `--grid-cols` (12), `--grid-gap` (1.5rem), `--container-max` (1280px), `--container-pad` (1rem).

Any element can be a column — including `article.card` for card grids.

## Sidebar layout

Responsive admin-dashboard layout: sticky sidebar, optional top nav, collapsible on mobile. Put `data-sidebar-layout` on a container (typically `<body>`), with `<aside data-sidebar>` for the sidebar and `<main>` for content. The sidebar stays sticky while the main content scrolls. On mobile (≤768px) it becomes a slide-out overlay toggled by a `[data-sidebar-toggle]` button.

```html
<body data-sidebar-layout>
  <nav data-topnav>
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
    <span>App Name</span>
  </nav>

  <aside data-sidebar>
    <header>Logo</header>
    <nav>
      <ul>
        <li><a href="#home" aria-current="page">Home</a></li>
        <li><a href="#users">Users</a></li>
        <li>
          <details open>
            <summary>Settings</summary>
            <ul>
              <li><a href="#general">General</a></li>
              <li><a href="#security">Security</a></li>
            </ul>
          </details>
        </li>
      </ul>
    </nav>
    <footer>
      <button class="outline small" style="width: 100%;">Logout</button>
    </footer>
  </aside>

  <main>
    <div style="padding: var(--space-3)">Main content area. Scrolls with the page body.</div>
  </main>
</body>
```

### Always-collapsible

Set `data-sidebar-layout="always"` to keep the toggle visible and functional on all screen sizes (the sidebar collapses at any width instead of only below 768px).

```html
<body data-sidebar-layout="always"> ... </body>
```

### Attributes

| Attribute | Element | Purpose |
|---|---|---|
| `data-sidebar-layout` | Container | Grid layout wrapper (sidebar + main), typically `<body>` |
| `data-sidebar-layout="always"` | Container | Always-collapsible sidebar |
| `data-topnav` | `<nav>` | Full-width top nav (optional; sidebar sits below it) |
| `data-sidebar` | `<aside>` | Sticky sidebar element |
| `data-sidebar-toggle` | `<button>` | Toggles sidebar (mobile) and collapse (always mode) |
| `data-sidebar-open` | Layout | Applied to the layout while the sidebar is open (managed by JS) |

The toggle handler in `sidebar.js` flips `data-sidebar-open` on the closest layout and dismisses the overlay on outside clicks below 768px (the breakpoint is hardcoded in JS — see SKILL.md gotchas). Set `--sidebar-width` to adjust the sidebar width globally.

## Utility classes

From `utilities.css` (utilities layer — lowest priority among Oat's own layers).

### Alignment and text

- `.align-left`, `.align-center`, `.align-right` — text alignment
- `.text-light` — muted text colour (`--muted-foreground`)
- `.text-lighter` — faint text colour (`--faint-foreground`)

### Flexbox

- `.flex` — `display: flex`
- `.flex-col` — `flex-direction: column`
- `.items-center` — `align-items: center`
- `.justify-center`, `.justify-between`, `.justify-end`
- `.hstack` — flex row, `align-items: center`, gap `--space-3`, wraps, zeroes child margins
- `.vstack` — flex column, gap `--space-3`

### Spacing

- `.gap-1`, `.gap-2`, `.gap-4`, `.gap-6` — `gap` from the `--space` scale (note there is no `.gap-3`)
- `.mt-2`, `.mt-4`, `.mt-6`, `.mt-8` — `margin-block-start`
- `.mb-2`, `.mb-4`, `.mb-6`, `.mb-8` — `margin-block-end`
- `.p-4` — padding `--space-4`

### Size and unstyled

- `.w-100` — `width: 100%`
- `ul.unstyled` / `ol.unstyled` — no list style, no padding
- `a.unstyled` — inherits color, no underline (primary colour on hover)

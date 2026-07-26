---
title: Layout
---

# Layout

## Grid System

A 12-column responsive grid using CSS Grid. Stacks to 4 columns on mobile (max-width: 768px).

### Container

```html
<div class="container">
  <!-- max-width: 1280px, centered, horizontal padding -->
</div>
```

Configurable via `--container-max` and `--container-pad`.

### Row

```html
<div class="row">
  <!-- CSS grid with 12 columns, gap: 1.5rem -->
</div>
```

Configurable via `--grid-cols` and `--grid-gap`.

### Columns

```html
<div class="row">
  <div class="col-4">Spans 4 columns</div>
  <div class="col-4">Spans 4 columns</div>
  <div class="col-4">Spans 4 columns</div>
</div>

<div class="row">
  <div class="col-6">Half width</div>
  <div class="col-6">Half width</div>
</div>

<div class="row">
  <div class="col-3">Quarter</div>
  <div class="col-6">Half</div>
  <div class="col-3">Quarter</div>
</div>
```

Column classes: `.col-1` through `.col-12`, or plain `.col` (spans all 12).

### Offsets

```html
<div class="row">
  <div class="col-4 offset-2">Shifted right by 2</div>
  <div class="col-4">Normal</div>
</div>
```

Offset classes: `.offset-1` through `.offset-6`. Offsets are ignored on mobile.

### Col-End

Stretch a column to the end of the row:

```html
<div class="row">
  <div class="col-3">Fixed width</div>
  <div class="col-4 col-end">Stretches to fill remaining space</div>
</div>
```

### Mobile Behavior

At `max-width: 768px`:
- Grid switches to 4 columns
- All `.col-*` classes span all 4 columns (full width)
- Offsets are ignored

## Sidebar Layout

A responsive admin dashboard layout with sticky sidebar and scrollable main content.

### Basic Sidebar

```html
<div data-sidebar-layout>
  <aside data-sidebar>
    <nav>
      <ul>
        <li><a href="#" aria-current="page">Home</a></li>
        <li><a href="#">Users</a></li>
        <li><a href="#">Settings</a></li>
      </ul>
    </nav>
    <footer>
      <button class="outline small">Logout</button>
    </footer>
  </aside>
  <main>
    <div class="container">
      <h1>Dashboard</h1>
      <p>Main content area. Scrolls with the page.</p>
    </div>
  </main>
</div>
```

### With Top Navigation

```html
<div data-sidebar-layout>
  <nav data-topnav>
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
    <span>App Name</span>
  </nav>

  <aside data-sidebar>
    <header>Logo</header>
    <nav>
      <ul>
        <li><a href="#" aria-current="page">Home</a></li>
        <li><a href="#">Users</a></li>
      </ul>
    </nav>
    <footer>Actions</footer>
  </aside>

  <main>
    <h1>Page Title</h1>
    <p>Content here.</p>
  </main>
</div>
```

### Always-Collapsible

Set `data-sidebar-layout="always"` to keep the toggle visible on all screen sizes:

```html
<body data-sidebar-layout="always">
  <!-- Sidebar collapses on desktop too when toggle is clicked -->
</body>
```

### Sidebar Structure

| Attribute | Element | Purpose |
|---|---|---|
| `data-sidebar-layout` | Container | Grid layout wrapper, typically `<body>` |
| `data-sidebar-layout="always"` | Container | Always-collapsible sidebar |
| `data-topnav` | `<nav>` | Full-width top navigation bar |
| `data-sidebar` | `<aside>` | Sticky sidebar element |
| `data-sidebar-toggle` | `<button>` | Toggle sidebar visibility |
| `data-sidebar-open` | Layout | Applied when sidebar is open (mobile) |

### Sidebar Navigation

The sidebar `<nav>` supports nested `<details>`/`<summary>` for collapsible sections:

```html
<aside data-sidebar>
  <nav>
    <ul>
      <li><a href="#" aria-current="page">Home</a></li>
      <li>
        <details open>
          <summary>Settings</summary>
          <ul>
            <li><a href="#">General</a></li>
            <li><a href="#">Security</a></li>
            <li><a href="#">Billing</a></li>
          </ul>
        </details>
      </li>
    </ul>
  </nav>
</aside>
```

### Sidebar Configuration

| Variable | Default | Purpose |
|---|---|---|
| `--sidebar-width` | `15rem` | Sidebar width |

Override:
```css
:root {
  --sidebar-width: 18rem;
}
```

### Sidebar Behavior

- **Desktop**: Sidebar is sticky, main content scrolls
- **Mobile (≤768px)**: Sidebar becomes a slide-out overlay, toggled by `[data-sidebar-toggle]`
- **Click outside sidebar on mobile**: Closes the sidebar
- **`always` mode**: Toggle visible on all sizes, collapses sidebar on desktop

## Responsive Breakpoints

| Breakpoint | Behavior |
|---|---|
| `> 768px` | Full grid (12 cols), sidebar visible |
| `≤ 768px` | Stacked grid (4 cols), sidebar hidden (slide-out) |

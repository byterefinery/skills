# Layout

Oat provides a grid system and sidebar layout pattern.

## Grid System

12-column CSS grid with responsive stacking.

### Variables

| Variable | Default | Description |
|---|---|---|
| `--grid-cols` | `12` | Number of columns |
| `--grid-gap` | `1.5rem` | Gap between columns |
| `--container-max` | `1280px` | Max width of container |
| `--container-pad` | `1rem` | Horizontal padding of container |

### Container

```html
<div class="container">
  <!-- Max-width centered content -->
</div>
```

### Row

```html
<div class="row">
  <!-- Grid children -->
</div>
```

### Column Classes

| Class | Span |
|---|---|
| `.col` | Full (all 12) |
| `.col-1` through `.col-12` | 1–12 columns |
| `.col-end` | Spans to last column |

### Offset Classes

| Class | Offset |
|---|---|
| `.offset-1` through `.offset-6` | 1–6 columns |

### Examples

```html
<div class="container">
  <div class="row">
    <div class="col-4">A</div>
    <div class="col-4">B</div>
    <div class="col-4">C</div>
  </div>

  <div class="row">
    <div class="col-6">A</div>
    <div class="col-6">B</div>
  </div>

  <div class="row">
    <div class="col-3">A</div>
    <div class="col-6">B</div>
    <div class="col-3">C</div>
  </div>

  <div class="row">
    <div class="col-4 offset-2">A</div>
    <div class="col-4">B</div>
  </div>

  <div class="row">
    <div class="col-3">A</div>
    <div class="col-4 col-end">B</div>
  </div>
</div>
```

### Responsive Behavior

At ≤768px:
- Grid reduces to 4 columns
- All `.col-*` classes span full width (4/4)
- Offsets are reset to 0
- Gap reduces to 1rem

---

## Sidebar Layout

Responsive admin dashboard layout with CSS grid.

### Structure

```html
<body data-sidebar-layout>
  <!-- Top nav (optional) -->
  <nav data-topnav>
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
    <span>App Name</span>
  </nav>

  <!-- Sidebar -->
  <aside data-sidebar>
    <header>Logo</header>
    <nav>
      <ul>
        <li><a href="#" aria-current="page">Home</a></li>
        <li><a href="#">Dashboard</a></li>
        <li>
          <details open>
            <summary>Settings</summary>
            <ul>
              <li><a href="#">General</a></li>
              <li><a href="#">Security</a></li>
            </ul>
          </details>
        </li>
      </ul>
    </nav>
    <footer>
      <button class="outline">Logout</button>
    </footer>
  </aside>

  <!-- Main content -->
  <main>
    <div style="padding: var(--space-3)">Page content</div>
  </main>
</body>
```

### Attributes

| Attribute | Element | Purpose |
|---|---|---|
| `data-sidebar-layout` | Container | Enables grid layout (sidebar + main) |
| `data-sidebar-layout="always"` | Container | Always-collapsible sidebar |
| `data-topnav` | `<nav>` | Full-width sticky top navigation |
| `data-sidebar` | `<aside>` | Sidebar panel |
| `data-sidebar-toggle` | `<button>` | Toggle button for sidebar |
| `data-sidebar-open` | Layout | Applied when sidebar is open (mobile) |

### Variables

| Variable | Default | Description |
|---|---|---|
| `--sidebar-width` | `15rem` | Sidebar width |

### Desktop Behavior (≥769px)

- Sidebar visible, fixed width
- Main content scrolls independently
- `data-sidebar-layout="always"`: toggle button visible, clicking collapses sidebar

### Mobile Behavior (≤768px)

- Sidebar hidden off-screen (translateX -100%)
- Toggle button visible
- Clicking toggle slides sidebar in as overlay
- Clicking outside sidebar dismisses it
- `data-sidebar-header` shown (flex row with toggle + title)

### Sidebar Navigation Styling

Inside `<aside data-sidebar> <nav>`:

- `<ul>` — vertical flex column, no padding
- `<a>` — flex row with gap, hover highlight, `aria-current` highlight
- `<details>` — borderless accordion sections
- `<summary>` — left-aligned chevron, smaller icon

### Grid Template

```css
[data-sidebar-layout] {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  grid-template-rows: auto 1fr;
  height: 100dvh;
}
```

- `nav[data-topnav]` — grid-column: 1 / -1 (full width)
- `aside[data-sidebar]` — grid-row: 2
- `main` — grid-row: 2, overflow-y: auto

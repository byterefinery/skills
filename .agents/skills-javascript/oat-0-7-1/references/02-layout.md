# Layout — Grid, Sidebar, Topnav

## 12-Column Grid

Uses CSS grid with `.container`, `.row`, and `.col-*` classes.

```html
<div class="container">
  <div class="row">
    <div class="col-4">Quarter</div>
    <div class="col-4">Quarter</div>
    <div class="col-4">Quarter</div>
  </div>
  <div class="row">
    <div class="col-6">Half</div>
    <div class="col-6">Half</div>
  </div>
</div>
```

### Column classes

- `.col` — spans full row (all 12 columns)
- `.col-1` through `.col-12` — span that many columns
- `.col-end` — stretches from start position to the end of the row

### Offsets

- `.offset-1` through `.offset-6` — add left margin to push columns right

```html
<div class="row">
  <div class="col-4 offset-2">Shifted right by 2</div>
  <div class="col-4">Normal</div>
</div>
```

### Responsive behavior

At `max-width: 768px`:
- Grid collapses to 4 columns
- All `.col-*` classes span full width (4 columns)
- Offsets are ignored

### Configurable variables

```css
:root {
  --grid-cols: 12;
  --grid-gap: 1.5rem;
  --container-max: 1280px;
  --container-pad: 1rem;
}
```

## Sidebar Layout

Admin-style layout with sticky sidebar and scrollable main content.

### Basic structure

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
      <button class="outline small" style="width: 100%;">Logout</button>
    </footer>
  </aside>
  <main>
    <div style="padding: var(--space-3)">Main content scrolls here.</div>
  </main>
</div>
```

### With top navigation

```html
<body data-sidebar-layout>
  <nav data-topnav>
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
    <span>App Name</span>
  </nav>

  <aside data-sidebar>
    <header>Logo</header>
    <nav>...navigation...</nav>
    <footer>Actions</footer>
  </aside>

  <main>Main page content.</main>
</body>
```

### Always-collapsible mode

Set `data-sidebar-layout="always"` to keep the toggle visible and functional on all screen sizes:

```html
<body data-sidebar-layout="always">
  ...
</body>
```

### Sidebar attributes

| Attribute | Element | Purpose |
|---|---|---|
| `data-sidebar-layout` | Container | Grid layout wrapper (sidebar + main), typically `<body>` |
| `data-sidebar-layout="always"` | Container | Always-collapsible sidebar |
| `data-topnav` | `<nav>` | Full-width top nav bar |
| `data-sidebar` | `<aside>` | Sticky sidebar element |
| `data-sidebar-toggle` | `<button>` | Toggle button for sidebar |
| `data-sidebar-open` | Layout | Applied when sidebar is open (mobile) |

### Collapsible sections in sidebar

Use native `<details>`/`<summary>` inside the sidebar nav:

```html
<aside data-sidebar>
  <nav>
    <ul>
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
</aside>
```

### Sidebar width

Override the CSS variable:

```css
:root {
  --sidebar-width: 18rem;
}
```

### Mobile behavior

- Below 768px: sidebar becomes a slide-out overlay
- Toggled by `[data-sidebar-toggle]` button
- Clicking outside sidebar dismisses it on mobile
- `data-sidebar-open` attribute is applied to the layout when open

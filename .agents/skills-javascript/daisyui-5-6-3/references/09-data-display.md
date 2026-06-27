# 09 — Data Display

## table

Data table with zebra striping and pinned rows/columns.

**Class names:**
- component: `table`
- modifier: `table-zebra`, `table-pin-rows`, `table-pin-cols`
- size: `table-xs`, `table-sm`, `table-md`, `table-lg`, `table-xl`

```html
<div class="overflow-x-auto">
  <table class="table {MODIFIER}">
    <thead>
      <tr><th>Name</th><th>Role</th></tr>
    </thead>
    <tbody>
      <tr><td>Alice</td><td>Admin</td></tr>
    </tbody>
  </table>
</div>
```

Wrap in `overflow-x-auto` for horizontal scrolling on small screens.

## stats

Displays numbers and data in blocks.

**Class names:**
- component: `stats`
- part: `stat`, `stat-title`, `stat-value`, `stat-desc`, `stat-figure`, `stat-actions`
- direction: `stats-horizontal`, `stats-vertical`

```html
<div class="stats {MODIFIER}">
  <div class="stat">
    <div class="stat-figure"><img src="{url}" /></div>
    <div class="stat-title">Total Users</div>
    <div class="stat-value">1,234</div>
    <div class="stat-desc">↑ 23% from last month</div>
  </div>
</div>
```

Horizontal by default. Use `stats-vertical` for vertical layout.

## list

Vertical row-based information display.

**Class names:**
- component: `list`, `list-row`
- modifier: `list-col-wrap`, `list-col-grow`

```html
<ul class="list">
  <li class="list-row">
    <span>Label</span>
    <span>Content fills remaining space</span>
  </li>
</ul>
```

By default the second child fills remaining space. Use `list-col-grow` on another child to change this. Use `list-col-wrap` to force wrapping.

## timeline

Chronological event display.

**Class names:**
- component: `timeline`
- part: `timeline-start`, `timeline-middle`, `timeline-end`
- modifier: `timeline-snap-icon`, `timeline-box`, `timeline-compact`
- direction: `timeline-vertical`, `timeline-horizontal`

```html
<ul class="timeline {MODIFIER}">
  <li>
    <div class="timeline-start">{date}</div>
    <div class="timeline-middle">●</div>
    <div class="timeline-end">{event}</div>
  </li>
</ul>
```

Vertical by default. Use `timeline-compact` to force all items on one side. Use `timeline-snap-icon` to snap icons to the start.

## steps

Process step indicator.

**Class names:**
- component: `steps`
- part: `step`, `step-icon`
- color: `step-primary`, `step-secondary`, `step-accent`, `step-neutral`, `step-info`, `step-success`, `step-warning`, `step-error`
- direction: `steps-vertical`, `steps-horizontal`

```html
<ul class="steps {MODIFIER}">
  <li class="step step-primary">Step 1</li>
  <li class="step">
    <span class="step-icon">✓</span>
    Step 2
  </li>
  <li class="step">Step 3</li>
</ul>
```

Horizontal by default. Add `step-primary` to mark the active step. Use `data-content="{value}"` on `<li>` to display custom content in the step indicator.

## badge

Status indicator for data.

**Class names:**
- component: `badge`
- style: `badge-outline`, `badge-dash`, `badge-soft`, `badge-ghost`
- color: `badge-primary`, `badge-secondary`, `badge-accent`, `badge-neutral`, `badge-info`, `badge-success`, `badge-warning`, `badge-error`
- size: `badge-xs`, `badge-sm`, `badge-md`, `badge-lg`, `badge-xl`

```html
<span class="badge {MODIFIER}">Label</span>
```

Can be used inside text or buttons. Remove inner text for an empty badge.

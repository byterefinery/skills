# Oat Layout & Utilities

Layout helpers from `utilities.css` and the 12-column grid from `grid.css`.

## Table of Contents

- [12-column grid](#12-column-grid)
- [Stacks & flex](#stacks--flex)
- [Spacing](#spacing)
- [Alignment & text](#alignment--text)
- [Reset helpers](#reset-helpers)

---

## 12-column grid

A 12-column grid using CSS grid. Structure is `.container` > `.row` > `.col-{n}` where n is 1–12. `.offset-{n}` (n = 1–6) pushes a column right; `.col-end` right-aligns a column in its row.

```html
<div class="container">
  <div class="row">
    <div class="col-4">col-4</div>
    <div class="col-4">col-4</div>
    <div class="col-4">col-4</div>
  </div>
  <div class="row">
    <div class="col-6">col-6</div>
    <div class="col-6">col-6</div>
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

Columns can nest any component — e.g. `col-4` cards for dashboard stat rows:

```html
<div class="container">
  <div class="row">
    <article class="card col-4">
      <header class="hstack justify-between items-center">
        <h4>Revenue</h4>
        <span class="badge" data-variant="success">+12%</span>
      </header>
      <h2>$42,200</h2>
      <progress value="72" max="100"></progress>
    </article>
    <!-- more col-4 cards -->
  </div>
</div>
```

## Stacks & flex

- `.hstack` — horizontal flex, `align-items: center`, `gap: var(--space-3)`, wraps; zeroes child margins
- `.vstack` — vertical flex, `gap: var(--space-3)`
- `.flex` — `display: flex`
- `.flex-col` — `flex-direction: column`
- `.items-center` — `align-items: center`
- `.justify-center` / `.justify-between` / `.justify-end` — `justify-content`

Common combos seen in the docs: `class="hstack justify-between items-center"`, `class="hstack justify-end mt-4"`, `class="vstack mt-4"`.

## Spacing

Values map to the `--space-*` scale (e.g. `--space-4` = 1rem).

- **Gap**: `.gap-1`, `.gap-2`, `.gap-4`, `.gap-6`
- **Margin top**: `.mt-2`, `.mt-4`, `.mt-6`, `.mt-8` (`margin-block-start`)
- **Margin bottom**: `.mb-2`, `.mb-4`, `.mb-6`, `.mb-8` (`margin-block-end`)
- **Padding**: `.p-4`

For other values, use the variables inline: `style="gap: var(--space-8)"`.

## Alignment & text

- `.align-left` / `.align-center` / `.align-right` — text alignment (start/center/end)
- `.text-light` — muted foreground color
- `.text-lighter` — faint foreground color
- `.w-100` — `width: 100%`

## Reset helpers

- `:is(ul, ol).unstyled` — removes list bullets and padding
- `a.unstyled` — inherits color, no underline (primary color on hover)

## Table wrapper

`.table` on a wrapping `<div>` gives the inner table a horizontal scrollbar on small screens (see the Table section of the CSS components reference).

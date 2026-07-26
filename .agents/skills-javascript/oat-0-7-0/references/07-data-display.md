---
title: Data Display
---

# Data Display

## Table

Tables are styled automatically. Wrap in `.table` for horizontal scroll on small screens.

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Alice</td>
        <td>alice@example.com</td>
        <td>Admin</td>
      </tr>
      <tr>
        <td>Bob</td>
        <td>bob@example.com</td>
        <td>User</td>
      </tr>
    </tbody>
    <tfoot>
      <tr>
        <td colspan="3">2 users</td>
      </tr>
    </tfoot>
  </table>
</div>
```

- `thead`: bottom border
- `tfoot`: top border
- `tbody tr`: bottom border, hover background
- `th`: medium weight, muted color
- `td`, `th`: `overflow-wrap: break-word`
- `.table` wrapper: `min-width: 320px`, `overflow-x: auto`

## Card

```html
<div class="card">
  <h3>Card Title</h3>
  <p>Card content with border, shadow, and padding.</p>
</div>
```

- Background: `var(--card)`, text: `var(--card-foreground)`
- Border: `1px solid var(--border)`
- Border radius: `var(--radius-medium)`
- Shadow: `var(--shadow-small)`
- Padding: `var(--space-6)`

## Badge

```html
<span class="badge">Default</span>
<span class="badge outline">Outline</span>
<span class="badge" data-variant="secondary">Secondary</span>
<span class="badge" data-variant="success">Success</span>
<span class="badge" data-variant="warning">Warning</span>
<span class="badge" data-variant="danger">Danger</span>
```

- Pill-shaped (`border-radius: var(--radius-full)`)
- Font: `var(--text-8)` (0.75rem), medium weight
- Variant colors use `--_variant-color` with light-dark transparency

### Badge with Remove Button

A nested `<button>` inside a badge acts as a removable '×' (revealed on hover):

```html
<span class="badge">
  Tag name
  <button aria-label="Remove">×</button>
</span>
```

## Skeleton

Loading placeholders with shimmer animation. Requires `role="status"` and class `skeleton`:

```html
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton box"></div>
```

- `.line`: full width, 1rem height
- `.box`: 4rem × 4rem square
- Animation: infinite shimmer gradient sweep

## Spinner

Add `aria-busy="true"` to any element for a CSS-only spinner:

```html
<div aria-busy="true"></div>
<div aria-busy="true" data-spinner="small"></div>
<div aria-busy="true" data-spinner="large"></div>
<div aria-busy="true" data-spinner="overlay">
  <p>Content that dims while busy</p>
</div>
```

- Default: 1.5rem spinning circle
- `small`: 1rem
- `large`: 2rem, 3px border
- `overlay`: positions spinner over content, dims children, disables pointer events

## Progress Bar

```html
<progress value="70" max="100"></progress>
```

Native `<progress>` styled with rounded bar, `--primary` fill color, `--muted` track.

## Meter

```html
<meter value="0.7"></meter>
<meter value="0.4" min="0" max="1" low="0.3" high="0.7" optimum="0.8"></meter>
```

Native `<meter>` with color-coded values:
- Optimum: `--success` (green)
- Sub-optimum: `--warning` (amber)
- Even less good: `--danger` (red)

Both progress and meter use `--bar-height` (0.5rem) and `--radius-full`.

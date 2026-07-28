---
title: Utilities
---

# Utilities

Utility classes for common layout and styling needs.

## Flexbox

```html
<div class="flex">           <!-- display: flex -->
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<div class="flex flex-col">  <!-- column direction -->
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

| Class | Property |
|---|---|
| `.flex` | `display: flex` |
| `.flex-col` | `flex-direction: column` |
| `.items-center` | `align-items: center` |
| `.justify-center` | `justify-content: center` |
| `.justify-between` | `justify-content: space-between` |
| `.justify-end` | `justify-content: flex-end` |

## Stack Helpers

```html
<div class="hstack">
  <span>Inline items with gap</span>
  <span>Wrapped as needed</span>
</div>

<div class="vstack">
  <div>Stacked vertically</div>
  <div>With consistent gap</div>
</div>
```

| Class | Behavior |
|---|---|
| `.hstack` | Horizontal flex, `gap: var(--space-3)`, wrap, `align-content: flex-start` |
| `.vstack` | Vertical flex, `gap: var(--space-3)` |

## Gap

```html
<div class="flex gap-1">Tight gap items</div>
<div class="flex gap-2">Small gap items</div>
<div class="flex gap-4">Normal gap items</div>
<div class="flex gap-6">Large gap items</div>
```

| Class | Gap |
|---|---|
| `.gap-1` | `var(--space-1)` (0.25rem) |
| `.gap-2` | `var(--space-2)` (0.5rem) |
| `.gap-4` | `var(--space-4)` (1rem) |
| `.gap-6` | `var(--space-6)` (1.5rem) |

## Text Alignment

```html
<p class="align-left">Left aligned</p>
<p class="align-center">Center aligned</p>
<p class="align-right">Right aligned</p>
```

| Class | Property |
|---|---|
| `.align-left` | `text-align: start` |
| `.align-center` | `text-align: center` |
| `.align-right` | `text-align: end` |

## Text Color

```html
<p class="text-light">Muted text</p>
<p class="text-lighter">Subtle text</p>
```

| Class | Color |
|---|---|
| `.text-light` | `var(--muted-foreground)` |
| `.text-lighter` | `var(--faint-foreground)` |

## Margins

```html
<div class="mt-2">Top margin 0.5rem</div>
<div class="mt-4">Top margin 1rem</div>
<div class="mt-6">Top margin 1.5rem</div>
<div class="mt-8">Top margin 2rem</div>

<div class="mb-2">Bottom margin 0.5rem</div>
<div class="mb-4">Bottom margin 1rem</div>
<div class="mb-6">Bottom margin 1.5rem</div>
<div class="mb-8">Bottom margin 2rem</div>
```

| Class | Property |
|---|---|
| `.mt-2` | `margin-block-start: var(--space-2)` |
| `.mt-4` | `margin-block-start: var(--space-4)` |
| `.mt-6` | `margin-block-start: var(--space-6)` |
| `.mt-8` | `margin-block-start: var(--space-8)` |
| `.mb-2` | `margin-block-end: var(--space-2)` |
| `.mb-4` | `margin-block-end: var(--space-4)` |
| `.mb-6` | `margin-block-end: var(--space-6)` |
| `.mb-8` | `margin-block-end: var(--space-8)` |

## Padding

```html
<div class="p-4">Padding 1rem on all sides</div>
```

| Class | Property |
|---|---|
| `.p-4` | `padding: var(--space-4)` |

## Width

```html
<div class="w-100">Full width</div>
```

| Class | Property |
|---|---|
| `.w-100` | `width: 100%` |

## Unstyled

Remove default list and link styling:

```html
<ul class="unstyled">
  <li>No bullets, no padding</li>
  <li>Flat list items</li>
</ul>

<a href="#" class="unstyled">No underline, inherits color</a>
```

| Class | Effect |
|---|---|
| `ul.unstyled`, `ol.unstyled` | `list-style: none`, `padding: 0` |
| `a.unstyled` | `color: inherit`, `text-decoration: none`, hover reverts to `--primary` |

## Reduced Motion

Oat automatically respects `prefers-reduced-motion: reduce`:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

All animations and transitions are effectively disabled when the user prefers reduced motion.

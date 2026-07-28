---
title: Buttons
---

# Buttons

Buttons are styled automatically. `<button>`, `[type=submit]`, `[type=reset]`, `[type=button]`, and `a.button` all receive the same styling. `::file-selector-button` is also styled.

## Variants

```html
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger">Danger</button>
```

## Visual Styles

```html
<button class="outline">Outline</button>
<button class="ghost">Ghost</button>
<button data-variant="danger" class="outline">Danger Outline</button>
<button data-variant="secondary" class="ghost">Secondary Ghost</button>
```

Combine `data-variant` with `class="outline"` or `class="ghost"`:

| Variant | Outline | Ghost |
|---|---|---|
| Default (primary) | Primary border | No border |
| `secondary` | Secondary border | No border |
| `danger` | Danger border | No border |

## Sizes

```html
<button class="small">Small</button>
<button>Default</button>
<button class="large">Large</button>
```

## Icon Button

Square button with no padding, sized by icon:

```html
<button class="icon" aria-label="Settings">⚙</button>
<button class="icon small" aria-label="Close">✕</button>
<button class="icon large" aria-label="Menu">☰</button>
```

## Hyperlink as Button

```html
<a href="#" class="button">Link styled as button</a>
```

## Disabled State

```html
<button disabled>Disabled</button>
<button data-variant="danger" disabled>Disabled Danger</button>
<button class="outline" disabled>Disabled Outline</button>
```

## Button Groups

Connected buttons using `<menu class="buttons">`:

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

Each `<li>` must contain exactly one button or `a.button`. The first button gets left border radius, the last gets right border radius, middle buttons have no border radius.

## File Selector Button

The native `::file-selector-button` pseudo-element is styled to match the theme:

```html
<input type="file">
<!-- The "Choose File" button part is styled automatically -->
```

## Button Anatomy

```
┌─────────────────────────┐
│  gap: var(--space-2)    │  ← items spaced with gap
│  padding: 2 4           │  ← vertical space-2, horizontal space-4
│  font-size: text-7      │  ← 0.875rem
│  font-weight: medium    │  ← 500
│  border-radius: medium  │  ← 0.375rem
│  inline-flex            │  ← flexbox, centered
└─────────────────────────┘
```

## Hover and Active

- **Hover**: Background color lightens (primary) or darkens (secondary)
- **Active**: `transform: translate(1px, 1px)` for pressed feel
- **Focus-visible**: `2px solid var(--ring)` outline with `2px` offset

## Complete Example

```html
<form>
  <button type="submit">Save</button>
  <button type="button" class="outline">Cancel</button>
</form>

<menu class="buttons">
  <li><button class="outline small">Cut</button></li>
  <li><button class="outline small">Copy</button></li>
  <li><button class="outline small">Paste</button></li>
</menu>

<button class="icon" aria-label="Delete">🗑</button>
<button data-variant="danger" class="ghost small">Remove</button>
```

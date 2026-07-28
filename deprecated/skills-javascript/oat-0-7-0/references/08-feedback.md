---
title: Feedback
---

# Feedback

## Alert

```html
<div role="alert">
  Informational alert with default border styling.
</div>

<div role="alert" data-variant="success">
  Operation completed successfully.
</div>

<div role="alert" data-variant="warning">
  Please review this warning.
</div>

<div role="alert" data-variant="danger">
  An error occurred.
</div>

<div role="alert" data-variant="error">
  Same as danger — both map to the danger color.
</div>
```

- Default: bordered box with `--border`
- With `data-variant`: no border, colored text and tinted background
- Variants: `success`, `warning`, `danger`, `error`
- Links inside variant alerts inherit the variant color

## Toast

Toast notifications via the global `ot.toast()` API. Auto-dismisses after 4000ms, pauses on hover.

### Basic Toast

```js
ot.toast('Action completed successfully');
```

### Toast with Title

```js
ot.toast('Action completed successfully', 'All good');
```

### Toast with Options

```js
ot.toast('Operation completed.', 'Success', { variant: 'success' });
ot.toast('Something went wrong.', 'Error', { variant: 'danger', placement: 'bottom-center' });
ot.toast('Please review.', 'Warning', { variant: 'warning', placement: 'top-left' });
```

### Options

| Option | Default | Values |
|---|---|---|
| `variant` | `'info'` | `'success'`, `'danger'`, `'warning'` |
| `placement` | `'top-right'` | `'top-left'`, `'top-center'`, `'top-right'`, `'bottom-left'`, `'bottom-center'`, `'bottom-right'` |
| `duration` | `4000` | Milliseconds. `0` = persistent (no auto-dismiss) |

### Custom Markup Toast

```js
// From a template element
ot.toast.el(document.querySelector('#my-template'));
ot.toast.el(document.querySelector('#my-template'), { duration: 8000, placement: 'bottom-center' });

// From a dynamic element
const el = document.createElement('output');
el.className = 'toast';
el.setAttribute('data-variant', 'warning');
el.innerHTML = '<h6 class="toast-title">Warning</h6><p>Custom content</p>';
ot.toast.el(el);
```

The element is cloned before display, so templates can be reused.

### Template Example

```html
<template id="undo-toast">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Changes saved</h6>
    <p>Your document has been updated.</p>
    <button data-variant="secondary" class="small" onclick="this.closest('.toast').remove()">Okay</button>
  </output>
</template>

<button onclick="ot.toast.el(document.querySelector('#undo-toast'), { duration: 8000 })">
  Show Undo Toast
</button>
```

### Clear Toaster

```js
ot.toast.clear();              // Clear all toasts
ot.toast.clear('top-right');   // Clear specific placement
```

### Toast Anatomy

```html
<output class="toast" data-variant="success">
  <h6 class="toast-title">Title</h6>
  <div class="toast-message">Message text</div>
</output>
```

- Max-width: 28rem, min-width: 20rem
- Left border colored by variant (`--_variant-color`)
- Enter animation: fade in + slide down
- Exit animation: fade out + collapse height
- Hover pauses auto-dismiss timer

## Tooltip

Tooltips are auto-converted from `title` attributes by Oat's JS. For manual control, use `data-tooltip` directly.

### Automatic Conversion

```html
<button title="Save changes">Save</button>
<!-- Automatically converted to data-tooltip, aria-label set, title removed -->
```

### Manual Tooltip

```html
<button data-tooltip="Save changes">Save</button>
```

### Placement

```html
<button data-tooltip="Top tooltip" data-tooltip-placement="top">Top</button>
<button data-tooltip="Bottom tooltip" data-tooltip-placement="bottom">Bottom</button>
<button data-tooltip="Left tooltip" data-tooltip-placement="left">Left</button>
<button data-tooltip="Right tooltip" data-tooltip-placement="right">Right</button>
```

Default placement: top.

### Tooltip Behavior

- Appears on `:hover` and `:focus-visible`
- 700ms delay before showing
- Dark background (`var(--foreground)`), light text (`var(--background)`)
- Arrow pointing toward the target element
- `z-index: calc(var(--z-modal) + 10)` (above modals)
- `pointer-events: none`

### Mutation Observer

The tooltip system uses a `MutationObserver` to auto-convert `title` attributes on dynamically added elements. No manual intervention needed for SPA content.

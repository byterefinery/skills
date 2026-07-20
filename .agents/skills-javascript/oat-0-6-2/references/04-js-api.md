# JavaScript API

Oat exposes a minimal global API on `window.ot`.

## Toast Notifications

### `ot.toast(message, title?, options?)`

Show a text-based toast notification.

```javascript
// Basic
ot.toast('Action completed');

// With title
ot.toast('Action completed', 'All good');

// With options
ot.toast('Success', 'Saved', { variant: 'success' });
ot.toast('Error', 'Oops', { variant: 'danger', placement: 'top-left' });
ot.toast('Warning', 'Warning', { variant: 'warning', placement: 'bottom-right' });
ot.toast('Info', 'Notice', { placement: 'top-center', duration: 0 });
```

### Options

| Option | Default | Values |
|---|---|---|
| `variant` | `''` | `'success'`, `'danger'`, `'warning'` |
| `placement` | `'top-right'` | `'top-left'`, `'top-center'`, `'top-right'`, `'bottom-left'`, `'bottom-center'`, `'bottom-right'` |
| `duration` | `4000` | Milliseconds until auto-dismiss. `0` = persistent. |

### `ot.toast.el(element, options?)`

Show a toast with custom HTML content.

```javascript
// From a template (cloned, original preserved)
ot.toast.el(document.querySelector('#my-template'));
ot.toast.el(document.querySelector('#my-template'), { duration: 8000, placement: 'bottom-center' });

// From a dynamic element
const el = document.createElement('output');
el.className = 'toast';
el.setAttribute('data-variant', 'warning');
el.innerHTML = '<h6 class="toast-title">Warning</h6><p>Custom content</p>';
ot.toast.el(el);
```

The element is cloned before display. Templates can be reused.

### `ot.toast.clear(placement?)`

Dismiss toasts.

```javascript
ot.toast.clear();           // All toasts
ot.toast.clear('top-right'); // Specific placement
```

### Toast Behavior

- Auto-dismiss after `duration` ms
- Timer pauses on hover, resumes on mouse leave
- Animated enter/exit transitions
- Stacked vertically in container
- Container uses Popover API (manual popover)
- Max width 28rem, min width 20rem

### Toast Container Structure

```html
<div class="toast-container" popover="manual" data-placement="top-right">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Title</h6>
    <div class="toast-message">Message</div>
  </output>
</div>
```

---

## Tooltip Enhancement

Oat progressively enhances native `title` attributes into styled tooltips.

### How It Works

1. On DOMContentLoaded, all `[title]` elements are processed
2. `title` → `data-tooltip` (custom styled)
3. `aria-label` added if not present
4. Original `title` removed
5. MutationObserver watches for new `[title]` elements

### Usage

```html
<button title="Save changes">Save</button>
<button title="Delete" data-tooltip-placement="bottom">Delete</button>
```

### Placement

Add `data-tooltip-placement` before or after the tooltip is enhanced:

```html
<button title="Top">Top</button>
<button title="Bottom" data-tooltip-placement="bottom">Bottom</button>
<button title="Left" data-tooltip-placement="left">Left</button>
<button title="Right" data-tooltip-placement="right">Right</button>
```

### Replaced Elements

`<img>`, `<iframe>`, and other replaced elements cannot have `title` rendered as tooltips. Wrap them:

```html
<span title="Photo tooltip"><img src="photo.jpg" /></span>
```

---

## Sidebar Toggle

Oat handles sidebar toggle via delegated click events. No direct API call needed.

### Toggle Button

```html
<button data-sidebar-toggle aria-label="Toggle menu" class="outline">☰</button>
```

Clicking toggles `data-sidebar-open` on the nearest `[data-sidebar-layout]` ancestor.

### Auto-dismiss on Mobile

On screens ≤768px, clicking outside the sidebar dismisses it automatically.

### Programmatic Toggle

```javascript
// Open sidebar
document.querySelector('[data-sidebar-layout]').setAttribute('data-sidebar-open', '');

// Close sidebar
document.querySelector('[data-sidebar-layout]').removeAttribute('data-sidebar-open');

// Toggle
document.querySelector('[data-sidebar-layout]').toggleAttribute('data-sidebar-open');
```

---

## Dialog Polyfills

Oat includes polyfills and shims for dialog support:

### `command`/`commandfor` Polyfill

Safari does not support `command`/`commandfor` on buttons. Oat polyfills this:

```javascript
// Polyfill behavior
button[commandfor="dialog-id"][command="show-modal"] → dialog.showModal()
button[commandfor="dialog-id"][command="close"] → dialog.close()
button[commandfor="dialog-id"] → toggle (showModal/close)
```

### Dialog Touch Shim

Prevents backdrop touch clicks from bleeding through on touch devices:

```javascript
// On touchstart on dialog backdrop → preventDefault + close
```

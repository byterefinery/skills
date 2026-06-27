# 07 — Feedback

## alert

Informs users about important events.

**Class names:**
- component: `alert`
- style: `alert-outline`, `alert-dash`, `alert-soft`
- color: `alert-info`, `alert-success`, `alert-warning`, `alert-error`
- direction: `alert-vertical`, `alert-horizontal`

```html
<div role="alert" class="alert {MODIFIER}">
  <span>Message</span>
</div>
```

Use `sm:alert-horizontal` for responsive layouts.

## toast

Stacks elements in a corner of the page.

**Class names:**
- component: `toast`
- placement: `toast-start`, `toast-center`, `toast-end`, `toast-top`, `toast-middle`, `toast-bottom`

```html
<div class="toast {MODIFIER}">
  <div class="alert alert-success">
    <span>Saved!</span>
  </div>
</div>
```

## modal

Dialog box opened by a button click.

**Class names:**
- component: `modal`
- part: `modal-box`, `modal-action`, `modal-backdrop`, `modal-toggle`
- modifier: `modal-open`
- placement: `modal-top`, `modal-middle`, `modal-bottom`, `modal-start`, `modal-end`

Using HTML dialog (recommended):
```html
<button onclick="my_modal.showModal()">Open</button>
<dialog id="my_modal" class="modal">
  <div class="modal-box">
    <h3>Title</h3>
    <p>Content</p>
  </div>
  <form method="dialog" class="modal-backdrop"><button>Close</button></form>
</dialog>
```

Using checkbox (legacy):
```html
<label for="my-modal" class="btn">Open</label>
<input type="checkbox" id="my-modal" class="modal-toggle" />
<div class="modal">
  <div class="modal-box">Content</div>
  <label class="modal-backdrop" for="my-modal">Close</label>
</div>
```

Use unique IDs for each modal. Add `tabindex="0"` to make it focusable.

## tooltip

Shows a message on hover.

**Class names:**
- component: `tooltip`
- part: `tooltip-content`
- modifier: `tooltip-open`
- placement: `tooltip-top`, `tooltip-bottom`, `tooltip-left`, `tooltip-right`
- color: `tooltip-primary`, `tooltip-secondary`, `tooltip-accent`, `tooltip-info`, `tooltip-success`, `tooltip-warning`, `tooltip-error`

```html
<div class="tooltip {MODIFIER}" data-tip="Tooltip text">
  <button class="btn">Hover me</button>
</div>
```

## skeleton

Loading state placeholder with shimmer animation.

**Class names:**
- component: `skeleton`
- modifier: `skeleton-text`

```html
<div class="skeleton"></div>
<div class="skeleton skeleton-text">Loading data...</div>
```

Add `h-*` and `w-*` utility classes to set dimensions.

## progress

Linear progress bar.

**Class names:**
- component: `progress`
- color: `progress-primary`, `progress-secondary`, `progress-accent`, `progress-neutral`, `progress-info`, `progress-success`, `progress-warning`, `progress-error`

```html
<progress class="progress {MODIFIER}" value="50" max="100"></progress>
```

Must specify `value` and `max` attributes.

## radial-progress

Circular progress indicator.

**Class names:**
- component: `radial-progress`

```html
<div class="radial-progress" style="--value:70;" aria-valuenow="70" role="progressbar">70%</div>
```

`--value` must be 0–100. Use `--size` (default `5rem`) and `--thickness` for customization. Always include `aria-valuenow` and `role="progressbar"`.

## countdown

Animated number transition between 0–999.

**Class names:**
- component: `countdown`

```html
<span class="countdown">
  <span style="--value:42;"></span>
</span>
```

Change the `--value` CSS variable and text via JavaScript. Add `aria-live="polite"` and `aria-label` for screen readers.

## swap

Toggles visibility between two elements using a checkbox or class.

**Class names:**
- component: `swap`
- part: `swap-on`, `swap-off`, `swap-indeterminate`
- modifier: `swap-active`
- style: `swap-rotate`, `swap-flip`

Using checkbox:
```html
<label class="swap {MODIFIER}">
  <input type="checkbox" />
  <span class="swap-on">☀️</span>
  <span class="swap-off">🌙</span>
</label>
```

Using class:
```html
<div class="swap swap-active {MODIFIER}">
  <span class="swap-on">On</span>
  <span class="swap-off">Off</span>
</div>
```

Use `swap-indeterminate` for a third indeterminate state.

## status

Small dot icon showing current status (online, offline, etc.).

**Class names:**
- component: `status`
- color: `status-primary`, `status-secondary`, `status-accent`, `status-neutral`, `status-info`, `status-success`, `status-warning`, `status-error`
- size: `status-xs`, `status-sm`, `status-md`, `status-lg`, `status-xl`

```html
<span class="status {MODIFIER}"></span>
```

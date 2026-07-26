# Utilities

Utility classes for common layout and styling patterns.

## Text Alignment

```css
.align-left    { text-align: start; }
.align-center  { text-align: center; }
.align-right   { text-align: end; }
```

## Text Color

```css
.text-light   { color: var(--muted-foreground); }
.text-lighter { color: var(--faint-foreground); }
```

## Flexbox

```css
.flex           { display: flex; }
.flex-col       { flex-direction: column; }
.items-center   { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-end    { justify-content: flex-end; }
```

## Stacks

```css
.hstack {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
  align-content: flex-start;
  height: auto;
}

.vstack {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
```

Stacks reset child margins and provide consistent gaps.

## Gap

```css
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-4 { gap: var(--space-4); }
```

## Margins

```css
.mt-2 { margin-block-start: var(--space-2); }
.mt-4 { margin-block-start: var(--space-4); }
.mt-6 { margin-block-start: var(--space-6); }

.mb-2 { margin-block-end: var(--space-2); }
.mb-4 { margin-block-end: var(--space-4); }
.mb-6 { margin-block-end: var(--space-6); }
```

## Padding

```css
.p-4 { padding: var(--space-4); }
```

## Width

```css
.w-100 { width: 100%; }
```

## Unstyled

Remove default list/link styling:

```css
:is(ul, ol, a).unstyled {
  list-style: none;
  text-decoration: none;
  padding: 0;
}
```

Used for breadcrumbs and custom navigation lists.

---

## Animations

### Pop-in

`class="animate-pop-in"` — 3D pop-in animation for modals/overlays.

```html
<dialog class="animate-pop-in" id="my-dialog">
  ...
</dialog>
```

Swings from above with perspective rotation. Supports exit animation via `data-state="closing"`.

### Slide-in

`class="animate-slide-in"` — Slide-in from right for toasts/panels.

```html
<div class="animate-slide-in">
  ...
</div>
```

Exit via `data-state="closing"`.

### Reduced Motion

All animations respect `prefers-reduced-motion: reduce`:

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

No extra configuration needed.

### Dialog Animations

Built-in dialog transitions:
- Scale from 0.95 to 1
- Opacity 0 to 1
- Backdrop fade
- Uses `@starting-style` for entry animation
- 150ms duration

### Toast Animations

Built-in toast transitions:
- Enter: translateY(-1rem) + opacity 0 → translateY(0) + opacity 1
- Exit: opacity 0, margin 0, padding 0, max-height 0
- 300ms duration

### Spinner Animation

`@keyframes spin` — 360deg rotation, 1s linear infinite. Applied to `[aria-busy="true"]::before`.

### Skeleton Animation

`@keyframes anim` — Shimmer effect via background-position shift. 2s infinite.

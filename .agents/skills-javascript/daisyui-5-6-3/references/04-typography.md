# 04 — Typography

## link

Adds underline style to links.

**Class names:**
- component: `link`
- style: `link-hover`
- color: `link-neutral`, `link-primary`, `link-secondary`, `link-accent`, `link-success`, `link-info`, `link-warning`, `link-error`

```html
<a class="link {MODIFIER}">Click me</a>
```

## kbd

Displays keyboard shortcuts.

**Class names:**
- component: `kbd`
- size: `kbd-xs`, `kbd-sm`, `kbd-md`, `kbd-lg`, `kbd-xl`

```html
<kbd class="kbd {MODIFIER}">K</kbd>
```

## text-rotate

Rotates up to 6 lines of text in an infinite loop (10s default). Pauses on hover.

**Class names:**
- component: `text-rotate`

```html
<span class="text-rotate">
  <span>
    <span>Word 1</span>
    <span>Word 2</span>
    <span>Word 3</span>
  </span>
</span>
```

Must have one inner span/div containing 2–6 child spans. Set custom duration with `duration-{ms}` (e.g., `duration-12000`).

## loading

Shows an animation to indicate loading state.

**Class names:**
- component: `loading`
- style: `loading-spinner`, `loading-dots`, `loading-ring`, `loading-ball`, `loading-bars`, `loading-infinity`
- size: `loading-xs`, `loading-sm`, `loading-md`, `loading-lg`, `loading-xl`

```html
<span class="loading {MODIFIER}"></span>
```

# 03 — Layout Components

## divider

Separates content vertically or horizontally.

**Class names:**
- component: `divider`
- color: `divider-neutral`, `divider-primary`, `divider-secondary`, `divider-accent`, `divider-success`, `divider-warning`, `divider-info`, `divider-error`
- direction: `divider-vertical`, `divider-horizontal`
- placement: `divider-start`, `divider-end`

```html
<div class="divider {MODIFIER}">{text}</div>
```

Omit text for a blank divider.

## join

Groups multiple items (buttons, inputs) with shared border radius.

**Class names:**
- component: `join`, `join-item`
- direction: `join-vertical`, `join-horizontal`

```html
<div class="join {MODIFIER}">{CONTENT}</div>
```

Any direct child of `join` gets joined. Use `lg:join-horizontal` for responsive layouts.

## stack

Visually puts elements on top of each other with slight offsets.

**Class names:**
- component: `stack`
- modifier: `stack-top`, `stack-bottom`, `stack-start`, `stack-end`

```html
<div class="stack {MODIFIER}">{CONTENT}</div>
```

Use `w-*` and `h-*` to make all items the same size.

## hero

Large box or image with title and description.

**Class names:**
- component: `hero`
- part: `hero-content`, `hero-overlay`

```html
<div class="hero">
  <div class="hero-overlay bg-black/40"></div>
  <div class="hero-content">
    <h1>Title</h1>
    <p>Description</p>
  </div>
</div>
```

Use `hero-overlay` inside the hero to overlay the background image with a color.

## indicator

Places an element on the corner of another element (badges, notifications).

**Class names:**
- component: `indicator`
- part: `indicator-item`
- placement: `indicator-start`, `indicator-center`, `indicator-end`, `indicator-top`, `indicator-middle`, `indicator-bottom`

```html
<div class="indicator">
  <span class="indicator-item">{badge}</span>
  <div>{main content}</div>
</div>
```

All `indicator-item` elements must come before the main content. Default placement is `indicator-end indicator-top`.

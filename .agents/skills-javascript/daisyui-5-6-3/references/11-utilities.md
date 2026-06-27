# 11 — Utilities

## mask

Crops element content to common shapes.

**Class names:**
- component: `mask`
- style: `mask-squircle`, `mask-heart`, `mask-hexagon`, `mask-hexagon-2`, `mask-decagon`, `mask-pentagon`, `mask-diamond`, `mask-square`, `mask-circle`, `mask-star`, `mask-star-2`, `mask-triangle`, `mask-triangle-2`, `mask-triangle-3`, `mask-triangle-4`
- modifier: `mask-half-1`, `mask-half-2`

```html
<img class="mask {STYLE}" src="{url}" />
```

`mask` + a style class is required. Works on any element, not just images. Set custom sizes with `w-*` and `h-*`.

## indicator

See [03 — Layout Components](references/03-layout-components.md).

## diff

Side-by-side comparison of two items with draggable divider.

**Class names:**
- component: `diff`
- part: `diff-item-1`, `diff-item-2`, `diff-resizer`

```html
<figure class="diff">
  <div class="diff-item-1">{item 1}</div>
  <div class="diff-item-2">{item 2}</div>
  <div class="diff-resizer"></div>
</figure>
```

Add `aspect-16/9` or similar to maintain aspect ratio.

## aura

Animated border light effect around a component.

**Class names:**
- component: `aura`
- style: `aura-dual`, `aura-rainbow`, `aura-holo`, `aura-gold`, `aura-silver`, `aura-glow`
- size: `aura-xs`, `aura-sm`, `aura-md`, `aura-lg`, `aura-xl`

```html
<div class="aura {MODIFIER}">
  <button class="btn btn-primary">Highlighted</button>
</div>
```

Must have exactly one direct child. Set custom colors with `text-*` (aura color) and `bg-*` (background). Set animation duration with `duration-*`. Use sparingly — don't apply to multiple elements on the same page.

## hover-3d

3D tilt effect on mouse movement.

**Class names:**
- component: `hover-3d`

```html
<div class="hover-3d">
  <figure>{content}</figure>
  <div></div><div></div><div></div><div></div>
  <div></div><div></div><div></div><div></div>
</div>
```

Must have exactly 9 direct children: 1 content element + 8 empty `<div>` hover zones. Only put non-interactive content inside (no buttons, links, inputs). Can be `<a>` instead of `<div>` to make the whole thing clickable.

## hover-gallery

Image gallery that shows additional images on horizontal hover.

**Class names:**
- component: `hover-gallery`

```html
<figure class="hover-gallery max-w-60">
  <img src="{image1}" />
  <img src="{image2}" />
  <img src="{image3}" />
</figure>
```

Up to 10 images. Needs a `max-width` constraint. Images must be same dimensions. Can be `<div>` or `<figure>`.

## calendar

Styles for third-party calendar libraries.

**Class names:**
- `cally` — for Cally web component
- `react-day-picker` — for React DayPicker
- `vc` — for Vanilla Calendar Pro

```html
<!-- Cally -->
<calendar-date class="cally">{content}</calendar-date>

<!-- React DayPicker -->
<DayPicker className="react-day-picker" />

<!-- Vanilla Calendar Pro -->
<div id="calendar" class="vc"></div>
<script>
  const { Calendar } = window.VanillaCalendarPro
  const cal = new Calendar("#calendar")
  cal.init()
</script>
```

## theme-controller

Checkbox/radio that controls the page theme.

**Class names:**
- component: `theme-controller`

```html
<input type="checkbox" value="dark" class="theme-controller" />
```

The `value` must be a valid daisyUI theme name. When checked, the page switches to that theme.

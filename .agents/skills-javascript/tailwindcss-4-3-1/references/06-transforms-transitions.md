# Transforms & Transitions

## Transform

### Enable/Disable

`transform` — enables CSS transforms using custom properties.

`transform-none` — `transform: none`.

`transform-cpu` — uses `transform` property (GPU composite).

`transform-gpu` — adds `translateZ(0)` for hardware acceleration.

### Transform Style

`transform-flat` → `transform-style: flat`.

`transform-3d` → `transform-style: preserve-3d`.

### Transform Box

`transform-content` → `transform-box: content-box`.

`transform-border` → `transform-box: border-box`.

`transform-fill` → `transform-box: fill-box`.

`transform-stroke` → `transform-box: stroke-box`.

`transform-view` → `transform-box: view-box`.

### Backface Visibility

`backface-visible`, `backface-hidden`.

## Translate

`translate-*` — spacing scale, fractions. Static: `none`, `full` (100%), `-full` (-100%).

Axis-specific: `translate-x-*`, `translate-y-*`, `translate-z-*` (no fractions for z).

Negative values: `-translate-x-4`, `-translate-y-full`.

3D: `translate-3d` — enables z-axis in the translate.

```html
<div class="translate-x-4 translate-y-2">
<div class="-translate-x-full">  /* slide out left */
<div class="translate-y-1/2">  /* 50% down */
```

## Scale

`scale-*` — bare integers (%). Static: `none`.

Axis-specific: `scale-x-*`, `scale-y-*`, `scale-z-*`.

Negative: `-scale-x-100` (flip horizontally).

3D: `scale-3d` — enables z-axis.

```html
<div class="scale-95">  /* 95% */
<div class="scale-x-[-1]">  /* flip X */
<div class="hover:scale-105">
```

## Rotate

`rotate-*` — bare integers (degrees). Static: `none`.

Axis-specific: `rotate-x-*`, `rotate-y-*`, `rotate-z-*`.

Negative: `-rotate-45`.

Arbitrary vector: `rotate-[x_45deg]`, `rotate-[1_2_3_45deg]`.

```html
<div class="rotate-45">
<div class="-rotate-90">
<div class="rotate-x-12">
```

## Skew

`skew-x-*`, `skew-y-*` — bare integers (degrees). Negative: `-skew-x-3`.

`skew-*` — applies to both axes.

## Perspective

`perspective-*` — theme values (`dramatic`, `near`, `normal`, `midrange`, `distant`). Static: `none`.

`perspective-origin-*` — `center`, `top`, `top-right`, `right`, `bottom-right`, `bottom`, `bottom-left`, `left`, `top-left`.

## Origin

`origin-*` — `center`, `top`, `top-right`, `right`, `bottom-right`, `bottom`, `bottom-left`, `left`, `top-left`. Theme: `--transform-origin-*`.

## Zoom

`zoom-*` — bare integers (%). Suggested: `50`, `75`, `90`, `95`, `100`, `105`, `110`, `125`, `150`, `200`.

## Transitions

### Transition Property

`transition` — default transition properties (color, background, border, outline, text-decoration, fill, stroke, gradients, opacity, box-shadow, transform, translate, scale, rotate, filter, backdrop-filter, display, content-visibility, overlay, pointer-events).

`transition-none` → `transition-property: none`.

`transition-all` → `transition-property: all`.

`transition-colors` — color-related properties only.

`transition-opacity` — opacity only.

`transition-shadow` — box-shadow only.

`transition-transform` — transform, translate, scale, rotate.

`transition-*` — arbitrary property names.

### Transition Behavior

`transition-discrete` → `transition-behavior: allow-discrete`.

`transition-normal` → `transition-behavior: normal`.

### Transition Duration

`duration-*` — bare integers (ms). Theme: `--transition-duration-*`.

Suggested: `75`, `100`, `150`, `200`, `300`, `500`, `700`, `1000`.

`duration-initial` — reset.

### Transition Timing Function

`ease-*` — theme values (`in`, `out`, `in-out`). Static: `linear`, `initial`.

### Transition Delay

`delay-*` — bare integers (ms). Theme: `--transition-delay-*`.

Suggested: `75`, `100`, `150`, `200`, `300`, `500`, `700`, `1000`.

## Animation

`animate-*` — theme values (`spin`, `ping`, `pulse`, `bounce`). Static: `none`.

```html
<div class="animate-spin">  /* loading spinner */
<div class="animate-pulse">  /* pulsing effect */
<div class="animate-bounce">  /* bouncing */
```

### Custom Animations

```css
@theme {
  --animate-fade-in: fade-in 0.3s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

```html
<div class="animate-fade-in">
```

## Will Change

`will-change-auto`, `will-change-scroll`, `will-change-contents`, `will-change-transform`.

`will-change-*` — arbitrary property names.

## Contain

`contain-none`, `contain-content`, `contain-strict`.

`contain-size`, `contain-inline-size`, `contain-layout`, `contain-paint`, `contain-style`.

`contain-*` — arbitrary values.

## Content

`content-none` → `content: none`.

`content-*` — arbitrary values with quotes.

```html
<div class="content-['Hello']">
```

## Cursor

`cursor-auto`, `cursor-default`, `cursor-pointer`, `cursor-wait`, `cursor-text`, `cursor-move`, `cursor-help`, `cursor-not-allowed`, `cursor-none`, `cursor-context-menu`, `cursor-progress`, `cursor-cell`, `cursor-crosshair`, `cursor-vertical-text`, `cursor-alias`, `cursor-copy`, `cursor-no-drop`, `cursor-grab`, `cursor-grabbing`, `cursor-all-scroll`, `cursor-zoom-in`, `cursor-zoom-out`.

Directional: `cursor-col-resize`, `cursor-row-resize`, `cursor-n-resize`, `cursor-e-resize`, `cursor-s-resize`, `cursor-w-resize`, `cursor-ne-resize`, `cursor-nw-resize`, `cursor-se-resize`, `cursor-sw-resize`, `cursor-ew-resize`, `cursor-ns-resize`, `cursor-nesw-resize`, `cursor-nwse-resize`.

## Touch Action

`touch-auto`, `touch-none`, `touch-manipulation`.

`touch-pan-x`, `touch-pan-left`, `touch-pan-right`.

`touch-pan-y`, `touch-pan-up`, `touch-pan-down`.

`touch-pinch-zoom`.

## User Select

`select-none`, `select-text`, `select-all`, `select-auto`.

## Resize

`resize-none`, `resize-x`, `resize-y`, `resize` (both).

## Scroll Snap

`snap-none`, `snap-x`, `snap-y`, `snap-both`.

`snap-mandatory`, `snap-proximity`.

`snap-align-none`, `snap-start`, `snap-end`, `snap-center`.

`snap-normal`, `snap-always`.

## Scroll Margin & Padding

`scroll-m-*`, `scroll-mx-*`, `scroll-my-*`, `scroll-ms-*`, `scroll-me-*`, `scroll-mbs-*`, `scroll-mbe-*`, `scroll-mt-*`, `scroll-mr-*`, `scroll-mb-*`, `scroll-ml-*`.

`scroll-p-*`, `scroll-px-*`, `scroll-py-*`, `scroll-ps-*`, `scroll-pe-*`, `scroll-pbs-*`, `scroll-pbe-*`, `scroll-pt-*`, `scroll-pr-*`, `scroll-pb-*`, `scroll-pl-*`.

## Columns

`columns-*` — bare integers, theme values. Static: `auto`.

`break-before-*` — `auto`, `avoid`, `all`, `avoid-page`, `page`, `left`, `right`, `column`.

`break-inside-*` — `auto`, `avoid`, `avoid-page`, `avoid-column`.

`break-after-*` — same as break-before.

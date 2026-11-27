# Filters & Blurs

## Filter

`filter` — enables CSS filter chain using custom properties.

`filter-none` → `filter: none`.

`filter-*` — arbitrary filter values.

## Blur

`blur` — default blur from theme. `blur-*` — theme values (`xs`, `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`). `blur-none`.

Arbitrary: `blur-[10px]`.

```html
<div class="blur-sm">
<div class="blur-xl">
<img class="hover:blur-none" class="blur-md">
```

## Brightness

`brightness-*` — bare integers (%). Theme: `--brightness-*`.

Suggested: `0`, `50`, `75`, `90`, `95`, `100`, `105`, `110`, `125`, `150`, `200`.

```html
<img class="brightness-75">  /* darken */
<img class="brightness-110">  /* brighten */
```

## Contrast

`contrast-*` — bare integers (%). Theme: `--contrast-*`.

Suggested: `0`, `50`, `75`, `100`, `125`, `150`, `200`.

## Grayscale

`grayscale` — default (100%). `grayscale-*` — bare integers (%). Theme: `--grayscale-*`.

Suggested: `0`, `25`, `50`, `75`, `100`.

## Hue Rotate

`hue-rotate-*` — bare integers (degrees). Negative: `-hue-rotate-15`. Theme: `--hue-rotate-*`.

Suggested: `0`, `15`, `30`, `60`, `90`, `180`.

## Invert

`invert` — default (100%). `invert-*` — bare integers (%). Theme: `--invert-*`.

Suggested: `0`, `25`, `50`, `75`, `100`.

## Saturate

`saturate-*` — bare integers (%). Theme: `--saturate-*`.

Suggested: `0`, `50`, `100`, `150`, `200`.

## Sepia

`sepia` — default (100%). `sepia-*` — bare integers (%). Theme: `--sepia-*`.

Suggested: `0`, `50`, `100`.

## Drop Shadow

`drop-shadow` — default from theme. `drop-shadow-*` — named shadows or colors.

`drop-shadow-none`.

Opacity modifier: `drop-shadow-md/75`.

Arbitrary: `drop-shadow-[0_4px_6px_rgba(0,0,0,0.1)]`.

```html
<div class="drop-shadow-lg">
<div class="drop-shadow-md/50">
<div class="drop-shadow-none">
```

## Opacity

`opacity-*` — bare integers (%). Theme: `--opacity-*`.

Suggested: `0`, `5`, `10`, ..., `100` (steps of 5).

```html
<div class="opacity-0">  /* hidden */
<div class="opacity-50">  /* half transparent */
<div class="opacity-100">  /* fully opaque */
```

## Backdrop Filters

All filter utilities have a `backdrop-*` variant that applies to the area behind an element.

### Backdrop Blur

`backdrop-blur` — default. `backdrop-blur-*` — theme values. `backdrop-blur-none`.

### Backdrop Brightness

`backdrop-brightness-*` — bare integers (%).

### Backdrop Contrast

`backdrop-contrast-*` — bare integers (%).

### Backdrop Grayscale

`backdrop-grayscale` — default (100%). `backdrop-grayscale-*`.

### Backdrop Hue Rotate

`backdrop-hue-rotate-*` — bare integers (degrees). Negative: `-backdrop-hue-rotate-15`.

### Backdrop Invert

`backdrop-invert` — default (100%). `backdrop-invert-*`.

### Backdrop Opacity

`backdrop-opacity-*` — bare integers (%).

### Backdrop Saturate

`backdrop-saturate-*` — bare integers (%).

### Backdrop Sepia

`backdrop-sepia` — default (100%). `backdrop-sepia-*`.

### Backdrop Filter

`backdrop-filter` — enables backdrop filter chain.

`backdrop-filter-none` → `backdrop-filter: none`.

## Combining Filters

Multiple filter utilities stack automatically. Tailwind manages the CSS custom properties internally.

```html
<div class="blur-sm brightness-110 contrast-125 saturate-150">
```

Compiled to a single `filter` declaration with all transforms chained.

## Practical Patterns

### Frosted Glass

```html
<div class="backdrop-blur-md bg-white/30 rounded-xl">
  Frosted glass card
</div>
```

### Image Hover Effects

```html
<img class="transition-all duration-300 hover:scale-105 hover:brightness-110 hover:saturate-150">
```

### Loading Skeleton

```html
<div class="animate-pulse bg-gray-200 rounded-lg h-4 w-3/4">
```

### Focus Ring

```html
<button class="ring-2 ring-blue-500 ring-offset-2 transition-all">
```

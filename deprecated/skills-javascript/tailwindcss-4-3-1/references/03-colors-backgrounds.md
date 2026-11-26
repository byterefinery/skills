# Colors & Backgrounds

## Color Utilities

All color utilities support the same value patterns: theme colors, arbitrary colors, and opacity modifiers.

### Text Color

`text-*` — resolves from `--text-color-*` and `--color-*` namespaces.

```html
<span class="text-red-500">Red text</span>
<span class="text-[#bada55]">Arbitrary</span>
<span class="text-red-500/50">Red with 50% opacity</span>
<span class="text-transparent">Transparent</span>
<span class="text-current">Current color</span>
<span class="text-inherit">Inherit</span>
```

### Background Color

`bg-*` — resolves from `--background-color-*` and `--color-*` namespaces.

```html
<div class="bg-blue-500">
<div class="bg-[url('/img.png')]">  /* arbitrary image */
<div class="bg-blue-500/30">  /* 30% opacity */
```

The `bg-*` utility is multi-purpose with arbitrary values:
- Colors → `background-color`
- Images/URLs → `background-image`
- Percentages/positions → `background-position`
- Lengths/sizes → `background-size`

### Border Color

`border-*`, `border-x-*`, `border-y-*`, `border-s-*`, `border-e-*`, `border-bs-*`, `border-be-*`, `border-t-*`, `border-r-*`, `border-b-*`, `border-l-*`.

Supports both color and width values. `border-2` sets width, `border-red-500` sets color.

```html
<div class="border border-red-500">
<div class="border-2 border-blue-500/50">
<div class="border-t-4 border-t-gray-300">
```

### Divide Color

`divide-*` — sets border color between children.

`divide-x-*`, `divide-y-*` — width. `divide-x-reverse`, `divide-y-reverse`.

`divide-solid`, `divide-dashed`, `divide-dotted`, `divide-double`, `divide-none`.

### Accent Color

`accent-*` — `accent-auto` and theme colors.

### Caret Color

`caret-*` — theme colors.

### Placeholder Color

`placeholder-*` — theme colors with opacity modifiers.

### Fill & Stroke (SVG)

`fill-*` — colors. `fill-none`.

`stroke-*` — colors and widths (`stroke-2`). `stroke-none`.

## Color Opacity Modifiers

Use `/` to apply opacity to any color utility:

```html
<div class="bg-red-500/50">  /* 50% opacity */
<div class="bg-red-500/[^var(--opacity)]">  /* arbitrary opacity */
<div class="text-blue-600/75">  /* 75% opacity */
```

Compiles to `color-mix(in oklab, <color> <opacity>%, transparent)` for perceptually uniform results.

Supported modifiers: `0`, `5`, `10`, ..., `100` (in steps of 5), or arbitrary values.

## Backgrounds

### Background Image

`bg-none` → `background-image: none`.

Theme: `--background-image-*` namespace.

Arbitrary: `bg-[url('/img.png')]`, `bg-[linear-gradient(...)]`.

### Background Size

`bg-auto`, `bg-cover`, `bg-contain`.

`bg-size-*` — arbitrary values.

### Background Position

`bg-top`, `bg-top-left`, `bg-top-right`, `bg-bottom`, `bg-bottom-left`, `bg-bottom-right`, `bg-left`, `bg-right`, `bg-center`.

`bg-position-*` — arbitrary values.

### Background Repeat

`bg-repeat`, `bg-no-repeat`, `bg-repeat-x`, `bg-repeat-y`, `bg-repeat-round`, `bg-repeat-space`.

### Background Attachment

`bg-fixed`, `bg-local`, `bg-scroll`.

### Background Clip

`bg-clip-border`, `bg-clip-padding`, `bg-clip-content`, `bg-clip-text`.

`bg-clip-text` is used for gradient text:

```html
<h1 class="bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
  Gradient Text
</h1>
```

### Background Origin

`bg-origin-border`, `bg-origin-padding`, `bg-origin-content`.

### Background Blend Mode

`bg-blend-*` — `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color`, `luminosity`.

### Mix Blend Mode

`mix-blend-*` — same values as bg-blend plus `plus-darker`, `plus-lighter`.

## Gradients

### Linear Gradients

`bg-linear-*` — direction or angle.

Directions: `to-t`, `to-tr`, `to-r`, `to-br`, `to-b`, `to-bl`, `to-l`, `to-tl`.

Angles: `bg-linear-0`, `bg-linear-45`, `bg-linear-90`, `bg-linear-180` (bare integers → degrees).

Negative angles: `-bg-linear-45`.

Interpolation modifiers: `/oklab`, `/oklch`, `/srgb`, `/hsl`, `/longer`, `/shorter`, `/increasing`, `/decreasing`.

```html
<div class="bg-linear-to-br/oklch from-blue-500 to-purple-500">
```

### Radial Gradients

`bg-radial` — default radial gradient. `bg-radial-*` — arbitrary gradient.

Modifiers for interpolation: same as linear.

### Conic Gradients

`bg-conic` — default. `bg-conic-*` — angle (bare integers → degrees). Negative: `-bg-conic-45`.

### Gradient Stops

`from-*`, `via-*`, `to-*` — colors with opacity modifiers, or positions (percentages).

`via-none` — removes the via stop.

```html
<div class="bg-linear-to-r from-red-500 via-yellow-500 to-green-500">
<div class="bg-linear-to-r from-blue-500/80 via-blue-500/50 50% to-transparent">
```

Stop positions: `from-25%`, `via-1/2`, `to-3/4`.

## Masks

### Mask Image

`mask-none`, `mask-*` (arbitrary images).

### Mask Size

`mask-auto`, `mask-cover`, `mask-contain`, `mask-size-*`.

### Mask Position

`mask-top`, `mask-top-left`, `mask-top-right`, `mask-bottom`, `mask-bottom-left`, `mask-bottom-right`, `mask-left`, `mask-right`, `mask-center`, `mask-position-*`.

### Mask Repeat

`mask-repeat`, `mask-no-repeat`, `mask-repeat-x`, `mask-repeat-y`, `mask-repeat-round`, `mask-repeat-space`.

### Mask Clip & Origin

`mask-clip-border`, `mask-clip-padding`, `mask-clip-content`, `mask-clip-fill`, `mask-clip-stroke`, `mask-clip-view`, `mask-no-clip`.

`mask-origin-border`, `mask-origin-padding`, `mask-origin-content`, `mask-origin-fill`, `mask-origin-stroke`, `mask-origin-view`.

### Mask Mode & Composite

`mask-alpha`, `mask-luminance`, `mask-match`.

`mask-add`, `mask-subtract`, `mask-intersect`, `mask-exclude`.

### Mask Type

`mask-type-alpha`, `mask-type-luminance`.

### Linear Masks

`mask-linear-*` — angle. `mask-linear-from-*`, `mask-linear-to-*` — colors/positions.

### Radial Masks

`mask-circle`, `mask-ellipse`.

`mask-radial-closest-side`, `mask-radial-farthest-side`, `mask-radial-closest-corner`, `mask-radial-farthest-corner`.

`mask-radial-at-*` — position. `mask-radial-from-*`, `mask-radial-to-*` — colors/positions.

### Conic Masks

`mask-conic-*` — angle. `mask-conic-from-*`, `mask-conic-to-*` — colors/positions.

### Edge Masks

`mask-x-from-*`, `mask-x-to-*` — horizontal edge fade.

`mask-y-from-*`, `mask-y-to-*` — vertical edge fade.

`mask-t-from-*`, `mask-t-to-*` — top edge.

`mask-r-from-*`, `mask-r-to-*` — right edge.

`mask-b-from-*`, `mask-b-to-*` — bottom edge.

`mask-l-from-*`, `mask-l-to-*` — left edge.

## Object Fit

`object-contain`, `object-cover`, `object-fill`, `object-none`, `object-scale-down`.

`object-*` — position: `top`, `top-left`, `top-right`, `bottom`, `bottom-left`, `bottom-right`, `left`, `right`, `center`.

## Box Decoration

`box-decoration-slice`, `box-decoration-clone`.

## Color Scheme

`scheme-normal`, `scheme-dark`, `scheme-light`, `scheme-light-dark`, `scheme-only-dark`, `scheme-only-light`.

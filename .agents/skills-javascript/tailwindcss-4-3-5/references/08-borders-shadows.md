# Borders & Shadows

## Border Radius

### All Corners

`rounded-*` — theme values (`xs`, `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`, `4xl`). Static: `none` (0), `full` (circle).

```html
<div class="rounded-lg">
<div class="rounded-full">  /* circle/pill */
<div class="rounded-none">
```

### Individual Sides

`rounded-t-*`, `rounded-r-*`, `rounded-b-*`, `rounded-l-*`.

### Individual Corners

`rounded-tl-*`, `rounded-tr-*`, `rounded-br-*`, `rounded-bl-*`.

### Start/End (Logical)

`rounded-s-*`, `rounded-e-*`, `rounded-ss-*`, `rounded-se-*`, `rounded-es-*`, `rounded-ee-*`.

## Border Width

`border-*`, `border-x-*`, `border-y-*`, `border-s-*`, `border-e-*`, `border-bs-*`, `border-be-*`, `border-t-*`, `border-r-*`, `border-b-*`, `border-l-*`.

Bare integers (px): `border-2`, `border-4`, `border-8`. Theme: `--border-width-*`.

```html
<div class="border-2 border-red-500">
<div class="border-b border-gray-200">
```

Omitting the value uses default width (1px): `border` → `border-width: 1px`.

## Border Style

`border-solid`, `border-dashed`, `border-dotted`, `border-double`, `border-hidden`, `border-none`.

## Border Color

Same utilities as width. Resolves from `--border-color-*` and `--color-*` namespaces. Supports opacity modifiers.

```html
<div class="border border-red-500/50">
<div class="border-t-2 border-t-blue-500">
```

## Divide

Width: `divide-x-*`, `divide-y-*` — bare integers (px), theme values. Default: 1px.

Color: `divide-*` — theme colors with opacity modifiers.

Style: `divide-solid`, `divide-dashed`, `divide-dotted`, `divide-double`, `divide-none`.

Reverse: `divide-x-reverse`, `divide-y-reverse`.

## Outline

### Outline Width

`outline` — default width. `outline-*` — bare integers (px), theme values.

### Outline Color

`outline-*` — theme colors with opacity modifiers.

### Outline Style

`outline-none`, `outline-solid`, `outline-dashed`, `outline-dotted`, `outline-double`.

`outline-hidden` — visually hidden outline (accessible).

### Outline Offset

`outline-offset-*` — bare integers, negative support.

```html
<button class="outline outline-2 outline-blue-500 outline-offset-2">
```

## Box Shadow

### Shadow Size

`shadow` — default shadow. `shadow-*` — theme values (`2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`). `shadow-none`.

### Shadow Color

`shadow-*` — theme colors with opacity modifiers.

```html
<div class="shadow-lg">
<div class="shadow-md shadow-blue-500/30">
<div class="shadow-none">
```

### Shadow Initial

`shadow-initial` — reset shadow color.

## Inset Shadow

Same pattern as box shadow: `inset-shadow`, `inset-shadow-*`, `inset-shadow-none`, `inset-shadow-initial`.

```html
<div class="inset-shadow-sm">
<div class="inset-shadow-md inset-shadow-blue-500/20">
```

## Ring

### Ring Width

`ring` — default (1px). `ring-*` — bare integers (px), theme values.

### Ring Color

`ring-*` — theme colors with opacity modifiers.

### Ring Offset

`ring-offset-*` — width (bare integers, theme values) or color.

`ring-inset` — inward ring.

```html
<button class="ring-2 ring-blue-500">
<button class="ring-2 ring-offset-2 ring-blue-500">
<button class="ring-4 ring-inset ring-gray-300">
```

## Inset Ring

`inset-ring` — default (1px). `inset-ring-*` — width or color.

```html
<input class="inset-ring-2 inset-ring-blue-500">
```

## Appearance

`appearance-none`, `appearance-auto`.

## Scheme

`scheme-normal`, `scheme-dark`, `scheme-light`, `scheme-light-dark`, `scheme-only-dark`, `scheme-only-light`.

## Forced Colors

`forced-color-adjust-none`, `forced-color-adjust-auto`.

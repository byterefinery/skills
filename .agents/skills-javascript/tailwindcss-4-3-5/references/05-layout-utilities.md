# Layout Utilities

## Display

| Class | CSS |
|---|---|
| `block` | `display: block` |
| `inline-block` | `display: inline-block` |
| `inline` | `display: inline` |
| `flex` | `display: flex` |
| `inline-flex` | `display: inline-flex` |
| `grid` | `display: grid` |
| `inline-grid` | `display: inline-grid` |
| `hidden` | `display: none` |
| `contents` | `display: contents` |
| `list-item` | `display: list-item` |
| `flow-root` | `display: flow-root` |
| `table` / `inline-table` | `display: table` / `inline-table` |
| `table-caption` | `display: table-caption` |
| `table-cell` | `display: table-cell` |
| `table-row` / `table-row-group` | `display: table-row` / `tr` |
| `table-column` / `table-column-group` | `display: table-column` / `colgroup` |
| `table-header-group` / `table-footer-group` | `display: thead` / `tfoot` |

## Positioning

| Class | CSS |
|---|---|
| `static` | `position: static` |
| `fixed` | `position: fixed` |
| `absolute` | `position: absolute` |
| `relative` | `position: relative` |
| `sticky` | `position: sticky` |

### Inset

`inset-*`, `inset-x-*`, `inset-y-*`, `top-*`, `right-*`, `bottom-*`, `left-*`, `inset-s-*`, `inset-e-*`, `inset-bs-*`, `inset-be-*`.

Static values: `auto`, `full` (100%), `-full` (-100%).

```html
<div class="absolute inset-0">  /* top/right/bottom/left: 0 */
<div class="fixed inset-x-0 top-0">  /* left/right: 0, top: 0 */
<div class="sticky top-4">
```

### Z-Index

`z-*` — supports negative values, bare integers, theme values. Static: `auto`.

```html
<div class="z-10">
<div class="z-auto">
<div class="-z-1">
```

### Order

`order-*` — bare integers 1–12, negative support. Static: `first` (-9999), `last` (9999).

## Float & Clear

`float-start`, `float-end`, `float-right`, `float-left`, `float-none`.

`clear-start`, `clear-end`, `clear-right`, `clear-left`, `clear-both`, `clear-none`.

## Sizing

### Width

`w-*` — spacing scale, fractions (`w-1/2`, `w-1/3`, `w-2/3`, `w-1/12`–`w-11/12`).

Static: `auto`, `full` (100%), `screen` (100vw), `svw` (100svw), `lvw` (100lvw), `dvw` (100dvw), `min` (min-content), `max` (max-content), `fit` (fit-content).

### Height

`h-*` — same values as width plus `lh` (1lh).

### Min/Max Width & Height

`min-w-*`, `max-w-*`, `min-h-*`, `max-h-*` — same value patterns. `max-w-none` / `max-h-none` → `none`.

`max-w-screen`, `min-w-screen`, `min-h-screen`, `max-h-screen`.

`max-w-*` also reads from `--container` namespace for `max-w-3xs` through `max-w-7xl`.

### Size (combined width + height)

`size-*` — sets both width and height. Same values as width/height.

### Inline/Block Size

`inline-*`, `min-inline-*`, `max-inline-*`, `block-*`, `min-block-*`, `max-block-*`.

### Aspect Ratio

`aspect-*` — static: `auto`, `square` (1/1). Fractions: `aspect-16/9`, `aspect-4/3`. Theme: `--aspect-video`.

## Box Sizing

`box-border` → `box-sizing: border-box`. `box-content` → `box-sizing: content-box`.

## Overflow

`overflow-*`, `overflow-x-*`, `overflow-y-*` — `auto`, `hidden`, `clip`, `visible`, `scroll`.

`overscroll-*`, `overscroll-x-*`, `overscroll-y-*` — `auto`, `contain`, `none`.

`scroll-auto`, `scroll-smooth` → `scroll-behavior`.

`scrollbar-auto`, `scrollbar-thin`, `scrollbar-none` → `scrollbar-width`.

`scrollbar-thumb-*`, `scrollbar-track-*` → scrollbar colors.

`scrollbar-gutter-auto`, `scrollbar-gutter-stable`, `scrollbar-gutter-both`.

## Container

`container` — sets `width: 100%` and `max-width` at each breakpoint. Reads from `--breakpoint-*` theme values.

```html
<div class="container mx-auto">
```

## Flexbox

### Flex Direction

`flex-row`, `flex-row-reverse`, `flex-col`, `flex-col-reverse`.

### Flex Wrap

`flex-wrap`, `flex-nowrap`, `flex-wrap-reverse`.

### Flex

`flex-*` — bare integers, fractions. Static: `auto`, `initial`, `none`.

```html
<div class="flex-1">  /* flex: 1 */
<div class="flex-auto">  /* flex: auto */
<div class="flex-initial">  /* flex: 0 auto */
<div class="flex-none">  /* flex: none */
```

### Flex Grow / Shrink

`grow`, `grow-*` — bare integers. `grow-0`. Default `grow` = `flex-grow: 1`.

`shrink`, `shrink-*` — bare integers. `shrink-0`. Default `shrink` = `flex-shrink: 1`.

### Flex Basis

`basis-*` — spacing scale, fractions. Static: `auto`, `full` (100%).

## Grid

### Grid Columns

`grid-cols-*` — bare integers (generates `repeat(N, minmax(0, 1fr))`), theme values, arbitrary `grid-cols-[minmax(0,1fr)_minmax(0,2fr)]`. Static: `none`, `subgrid`.

### Grid Rows

`grid-rows-*` — same pattern as columns.

### Column/Row Span

`col-span-*` — bare integers. Static: `full` (1 / -1).

`row-span-*` — same pattern.

### Column/Row Start & End

`col-start-*`, `col-end-*`, `row-start-*`, `row-end-*` — bare integers (negative supported), static: `auto`.

### Grid Auto Flow

`grid-flow-row`, `grid-flow-col`, `grid-flow-dense`, `grid-flow-row-dense`, `grid-flow-col-dense`.

### Auto Columns / Rows

`auto-cols-*` — static: `auto`, `min`, `max`, `fr`.

`auto-rows-*` — same values.

## Gap

`gap-*`, `gap-x-*`, `gap-y-*` — spacing scale, theme values.

## Space Between Children

`space-x-*`, `space-y-*` — spacing scale, negative support.

`space-x-reverse`, `space-y-reverse`.

Uses margin on children (not gap), so works with older browsers.

## Justify / Align Content

### Justify Content

`justify-normal`, `justify-center`, `justify-start`, `justify-end`, `justify-between`, `justify-around`, `justify-evenly`, `justify-baseline`, `justify-stretch`. Safe variants: `justify-center-safe`, `justify-end-safe`.

### Align Content

`content-normal`, `content-center`, `content-start`, `content-end`, `content-between`, `content-around`, `content-evenly`, `content-baseline`, `content-stretch`. Safe variants available.

### Place Content

`place-content-center`, `place-content-start`, `place-content-end`, `place-content-between`, `place-content-around`, `place-content-evenly`, `place-content-baseline`, `place-content-stretch`.

## Justify / Align Items

### Justify Items

`justify-items-normal`, `justify-items-center`, `justify-items-start`, `justify-items-end`, `justify-items-stretch`.

### Align Items

`items-center`, `items-start`, `items-end`, `items-baseline`, `items-baseline-last`, `items-stretch`.

### Place Items

`place-items-center`, `place-items-start`, `place-items-end`, `place-items-baseline`, `place-items-stretch`.

## Self Alignment

### Justify Self

`justify-self-auto`, `justify-self-start`, `justify-self-end`, `justify-self-center`, `justify-self-stretch`.

### Align Self

`self-auto`, `self-start`, `self-end`, `self-center`, `self-baseline`, `self-baseline-last`, `self-stretch`.

### Place Self

`place-self-auto`, `place-self-start`, `place-self-end`, `place-self-center`, `place-self-stretch`.

## Table Layout

`table-auto`, `table-fixed` → `table-layout`.

`caption-top`, `caption-bottom` → `caption-side`.

`border-collapse`, `border-separate` → `border-collapse`.

`border-spacing-*`, `border-spacing-x-*`, `border-spacing-y-*` → `border-spacing`.

## Visibility

`visible`, `invisible`, `collapse`.

## Isolation

`isolate` → `isolation: isolate`. `isolation-auto` → `isolation: auto`.

## Pointers

`pointer-events-none`, `pointer-events-auto`.

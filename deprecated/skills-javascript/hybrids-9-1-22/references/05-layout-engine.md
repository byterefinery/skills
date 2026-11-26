# Layout Engine

## Table of Contents

- [Overview](#overview)
- [Usage](#usage)
- [Layout Rules](#layout-rules)
- [Flexbox Rules](#flexbox-rules)
- [Grid Rules](#grid-rules)
- [Alignment Rules](#alignment-rules)
- [Size Rules](#size-rules)
- [Spacing Rules](#spacing-rules)
- [Position Rules](#position-rules)
- [Responsive Queries](#responsive-queries)
- [Dimensions](#dimensions)
- [Gotchas](#gotchas)

---

## Overview

The layout engine lets you declare CSS layouts directly in templates using the `layout` attribute. Rules are space-separated tokens that compile to CSS classes with generated stylesheets.

```html
<template layout="column center gap:2">
  <div layout="grow grid:1|max">Content</div>
  <footer layout@768px="hidden">Footer</footer>
</template>
```

### How It Works

1. Layout tokens are parsed and compiled to CSS rules
2. A unique class name is generated per element
3. CSS rules are injected into a shared stylesheet (via `adoptedStyleSheets` or `<style>`)
4. The class is applied to the element

### Template Element

The root `<template>` with a `layout` attribute applies styles to the host element:

```js
html`
  <template layout="column center gap:2">
    <h1>Title</h1>
    <p>Content</p>
  </template>
`
```

This applies the layout to the host component (shadow or light DOM root).

---

## Usage

### Host Layout (on `<template>`)

```js
html`
  <template layout="column gap:2 padding:2">
    <h1>Title</h1>
    <div layout="grow">Content area</div>
  </template>
`
```

### Element Layout

```js
html`
  <div layout="row center gap:1">
    <span layout="size:full">Full width</span>
  </div>
`
```

### Responsive Layout

```js
html`
  <div layout@768px="row" layout@480px="column">
    <!-- row on ≥768px, column on ≥480px, default otherwise -->
  </div>
`
```

### Media Queries

```js
html`
  <div layout@print="hidden" layout@portrait="column">
    Content
  </div>
`
```

---

## Layout Rules

### Display

| Rule | CSS |
|---|---|
| `block` | `display: block` |
| `inline` | `display: inline` |
| `inline:block` | `display: inline-block` |
| `contents` | `display: contents` |
| `hidden` | `display: none` |

---

## Flexbox Rules

| Rule | CSS |
|---|---|
| `row` | `display: flex; flex-flow: row nowrap` |
| `row-reverse` | `display: flex; flex-flow: row-reverse nowrap` |
| `column` | `display: flex; flex-flow: column nowrap` |
| `column-reverse` | `display: flex; flex-flow: column-reverse nowrap` |
| `row:wrap` | `display: flex; flex-flow: row wrap` |
| `column:wrap` | `display: flex; flex-flow: column wrap` |
| `grow` | `flex-grow: 1` |
| `grow:2` | `flex-grow: 2` |
| `shrink` | `flex-shrink: 1` |
| `shrink:0` | `flex-shrink: 0` |
| `basis:0` | `flex-basis: 0` |
| `basis:full` | `flex-basis: 100%` |
| `order` | `order: 0` |
| `order:2` | `order: 2` |

---

## Grid Rules

| Rule | CSS |
|---|---|
| `grid` | `display: grid` |
| `grid:2` | `display: grid; grid-template-columns: repeat(2, minmax(0, 1fr))` |
| `grid:1fr\|2fr` | `display: grid; grid-template-columns: 1fr 2fr` |
| `grid:3:rows` | `display: grid; grid-template-rows: repeat(3, minmax(0, 1fr))` |
| `grid:2:rows:auto-flow` | `display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); grid-auto-flow: row` |
| `grid:2:rows:dense` | `display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); grid-auto-flow: dense` |
| `area` | `grid-column: span 1; grid-row: span 1` |
| `area:2` | `grid-column: span 2` |
| `area:2:3` | `grid-column: span 2; grid-row: span 3` |

---

## Alignment Rules

| Rule | CSS |
|---|---|
| `center` | `place-items: center; place-content: center` |
| `items` | `place-items: start` |
| `items:center` | `place-items: center center` |
| `items:start:end` | `place-items: start end` |
| `content` | `place-content: start` |
| `content:center` | `place-content: center center` |
| `self` | `place-self: start` |
| `self:center` | `place-self: center center` |

---

## Size Rules

| Rule | CSS |
|---|---|
| `size:full` | `width: 100%; height: 100%; box-sizing: border-box` |
| `size:100` | `width: 100px; height: 100px; box-sizing: border-box` |
| `size:min` | `width: min-content; height: min-content` |
| `size:max` | `width: max-content; height: max-content` |
| `size:fit` | `width: fit-content; height: fit-content` |
| `size:100:200` | `width: 100px; height: 200px` |
| `width:full` | `width: 100%; box-sizing: border-box` |
| `width:100:50:200` | `width: 100px; min-width: 50px; max-width: 200px` |
| `height:full` | `height: 100%; box-sizing: border-box` |
| `height:100:50:200` | `height: 100px; min-height: 50px; max-height: 200px` |
| `ratio:16/9` | `aspect-ratio: 16/9` |
| `overflow:hidden` | `overflow: hidden` |
| `overflow:y:scroll` | `overflow-y: scroll` (with flex scroll helpers) |
| `overflow:x:auto` | `overflow-x: auto` |

---

## Spacing Rules

| Rule | CSS |
|---|---|
| `gap` | `column-gap: 8px; row-gap: 8px` |
| `gap:2` | `column-gap: 16px; row-gap: 16px` |
| `gap:1:2` | `column-gap: 8px; row-gap: 16px` |
| `margin:1` | `margin: 8px` |
| `margin:1:2:3:4` | `margin: 8px 16px 24px 32px` |
| `margin:top:2` | `margin-top: 16px` |
| `margin:bottom:1` | `margin-bottom: 8px` |
| `margin:left:auto` | `margin-left: auto` |
| `margin:right:auto` | `margin-right: auto` |
| `padding:1` | `padding: 8px` |
| `padding:1:2:3:4` | `padding: 8px 16px 24px 32px` |
| `padding:top:2` | `padding-top: 16px` |
| `padding:bottom:1` | `padding-bottom: 8px` |

### Gap Shorthand

The `gap` rule is the most commonly used spacing rule. Numeric values are multiplied by 8px (1 rem unit):

- `gap` → 8px
- `gap:1` → 8px
- `gap:2` → 16px
- `gap:0.5` → 4px

---

## Position Rules

### Position Types

| Rule | CSS |
|---|---|
| `relative` | `position: relative` |
| `absolute` | `position: absolute` |
| `fixed` | `position: fixed` |
| `sticky` | `position: sticky` |
| `static` | `position: static` |

### Position Values

| Rule | CSS |
|---|---|
| `inset` | `top: 0; right: 0; bottom: 0; left: 0` |
| `inset:1` | `top: 8px; right: 8px; bottom: 8px; left: 8px` |
| `top` | `top: 0` |
| `top:1` | `top: 8px` |
| `top:full` | `top: 100%` |
| `bottom:0` | `bottom: 0` |
| `left:auto` | `left: auto` |
| `right:0` | `right: 0` |
| `layer` | `z-index: 1` |
| `layer:10` | `z-index: 10` |

### View Transitions

| Rule | CSS |
|---|---|
| `view:name` | `view-transition-name: name` |

---

## Responsive Queries

Layout attributes support responsive breakpoints via the `@` syntax:

### Min-Width Breakpoints

```html
<!-- Applied when viewport ≥ 768px -->
<div layout@768px="row">

<!-- Applied when viewport ≥ 1024px -->
<div layout@1024px="grid:3">
```

### Named Queries

| Query | Media |
|---|---|
| `@print` | `print` |
| `@portrait` | `(orientation: portrait)` |
| `@landscape` | `(orientation: landscape)` |
| `@hover` | `(hover: hover)` |
| `@any-hover` | `(any-hover: hover)` |

### Combined Queries

```html
<!-- Applied when ≥768px OR ≥1024px -->
<div layout@768px\|1024px="row">
```

---

## Dimensions

Special dimension keywords:

| Keyword | Value |
|---|---|
| `min` | `min-content` |
| `max` | `max-content` |
| `fit` | `fit-content` |
| `full` | `100%` |

Numeric values without units are treated as rem (×8px):

- `1` → `8px`
- `2` → `16px`
- `0.5` → `4px`
- `1.5` → `12px`

String values with units are passed through:

- `100%` → `100%`
- `10px` → `10px`
- `2rem` → `2rem`
- `auto` → `auto`

### CSS Variables

Use CSS custom properties in layout rules:

```html
<div layout="gap:--my-gap">
<div layout="width:--content-width">
```

---

## Gotchas

- **Layout attributes cannot contain expressions** — `layout="column gap:\${size}"` throws an error. Use CSS variables or conditional class names instead
- **Host layout requires `<template>` as root** — when using `<template layout="...">`, it must be the only child of the render output
- **Layout classes are auto-generated** — class names like `l-abc12` are random and should not be referenced in external CSS
- **Styles are shared globally** — the layout engine injects rules into a shared stylesheet, not per-component
- **Numeric values are rem-based** — `gap:2` means `16px` (2 × 8px), not `2px`
- **`overflow:scroll` adds flex helpers** — when using `overflow:y:scroll`, the engine adds `flex-grow: 1; flex-basis: 0; overscroll-behavior: contain` for proper flex container scrolling
